#!/usr/bin/env bash
# Живое демо П37 (issue #6, волна ×6): подписанные конверты ed25519 + A2A AgentCard.
#
#   1. супервизор живёт; карта агента строится из ЖИВОГО статуса через
#      `agrypctl card` (= `agrypctl status --card`) и валидируется схемой A2A;
#   2. завод юнита разрешается ТОЛЬКО годным ed25519-конвертом:
#        годная подпись  -> OverseerGate.admit -> договор ложится -> юнит жив;
#        битая подпись   -> RefusedUnit        -> договор НЕ ложится -> юнита нет;
#        чужой ключ/повтор seq/легаси-WOTS -> RefusedUnit.
#   «Супервизор, которому можно верить без сети»: ключ заперт при рождении
#   клетки, цепь seq обязана расти, любое сомнение = отказ (fail-closed).
#   Примитив — vendored orlp/ed25519 (zlib): vendor/ed25519/ + tools/ed25519tool.
set -u
cd "$(dirname "$0")/.."

pkill -9 -f "agryp --dir demo/envelope-units" 2>/dev/null
pkill -9 -f "demo/envelope_worker.sh" 2>/dev/null
sleep 0.3

make -s agryp ed25519tool || exit 1
rm -rf demo/envelope-units
mkdir -p demo/envelope-units
cat > demo/envelope-units/alpha.agent <<'EOF'
name        = alpha
exec        = sh demo/envelope_worker.sh
restart     = always
budget-sec  = 60
cooldown-ms = 800
EOF
cat > demo/envelope_worker.sh <<'EOF'
echo "[$AGRY_UNIT] старт попытки $$"
while :; do sleep 1; echo "[$AGRY_UNIT] heartbeat"; done
EOF

./agryp --dir demo/envelope-units > demo/envelope-transcript.jsonl 2>&1 &
SUP=$!
sleep 3

# ---------- Приёмка 1: A2A AgentCard из живого супервизора (agrypctl) ----------
./agrypctl card --dir demo/envelope-units > demo/agentcard.json \
    || { echo ">> ДЕМО ПРОВАЛЕНО: agrypctl card не выдал карту живого супервизора"; exit 1; }
./agrypctl status --card --dir demo/envelope-units > demo/agentcard-status-card.json \
    || { echo ">> ДЕМО ПРОВАЛЕНО: agrypctl status --card не выдал карту"; exit 1; }
python3 tools/agentcard.py check demo/agentcard.json > /dev/null \
    || { echo ">> ДЕМО ПРОВАЛЕНО: карта (agrypctl card) не прошла схему A2A"; exit 1; }
python3 tools/agentcard.py check demo/agentcard-status-card.json > /dev/null \
    || { echo ">> ДЕМО ПРОВАЛЕНО: карта (status --card) не прошла схему A2A"; exit 1; }
grep -aq '"type": "AgentCard"' demo/agentcard.json \
    || { echo ">> ДЕМО ПРОВАЛЕНО: это не AgentCard"; exit 1; }
grep -aq '"alg": "ed25519"' demo/agentcard.json \
    || { echo ">> ДЕМО ПРОВАЛЕНО: карта не декларирует ed25519-подпись конвертов"; exit 1; }
grep -aq 'unit:alpha' demo/agentcard.json \
    || { echo ">> ДЕМО ПРОВАЛЕНО: живой юнит не попал в skills"; exit 1; }
URL=$(python3 -c "import json;print(json.load(open('demo/agentcard.json'))['url'])")
case "$URL" in file://*) [ -f "${URL#file://}" ] || { echo ">> ДЕМО ПРОВАЛЕНО: endpoint мёртв"; exit 1; } ;;
  *) echo ">> ДЕМО ПРОВАЛЕНО: endpoint не file:// — $URL"; exit 1;; esac
echo ">> демо: AgentCard валидна по схеме A2A, endpoint живой ($URL)"

# ---------- Приёмка 2: завод юнита решает ed25519-подпись (fail-closed) ----------
python3 - demo/envelope-units <<'PY'
import sys
sys.path.insert(0, "tools")
from pathlib import Path
import signed_envelope as se

cell = Path("demo/envelope-units")
signer = se.CellSigner(b"demo-cell-secret")          # ключ клетки (рождение; TEST ONLY)
gate = se.OverseerGate(trusted_key_ids=signer.trusted_keys)

def lay_contract(unit: str):
    (cell / f"{unit}.agent").write_text(
        f"name        = {unit}\nexec        = sh demo/envelope_worker.sh\n"
        "restart     = always\nbudget-sec  = 60\ncooldown-ms = 800\n")

def birth(unit: str, envelope):
    """Завод юнита ТОЛЬКО через годный конверт."""
    body = gate.admit(envelope)                      # битое -> RefusedUnit
    assert body["unit"] == unit and body["alg"] == "ed25519"
    lay_contract(unit)

# 1) годный конверт крови -> завод разрешён
birth("beta", signer.sign("blood", "beta", {"request": "unit-birth", "mem_mb": 32}))
print("DEMO: годный ed25519-конверт -> beta заведён (договор лежит)")

# 2) битая подпись -> отказ завода: договор НЕ ложится
env = signer.sign("blood", "gamma", {"request": "unit-birth"})
env["env"]["payload"]["mem_mb"] = 1                  # подмена байта payload
try:
    birth("gamma", env)
    print("DEMO FAIL: подделка прошла дверь"); sys.exit(1)
except se.RefusedUnit as e:
    print(f"DEMO: битая подпись -> отказ завода gamma ({e})")
assert not (cell / "gamma.agent").exists(), "подделка завела юнита — overseer лжёт"

# 3) чужой ключ -> отказ (не в списке доверия клетки)
rogue = se.CellSigner(b"attacker-key")               # TEST ONLY
try:
    birth("delta", rogue.sign("blood", "delta", {"request": "unit-birth"}))
    print("DEMO FAIL: чужой ключ прошёл дверь"); sys.exit(1)
except se.RefusedUnit as e:
    print(f"DEMO: чужой ключ -> отказ завода delta ({e})")
assert not (cell / "delta.agent").exists()

# 4) повтор конверта -> отказ (цепь seq обязана расти)
replay = signer.sign("event", "beta", {"note": "once"})
gate.admit(replay)
try:
    gate.admit(replay)
    print("DEMO FAIL: повтор конверта принят"); sys.exit(1)
except se.RefusedUnit as e:
    print(f"DEMO: повтор seq -> отказ ({e})")

# 5) легаси волны ×4 (sha256-wots) -> в ed25519-дверь не входит
wots = se.WotsCellSigner(b"legacy-x4")
try:
    birth("epsilon", wots.sign("blood", "epsilon", {"request": "unit-birth"}))
    print("DEMO FAIL: легаси-конверт принят"); sys.exit(1)
except se.RefusedUnit as e:
    print(f"DEMO: легаси sha256-wots -> отказ завода epsilon ({e})")
assert not (cell / "epsilon.agent").exists()

# 6) мусор вместо конверта -> отказ, наружу только RefusedUnit
for garbage in (None, 42, {}, {"env": {"v": 2, "alg": "ed25519"}}):
    try:
        gate.admit(garbage); print("DEMO FAIL: мусор принят"); sys.exit(1)
    except se.RefusedUnit:
        pass
print("DEMO: fail-closed подтверждён на мусоре 4 видов")
PY
[ $? -eq 0 ] || { echo ">> ДЕМО ПРОВАЛЕНО: церемония завода"; exit 1; }

# beta реально живёт: договор лёг — виток 5: новая клетка подхватывается
# по SIGHUP (файл-договор читается супервизором на витке релоада)
kill -HUP "$SUP" 2>/dev/null
sleep 2
./agryp status --dir demo/envelope-units > demo/envelope-status-snapshot.jsonl
grep -aq '"unit":"beta","state":"RUNNING"' demo/envelope-status-snapshot.jsonl \
    || { echo ">> ДЕМО ПРОВАЛЕНО: beta не жива — завод по подписи не сработал"; exit 1; }
grep -aq '"unit":"gamma"' demo/envelope-status-snapshot.jsonl \
    && { echo ">> ДЕМО ПРОВАЛЕНО: gamma жива — overseer солгал"; exit 1; }
grep -aq '"unit":"delta"' demo/envelope-status-snapshot.jsonl \
    && { echo ">> ДЕМО ПРОВАЛЕНО: delta жива — чужой ключ завёл юнита"; exit 1; }
grep -aq '"unit":"epsilon"' demo/envelope-status-snapshot.jsonl \
    && { echo ">> ДЕМО ПРОВАЛЕНО: epsilon жива — легаси-конверт завёл юнита"; exit 1; }

kill "$SUP" 2>/dev/null
pkill -9 -f "demo/envelope_worker.sh" 2>/dev/null
echo ">> демо П37: ed25519-подпись решает завод, карта живая через agrypctl, дверь fail-closed — зелёный"
