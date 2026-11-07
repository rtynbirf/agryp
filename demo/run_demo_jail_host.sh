#!/usr/bin/env bash
# Демо витка 9, ЦУ 011: jail-приёмка границы Ст. 9 — сироты 0 за клеткой.
# Граница (M7, виток 8): PDEATHSIG — один уровень; агент, породивший
# собственных детей, оставляет их сиротами при kill -9 супервизора.
# Дом-ответ (виток 7): jail = pid — ребёнок супервизора есть PID 1
# pid-комнаты, смерть init комнаты убивает комнату целиком (pid_namespaces(7)).
#
# Среда честно названа в транскрипте (Ст. 6): прямая клетка на хосте —
# EPERM (нет CAP_SYS_ADMIN); обёртка unshare --user --map-root-user --pid
# даёт супервизору CAP_SYS_ADMIN в собственной user-комнате, и
# clone(CLONE_NEWPID) внутри agryp проходит без единой правки ядра —
# agryp user-ns не трогает (решение витка 7), его трогает среда.
#
# Контроль границы: тот же прогон без клетки → сироты 20 (по юниту).
# Итог: kill -9 супервизора → сироты 0 за клеткой, хост чист.
set -u
cd "$(dirname "$0")/.."
make -s agryp || exit 1

WORK=/tmp/agryp-011-host
TR=demo/jail-host-transcript.jsonl
NOW() { date -u +%Y-%m-%dT%H:%M:%SZ; }
emit() { printf '{"ts":"%s",%s}\n' "$(NOW)" "$1" >> "$TR"; }

pkill -f 'agryp --dir' 2>/dev/null && sleep 0.3
pkill -9 -f 'while :' 2>/dev/null && sleep 0.3
rm -rf "$WORK"; mkdir -p "$WORK/control/units" "$WORK/jail/units"
rm -f "$TR"

mkunits() { # $1 = каталог, $2 = префикс имён, $3 = доп. строка юнита ("" | "jail = pid")
    i=1
    while [ "$i" -le 20 ]; do
        n=$(printf '%s%02d' "$2" "$i")
        printf 'name = %s\nexec = /bin/sh -c '"'"'while :; do sleep 1; done'"'"'\nrestart = always\n%s\n' \
            "$n" "$3" > "$1/$n.agent"
        i=$((i + 1))
    done
}

# --- проба среды (вслух, Ст. 6) ---
if unshare --pid --fork --mount-proc true 2>/dev/null; then HOST_PIDNS="ok"; else HOST_PIDNS="EPERM"; fi
if unshare --user --map-root-user --pid --fork true 2>/dev/null; then WRAP_PIDNS="ok"; else WRAP_PIDNS="EPERM"; fi
emit "\"event\":\"host-probe\",\"pidns_plain\":\"$HOST_PIDNS\",\"userns_wrapper\":\"$WRAP_PIDNS\",\"note\":\"ядро agryp не менялось: user-ns открывает среда, agryp входит только в свои pid/mount-комнаты (виток 7)\""
[ "$WRAP_PIDNS" = "ok" ] || { echo ">> ПРОВАЛЕНО: среда лишилась userns — приёмка невозможна (Ст. 6: названо вслух)"; exit 1; }

FAIL=0

# ================= КОНТРОЛЬ ГРАНИЦЫ: без клетки =================
mkunits "$WORK/control/units" c ""
./agryp --dir "$WORK/control/units" > "$WORK/control/sup.log" 2>&1 &
P=$!
sleep 3
CB=$(pgrep -c -f 'while :' || true)
kill -9 "$P" 2>/dev/null
sleep 5
CA=$(pgrep -c -f 'while :' || true)
emit "\"event\":\"arm-control\",\"units\":20,\"jail\":\"none\",\"procs_before_kill\":$CB,\"orphans_after_5s\":$CA,\"expect\":\"20: PDEATHSIG — один уровень, внутренние sh переживают супервизора (граница Ст. 9 живьём)\""
cat "$WORK/control/sup.log" >> "$TR"
pkill -9 -f 'while :' 2>/dev/null; sleep 1
[ "$CA" -eq 20 ] || { echo ">> контроль границы изменился: сирот $CA (ожидалось 20) — Ст. 6: названо вслух"; FAIL=1; }

# ================= ЛЕЧЕНИЕ: jail = pid в userns-обёртке =================
mkunits "$WORK/jail/units" j "jail = pid"
unshare --user --map-root-user --pid --fork /bin/sh -c '
    cd "'"$PWD"'"
    exec ./agryp --dir "'"$WORK"'/jail/units"
' > "$WORK/jail/sup.log" 2>&1 &
sleep 3
JP=$(pgrep -f 'agryp --dir /tmp/agryp-011-host/jail/units' | head -1)
[ -n "$JP" ] || { echo ">> ПРОВАЛЕНО: супервизор в обёртке не поднялся"; cat "$WORK/jail/sup.log"; exit 1; }
JB=$(pgrep -c -f 'while :' || true)
kill -9 "$JP" 2>/dev/null
sleep 5
JA=$(pgrep -c -f 'while :' || true)
JAILED=$(grep -ac '"event":"spawn".*"jailed":1' "$WORK/jail/sup.log")
JSKIP=$(grep -ac '"event":"jail-skip"' "$WORK/jail/sup.log")
emit "\"event\":\"arm-jail\",\"units\":20,\"jail\":\"pid\",\"wrapper\":\"unshare --user --map-root-user --pid --fork\",\"procs_before_kill\":$JB,\"orphans_after_5s\":$JA,\"jailed_spawns\":$JAILED,\"jail_skips\":$JSKIP,\"expect\":\"0: смерть init комнаты убивает комнату (pid_namespaces(7))\""
cat "$WORK/jail/sup.log" >> "$TR"
[ "$JAILED" -eq 20 ] || { echo ">> ПРОВАЛЕНО: спавнов с jailed:1 — $JAILED из 20"; FAIL=1; }
[ "$JSKIP" -eq 0 ] || { echo ">> ПРОВАЛЕНО: jail-skip в лечении — $JSKIP (клетка молча не встала — Ст. 6)"; FAIL=1; }
[ "$JA" -eq 0 ] || { echo ">> ПРОВАЛЕНО: сирот за клеткой $JA (обещание: 0)"; FAIL=1; }

pkill -9 -f 'while :' 2>/dev/null; sleep 1
HL=$(pgrep -c -f 'while :' || true)
emit "\"event\":\"verdict\",\"control_orphans\":$CA,\"jail_orphans\":$JA,\"host_leftover\":$HL"
[ "$HL" -eq 0 ] || { echo ">> ПРОВАЛЕНО: на хосте остались процессы — $HL"; FAIL=1; }

python3 demo/audit_jail_host.py "$TR" || FAIL=1

[ "$FAIL" -eq 0 ] \
    && echo ">> jail-host: граница Ст. 9 воспроизведена (20/20), клетка закрыла её (0/20), хост чист" \
    || exit 1
