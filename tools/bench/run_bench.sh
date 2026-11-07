#!/bin/sh
# Бенчмарк витка 8 (ТЗ-8 §2): ферма 100 агентов, одинаковые испытания,
# сырые числа в JSONL. Метрики M1–M7 — см. docs/spec/TZ-8.md.
# Агент — нативной формы (один процесс): dash ведёт одиночный цикл сам.
# M7 — граница Ст. 9: агент с внуками переживает kill -9 супервизора.
set -u
cd "$(dirname "$0")/../.."
WORK=${WORK:-/tmp/agryp-bench}
OUT=docs/bench
mkdir -p "$WORK/units" "$WORK/one" "$WORK/units7" "$OUT"
TR="$OUT/bench-transcript.jsonl"
: > "$TR"

rss() { awk '/VmRSS/{print $2}' "/proc/$1/status" 2>/dev/null | head -1; }
med3() { printf '%s\n' "$1" "$2" "$3" | sort -n | sed -n 2p; }
workers() { pgrep -c -f "while :" 2>/dev/null | head -1; }
emit() { printf '{"ts":"%s",%s}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" >> "$TR"; }

# --- ферма 100 тихих агентов (нативная форма: цикл = сам процесс) ---
i=1
while [ "$i" -le 100 ]; do
    n=$(printf 'farm-%03d' "$i")
    cat > "$WORK/units/$n.agent" <<EOF
# Бенчмарк-агент ТЗ-8: тихий, вечный, один процесс.
name        = $n
exec        = while :; do sleep 1; done
restart     = always
cooldown-ms = 250
EOF
    i=$((i + 1))
done

# --- M1: бинарь ---
b=$(wc -c < ./agryp)
deps=$(ldd ./agryp 2>/dev/null | wc -l)
emit "\"participant\":\"agryp\",\"metric\":\"M1\",\"binary_bytes\":$b,\"dyn_deps\":$deps,\"deps_note\":\"libc only\""

# --- M2: покой (1 агент — ядро требует >=1 юнит) ---
cat > "$WORK/one/solo.agent" <<'EOF'
name = solo
exec = while :; do sleep 1; done
restart = always
EOF
./agryp --dir "$WORK/one" > "$WORK/one.log" 2>&1 &
P1=$!
sleep 3
a=$(rss "$P1"); sleep 1; b2=$(rss "$P1"); sleep 1; c=$(rss "$P1")
m2med=$(med3 "$a" "$b2" "$c")
kill -9 "$P1" 2>/dev/null
sleep 5
m2orph=$(workers)
emit "\"participant\":\"agryp\",\"metric\":\"M2\",\"rss_kb_samples\":[$a,$b2,$c],\"rss_kb_median\":$m2med,\"agents\":1,\"orphans_after_kill9\":$m2orph,\"note\":\"0 агентов ядро не поддерживает (Ст. 11): покой = 1 агент\""

pkill -9 -f "while :" 2>/dev/null   # унести остатки M2 до фермы
sleep 1

# --- ферма: старт, разгон ---
./agryp --dir "$WORK/units" > "$WORK/farm.log" 2>&1 &
P=$!
sleep 5
wfarm=$(workers)

# --- M3: RSS супервизора при 100 агентах ---
a=$(rss "$P"); sleep 1; b2=$(rss "$P"); sleep 1; c=$(rss "$P")
m3med=$(med3 "$a" "$b2" "$c")
emit "\"participant\":\"agryp\",\"metric\":\"M3\",\"agents\":100,\"workers_seen\":$wfarm,\"rss_kb_samples\":[$a,$b2,$c],\"rss_kb_median\":$m3med"

# --- M4: журнал за ровно 30 с при тихой ферме ---
s1=$(wc -c < "$WORK/farm.log")
sleep 30
s2=$(wc -c < "$WORK/farm.log")
emit "\"participant\":\"agryp\",\"metric\":\"M4\",\"window_sec\":30,\"journal_bytes_delta\":$((s2 - s1))"

# --- M6: рестарт одного агента ---
sp1=$(grep -c '"event":"spawn"' "$WORK/farm.log")
victim=$(pgrep -f "while :" | head -1)
kill -9 "$victim" 2>/dev/null
sleep 10
wfarm2=$(workers)
sp2=$(grep -c '"event":"spawn"' "$WORK/farm.log")
emit "\"participant\":\"agryp\",\"metric\":\"M6\",\"workers_before\":$wfarm,\"workers_after\":$wfarm2,\"spawn_events_before\":$sp1,\"spawn_events_after\":$sp2"

# --- M5: сироты после kill -9 супервизора (нативные агенты) ---
kill -9 "$P" 2>/dev/null
sleep 5
orph=$(workers)
emit "\"participant\":\"agryp\",\"metric\":\"M5\",\"agents\":100,\"orphans_after_5s\":$orph,\"expect\":\"0: PDEATHSIG убивает прямого ребёнка — он и есть агент\""

pkill -9 -f "while :" 2>/dev/null
sleep 1

# --- M7: граница Ст. 9 — агент с внуками (вложенный sh) ---
i=1
while [ "$i" -le 20 ]; do
    n=$(printf 'nest-%02d' "$i")
    cat > "$WORK/units7/$n.agent" <<EOF
# Агент-граница: сам порождает ребёнка (как настоящий агент с тулами).
name = $n
exec = /bin/sh -c 'while :; do sleep 1; done'
restart = always
cooldown-ms = 250
EOF
    i=$((i + 1))
done
./agryp --dir "$WORK/units7" > "$WORK/nest.log" 2>&1 &
P7=$!
sleep 5
wb=$(workers)
kill -9 "$P7" 2>/dev/null
sleep 5
wa=$(workers)
emit "\"participant\":\"agryp\",\"metric\":\"M7\",\"agents\":20,\"procs_before_kill\":$wb,\"grandchildren_orphans\":$wa,\"verdict\":\"граница Ст. 9: PDEATHSIG — один уровень; внуки переживают супервизора; дом-ответ — jail=pid (pid_namespaces(7): смерть init убивает комнату)\""

pkill -9 -f "while :" 2>/dev/null
echo "agryp-bench: транскрипт $TR; M5 сироты=$orph; M7 внуки-сироты=$wa"
