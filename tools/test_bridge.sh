#!/bin/sh
# Приёмка тикета 008 (виток 7): трансляция examples/*.agent туда-обратно —
# семантика restart/budget/cooldown/mem/max-attempts сохраняется; потери
# (token-budget, jail) объявлены в шапке .service. systemd-analyze verify
# прогоняется, если доступен, — иначе пропуск вслух (Ст. 6).
set -u
cd "$(dirname "$0")/.."
tmp=$(mktemp -d) || exit 2
trap 'rm -rf "$tmp"' EXIT
fail=0

for f in examples/*.agent; do
    stem=$(basename "$f" .agent)
    sh tools/agent2unit.sh "$f" > "$tmp/$stem.service" || { fail=1; continue; }
    sh tools/unit2agent.sh "$tmp/$stem.service" > "$tmp/$stem.agent" \
        || { fail=1; continue; }
    python3 tools/bridge_compare.py "$f" "$tmp/$stem.agent" "$tmp/$stem.service" \
        || fail=1
done

if command -v systemd-analyze >/dev/null 2>&1; then
    for s in "$tmp"/*.service; do
        out=$(systemd-analyze verify "$s" 2>&1) || { echo "  verify FAIL: $out"; fail=1; }
    done
    echo ">> systemd-analyze verify: прогнан на всех порождённых .service"
else
    echo ">> systemd-analyze недоступен — проверка пропущена вслух (Ст. 6)"
fi

[ "$fail" -eq 0 ] && echo "OK: мост туда-обратно зелёный" \
    || { echo "FAIL: мост врёт"; exit 1; }
