trap '' TERM
echo "[stubborn] старт попытки $$, TERM игнорирую"
while :; do sleep 1; echo "[stubborn] heartbeat"; done
