#!/usr/bin/env bash
# Живое демо Витка 11 — readiness файл-как-API (тикет 016):
# sd_notify READY=1 без сокетов, s6 notification-fd без пайпов:
# агенту выдан env AGRY_READY_PATH — создал файл, попытка готова.
#   t=0    boot: quickready (готов за ~0.4 с), neverready (молчит — и это факт)
#   t=4    статус-срез: quickready "ready":true, neverready "ready":false
#   t=4.5  SIGTERM; сирот 0; аудит OK
set -u
cd "$(dirname "$0")/.."

# Зачистка стреев прошлого падения (два супервизора на одном каталоге лгут)
pkill -9 -f "agryp --dir demo/ready-units" 2>/dev/null
sleep 0.3

make -s agryp || exit 1
mkdir -p demo/ready-units
cat > demo/ready-units/quickready.agent <<'EOF'
name         = quickready
exec         = sleep 0.4; touch "$AGRY_READY_PATH"; while :; do sleep 1; echo hb; done
restart      = always
cooldown-ms  = 500
EOF
cat > demo/ready-units/neverready.agent <<'EOF'
name         = neverready
exec         = while :; do sleep 1; echo hb; done
restart      = always
cooldown-ms  = 500
EOF

./agryp --dir demo/ready-units > demo/ready-transcript.jsonl 2>&1 &
SUP=$!
# Гигиена Хозяина демо: любой выход убивает супервизора — сирот не оставляем (Ст. 9)
trap 'kill -TERM "$SUP" 2>/dev/null; wait "$SUP" 2>/dev/null' EXIT
sleep 4

./agryp status --dir demo/ready-units > demo/ready-status-snapshot.jsonl
grep -a '"unit":"quickready","state":"RUNNING"' demo/ready-status-snapshot.jsonl | grep -aq '"ready":1,' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: quickready не готов в статусе (Ст. 13)"; exit 1; }
grep -a '"unit":"neverready","state":"RUNNING"' demo/ready-status-snapshot.jsonl | grep -aq '"ready":0,' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: молчун назвался готовым — статус лжёт (Ст. 6)"; exit 1; }

QR=$(grep -a '"unit":"quickready"' demo/ready-transcript.jsonl | grep -ac '"event":"ready"')
NR=$(grep -a '"unit":"neverready"' demo/ready-transcript.jsonl | grep -ac '"event":"ready"')
if [ "$QR" -lt 1 ] || [ "$NR" -ne 0 ]; then
    echo ">> ДЕМО ПРОВАЛЕНО: ready у quickready=$QR, у neverready=$NR — договор лжёт (Виток 11)"; exit 1
fi
QMS=$(grep -a '"unit":"quickready"' demo/ready-transcript.jsonl \
      | grep -a '"event":"ready"' | head -1 \
      | python3 -c "import json,sys; print(json.loads(sys.stdin.read())['ms'])")
if [ "$QMS" -lt 300 ] || [ "$QMS" -gt 2500 ]; then
    echo ">> ДЕМО ПРОВАЛЕНО: ready_ms=$QMS вне разумного окна (300..2500) — задержка лжёт"; exit 1
fi
echo ">> демо: ready файл-как-API — quickready объявился за ${QMS}мс, молчун честно не готов (neverready: 0 ready)"

kill -TERM "$SUP" 2>/dev/null
wait "$SUP" 2>/dev/null
sleep 1

ORPHANS=$(pgrep -f 'AGRY_READY_PATH' | wc -l)
if [ "$ORPHANS" -ne 0 ]; then
    echo ">> ДЕМО ПРОВАЛЕНО: $ORPHANS сирот остались живы (Ст. 9 нарушена)"; exit 1
fi
LEFT=$(ls demo/ready-units/*.ready 2>/dev/null | wc -l)
if [ "$LEFT" -ne 0 ]; then
    echo ">> ДЕМО ПРОВАЛЕНО: $LEFT ready-файлов пережили смерть попыток — чистота между жизнями нарушена"; exit 1
fi

python3 demo/audit_transcript.py demo/ready-transcript.jsonl || exit 1
echo ">> демо Витка 11 (ready) завершено: сирот — 0, ready-файлов не осталось, транскрипт: demo/ready-transcript.jsonl"
