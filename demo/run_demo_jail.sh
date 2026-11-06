#!/usr/bin/env bash
# Демо витка 7, тикет 007: клетка имён (jail = pid,mount).
# В песочнице clone(CLONE_NEWPID) даёт EPERM → loud jail-skip с errno,
# ровно один, и юнит живёт дальше без клетки (работа не молчит).
# Контрольный юнит без jail не знает о клетке ничего. Сироты — 0.
set -u
cd "$(dirname "$0")/.."
make -s agryp || exit 1

# зачистка стреев (урок ТЗ-6: зомби-супервизор врёт дважды)
pkill -f 'agryp --dir demo/jail-units' 2>/dev/null && sleep 0.3
rm -f demo/jail-units/.agryp-status demo/jail-units/.agryp-report
rm -f demo/jail-units/.agryp-ctl/*.down 2>/dev/null
rm -f demo/jail-transcript.jsonl demo/jail-status-snapshot.jsonl

./agryp --dir demo/jail-units > demo/jail-transcript.jsonl 2>&1 &
SUP=$!
sleep 3
./agryp status --dir demo/jail-units > demo/jail-status-snapshot.jsonl
kill -TERM "$SUP" 2>/dev/null
wait "$SUP" 2>/dev/null
sleep 1

[ -f demo/jail-units/.agryp-status ] && {
    echo ">> ДЕМО ПРОВАЛЕНО: файл статуса пережил супервизора (Ст. 13)"; exit 1; }

TR=demo/jail-transcript.jsonl
SKIPS=$(grep -ac '"event":"jail-skip"' "$TR")
JAILED=$(grep -ac '"event":"spawn".*"jailed":[1-3]' "$TR")
FAIL=0

if [ "$SKIPS" -gt 0 ]; then
    # песочница: клетку не дали — должна быть ровно одна громкая правда
    [ "$SKIPS" -eq 1 ] || { echo ">> ПРОВАЛЕНО: jail-skip $SKIPS раз, а громкость — один раз"; FAIL=1; }
    grep -aq '"unit":"jailed".*"event":"spawn"' "$TR" \
        || { echo ">> ПРОВАЛЕНО: после jail-skip спавна нет — работа не продолжилась"; FAIL=1; }
    echo ">> демо: среда без CAP_SYS_ADMIN — jail-skip (EPERM) вслух, работа дальше"
elif [ "$JAILED" -gt 0 ]; then
    echo ">> демо: клетка встала — spawn с jailed:3 (рождение в комнатах имён)"
else
    echo ">> ДЕМО ПРОВАЛЕНО: ни jail-skip, ни jailed — молчаливая усечка (Ст. 6)"; FAIL=1
fi

grep -aq '"unit":"plain".*"event":"jail-skip"' "$TR" && {
    echo ">> ДЕМО ПРОВАЛЕНО: контрольный юнит без jail получил клеточное событие"; FAIL=1; }
grep -aq '"jail":' demo/jail-status-snapshot.jsonl \
    || { echo ">> ПРОВАЛЕНО: в статус-срезе нет поля jail"; FAIL=1; }

ORPHANS=$(pgrep -f 'jail_worker' | wc -l)
[ "$ORPHANS" -eq 0 ] || { echo ">> ПРОВАЛЕНО: сирот $ORPHANS (Ст. 9)"; FAIL=1; }

python3 demo/audit_transcript.py "$TR" || FAIL=1

[ "$FAIL" -eq 0 ] \
    && echo ">> демо-jail завершено: клеточная правда одна, юниты живы, сирот 0" \
    || exit 1
