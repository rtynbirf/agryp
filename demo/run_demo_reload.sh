#!/usr/bin/env bash
# Живое демо Витка 6 + Витка 11 (тикеты 005, 017; школа systemd daemon-reload
# и Type=notify-reload):
#   t=0    boot: alpha (budget 5 с), beta (вечный цикл), stubborn (trap '' TERM)
#   t=3    правки каталога: alpha budget 5→60, beta и stubborn удалены,
#          gamma добавлен; SIGHUP
#   t≈3    alpha жив на той же попытке с новым бюджетом (дети не умирают),
#          beta ушёл graceful (reason reload), gamma стартовал;
#          reload 1/1/2 gen=1 — скобка reload→reload-done открыта
#   t≈3.3  stubborn игнорирует TERM — по GRACE_MS казнь законом reload-kill,
#          exit по сигналу 9, пыль легла — reload-done gen=1 1/1/2, ms ≥ 3000
#   t=8    SIGTERM → shutdown; сирот 0; аудитор OK (правила №11-№12)
set -u
cd "$(dirname "$0")/.."

# Зачистка стреев прошлого падения (два супервизора на одном каталоге лгут)
pkill -9 -f "agryp --dir demo/reload-units" 2>/dev/null
pkill -9 -f "demo/reload_worker.sh" 2>/dev/null
pkill -9 -f "demo/reload_stubborn.sh" 2>/dev/null
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
cat > demo/reload-units/stubborn.agent <<'EOF'
name        = stubborn
exec        = exec sh demo/reload_stubborn.sh
restart     = always
cooldown-ms = 800
EOF
cat > demo/reload_worker.sh <<'EOF'
echo "[$AGRY_UNIT] старт попытки $$"
while :; do sleep 1; echo "[$AGRY_UNIT] heartbeat"; done
EOF
cat > demo/reload_stubborn.sh <<'EOF'
trap '' TERM
echo "[stubborn] старт попытки $$, TERM игнорирую"
while :; do sleep 1; echo "[stubborn] heartbeat"; done
EOF

./agryp --dir demo/reload-units > demo/reload-transcript.jsonl 2>&1 &
SUP=$!
sleep 3

# Правки договоров: изменить alpha, удалить beta и stubborn, добавить gamma
cat > demo/reload-units/alpha.agent <<'EOF'
name        = alpha
exec        = sh demo/reload_worker.sh
restart     = always
budget-sec  = 60
cooldown-ms = 800
EOF
rm demo/reload-units/beta.agent demo/reload-units/stubborn.agent
cat > demo/reload-units/gamma.agent <<'EOF'
name        = gamma
exec        = sh demo/reload_worker.sh
restart     = always
cooldown-ms = 800
EOF
kill -HUP "$SUP"
sleep 4.5

# Приёмка 1: alpha жив на той же попытке с новым бюджетом (дети не умирают)
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

# Приёмка 4 (тикет 017): событие reload с числами и gen — скобка открыта
grep -aq '"event":"reload","added":1,"changed":1,"removed":2,"skipped":0,"gen":1' demo/reload-transcript.jsonl \
    || { echo ">> ДЕМО ПРОВАЛЕНО: reload не объявил 1/1/2 skipped=0 gen=1"; exit 1; }
echo ">> демо: reload 1/1/2 gen=1 — alpha изменён, beta+stubborn удалены, gamma добавлен"

# Приёмка 5 (тикет 017): stubborn игнорировал TERM — казнь законом reload-kill
grep -a '"unit":"stubborn"' demo/reload-transcript.jsonl | grep -aq '"event":"reload-kill"' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: stubborn не получил reload-kill по GRACE_MS"; exit 1; }
grep -a '"unit":"stubborn"' demo/reload-transcript.jsonl | grep -aq '"by_signal":9' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: stubborn умер не от SIGKILL группы"; exit 1; }
echo ">> демо: stubborn добит reload-kill после GRACE_MS — exit по сигналу 9"

# Приёмка 6 (тикет 017): скобка закрыта reload-done с теми же числами и gen,
# ms — реальное время оседания: stubborn заставил скобку жить ≥ GRACE_MS
DONE=$(grep -a '"event":"reload-done","gen":1,"added":1,"changed":1,"removed":2' demo/reload-transcript.jsonl)
MS=$(echo "$DONE" | head -1 | sed -n 's/.*"ms":\([0-9]*\).*/\1/p')
[ -n "$MS" ] && [ "$MS" -ge 3000 ] \
    || { echo ">> ДЕМО ПРОВАЛЕНО: reload-done ms='$MS' < 3000 — скобка закрылась без ожидания пыли: $DONE"; exit 1; }
echo ">> демо: reload-done gen=1 1/1/2 закрыл скобку, ms ≥ 3000 — пыль осела честно"

kill -TERM "$SUP" 2>/dev/null
wait "$SUP" 2>/dev/null
sleep 1

ORPHANS=$(pgrep -f 'reload_worker.sh|reload_stubborn.sh' | wc -l)
if [ "$ORPHANS" -ne 0 ]; then
    echo ">> ДЕМО ПРОВАЛЕНО: $ORPHANS сирот остались живы (Ст. 9 нарушена)"; exit 1
fi

python3 demo/audit_transcript.py demo/reload-transcript.jsonl || exit 1
echo ">> демо Витка 6+11 (reload, скобка) завершено: сирот — 0, транскрипт: demo/reload-transcript.jsonl"
