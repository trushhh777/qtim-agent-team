# Паттерны оркестрации qtim для Codex

> Этот файл читает team-lead. Subagents получают только свой bounded prompt и ссылки на `.codex/team-charter.md` / `memory/`.

Codex subagents запускаются явно. Вызов `$qtim-team-up` или `$qtim-team-lazy` является явной просьбой пользователя на соответствующий subagent workflow.

## Execution Depth

| Mode | Когда | Codex-механика |
|---|---|---|
| A Direct | простая правка, вопрос, небольшой поиск | main thread |
| B Single subagent | изоляция контекста или одна bounded работа | один `explorer`/`worker`/custom agent |
| C Lazy team | несколько ролей, один проход без петель | spawn нужных ролей по мере необходимости |
| D Full team-up | implement -> test -> fix -> retest -> review | параллельный warm-up ролей + циклы |

При сомнении стартуй дешевле и эскалируй вверх.

## Patterns

### 1. Tournament

Когда есть несколько валидных архитектурных или UX-подходов. Spawn 2-4 independent agents with different angles, then synthesize in main thread or a reviewer/judge agent.

Rules:

- every candidate gets the same rubric;
- rubric references `memory/invariants.md`;
- main thread decides and records the winning ADR in `memory/decisions.md`.

### 2. Loop Until Done

Когда нужен повтор до stop condition: flaky bug, browser reproduction, performance threshold.

Rules:

- set max iterations and time budget;
- tester owns reproduction evidence;
- implementation agent fixes only after the bug is localized;
- record final trace and fix in `memory/bug-log.md`.

### 3. Classify And Act

Когда нужно разложить backlog, bug list, failing tests, routes, tables or components by owner.

Rules:

- use explorer/classifier first for read-heavy triage;
- main thread assigns owners;
- P0/P1 can trigger immediate worker tasks;
- lower priority items go to memory/backlog rather than spawning unnecessary agents.

### 4. Fan-Out And Synthesize

Когда есть независимые scopes: routes, tables, packages, UI screens, risk lenses.

Rules:

- one agent per independent scope;
- disjoint write sets for write tasks;
- read-only audit scopes can run broadly;
- main thread deduplicates and verifies file:line claims.

### 5. Independent Review / Adversarial Verification

Когда изменение security-critical, money-critical, public API, migration, auth, tenant/scope visibility, or hard to rollback.

Use `independent-review.md`. Spawn one or more read-only reviewer threads with a narrow prompt. They do not edit code. Main thread verifies every finding.

### 6. Generate And Filter

Когда нужно много дешёвых вариантов: copy, names, empty states, UX labels, test scenario names.

Rules:

- generator produces many candidates;
- filter/judge uses explicit rubric;
- top-K only enters implementation;
- record final choice if product-visible.

## Готовые рецепты

Конкретизация паттернов выше под три частых кейса. В Codex нет отдельного workflow-движка: рецепт исполняет main thread, явно спавня subagent threads по стадиям. Запуск — только по opt-in пользователя; итог main thread коммитит в `memory/` сам (subagent threads эфемерны).

### Recipe: Ensemble Review (паттерны 4 + 5)

Когда: перед мержем крупного или рискованного эпика; для money/security-critical — обязателен до APPROVED.

1. **Линзы (параллельно, read-only).** По одному reviewer-агенту на линзу; каждый получает scope (по умолчанию — незакоммиченные изменения: `git status` + `git diff`) и ровно одну линзу. Дефолтный набор:
   - модель доступа и видимость данных: обход политик/гардов, утечка чужих данных, наследование scope дочерними сущностями;
   - гонки и идемпотентность: конкурентные write-пути (все ветки, не только основная), повторный прогон миграций;
   - производительность: N+1, отсутствующие индексы на FK и колонках фильтра, лишние запросы;
   - типы и контракты: any, локальные дубли типов, hardcode URL/ключей вместо конфига;
   - UX-поверхность: loading/empty/error, тексты на языке UI, тестовые селекторы на интерактиве.

   Каждая линза сверяется с charter + `memory/` и возвращает findings строго `file:line + severity P0-P3` — не стилистику и не пожелания.
2. **Скептик-верификация.** На каждый finding — отдельный агент с заданием «попробуй ОПРОВЕРГНУТЬ по фактическому коду»; не подтвердилось по коду -> finding отброшен. При потоке findings ограничивай: топ-10-12 на линзу по severity, остальное отметь как непроверенное.
3. **Синтез (main thread).** Дедуп (одна проблема из разных линз = одна запись), группировка по severity, маршрутизация по ролям-владельцам; вердикт NOT APPROVED при любом подтверждённом P0/P1. Отчёт — в `memory/review-report.md`.

### Recipe: Access Audit (паттерн 4, барьер перед синтезом)

Когда: периодический security-аудит видимости данных или проверка после изменения модели доступа.

1. Вход: явный список сущностей (workspace, project, ...) — без него аудит не стартует.
2. **Fan-out (параллельно, read-only).** Агент на сущность: включён ли контроль доступа и есть ли политика/гард на каждой операции; наследование scope дочерними сущностями (нет ли собственного владельца в обход канона); утечка чужих данных; обходные пути (серверные routes мимо политики, привилегированный клиент без гарда). Findings с `file:line`, сверка с charter + `memory/`.
3. **Синтез — только после ВСЕХ отчётов** (щели на стыках видны только по полной картине): карта видимости по ролям/акторам + список щелей (дочерние сущности, наследующие scope; пересечения политик; обходные пути). Карту — в `memory/` (topic-файл со ссылкой из `MEMORY.md`).

### Recipe: Flaky Hunt (паттерн 2)

Когда: тест или сценарий падает «раз в N прогонов» и нужен воспроизводимый trace для фикса.

1. Вход: сценарий и как его гонять (команда/шаги/URL); stop-условия: trace пойман / max прогонов (по умолчанию ~25) / лимит времени-бюджета.
2. **Цикл.** tester-агент прогоняет сценарий; при fail сохраняет артефакты (trace, скриншот, console+network лог) в принятый в проекте каталог и возвращает путь; зелёный прогон -> следующая итерация. Код в цикле не правится.
3. **Фиксация.** Пойманный trace и итоговый фикс — в `memory/bug-log.md`. Не пойман за лимит — честно сказать и предложить увеличить лимит или изменить условия среды.

## Global Rules

- Do not spawn subagents unless the user explicitly asked via qtim skill or direct delegation request.
- Do not paste full orchestration rules into subagent prompts.
- Do not run parallel writers over overlapping files.
- Subagent output is evidence, not truth.
- Durable decisions go into `memory/`.
- Close completed threads when they are no longer needed.
