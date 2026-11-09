# Волна CI: полная живая батарея + санитайзеры (2026-11-10, независимая сессия)

Аддитивное продолжение аудита 364c1f0. Две дыры покрытия закрыты, одна
настоящая находка UB — задокументирована.

## Что добавлено в ci.yml (block-стиль триггера не тронут)

1. **battery** — вся живая батарея, что гоняет рука: demo, demo-ctl,
   demo-finish, demo-reload, demo-stream, demo-envelope, journal-audit,
   bridge-test. Урок бага `--dir` (364c1f0): интерфейсный баг жил, потому
   что CI не гонял demo-ctl. Теперь CI гоняет всё.
2. **sanitizers** — ASan + UBSan на живой батарее ядра: `-O1 -g
   -fno-omit-frame-pointer -fsanitize=address,undefined
   -fsanitize-address-use-after-scope`; `ASAN_OPTIONS=detect_leaks=1:
   abort_on_error=1`, `UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1`.
   Санитайзеры — не «дебаг-помощь», а исполняемый контракт вокруг
   времени жизни, границ и инициализации (школа systemd/Fuchsia).

## Находка №2 (UB, не наша): vendored orlp/ed25519

Sanitizer-прогон вскрыл: `vendor/ed25519/ge.c:359:50: runtime error:
left shift of negative value -4` (ge_select) — классический UB сдвига
отрицательного значения, живёт в vendored verbatim-коде апстрима
(orlp/ed25519, zlib). Практически безобиден на gcc, но контракт UB
ломает: demo-envelope под санитайзерами красный, остальные таргеты —
зелёные. Verbatim-контракт vendor не позволяет чинить на месте —
фикс только апстримом; sanitizer-джоб исключает demo-envelope с
пометкой; строка в KNOWN_ISSUES.md. Сам факт — доказательство работы
контракта: санитайзер ловит UB даже в чужом верbatim-коде.

## Верификация на чистой машине (2026-11-10)

Sanitizer-прогон (halt_on_error, detect_leaks=1):

| Таргет | Вердикт |
|---|---|
| demo | 🟢 |
| demo-ctl | 🟢 |
| demo-finish | 🟢 |
| demo-reload | 🟢 |
| demo-stream | 🟢 |
| demo-metrics | 🟢 |
| demo-rotate | 🟢 |
| demo-sign | 🟢 |
| demo-envelope | 🔴 только vendor-UB (ge.c:359) — исключён из sanitizer-джоба |

Ядро (src/agryp.c, 1196 строк) под ASan+UBSan+LSan на живой батарее —
ноль находок: ни одного выхода за границы, ни одного утечки (ядро не
держит кучу — вся память статическая, fork+exec детей образ заменяет).

Сироты 0 во всех прогонах; сборка под санитайзерами — ноль
предупреждений.

## Правила волны

Мембранные файлы (README.md, AGENTS.md, llms.txt) не тронуты; force-push
не применялся; секретов нет; триггер ci.yml — block-стиль, история
«ain]» не заведена заново.
