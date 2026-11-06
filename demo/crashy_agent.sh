#!/usr/bin/env bash
# Демо-агент «crashy»: честно работает 2 секунды и падает с кодом 3.
echo "[crashy-agent] попытка pid=$$: работаю 2 секунды и упаду"
sleep 2
exit 3
