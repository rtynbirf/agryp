#!/usr/bin/env bash
# Живое демо Витка 6 — SIGHUP-reload (тикет 005, школа systemd daemon-reload):
#   t=0    boot: alpha (budget 5 с) и beta (вечный цикл) — детей не трогаем
#   t=3    правки каталога: alpha budget 5→60, beta удалён, gamma добавлен; SIGHUP
#   t≈5    alpha жив на той же попытке с новым бюджетом (дети не умирают),
#          beta ушёл graceful (reason reload), gamma стартовал; reload 1/1/1
#   t=6    SIGTERM → shutdown; сирот 0; аудитор OK
set -u
cd "$(dirname "$0")/.."

# Зачистка стреев прошлого падения (два супервизора на одном каталоге лгут)
pkill -9 -f "agryp --dir demo/reload-units" 2>/dev/null
pkill -9 -f "demo/reload_worker.sh" 2>/dev/null
sleep 0.3

make -s agryp || exit 1
rm -rf demo/reload-units
mkdir -p demo/reload-units
cat > demo/reload-units/alpha.agent <<'EOF'
name        = alpha
exec        = sh demo/reload_worker.sh
restart     = always
budget-sec  = 5
cooldown-ms = 800
EOF
cat > demo/reload-units/beta.agent <<'EOF'
name        = beta
exec        = sh demo/reload_worker.sh
restart     = always
cooldown-ms = 800
EOF
cat > demo/reload_worker.sh <<'EOF'
echo "[$AGRY_UNIT] старт попытки $$"
while :; do sleep 1; echo "[$AGRY_UNIT] heartbeat"; done
EOF

./agryp --dir demo/reload-units > demo/reload-transcript.jsonl 2>&1 &
SUP=$!
sleep 3

# Правки договоров: изменить alpha, удалить beta, добавить gamma — без смерти детей
cat > demo/reload-units/alpha.agent <<'EOF'
name        = alpha
exec        = sh demo/reload_worker.sh
restart     = always
budget-sec  = 60
cooldown-ms = 800
EOF
rm demo/reload-units/beta.agent
cat > demo/reload-units/gamma.agent <<'EOF'
name        = gamma
exec        = sh demo/reload_worker.sh
restart     = always
cooldown-ms = 800
EOF
kill -HUP "$SUP"
sleep 2

# Приёмка 1: alpha жив на той же попытке с новым бюджетом (дети не умирают)
grep -a '"unit":"alpha","state":"RUNNING"' demo/reload-status-snapshot.jsonl 2>/dev/null >/dev/null
./agryp status --dir demo/reload-units > demo/reload-status-snapshot.jsonl
grep -a '"unit":"alpha","state":"RUNNING"' demo/reload-status-snapshot.jsonl | grep -aq '"budget_sec":60' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: бюджет alpha не применился без перезапуска (reload лжёт)"; exit 1; }
A_SPAWNS=$(grep -a '"unit":"alpha"' demo/reload-transcript.jsonl | grep -ac '"event":"spawn"')
[ "$A_SPAWNS" -eq 1 ] \
    || { echo ">> ДЕМО ПРОВАЛЕНО: alpha перезапускался при reload — дети умирают (Ст. 9)"; exit 1; }
echo ">> демо: alpha жив на attempt 1 с budget_sec=60 — дедлайн пересчитан от живой попытки"

# Приёмка 2: beta ушёл graceful — exit и stopped reason reload, без KILL
grep -a '"unit":"beta"' demo/reload-transcript.jsonl | grep -aq '"reason":"reload"' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: beta не получил graceful-stop по Ст. 9"; exit 1; }
grep -a '"unit":"beta"' demo/reload-transcript.jsonl | grep -aq '"by_signal":15' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: beta умер не от TERM группы"; exit 1; }

# Приёмка 3: gamma появился и стартовал
grep -aq '"event":"unit-added"' demo/reload-transcript.jsonl \
    || { echo ">> ДЕМО ПРОВАЛЕНО: нет unit-added"; exit 1; }
grep -a '"unit":"gamma"' demo/reload-transcript.jsonl | grep -aq '"event":"spawn"' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: gamma не стартовал после reload"; exit 1; }

# Приёмка 4: событие reload с честными числами 1/1/1
grep -aq '"event":"reload","added":1,"changed":1,"removed":1' demo/reload-transcript.jsonl \
    || { echo ">> ДЕМО ПРОВАЛЕНО: событие reload не сходится с правками (1/1/1)"; exit 1; }
echo ">> демо: reload 1/1/1 — alpha изменён, beta удалён graceful, gamma добавлен"

kill -TERM "$SUP" 2>/dev/null
wait "$SUP" 2>/dev/null
sleep 1

ORPHANS=$(pgrep -f 'demo/reload_worker.sh' | wc -l)
if [ "$ORPHANS" -ne 0 ]; then
    echo ">> ДЕМО ПРОВАЛЕНО: $ORPHANS сирот остались живы (Ст. 9 нарушена)"; exit 1
fi

python3 demo/audit_transcript.py demo/reload-transcript.jsonl || exit 1
echo ">> демо Витка 6 (reload) завершено: сирот — 0, транскрипт: demo/reload-transcript.jsonl"
