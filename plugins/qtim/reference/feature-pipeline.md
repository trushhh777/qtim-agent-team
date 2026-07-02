# Feature-pipeline qtim для Codex

> Generic reference qtim. Проектные инварианты и роли живут в `.codex/team-charter.md`; здесь — переносимая механика PM-конвейера «хотелка -> план». Setup переносит суть этого файла в charter (PM track), чтобы сгенерированные агенты не зависели от файлов плагина.

## Принцип

PM-трек документирует, dev-трек реализует. Каждая фича проходит фиксированные стадии с checkpoint у пользователя; артефакты — версионируемые файлы в `docs/features/<slug>/` проекта. `memory/` хранит только решения и указатели на артефакты, не их содержимое.

Точность описания задачи важнее скорости: декомпозиция и оценка обязаны опираться на consult профильных dev-агентов, а не на предположения PM-роли.

## Артефакты и статусы

Канонический набор файлов `docs/features/<slug>/`:

| Файл | Содержимое |
|---|---|
| `intake.md` | исходная хотелка + уточнения пользователя |
| `prd.md` | PRD: цели, сценарии, acceptance criteria |
| `decomposition.md` | work items с привязкой к слоям и файлам |
| `estimate.md` | grounded-оценки S/M/L/XL по work items |
| `plan.md` | фазы реализации, gates, handoff |

Каждый файл начинается с шапки:

```text
Feature: <название>
Slug: <slug>
Status: Draft | Approved | In Development | Done
Дата: YYYY-MM-DD
```

и заканчивается секцией `## История изменений` (append-only, строка на ревизию).

Resume-правило: если `docs/features/<slug>/` уже существует, продолжай с первой стадии, чей артефакт не в статусе Approved и выше. Не перезапускай конвейер с нуля.

## Стадии и checkpoints

| Стадия | Кто работает | Выход | Checkpoint |
|---|---|---|---|
| 1 Intake | main thread / product | `intake.md` | пользователь подтверждает понимание |
| 2 PRD | product | `prd.md` | пользователь утверждает PRD |
| 3 Decomposition | product + dev-consult | `decomposition.md` | пользователь утверждает состав work items |
| 4 Estimation | профильные dev-роли + product | `estimate.md` | пользователь принимает оценки и риски |
| 5 Plan | product + architect | `plan.md` | финальное approval |
| 6 Handoff | main thread | указатель в `memory/decisions.md` | — |

Правило dev-consult (стадии 3-4): architect смотрит слои, data flow и инварианты; database/frontend/testing роли — каждый свой слой (затронутые файлы, интеграционные точки, существующие похожие фичи, риски). Consult-режим read-only: dev-агенты не редактируют файлы, их вывод — evidence для product-роли. `explorer` — для broad read-heavy поиска по кодовой базе.

## Правила grounded-оценки

- Шкала только относительная: **S / M / L / XL** + confidence (high / medium / low) + риск-факторы. Часы и дни не выдумывать.
- XL означает «work item нужно разрезать», а не «очень долго».
- Размер каждого work item даёт профильный dev-агент — владелец слоя, не PM-роль.
- Каждая оценка обязана ссылаться на evidence: конкретные файлы, покрытие тестами, число интеграционных точек, похожие прошлые фичи (git log, `memory/decisions.md`) как reference class.
- Оценка без evidence не принимается в `estimate.md`.

## Handoff contract

- `plan.md` заканчивается секцией `## Handoff` с готовым prompt для реализации через полный team-workflow или lazy-режим.
- Dev-команда читает `plan.md` (scope, фазы, gates) и `prd.md` (acceptance criteria) как источник требований.
- Тот, кто реализует, обновляет Status артефактов: `In Development` при старте, `Done` после прохождения gates.
- Многофазные фичи — полный team-workflow; S/M в одну фазу — lazy-режим.
- В `memory/decisions.md` добавляется одна строка-указатель на утверждённую фичу.

## Anti-Patterns

- Оценки и декомпозиция без обследования реального кода профильными ролями.
- PM-роль пишет production code, SQL или тесты.
- Пропуск checkpoint «потому что и так очевидно».
- PRD и решения только в чате или в `memory/` вместо `docs/features/`.
- Перезапуск конвейера с нуля при существующем slug.
- Дублирование содержимого артефактов в `memory/` вместо указателей.
