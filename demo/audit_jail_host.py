#!/usr/bin/env python3
"""Аудитор jail-приёмки ЦУ 011 (Ст. 6: «журнал не лжёт»).

Проверяет транскрипт demo/jail-host-transcript.jsonl:

  1. без NUL-байтов; каждая строка — корректный JSON (журнал агентов
     и события приёмки живут одним файлом);
  2. проба среды: ровно одна, userns-обёртка рабочая;
  3. контроль границы (без клетки): 20 юнитов, 40 процессов перед
     kill -9, сирот через 5 с — 20 (по вечному внутреннему sh на юнит);
  4. лечение (jail = pid в userns-обёртке): 20 спавнов, все "jailed":1,
     jail-skip — ноль (клетка не встала молча — запрещено Ст. 6),
     сирот через 5 с — 0;
  5. вердикт: контроль 20 / лечение 0 / хост чист;
  6. дисциплина спавнов: каждый из c01–c20 и j01–j20 заспан ровно один
     раз; контрольному юниту клеточные поля не присвоены (двух правд нет).

Глобальная монотонность ts не проверяется намеренно: журналы обеих рук
копируются в транскрипт после меток рук (сырые куски, как есть).

Успех: печатает OK и сводку, код выхода 0. Иначе — список нарушений, код 1.
"""
import json
import re
import sys


def main(path):
    errors = []
    with open(path, "rb") as f:
        raw = f.read()
    if b"\x00" in raw:
        errors.append("NUL-байты в транскрипте")

    lines = raw.decode("utf-8", "replace").splitlines()
    events = []
    for i, ln in enumerate(lines):
        if not ln.strip():
            continue
        try:
            events.append((i + 1, json.loads(ln)))
        except json.JSONDecodeError as e:
            errors.append(f"строка {i + 1}: не JSON ({e}); текст: {ln[:80]!r}")
            continue

    probe = [e for _, e in events if e.get("event") == "host-probe"]
    if len(probe) != 1:
        errors.append(f"host-probe: {len(probe)} шт., обязана быть одна")
    else:
        if probe[0].get("userns_wrapper") != "ok":
            errors.append("обёртка userns не рабочая — приёмка не должна была идти")

    ctl = [e for _, e in events if e.get("event") == "arm-control"]
    jai = [e for _, e in events if e.get("event") == "arm-jail"]
    if len(ctl) != 1:
        errors.append(f"arm-control: {len(ctl)} шт., обязана быть одна")
    else:
        e = ctl[0]
        if e.get("units") != 20 or e.get("jail") != "none":
            errors.append("контроль: не 20 юнитов без клетки")
        if e.get("procs_before_kill") != 40:
            errors.append(f"контроль: процессов перед kill -9 — {e.get('procs_before_kill')}, ожидалось 40")
        if e.get("orphans_after_5s") != 20:
            errors.append(f"контроль: сирот {e.get('orphans_after_5s')}, граница Ст. 9 требует 20")
    if len(jai) != 1:
        errors.append(f"arm-jail: {len(jai)} шт., обязана быть одна")
    else:
        e = jai[0]
        if e.get("units") != 20 or e.get("jail") != "pid":
            errors.append("лечение: не 20 юнитов с jail = pid")
        if e.get("procs_before_kill") != 40:
            errors.append(f"лечение: процессов перед kill -9 — {e.get('procs_before_kill')}, ожидалось 40")
        if e.get("jailed_spawns") != 20:
            errors.append(f"лечение: спавнов с jailed:1 — {e.get('jailed_spawns')}, ожидалось 20")
        if e.get("jail_skips") != 0:
            errors.append(f"лечение: jail-skip — {e.get('jail_skips')}, обязан быть ноль (Ст. 6)")
        if e.get("orphans_after_5s") != 0:
            errors.append(f"лечение: сирот {e.get('orphans_after_5s')}, обещание клетки — 0")

    verdict = [e for _, e in events if e.get("event") == "verdict"]
    if len(verdict) != 1:
        errors.append(f"verdict: {len(verdict)} шт., обязан быть один")
    else:
        v = verdict[0]
        if v.get("control_orphans") != 20:
            errors.append(f"вердикт: контроль {v.get('control_orphans')}, ожидалось 20")
        if v.get("jail_orphans") != 0:
            errors.append(f"вердикт: лечение {v.get('jail_orphans')}, ожидалось 0")
        if v.get("host_leftover") != 0:
            errors.append(f"вердикт: на хосте {v.get('host_leftover')} процессов")

    spawns = {}
    for _, e in events:
        if e.get("event") == "spawn":
            spawns.setdefault(e.get("unit"), []).append(e)
    for n in range(1, 21):
        for prefix, must_jail in (("c", False), ("j", True)):
            name = f"{prefix}{n:02d}"
            got = spawns.get(name, [])
            if len(got) != 1:
                errors.append(f"юнит {name}: спавнов {len(got)}, обязан быть один")
            elif must_jail and got[0].get("jailed") != 1:
                errors.append(f"юнит {name}: jailed={got[0].get('jailed')}, клетка не встала")
            elif not must_jail and got[0].get("jailed") == 1:
                errors.append(f"юнит {name}: контрольному присвоена клетка (две правды)")
    for unit in spawns:
        if not re.fullmatch(r"[cj]\d{2}", str(unit)):
            errors.append(f"чужой юнит в транскрипте: {unit}")

    if errors:
        print("АУДИТ ПРОВАЛЕН (Ст. 6):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("OK: jail-host-транскрипт не лжёт — контроль границы 20/20, клетка закрыла её 0/20, хост чист")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
