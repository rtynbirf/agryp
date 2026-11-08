#!/usr/bin/env python3
# check_constitution.py — машина сверяет Ст. 1 конституции с телом ядра.
# Родитель: волна ×4 (2026-11-11), аудит 2026-11-08 пункт 2 — Поправка №11
# была поднята «по факту» (tasks/done/012-vitok-10.md), но статьи в
# конституции не было, и объявленная проверка Ст. 1 лежала красной.
# Статья без команды проверки — не статья (Преамбула); проверка, которая
# не запускается машиной — лозунг. Здесь проверка запускается.
#
# Проверки:
#   1. find *.c == 1            (Ст. 1 — один файл)
#   2. wc -l src/agryp.c <= N   (N — потолок из статьи «не больше N строк»)
#   3. «сейчас M» из статьи == факту (статья не лжёт о настоящем)
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

    # Ст. 1 — один файл
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

    print(f"Ст. 1 говорит правду: 1 файл C, {actual}/{ceiling} строк, «сейчас {claimed}» сходится.")
    print("КОНСТИТУЦИЯ ЦЕЛА.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
