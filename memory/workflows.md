# Workflow state map

## Авторизация и глубина

qtim fan-out разрешён только явным skill invocation или прямой просьбой. A/B/C/D означает глубину coordination loops, а не число ролей: `plugins/qtim/reference/orchestration-patterns.md:7-25,127-135`.

- A — main thread.
- B — один bounded agent.
- C — `$qtim-team-lazy`, один проход нескольких нужных ролей.
- D — `$qtim-team-up`, implement -> test -> fix -> retest -> review.

Main thread владеет graph; child agents возвращают запрос на роль и не спавнят qtim descendants.

Cross-dialog `$qtim-mission` ортогонален A/B/C/D: coordinator владеет видимыми
peer tasks, DAG, integration и общим verification gate, а node с
`execution: lazy` получает ровно один локальный уровень `$qtim-team-lazy`:

```text
Approved spec -> ready -> creating -> running -> succeeded -> validated
writer: validated -> topological cherry-pick -> affected gate -> integrated
validated/integrated dependencies -> downstream -> clean-context verification
APPROVED -> Done
```

`PREVIEW`/`RECOMMEND` не создают tasks; `clientThreadId` не считается usable
`threadId`; dirty checkout, scope violation, lost handle и conflict блокируются
fail-visible. Portable evidence живёт в `memory/missions/<slug>/`, opaque runtime
hints — отдельно в gitignored `.codex/qtim-runtime/`.

## Bootstrap и onboard

- `$qtim-setup`: discovery -> решения -> подтверждённый plan -> generation -> verification. Re-run меняет только выбранные track markers и сохраняет другой track/ручной текст: `plugins/qtim/skills/qtim-setup/SKILL.md:112-145,224-231`.
- `$qtim-onboard`: inventory -> подтверждение объёма -> read-only researchers -> main-thread synthesis -> index: `plugins/qtim/skills/qtim-onboard/SKILL.md:18-51`.
- `$qtim-product-onboard`: отдельный проход по экранам/flows, акторам, glossary и analytics; dev-memory не заменяет: `plugins/qtim/skills/qtim-product-onboard/SKILL.md:22-56`.

## Feature lifecycle

```text
Intake
  ├─ S/M, одна фаза, без Fork Test -> feature-brief.md -> handoff
  └─ L/XL, много фаз или Fork Test -> prd.md -> decomposition.md
                                      -> estimate.md -> plan.md -> handoff
```

- Пользователь подтверждает track после Intake; fast-path может перейти в full с записью в `История изменений`: `plugins/qtim/reference/feature-pipeline.md:7-14`.
- Каждый artifact имеет `Feature`, `Slug`, `Status`, `Дата` и append-only history; statuses `Draft -> Approved -> In Development -> Done`: `plugins/qtim/reference/feature-pipeline.md:16-36`.
- Existing slug не перезапускается; продолжение идёт с первого обязательного artifact без `Approved`: `plugins/qtim/reference/feature-pipeline.md:38`.
- Decomposition/estimate имеют общий checkpoint; consult selective; slices вертикальные с одним DRI, grounded S/M/L/XL: `plugins/qtim/reference/feature-pipeline.md:69-92`.
- Handoff переводит plan/brief в `In Development`, затем `Done`; deviations идут
  в history, а `memory/decisions.md` получает один pointer. Перед pointer обязателен
  блок «Что запускать дальше» с topology-based выбором direct/team-lazy/team-up/
  mission; recommendation ничего не запускает. Approved mission graph получает
  `запусти`, а unresolved integration/lazy/runtime choice — `preview`.

## Team lifecycle

- `$qtim-team-lazy` эскалирует в team-up при rework loop, review block, новой обязательной роли или irreversible ambiguity: `plugins/qtim/skills/qtim-team-lazy/SKILL.md:10-18,35-44`.
- `$qtim-team-up` читает `memory/epic-state.md`, feature artifacts и ведёт D-loop до gates: `plugins/qtim/skills/qtim-team-up/SKILL.md:12-33`.
- После законченной C/D работы `$qtim-team-retro` записывает `retro-log.md` и role-scoped `lessons.md`: `plugins/qtim/skills/qtim-team-retro/SKILL.md:6-35`.
- `$qtim-team-down` записывает незавершённый handoff в `epic-state.md`; stale state удаляется только после завершения: `plugins/qtim/skills/qtim-team-down/SKILL.md:12-31`.

## Update state machine

1. Сравнить installed plugin version и charter stamp.
2. Если project новее plugin — не downgrade.
3. Собрать upgrade sections oldest→newest.
4. Показать diff/plan и получить подтверждение.
5. Сохранять user edits, unknown hooks, `memory/` и `docs/features/`.
6. Поднимать charter/TOML stamps только после полностью применённой версии.
7. При первом `pending` остановиться; следующий update повторяет незавершённый диапазон.

Evidence: `plugins/qtim/skills/qtim-update/SKILL.md:10-61`.

Исторический текст migration sections является versioned evidence, а не текущей policy: 2.9 inheritance superseded явными pairs 2.10.
