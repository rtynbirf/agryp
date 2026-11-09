#!/usr/bin/env bash
# Живое демо Витка 6 — finish-хук (тикет 004, школа s6 ./finish) + Виток 11 —
# per-unit потолок хука (тикет 015, школа s6 timeout-finish, дефолт 5000):
#   t=0    boot: sweeper живёт 2 с и падает с кодом 3, база лестницы 500 мс;
#          slowfin живёт 1 с, падает с кодом 7, хук хочет 2 с — а его
#          finish-timeout-ms=600: упор вслух, добит SIGKILL'ом (Ст. 11)
#   t=9    SIGTERM; к этому моменту ≥3 смертей, после каждой — finish-хук
# Проверки: след уборки в demo/finish-sweep.log; finish в журнале по каждой
# смерти (аудитор сверяет 1:1); slowfin упёрся в свой потолок ≥2 раз;
# сирот 0; аудит OK.
set -u
cd "$(dirname "$0")/.."

# Зачистка стреев прошлого падения (два супервизора на одном каталоге лгут)
pkill -9 -f "agryp --dir demo/finish-units" 2>/dev/null
pkill -9 -f "demo/finish_worker.sh" 2>/dev/null
sleep 0.3

make -s agryp || exit 1
mkdir -p demo/finish-units
rm -f demo/finish-sweep.log
cat > demo/finish-units/sweeper.agent <<'EOF'
name         = sweeper
exec         = sh demo/finish_worker.sh
restart      = always
cooldown-ms  = 500
finish       = echo "sweep unit=$AGRY_UNIT code=$AGRY_EXIT_CODE sig=$AGRY_BY_SIGNAL" >> demo/finish-sweep.log
EOF
cat > demo/finish-units/slowfin.agent <<'EOF'
name              = slowfin
exec              = sleep 1; exit 7
restart           = always
cooldown-ms       = 300
finish-timeout-ms = 600
finish            = sleep 2
EOF

./agryp --dir demo/finish-units > demo/finish-transcript.jsonl 2>&1 &
SUP=$!
sleep 9
kill -TERM "$SUP" 2>/dev/null
wait "$SUP" 2>/dev/null
sleep 1

SWEEPS=$(grep -ac '^sweep ' demo/finish-sweep.log 2>/dev/null)
SWEEPS=${SWEEPS:-0}
FINISHES=$(grep -ac '"event":"finish"' demo/finish-transcript.jsonl)
EXITS=$(grep -ac '"event":"exit"' demo/finish-transcript.jsonl)
if [ "$SWEEPS" -lt 3 ]; then
    echo ">> ДЕМО ПРОВАЛЕНО: хук отработал $SWEEPS раз (нужно ≥3) — уборка не пахала"; exit 1
fi
if [ "$FINISHES" -ne "$EXITS" ] || [ "$FINISHES" -lt 3 ]; then
    echo ">> ДЕМО ПРОВАЛЕНО: finish в журнале $FINISHES, exit'ов $EXITS — что-то умерло молча (Ст. 6)"; exit 1
fi
FTO=$(grep -a '"unit":"slowfin"' demo/finish-transcript.jsonl | grep -ac '"timeout":true,"ms":600')
if [ "$FTO" -lt 2 ]; then
    echo ">> ДЕМО ПРОВАЛЕНО: slowfin упёрся в свой потолок $FTO раз (нужно ≥2) — finish-timeout-ms не пахал (Виток 11)"; exit 1
fi
echo ">> демо: $EXITS смертей → $FINISHES finish-хуков, след уборки: demo/finish-sweep.log ($SWEEPS строк)"
echo ">> демо: slowfin хотел 2 с прощания — добит per-unit finish-timeout-ms=600 ×$FTO (s6 timeout-finish, Виток 11)"

ORPHANS=$(pgrep -f 'demo/finish_worker.sh' | wc -l)
if [ "$ORPHANS" -ne 0 ]; then
    echo ">> ДЕМО ПРОВАЛЕНО: $ORPHANS сирот остались живы (Ст. 9 нарушена)"; exit 1
fi

python3 demo/audit_transcript.py demo/finish-transcript.jsonl || exit 1
echo ">> демо Витка 6 (finish) завершено: сирот — 0, транскрипт: demo/finish-transcript.jsonl"
