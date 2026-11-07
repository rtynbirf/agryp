#!/bin/sh
# Бенчмарк витка 8 (ТЗ-8 §3): stdiobus v2.0.3, те же испытания M1–M6.
# Требует бинарь сверстника: STDIOBUS_BIN (или клон в /tmp/peers/stdiobus).
set -u
cd "$(dirname "$0")/../.."
BIN=${STDIOBUS_BIN:-/tmp/peers/stdiobus/releases/v2.0.3/linux-amd64/stdio_bus}
SRC=${STDIOBUS_SRC:-/tmp/peers/stdiobus}
[ -x "$BIN" ] || { echo "stdiobus-бинарь не найден: $BIN" >&2; exit 2; }
WORK=${WORK:-/tmp/stdiobus-bench}
OUT=docs/bench
mkdir -p "$WORK" "$OUT"
T=$(date -u +%Y-%m-%dT%H:%M:%SZ)
TR="$OUT/stdiobus-transcript.jsonl"
: > "$TR"

rss() { awk '/VmRSS/{print $2}' "/proc/$1/status" 2>/dev/null | head -1; }
med3() { printf '%s\n' "$1" "$2" "$3" | sort -n | sed -n 2p; }
workers() { pgrep -c -f "while :" 2>/dev/null | head -1; }
emit() { printf '%s\n' "$1" >> "$TR"; }
commit=$(git -C "$SRC" rev-parse HEAD 2>/dev/null || echo unknown)

cfg() { # $1 = instances, $2 = путь конфига
    printf '{"pools":[{"id":"farm","command":"/bin/sh","args":["-c","while :; do sleep 1; done"],"instances":%s}],"limits":{"max_restarts":5,"restart_window_sec":60,"drain_timeout_sec":30}}' "$1" > "$2"
}

# --- M1 ---
b=$(wc -c < "$BIN")
deps=$(ldd "$BIN" 2>/dev/null | wc -l)
emit "{\"ts\":\"$T\",\"participant\":\"stdiobus\",\"metric\":\"M1\",\"binary_bytes\":$b,\"dyn_deps\":$deps,\"src_commit\":\"$commit\",\"src\":\"github.com/stdiobus/stdiobus releases/v2.0.3/linux-amd64 (prebuilt)\"}"

# --- M2: покой (1 воркер) ---
cfg 1 "$WORK/one.json"
"$BIN" --config "$WORK/one.json" --unix "$WORK/one.sock" > "$WORK/one.log" 2>&1 &
P1=$!
sleep 3
a=$(rss "$P1"); sleep 1; b2=$(rss "$P1"); sleep 1; c=$(rss "$P1")
m2med=$(med3 "$a" "$b2" "$c")
kill -9 "$P1" 2>/dev/null
sleep 5
m2orph=$(workers)
emit "{\"ts\":\"$T\",\"participant\":\"stdiobus\",\"metric\":\"M2\",\"rss_kb_samples\":[$a,$b2,$c],\"rss_kb_median\":$m2med,\"agents\":1,\"orphans_after_kill9\":$m2orph}"

pkill -9 -f "while :" 2>/dev/null   # унести выжившего M2: у сверстника нет PDEATHSIG
sleep 1

# --- ферма 100 ---
cfg 100 "$WORK/cfg.json"
"$BIN" --config "$WORK/cfg.json" --unix "$WORK/bus.sock" > "$WORK/bus.log" 2>&1 &
P=$!
sleep 5
wfarm=$(workers)

# --- M3 ---
a=$(rss "$P"); sleep 1; b2=$(rss "$P"); sleep 1; c=$(rss "$P")
m3med=$(med3 "$a" "$b2" "$c")
emit "{\"ts\":\"$T\",\"participant\":\"stdiobus\",\"metric\":\"M3\",\"agents\":100,\"workers_seen\":$wfarm,\"rss_kb_samples\":[$a,$b2,$c],\"rss_kb_median\":$m3med}"

# --- M4: их stdout-журнал за 30 с ---
s1=$(wc -c < "$WORK/bus.log")
sleep 30
s2=$(wc -c < "$WORK/bus.log")
emit "{\"ts\":\"$T\",\"participant\":\"stdiobus\",\"metric\":\"M4\",\"window_sec\":30,\"journal_bytes_delta\":$((s2 - s1))}"

# --- M6: рестарт одного воркера ---
ws1=$(grep -c "Worker started" "$WORK/bus.log")
victim=$(pgrep -f "while :" | head -1)
kill -9 "$victim" 2>/dev/null
sleep 10
wfarm2=$(workers)
ws2=$(grep -c "Worker started" "$WORK/bus.log")
emit "{\"ts\":\"$T\",\"participant\":\"stdiobus\",\"metric\":\"M6\",\"workers_before\":$wfarm,\"workers_after\":$wfarm2,\"worker_started_before\":$ws1,\"worker_started_after\":$ws2}"

# --- M5: сироты ---
kill -9 "$P" 2>/dev/null
sleep 5
orph=$(workers)
emit "{\"ts\":\"$T\",\"participant\":\"stdiobus\",\"metric\":\"M5\",\"workers_before\":$wfarm,\"orphans_after_5s\":$orph}"

echo "stdiobus-bench: транскрипт $TR; сироты=$orph; воркеров после рестарта=$wfarm2"
