/*
 * agryp — минимальный супервизор (PID 1) для AI-агентов.
 *
 * Один файл. Только libc. Ноль зависимостей. Этика LFS:
 * агент — это процесс первого класса, у которого есть
 * политика перезапуска и бюджет попытки, а не «табличка в терминале».
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
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#define MAX_UNITS 64
#define NAME_LEN  64
#define EXEC_LEN  512
#define GRACE_MS  3000   /* время на вежливую смерть при SIGTERM */

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
    /* рантайм */
    state_t   state;
    pid_t     pid;
    long long deadline_ms;   /* дедлайн бюджета текущей попытки */
    long long next_start_ms; /* когда выходить из cooldown */
    int       attempts;
    int       exits_ok;
    int       exits_fail;
    int       budget_kills;
    int       restarts;
} unit_t;

static unit_t g_units[MAX_UNITS];
static int    g_nunits = 0;
static volatile sig_atomic_t g_stop = 0;

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
        execl("/bin/sh", "sh", "-c", u->exec, (char *)NULL);
        _exit(127);
    }
    u->pid         = p;
    u->state       = U_RUNNING;
    u->attempts++;
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

    int want = (u->restart == R_ALWAYS) ||
               (u->restart == R_ON_FAILURE && !ok);
    if (want && (u->max_attempts == 0 || u->attempts < u->max_attempts)) {
        u->state = U_COOLDOWN;
        u->next_start_ms = now_ms() + u->cooldown_ms;
        u->restarts++;
        log_ev(u, "restart", "\"next_attempt\":%d,\"cooldown_ms\":%d",
               u->attempts + 1, u->cooldown_ms);
    } else {
        u->state = U_STOPPED;
        log_ev(u, "stopped", "\"reason\":\"%s\"",
               want ? "max-attempts" : "policy");
    }
}

static void reap(void)
{
    for (;;) {
        int status;
        pid_t p = waitpid(-1, &status, WNOHANG);
        int i;

        if (p <= 0) break;
        for (i = 0; i < g_nunits; i++) {
            if (g_units[i].pid == p) { handle_exit(&g_units[i], status); break; }
        }
    }
}

/* ---------- главный цикл ---------- */

static void on_signal(int s) { (void)s; g_stop = 1; }

int main(int argc, char **argv)
{
    const char *dir = "examples";
    struct sigaction sa;
    long long t0 = now_ms();
    int i;

    for (i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--dir") && i + 1 < argc) dir = argv[++i];
        else if (!strcmp(argv[i], "-h") || !strcmp(argv[i], "--help")) {
            printf("usage: agryp [--dir DIR]\n");
            return 0;
        } else {
            fprintf(stderr, "agryp: неизвестный аргумент '%s'\n", argv[i]);
            return 2;
        }
    }

    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_signal;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;                 /* без SA_RESTART: poll() получит EINTR */
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT,  &sa, NULL);
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

    for (i = 0; i < g_nunits; i++) spawn_unit(&g_units[i]);

    while (!g_stop) {
        long long timeout = 250;

        reap();

        /* выход из cooldown */
        long long now = now_ms();
        for (i = 0; i < g_nunits; i++) {
            unit_t *u = &g_units[i];
            if (u->state == U_COOLDOWN && now >= u->next_start_ms)
                spawn_unit(u);
        }

        /* бюджет: попытка вышла за лимит — SIGKILL */
        now = now_ms();
        for (i = 0; i < g_nunits; i++) {
            unit_t *u = &g_units[i];
            if (u->state == U_RUNNING && u->deadline_ms > 0 && u->pid > 0) {
                long long left = u->deadline_ms - now;
                if (left <= 0) {
                    u->budget_kills++;
                    log_ev(u, "budget-kill", "\"pid\":%d,\"attempt\":%d",
                           (int)u->pid, u->attempts);
                    kill(u->pid, SIGKILL);
                    u->deadline_ms = 0;      /* не бьём второй раз */
                } else if (left < timeout) {
                    timeout = left;
                }
            }
        }
        if (g_stop) break;
        poll(NULL, 0, (int)timeout);
    }

    /* graceful shutdown: TERM → ждём → KILL */
    log_ev(NULL, "shutdown", "\"reason\":\"signal\"");
    for (i = 0; i < g_nunits; i++)
        if (g_units[i].state == U_RUNNING && g_units[i].pid > 0)
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
            kill(g_units[i].pid, SIGKILL);
    reap();

    for (i = 0; i < g_nunits; i++) {
        unit_t *u = &g_units[i];
        log_ev(u, "summary",
               "\"attempts\":%d,\"exits_ok\":%d,\"exits_fail\":%d,"
               "\"budget_kills\":%d,\"restarts\":%d",
               u->attempts, u->exits_ok, u->exits_fail,
               u->budget_kills, u->restarts);
    }
    log_ev(NULL, "uptime-ms", "\"value\":%lld", now_ms() - t0);
    return 0;
}
