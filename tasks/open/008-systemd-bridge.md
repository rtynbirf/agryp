# Тикет 008 · Мост `.agent` ↔ systemd unit

Роль: ДОКТОР + ЯДРО-ревизор (контракт — AGENTS.md §3). Статус: open. Виток: 7.
Приоритет: низкий. Зависит от: тикет 004 (ключ `finish` уже в формате).

## Задача

У половины машин Хозяев уже стоит systemd. Мост — не интеграция (Ст. 4
запрещает зависимости), а двусторонняя трансляция форматов утилитой
`agryp-convert` (POSIX sh, ноль зависимостей):

- `.agent` → unit: `exec` → `ExecStart=/bin/sh -c '…'`;
  `restart = always` → `Restart=always`; `budget-sec` →
  `TimeoutStartSec`+watchdog-примечание; `finish` → `ExecStopPost=`;
  `mem-max-mb` → `MemoryMax=`; `cooldown-ms` → `RestartSec`;
  `token-budget` → комментарий-примечание (у systemd валюты токенов нет);
- unit → `.agent`: обратная трансляция с loud-предупреждением на каждый
  потерянный ключ (ничего не молчит — Ст. 6 тем же принципом);
- тест: Round-trip на демо-юнитах — `convert convert convert` возвращает
  исходные ключи, потери перечислены вслух.

## Граница

- Не генерируем и не ставим юниты в систему — только текст в stdout.
- Потолок Ст. 1 не трогается: утилита живёт отдельно (`agryp-convert`),
  размер и проверки объявляет своей секцией в README.

## Приёмки

1. `agryp-convert examples/hello.agent` → валидный unit-текст
   (`systemd-analyze verify` — где доступен).
2. Round-trip: ключи теряются только те, у которых нет аналога, и каждая
   потеря напечатана.
3. `wc -l agryp-convert` → объявлено в README; файл — POSIX sh.
