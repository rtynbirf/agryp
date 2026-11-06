#!/usr/bin/env bash
# Демо-агент «hello»: живёт вечно, раз в секунду heartbeat + self-report.
# Договор hook'а (Ст. 14): канал приходит в env, как sd_notify у systemd;
# каждый heartbeat = 500 токенов в файл отчёта. Без env — просто работает.
echo "[hello-agent] старт, pid=$$"
i=0
while true; do
  i=$((i+1))
  echo "[hello-agent] heartbeat #$i pid=$$"
  [ -n "${AGRY_TOKEN_REPORT:-}" ] && \
      echo "${AGRY_UNIT:-unknown} tokens 500" >> "$AGRY_TOKEN_REPORT"
  sleep 1
done
