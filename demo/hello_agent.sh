#!/usr/bin/env bash
# Демо-агент «hello»: живёт вечно, раз в секунду шлёт heartbeat.
# Его убьют дважды: снаружи kill -9 (демо отказоустойчивости)
# и самим agryp по бюджету попытки.
echo "[hello-agent] старт, pid=$$"
i=0
while true; do
  i=$((i+1))
  echo "[hello-agent] heartbeat #$i pid=$$"
  sleep 1
done
