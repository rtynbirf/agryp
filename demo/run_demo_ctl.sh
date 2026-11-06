#!/usr/bin/env bash
# Живое демо Витка 5 (≈14 с) — agrypctl: команда = файл-договор (Ст. 13, школа s6):
#   t=0    boot: worker и ghost (restart = always, база лестницы 800 мс)
#   t=3    agrypctl stop worker → ctl-down: попытка казнена TERM'ом группы,
#          рестартов ноль (политика заморожена); ghost не тронут — заморозка пер-юнит
#   t=5    agrypctl start worker → ctl-up: новая попытка, лестница с нуля
#   t=7    agrypctl status: worker RUNNING на свежей попытке (attempt 2)
#   t=9    SIGTERM → graceful shutdown; сирот 0; аудитор + отрицательный тест — OK
set -u
cd "$(dirname "$0")/.."

make -s agryp || exit 1
rm -rf demo/ctl-units
mkdir -p demo/ctl-units
cat > demo/ctl-units/worker.agent <<'EOF'
name        = worker
exec        = sh demo/ctl_worker.sh
restart     = always
cooldown-ms = 800
EOF
cat > demo/ctl-units/ghost.agent <<'EOF'
name        = ghost
exec        = sh demo/ctl_worker.sh
restart     = always
cooldown-ms = 800
EOF
cat > demo/ctl_worker.sh <<'EOF'
echo "[$AGRY_UNIT] работаю, pid $$"
while :; do sleep 1; echo "[$AGRY_UNIT] heartbeat"; done
EOF

./agryp --dir demo/ctl-units > demo/ctl-transcript.jsonl 2>&1 &
SUP=$!
sleep 3

./agrypctl --dir demo/ctl-units stop worker
sleep 2

# Приёмка 1: worker не рестартовал при живом .down (политика заморожена)
if grep -a '"unit":"worker"' demo/ctl-transcript.jsonl | grep -aq '"event":"restart"'; then
    echo ">> ДЕМО ПРОВАЛЕНО: worker рестартовал при живом .down (Ст. 13 нарушена)"; exit 1
fi
# Приёмка 2: ctl-down в журнале есть, ghost жив (сердцебиения продолжаются)
grep -aq '"event":"ctl-down"' demo/ctl-transcript.jsonl \
    || { echo ">> ДЕМО ПРОВАЛЕНО: нет ctl-down (Ст. 6: молчаливая казнь)"; exit 1; }
GHOST_HB=$(grep -acF '[ghost] heartbeat' demo/ctl-transcript.jsonl)
[ "$GHOST_HB" -ge 2 ] \
    || { echo ">> ДЕМО ПРОВАЛЕНО: ghost замер — заморозка должна быть пер-юнит"; exit 1; }
echo ">> демо: worker казнён без рестартов (ctl-down), ghost жив ($GHOST_HB сердцебиений)"

./agrypctl --dir demo/ctl-units start worker
sleep 2

# Приёмка 3: ctl-up есть и worker получил новую попытку (attempt 2)
grep -aq '"event":"ctl-up"' demo/ctl-transcript.jsonl \
    || { echo ">> ДЕМО ПРОВАЛЕНО: нет ctl-up после снятия файла"; exit 1; }
grep -a '"unit":"worker"' demo/ctl-transcript.jsonl | grep -aq '"attempt":2' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: worker не получил новую попытку после ctl-up"; exit 1; }

# Приёмка 4: файл семьи живой — status показывает worker RUNNING на attempt 2
./agrypctl --dir demo/ctl-units status > demo/ctl-status-snapshot.jsonl
grep -a '"unit":"worker","state":"RUNNING"' demo/ctl-status-snapshot.jsonl | grep -aq '"attempt":2' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: статус не показывает свежую попытку worker (Ст. 13)"; exit 1; }
echo ">> демо: ctl-up → новая попытка worker, статус снят (demo/ctl-status-snapshot.jsonl)"

kill -TERM "$SUP" 2>/dev/null
wait "$SUP" 2>/dev/null
sleep 1

if [ -f demo/ctl-units/.agryp-status ]; then
    echo ">> ДЕМО ПРОВАЛЕНО: файл статуса пережил супервизор (Ст. 13)"; exit 1
fi
ORPHANS=$(pgrep -f 'demo/ctl_worker.sh' | wc -l)
if [ "$ORPHANS" -ne 0 ]; then
    echo ">> ДЕМО ПРОВАЛЕНО: $ORPHANS сирот остались живы (Ст. 9 нарушена)"; exit 1
fi

python3 demo/audit_transcript.py demo/ctl-transcript.jsonl || exit 1
python3 demo/negative_ctl_test.py || exit 1
echo ">> демо Витка 5 завершено: сирот — 0, ctl-дисциплина доказана, транскрипт: demo/ctl-transcript.jsonl"
