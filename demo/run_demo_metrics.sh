#!/usr/bin/env bash
# Живое демо Витка 10 — экспорт метрик в файл (тикет 011, Ст. 13):
#   t=0    boot: hello (вечный) и crashy (падучий, лестница Ст. 8)
#   t≈4    .agryp-metrics.prom существует, формат OpenMetrics, счётчики
#          сходятся с журналом транскрипта; `agryp metrics` читает тот же файл
#   t=5    SIGTERM → metrics файл снят (мёртвый не притворяется живым)
set -u
cd "$(dirname "$0")/.."

pkill -9 -f "agryp --dir demo/metrics-units" 2>/dev/null
sleep 0.3

make -s agryp || exit 1
rm -rf demo/metrics-units
mkdir -p demo/metrics-units
cp examples/hello.agent  demo/metrics-units/hello.agent
cp examples/crashy.agent demo/metrics-units/crashy.agent

./agryp --dir demo/metrics-units > demo/metrics-transcript.jsonl 2>&1 &
SUP=$!
sleep 4

# Приёмка 1: файл жив, формат валиден grepp'ом на OpenMetrics
[ -f demo/metrics-units/.agryp-metrics.prom ] \
    || { echo ">> ДЕМО ПРОВАЛЕНО: .agryp-metrics.prom не появился"; exit 1; }
M=demo/metrics-units/.agryp-metrics.prom
grep -aq '^# HELP agryp_up_ms ' "$M" || { echo ">> ДЕМО ПРОВАЛЕНО: нет HELP agryp_up_ms"; exit 1; }
grep -aq '^# TYPE agryp_orphans_total counter' "$M" || { echo ">> ДЕМО ПРОВАЛЕНО: TYPE counter не объявлен"; exit 1; }
# каждая содержательная строка: metric{label="x"} value — без мусора
if grep -vE '^(#|$)' "$M" | grep -qvE '^agryp_[a-z_]+(\{unit="[^"]*"\})? [0-9]+$'; then
    echo ">> ДЕМО ПРОВАЛЕНО: в .prom есть строки не по формату:"; grep -vE '^(#|$)' "$M" | grep -vE '^agryp_[a-z_]+(\{unit="[^"]*"\})? [0-9]+$'; exit 1
fi
echo ">> демо: .prom валиден — HELP/TYPE на месте, все значения числовые"

# Приёмка 2: счётчики сходятся с журналом (Совпадает = правда одна)
for u in hello crashy; do
    M_ATT=$(sed -n "s/^agryp_attempts_total{unit=\"$u\"} \([0-9]*\)$/\\1/p" "$M")
    J_ATT=$(grep -a "\"unit\":\"$u\"" demo/metrics-transcript.jsonl | grep -ac '"event":"spawn"')
    [ -n "$M_ATT" ] && [ "$M_ATT" -eq "$J_ATT" ] \
        || { echo ">> ДЕМО ПРОВАЛЕНО: attempts $u в .prom=$M_ATT, в журнале spawn'ов=$J_ATT"; exit 1; }
done
# сумма exits_ok по всем юнитам .prom == число exit ok:true в транскрипте
M_OK=$(grep -c '^agryp_exits_ok_total' "$M" | sed 's/^/x/') # наличие метрик
M_OK_SUM=$(grep '^agryp_exits_ok_total' "$M" | awk '{s+=$NF} END{print s+0}')
J_OK=$(grep -ac '"event":"exit".*"ok":true' demo/metrics-transcript.jsonl)
[ "$M_OK_SUM" -eq "$J_OK" ] \
    || { echo ">> ДЕМО ПРОВАЛЕНО: exits_ok сумма .prom=$M_OK_SUM, журнал=$J_OK"; exit 1; }
echo ">> демо: счётчики .prom == журнал (attempts/exits_ok — одна правда на два носителя)"

# Приёмка 3: agryp metrics читает тот же файл (Ст. 13 — не второй источник).
# Детерминизм: супервизор в цикле переписывает .prom (agryp_up_ms живёт, мс),
# поэтому на время сверки замораживаем его STOP'ом — файл стабилен, гонки нет
# (урок прогона 42647663156: красный на живом файле — гонка демо, не баг кода).
kill -STOP "$SUP" 2>/dev/null
sleep 0.3
./agryp metrics --dir demo/metrics-units > demo/metrics-ctl-snapshot.prom
diff -q "$M" demo/metrics-ctl-snapshot.prom >/dev/null \
    || { echo ">> ДЕМО ПРОВАЛЕНО: agryp metrics отдал не то, что в файле"; kill -CONT "$SUP" 2>/dev/null; exit 1; }
kill -CONT "$SUP" 2>/dev/null
echo ">> демо: agryp metrics == файл (одна правда, ноль сокетов)"

kill -TERM "$SUP" 2>/dev/null
wait "$SUP" 2>/dev/null
sleep 1

[ ! -f "$M" ] || { echo ">> ДЕМО ПРОВАЛЕНО: .prom остался после смерти супервизора — мёртвый притворяется живым"; exit 1; }
[ -f demo/metrics-units/.agryp-journal.ndjson ] \
    || { echo ">> ДЕМО ПРОВАЛЕНО: журнал-файл не дожил до конца — история потеряна"; exit 1; }

python3 demo/audit_transcript.py demo/metrics-transcript.jsonl || exit 1
echo ">> демо Витка 10 (метрики) завершено: транскрипт demo/metrics-transcript.jsonl, метрики сняты и сверены"
