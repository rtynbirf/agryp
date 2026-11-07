# trap обязан жить в самом лидере группы: `sh script` плодит второго dash,
# а супервизор казнит группу по лидеру — внешний sh trap'а не знает.
trap '' TERM
while :; do sleep 1; echo "[$AGRY_UNIT] жив вопреки TERM"; done
