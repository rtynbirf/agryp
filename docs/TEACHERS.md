# Учителя и сверстники: сверка со средой обитания

Дата: 2026-11-06. Метод: два фронта сравнения — «учителя» (классические
супервизоры и PID1, полвека практики) и «сверстники» (agent-runtime
2025–2026). Каждому чужому механизму — один вопрос: это универсальный
инвариант любого PID1 или особенность чужого слоя? Инвариант — берём,
особенность — отвергаем с причиной. Сингулярность — это умение сказать «нет».

Вердикты: **уже было** — инвариант стоял до сверки; **принято** — вошло
по Поправке №2 (2026-11-06) одним атомом с кодом и статьями конституции;
**отвергнуто** — не наш слой, с причиной.

## I. Учителя: классические супервизоры и PID1

| Учитель | Механизм | Урок | Вердикт |
|---|---|---|---|
| systemd | `Restart=` + `RestartSec` + `RestartSteps`/`RestartMaxDelaySec` (v254) — геометрическая лестница с насыщением | пауза рестарта — не константа, а лестница с потолком | **принято** (Ст. 8): `cooldown-ms` → удвоение до `BACKOFF_CAP_MS` |
| systemd | `StartLimitIntervalSec`/`StartLimitBurst` — предохранитель рестарт-шторма | поверх любой политики рестарта нужен fuse | **принято** (Ст. 8): `CRASH_LIMIT` → терминальный `failed` |
| supervisord | `startsecs` / `BACKOFF` / `FATAL` | фазы старт/работа, растущий backoff, терминальное состояние | **принято**: `SUSTAIN_MS` + `failed` |
| Kubernetes | CrashLoopBackOff: экспонента + сброс после устойчивой работы | лестница гаснет, если юнит доказал, что умеет работать | **принято**: `SUSTAIN_MS` |
| launchd | `ThrottleInterval` — глобальный троттлинг рестартов | рестарт без паузы — это шторм | покрыт лестницей Ст. 8 |
| s6 | анти-busyloop: «не стартовал» (пауза) ≠ «проработал и упал» (быстрый рестарт) | различать две смерти по прожитому времени | **принято**: `SUSTAIN_MS` |
| s6 | `./finish` + `timeout-finish` + exit 125 = перманентный фейл | хук очистки между смертью и рестартом | **принято** (Виток 6, Поправка №5): `finish = <строка sh>`, `FINISH_MS`, вне группы попытки |
| runit | три стадии, stage 2 перезапускается при крахе | супервизор супервизится | **отвергнуто**: один процесс, один файл (Ст. 1) |
| tini | жнец зомби `waitpid(-1)` + форвардинг сигналов | минимальный PID1 = сигнальная петля + жатва | **уже было** (Ст. 9: `reap()`, shutdown TERM группе) |
| tini / POSIX | `kill(-pgid)` по группе | дерево режем группой, а не одиночным pid | **уже было** (Ст. 9: `setpgid` + `kill(-pgid)`) |
| Linux | `PR_SET_CHILD_SUBREAPER`: сироты усыновляются subreaper'ом | вне PID1 объяви себя собирателем сирот | **принято** (Ст. 9): усыновление + `reap-orphan` вслух |
| tini `-p` | `PR_SET_PDEATHSIG`: ребёнок умирает с родителем | страховка от сирот даже при SIGKILL супервизора | **принято** (Ст. 9): в ребёнке, не встал — exit 125 вслух |
| systemd | `KillMode=cgroup`, TERM → `TimeoutStopSec` → KILL | двухфазный стоп по всей группе | **уже было** (Ст. 9: `GRACE_MS 3000`) |
| systemd | `WatchdogSec` (sd_notify `WATCHDOG=1`) | liveness по пингам | **отвергнуто**: зависшего ловит валюта времени (Ст. 7: `budget-sec`) |
| systemd | SIGHUP daemon-reload | конфиг перечитывается без смерти детей | **принято** (Виток 6, Поправка №7): каталог *.agent перечитывается по SIGHUP, дети живут |
| systemd | cgroups v2 delegation, правило одного писателя | клетка памяти в собственной ветке | **уже было** (Ст. 15) |

## II. Сверстники: agent-runtime 2025–2026

| Сверстник | Механизм | Урок | Вердикт |
|---|---|---|---|
| Claude Code | таймауты Bash-инструмента (`BASH_DEFAULT_TIMEOUT_MS` 120000 / `MAX` 600000) | таймаут — параметр инструмента | **уже было** (Ст. 7: бюджет попытки) |
| Claude Code | hooks (exit 2 = блок действия), фоновые задачи, «убить всё фоновое» | мягкие kill switch'и рядом с агентом | **отвергнуто**: PID1 не парсит намерения; наш kill switch — сигнал группе (Ст. 9) |
| Claude Code | sandbox Seatbelt/bubblewrap, egress-прокси с доменами | изоляция — отдельная ось | **отвергнуто**: соседний слой; у нас клетка памяти (Ст. 15) |
| OpenAI Codex | песочница × approval policy как конфиг (read-only/workspace-write; untrusted/on-failure/never) | пара «клетка × политика эскалации» | **отвергнуто**: изоляция ФС/сети — не процессный слой |
| OpenAI Agents SDK | guardrails с `tripwire_triggered` | дешёвый предохранитель до дорогого действия | **отвергнуто**: токен-фаза — слой выше процесса |
| MCP | lifecycle: handshake, cancellation («SHOULD, MAY игнорировать»), shutdown — на усмотрение транспорта | мягкая отмена без гарантий | подтверждает нишу: у нас смерть — сигнал ОС, гарант — ядро (Ст. 9) |
| LangGraph | checkpointer, durable execution, resume по `thread_id` | крах = возобновление состояния | **отвергнуто**: состояние агента — слой выше; мы возрождаем процесс |
| E2B / Modal | timeout / pause / snapshot / idle-kill с причинами смерти | время жизни среды — управляемый параметр | **уже было** (валюта времени, Ст. 7); pause/snapshot — не PID1 |
| OTel GenAI | семантические конвенции: agent/tool spans | журнал процессов должен быть машиночитаемым | **уже было** (Ст. 6: NDJSON-события); встраивание отвергнуто — ноль зависимостей (Ст. 2) |
| OpenHands | stuck detector: паттерны зацикливания → авто-halt | зависание — не только таймаут | **отвергнуто**: детекция паттернов требует понимать вывод; валюты Ст. 7 ловят то же тупо и честно |
| Letta | агент = персистентный сервис с БД, переживает рестарты | состояние живёт дольше процесса | **отвергнуто**: противоположный полюс — у нас процесс-первоклассник, состояние принадлежит агенту |

## III. Три дыры индустрии — три наши статьи

Отчёт по сверстникам сходится в трёх «делают плохо»:

1. **Нет единого kill switch'а** — MCP cancellation «MAY игнорировать»,
   у CLI свои Esc. Ответ: Ст. 9 — `kill(-pgid)` всей семьи, гарант — ядро.
2. **Нет сквозного run-бюджета** — лимиты пер-инструмент и пер-сандбокс.
   Ответ: Ст. 7 — бюджет попытки в двух валютах: время и токены.
3. **Аудит раздроблен** — hooks это скрипты без схемы. Ответ: Ст. 6 —
   один NDJSON-журнал процессных событий + аудитор, который сверяет
   счётчики с хронологией и каждую ступень лестницы с конфигом юнита.

## IV. Итог сверки

Принято по Поправке №2 (2026-11-06), одним атомом:

1. **Лестница перезапуска** — `cooldown-ms` база, удвоение до
   `BACKOFF_CAP_MS`, `SUSTAIN_MS` гасит, `CRASH_LIMIT` → терминальный
   `failed` (systemd + supervisord + Kubernetes + s6 + launchd — пять
   учителей, один вывод);
2. **Усыновление сирот** — `PR_SET_CHILD_SUBREAPER` + `reap-orphan` вслух;
3. **Страховка ребёнка** — `PR_SET_PDEATHSIG`, не встал — exit 125 вслух;
4. **Терминальное состояние** — `failed` вместо вечного цикла
   (supervisord `FATAL`, k8s CrashLoopBackOff).

Семь инвариантов сверка подтвердила как «уже было»: жнец зомби,
форвардинг сигналов, двухфазный стоп, группы процессов, клетка памяти,
журнал, бюджет. Остальное отвергнуто с причиной: сингулярность держится
на отказах не хуже, чем на принятиях.

## V. Живая сверка ниши (2026-11-07, GitHub API с токеном Хозяина)

Метод витка 4: не «что я помню», а живой поиск API — поисковые запросы +
README топов ниши (токен Хозяина, read-only, значение не печатается).
Итог: ниша больше не пуста — она **размечена слоями**. Клетку agryp
(PID1-ядро жизненного цикла) не занял никто.

### Сверстники уровня процессов

| Сверстник | ★ | Слой | Что даёт | Чего не даёт (клетка agryp) |
|---|---|---|---|---|
| qhkm/zeptopm | 6 | PM2 для LLM (Rust) | процесс на агента, рестарт с экспонентой, бюджеты токены/USD, hot reload | один файл C / ноль зависимостей; файл-как-API (у него HTTP); самоверифицирующийся журнал; конституция |
| stdiobus/stdiobus | 20 | C-демон-роутер | NDJSON JSON-RPC между клиентами и воркерами, session affinity, epoll/kqueue, libc-only | жизненный цикл: нет бюджетов, рестартов, сирот, аудита — роутер, не PID1 (agryp и stdiobus дополняют друг друга) |
| z80dev/lemon | 136 | агент-демон (Elixir/OTP) | supervised BEAM-процессы на run/tool-call, circuit breaker, cron, judge | требует BEAM-рантайм; не один файл; не PID1 для произвольных `sh -c` агентов |
| elchemista/spectre | 13 | OTP-библиотека (Elixir) | supervision-деревья для conversation/tool-процессов | библиотека слоя приложения, не ОС-надзор |

### Сверстники уровней выше (рантаймы и приложения)

| Сверстник | ★ | Слой | Урок | Вердикт |
|---|---|---|---|---|
| paperclipai/paperclip | 111677 | «компания для агентов» (Node/React) | бюджеты и governance на уровне организации | не процессный слой; подтверждает спрос |
| herdrdev/herdr | 48487 | терминальный мультиплексор агентов (Rust) | panes working/blocked/idle — статус рядом с агентом | «original processes do not survive» — не PID1 |
| tinyhumansai/openhuman | 42567 | harness (Rust) | 500 агентов на $10 VPS — экономика плотности | harness, не супервизор |
| OrchestratorInc/agent-orchestrator | 14172 | fleet-менеджер (worktree на задачу) | CI-конвейер обратно в воркера | приложение, не процессный слой |

### Что следует для Ст. 5 (Поправка №3)

1. Процессный слой для агентов возник в 2026 — вопрос больше не «кто первый»,
   а «кто даёт гарантии ядра».
2. Сингулярность agryp — пять свойств, которых нет ни у одного сверстника:
   один файл C; ноль зависимостей; файл-как-API (статус/отчёт/ctl — файлы,
   не сокеты); самоверифицирующийся NDJSON-журнал (аудитор сверяет счётчики
   и каждую ступень лестницы); гарантии уровня ядра (группа попытки,
   subreaper, PDEATHSIG, клетка cgroup).
3. Бюджеты (Ст. 7/14) — не уникальны (zeptopm ведёт токены/USD): наша валюта
   — контракт юнита, согласование двух валют и казнь всей группы, а не факт бюджета.

### Числа живого поиска (срез 2026-11-07)

- `"agent supervisor process"` → 135 репо; `topic:agent-orchestration` → 4894;
  `"ai agent orchestrator process manager"` → 6; `"llm agent supervisor restart"`
  → 1; `"agent process group supervisor"` → 2.
- Учителя живы: systemd ★17003 (push 2026-11-06), s6 ★991, s6-rc ★166,
  tini ★11290 (последний push 2025-05 — уснул). supervisord живёт на
  `Supervisor/supervisor`; runit — вне GitHub (smarden.org).

## Источники

Учителя:

- systemd.service(5): https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
- systemd(1): https://www.freedesktop.org/software/systemd/man/latest/systemd.html
- s6-supervise: https://skarnet.org/software/s6/s6-supervise.html
- runit(8): http://smarden.org/runit/runit.8.html
- tini: https://github.com/krallin/tini
- supervisord: http://supervisord.org/configuration.html
- k8s pod lifecycle: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
- launchd: https://www.launchd.info/
- waitpid(2): https://man7.org/linux/man-pages/man2/waitpid.2.html
- prctl(2): https://man7.org/linux/man-pages/man2/prctl.2.html
- kill(2): https://man7.org/linux/man-pages/man2/kill.2.html
- setpgid(2): https://man7.org/linux/man-pages/man2/setpgid.2.html

Сверстники:

- Claude Code hooks: https://code.claude.com/docs/en/hooks
- Claude Code sandboxing: https://code.claude.com/docs/en/sandboxing
- Claude Code env-vars: https://code.claude.com/docs/en/env-vars
- Codex sandbox: https://github.com/openai/codex/blob/main/docs/sandbox.md
- OpenAI Agents SDK guardrails: https://openai.github.io/openai-agents-python/guardrails/
- MCP lifecycle: https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle
- MCP cancellation: https://modelcontextprotocol.io/specification/2025-06-18/basic/utilities/cancellation
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- E2B sandbox timeout: https://docs.e2b.dev/api-reference/sandboxes/set-sandbox-timeout
- Modal sandbox: https://modal.com/docs/guide/sandbox
- OTel GenAI: https://github.com/open-telemetry/semantic-conventions-genai
- OpenHands stuck detector: https://docs.openhands.dev/sdk/guides/agent-stuck-detector
- Letta stateful agents: https://docs.letta.com/concepts/stateful-agents

Сверстники §V (живая сверка 2026-11-07, GitHub API):

- zeptopm: https://github.com/qhkm/zeptopm
- stdiobus: https://github.com/stdiobus/stdiobus
- lemon: https://github.com/z80dev/lemon
- spectre: https://github.com/elchemista/spectre
- paperclip: https://github.com/paperclipai/paperclip
- herdr: https://github.com/herdrdev/herdr
- openhuman: https://github.com/tinyhumansai/openhuman
- agent-orchestrator: https://github.com/OrchestratorInc/agent-orchestrator
- supervisor (учитель, верное место на GitHub): https://github.com/Supervisor/supervisor
