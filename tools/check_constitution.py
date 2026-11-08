#!/usr/bin/env python3
# check_constitution.py — машина сверяет Ст. 1 конституции с телом ядра.
# Родитель: волна ×4 (2026-11-11), аудит 2026-11-08 пункт 2 — Поправка №11
# была поднята «по факту» (tasks/done/012-vitok-10.md), но статьи в
# конституции не было, и объявленная проверка Ст. 1 лежала красной.
# Статья без команды проверки — не статья (Преамбула); проверка, которая
# не запускается машиной — лозунг. Здесь проверка запускается.
#
# Проверки:
#   1. find src/*.c == 1        (Ст. 1 — ядро один файл)
#   2. wc -l src/agryp.c <= N   (N — потолок из статьи «не больше N строк»)
#   3. «сейчас M» из статьи == факту (статья не лжёт о настоящем)
#   4. Поправка №12 — счёт границы: tools/*.c == T, vendor/*.c == V,
#      .c вне src/tools/vendor == 0 (числа T/V берутся ИЗ статьи —
#      статья обязана знать настоящее, машина не даёт ей лгать)
# rc=0 — конституция говорит правду; rc=1 — статья лжёт (с приговором).
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONSTITUTION = ROOT / "CONSTITUTION.md"
CORE = ROOT / "src" / "agryp.c"


def fail(msg: str) -> int:
    print(f"КОНСТИТУЦИЯ ЛЖЁТ: {msg}")
    return 1


def main() -> int:
    if not CONSTITUTION.exists():
        return fail("нет CONSTITUTION.md")
    if not CORE.exists():
        return fail("нет src/agryp.c")

    text = CONSTITUTION.read_text(encoding="utf-8")

    # Ст. 1 — один файл (ядро)
    c_files = [p for p in ROOT.glob("src/*.c")]
    if len(c_files) != 1:
        return fail(f"файлов *.c в src/ — {len(c_files)}, а статья требует 1")

    actual = len(CORE.read_text(encoding="utf-8").splitlines())

    # Потолок: «не больше N строк» в статье Ст. 1
    art1 = text.split("### Ст. 1", 1)
    if len(art1) < 2:
        return fail("не нашёл Ст. 1")
    art1 = art1[1].split("### Ст. 2", 1)[0]
    m = re.search(r"не больше (\d+) строк", art1)
    if not m:
        return fail("в Ст. 1 нет команды проверки «не больше N строк»")
    ceiling = int(m.group(1))
    if actual > ceiling:
        return fail(f"{actual} строк > потолка Ст. 1 ({ceiling}) — код перерос статью")

    # «сейчас M» — статья обязана знать настоящее
    m2 = re.search(r"сейчас (\d+)", art1)
    if not m2:
        return fail("в Ст. 1 нет отметки «сейчас N» — статья не знает настоящее")
    claimed = int(m2.group(1))
    if claimed != actual:
        return fail(f"статья говорит «сейчас {claimed}», а тело — {actual}")

    # Поправка №12 — счёт границы клетки (числа объявлены в статье)
    m_tools = re.search(r"`find tools -name '\*\.c' \| wc -l` → `(\d+)`", art1)
    m_vendor = re.search(r"`find vendor -name '\*\.c' \| wc -l` → `(\d+)`", art1)
    if not m_tools or not m_vendor:
        return fail("в Ст. 1 нет счёта границы (tools/vendor) — Поправка №12 стёрта?")
    tools_n = int(m_tools.group(1))
    vendor_n = int(m_vendor.group(1))

    tools_c = sorted(str(p) for p in ROOT.glob("tools/*.c"))
    if len(tools_c) != tools_n:
        return fail(f"файлов *.c в tools/ — {len(tools_c)}, а статья объявляет {tools_n}")
    vendor_c = sorted(str(p) for p in ROOT.glob("vendor/**/*.c"))
    if len(vendor_c) != vendor_n:
        return fail(f"файлов *.c в vendor/ — {len(vendor_c)}, а статья объявляет {vendor_n}")

    allowed = [str(ROOT / "src"), str(ROOT / "tools"), str(ROOT / "vendor")]
    stray = [str(p) for p in ROOT.rglob("*.c")
             if not any(str(p).startswith(a + "/") for a in allowed)
             and "/.git/" not in str(p)]
    if stray:
        return fail(f"контрабанда: *.c вне src/tools/vendor — {stray}")

    print(f"Ст. 1 говорит правду: ядро 1 файл, {actual}/{ceiling} строк, "
          f"«сейчас {claimed}» сходится; граница: tools {len(tools_c)}/{tools_n}, "
          f"vendor {len(vendor_c)}/{vendor_n}, вне зон 0.")
    print("КОНСТИТУЦИЯ ЦЕЛА.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
