#!/bin/sh
# agent2unit — мост .agent → systemd .service (тикет 008, виток 7).
# Файл порождает файл (Ст. 13): ни одного вызова systemctl, ядро agryp
# не растёт ни на строку (Ст. 1). Эквивалентность не обещается —
# обещается честная таблица потерь: она в шапке каждого .service и в README.
#
# usage: agent2unit.sh <unit.agent> [> unit.service]
set -u
[ $# -eq 1 ] || { echo "usage: agent2unit.sh <unit.agent>" >&2; exit 2; }
[ -f "$1" ] || { echo "agent2unit: нет файла $1" >&2; exit 2; }
f=$1; stem=$(basename "$f" .agent)
dir=$(cd "$(dirname "$f")" && pwd)

# разбор как у ядра (parse_unit_file): полный комментарий — строка,
# начинающаяся с '#'; ключ=значение; пустое — мимо
k_name= k_exec= k_restart=always k_budget=0 k_cooldown=1000
k_maxatt=0 k_token=0 k_mem=0 k_finish= k_jail=
while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in *[![:space:]]*) ;; *) continue ;; esac
    case "$line" in '#'*) continue ;; esac
    key=${line%%=*}; val=${line#*=}
    key=$(printf '%s' "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    val=$(printf '%s' "$val" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    case "$key" in
        name)         k_name=$val ;;
        exec)         k_exec=$val ;;
        restart)      k_restart=$val ;;
        budget-sec)   k_budget=$val ;;
        cooldown-ms)  k_cooldown=$val ;;
        max-attempts) k_maxatt=$val ;;
        token-budget) k_token=$val ;;
        mem-max-mb)   k_mem=$val ;;
        finish)       k_finish=$val ;;
        jail)         k_jail=$val ;;
        *) echo "agent2unit: $f: неизвестный ключ '$key' — мимо моста" >&2 ;;
    esac
done < "$f"
[ -n "$k_exec" ] || { echo "agent2unit: $f: ключ exec не задан" >&2; exit 2; }

# RestartSec: 1000 мс → 1; 250 мс → 0.250 (systemd ест доли секунды)
sec=$((k_cooldown / 1000)); frac=$((k_cooldown % 1000))
rs=$sec; [ "$frac" -ne 0 ] && rs="$sec.$(printf '%03d' "$frac")"

rmax=infinity
[ "$k_budget" -gt 0 ] 2>/dev/null && rmax=$k_budget

{
    echo "# $stem.service — порождён tools/agent2unit.sh из $stem.agent (виток 7, тикет 008)."
    echo "# Файл порождает файл (Ст. 13): systemctl из agryp не зовётся — этим файлом"
    echo "# кормят УЖЕ ЖИВУЩИЙ systemd-супервизор (Ст. 5: не пере-делывать его)."
    echo "# ПОТЕРИ ПРИ ТРАНСЛЯЦИИ (честно, Ст. 11):"
    [ -n "$k_jail" ] && \
        echo "#  - jail = $k_jail — комнаты имён попытки не переносятся: это не контейнер"
    echo "#  - token-budget = $k_token — у systemd нет второй валюты бюджета;"
    echo "#    валюты страхуют друг друга только внутри agryp (Ст. 14)"
    echo "#  - max-attempts у systemd живёт в окне StartLimitIntervalSec, не за жизнь юнита"
    echo "#  - казнь по бюджету: у нас SIGKILL группы попытки, у systemd TERM → KILL сервиса"
    echo ""
    echo "[Unit]"
    echo "Description=agryp unit ${k_name:-$stem}"
    echo "StartLimitIntervalSec=0"
    echo ""
    echo "[Service]"
    echo "Type=simple"
    echo "WorkingDirectory=$dir"
    echo "ExecStart=/bin/sh -c '$k_exec'"
    echo "Restart=$k_restart"
    echo "RestartSec=$rs"
    echo "RuntimeMaxSec=$rmax"
    [ "$k_mem" -gt 0 ] 2>/dev/null && echo "MemoryMax=${k_mem}M"
    [ -n "$k_finish" ] && echo "ExecStopPost=/bin/sh -c '$k_finish'"
    echo "StartLimitBurst=$k_maxatt"
}
