#!/bin/sh
# Стример тикета 009: квант 500 токенов каждые 25 мс (20k/с), после
# каждой записи — рапорт в файл и SIGUSR2 супервизору (AGRY_SUPER_PID).
# Латентность казни меряет сам пострадавший: момент 10-го кванта (линия
# 5000) пишется в /tmp/agryp-stream-cross.*, последний пульс (каждые 5 мс
# после линии) — в /tmp/agryp-stream-last.*; SIGKILL группы останавливает
# пульс на месте — разница и есть задержка «пересёк — убит».
[ -n "${AGRY_TOKEN_REPORT:-}" ] || exit 3
cross=/tmp/agryp-stream-cross.$$ last=/tmp/agryp-stream-last.$$
: > "$last"
echo "[streamer] старт, pid=$$; жгу 500 токенов / 25 мс, пульс: $last"
i=0 pulses=0
while :; do
    i=$((i+1))
    echo "${AGRY_UNIT:-streamer} tokens 500" >> "$AGRY_TOKEN_REPORT"
    [ -n "${AGRY_SUPER_PID:-}" ] && kill -USR2 "$AGRY_SUPER_PID" 2>/dev/null
    date +%s%N > "$last"
    if [ "$i" -ge 10 ]; then
        [ -s "$cross" ] || date +%s%N > "$cross"
        echo "[streamer] линия 5000 пройдена ($((i*500)) токенов) — жду казнь"
        while [ "$pulses" -lt 2000 ]; do   # 10 с пульса — предохранитель
            date +%s%N > "$last"
            pulses=$((pulses+1)); sleep 0.005
        done
        echo "[streamer] пережил свой бюджет на 10 с — демо провалено"
        exit 9
    fi
    sleep 0.025
done
