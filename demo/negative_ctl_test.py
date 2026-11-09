#!/usr/bin/env python3
"""Отрицательный тест аудитора — тикеты 002 и 006 (Ст. 6: журнал не лжёт).

Собирает эталонный ctl-транскрипт и прогоняет через аудитора (ожидаем OK),
затем вклеивает четыре подделки и требует FAIL с точным приговором:

  A. spawn при живом .down — политика заморожена, спавн подделкой быть не может;
  B. ctl-up без ctl-down — журнал лжёт о разморозке;
  C. ctl-kill без последующего exit — эскалация не мажет (Виток 6);
  D. finish у юнита без finish-конфига — хук из воздуха (Виток 6, Ст. 17).

Единственная форма доказательства — прогон: эталон зелёный, все подделки
пойманы с нужной формулировкой, код выхода 0. Иначе — FAIL.
"""
import json
import os
import subprocess
import sys
import tempfile

AUDITOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_transcript.py")
TS = "2026-11-07T12:00:00Z"


def ev(up, event, unit=None, **kw):
    e = {"ts": TS, "up_ms": up, "event": event}
    if unit:
        e["unit"] = unit
    e.update(kw)
    return json.dumps(e)


def reference():
    """Эталонный виток ctl: spawn → ctl-down → казнь → ctl-up → новая попытка."""
    return [
        ev(0, "boot", units=1, dir="demo/ctl-units"),
        ev(100, "spawn", unit="worker", pid=101, attempt=1, budget_sec=0),
        ev(200, "ctl-down", unit="worker"),
        ev(300, "exit", unit="worker", by_signal=15, ok=False),
        ev(310, "stopped", unit="worker", reason="ctl-down"),
        ev(400, "ctl-up", unit="worker"),
        ev(500, "spawn", unit="worker", pid=102, attempt=2, budget_sec=0),
        ev(600, "exit", unit="worker", code=0, ok=True),
        ev(610, "stopped", unit="worker", reason="policy"),
        ev(700, "shutdown", reason="signal"),
        ev(710, "summary", unit="worker", attempts=2, exits_ok=1, exits_fail=1,
           budget_kills=0, token_kills=0, tokens_total=0, restarts=0),
        ev(720, "uptime-ms", value=720),
    ]


def run_auditor(lines):
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        f.write("\n".join(lines) + "\n")
        path = f.name
    try:
        r = subprocess.run([sys.executable, AUDITOR, path],
                           capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr
    finally:
        os.unlink(path)


def main():
    errors = []

    rc, out = run_auditor(reference())
    if rc != 0:
        errors.append(f"эталон не прошёл аудит (ожидался OK):\n{out}")

    # Подделка A: spawn при живом .down (после казни, до ctl-up, по времени — между)
    forged = reference()[:4] + [ev(305, "spawn", unit="worker", pid=999, attempt=2)] + reference()[4:]
    rc, out = run_auditor(forged)
    if rc == 0:
        errors.append("подделка A (spawn при живом .down) прошла аудит — аудитор слеп")
    elif "живом .down" not in out:
        errors.append(f"подделка A поймана не той формулировкой:\n{out}")

    # Подделка B: ctl-up без ctl-down (вклеен до первого ctl-down)
    forged_b = reference()[:2] + [ev(150, "ctl-up", unit="worker")] + reference()[2:]
    rc, out = run_auditor(forged_b)
    if rc == 0:
        errors.append("подделка B (ctl-up без ctl-down) прошла аудит — аудитор слеп")
    elif "ctl-up без ctl-down" not in out:
        errors.append(f"подделка B поймана не той формулировкой:\n{out}")

    # Подделка C: ctl-kill без последующего exit (после всех exit, перед shutdown)
    forged_c = reference()[:9] + [ev(650, "ctl-kill", unit="worker", grace_ms=3000, why="ctl")] + reference()[9:]
    rc, out = run_auditor(forged_c)
    if rc == 0:
        errors.append("подделка C (ctl-kill без exit) прошла аудит — аудитор слеп")
    elif "ctl-kill без последующего exit" not in out:
        errors.append(f"подделка C поймана не той формулировкой:\n{out}")

    # Подделка D: finish у юнита без finish-конфига (worker не объявлял хук)
    forged_d = reference()[:3] + [ev(310, "finish", unit="worker", hook_exit=0)] + reference()[3:]
    rc, out = run_auditor(forged_d)
    if rc == 0:
        errors.append("подделка D (finish без конфига) прошла аудит — аудитор слеп")
    elif "без finish-конфига" not in out:
        errors.append(f"подделка D поймана не той формулировкой:\n{out}")

    if errors:
        print("FAIL negative_ctl_test:")
        for e in errors:
            print("  -", e)
        return 1
    print("OK: эталон прошёл, подделки A–D пойманы — аудитору ничего не впарить.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
