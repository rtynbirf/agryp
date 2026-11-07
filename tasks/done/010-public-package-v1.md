# ЦУ 010 · GitHub-пакет v1.0: push витка 8 и перевод репо в public

Роль: ДОКТОР (контракт — AGENTS.md §3). Статус: done (отчёт ниже).
Виток: 9. Исполнено автором лично (мандат Хозяина «делай сам»);
триггер — свежий токен Хозяина (2026-11-07, старый отозван GitHub'ом).
Полный отчёт витка — `docs/spec/TZ-9.md` §2.

## Задача

Когда Хозяин положит свежий токен в файл вне git-слежки:

1. push ветки main с витком 8 (бенчмарк, Поправка №9, фикс `up_ms`);
2. тег `v1.0` + GitHub Release с выдержкой из `docs/BENCHMARK-8.md`;
3. описание репо, topics (`agent-supervisor`, `pid1`, `process-manager`,
   `ai-agents`, `supervisor`, `c`), флаги Settings по доктрине
   `rtynbirf/github-runbook`;
4. перевод репо в public — только после скана `grep -rEn
   'ghp_[A-Za-z0-9]{20,}' . --exclude-dir=.git` → пусто;
5. сверка: README, LICENSE (MIT), CONSTITUTION — на месте.

## Отчёт (виток 9, 2026-11-07)

1. **Push**: чистый клон в /tmp (токен — только в URL, клон удалён
   после), overlay локального дерева правды, коммит витков 8–9
   (бенчмарк M1–M7 + транскрипты, Поправка №9, фикс `up_ms`, пакет
   витка 9), push main.
2. **Тег и релиз**: аннотированный `v1.0` запушен; GitHub Release
   создан API с выдержкой из BENCHMARK-8.md (таблица M1–M7, сироты
   0 из 100 у agryp против 100 из 100 у stdiobus, граница Ст. 9 и
   M8 — закрытие клеткой).
3. **Description/topics**: описание и 10 topics стояли с витка 5 и
   являются надмножеством списка этого ЦУ (pid1, process-manager,
   ai-agents, supervisor, c — внутри; agent-supervisor не влез —
   лимит доктрины runbook 5–11 уже исчерпан полезным набором с
   `init-system`, `ndjson`, `posix`, `agent-infrastructure`, `cgroups`).
   Флаги Settings приведены к runbook: `delete_branch_on_merge` false→true,
   squash/merge-заголовки COMMIT_OR_PR_TITLE→PR_TITLE/PR_BODY; Issues ON и
   Wiki/Discussions/Projects OFF подтверждены; Dependabot-алерты и
   автоматические security-фиксы — 204. Хвост правды (Ст. 6):
   `allow_auto_merge` API аккаунта не принял — PATCH с ним и точечный
   повтор вернули прежнее значение; флаг назван неустановленным, а не
   «поставлен».
4. **Скан секретов до флипа**: пусто и по рабочему дереву
   (`grep -rEn 'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}'`,
   плюс литералы старого и нового токенов), и по всей истории
   (`git log --all -p`). Токен в историю не попадал никогда — только
   в URL одноразовых клонов.
5. **Перевод в public**: PATCH private→false; анонимная сверка:
   `git ls-remote` видит `v1.0` без токена, README/LICENSE (MIT)/
   CONSTITUTION на месте (contents API), репо читается без авторизации.

## Приёмки — исполнены

1. `git ls-remote` видит тег `v1.0` (анонимно, после флипа).
2. Релиз содержит таблицу из BENCHMARK-8.md.
3. Секретов в дереве и истории нет (скан — до флипа публичности).
