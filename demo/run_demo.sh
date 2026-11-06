#!/usr/bin/env bash
# Живое демо agryp (35 с) — три статьи одним атомом:
#   t=0    boot; Ст. 15: клетка памяти — в среде без cgroups честный cgroup-skip
#   t=5    kill -9 -- -PGID всей группе процессов hello (Ст. 9)
#   t=15   Ст. 13: ./agryp status снимает NDJSON-срез → demo/status-snapshot.jsonl
#   t≈16   Ст. 14: попытка hello переросла token-budget 5000 → token-kill
#   t=35   SIGTERM → graceful shutdown; сирот 0; файла статуса больше нет
set -u
cd "$(dirname "$0")/.."

make -s agryp || exit 1

./agryp --dir examples > demo/demo-transcript.jsonl 2>&1 &
SUP=$!
sleep 5

PID=$(grep -a '"unit":"hello"' demo/demo-transcript.jsonl \
      | grep -a '"event":"spawn"' | tail -1 \
      | sed -E 's/.*"pid":([0-9]+).*/\1/')
if [ -n "${PID:-}" ]; then
    kill -9 -- "-$PID" 2>/dev/null \
        && echo ">> демо: kill -9 -- -$PID отправлен группе процессов hello"
fi

sleep 10
./agryp status --dir examples > demo/status-snapshot.jsonl
if [ -s demo/status-snapshot.jsonl ]; then
    echo ">> демо: Ст. 13 — статус снят в t=15, семья живая (NDJSON в demo/status-snapshot.jsonl)"
else
    echo ">> ДЕМО ПРОВАЛЕНО: статус-файл пуст при живом супервизоре (Ст. 13)"; exit 1
fi

sleep 20
kill -TERM "$SUP" 2>/dev/null
wait "$SUP" 2>/dev/null
sleep 1

if [ -f examples/.agryp-status ]; then
    echo ">> ДЕМО ПРОВАЛЕНО: файл статуса пережил супервизор (Ст. 13)"; exit 1
fi
ORPHANS=$(pgrep -f 'demo/hello_agent.sh|demo/crashy_agent.sh' | wc -l)
if [ "$ORPHANS" -ne 0 ]; then
    echo ">> ДЕМО ПРОВАЛЕНО: $ORPHANS сирот остались живы (Ст. 9 нарушена)"
    exit 1
fi
echo ">> демо завершено: сирот — 0, файла статуса нет, транскрипт: demo/demo-transcript.jsonl"
