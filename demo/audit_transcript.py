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
 10. readiness (Виток 11, тикет 016): ready возможен только у живой
     попытки, один на попытку; ms — задержка от старта попытки и обязана
     сходиться с расстоянием от spawn до ready (±2 мс — такт now_ms).
 11. скобка reload→reload-done (Виток 11, тикет 017; школа
     Type=notify-reload): каждый reload обязан закрыться ровно одним
     reload-done с тем же gen и теми же числами; unit-added/unit-removed
     в окне скобки (от предыдущего reload-done до этого) сходятся с
     числами пары; скобка не переживает ни следующего reload, ни конца
     журнала.
 12. reload-kill (Виток 11, тикет 017): казнь упрямого удалённого
     подтверждена последующим exit'ом — пары kill→труп проверяются и для
     неё, скобка без трупов не закрывается.
 13. аудитор против выдумки (Виток 11, тикет 018; школа fail-closed):
     нет журнала, пуст каталог юнитов, юнит без договора, не-целые
     ts/up_ms — всё это КРАСНЫЙ с честной причиной, а не OK и не падение.
     Проверяльщик проверяет себя: make audit-neg гоняет негативные пробы
     (обязаны краснеть по делу) и канарейку (обязана быть зелёной).

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
    "cgroup-skip", "jail-skip", "report-drop", "subreaper", "reap-orphan",
    "shutdown", "summary", "uptime-ms", "finish", "reload", "reload-done",
    "reload-kill", "unit-added", "unit-removed", "unit-sign", "rotate", "ready",
}
# константы Ст. 8 — сверены с #define в src/agryp.c
BACKOFF_CAP_MS = 30000
CRASH_LIMIT = 5


def fail(errors, idx, msg):
    errors.append(f"строка {idx + 1}: {msg}")


def load_unit_configs(repo_root):
    """cooldown-ms из *.agent — база лестницы (Ст. 8); finish — хук (Виток 6).
    Юниты лежат в examples/ и в каталогах демо — аудитор читает все сразу.
    AGRY_AUDIT_UNITS — дополнительные каталоги через двоеточие (негативные
    пробы тикета 018 несут свои договоры; прод-поведение не меняют)."""
    cfgs = {}
    subs = ["examples", "demo/ctl-units", "demo/finish-units", "demo/reload-units",
            "demo/jail-units", "demo/stream-units", "demo/metrics-units",
            "demo/rotate-units", "demo/sign-units", "demo/ready-units"]
    for d in os.environ.get("AGRY_AUDIT_UNITS", "").split(":"):
        if d.strip():
            subs.append(d.strip())
    for sub in subs:
        p = sub if os.path.isabs(sub) else os.path.join(repo_root, sub)
        for p in sorted(glob.glob(os.path.join(p, "*.agent"))):
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
    if not cfgs:
        # тикет 018 (школа fail-closed): пустой каталог = нет доказательств.
        # Молчаливый дефолт cooldown-1000 — выдумка 5.2; против выдуманных
        # договоров аудитор не проверяет.
        print("FAIL: каталог юнитов пуст (*.agent не найдены) — против "
              "выдуманных договоров не проверяем (тикет 018)")
        return 1
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except OSError as e:
        print(f"FAIL: журнал не читается: {path}: {e} — нет доказательств, "
              "нет вердикта «OK» (тикет 018)")
        return 1

    try:
        raw_text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        print(f"FAIL: журнал не декодируется (utf-8): {e} — нет доказательств, нет вердикта (тикет 018)")
        return 1


    if b"\x00" in raw:
        errors.append("найдены NUL-байты — журнал с дырами (нарушен O_APPEND)")
    events = []
    agent_lines = 0
    for idx, line in enumerate(raw_text.splitlines()):
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
        if not isinstance(ev, dict) or not isinstance(ev.get("event"), str) or not isinstance(ev.get("ts"), str):
            fail(errors, idx, f"структура лжи: событие/ts не тех типов: {line[:80]}")
            continue
        if not isinstance(ev.get("up_ms"), int) or isinstance(ev.get("up_ms"), bool) or ev["up_ms"] < 0:
            fail(errors, idx, f"up_ms={ev.get('up_ms')!r} — не честное время (тикет 018)")
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
            "stopped_idx": [],
            "budget_kills": 0, "token_kills": 0, "running": False, "ok_exits": 0,
            "streak": None, "failed": False,
            "ctl_down": False, "ctl_e0": None, "expect_stop": None,
            "finishes": [], "retired": False, "added": False,
            "ready": False, "spawn_up": None,
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
            u["spawn_up"] = ev.get("up_ms")
            u["ready"] = False
        elif et == "exit":
            if not u["running"]:
                fail(errors, idx, f"exit юнита {name} без живой попытки")
            u["running"] = False
            u["ready"] = False
            u["exits"].append((idx, ev.get("ok")))
            if ev.get("ok") is True:
                u["ok_exits"] += 1
        elif et == "finish":
            if not u["exits"]:
                fail(errors, idx, f"finish юнита {name} без смерти попытки — журнал лжёт")
            u["finishes"].append(idx)
        elif et == "ready":
            if not u["running"]:
                fail(errors, idx, f"ready юнита {name} без живой попытки — готовность лжёт")
            if u["ready"]:
                fail(errors, idx, f"{name}: второй ready на одной попытке")
            ms = ev.get("ms")
            if not isinstance(ms, int) or ms < 0:
                fail(errors, idx, f"{name}: ready.ms={ms!r} — не честная задержка")
            elif u["spawn_up"] is not None:
                want = ev.get("up_ms") - u["spawn_up"]
                if abs(ms - want) > 2:
                    fail(errors, idx,
                         f"{name}: ready.ms={ms}, а от спавна прошло {want} — задержка лжёт")
            u["ready"] = True
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
            u["stopped_idx"].append(idx)
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

        # каждый budget-kill / token-kill / ctl-kill / reload-kill → последующий exit того же юнита
        for kidx, kev in events:
            if kev.get("unit") == name and kev["event"] in ("budget-kill", "token-kill", "ctl-kill", "reload-kill"):
                if not any(eidx > kidx for eidx, _ in u["exits"]):
                    fail(errors, kidx, f"{name}: {kev['event']} без последующего exit")

        if len(u["spawns"]) != len(u["exits"]):
            fail(errors, 0, f"{name}: spawn'ов {len(u['spawns'])}, exit'ов {len(u['exits'])}")

        # виток 7 (тикет 007): клетке имён положена ровно одна правда —
        # jailed в спавне или loud jail-skip; молчаливой усечки нет (Ст. 6)
        jcfg = cfgs.get(name, {}).get("jail", "").strip()
        j_spawn = sum(1 for _, e in events
                      if e.get("unit") == name and e["event"] == "spawn"
                      and e.get("jailed", 0))
        j_skip = sum(1 for _, e in events
                     if e.get("unit") == name and e["event"] == "jail-skip")
        if jcfg:
            if j_spawn and j_skip:
                fail(errors, 0, f"{name}: jailed и jail-skip одновременно — двух правд не бывает")
            if not j_spawn and not j_skip:
                fail(errors, 0, f"{name}: объявлен jail, но ни jailed, ни jail-skip — молчаливая усечка (Ст. 6)")
        elif j_spawn or j_skip:
            fail(errors, 0, f"{name}: клеточные события без объявления jail в конфиге")

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
                # каждый exit ДО shutdown обязан получить restart или stopped
                # до shutdown (Виток 11: останов перед shutdown получает stopped
                # reason shutdown; после строки shutdown похороны молчаливы);
                # exit-ы во время shutdown (после события shutdown) — исключение
                n_exit_before = sum(
                    1 for eidx, _ in u["exits"]
                    if shutdown_idx is not None and eidx < shutdown_idx
                )
                n_stopped_before = sum(
                    1 for sidx in u["stopped_idx"]
                    if shutdown_idx is not None and sidx < shutdown_idx
                )
                if u["restarts"] + n_stopped_before != n_exit_before:
                    fail(errors, 0,
                         f"{name}: restarts({u['restarts']})+stopped до shutdown "
                         f"({n_stopped_before}) ≠ exit'ов до shutdown ({n_exit_before})")

    if not units:
        errors.append("в транскрипте нет ни одного юнита")
    for name in sorted(units):
        if name in cfgs:
            continue
        # тикет 018, проба 5.2: юнит без договора — выдумка… КРОМЕ случая,
        # когда договор умер честно: unit-removed в транскрипте (демо reload
        # удаляет *.agent на живую — история длиннее каталога). Фантом без
        # договора и без смерти договора не проверяется — он выдуман.
        removed = any(e.get("unit") == name and e["event"] == "unit-removed"
                      for _, e in events)
        if not removed:
            fail(errors, 0,
                 f"юнит {name} без договора в каталоге — выдумка не проверяется (тикет 018)")

    # Скобка reload→reload-done (Виток 11, тикет 017; школа Type=notify-reload):
    # перечитывание объявляется reload'ом (числа + gen) и обязано закрыться
    # reload-done с теми же gen и числами. Окно скобки — от предыдущего
    # reload-done (или начала журнала) до закрывающего reload-done: события
    # apply-прохода (unit-added/unit-removed) идут ДО строки reload, поэтому
    # окно копится с момента открытия предыдущей скобки, а не от строки reload.
    open_rl = None
    win_add = win_rem = 0
    for idx, ev in events:
        et = ev["event"]
        if et == "unit-added":
            win_add += 1
        elif et == "unit-removed":
            win_rem += 1
        elif et == "reload":
            if open_rl is not None:
                fail(errors, idx,
                     f"reload gen={open_rl.get('gen')} не закрыт reload-done — скобка висит")
            open_rl = ev                    # окно не трогаем: apply уже в нём
        elif et == "reload-done":
            if open_rl is None:
                fail(errors, idx, "reload-done без открытого reload — скобка лжёт")
            else:
                for k in ("added", "changed", "removed"):
                    if ev.get(k) != open_rl.get(k):
                        fail(errors, idx,
                             f"reload-done {k}={ev.get(k)}, а reload объявил "
                             f"{open_rl.get(k)} — скобка лжёт")
                if ev.get("gen") != open_rl.get("gen"):
                    fail(errors, idx,
                         f"reload-done gen={ev.get('gen')}, а скобка открыта "
                         f"gen={open_rl.get('gen')} — пара лжёт")
                if ev.get("added") != win_add or ev.get("removed") != win_rem:
                    fail(errors, idx,
                         f"reload-done added={ev.get('added')}/removed={ev.get('removed')}, "
                         f"а в окне скобки unit-added {win_add} / unit-removed {win_rem}")
                open_rl = None
                win_add = win_rem = 0
    if open_rl is not None:
        fail(errors, events[-1][0] if events else 0,
             f"reload gen={open_rl.get('gen')} дожил до конца журнала не закрытым — скобка висит")

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
