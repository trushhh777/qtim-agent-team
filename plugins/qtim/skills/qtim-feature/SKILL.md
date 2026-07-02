---
name: qtim-feature
description: "Use when a PM/analyst wants to drive a raw feature idea through the qtim pipeline in Codex: intake -> PRD -> grounded decomposition -> estimate -> plan, with versioned artifacts in docs/features/<slug>/ and handoff to $qtim-team-up or $qtim-team-lazy."
---

# qtim Feature Pipeline

Ты ведёшь хотелку от сырой идеи до утверждённого плана реализации. Invocation of this skill is explicit permission to spawn the Codex subagents needed for grounding: `qtim-product`, `qtim-architect`, профильные dev-роли в consult-режиме и built-in `explorer`.

Production code из этого skill не пишется — выход конвейера это документы и handoff.

## Preconditions

1. Read `.codex/team-charter.md`. Если файла нет или в нём нет PM track (маркер `<!-- qtim:track:pm:start -->`), stop and ask the user to run `$qtim-setup`.
2. Read `../../reference/feature-pipeline.md` for shared mechanics.
3. Определи slug фичи: kebab-case от короткого имени.
4. Если `docs/features/<slug>/` уже существует, прочитай Status всех артефактов и **продолжи с первой стадии, чей артефакт не Approved**. Не перезапускай конвейер с нуля.

## Artifacts

Все артефакты — в `docs/features/<slug>/`: `intake.md`, `prd.md`, `decomposition.md`, `estimate.md`, `plan.md`. Шапка (Feature / Slug / Status / Дата), секция «История изменений» и статусная машина Draft -> Approved -> In Development -> Done — по конвенции из charter PM track. В `memory/decisions.md` — только строка-указатель на утверждённую фичу.

## Stage 1: Intake

Перед вопросами прочитай продуктовую память, если она создана (`memory/product-map.md`, `product-actors.md`, `product-glossary.md`, `product-metrics.md` — их наполняет `$qtim-product-onboard`): говори с пользователем в терминах его продукта и не спрашивай то, что уже известно из памяти. Если памяти нет и кодовая база существует — предложи прогнать `$qtim-product-onboard` (не блокирует: можно продолжать без него).

Задай пользователю структурированные вопросы (одним компактным блоком, не по одному):

- какую проблему решаем и кто её испытывает;
- желаемый результат в языке пользователя;
- критерии успеха;
- ограничения: сроки, зависимости, совместимость;
- что явно вне scope.

Запиши `intake.md`. **Checkpoint:** покажи сводку понимания, получи подтверждение до PRD.

## Stage 2: PRD

Spawn `qtim-product` (fallback: `worker` с inline-инструкциями PM-роли из charter) с компактным prompt по шаблону team-up: read first AGENTS.md, charter PM track, `intake.md`.

Выход — `prd.md`: цели, не-цели, сценарии с acceptance criteria, UX-заметки, метрики, риски, open questions. Метрики успеха привязывай к реальным событиям аналитики из `memory/product-metrics.md`, когда память создана; отсутствующее событие фиксируй как задачу на трекинг, а не как факт. **Checkpoint:** пользователь утверждает или правит; Status -> Approved.

## Stage 3: Decomposition (grounded)

Точность описания важнее скорости — декомпозиция строится на consult dev-команды, не на предположениях:

1. Fan-out read-only consult по затронутым слоям: `qtim-architect` (слои, data flow, инварианты) и профильные `qtim-database` / `qtim-frontend` / `qtim-testing` — каждый возвращает по своему слою затронутые файлы, интеграционные точки, похожие существующие фичи и риски. `explorer` — для broad-поиска. Consult-агенты не редактируют файлы.
2. `qtim-product` агрегирует `decomposition.md`: таблица work items `id | название | слой/роль | зависимости | grounding (файлы)`.

**Checkpoint:** пользователь утверждает состав work items.

## Stage 4: Estimation (grounded)

Размер каждого work item даёт профильный dev-агент — владелец слоя: S / M / L / XL + confidence + риск-факторы, каждая оценка с evidence (файлы, покрытие тестами, интеграционные точки, reference class из git log / `memory/decisions.md`). Оценка без evidence не принимается. XL = разрезать work item и вернуться к декомпозиции.

`qtim-product` сводит `estimate.md` с итоговой таблицей и суммарным риском. **Checkpoint:** пользователь принимает оценки.

## Stage 5: Plan

`qtim-product` + `qtim-architect` собирают `plan.md`:

- фазы/milestones с составом work items;
- что параллелится (disjoint write scopes);
- verification gates по фазам: typecheck, build, tests, browser evidence для UI;
- rollout/rollback и обратимость;
- критерий Done.

**Checkpoint:** финальное approval; Status -> Approved.

## Stage 6: Handoff

1. Добавь строку-указатель в `memory/decisions.md`.
2. `plan.md` заканчивается секцией `## Handoff` с готовым prompt:

```text
$qtim-team-up: реализуй Phase 1 из docs/features/<slug>/plan.md.
PRD и acceptance criteria: docs/features/<slug>/prd.md.
Обнови Status артефактов: In Development при старте, Done после gates.
```

3. Рекомендация: многофазные фичи — `$qtim-team-up`; S/M в одну фазу — `$qtim-team-lazy`.
4. Если реализацию запускает не пользователь-PM, сообщи, что разработчик вызывает этот prompt в новой Codex thread.

## Anti-Patterns

- Декомпозиция или оценки без consult профильных dev-ролей по реальному коду.
- Production code, SQL или тесты из этого skill.
- Пропуск checkpoint «потому что очевидно».
- PRD и решения только в чате или memory вместо `docs/features/`.
- Перезапуск конвейера с нуля при существующем slug.
- Выдуманные часы вместо относительной шкалы с evidence.
