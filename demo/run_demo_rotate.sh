#!/usr/bin/env bash
# Живое демо Витка 10 — журнал-ротация с пломбой (тикет 012, Ст. 11):
#   t=0    boot: crashy (падучий — события сыплются), --rotate-bytes 512
#   t≈5    журнал отротирован много раз; хвосты .1/.2/.3 запечатаны
#   audit  tools/journal_audit.sh: цепь печатей цела (rc=0)
#   audit- negative: подделка середины .2 ловится с точным приговором
set -u
cd "$(dirname "$0")/.."

pkill -9 -f "agryp --dir demo/rotate-units" 2>/dev/null
sleep 0.3

make -s agryp || exit 1
rm -rf demo/rotate-units
mkdir -p demo/rotate-units
# Тикающие агенты: живут секунду, выходят чисто, рестарт (события каждые ~1.1с).
# Их двое — журнал растёт быстро, fuse Ст. 8 не срабатывает (выходы чистые).
for u in tick1 tick2; do
cat > demo/rotate-units/$u.agent <<EOF
name        = $u
exec        = sleep 1
restart     = always
cooldown-ms = 1000
EOF
done
cp examples/crashy.agent demo/rotate-units/crashy.agent
# маленький потолок лестницы не важен: ротация по байтам, не по времени

./agryp --dir demo/rotate-units --rotate-bytes 384 > demo/rotate-transcript.jsonl 2>&1 &
SUP=$!
sleep 6
kill -TERM "$SUP" 2>/dev/null
wait "$SUP" 2>/dev/null
sleep 0.5

J=demo/rotate-units/.agryp-journal.ndjson
[ -f "$J" ] || { echo ">> ДЕМО ПРОВАЛЕНО: журнала нет"; exit 1; }
N_ROT=$(grep -ac '"event":"rotate"' demo/rotate-transcript.jsonl)
[ "$N_ROT" -ge 5 ] \
    || { echo ">> ДЕМО ПРОВАЛЕНО: ротаций всего $N_ROT (жду ≥5 при --rotate-bytes 384)"; exit 1; }
echo ">> демо: ротаций $N_ROT — хвосты отрезаны, печати выставлены"

# Печать в НОВОМ журнале — первая строка после каждой ротации
for f in "$J.1" "$J.2" "$J.3"; do
    [ -f "$f" ] || { echo ">> ДЕМО ПРОВАЛЕНО: $f не существует"; exit 1; }
done
echo ">> демо: хвосты .1/.2/.3 на месте (ROTATE_KEEP=3)"

# Приёмка 1: аудитор цепи печатей — цела
sh tools/journal_audit.sh demo/rotate-units || exit 1

# Приёмка 2: негативная — подделка СЕРЕДИНЫ хвоста ловится с приговором
rm -rf /tmp/agryp-rotate-tamper
cp -r demo/rotate-units /tmp/agryp-rotate-tamper
SZ=$(stat -c %s /tmp/agryp-rotate-tamper/.agryp-journal.ndjson.2)
OFF=$((SZ / 2))
printf 'X' | dd of=/tmp/agryp-rotate-tamper/.agryp-journal.ndjson.2 bs=1 seek=$OFF conv=notrunc status=none
if sh tools/journal_audit.sh /tmp/agryp-rotate-tamper 2>/dev/null; then
    echo ">> ДЕМО ПРОВАЛЕНО: подделка середины хвоста НЕ поймана — аудитор лжёт"
    exit 1
fi
sh tools/journal_audit.sh /tmp/agryp-rotate-tamper 2>&1 | grep -aq 'ПОДДЕЛКА' \
    || { echo ">> ДЕМО ПРОВАЛЕНО: приговор не точный (нет слова ПОДДЕЛКА)"; exit 1; }
echo ">> демо: подделка середины .2 поймана — точный приговор, журнал не лжёт"

python3 demo/audit_transcript.py demo/rotate-transcript.jsonl || exit 1
echo ">> демо Витка 10 (ротация) завершено: $N_ROT ротаций, цепь цела, транскрипт demo/rotate-transcript.jsonl"
