#!/usr/bin/env bash
# Живое демо Витка 6 (≈14 с) — чистота между жизнями, reload, эскалация:
#   t=0    boot: sweeper (finish-хук, 3 попытки), resident, victim
#   t=3    жертвы готовы: resident.changed (budget 60→90), +newcomer +stubborn,
#          -victim → SIGHUP → reload 2/1/1 без единой смерти живых попыток
#   t=4.5  статус-срез: resident жив на attempt 1, budget_sec уже 90 (Ст. 18)
#   t=5    agrypctl stop stubborn → ctl-down: TERM игнорируется (trap '' TERM)
#   t≈8    Ст. 13: GRACE_MS истёк → ctl-kill → SIGKILL группы → exit sig 9
#   t=10   sweeper: 3 смерти, 3 finish-хука, junk-каталог убран (Ст. 17)
#   t=11   SIGTERM → graceful shutdown; сирот 0; файла статуса нет
set -u
cd "$(dirname "$0")/.."

make -s agryp || exit 1
rm -rf demo/v6-units demo/v6-finish.log
mkdir -p demo/v6-units

cat > demo/v6-units/sweeper.agent <<'EOF'
name          = sweeper
exec          = mkdir -p /tmp/agryp-v6-workdir-$AGRY_UNIT; sleep 1; exit 3
restart       = on-failure
max-attempts  = 3
cooldown-ms   = 700
finish        = rm -rf /tmp/agryp-v6-workdir-$AGRY_UNIT; echo "[sweeper] убрал за мёртвым" >> demo/v6-finish.log
EOF
cat > demo/v6-units/resident.agent <<'EOF'
name         = resident
exec         = echo "[resident] жив"; while :; do sleep 1; echo "[resident] hb"; done
restart      = always
budget-sec   = 60
cooldown-ms  = 1000
EOF
cat > demo/v6-units/victim.agent <<'EOF'
name        = victim
exec        = echo "[victim] обречён"; while :; do sleep 1; echo "[victim] hb"; done
restart     = always
cooldown-ms = 1000
EOF

./agryp --dir demo/v6-units > demo/v6-transcript.jsonl 2>&1 &
SUP=$!
# Гигиена Хозяина демо: любой выход убивает супервизора — сирот не оставляем (Ст. 9)
trap 'kill -TERM "$SUP" 2>/dev/null; wait "$SUP" 2>/dev/null' EXIT
sleep 3

# --- reload: изменить resident, добавить newcomer и stubborn, удалить victim ---
sed -i 's/budget-sec   = 60/budget-sec   = 90/' demo/v6-units/resident.agent
cat > demo/v6-units/newcomer.agent <<'EOF'
name         = newcomer
exec         = echo "[newcomer] пришёл по reload"; while :; do sleep 1; echo "[newcomer] hb"; done
restart      = always
cooldown-ms  = 1000
EOF
cat > demo/v6-units/stubborn.agent <<'EOF'
name        = stubborn
exec        = trap '' TERM; echo "[stubborn] TERM меня не берёт"; while :; do sleep 1; echo "[stubborn] hb"; done
restart     = always
cooldown-ms = 1000
EOF
rm demo/v6-units/victim.agent
kill -HUP "$SUP"
sleep 1.5

# Приёмка reload: событие с числами 2/1/1
grep -aq '"event":"reload","added":2,"changed":1,"removed":1' demo/v6-transcript.jsonl \
    || { echo ">> ДЕМО ПРОВАЛЕНО: reload не дал 2/1/1 (Ст. 18)"; exit 1; }
# Приёмка: victim получил exit + stopped reason reload; newcomer стартовал
grep -aq '"unit":"victim".*"event":"stopped","reason":"reload"' demo/v6-transcript.jsonl \
    || { echo ">> ДЕМО ПРОВАЛЕНО: victim не остановлен как reload (Ст. 18)"; exit 1; }
grep -aq '"unit":"newcomer".*"event":"spawn"' demo/v6-transcript.jsonl \
    || { echo ">> ДЕМО ПРОВАЛЕНО: newcomer не стартовал после reload"; exit 1; }
# Приёмка: resident жив на той же попытке, budget уже 90 — без смерти (Ст. 18)
./agryp status --dir demo/v6-units > demo/v6-status-snapshot.jsonl
grep -a '"unit":"resident","state":"RUNNING"' demo/v6-status-snapshot.jsonl | grep -aq '"attempt":1' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: resident сменил попытку при reload (кровопролитие)"; exit 1; }
grep -a '"unit":"resident","state":"RUNNING"' demo/v6-status-snapshot.jsonl | grep -aq '"budget_sec":90' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: бюджет 90 не применился к живой попытке (Ст. 18)"; exit 1; }
echo ">> демо: reload 2/1/1 без кровопролития — resident жив (attempt 1, budget 90), victim ушёл, newcomer встал"

./agrypctl --dir demo/v6-units stop stubborn >/dev/null
sleep 4

# Приёмка эскалации: TERM проигнорирован → ctl-kill → exit по сигналу 9 (Ст. 13)
grep -aq '"event":"ctl-down"' demo/v6-transcript.jsonl \
    || { echo ">> ДЕМО ПРОВАЛЕНО: нет ctl-down"; exit 1; }
grep -aq '"unit":"stubborn".*"event":"ctl-kill"' demo/v6-transcript.jsonl \
    || { echo ">> ДЕМО ПРОВАЛЕНО: упрямый юнит не добит ctl-kill (Ст. 13)"; exit 1; }
grep -a '"unit":"stubborn"' demo/v6-transcript.jsonl | grep -aq '"event":"exit","by_signal":9' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: stubborn не умер по сигналу 9"; exit 1; }
grep -a '"unit":"stubborn"' demo/v6-transcript.jsonl | grep -aq '"event":"stopped","reason":"ctl-down"' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: stubborn не остановлен с reason ctl-down"; exit 1; }
echo ">> демо: эскалация доказана — trap '' TERM пережил 3 с, ctl-kill добил группой"

sleep 2.5
# Приёмка finish-хука: 3 смерти — 3 уборки, junk-каталог не переживает попытку (Ст. 17)
N=$(grep -ac 'убрал за мёртвым' demo/v6-finish.log 2>/dev/null || true)
[ "${N:-0}" -eq 3 ] \
    || { echo ">> ДЕМО ПРОВАЛЕНО: finish-хук стрелял $N раз вместо 3 (Ст. 17)"; exit 1; }
[ ! -d /tmp/agryp-v6-workdir-sweeper ] \
    || { echo ">> ДЕМО ПРОВАЛЕНО: junk-каталог пережил смерть (Ст. 17)"; exit 1; }
grep -a '"unit":"sweeper"' demo/v6-transcript.jsonl | grep -aq '"event":"stopped","reason":"max-attempts"' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: sweeper не остановился по max-attempts"; exit 1; }
echo ">> демо: finish 3/3, junk убран, sweeper остановлен по max-attempts"

kill -TERM "$SUP" 2>/dev/null
wait "$SUP" 2>/dev/null
sleep 1

if [ -f demo/v6-units/.agryp-status ]; then
    echo ">> ДЕМО ПРОВАЛЕНО: файл статуса пережил супервизор (Ст. 13)"; exit 1
fi
ORPHANS=$(pgrep -f 'agryp-v6-workdir|v6_resident|\[stubborn\]' | wc -l)
ORPHANS=$((ORPHANS + $(pgrep -f 'sleep 1; echo' | wc -l)))
if [ "$ORPHANS" -ne 0 ]; then
    echo ">> ДЕМО ПРОВАЛЕНО: $ORPHANS сирот остались живы (Ст. 9 нарушена)"; exit 1
fi

python3 demo/audit_transcript.py demo/v6-transcript.jsonl --units demo/v6-units || exit 1
echo ">> демо Витка 6 завершено: сирот — 0, reload без крови, эскалация и finish доказаны, транскрипт: demo/v6-transcript.jsonl"
