#!/usr/bin/env bash
# Живое демо Витка 5+6 (≈19 с) — agrypctl: команда = файл-договор (Ст. 13, школа s6):
#   t=0    boot: worker и ghost (restart = always, база лестницы 800 мс)
#   t=3    agrypctl stop worker → ctl-down: попытка казнена TERM'ом группы,
#          рестартов ноль (политика заморожена); ghost не тронут — заморозка пер-юнит
#   t=5    agrypctl start worker → ctl-up: новая попытка, лестница с нуля
#   t=7    agrypctl status: worker RUNNING на свежей попытке (attempt 2)
#   t=9    Виток 6 (тикет 006): stop stubborn (trap '' TERM — игнорирует TERM)
#   t≈13   GRACE_MS истёк → ctl-kill, SIGKILL группы; exit по сигналу 9
#   t=14   SIGTERM → graceful shutdown; сирот 0; аудитор + отрицательный тест — OK
set -u
cd "$(dirname "$0")/.."

# Зачистка стреев прошлого падения: два супервизора на одном ctl-каталоге
# переплетают события в одну лжи (проверено живым демо 2026-11-07).
pkill -9 -f "agryp --dir demo/ctl-units" 2>/dev/null
pkill -9 -f "demo/ctl_worker.sh|demo/stubborn_worker.sh" 2>/dev/null
sleep 0.3

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
cat > demo/ctl-units/stubborn.agent <<'EOF'
name        = stubborn
exec        = . demo/stubborn_worker.sh
restart     = always
cooldown-ms = 800
EOF
cat > demo/stubborn_worker.sh <<'EOF'
# trap обязан жить в самом лидере группы: `sh script` плодит второго dash,
# а супервизор казнит группу по лидеру — внешний sh trap'а не знает.
trap '' TERM
while :; do sleep 1; echo "[$AGRY_UNIT] жив вопреки TERM"; done
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

# --- Виток 6 (тикет 006): эскалация ctl-stop TERM → GRACE_MS → KILL ---
./agrypctl --dir demo/ctl-units stop stubborn
sleep 4

grep -aq '"event":"ctl-kill"' demo/ctl-transcript.jsonl \
    || { echo ">> ДЕМО ПРОВАЛЕНО: TERM-упрямый юнит не получил ctl-kill за GRACE_MS"; exit 1; }
grep -a '"unit":"stubborn"' demo/ctl-transcript.jsonl | grep -aq '"by_signal":9' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: stubborn не умер по сигналу 9 — казнь не дошла"; exit 1; }
STUB_RESTARTS=$(grep -a '"unit":"stubborn"' demo/ctl-transcript.jsonl | grep -ac '"event":"restart"')
[ "$STUB_RESTARTS" -eq 0 ] \
    || { echo ">> ДЕМО ПРОВАЛЕНО: stubborn рестартовал после казни — казнь закона растит лестницу"; exit 1; }
echo ">> демо: stubborn пережил TERM, за GRACE_MS получил ctl-kill и умер по сигналу 9 (без рестартов)"

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
echo ">> демо Витков 5+6 завершено: сирот — 0, ctl-дисциплина и эскалация доказаны, транскрипт: demo/ctl-transcript.jsonl"
