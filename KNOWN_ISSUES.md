# KNOWN ISSUES · agryp

> Живой список известных красных и квирков. Append-only: новые записи дописываются секциями, старые не стираются.

## Волна ×5 · 2026-11-09

| Статус | Суть | Прогон/факт | Судьба |
|---|---|---|---|
| 🟢 закрыто | push-триггер ci.yml `branches: ain]` + 2 стартап-провала попыток правки | runs 42482290275 / 42482568329 (failure, 0 jobs, name = путь файла) | вылечено `d52abd3ab5` (block-стиль `- main`); dispatch ci 42526805179 🟢 (×5-C) |
| ⬜ квирк | логи тех красных истёрты retention-политикой: jobs API пуст, logs 404 | API-срез ×5-C 09.11 | диагноз по истории коммитов + локальное репро (gcc c11/c99, make audit/ctl/metrics/rotate/sign/catalog-guard — всё 🟢) |
| ⬜ todo | Виток 10: OpenMetrics-файл, ротация журнала с пломбой, сигнатуры юнитов — зрелый контракт | polimat-hub#24 (П-06) | за следующей волной; каркас (vitok-10 шаг + demo-мишени) уже зелёный |

## Квирки среды
- Раннеры: `rust toolchain предустановлен`, но для agryp не нужен — ноль зависимостей, только libc.
- При правке ci.yml из транзитного коммита GitHub пишет startup_failure с name = путём файла — не паниковать, это парсер, не код.

## Независимый аудит · 2026-11-10 (санитайзер-волна)

| Статус | Суть | Прогон/факт | Судьба |
|---|---|---|---|
| ⬜ квирк | vendored orlp/ed25519 (verbatim): UBSan «left shift of negative value -4» — `vendor/ed25519/ge.c:359` (ge_select) | sanitizer-прогон аудита: ядро чистое (8 демо 🟢), demo-envelope 🔴 только на vendor-UB | фикс только апстримом (verbatim-контракт); sanitizer-джоб CI исключает demo-envelope с пометкой; протокол — docs/audits/CI-BATTERY-SANITIZERS-2026-11-10.md |
| 🟢 закрыто | ядро под ASan+UBSan+LSan (halt_on_error) на живой батарее — ноль находок, куча не держится | sanitizer-прогон 2026-11-10: demo/ctl/finish/reload/stream/metrics/rotate/sign 🟢 | контракт закреплён CI-джобом `sanitizers` (ci.yml) |
| 🟢 закрыто | живая батарея не гонялась CI (demo-ctl был красным на чистой машине — баг `--dir` дожил до внешнего аудита 364c1f0) | CI-джоб `battery`: demo, ctl, finish, reload, stream, envelope, journal-audit, bridge-test | закрыто в этой же волне |
