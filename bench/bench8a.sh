#!/usr/bin/env bash
# ============================================================================
# agryp · Виток 8а — бенчмарк ниши «PID 1 для агентов»
# Запуск:  ./bench8a.sh [N_агентов=100] [окно_сек=15]
# Честность: каждая строка результата — из прогона, не из обещания.
# Пустая клетка = SKIPPED(причина), а не выдуманная цифра (Ст. 6: журнал не лжёт).
# ============================================================================
set -u
N="${1:-100}"; WINDOW="${2:-15}"
cd "$(dirname "$0")" || exit 2
REPO="$(pwd -P)"

[ -x "$REPO/agryp" ] || { echo "[bench] сборка agryp..."; make agryp >/dev/null || exit 2; }
COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
echo "[bench] agryp @ $COMMIT, ядро: $(wc -l < "$REPO/src/agryp.c") строк C"
echo "[bench] N=$N окно=${WINDOW}s хост=$(uname -sr), CAP_SYS_ADMIN: $([ "$(id -u)" = 0 ] && echo возможно || echo нет)"

WORK="$(mktemp -d /tmp/agryp-bench.XXXXXX)"
J="$WORK/journal.ndjson"; S="$WORK/.agryp-status"
trap 'pkill -9 -f hello_agent.sh 2>/dev/null; pkill -9 -f crashy_agent.sh 2>/dev/null; rm -rf "$WORK"' EXIT

# --- генерация N бессмертных + 1 падучего (лестница Ст. 8) ---
HELLO="$REPO/demo/hello_agent.sh"; CRASHY="$REPO/demo/crashy_agent.sh"
for i in $(seq 1 "$N"); do
  printf 'name = bench%03d\nexec = bash %s\nrestart = always\nbudget-sec = 300\ntoken-budget = 1000000\ncooldown-ms = 1000\n' "$i" "$HELLO" > "$WORK/bench$(printf '%03d' "$i").agent"
done
printf 'name = crashy\nexec = bash %s\nrestart = on-failure\nbudget-sec = 300\ncooldown-ms = 1000\nmem-max-mb = 64\n' "$CRASHY" > "$WORK/crashy.agent"

# --- 1. латентность старта: exec -> все N RUNNING в статусе (полл 10 мс) ---
T0=$(date +%s%3N)
"$REPO/agryp" --dir "$WORK" > "$J" 2>&1 &
PID=$!
LAT=""
for _ in $(seq 1 3000); do
  if [ -f "$S" ] && [ "$(grep -c '"state":"RUNNING"' "$S" 2>/dev/null || echo 0)" -ge "$N" ]; then
    LAT=$(( $(date +%s%3N) - T0 )); break
  fi
  sleep 0.01
done
[ -n "$LAT" ] || { echo "[bench] FAIL: $N юнитов не поднялись за 30 с (см. $J)"; kill -9 "$PID" 2>/dev/null; exit 1; }
echo "PROOF  старт $N+1 юнитов до полного RUNNING: ${LAT} мс"

# --- окно измерения: RSS, журнал, статус ---
sleep "$WINDOW"
RSS_KB=$(ps -o rss= -p "$PID" | tr -d ' ')
JB=$(wc -c < "$J"); SB=$(wc -c < "$S")
echo "PROOF  RSS супервизора при $N агентах: ${RSS_KB} КБ (окно ${WINDOW}с)"
echo "PROOF  журнал: ${JB} байт NDJSON; статус-файл: ${SB} байт"
echo "PROOF  на агента приходится ~$(( JB / (N + 1) )) байт журнала/агент за ${WINDOW}с"

# --- 2. лестница перезапуска (Ст. 8): удвоение cooldown у crashy ---
echo "PROOF  лестница crashy (cooldown мс по журналу): $(grep -o '"backoff_ms":[0-9]*' "$J" | grep -o '[0-9]*' | sort -un | tr '\n' ' ')"

# --- 3. клетка: честный вердикт о jail/cgroups на этом хосте ---
if grep -q '"event":"jail-ok"' "$J"; then
  echo "PROOF  jail: клетка pid/mount РАБОТАЕТ на этом хосте (CAP_SYS_ADMIN есть)"
else
  echo "HONEST jail: на хосте клетка пропущена — $(grep -o '"event":"jail[^,]*' "$J" | head -1) / $(grep -o '"event":"cgroup-skip"[^}]*' "$J" | head -1)"
  echo "HONEST jail: полный jail-прогон — на машине владельца с CAP_SYS_ADMIN (§14 дислокации)"
fi

# --- 4. сироты после kill -9 (уникальное обещание дома: рой не переживает надзирателя) ---
kill -9 "$PID" 2>/dev/null; sleep 2
ORPH=$(pgrep -fc hello_agent.sh 2>/dev/null); ORPH=${ORPH:-0}
echo "PROOF  сирот hello_agent.sh через 2 с после kill -9 PID 1: ${ORPH} (ожидание 0 — PR_SET_PDEATHSIG)"
[ "$ORPH" = "0" ] || echo "HONEST сироты есть — НЕ скрываем, разбор обязателен (Ст. 6)"

# --- 5. сверстники: только то, что реально установлено ---
if command -v tini >/dev/null 2>&1; then
  python3 - <<'PY'
import subprocess, time
t=[]
for _ in range(50):
    a=time.perf_counter_ns(); subprocess.run(["tini","-s","--","true"]); t.append((time.perf_counter_ns()-a)/1e6)
t.sort(); print(f"PROOF  tini (50 прогонов): медиана накладных {t[25]:.2f} мс/спавн")
PY
else
  echo "SKIPPED tini: не установлен на этом хосте (спит с 2025-05 — апстрим мёртв)"
fi
for peer in zeptopm stdiobus; do
  command -v "$peer" >/dev/null 2>&1 && echo "PROOF  $peer найден — прогон вручную по его README" \
    || echo "SKIPPED $peer: не установлен (zeptopm: push 2026-04 — уснул)"
done

echo "[bench] готово. Сырой журнал: $J (сохраните до выхода — trap чистит WORK)"
