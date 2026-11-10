#!/bin/sh
# Негативные пробы аудитора (Виток 11, тикет 018; школа fail-closed и
# «проверяльщик проверяльщика» — свёрка 5.2). Проверка сама доказывает,
# что ей можно верить:
#   1) канарейка (честный журнал) обязана быть ЗЕЛЁНОЙ — аудитор не
#      разучился верить правде;
#   2) каждая проба из MANIFEST.tsv обязана быть КРАСНОЙ С ТОЙ ПРИЧИНОЙ —
#      пропущенная выдумка или краснота «не по делу» = проба провалена.
# rc=0 — аудитору можно верить; rc=1 — нельзя (и CI красный).
set -u
cd "$(dirname "$0")/.."

fail=0
n_probes=0

AGRY_AUDIT_UNITS=tests/negative/units python3 demo/audit_transcript.py \
    tests/positive/canary.jsonl >/tmp/agryp-canary.out 2>&1
if [ $? -eq 0 ]; then
    echo ">> канарейка зелёная: аудитору можно верить на честном журнале"
else
    echo ">> ПРОБА ПРОВАЛЕНА: канарейка красная — аудитор отверг правду:"
    cat /tmp/agryp-canary.out
    fail=1
fi

while IFS="	" read -r fname want; do
    [ -z "${fname:-}" ] && continue
    case "$fname" in \#*) continue ;; esac
    n_probes=$((n_probes + 1))
    out=$(AGRY_AUDIT_UNITS=tests/negative/units \
          python3 demo/audit_transcript.py "tests/negative/$fname" 2>&1)
    rc=$?
    if [ "$rc" -eq 0 ]; then
        echo ">> ПРОБА ПРОВАЛЕНА: $fname — аудитор пропустил выдумку (жду красного: '$want')"
        echo "$out" | head -5
        fail=1
    elif printf '%s' "$out" | grep -aq "$want"; then
        echo ">> проба $fname: красная по делу — '$want'"
    else
        echo ">> ПРОБА ПРОВАЛЕНА: $fname — красный не по той причине (жду '$want'):"
        echo "$out" | head -5
        fail=1
    fi
done < tests/negative/MANIFEST.tsv

if [ "$fail" -eq 0 ]; then
    echo ">> проверяльщик проверен: канарейка зелёная, $n_probes проб красных по делу — аудитору верить можно"
    exit 0
fi
echo ">> аудитору НЕЛЬЗЯ верить — проба провалена"
exit 1
