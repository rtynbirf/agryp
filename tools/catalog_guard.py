#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""catalog_guard — контракт каталога счётом (П-04 / T04 / agryp#1).

Каталог — это таблица с договором, не текст: любое изменение, ломающее
счёт строк, счёт категорий, сортировку, уникальность или непустоту полей,
валит CI. Судья — машина, человек не пересчитывает руками.

Формат данных: docs/tool-catalog.csv (utf-8-sig), колонки
category,tool,description — 2444 позиции, 34 категории (канон v3,
восстановлен из коммита b53199d волной FIX-1).
"""
import csv, sys, os, collections

CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs', 'tool-catalog.csv')

# --- КОНТРАКТ (правится одним коммитом вместе с каталогом) ---
EXPECTED_ROWS = 2444        # позиций (строк данных, без заголовка)
EXPECTED_CATEGORIES = 34    # категорий
REQUIRED = ("category", "tool", "description")

def main() -> int:
    if not os.path.exists(CSV_PATH):
        print(f"GUARD FAIL: {CSV_PATH} отсутствует"); return 1
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    fails = []
    if len(rows) != EXPECTED_ROWS:
        fails.append(f"позиций {len(rows)} ≠ контракту {EXPECTED_ROWS}")
    cats = collections.Counter((r.get("category") or "").strip() for r in rows)
    cats.pop("", None)
    for i, r in enumerate(rows, 2):
        for col in REQUIRED:
            if not (r.get(col) or "").strip():
                fails.append(f"строка {i}: пусто {col}")
    keys = [(r.get("category", "").strip().lower(), r.get("tool", "").strip().lower()) for r in rows]
    dups = sorted({k for k in keys if keys.count(k) > 1})
    if dups:
        fails.append(f"дубли (категория+инструмент): {dups[:5]}")
    for c in cats:
        names = [r["tool"].strip().lower() for r in rows if r.get("category", "").strip() == c]
        if names != sorted(names):
            fails.append(f"категория «{c}»: нарушена алфавитная сортировка")
    if len(cats) != EXPECTED_CATEGORIES:
        fails.append(f"категорий {len(cats)} ≠ контракту {EXPECTED_CATEGORIES}")
    if fails:
        print("GUARD FAIL — каталог сломал контракт:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print(f"GUARD OK: {len(rows)} позиций × {len(cats)} категорий — контракт "
          f"({EXPECTED_ROWS}×{EXPECTED_CATEGORIES}) в силе")
    return 0

if __name__ == "__main__":
    sys.exit(main())
