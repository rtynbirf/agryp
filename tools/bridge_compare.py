#!/usr/bin/env python3
"""Сверка туда-обратно моста (тикет 008, виток 7).

Сравнивает исходный *.agent с полученным из *.service *.agent:
  - семантика name/exec/restart/budget-sec/cooldown-ms/mem-max-mb/
    max-attempts обязана сохраниться (отсутствие = значение по умолчанию);
  - token-budget и jail — ОБЪЯВЛЕННЫЕ потери: в обратном файле их нет,
    зато шапка .service обязана о них сказать (Ст. 6: молчания нет).
"""
import sys

DEFAULTS = {
    "restart": "always", "budget-sec": "0", "cooldown-ms": "1000",
    "max-attempts": "0", "token-budget": "0", "mem-max-mb": "0",
}
LOSSES = ("token-budget", "jail")


def parse(path):
    d = {}
    with open(path, encoding="utf-8") as f:
        for ln in f:
            s = ln.strip()
            if not s or s.startswith("#"):
                continue
            if "=" not in s:
                continue
            k, v = s.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def main(orig_path, back_path, svc_path):
    orig, back = parse(orig_path), parse(back_path)
    with open(svc_path, encoding="utf-8") as f:
        svc = f.read()
    bad = []
    for k in sorted(set(orig) | set(back)):
        if k in LOSSES:
            if k in orig:
                if k in back:
                    bad.append(f"{k}: назван потерей, но вернулся из systemd")
                if k not in svc:
                    bad.append(f"{k}: потерян, а шапка .service о нём молчит (Ст. 6)")
            continue
        a = orig.get(k, DEFAULTS.get(k))
        b = back.get(k, DEFAULTS.get(k))
        if a != b:
            bad.append(f"{k}: было {a!r}, вернулось {b!r}")
    if bad:
        print(f"FAIL {orig_path}:")
        for b in bad:
            print(f"  - {b}")
        return 1
    print(f"OK {orig_path} → .service → .agent: семантика сохранена, потери названы")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage: bridge_compare.py <orig.agent> <back.agent> <gen.service>",
              file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
