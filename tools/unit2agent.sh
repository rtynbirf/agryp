#!/bin/sh
# unit2agent — обратный мост .service → .agent (тикет 008, виток 7).
# Читает systemd-юнит, отдаёт договор agryp. Потери невозвратимы:
# token-budget и jail в .service не живут — их нет и здесь; в шапке
# это сказано вслух (Ст. 6: ничего не происходит молча).
#
# usage: unit2agent.sh <unit.service> [> unit.agent]
set -u
[ $# -eq 1 ] || { echo "usage: unit2agent.sh <unit.service>" >&2; exit 2; }
[ -f "$1" ] || { echo "unit2agent: нет файла $1" >&2; exit 2; }
f=$1; stem=$(basename "$f" .service)

k_name= k_exec= k_restart=always k_budget=0 k_cooldown=1000
k_maxatt=0 k_mem=0 k_finish=
while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in *[![:space:]]*) ;; *) continue ;; esac
    case "$line" in '#'*) continue ;; esac
    case "$line" in \[*\]) continue ;; esac          # секции [Unit]/[Service]
    key=${line%%=*}; val=${line#*=}
    key=$(printf '%s' "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    val=$(printf '%s' "$val" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    case "$key" in
        Description)
            case "$val" in
                "agryp unit "*) k_name=${val#"agryp unit "} ;;
            esac ;;
        ExecStart|ExecStopPost)
            # снимаем обёртку /bin/sh -c '...'
            case "$val" in
                "/bin/sh -c '"*) v=${val#"/bin/sh -c '"}
                                v=${v%"'"}
                                [ "$key" = ExecStart ] && k_exec=$v || k_finish=$v ;;
                *) echo "unit2agent: $f: $key без обёртки /bin/sh -c — мимо моста" >&2 ;;
            esac ;;
        Restart)       k_restart=$val ;;
        RestartSec)
            int=${val%%.*}; frac=
            case "$val" in *.*) frac=${val#*.} ;; esac
            fms=0
            case ${#frac} in
                3) fms=$((10#$frac)) ;;
                2) fms=$((10#$frac * 10)) ;;
                1) fms=$((10#$frac * 100)) ;;
            esac
            k_cooldown=$((int * 1000 + fms)) ;;
        RuntimeMaxSec)
            [ "$val" != infinity ] && k_budget=$val ;;
        MemoryMax)
            case "$val" in
                *M) k_mem=${val%M} ;;
                *)  echo "unit2agent: $f: MemoryMax без M ('$val') — мимо моста" >&2 ;;
            esac ;;
        StartLimitBurst) k_maxatt=$val ;;
    esac
done < "$f"
[ -n "$k_exec" ] || { echo "unit2agent: $f: ExecStart без обёртки /bin/sh -c" >&2; exit 2; }

{
    echo "# $stem.agent — порождён tools/unit2agent.sh из $stem.service (виток 7, тикет 008)."
    echo "# Невозвратимые потери: token-budget (у systemd нет второй валюты) и"
    echo "# jail (комнаты имён в .service не живут) — см. таблицу потерь в README."
    [ -n "$k_name" ] && echo "name         = $k_name"
    echo "exec         = $k_exec"
    echo "restart      = $k_restart"
    echo "budget-sec   = $k_budget"
    echo "cooldown-ms  = $k_cooldown"
    echo "max-attempts = $k_maxatt"
    [ "$k_mem" -gt 0 ] 2>/dev/null && echo "mem-max-mb   = $k_mem"
    [ -n "$k_finish" ] && echo "finish       = $k_finish"
    true   # статус блока не должен наследовать условное echo (пустой finish — не ошибка)
}
