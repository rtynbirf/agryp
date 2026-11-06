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
       - каждый budget-kill подтверждён exit-ом по сигналу 9;
       - exits_ok == число exit с ok:true, exits_fail == с ok:false;
  5. каждый счётчик summary == числу событий в потоке;
  6. summary есть по каждому юниту, ровно по одному, uptime-ms — последним.

Успех: печатает OK и сводку, код выхода 0. Иначе — список нарушений, код 1.
"""
import json
import sys

ALLOWED_AFTER_SHUTDOWN = {"exit", "summary", "uptime-ms"}
VALID_EVENTS = {
    "boot", "spawn", "spawn-fail", "exit", "restart", "stopped",
    "budget-kill", "shutdown", "summary", "uptime-ms",
}


def fail(errors, idx, msg):
    errors.append(f"строка {idx + 1}: {msg}")


def main(path):
    errors = []
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
            "budget_kills": 0, "running": False, "ok_exits": 0,
        })
        et = ev["event"]
        if et == "spawn":
            if u["running"]:
                fail(errors, idx, f"spawn юнита {name} поверх живой попытки")
            u["running"] = True
            u["spawns"].append((idx, ev.get("attempt")))
        elif et == "exit":
            if not u["running"]:
                fail(errors, idx, f"exit юнита {name} без живой попытки")
            u["running"] = False
            u["exits"].append((idx, ev.get("ok")))
            if ev.get("ok") is True:
                u["ok_exits"] += 1
        elif et == "restart":
            u["restarts"] += 1
        elif et == "stopped":
            u["stopped"] += 1
        elif et == "budget-kill":
            u["budget_kills"] += 1
        elif et == "summary":
            u.setdefault("summary", []).append((idx, ev))

    for name, u in sorted(units.items()):
        attempts = [a for _, a in u["spawns"]]
        if attempts != list(range(1, len(attempts) + 1)):
            fail(errors, 0, f"{name}: номера попыток не подряд: {attempts}")

        # каждый budget-kill → последующий exit того же юнита
        for kidx, kev in events:
            if kev.get("unit") == name and kev["event"] == "budget-kill":
                if not any(eidx > kidx for eidx, _ in u["exits"]):
                    fail(errors, kidx, f"{name}: budget-kill без последующего exit")

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
                # graceful-финал: последний exit не перезапущен
                if u["restarts"] + u["stopped"] != len(u["exits"]) - 1:
                    fail(errors, 0,
                         f"{name}: restarts({u['restarts']})+stopped({u['stopped']}) "
                         f"≠ exits-1({len(u['exits']) - 1})")

    if not units:
        errors.append("в транскрипте нет ни одного юнита")

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
