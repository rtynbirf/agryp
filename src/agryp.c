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
#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#define MAX_UNITS 64
#define NAME_LEN  64
#define EXEC_LEN  512
#define CG_BASE_LEN 512 /* потолок пути делегированной ветки cgroup (Ст. 11) */
#define GRACE_MS  3000   /* время на вежливую смерть при SIGTERM */
#define SUSTAIN_MS     10000 /* «проработал» гасит лестницу перезапуска (Ст. 8) */
#define BACKOFF_CAP_MS 30000 /* потолок лестницы перезапуска (Ст. 8) */
#define CRASH_LIMIT    5     /* подряд своих смертей → терминальный failed (Ст. 8) */

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
    long long run_started_ms; /* старт текущей попытки: «проработал» меряем от неё */
} unit_t;

static unit_t g_units[MAX_UNITS];
static int    g_nunits = 0;
static volatile sig_atomic_t g_stop = 0;
static char g_status_path[1152];  /* Ст. 13: снимок состояния — файл, не сокет */
static char g_report_path[1152];  /* Ст. 14: сюда агенты отдают burn-rate */
static char g_cgbase[CG_BASE_LEN]; /* Ст. 15: наша делегированная ветка cgroup v2 */
static long long g_t0;

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

static void log_ev(const unit_t *u, const char *event, const char *fmt, ...)
{
    char tsbuf[32], extra[256];
    va_list ap;

    va_start(ap, fmt);
    if (fmt) vsnprintf(extra, sizeof extra, fmt, ap);
    else     extra[0] = '\0';
    va_end(ap);

    wall_ts(tsbuf, sizeof tsbuf);
    if (u && extra[0])
        printf("{\"ts\":\"%s\",\"up_ms\":%lld,\"unit\":\"%s\",\"event\":\"%s\",%s}\n",
               tsbuf, now_ms(), u->name, event, extra);
    else if (u)
        printf("{\"ts\":\"%s\",\"up_ms\":%lld,\"unit\":\"%s\",\"event\":\"%s\"}\n",
               tsbuf, now_ms(), u->name, event);
    else if (extra[0])
        printf("{\"ts\":\"%s\",\"up_ms\":%lld,\"event\":\"%s\",%s}\n",
               tsbuf, now_ms(), event, extra);
    else
        printf("{\"ts\":\"%s\",\"up_ms\":%lld,\"event\":\"%s\"}\n",
               tsbuf, now_ms(), event);
    fflush(stdout);
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
        char path[1024], line[1024];
        FILE *f;
        unit_t u;
        int lineno = 0;

        if (len < 7 || strcmp(de->d_name + len - 6, ".agent")) continue;
        snprintf(path, sizeof path, "%s/%s", dir, de->d_name);
        f = fopen(path, "r");
        if (!f) continue;

        memset(&u, 0, sizeof u);
        u.restart     = R_ALWAYS;
        u.cooldown_ms = 1000;
        snprintf(u.name, sizeof u.name, "%.*s", (int)(len - 6), de->d_name);

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
            if      (!strcmp(key, "name"))         snprintf(u.name, sizeof u.name, "%.60s", val);
            else if (!strcmp(key, "exec"))         snprintf(u.exec, sizeof u.exec, "%.500s", val);
            else if (!strcmp(key, "restart")) {
                if (parse_restart(val, &u.restart))
                    fprintf(stderr, "agryp: %s:%d: неизвестный restart '%s'\n", path, lineno, val);
            }
            else if (!strcmp(key, "budget-sec"))   u.budget_sec   = atoi(val);
            else if (!strcmp(key, "cooldown-ms"))  u.cooldown_ms  = atoi(val);
            else if (!strcmp(key, "max-attempts")) u.max_attempts = atoi(val);
            else if (!strcmp(key, "token-budget")) u.token_budget = atoi(val);
            else if (!strcmp(key, "mem-max-mb"))   u.mem_max_mb   = atoi(val);
            else fprintf(stderr, "agryp: %s:%d: неизвестный ключ '%s'\n", path, lineno, key);
        }
        fclose(f);

        if (!u.exec[0]) {
            fprintf(stderr, "agryp: %s: ключ exec не задан — юнит пропущен\n", path);
            continue;
        }
        g_units[g_nunits++] = u;
    }
    closedir(d);
}

/* ---------- жизнь юнита ---------- */

static void spawn_unit(unit_t *u)
{
    pid_t p = fork();

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
    u->pid         = p;
    u->pgid        = p;
    u->state       = U_RUNNING;
    u->attempts++;
    u->run_started_ms = now_ms();
    u->tokens      = 0;
    u->deadline_ms = (u->budget_sec > 0)
                     ? now_ms() + (long long)u->budget_sec * 1000LL
                     : 0;
    log_ev(u, "spawn", "\"pid\":%d,\"attempt\":%d,\"budget_sec\":%d",
           (int)p, u->attempts, u->budget_sec);
}

static void handle_exit(unit_t *u, int status)
{
    int code = WIFEXITED(status)   ? WEXITSTATUS(status) : -1;
    int sig  = WIFSIGNALED(status) ? WTERMSIG(status)    : 0;
    int ok   = WIFEXITED(status) && WEXITSTATUS(status) == 0;

    if (ok) u->exits_ok++; else u->exits_fail++;
    u->pid = 0;

    if (sig) log_ev(u, "exit", "\"by_signal\":%d,\"ok\":%s", sig, ok ? "true" : "false");
    else     log_ev(u, "exit", "\"code\":%d,\"ok\":%s",       code, ok ? "true" : "false");

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

    int want = (u->restart == R_ALWAYS) ||
               (u->restart == R_ON_FAILURE && !ok);
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
        log_ev(u, "stopped", "\"reason\":\"%s\"",
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
        if (!known)                            /* subreaper: усыновлённого хороним вслух */
            log_ev(NULL, "reap-orphan", "\"pid\":%d,\"code\":%d", (int)p,
                   WIFEXITED(status) ? WEXITSTATUS(status) : -1);
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
                   "\"mem_max_mb\":%d,\"attempts\":%d,\"exits_ok\":%d,"
                   "\"exits_fail\":%d,\"budget_kills\":%d,\"token_kills\":%d,"
                   "\"restarts\":%d,\"streak\":%d}\n",
                u->name, state_name(u->state), (int)u->pid, u->attempts,
                u->budget_sec, u->token_budget, u->tokens, u->mem_max_mb,
                u->attempts, u->exits_ok, u->exits_fail,
                u->budget_kills, u->token_kills, u->restarts, u->fail_streak);
    }
    fclose(f);
    rename(tmp, g_status_path);
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

/* ---------- память: клетка cgroup v2 в собственной ветке (Ст. 15) ---------- */

/* Правило одного писателя в делегированном дереве cgroups: agryp строит
 * комнаты только внутри собственной ветки (/proc/self/cgroup). Среда не
 * даёт cgroups — loud cgroup-skip и работа дальше; молчаливой усечки нет. */
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
    for (i = 0; i < g_nunits; i++) {
        unit_t *u = &g_units[i];
        char dir[1200], val[1280], mbuf[32];
        int fd, m;

        if (u->mem_max_mb <= 0) continue;
        snprintf(dir, sizeof dir, "%.480s/agryp-%.63s", g_cgbase, u->name);
        snprintf(val, sizeof val, "%.1180s/memory.max", dir);
        if ((mkdir(dir, 0755) && errno != EEXIST) || (fd = open(val, O_WRONLY)) < 0)
            goto deny;
        m = snprintf(mbuf, sizeof mbuf, "%dM", u->mem_max_mb);
        if (write(fd, mbuf, (size_t)m) != (ssize_t)m) { close(fd); goto deny; }
        close(fd);
        continue;
deny:
        log_ev(u, "cgroup-skip", "\"reason\":\"cgroupfs недоступен\",\"errno\":%d", errno);
        u->mem_max_mb = 0;
    }
}

/* ---------- главный цикл ---------- */

static void on_signal(int s) { (void)s; g_stop = 1; }

static void on_status(int s) { (void)s; }   /* пинг лишь будит poll() — EINTR */

int main(int argc, char **argv)
{
    const char *dir = "examples";
    struct sigaction sa;
    int status_mode = 0;
    int i;

    for (i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--dir") && i + 1 < argc) dir = argv[++i];
        else if (!strcmp(argv[i], "status")) status_mode = 1;   /* Ст. 13: status читает файл */
        else if (!strcmp(argv[i], "-h") || !strcmp(argv[i], "--help")) {
            printf("usage: agryp [--dir DIR] | agryp status [--dir DIR]\n");
            return 0;
        } else {
            fprintf(stderr, "agryp: неизвестный аргумент '%s'\n", argv[i]);
            return 2;
        }
    }

    if (status_mode) return print_status(dir);
    snprintf(g_status_path, sizeof g_status_path, "%s/.agryp-status", dir);
    snprintf(g_report_path, sizeof g_report_path, "%s/.agryp-report", dir);
    g_t0 = now_ms();

    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_signal;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;                 /* без SA_RESTART: poll() получит EINTR */
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT,  &sa, NULL);
    sa.sa_handler = on_status;
    sigaction(SIGUSR1, &sa, NULL);   /* Ст. 13: пинг будит цикл, статус и так свежий */
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
    log_ev(NULL, "boot", "\"units\":%d,\"dir\":\"%s\"", g_nunits, dir);
    if (prctl(PR_SET_CHILD_SUBREAPER, 1, 0, 0, 0) == 0)
        log_ev(NULL, "subreaper", "\"on\":true");
    else
        log_ev(NULL, "subreaper", "\"on\":false,\"errno\":%d", errno);
    cgroup_init();                     /* Ст. 15: комнаты или честный отказ — до первого spawn */
    for (i = 0; i < g_nunits; i++) spawn_unit(&g_units[i]);

    while (!g_stop) {
        long long timeout = 250;

        write_status();                /* Ст. 13: файл статуса всегда свежий */
        reap();

        /* выход из cooldown */
        long long now = now_ms();
        for (i = 0; i < g_nunits; i++) {
            unit_t *u = &g_units[i];
            if (u->state == U_COOLDOWN && now >= u->next_start_ms)
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
    return 0;
}
