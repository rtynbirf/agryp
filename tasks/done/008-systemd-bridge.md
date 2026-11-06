# Тикет 008 · Мост `.agent` ↔ systemd unit: файл порождает файл

Роль: ДОКТОР + ЯДРО (контракт — AGENTS.md §3). Статус: done (отчёт ниже). Виток: 7.
ЦУ Хозяина (Виток 6): у фермы с systemd уже есть супервизор — не
пере-делывать его (Ст. 5), а разговаривать с ним на его языке.

## Задача

Школа systemd, встреченная гостеприимно:

- скрипт-транслятор (POSIX sh, рядом с `agrypctl`): `*.agent` →
  `*.service` (Restart=, RestartSec=, MemoryMax=, TimeoutStopSec=,
  ExecStart= из `sh -c`) и обратно — `*.service` → `*.agent`;
- трансляция — файл порождает файл (Ст. 13), никаких вызовов
  systemctl из ядра; ядро agryp не меняется вообще;
- соответствие ключей задокументировано таблицей в README (что
  теряется: token-budget — у systemd нет второй валюты — честно
  пометить в шапке сгенерированного файла);
- тест: трансляция examples/*.agent туда-обратно — семантика
  restart/budget/cooldown сохраняется.

## Граница

- Потолок Ст. 1 не трогается (ядро не растёт ни на строку).
- Не обещаем эквивалентность — обещаем честную таблицу потерь.

## Приёмки

1. `bash tools/agent2unit.sh examples/hello.agent` → валидный
   `hello.service` (проверка `systemd-analyze verify`, если доступен).
2. Обратная трансляция → юнит, эквивалентный по restart/бюджету.
3. Таблица потерь в README; тест туда-обратно зелёный.

---

## Отчёт о исполнении (Виток 7, 2026-11-07 — исполнено автором лично)

Статус: **done**. Ядро agryp не менялось ни на строку (Ст. 1 не тронута
этим тикетом) — мост живёт в `tools/`:

- `tools/agent2unit.sh` (POSIX sh): `*.agent` → `*.service` —
  `ExecStart=/bin/sh -c '...'`, `Restart=`, `RestartSec=` (мс), 
  `RuntimeMaxSec=`/`infinity`, `MemoryMax=`, `ExecStopPost=`,
  `StartLimitBurst=` + `StartLimitIntervalSec=0`, `WorkingDirectory=`
  (каталог .agent); шапка честных потерь в каждом файле.
- `tools/unit2agent.sh`: обратная трансляция с разбором долей секунды;
  token-budget и jail невозвратимы — сказано в шапке (Ст. 6).
- Таблица соответствия и потерь — README (раздел «Виток 7»).
- Доказательства: `make bridge-test` — туда-обратно по всем
  examples/*.agent: семантика restart/budget/cooldown/mem/max-attempts
  сохранена, потери названы; `systemd-analyze verify` (доступен) —
  rc 0 на каждом .service.
- Слепая зона: exec с одинарными кавычками сломает обёртку — в
  examples таких нет; проверка вслух при разборе.
