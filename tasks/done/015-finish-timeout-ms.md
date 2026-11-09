# Тикет 015 · finish-timeout-ms per-unit (Поправка №13)

> Виток 11 · открыт и исполнен 2026-11-10 (инициатива Хозяина, чат;
> дверь — `docs/SVERKA-VITOK6-PARALLEL.md`, предложение 1; ТЗ-10)

## Суть

Потолок жизни finish-хука стал per-unit ключом `finish-timeout-ms`.
До витка был жёсткий глобальный `FINISH_MS 5000` — свёртка двух
независимых реализаций витка 6 показала спор 2000 (вилка) против 5000
(main) и вердикт: канон — настройка per-unit при щедром дефолте, как у
s6 `timeout-finish` (файл в servicedir, дефолт 5000 мс — ровно наш
`FINISH_MS`).

## Договор

- Ключ: `finish-timeout-ms = <мс>` в `*.agent`; не задан или 0/минус —
  дефолт ядра `FINISH_MS` 5000. «Без лимита» не бывает: бесконечный хук
  нарушает Ст. 11 — объявлено в статье, README и ТЗ-10.
- Событие упора: `"finish"` с `"timeout":true,"ms":<потолок юнита>` —
  теперь видно, КАКИЙ потолок сработал.
- reload: изменение ключа = `changed`, применяется к живому юниту сразу.
- Ядро: парсинг (+4 строки), поле `finish_timeout_ms` в `unit_t`,
  `run_finish` берёт потолок юнита, reload сравнивает и применяет.

## Приёмка (факт, 2026-11-10)

- `make demo-finish`: sweeper (хук-эхо, ≥3 смертей → 3 хука, след
  `demo/finish-sweep.log`) + slowfin (хук `sleep 2`,
  `finish-timeout-ms = 600`): добит потолком **×4** за прогон, транскрипт
  `demo/finish-transcript.jsonl` — аудит `OK: 39 событий, 2 юнит(ов)`.
- Приёмка демо машиной: `FTO ≥ 2` по `"timeout":true,"ms":600`.
- Батарея целиком зелёная: demo, demo-ctl, demo-reload, demo-stream,
  demo-ready, demo-metrics, demo-rotate, demo-sign, demo-envelope,
  test-p37 (42/42), journal-audit, bridge-test — rc=0.
- Поправка №13 вписана в Ст. 11; Ст. 1 обновлена машиной
  (`tools/check_constitution.py` rc=0).

## Границы

Готовность хука к per-unit потолку не делает хук частью политики
перезапуска: сбой хука лестницу не трогает (Виток 6, неизменно).
