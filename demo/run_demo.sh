#!/usr/bin/env bash
# Живое демо agryp:
#   t=0    супервизор поднимает hello (restart=always, budget 8 c)
#          и crashy (restart=on-failure, падает каждые 2 c)
#   t=5    мы убиваем процесс hello командой kill -9
#          → agryp фиксирует смерть (by_signal 9) и поднимает новую попытку
#   t≈14   попытка hello перерастает бюджет 8 с
#          → agryp сам режет её SIGKILL и перезапускает
#   t=30   SIGTERM супервизору → graceful shutdown + summary по каждому агенту
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
    kill -9 "$PID" 2>/dev/null && echo ">> демо: kill -9 $PID отправлен агенту hello"
fi

sleep 25
kill -TERM "$SUP" 2>/dev/null
wait "$SUP" 2>/dev/null
echo ">> демо завершено, транскрипт: demo/demo-transcript.jsonl"
