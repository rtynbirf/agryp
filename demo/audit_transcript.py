#!/usr/bin/env python3
"""Аудитор демо-транскрипта agryp (Ст. 6 конституции: «журнал не лжёт»).

Сверяет итоговые счётчики summary с полной хронологией событий и
проверяет дисциплину жизненного цикла:

  1. без NUL-байтов; строки журнала супервизора (префикс `{"ts":`)
     обязаны разбираться как JSON; прочие строки — вывод агентов,
     он живёт в том же файле (O_APPEND, см. README);
  2. монотонность: ts и up_ms не убывают;
  3. первый event — boot; есть shutdown; после shutdown только
     exit / summary / uptime-ms;
  4. на юнит:
       - попытки нумеруются подряд 1, 2, 3... и не перекрываются
         (новый spawn только после exit предыдущего);
       - каждый budget-kill / token-kill подтверждён exit-ом по сигналу 9;
       - exits_ok == число exit с ok:true, exits_fail == с ok:false;
  5. каждый счётчик summary == числу событий в потоке;
  6. summary есть по каждому юниту, ровно по одному, uptime-ms — последним;
  7. лестница перезапуска (Ст. 8): в каждом restart поле backoff_ms равно
     cooldown-ms юнита, удвоенному (streak-1) раз до потолка BACKOFF_CAP_MS
     (константы сверены с #define в src/agryp.c); streak либо сброс (0/1),
     либо +1 к предыдущему;
  8. failed (Ст. 8) — терминален: streak == CRASH_LIMIT, после него
     спавнов юнита не бывает.
  9. ctl-дисциплина (Виток 5, Ст. 13): spawn при живом .down невозможен;
     ctl-up без ctl-down — ложь; казнённая ctl-down попытка обязана
     получить exit и остановиться с reason ctl-down.

Успех: печатает OK и сводку, код выхода 0. Иначе — список нарушений, код 1.
"""
import glob
import json
import os
import sys

ALLOWED_AFTER_SHUTDOWN = {"exit", "summary", "uptime-ms", "reap-orphan", "finish"}
VALID_EVENTS = {
    "boot", "spawn", "spawn-fail", "exit", "restart", "stopped", "failed",
    "budget-kill", "token-kill", "ctl-down", "ctl-up", "ctl-drop", "ctl-kill",
    "cgroup-skip", "report-drop", "subreaper", "reap-orphan", "shutdown",
    "summary", "uptime-ms", "finish", "reload", "unit-added", "unit-removed",
}
# константы Ст. 8 — сверены с #define в src/agryp.c
BACKOFF_CAP_MS = 30000
CRASH_LIMIT = 5


def fail(errors, idx, msg):
    errors.append(f"строка {idx + 1}: {msg}")


def load_unit_configs(repo_root):
    """cooldown-ms из *.agent — база лестницы (Ст. 8); finish — хук (Виток 6).
    Юниты лежат в examples/ и в каталогах демо — аудитор читает все сразу."""
    cfgs = {}
    for sub in ("examples", "demo/ctl-units", "demo/finish-units", "demo/reload-units"):
        for p in sorted(glob.glob(os.path.join(repo_root, sub, "*.agent"))):
            cfg = {}
            with open(p, encoding="utf-8") as f:
                for ln in f:
                    ln = ln.strip()
                    if not ln or ln.startswith("#") or "=" not in ln:
                        continue
                    k, v = ln.split("=", 1)
                    cfg[k.strip()] = v.strip()
            cfgs[p.rsplit("/", 1)[-1][:-6]] = cfg
    return cfgs


def main(path):
    errors = []
    cfgs = load_unit_configs(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    with open(path, "rb") as f:
        raw = f.read()

    if b"\x00" in raw:
        errors.append("найдены NUL-байты — журнал с дырами (нарушен O_APPEND)")

    events = []
    agent_lines = 0
    for idx, line in enumerate(raw.decode("utf-8").splitlines()):
        if not line.strip():
            continue
        if not line.startswith('{"ts":'):
            agent_lines += 1   # вывод агентов в том же файле рядом с журналом
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError as e:
            fail(errors, idx, f"битая строка журнала: {e}")
            continue
        if "up_ms" not in ev or "event" not in ev:
            fail(errors, idx, f"нет up_ms/event: {line[:80]}")
            continue
        if ev["event"] not in VALID_EVENTS:
            fail(errors, idx, f"неизвестное событие '{ev['event']}'")
        events.append((idx, ev))

    if errors:
        report(errors)
        return 1

    prev_ts = prev_up = None
    shutdown_idx = None
    for idx, ev in events:
        ts, up = ev["ts"], ev["up_ms"]
        if prev_ts is not None:
            if ts < prev_ts:
                fail(errors, idx, f"ts убывает: {prev_ts} → {ts}")
            if up < prev_up:
                fail(errors, idx, f"up_ms убывает: {prev_up} → {up}")
        prev_ts, prev_up = ts, up

        if ev["event"] == "boot":
            if idx != events[0][0]:
                fail(errors, idx, "boot не первым событием")
        if ev["event"] == "shutdown":
            if shutdown_idx is not None:
                fail(errors, idx, "второй shutdown")
            shutdown_idx = idx
        elif shutdown_idx is not None and ev["event"] not in ALLOWED_AFTER_SHUTDOWN:
            fail(errors, idx, f"'{ev['event']}' после shutdown")
    if shutdown_idx is None:
        errors.append("нет события shutdown — прогон не завершён graceful")

    # хронология по юнитам
    units = {}
    for idx, ev in events:
        name = ev.get("unit")
        if name is None:
            continue
        u = units.setdefault(name, {
            "spawns": [], "exits": [], "restarts": 0, "stopped": 0,
            "budget_kills": 0, "token_kills": 0, "running": False, "ok_exits": 0,
            "streak": None, "failed": False,
            "ctl_down": False, "ctl_e0": None, "expect_stop": None,
            "finishes": [], "retired": False, "added": False,
        })
        et = ev["event"]
        if et == "spawn":
            if u["retired"]:
                fail(errors, idx,
                     f"spawn юнита {name} после unit-removed — жизни больше нет (Виток 6)")
            if u["ctl_down"]:
                fail(errors, idx,
                     f"spawn юнита {name} при живом .down — политика заморожена (Ст. 13)")
            if u["running"]:
                fail(errors, idx, f"spawn юнита {name} поверх живой попытки")
            if u["failed"]:
                fail(errors, idx, f"spawn юнита {name} после терминального failed")
            u["running"] = True
            u["spawns"].append((idx, ev.get("attempt")))
        elif et == "exit":
            if not u["running"]:
                fail(errors, idx, f"exit юнита {name} без живой попытки")
            u["running"] = False
            u["exits"].append((idx, ev.get("ok")))
            if ev.get("ok") is True:
                u["ok_exits"] += 1
        elif et == "finish":
            if not u["exits"]:
                fail(errors, idx, f"finish юнита {name} без смерти попытки — журнал лжёт")
            u["finishes"].append(idx)
        elif et == "restart":
            u["restarts"] += 1
            streak, backoff = ev.get("streak"), ev.get("backoff_ms")
            base = int(cfgs.get(name, {}).get("cooldown-ms", "1000"))
            if not isinstance(streak, int) or not isinstance(backoff, int):
                fail(errors, idx, f"{name}: restart без backoff_ms/streak")
            else:
                want = base if streak <= 1 else min(base * 2 ** (streak - 1), BACKOFF_CAP_MS)
                if backoff != want:
                    fail(errors, idx,
                         f"{name}: ступень лестницы backoff_ms={backoff}, а по конфигу {want}")
                prev = u["streak"]
                if prev is not None and streak not in (0, 1, prev, prev + 1):
                    fail(errors, idx,
                         f"{name}: streak={streak} после {prev} — лестница нарушена")
                u["streak"] = streak
        elif et == "failed":
            u["failed"] = True
            if ev.get("streak") != CRASH_LIMIT:
                fail(errors, idx,
                     f"{name}: failed при streak={ev.get('streak')}, а fuse — {CRASH_LIMIT}")
        elif et == "unit-added":
            u["added"] = True
        elif et == "unit-removed":
            u["retired"] = True               # файл удалён: спавнов быть не должно
            if u["running"]:
                u["expect_stop"] = "reload"   # graceful-stop по Ст. 9
        elif et == "ctl-down":
            if u["ctl_down"]:
                fail(errors, idx, f"{name}: второй ctl-down без ctl-up")
            u["ctl_down"] = True
            if u["running"]:              # казнь ещё не отработала — ждём exit
                u["ctl_e0"] = len(u["exits"])
                u["expect_stop"] = "ctl-down"
        elif et == "ctl-up":
            if not u["ctl_down"]:
                fail(errors, idx, f"{name}: ctl-up без ctl-down — журнал лжёт")
            if u["ctl_e0"] is not None and len(u["exits"]) == u["ctl_e0"]:
                fail(errors, idx, f"{name}: ctl-down казнил попытку, но exit не пришёл")
            u["ctl_down"] = False
            u["ctl_e0"] = None
        elif et == "stopped":
            u["stopped"] += 1
            if u["expect_stop"] is not None:
                if ev.get("reason") != u["expect_stop"]:
                    fail(errors, idx,
                         f"{name}: stopped reason={ev.get('reason')}, а обязан '{u['expect_stop']}'")
                u["expect_stop"] = None
        elif et == "budget-kill":
            u["budget_kills"] += 1
        elif et == "token-kill":
            u["token_kills"] += 1
        elif et == "summary":
            u.setdefault("summary", []).append((idx, ev))

    for name, u in sorted(units.items()):
        attempts = [a for _, a in u["spawns"]]
        if attempts != list(range(1, len(attempts) + 1)):
            fail(errors, 0, f"{name}: номера попыток не подряд: {attempts}")

        # finish-хук (Виток 6): у юнита с объявленным finish — хук после КАЖДОЙ смерти
        if cfgs.get(name, {}).get("finish", "").strip():
            if len(u["finishes"]) != len(u["exits"]):
                fail(errors, 0, f"{name}: finish-хуков {len(u['finishes'])}, а смертей {len(u['exits'])} — что-то убрано молча")
            for (eidx, _), fidx in zip(u["exits"], u["finishes"]):
                if fidx < eidx:
                    fail(errors, fidx, f"{name}: finish раньше своей смерти — хронология лжёт")

        # каждый budget-kill / token-kill / ctl-kill → последующий exit того же юнита
        for kidx, kev in events:
            if kev.get("unit") == name and kev["event"] in ("budget-kill", "token-kill", "ctl-kill"):
                if not any(eidx > kidx for eidx, _ in u["exits"]):
                    fail(errors, kidx, f"{name}: {kev['event']} без последующего exit")

        if len(u["spawns"]) != len(u["exits"]):
            fail(errors, 0, f"{name}: spawn'ов {len(u['spawns'])}, exit'ов {len(u['exits'])}")

        if "summary" in u:
            if len(u["summary"]) != 1:
                fail(errors, 0, f"{name}: summary {len(u['summary'])} раз, а не 1")
            else:
                _, s = u["summary"][0]
                checks = {
                    "attempts": len(u["spawns"]),
                    "restarts": u["restarts"],
                    "budget_kills": u["budget_kills"],
                    "token_kills": u["token_kills"],
                }
                for key, expect in checks.items():
                    if s.get(key) != expect:
                        fail(errors, 0,
                             f"{name}: summary.{key}={s.get(key)}, в потоке {expect}")
                if s.get("exits_ok") != u["ok_exits"]:
                    fail(errors, 0,
                         f"{name}: summary.exits_ok={s.get('exits_ok')}, в потоке {u['ok_exits']}")
                n_fail = sum(1 for _, ok in u["exits"] if ok is False)
                if s.get("exits_fail") != n_fail:
                    fail(errors, 0,
                         f"{name}: summary.exits_fail={s.get('exits_fail')}, в потоке {n_fail}")
                # каждый exit ДО shutdown обязан получить restart или stopped;
                # exit-ы во время shutdown (после события shutdown) — исключение
                n_exit_before = sum(
                    1 for eidx, _ in u["exits"]
                    if shutdown_idx is not None and eidx < shutdown_idx
                )
                if u["restarts"] + u["stopped"] != n_exit_before:
                    fail(errors, 0,
                         f"{name}: restarts({u['restarts']})+stopped({u['stopped']}) "
                         f"≠ exit'ов до shutdown ({n_exit_before})")

    if not units:
        errors.append("в транскрипте нет ни одного юнита")

    # SIGHUP-reload (Виток 6): числа события обязаны сходиться с юнит-событиями
    reloads = [e for _, e in events if e["event"] == "reload"]
    if len(reloads) == 1:
        n_add = sum(1 for _, e in events if e["event"] == "unit-added")
        n_rem = sum(1 for _, e in events if e["event"] == "unit-removed")
        if reloads[0].get("added") != n_add or reloads[0].get("removed") != n_rem:
            fail(errors, 0,
                 f"reload лжёт: added={reloads[0].get('added')} (unit-added {n_add}), "
                 f"removed={reloads[0].get('removed')} (unit-removed {n_rem})")

    tail = [ev["event"] for _, ev in events[-len(units) - 1:]]
    if "uptime-ms" not in tail:
        errors.append("uptime-ms не в хвосте транскрипта")

    report(errors, events, units, agent_lines)
    return 0 if not errors else 1


def report(errors, events=None, units=None, agent_lines=0):
    if errors:
        print(f"FAIL: {len(errors)} нарушений:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    n_units = len(units) if units else 0
    print(f"OK: {len(events)} событий журнала + {agent_lines} строк агентов, "
          f"{n_units} юнит(ов), журнал не лжёт.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: audit_transcript.py <demo-transcript.jsonl>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
