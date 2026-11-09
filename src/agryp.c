/*
 * agryp — минимальный супервизор (PID 1) для AI-агентов.
 *
 * Один файл. Только libc. Ноль зависимостей. Этика LFS:
 * агент — это процесс первого класса, у которого есть
 * политика перезапуска и бюджет попытки, а не «табличка в терминале».
 * Попытка — группа процессов (setpgid): режем всю семью,
 * внуков-сирот не оставляем.
 *
 * Сборка:  gcc -O2 -Wall -Wextra -std=c99 -o agryp src/agryp.c
 * Запуск:  ./agryp --dir examples
 *
 * Юниты: *.agent (формат см. README).
 * Логи: JSON-строки в stdout — удобно скармливать любому сборщику.
 */
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <sched.h>
#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#define MAX_UNITS 128 /* Поправка №9: ферма агентов 100+ (ТЗ-8, виток 8) */
#define NAME_LEN  64
#define EXEC_LEN  512
#define CG_BASE_LEN 512 /* потолок пути делегированной ветки cgroup (Ст. 11) */
#define GRACE_MS  3000   /* время на вежливую смерть при SIGTERM */
#define SUSTAIN_MS     10000 /* «проработал» гасит лестницу перезапуска (Ст. 8) */
#define BACKOFF_CAP_MS 30000 /* потолок лестницы перезапуска (Ст. 8) */
#define CRASH_LIMIT    5     /* подряд своих смертей → терминальный failed (Ст. 8) */
#define FINISH_MS 5000   /* дефолт потолка finish-хука (s6 timeout-finish): ключ юнита перекрывает (Виток 11) */
#define ROTATE_BYTES  262144 /* Виток 10: потолок журнала до ротации (может --rotate-bytes) */
#define ROTATE_KEEP   3      /* Виток 10: сколько отрезанных хвостов хранить */

typedef enum { R_ALWAYS = 0, R_ON_FAILURE = 1, R_NO = 2 } restart_t;
typedef enum { U_STOPPED = 0, U_RUNNING = 1, U_COOLDOWN = 2 } state_t;

typedef struct {
    /* конфигурация */
    char      name[NAME_LEN];
    char      exec[EXEC_LEN];
    restart_t restart;
    int       budget_sec;    /* 0 = без лимита: agryp режет попытку по таймауту */
    int       cooldown_ms;   /* пауза перед перезапуском */
    int       max_attempts;  /* 0 = без лимита */
    int       token_budget;  /* 0 = без лимита: вторая валюта бюджета (Ст. 14) */
    int       mem_max_mb;    /* 0 = без клетки: memory.max cgroups v2 (Ст. 15) */
    int       jail;          /* 0|1=pid|2=mount|3 — комнаты имён попытки (Виток 7) */
    char      finish[256];   /* хук уборки между смертью и рестартом (Виток 6, школа s6) */
    int       finish_timeout_ms; /* потолок хука per-unit, 0→FINISH_MS (Виток 11, s6 timeout-finish) */
    /* рантайм */
    state_t   state;
    pid_t     pid;
    pid_t     pgid;      /* группа попытки: kill(-pgid) режет всю семью */
    long long deadline_ms;   /* дедлайн бюджета текущей попытки */
    long long next_start_ms; /* когда выходить из cooldown */
    int       attempts;
    int       exits_ok;
    int       exits_fail;
    int       budget_kills;
    int       restarts;
    int       token_kills;
    int       tokens;        /* съедено в текущей попытке */
    int       tokens_total;  /* съедено за всё время */
    int       fail_streak;   /* подряд своих смертей — растит лестницу (Ст. 8) */
    int       sup_kill;      /* казнь законом (бюджет/токены) — не ошибка агента */
    int       ctl_down;      /* файл <unit>.down жив — политика заморожена (Ст. 13) */
    long long ctl_since_ms;  /* с каких пор жив .down: TERM не убил за GRACE_MS — казнь (Виток 6) */
    int       retired;       /* файл юнита удалён из каталога — жизни больше нет (Виток 6) */
    long long run_started_ms; /* старт текущей попытки: «проработал» меряем от неё */
    int       ready;          /* Виток 11: попытка объявила готовность ready-файлом */
    long long ready_ms;       /* Виток 11: задержка готовности от старта попытки */
    char      sign[65];      /* Виток 10: сигнатура договора — sha256 байт *.agent */
    long long sign_mtime;    /* Виток 10: mtime договора на момент подписи */
} unit_t;

static unit_t g_units[MAX_UNITS];
static int    g_nunits = 0;
static volatile sig_atomic_t g_stop = 0;
static volatile sig_atomic_t g_hup = 0;  /* SIGHUP: перечитать каталог юнитов (Виток 6) */
static char g_status_path[1152];  /* Ст. 13: снимок состояния — файл, не сокет */
static char g_report_path[1152];  /* Ст. 14: сюда агенты отдают burn-rate */
static char g_cgbase[CG_BASE_LEN]; /* Ст. 15: наша делегированная ветка cgroup v2 */
static char g_ctl_dir[1152];  /* agrypctl: файлы-договоры вместо сокетов (Ст. 13) */
static char g_units_dir[1024]; /* Виток 11: каталог юнитов — от него строится AGRY_READY_PATH */
static char g_dropped[8][NAME_LEN]; /* Виток 6: ctl-drop не шумит — реестр последних 8 имён */
static int  g_ndropped = 0;
static long long g_t0;
/* Виток 10: двойная летопись (stdout + файл) и метрики файлом (Ст. 13) */
static char g_journal_path[1152];
static char g_metrics_path[1152];
static FILE *g_journal;
static long long g_journal_bytes;
static long long g_rotate_bytes = ROTATE_BYTES;
static long long g_orphans;   /* усыновлённые сироты (subreaper) */
static long long g_reloads;   /* перезагрузок каталога (SIGHUP) */
static long long g_rotations; /* ротаций журнала */

/* ---------- sha256: пломбы Витка 10 (ротация журнала, сигнатуры договоров) ---------- */

/* Компактная самодостаточная реализация (FIPS 180-4). Ноль зависимостей: Ст. 1. */
typedef struct {
    unsigned int h[8];
    unsigned long long len;
    unsigned char buf[64];
    size_t n;
} sha256_ctx;

static unsigned int ror32(unsigned int x, int r)
{
    return (x >> r) | (x << (32 - r));
}

static void sha256_block(sha256_ctx *c, const unsigned char *p)
{
    static const unsigned int K[64] = {
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
        0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
        0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
        0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
        0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
        0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
        0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
        0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    };
    unsigned int w[64], a, b, cc, d, e, f, g, h;
    int i;

    for (i = 0; i < 16; i++)
        w[i] = ((unsigned int)p[4 * i] << 24) | ((unsigned int)p[4 * i + 1] << 16) |
               ((unsigned int)p[4 * i + 2] << 8) | (unsigned int)p[4 * i + 3];
    for (i = 16; i < 64; i++) {
        unsigned int s0 = ror32(w[i - 15], 7) ^ ror32(w[i - 15], 18) ^ (w[i - 15] >> 3);
        unsigned int s1 = ror32(w[i - 2], 17) ^ ror32(w[i - 2], 19) ^ (w[i - 2] >> 10);
        w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }
    a = c->h[0]; b = c->h[1]; cc = c->h[2]; d = c->h[3];
    e = c->h[4]; f = c->h[5]; g  = c->h[6]; h = c->h[7];
    for (i = 0; i < 64; i++) {
        unsigned int S1 = ror32(e, 6) ^ ror32(e, 11) ^ ror32(e, 25);
        unsigned int ch = (e & f) ^ (~e & g);
        unsigned int t1 = h + S1 + ch + K[i] + w[i];
        unsigned int S0 = ror32(a, 2) ^ ror32(a, 13) ^ ror32(a, 22);
        unsigned int maj = (a & b) ^ (a & cc) ^ (b & cc);
        unsigned int t2 = S0 + maj;
        h = g; g = f; f = e; e = d + t1;
        d = cc; cc = b; b = a; a = t1 + t2;
    }
    c->h[0] += a; c->h[1] += b; c->h[2] += cc; c->h[3] += d;
    c->h[4] += e; c->h[5] += f; c->h[6] += g;  c->h[7] += h;
}

static void sha256_init(sha256_ctx *c)
{
    c->h[0] = 0x6a09e667; c->h[1] = 0xbb67ae85; c->h[2] = 0x3c6ef372; c->h[3] = 0xa54ff53a;
    c->h[4] = 0x510e527f; c->h[5] = 0x9b05688c; c->h[6] = 0x1f83d9ab; c->h[7] = 0x5be0cd19;
    c->len = 0; c->n = 0;
}

static void sha256_update(sha256_ctx *c, const void *data, size_t n)
{
    const unsigned char *p = data;

    c->len += n;
    while (n > 0) {
        size_t take = 64 - c->n;
        if (take > n) take = n;
        memcpy(c->buf + c->n, p, take);
        c->n += take; p += take; n -= take;
        if (c->n == 64) { sha256_block(c, c->buf); c->n = 0; }
    }
}

static void sha256_final(sha256_ctx *c, unsigned char out[32])
{
    unsigned long long bits = c->len * 8;
    unsigned char pad = 0x80;
    int i;

    sha256_update(c, &pad, 1);
    pad = 0;
    while (c->n != 56)
        sha256_update(c, &pad, 1);
    for (i = 7; i >= 0; i--) {
        unsigned char b = (unsigned char)(bits >> (8 * i));
        sha256_update(c, &b, 1);
    }
    for (i = 0; i < 8; i++) {
        out[4 * i]     = (unsigned char)(c->h[i] >> 24);
        out[4 * i + 1] = (unsigned char)(c->h[i] >> 16);
        out[4 * i + 2] = (unsigned char)(c->h[i] >> 8);
        out[4 * i + 3] = (unsigned char)(c->h[i]);
    }
}

static void sha256_hex(const unsigned char *d, char *hex)
{
    int i;

    for (i = 0; i < 32; i++)
        snprintf(hex + 2 * i, 3, "%02x", d[i]);
}

/* Хеш файла целиком: 0 — ок (hexout 65 байт), -1 — файл не открылся. */
static int sha256_file(const char *path, char hexout[65])
{
    FILE *f = fopen(path, "rb");
    sha256_ctx c;
    unsigned char buf[4096], d[32];
    size_t n;

    if (!f) return -1;
    sha256_init(&c);
    while ((n = fread(buf, 1, sizeof buf, f)) > 0)
        sha256_update(&c, buf, n);
    fclose(f);
    sha256_final(&c, d);
    sha256_hex(d, hexout);
    return 0;
}

/* ---------- время и логи ---------- */

static long long now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000LL + ts.tv_nsec / 1000000LL;
}

static void wall_ts(char *buf, size_t n)
{
    time_t t = time(NULL);
    struct tm tm;
    gmtime_r(&t, &tm);
    strftime(buf, n, "%Y-%m-%dT%H:%M:%SZ", &tm);
}

/* Виток 10: двойная летопись. Строка события уходит и в stdout (транскрипт
 * демо), и в файл журнала — единственный носитель, который ротируется
 * с пломбой-печатью. Журнал недоступен — события остаются в stdout, вслух. */
static void log_ev(const unit_t *u, const char *event, const char *fmt, ...)
{
    char tsbuf[32], extra[256], line[1600];
    va_list ap;
    long long up = now_ms() - g_t0;   /* виток 8: up_ms — жизнь супервизора, а не часы машины */

    va_start(ap, fmt);
    if (fmt) vsnprintf(extra, sizeof extra, fmt, ap);
    else     extra[0] = '\0';
    va_end(ap);

    wall_ts(tsbuf, sizeof tsbuf);
    if (u && extra[0])
        snprintf(line, sizeof line,
                 "{\"ts\":\"%s\",\"up_ms\":%lld,\"unit\":\"%s\",\"event\":\"%s\",%s}\n",
                 tsbuf, up, u->name, event, extra);
    else if (u)
        snprintf(line, sizeof line,
                 "{\"ts\":\"%s\",\"up_ms\":%lld,\"unit\":\"%s\",\"event\":\"%s\"}\n",
                 tsbuf, up, u->name, event);
    else if (extra[0])
        snprintf(line, sizeof line,
                 "{\"ts\":\"%s\",\"up_ms\":%lld,\"event\":\"%s\",%s}\n",
                 tsbuf, up, event, extra);
    else
        snprintf(line, sizeof line,
                 "{\"ts\":\"%s\",\"up_ms\":%lld,\"event\":\"%s\"}\n",
                 tsbuf, up, event);

    fputs(line, stdout);
    fflush(stdout);
    if (g_journal) {
        size_t n = strlen(line);
        if (fwrite(line, 1, n, g_journal) == n)
            g_journal_bytes += (long long)n;
        fflush(g_journal);
    }
}

/* Ротация журнала с пломбой (Виток 10, тикет «журнал-ротация»): хвост
 * отрезается атомарно (rename-цепочка), в НОВЫЙ журнал первой строкой
 * ложится реестр-печать: sha256 всего отрезанного файла — подделка любого
 * байта хвоста (включая середину) ловится аудитором tools/journal_audit.sh;
 * цепь печатей тянется через ротации, пока живы ROTATE_KEEP хвостов. */
static void journal_rotate(void)
{
    char p1[1200], p2[1200], p3[1200];
    char seal[65] = "";

    if (!g_journal) return;
    fclose(g_journal);
    g_journal = NULL;
    if (sha256_file(g_journal_path, seal) != 0)
        seal[0] = '\0';                       /* печать не снята — вслух ниже */
    snprintf(p1, sizeof p1, "%s.1", g_journal_path);
    snprintf(p2, sizeof p2, "%s.2", g_journal_path);
    snprintf(p3, sizeof p3, "%s.3", g_journal_path);
    unlink(p3);
    rename(p2, p3);
    rename(p1, p2);
    rename(g_journal_path, p1);
    g_journal = fopen(g_journal_path, "w");
    g_journal_bytes = 0;
    g_rotations++;
    if (!g_journal) {
        fprintf(stderr, "agryp: журнал %s не открылся после ротации: %s\n",
                g_journal_path, strerror(errno));
        return;
    }
    log_ev(NULL, "rotate", "\"rotated_bytes\":%lld,\"seal\":\"%s\"",
           g_rotate_bytes, seal[0] ? seal : "UNSEALED");
}

/* ---------- парсинг юнитов ---------- */

static char *trim(char *s)
{
    char *end;
    while (*s == ' ' || *s == '\t' || *s == '\r' || *s == '\n') s++;
    end = s + strlen(s);
    while (end > s && (end[-1] == ' ' || end[-1] == '\t' || end[-1] == '\r' || end[-1] == '\n'))
        end--;
    *end = '\0';
    return s;
}

static int parse_restart(const char *v, restart_t *out)
{
    if (!strcmp(v, "always"))                  { *out = R_ALWAYS;     return 0; }
    if (!strcmp(v, "on-failure") ||
        !strcmp(v, "on_failure"))              { *out = R_ON_FAILURE; return 0; }
    if (!strcmp(v, "no") || !strcmp(v, "never")) { *out = R_NO;       return 0; }
    return -1;
}

/* Виток 7 (тикет 007): ключ jail — комнаты имён попытки: `pid`, `mount`,
 * `pid,mount` или пусто. Неизвестное слово — вслух в stderr, клетка пустее
 * (Ст. 6: ничего не происходит молча). */
static int parse_jail(const char *val)
{
    char buf[32];
    char *tok, *s = buf;
    int mask = 0;

    snprintf(buf, sizeof buf, "%.31s", val);
    for (tok = strtok(s, ","); tok; tok = strtok(NULL, ",")) {
        if      (!strcmp(tok, "pid"))   mask |= 1;
        else if (!strcmp(tok, "mount")) mask |= 2;
        else fprintf(stderr, "agryp: jail: неизвестное слово '%s' — пропущено\n", tok);
    }
    return mask;
}

/* Читает один *.agent-файл в u: 0 — юнит готов, -1 — пропустить.
 * Общая для boot (load_units) и SIGHUP-reload (Виток 6). */
static int parse_unit_file(const char *path, const char *stem, size_t stem_len, unit_t *u)
{
    char line[1024];
    FILE *f = fopen(path, "r");
    int lineno = 0;

    if (!f) return -1;
    memset(u, 0, sizeof *u);
    u->restart     = R_ALWAYS;
    u->cooldown_ms = 1000;
    u->finish_timeout_ms = FINISH_MS;      /* Виток 11: дефолт канона s6 (5000) */
    snprintf(u->name, sizeof u->name, "%.*s", (int)stem_len, stem);
    while (fgets(line, sizeof line, f)) {
        char *s, *eq, *key, *val;
        lineno++;
        s = trim(line);
        if (!*s || *s == '#') continue;
        eq = strchr(s, '=');
        if (!eq) {
            fprintf(stderr, "agryp: %s:%d: строка без '=' пропущена\n", path, lineno);
            continue;
        }
        *eq = '\0';
        key = trim(s);
        val = trim(eq + 1);
        if      (!strcmp(key, "name"))         snprintf(u->name, sizeof u->name, "%.60s", val);
        else if (!strcmp(key, "exec"))         snprintf(u->exec, sizeof u->exec, "%.500s", val);
        else if (!strcmp(key, "restart")) {
            if (parse_restart(val, &u->restart))
                fprintf(stderr, "agryp: %s:%d: неизвестный restart '%s'\n", path, lineno, val);
        }
        else if (!strcmp(key, "budget-sec"))   u->budget_sec   = atoi(val);
        else if (!strcmp(key, "cooldown-ms"))  u->cooldown_ms  = atoi(val);
        else if (!strcmp(key, "max-attempts")) u->max_attempts = atoi(val);
        else if (!strcmp(key, "token-budget")) u->token_budget = atoi(val);
        else if (!strcmp(key, "mem-max-mb"))   u->mem_max_mb   = atoi(val);
        else if (!strcmp(key, "jail"))         u->jail         = parse_jail(val);
        else if (!strcmp(key, "finish"))       snprintf(u->finish, sizeof u->finish, "%.250s", val);
        else if (!strcmp(key, "finish-timeout-ms")) {
            u->finish_timeout_ms = atoi(val);  /* 0/минус — не «без лимита»: бесконечный */
            if (u->finish_timeout_ms <= 0)     /* хук нарушает Ст. 11 — дефолт ядра (Виток 11) */
                u->finish_timeout_ms = FINISH_MS;
        }
        else fprintf(stderr, "agryp: %s:%d: неизвестный ключ '%s'\n", path, lineno, key);
    }
    fclose(f);
    if (!u->exec[0]) {
        fprintf(stderr, "agryp: %s: ключ exec не задан — юнит пропущен\n", path);
        return -1;
    }
    /* Виток 10: подпись договора — хеш байт файла + mtime. «Кто менял» мы
     * не различаем (агентов не подписываем — названо вслух), но «ЧТО именно
     * поменялось» — машинный факт: дифф двух хешей виден в unit-sign. */
    {
        struct stat st;
        if (sha256_file(path, u->sign) == 0 && stat(path, &st) == 0)
            u->sign_mtime = (long long)st.st_mtime;
        else {
            u->sign[0] = '\0';
            fprintf(stderr, "agryp: %s: подпись договора не снята\n", path);
        }
    }
    return 0;
}

static void load_units(const char *dir)
{
    DIR *d = opendir(dir);
    struct dirent *de;

    if (!d) {
        fprintf(stderr, "agryp: не могу открыть каталог юнитов %s: %s\n", dir, strerror(errno));
        exit(2);
    }
    while ((de = readdir(d)) != NULL && g_nunits < MAX_UNITS) {
        size_t len = strlen(de->d_name);
        char path[1024];
        unit_t u;

        if (len < 7 || strcmp(de->d_name + len - 6, ".agent")) continue;
        snprintf(path, sizeof path, "%s/%s", dir, de->d_name);
        if (parse_unit_file(path, de->d_name, len - 6, &u) == 0)
            g_units[g_nunits++] = u;
    }
    closedir(d);
}

/* ---------- жизнь юнита ---------- */

/* Виток 7 (тикет 007): PID 1 pid-комнаты глух к сигналам без обработчика
 * (pid_namespaces(7)) — прокси умирает так же, как умер бы агент без клетки. */
static void jail_term(int s) { signal(s, SIG_DFL); raise(s); }

static void spawn_unit(unit_t *u)
{
    /* Клетка имён (Ст. 15-сосед, тикет 007): вход в новую pid-комнату —
     * только родиться в ней, поэтому вместо fork() — clone(CLONE_NEWPID
     * [|CLONE_NEWNS]): ребёнок и есть PID 1 своей комнаты, геометрия
     * попытки не меняется (тот же ребёнок супервизора, та же группа,
     * тот же PDEATHSIG). Среда не дала (EPERM) — loud jail-skip и работа
     * дальше без клетки, как cgroup-skip (Ст. 15); молчаливой усечки нет. */
    int jmask = u->jail & 3;
    int jf    = ((jmask & 1) ? CLONE_NEWPID : 0) | ((jmask & 2) ? CLONE_NEWNS : 0);
    pid_t p = jf ? (pid_t)syscall(SYS_clone, (long)jf | SIGCHLD,
                                  0, NULL, NULL, NULL)
                 : fork();

    if (p < 0 && jf) {
        log_ev(u, "jail-skip", "\"reason\":\"clone\",\"errno\":%d", errno);
        u->jail = 0; jmask = 0; jf = 0;    /* вслух один раз; reload перевзводит */
        p = fork();
    }
    if (p < 0) {
        log_ev(u, "spawn-fail", "\"error\":\"fork\",\"errno\":%d", errno);
        u->state = U_COOLDOWN;
        u->next_start_ms = now_ms() + u->cooldown_ms;
        return;
    }
    if (p == 0) {                              /* ребёнок: агент */
        signal(SIGTERM, SIG_DFL);
        signal(SIGINT,  SIG_DFL);
        pid_t ppid = getppid();                /* страховка от сирот (Ст. 9): */
        if (prctl(PR_SET_PDEATHSIG, SIGKILL, 0, 0, 0) < 0 || getppid() != ppid) {
            fprintf(stderr, "agryp: %s: страховка PDEATHSIG не встала\n", u->name);
            _exit(125);
        }
        setpgid(0, 0);                         /* своя группа: режем семью целиком */
        setenv("AGRY_UNIT", u->name, 1);       /* договор hook'а: кто ты и куда отчитываться */
        setenv("AGRY_TOKEN_REPORT", g_report_path, 1);
        {   /* Виток 11 (тикет 016): readiness без сокетов — канал объявлен env-договором */
            char rp[1152];
            snprintf(rp, sizeof rp, "%.500s/%.63s.ready", g_units_dir, u->name);
            setenv("AGRY_READY_PATH", rp, 1);  /* создал файл — попытка готова (Ст. 13) */
        }
        if (jmask & 1) {                       /* терминал комнаты глух: TERM проксируется */
            signal(SIGTERM, jail_term);
            signal(SIGINT,  jail_term);
        }
        if (jmask & 2 &&                       /* mount-клетка: propagation наружу закрыт; */
            mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) < 0)
            fprintf(stderr, "agryp: %s: jail: / не стал private: %s\n",
                    u->name, strerror(errno));
        {   /* тикет 009: кому будить после записи токен-рапорта (SIGUSR2) */
            char supbuf[16];
            snprintf(supbuf, sizeof supbuf, "%d", (int)ppid);
            setenv("AGRY_SUPER_PID", supbuf, 1);
        }
        if (u->mem_max_mb > 0) {               /* в клетку до exec: ни байта мимо лимита */
            char procs[1280], pbuf[32];
            int fd, n = snprintf(pbuf, sizeof pbuf, "%d", (int)getpid());
            snprintf(procs, sizeof procs, "%.480s/agryp-%.63s/cgroup.procs", g_cgbase, u->name);
            fd = open(procs, O_WRONLY);
            if (fd < 0 || write(fd, pbuf, (size_t)n) != (ssize_t)n)
                _exit(126);                    /* лимит объявлен — тишина запрещена (Ст. 11) */
            close(fd);
        }
        execl("/bin/sh", "sh", "-c", u->exec, (char *)NULL);
        _exit(127);
    }
    setpgid(p, p);                             /* и в родителе — закрываем гонку */
    {   /* Виток 11: чистота между жизнями — чужой ready-файл попытку не переживёт */
        char rp[1152];
        snprintf(rp, sizeof rp, "%.500s/%.63s.ready", g_units_dir, u->name);
        unlink(rp);
    }
    u->ready = 0; u->ready_ms = 0;             /* новая попытка — готовность с нуля */
    u->pid         = p;
    u->pgid        = p;
    u->state       = U_RUNNING;
    u->attempts++;
    u->run_started_ms = now_ms();
    u->tokens      = 0;
    u->deadline_ms = (u->budget_sec > 0)
                     ? now_ms() + (long long)u->budget_sec * 1000LL
                     : 0;
    log_ev(u, "spawn", "\"pid\":%d,\"attempt\":%d,\"budget_sec\":%d,\"jailed\":%d",
           (int)p, u->attempts, u->budget_sec, jf ? jmask : 0);
}

/* finish-хук (Виток 6, школа s6): уборка между смертью попытки и рестартом.
 * Хук — часть попытки, но вне её группы; FINISH_MS на прощание, упор — вслух
 * (Ст. 11); сбой хука лестницу перезапуска не трогает — он не часть политики. */
static void run_finish(unit_t *u, int code, int sig)
{
    char ec[16], bs[16];
    int status;
    pid_t p, r;
    long long deadline;

    if (!u->finish[0]) return;                 /* хук не объявлен — молчание честно */
    snprintf(ec, sizeof ec, "%d", code);
    snprintf(bs, sizeof bs, "%d", sig);
    p = fork();
    if (p < 0) { log_ev(u, "finish", "\"error\":\"fork\",\"errno\":%d", errno); return; }
    if (p == 0) {
        setpgid(0, 0);                         /* свою группу: группу попытки не режем */
        setenv("AGRY_UNIT", u->name, 1);       /* договор: кто ты и чем кончил */
        setenv("AGRY_EXIT_CODE", ec, 1);
        setenv("AGRY_BY_SIGNAL", bs, 1);
        execl("/bin/sh", "sh", "-c", u->finish, (char *)NULL);
        _exit(127);
    }
    deadline = now_ms() + u->finish_timeout_ms;   /* потолок per-unit (Виток 11) */
    while ((r = waitpid(p, &status, WNOHANG)) == 0 && now_ms() < deadline)
        poll(NULL, 0, 25);
    if (r == 0) {                              /* упёрся в потолок — говорим вслух */
        kill(p, SIGKILL);
        waitpid(p, &status, 0);
        log_ev(u, "finish", "\"timeout\":true,\"ms\":%d", u->finish_timeout_ms);
        return;
    }
    if (r < 0) { log_ev(u, "finish", "\"error\":\"waitpid\",\"errno\":%d", errno); return; }
    if (WIFSIGNALED(status))
        log_ev(u, "finish", "\"by_signal\":%d", WTERMSIG(status));
    else
        log_ev(u, "finish", "\"code\":%d", WEXITSTATUS(status));
}

static void handle_exit(unit_t *u, int status)
{
    int code = WIFEXITED(status)   ? WEXITSTATUS(status) : -1;
    int sig  = WIFSIGNALED(status) ? WTERMSIG(status)    : 0;
    int ok   = WIFEXITED(status) && WEXITSTATUS(status) == 0;

    if (ok) u->exits_ok++; else u->exits_fail++;
    u->pid = 0;
    {   /* Виток 11: мёртвая попытка не остаётся «готовой» — договор снят (Ст. 13) */
        char rp[1152];
        snprintf(rp, sizeof rp, "%.500s/%.63s.ready", g_units_dir, u->name);
        unlink(rp);
    }
    u->ready = 0; u->ready_ms = 0;

    if (sig) log_ev(u, "exit", "\"by_signal\":%d,\"ok\":%s", sig, ok ? "true" : "false");
    else     log_ev(u, "exit", "\"code\":%d,\"ok\":%s",       code, ok ? "true" : "false");

    run_finish(u, code, sig);                  /* Виток 6: уборка до лестницы (тикет 004) */

    if (g_stop) { u->state = U_STOPPED; return; }

    /* Лестница перезапуска (Ст. 8, учителя — docs/TEACHERS.md): своя смерть
     * растит счётчик, победа гасит, казнь закона нейтральна, «проработал» — с нуля. */
    int sup_killed = u->sup_kill;
    u->sup_kill = 0;
    if (!sup_killed) {                         /* казнь закона лестницу не трогает */
        if (ok) u->fail_streak = 0;
        else    u->fail_streak++;
    }
    if (now_ms() - u->run_started_ms >= SUSTAIN_MS)
        u->fail_streak = 0;

    int want = ((u->restart == R_ALWAYS) ||
                (u->restart == R_ON_FAILURE && !ok)) && !u->ctl_down && !u->retired;
    int fused = want && !ok && !sup_killed && u->fail_streak >= CRASH_LIMIT;

    if (want && !fused && (u->max_attempts == 0 || u->attempts < u->max_attempts)) {
        int delay = u->cooldown_ms;
        if (u->fail_streak > 1) {
            int k = u->fail_streak - 1;
            while (k-- > 0 && delay < BACKOFF_CAP_MS) delay *= 2;
            if (delay > BACKOFF_CAP_MS) delay = BACKOFF_CAP_MS;
        }
        u->state = U_COOLDOWN;
        u->next_start_ms = now_ms() + delay;
        u->restarts++;
        log_ev(u, "restart", "\"next_attempt\":%d,\"backoff_ms\":%d,\"streak\":%d",
               u->attempts + 1, delay, u->fail_streak);
    } else {
        u->state = U_STOPPED;
        if (fused)
            log_ev(u, "failed", "\"reason\":\"crash-loop\",\"streak\":%d,\"attempts\":%d",
                   u->fail_streak, u->attempts);
        log_ev(u, "stopped", "\"reason\":\"%s\"", u->ctl_down ? "ctl-down" :
               u->retired ? "reload" :
               fused ? "crash-loop" : want ? "max-attempts" : "policy");
    }
}

static void reap(void)
{
    for (;;) {
        int status;
        pid_t p = waitpid(-1, &status, WNOHANG);
        int i;

        if (p <= 0) break;
        int known = 0;
        for (i = 0; i < g_nunits; i++) {
            if (g_units[i].pid == p) { handle_exit(&g_units[i], status); known = 1; break; }
        }
        if (!known) {                          /* subreaper: усыновлённого хороним вслух */
            g_orphans++;                       /* Виток 10: счёт сирот — метрика */
            log_ev(NULL, "reap-orphan", "\"pid\":%d,\"code\":%d", (int)p,
                   WIFEXITED(status) ? WEXITSTATUS(status) : -1);
        }
    }
}

/* ---------- статус: файл вместо сокета (Ст. 13) ---------- */

static const char *state_name(state_t s)
{
    return s == U_RUNNING ? "RUNNING" : s == U_COOLDOWN ? "COOLDOWN" : "STOPPED";
}

/* Снимок семьи: пишем в tmp и rename — читатель никогда не видит полфайла.
 * Существование файла = PID 1 жив; на выходе unlink — мёртвый не «зелёный».
 * SIGUSR1 не нужен для свежести: файл переписывается каждую итерацию цикла. */
static void write_status(void)
{
    char tmp[1200];
    FILE *f;
    int i;

    snprintf(tmp, sizeof tmp, "%s.tmp", g_status_path);
    f = fopen(tmp, "w");
    if (!f) return;
    fprintf(f, "{\"sup\":\"agryp\",\"pid\":%d,\"units\":%d,\"uptime_ms\":%lld}\n",
            (int)getpid(), g_nunits, now_ms() - g_t0);
    for (i = 0; i < g_nunits; i++) {
        unit_t *u = &g_units[i];
        fprintf(f, "{\"unit\":\"%s\",\"state\":\"%s\",\"pid\":%d,\"attempt\":%d,"
                   "\"budget_sec\":%d,\"token_budget\":%d,\"tokens\":%d,"
                   "\"mem_max_mb\":%d,\"jail\":%d,\"attempts\":%d,\"exits_ok\":%d,"
                   "\"exits_fail\":%d,\"budget_kills\":%d,\"token_kills\":%d,"
                   "\"restarts\":%d,\"streak\":%d,\"ready\":%d,\"ready_ms\":%lld,"
                   "\"ctl_down\":%d}\n",
                u->name, state_name(u->state), (int)u->pid, u->attempts,
                u->budget_sec, u->token_budget, u->tokens, u->mem_max_mb,
                u->jail, u->attempts, u->exits_ok, u->exits_fail,
                u->budget_kills, u->token_kills, u->restarts, u->fail_streak,
                u->ready, u->ready_ms, u->ctl_down);
    }
    fclose(f);
    rename(tmp, g_status_path);
}

/* Метрики файлом (Виток 10, тикет «экспорт метрик», Ст. 13 — файл вместо сокета):
 * формат Prometheus/OpenMetrics textfile — читается мировым инструментарием,
 * пишется атомарно (tmp + rename), переписывается каждую итерацию цикла.
 * Файл существует = супервизор жив; на выходе unlink (Ст. 13). */
static void metrics_label(char *out, size_t n, const char *unit)
{
    size_t i, j = 0;

    for (i = 0; unit[i] && j + 4 < n; i++) {
        if (unit[i] == '\\' || unit[i] == '"' || unit[i] == '\n') {
            out[j++] = '\\';
            out[j++] = unit[i] == '\n' ? 'n' : unit[i];
        } else
            out[j++] = unit[i];
    }
    out[j] = '\0';
}

static void write_metrics(void)
{
    char tmp[1200], lab[96];
    FILE *f;
    int i;

    snprintf(tmp, sizeof tmp, "%s.tmp", g_metrics_path);
    f = fopen(tmp, "w");
    if (!f) return;
    fprintf(f, "# HELP agryp_up_ms Жизнь супервизора, мс\n# TYPE agryp_up_ms gauge\n");
    fprintf(f, "agryp_up_ms %lld\n", now_ms() - g_t0);
    fprintf(f, "# HELP agryp_units Юнитов в каталоге\n# TYPE agryp_units gauge\n");
    fprintf(f, "agryp_units %d\n", g_nunits);
    fprintf(f, "# HELP agryp_orphans_total Усыновлённые сироты (subreaper)\n# TYPE agryp_orphans_total counter\n");
    fprintf(f, "agryp_orphans_total %lld\n", g_orphans);
    fprintf(f, "# HELP agryp_reloads_total Перезагрузок каталога (SIGHUP)\n# TYPE agryp_reloads_total counter\n");
    fprintf(f, "agryp_reloads_total %lld\n", g_reloads);
    fprintf(f, "# HELP agryp_rotations_total Ротаций журнала с пломбой\n# TYPE agryp_rotations_total counter\n");
    fprintf(f, "agryp_rotations_total %lld\n", g_rotations);
    fprintf(f, "# HELP agryp_attempts_total Попыток юнита\n# TYPE agryp_attempts_total counter\n");
    fprintf(f, "# HELP agryp_exits_ok_total Чистых выходов (code 0)\n# TYPE agryp_exits_ok_total counter\n");
    fprintf(f, "# HELP agryp_exits_fail_total Неудачных выходов\n# TYPE agryp_exits_fail_total counter\n");
    fprintf(f, "# HELP agryp_budget_kills_total Казней по бюджету времени\n# TYPE agryp_budget_kills_total counter\n");
    fprintf(f, "# HELP agryp_token_kills_total Казней по токен-бюджету\n# TYPE agryp_token_kills_total counter\n");
    fprintf(f, "# HELP agryp_tokens_total Токенов съедено за всё время\n# TYPE agryp_tokens_total counter\n");
    fprintf(f, "# HELP agryp_restarts_total Перезапусков (выход из попытки в cooldown)\n# TYPE agryp_restarts_total counter\n");
    fprintf(f, "# HELP agryp_fail_streak Смертей подряд (лестница Ст. 8)\n# TYPE agryp_fail_streak gauge\n");
    fprintf(f, "# HELP agryp_ctl_down Политика заморожена файлом .down\n# TYPE agryp_ctl_down gauge\n");
    for (i = 0; i < g_nunits; i++) {
        unit_t *u = &g_units[i];

        metrics_label(lab, sizeof lab, u->name);
        fprintf(f, "agryp_attempts_total{unit=\"%s\"} %d\n", lab, u->attempts);
        fprintf(f, "agryp_exits_ok_total{unit=\"%s\"} %d\n", lab, u->exits_ok);
        fprintf(f, "agryp_exits_fail_total{unit=\"%s\"} %d\n", lab, u->exits_fail);
        fprintf(f, "agryp_budget_kills_total{unit=\"%s\"} %d\n", lab, u->budget_kills);
        fprintf(f, "agryp_token_kills_total{unit=\"%s\"} %d\n", lab, u->token_kills);
        fprintf(f, "agryp_tokens_total{unit=\"%s\"} %d\n", lab, u->tokens_total);
        fprintf(f, "agryp_restarts_total{unit=\"%s\"} %d\n", lab, u->restarts);
        fprintf(f, "agryp_fail_streak{unit=\"%s\"} %d\n", lab, u->fail_streak);
        fprintf(f, "agryp_ctl_down{unit=\"%s\"} %d\n", lab, u->ctl_down);
    }
    fclose(f);
    rename(tmp, g_metrics_path);
}

static int print_status(const char *dir)
{
    char path[1152];
    char line[2048];
    FILE *f;

    snprintf(path, sizeof path, "%s/.agryp-status", dir);
    f = fopen(path, "r");
    if (!f) {
        fprintf(stderr, "agryp: супервизор не запущен (нет %s)\n", path);
        return 1;
    }
    while (fgets(line, sizeof line, f)) fputs(line, stdout);
    fclose(f);
    return 0;
}

/* ---------- токен: агент сам отдаёт burn-rate (Ст. 14) ---------- */

/* Договор как у sd_notify: канал передаётся через env (AGRY_TOKEN_REPORT).
 * Строки «<unit> tokens <n>» копятся в отчёт; супервизор съедает его раз
 * в итерацию. Молчащий агент не обманывает бюджет: его ловит time-бюджет. */
static void collect_tokens(void)
{
    char line[256], name[64], verb[32];
    FILE *f, *tr;
    int n, i;

    f = fopen(g_report_path, "r");
    if (!f) return;
    while (fgets(line, sizeof line, f)) {
        int found = 0;
        if (sscanf(line, "%63s %31s %d", name, verb, &n) != 3 || strcmp(verb, "tokens"))
            continue;
        for (i = 0; i < g_nunits; i++)
            if (!strcmp(g_units[i].name, name)) {
                g_units[i].tokens_total += n;
                g_units[i].tokens += n;
                found = 1;
                break;
            }
        if (!found)
            log_ev(NULL, "report-drop", "\"unit\":\"%s\",\"tokens\":%d", name, n);
    }
    fclose(f);
    tr = fopen(g_report_path, "w");   /* отчёт съеден целиком */
    if (tr) fclose(tr);
}

/* ---------- готовность: файл-договор вместо сокета (Виток 11, тикет 016) ---------- */

/* Договор как у sd_notify READY=1 / s6 notification-fd, но канал — файл:
 * агенту выдан AGRY_READY_PATH, создал файл — попытка готова. Сокета нет,
 * пайпа нет: файловая система и есть API (Ст. 13). Появление — вслух один
 * раз на попытку: ready с честной задержкой от старта попытки. Молчание
 * агента готовностью не считается: кто не объявился — тот не готов. */
static void poll_ready(void)
{
    int i;

    for (i = 0; i < g_nunits; i++) {
        unit_t *u = &g_units[i];
        char rp[1152];
        if (u->ready || u->state != U_RUNNING || u->pid <= 0) continue;
        snprintf(rp, sizeof rp, "%.500s/%.63s.ready", g_units_dir, u->name);
        if (access(rp, F_OK) == 0) {
            u->ready = 1;
            u->ready_ms = now_ms() - u->run_started_ms;
            log_ev(u, "ready", "\"ms\":%lld,\"attempt\":%d", u->ready_ms, u->attempts);
        }
    }
}

/* ---------- ctl: команда — файл-договор (Виток 5, школа s6) ---------- */

/* agrypctl stop кладёт <dir>/.agryp-ctl/<unit>.down, start снимает: файловая
 * система и есть API (Ст. 13). Файл жив — попытка казнена TERM'ом группы,
 * политика перезапуска заморожена. Файл снят — ctl-up: рука оператора даёт
 * новую попытку с чистой лестницей. Чужое имя — ctl-drop: молчания нет. */
static void poll_ctl(void)
{
    DIR *d = opendir(g_ctl_dir);
    struct dirent *de;
    char name[NAME_LEN];
    int i, seen[MAX_UNITS] = {0};
    if (!d) return;                            /* ctl-каталога нет — команд нет */
    while ((de = readdir(d)) != NULL) {
        size_t len = strlen(de->d_name);
        if (len < 6 || strcmp(de->d_name + len - 5, ".down")) continue;
        snprintf(name, sizeof name, "%.*s", (int)(len - 5), de->d_name);
        for (i = 0; i < g_nunits && strcmp(g_units[i].name, name); i++);
        if (i == g_nunits) {
            int j, said = 0;                   /* чужое имя — вслух один раз (Ст. 6, Виток 6) */
            for (j = 0; j < g_ndropped && j < 8; j++)
                if (!strcmp(g_dropped[j], name)) { said = 1; break; }
            if (!said) {
                snprintf(g_dropped[g_ndropped % 8], NAME_LEN, "%s", name);
                g_ndropped++;
                log_ev(NULL, "ctl-drop", "\"file\":\"%.63s\"", de->d_name);
            }
            continue;
        }
        seen[i] = 1; unit_t *u = &g_units[i];
        if (!u->ctl_down) {                    /* файл появился: казнь и заморозка */
            u->ctl_down = 1; u->ctl_since_ms = now_ms(); log_ev(u, "ctl-down", NULL);
            if (u->state == U_RUNNING && u->pid > 0) {
                u->sup_kill = 1;               /* казнь закона лестницу не растит */
                if (kill(-u->pgid, SIGTERM) < 0) kill(u->pid, SIGTERM);
            }
        }
    }
    closedir(d);
    for (i = 0; i < g_nunits; i++) {           /* тикет 006: TERM не убил за GRACE_MS — казнь */
        unit_t *u = &g_units[i];
        if (u->ctl_down && u->ctl_since_ms > 0 && u->state == U_RUNNING &&
            u->pid > 0 && now_ms() - u->ctl_since_ms > GRACE_MS) {
            u->sup_kill = 1;                   /* казнь закона: лестницу не растит */
            u->ctl_since_ms = 0;               /* закон казнил один раз — вторым бить не надо */
            log_ev(u, "ctl-kill", "\"pid\":%d,\"attempt\":%d", (int)u->pid, u->attempts);
            if (kill(-u->pgid, SIGKILL) < 0) kill(u->pid, SIGKILL);
        }
    }
    for (i = 0; i < g_nunits; i++) {
        unit_t *u = &g_units[i];
        if (u->ctl_down && !seen[i]) {         /* файл снят: ctl-up — новая жизнь */
            u->ctl_down = 0; u->fail_streak = 0;   /* рука оператора: лестница с нуля */
            log_ev(u, "ctl-up", NULL);
            if (u->state != U_RUNNING) spawn_unit(u);   /* минуя cooldown */
        }
    }
}

/* ---------- память: клетка cgroup v2 в собственной ветке (Ст. 15) ---------- */

/* Правило одного писателя в делегированном дереве cgroups: agryp строит
 * комнаты только внутри собственной ветки (/proc/self/cgroup). Среда не
 * даёт cgroups — loud cgroup-skip и работа дальше; молчаливой усечки нет. */
/* Комнатка юнита внутри собственной ветки cgroup v2 (Ст. 15); отказ — вслух.
 * Общая для boot (cgroup_init) и SIGHUP-reload (Виток 6). */
static void cgroup_room(unit_t *u)
{
    char dir[1200], val[1280], mbuf[32];
    int fd, m;

    if (u->mem_max_mb <= 0) return;
    snprintf(dir, sizeof dir, "%.480s/agryp-%.63s", g_cgbase, u->name);
    snprintf(val, sizeof val, "%.1180s/memory.max", dir);
    if ((mkdir(dir, 0755) && errno != EEXIST) || (fd = open(val, O_WRONLY)) < 0)
        goto deny;
    m = snprintf(mbuf, sizeof mbuf, "%dM", u->mem_max_mb);
    if (write(fd, mbuf, (size_t)m) != (ssize_t)m) { close(fd); goto deny; }
    close(fd);
    return;
deny:
    log_ev(u, "cgroup-skip", "\"reason\":\"cgroupfs недоступен\",\"errno\":%d", errno);
    u->mem_max_mb = 0;
}

static void cgroup_init(void)
{
    char line[300];
    FILE *f;
    int i;

    f = fopen("/proc/self/cgroup", "r");
    if (f) {
        while (fgets(line, sizeof line, f))
            if (!strncmp(line, "0::", 3)) {
                size_t len = strlen(line);
                if (len && line[len - 1] == '\n') line[len - 1] = '\0';
                if (len > 1 && line[len - 1] == '/') line[len - 1] = '\0';
                snprintf(g_cgbase, sizeof g_cgbase, "/sys/fs/cgroup%.498s", line + 3);
                break;
            }
        fclose(f);
    }
    if (!g_cgbase[0])
        snprintf(g_cgbase, sizeof g_cgbase, "/sys/fs/cgroup");
    for (i = 0; i < g_nunits; i++)
        cgroup_room(&g_units[i]);
}

/* ---------- SIGHUP-reload: договоры меняются, дети живут (Виток 6, школа daemon-reload) ---------- */

/* daemon-reload без кровопролития: живые попытки не умирают; изменённые
 * ключи применяются сразу (дедлайн бюджета пересчитывается от текущей
 * попытки), новый *.agent — юнит появляется и стартует, удалённый —
 * юнит получает graceful-stop по Ст. 9. Перезапуск конкретного юнита —
 * не здесь: это agrypctl stop/start (Виток 5). */
static void do_reload(const char *dir)
{
    unit_t fresh[MAX_UNITS];
    DIR *d = opendir(dir);
    struct dirent *de;
    int nfresh = 0, added = 0, changed = 0, removed = 0;
    int i, j;

    if (!d) { log_ev(NULL, "reload", "\"error\":\"opendir\",\"errno\":%d", errno); return; }
    while ((de = readdir(d)) != NULL && nfresh < MAX_UNITS) {
        size_t len = strlen(de->d_name);
        char path[1024];

        if (len < 7 || strcmp(de->d_name + len - 6, ".agent")) continue;
        snprintf(path, sizeof path, "%s/%s", dir, de->d_name);
        if (parse_unit_file(path, de->d_name, len - 6, &fresh[nfresh]) == 0) nfresh++;
    }
    closedir(d);
    for (j = 0; j < nfresh; j++) {
        unit_t *nu = &fresh[j];
        for (i = 0; i < g_nunits && strcmp(g_units[i].name, nu->name); i++);
        if (i < g_nunits) {                    /* договор изменился — дети живут */
            unit_t *u = &g_units[i];
            if (u->restart != nu->restart || u->budget_sec != nu->budget_sec ||
                u->cooldown_ms != nu->cooldown_ms || u->max_attempts != nu->max_attempts ||
                u->token_budget != nu->token_budget || u->mem_max_mb != nu->mem_max_mb ||
                u->jail != nu->jail ||
                u->finish_timeout_ms != nu->finish_timeout_ms ||   /* Виток 11 */
                strcmp(u->exec, nu->exec) || strcmp(u->finish, nu->finish)) {
                changed++;
                u->restart = nu->restart;
                u->budget_sec = nu->budget_sec;
                u->cooldown_ms = nu->cooldown_ms;
                u->max_attempts = nu->max_attempts;
                u->token_budget = nu->token_budget;
                u->mem_max_mb = nu->mem_max_mb;
                u->jail = nu->jail;            /* reload перевзводит клетку имён */
                snprintf(u->exec, sizeof u->exec, "%.500s", nu->exec);
                snprintf(u->finish, sizeof u->finish, "%.250s", nu->finish);
                u->finish_timeout_ms = nu->finish_timeout_ms;  /* Виток 11: per-unit потолок */
                if (u->state == U_RUNNING)     /* дедлайн — от живой попытки */
                    u->deadline_ms = (u->budget_sec > 0)
                                     ? u->run_started_ms + (long long)u->budget_sec * 1000LL
                                     : 0;
            }
            /* Виток 10: сигнатура договора — дифф двух хешей, вслух, каждый reload */
            if (strcmp(u->sign, nu->sign)) {
                log_ev(u, "unit-sign", "\"old\":\"%s\",\"new\":\"%s\",\"mtime\":%lld",
                       u->sign[0] ? u->sign : "",
                       nu->sign[0] ? nu->sign : "", nu->sign_mtime);
                snprintf(u->sign, sizeof u->sign, "%.64s", nu->sign);
                u->sign_mtime = nu->sign_mtime;
            }
        } else if (g_nunits < MAX_UNITS) {     /* новый файл: юнит появляется и стартует */
            unit_t *u = &g_units[g_nunits++];
            *u = *nu;
            log_ev(u, "unit-added", NULL);
            if (u->sign[0])
                log_ev(u, "unit-sign", "\"old\":null,\"new\":\"%s\",\"mtime\":%lld",
                       u->sign, u->sign_mtime);
            added++;
            cgroup_room(u);                    /* комнатка или честный отказ (Ст. 15) */
            if (!u->ctl_down) spawn_unit(u);
        } else
            fprintf(stderr, "agryp: reload: %s: потолок MAX_UNITS — юнит пропущен\n", nu->name);
    }
    for (i = 0; i < g_nunits; i++) {           /* файл удалён: graceful-stop по Ст. 9 */
        unit_t *u = &g_units[i];
        int found = 0;

        for (j = 0; j < nfresh; j++)
            if (!strcmp(u->name, fresh[j].name)) { found = 1; break; }
        if (!found && !u->retired) {
            removed++;
            u->retired = 1; u->restart = R_NO; /* жизни больше нет — лестница не важна */
            log_ev(u, "unit-removed", NULL);
            if (u->sign[0])
                log_ev(u, "unit-sign", "\"old\":\"%s\",\"new\":null,\"mtime\":%lld",
                       u->sign, u->sign_mtime);
            if (u->state == U_RUNNING && u->pid > 0) {
                u->sup_kill = 1;
                if (kill(-u->pgid, SIGTERM) < 0) kill(u->pid, SIGTERM);
            } else if (u->state != U_RUNNING)
                u->state = U_STOPPED;
        }
    }
    g_reloads++;                               /* Виток 10: счётчик — метрика */
    log_ev(NULL, "reload", "\"added\":%d,\"changed\":%d,\"removed\":%d", added, changed, removed);
}

/* ---------- главный цикл ---------- */

static void on_signal(int s) { (void)s; g_stop = 1; }

static void on_status(int s) { (void)s; }   /* пинг лишь будит poll() — EINTR */

static void on_reload(int s) { (void)s; g_hup = 1; }   /* сам reload — в главной петле */

int main(int argc, char **argv)
{
    const char *dir = "examples";
    struct sigaction sa;
    int status_mode = 0;
    int i;

    for (i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--dir") && i + 1 < argc) dir = argv[++i];
        else if (!strcmp(argv[i], "--rotate-bytes") && i + 1 < argc) {
            g_rotate_bytes = atoll(argv[++i]); /* Виток 10: демо и мелкие диски */
            if (g_rotate_bytes < 256) g_rotate_bytes = 256;
        }
        else if (!strcmp(argv[i], "status")) status_mode = 1;   /* Ст. 13: status читает файл */
        else if (!strcmp(argv[i], "metrics")) status_mode = 2;  /* Виток 10: метрики — тот же файл */
        else if (!strcmp(argv[i], "-h") || !strcmp(argv[i], "--help")) {
            printf("usage: agryp [--dir DIR] [--rotate-bytes N] | agryp status [--dir DIR] | agryp metrics [--dir DIR]\n");
            return 0;
        } else {
            fprintf(stderr, "agryp: неизвестный аргумент '%s'\n", argv[i]);
            return 2;
        }
    }

    if (status_mode == 1) return print_status(dir);
    if (status_mode == 2) {                    /* Виток 10: .prom — тот же файл-договор */
        char mpath[1152];
        FILE *f;
        char line[2048];

        snprintf(mpath, sizeof mpath, "%s/.agryp-metrics.prom", dir);
        f = fopen(mpath, "r");
        if (!f) {
            fprintf(stderr, "agryp: супервизор не запущен (нет %s)\n", mpath);
            return 1;
        }
        while (fgets(line, sizeof line, f)) fputs(line, stdout);
        fclose(f);
        return 0;
    }
    snprintf(g_status_path, sizeof g_status_path, "%s/.agryp-status", dir);
    snprintf(g_report_path, sizeof g_report_path, "%s/.agryp-report", dir);
    snprintf(g_ctl_dir, sizeof g_ctl_dir, "%s/.agryp-ctl", dir);
    snprintf(g_units_dir, sizeof g_units_dir, "%s", dir);  /* Виток 11: ready-файлы рядом с юнитами */
    snprintf(g_journal_path, sizeof g_journal_path, "%s/.agryp-journal.ndjson", dir);
    snprintf(g_metrics_path, sizeof g_metrics_path, "%s/.agryp-metrics.prom", dir);
    g_journal = fopen(g_journal_path, "a");
    if (g_journal) {
        fseek(g_journal, 0, SEEK_END);
        g_journal_bytes = ftell(g_journal);
    } else
        fprintf(stderr, "agryp: журнал %s не открылся: %s — события только в stdout\n",
                g_journal_path, strerror(errno));
    g_t0 = now_ms();

    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_signal;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;                 /* без SA_RESTART: poll() получит EINTR */
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT,  &sa, NULL);
    sa.sa_handler = on_status;
    sigaction(SIGUSR1, &sa, NULL);   /* Ст. 13: пинг будит цикл, статус и так свежий */
    sigaction(SIGUSR2, &sa, NULL);   /* тикет 009: токен-рапорт в файле — будим немедленно */
    sa.sa_handler = on_reload;
    sigaction(SIGHUP, &sa, NULL);    /* Виток 6: daemon-reload без смерти детей */
    signal(SIGPIPE, SIG_IGN);

    /* O_APPEND на открытый файл stdout: флаг наследуется детьми через fork+exec,
     * и все записи (наши JSON-строки и вывод агентов) атомарно идут в конец.
     * Без него stdio родителя пишет по своей устаревшей позиции, пока дети
     * уехали вперёд, — в логе появляются разреженные дыры из NUL-байтов. */
    int out_flags = fcntl(STDOUT_FILENO, F_GETFL, 0);
    if (out_flags >= 0)
        fcntl(STDOUT_FILENO, F_SETFL, out_flags | O_APPEND);

    load_units(dir);
    if (g_nunits == 0) {
        fprintf(stderr, "agryp: в каталоге %s нет юнитов *.agent\n", dir);
        return 2;
    }
    log_ev(NULL, "boot", "\"units\":%d,\"dir\":\"%s\",\"rotate_bytes\":%lld", g_nunits, dir, g_rotate_bytes);
    for (i = 0; i < g_nunits; i++)             /* Виток 10: подпись каждого договора при boot */
        if (g_units[i].sign[0])
            log_ev(&g_units[i], "unit-sign", "\"old\":null,\"new\":\"%s\",\"mtime\":%lld",
                   g_units[i].sign, g_units[i].sign_mtime);
    if (prctl(PR_SET_CHILD_SUBREAPER, 1, 0, 0, 0) == 0)
        log_ev(NULL, "subreaper", "\"on\":true");
    else
        log_ev(NULL, "subreaper", "\"on\":false,\"errno\":%d", errno);
    cgroup_init();                     /* Ст. 15: комнаты или честный отказ — до первого spawn */
    poll_ctl();                        /* Виток 5: .down с прошлой жизни — юнит мёртв до снятия */
    for (i = 0; i < g_nunits; i++) if (!g_units[i].ctl_down) spawn_unit(&g_units[i]);

    while (!g_stop) {
        long long timeout = 250;

        write_status();                /* Ст. 13: файл статуса всегда свежий */
        write_metrics();               /* Виток 10: .prom всегда свежий */
        if (g_journal && g_journal_bytes >= g_rotate_bytes)
            journal_rotate();          /* Виток 10: отрезали хвост — печать в новом */
        reap();
        poll_ctl();                    /* Виток 5: файлы-договоры — казнь/заморозка/ctl-up */
        poll_ready();                  /* Виток 11: ready-файлы — готовность вслух */
        if (g_hup) {                   /* Виток 6: перечитать договоры без смерти детей */
            g_hup = 0;
            do_reload(dir);
        }

        /* выход из cooldown */
        long long now = now_ms();
        for (i = 0; i < g_nunits; i++) {
            unit_t *u = &g_units[i];
            if (u->state == U_COOLDOWN && now >= u->next_start_ms && !u->ctl_down)
                spawn_unit(u);
        }

        collect_tokens();              /* Ст. 14: съели отчёт агентов */

        /* бюджет: попытка вышла за лимит — SIGKILL */
        now = now_ms();
        for (i = 0; i < g_nunits; i++) {
            unit_t *u = &g_units[i];
            if (u->state == U_RUNNING && u->deadline_ms > 0 && u->pid > 0) {
                long long left = u->deadline_ms - now;
                if (left <= 0) {
                    u->budget_kills++;
                    u->sup_kill = 1;
                    log_ev(u, "budget-kill", "\"pid\":%d,\"attempt\":%d",
                           (int)u->pid, u->attempts);
                    if (kill(-u->pgid, SIGKILL) < 0)
                        kill(u->pid, SIGKILL);   /* группа уже пуста — по pid */
                    u->deadline_ms = 0;      /* не бьём второй раз */
                } else if (left < timeout) {
                    timeout = left;
                }
            }
        }
        /* токен: перерос token-budget — SIGKILL группы (Ст. 14) */
        for (i = 0; i < g_nunits; i++) {
            unit_t *u = &g_units[i];
            if (u->state == U_RUNNING && u->token_budget > 0 &&
                u->tokens >= u->token_budget) {
                u->token_kills++;
                u->sup_kill = 1;
                log_ev(u, "token-kill", "\"tokens\":%d,\"budget\":%d",
                       u->tokens, u->token_budget);
                if (kill(-u->pgid, SIGKILL) < 0)
                    kill(u->pid, SIGKILL);
                u->tokens = 0;
            }
        }
        if (g_stop) break;
        poll(NULL, 0, (int)timeout);
    }

    /* graceful shutdown: TERM → ждём → KILL */
    log_ev(NULL, "shutdown", "\"reason\":\"signal\"");
    for (i = 0; i < g_nunits; i++)
        if (g_units[i].state == U_RUNNING && g_units[i].pid > 0)
            if (kill(-g_units[i].pgid, SIGTERM) < 0)
                kill(g_units[i].pid, SIGTERM);

    long long deadline = now_ms() + GRACE_MS;
    for (;;) {
        int running = 0;
        reap();
        for (i = 0; i < g_nunits; i++)
            if (g_units[i].state == U_RUNNING) running++;
        if (!running || now_ms() >= deadline) break;
        poll(NULL, 0, 50);
    }
    for (i = 0; i < g_nunits; i++)
        if (g_units[i].state == U_RUNNING && g_units[i].pid > 0)
            if (kill(-g_units[i].pgid, SIGKILL) < 0)
                kill(g_units[i].pid, SIGKILL);
    reap();

    for (i = 0; i < g_nunits; i++) {
        unit_t *u = &g_units[i];
        log_ev(u, "summary",
               "\"attempts\":%d,\"exits_ok\":%d,\"exits_fail\":%d,"
               "\"budget_kills\":%d,\"token_kills\":%d,\"tokens_total\":%d,"
               "\"restarts\":%d",
               u->attempts, u->exits_ok, u->exits_fail,
               u->budget_kills, u->token_kills, u->tokens_total, u->restarts);
    }
    log_ev(NULL, "uptime-ms", "\"value\":%lld", now_ms() - g_t0);
    unlink(g_status_path);   /* Ст. 13: мёртвый PID 1 не притворяется живым */
    unlink(g_report_path);
    unlink(g_metrics_path);  /* Виток 10: и метрики мёртвого — тоже не метрики */
    if (g_journal) { fclose(g_journal); g_journal = NULL; }  /* журнал живёт — история не unlink */
    return 0;
}
