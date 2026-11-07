#!/usr/bin/env bash
# Демо витка 7, тикет 009: токен-казнь без запаздывания итерации.
# Стример жжёт 20k токенов/с и будит супервизор SIGUSR2 после каждого
# кванта; момент пересечения бюджета (линия 5000) и последний пульс
# (каждые 5 мс) пишутся самим стримером в /tmp — разница есть латентность
# «пересёк — убит». Приёмка: ≤ 300 мс.
set -u
cd "$(dirname "$0")/.."
make -s agryp || exit 1

# зачистка стреев (урок ТЗ-6)
pkill -f 'agryp --dir demo/stream-units' 2>/dev/null && sleep 0.3
rm -f demo/stream-units/.agryp-status demo/stream-units/.agryp-report
rm -f /tmp/agryp-stream-cross.* /tmp/agryp-stream-last.* 2>/dev/null
rm -f demo/stream-transcript.jsonl

./agryp --dir demo/stream-units > demo/stream-transcript.jsonl 2>&1 &
SUP=$!
sleep 4
kill -TERM "$SUP" 2>/dev/null
wait "$SUP" 2>/dev/null
sleep 1
[ -f demo/stream-units/.agryp-status ] && {
    echo ">> ДЕМО ПРОВАЛЕНО: файл статуса пережил супервизора (Ст. 13)"; exit 1; }

FAIL=0
TKILL=$(grep -a '"event":"token-kill"' demo/stream-transcript.jsonl | tail -1)
[ -n "$TKILL" ] || { echo ">> ДЕМО ПРОВАЛЕНО: token-kill не пришёл — стример пережил бюджет"; FAIL=1; }
TOKENS=$(printf '%s' "$TKILL" | sed -nE 's/.*"tokens":([0-9]+).*/\1/p')
[ -n "$TOKENS" ] && [ "$TOKENS" -le 6000 ] \
    || { echo ">> ДЕМО ПРОВАЛЕНО: казнь пришла с tokens=$TOKENS — будильник не сработал (тик вместо звона)"; FAIL=1; }

CROSS=$(cat /tmp/agryp-stream-cross.* 2>/dev/null | tail -1)
LAST=$(cat /tmp/agryp-stream-last.* 2>/dev/null | tail -1)
if [ -n "$CROSS" ] && [ -n "$LAST" ]; then
    LAT=$(( (LAST - CROSS) / 1000000 ))
    [ "$LAT" -le 300 ] || { echo ">> ДЕМО ПРОВАЛЕНО: латентность казни ${LAT} мс > 300 мс"; FAIL=1; }
    echo ">> демо: пересёк 5000 → SIGKILL за ${LAT} мс (приёмка ≤ 300 мс); в token-kill tokens=$TOKENS"
else
    echo ">> демо: казнь пришла до первого пульса после линии — латентность < 5 мс; tokens=$TOKENS"
fi

ORPHANS=$(pgrep -f 'stream_worker' | wc -l)
[ "$ORPHANS" -eq 0 ] || { echo ">> ПРОВАЛЕНО: сирот $ORPHANS (Ст. 9)"; FAIL=1; }

python3 demo/audit_transcript.py demo/stream-transcript.jsonl || FAIL=1

[ "$FAIL" -eq 0 ] \
    && echo ">> демо-stream завершено: burn-rate без запаздывания итерации, сирот 0" \
    || exit 1
