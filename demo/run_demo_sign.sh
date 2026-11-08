#!/usr/bin/env bash
# Живое демо Витка 10 — сигнатуры юнитов (тикет 014, Ст. 6):
#   t=0    boot: alpha — журнал пишет unit-sign old=null
#   t=3    правка договора alpha (budget-sec 60→30): SIGHUP
#   t≈4    журнал: unit-sign с old≠new (два разных 64-hex) + mtime —
#          «что именно поменялось» — машинный факт, дети живы
set -u
cd "$(dirname "$0")/.."

pkill -9 -f "agryp --dir demo/sign-units" 2>/dev/null
pkill -9 -f "demo/reload_worker.sh" 2>/dev/null
sleep 0.3

make -s agryp || exit 1
rm -rf demo/sign-units
mkdir -p demo/sign-units
cat > demo/sign-units/alpha.agent <<'EOF'
name        = alpha
exec        = sh demo/reload_worker.sh
restart     = always
budget-sec  = 60
cooldown-ms = 800
EOF
cat > demo/reload_worker.sh <<'EOF'
echo "[$AGRY_UNIT] старт попытки $$"
while :; do sleep 1; echo "[$AGRY_UNIT] heartbeat"; done
EOF

./agryp --dir demo/sign-units > demo/sign-transcript.jsonl 2>&1 &
SUP=$!
sleep 3

# подмена договора: попытка жива, меняется файл
cat > demo/sign-units/alpha.agent <<'EOF'
name        = alpha
exec        = sh demo/reload_worker.sh
restart     = always
budget-sec  = 30
cooldown-ms = 800
EOF
kill -HUP "$SUP"
sleep 2

# Приёмка 1: при boot — подпись с old:null
grep -a '"event":"unit-sign".*"old":null' demo/sign-transcript.jsonl | grep -aq '"unit":"alpha"' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: подпись при boot отсутствует (old:null)"; exit 1; }

# Приёмка 2: после правки — old≠new, оба 64-hex, mtime есть
SIGN_EV=$(grep -a '"event":"unit-sign"' demo/sign-transcript.jsonl | grep -av '"old":null')
echo "$SIGN_EV" | grep -aq '"unit":"alpha"' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: событие unit-sign после подмены договора отсутствует"; exit 1; }
echo "$SIGN_EV" | grep -aqE '"old":"[0-9a-f]{64}","new":"[0-9a-f]{64}","mtime":[0-9]+' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: unit-sign не содержит дифф двух 64-hex хешей + mtime"; exit 1; }
OLD=$(echo "$SIGN_EV" | sed -n 's/.*"old":"\([0-9a-f]*\)".*/\1/p')
NEW=$(echo "$SIGN_EV" | sed -n 's/.*"new":"\([0-9a-f]*\)".*/\1/p')
[ "$OLD" != "$NEW" ] \
    || { echo ">> ДЕМО ПРОВАЛЕНО: old == new — дифф лжи"; exit 1; }
# хеш старого договора воспроизводим независимо (правда одна)
OLD_FILE=$(mktemp)
cat > "$OLD_FILE" <<'EOF'
name        = alpha
exec        = sh demo/reload_worker.sh
restart     = always
budget-sec  = 60
cooldown-ms = 800
EOF
CALC=$(sha256sum "$OLD_FILE" | cut -d' ' -f1)
rm -f "$OLD_FILE"
[ "$OLD" = "$CALC" ] \
    || { echo ">> ДЕМО ПРОВАЛЕНО: old-хеш не воспроизводится sha256sum — подпись лжёт ($OLD != $CALC)"; exit 1; }
echo ">> демо: unit-sign old≠new, old воспроизводим sha256sum — договор подписан честно"

# Приёмка 3: дети живы (сигнатуры не про жизни — reload Витка 6)
./agryp status --dir demo/sign-units > demo/sign-status-snapshot.jsonl
grep -a '"unit":"alpha","state":"RUNNING"' demo/sign-status-snapshot.jsonl | grep -aq '"budget_sec":30' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: бюджет 30 не применился к живой попытке"; exit 1; }
A_SPAWNS=$(grep -a '"unit":"alpha"' demo/sign-transcript.jsonl | grep -ac '"event":"spawn"')
[ "$A_SPAWNS" -eq 1 ] \
    || { echo ">> ДЕМО ПРОВАЛЕНО: alpha перезапускался при подписи договора — дети умерли"; exit 1; }

kill -TERM "$SUP" 2>/dev/null
wait "$SUP" 2>/dev/null
sleep 1
ORPHANS=$(pgrep -f 'demo/reload_worker.sh' | wc -l)
[ "$ORPHANS" -eq 0 ] || { echo ">> ДЕМО ПРОВАЛЕНО: $ORPHANS сирот"; exit 1; }

python3 demo/audit_transcript.py demo/sign-transcript.jsonl || exit 1
echo ">> демо Витка 10 (сигнатуры) завершено: договор подписан при boot и при каждом reload"
