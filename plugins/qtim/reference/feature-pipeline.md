# Feature-pipeline qtim для Codex

> Generic reference qtim. Проектные инварианты и роли живут в `.codex/team-charter.md`; здесь — переносимая механика PM-конвейера «хотелка -> план». Setup переносит суть этого файла в charter (PM track), чтобы сгенерированные агенты не зависели от файлов плагина.

## Принцип

PM-трек документирует, dev-трек реализует. Церемония пропорциональна риску, а не самому ярлыку «фича»:

- **Полный трек** — многофазная фича, размер L/XL или сработало хотя бы одно условие Fork Test из [intake-protocol.md](intake-protocol.md). Выход: пять последовательных артефактов.
- **Fast-path** — S/M-хотелка в одну фазу без развилок. Стадии PRD/decomposition/estimate/plan заменяет один `feature-brief.md` с единственным checkpoint после Intake.

Трек предлагает main thread после Intake; пользователь подтверждает или переопределяет его на checkpoint. Если внутри fast-path обнаружилась развилка или многофазность, сохрани `intake.md`, переименуй незавершённый `feature-brief.md` в `prd.md`, приведи его к PRD-формату и продолжи полным треком. Зафиксируй переход в «Истории изменений».

Артефакты версионируются в `docs/features/<slug>/`. `memory/` хранит только решения и указатели, не содержимое документов.

## Артефакты и статусы

| Файл | Содержимое |
|---|---|
| `intake.md` | исходная хотелка, уточнения, подтверждённый трек |
| `prd.md` | полный трек: цели, сценарии, acceptance criteria |
| `decomposition.md` | полный трек: work items с привязкой к слоям и файлам |
| `estimate.md` | полный трек: grounded-оценки S/M/L/XL |
| `plan.md` | полный трек: фазы, gates, handoff |
| `feature-brief.md` | fast-path: PRD-lite, grounded work items, план одной фазы, gates и handoff |

Каждый файл начинается с шапки:

```text
Feature: <название>
Slug: <slug>
Status: Draft | Approved | In Development | Done
Дата: YYYY-MM-DD
```

и заканчивается секцией `## История изменений` (append-only: ревизия, смена трека или зафиксированное в реализации отклонение).

Resume-правило: если каталог уже существует, не начинай заново. `feature-brief.md` означает fast-path; `prd.md`/полный набор — полный трек. Продолжай с первого обязательного артефакта, который не достиг `Approved`. Если набор неоднозначен, прочитай историю `intake.md` и попроси решение только если она не разрешает конфликт.

## Стадии и checkpoints

| Стадия | Кто работает | Выход | Checkpoint |
|---|---|---|---|
| 1 Intake | main thread / product | `intake.md` | пользователь подтверждает понимание и трек |
| 2 PRD | product | `prd.md` | пользователь утверждает PRD |
| 3 Decomposition | product + dev-consult | `decomposition.md` | общий со стадией 4 |
| 4 Estimation | владельцы слоёв + product | `estimate.md` | пользователь одним решением утверждает work items и оценки |
| 5 Plan | product + architect | `plan.md` | финальное approval |
| 6 Handoff | main thread | указатель в `memory/decisions.md` | — |

Fast-path заменяет стадии 2-5 одним `feature-brief.md`; стадии 1 и 6 общие.

## Fast-path brief

Main thread собирает brief сам. Обязательного fan-out ролей нет, но evidence остаётся обязательным: читай ключевые файлы, используй built-in `explorer` для широкого поиска или уже активную профильную роль для точечного consult.

DRI и contributing роли/слои в brief задают ownership реализации, а не обязательный planning fan-out. Main thread обосновывает единый размер S/M кодовым evidence; оценку уже привлечённой профильной роли учитывает как дополнительный signal. Если evidence не позволяет обосновать хотя бы один contributing layer или появляется правдоподобный L/XL, переключайся на полный трек с layer estimates.

`feature-brief.md` содержит:

- проблему, желаемый результат, сценарии с acceptance criteria и не-цели;
- work items с DRI, contributing ролями/слоями и привязкой к конкретным файлам;
- размер S/M и одну строку evidence-обоснования;
- одну фазу с verification gates (typecheck/build/tests, browser evidence для UI), rollback/обратимостью и критерием Done;
- секцию `## Handoff`.

Пользователь утверждает brief целиком; после approval переходи к handoff и рекомендуй `$qtim-team-lazy`.

## Dev-consult полного трека

На стадиях 3-4 architect проверяет слои, data flow и инварианты; database/frontend/testing — только реально затронутые слои, каждый возвращает затронутые файлы, интеграционные точки, похожие фичи и риски. Узкая фича обычно требует `qtim-architect` и владельца одного слоя, а не веер всей команды. Consult read-only; вывод ролей — evidence для product. `explorer` используй для broad read-heavy поиска.

Состав work items и оценки утверждаются вместе. Если пользователь меняет decomposition, пересчитай оценки изменённых items до повторного checkpoint.

## Правило нарезки

Work item и фаза плана — вертикальный срез: узкий, но полный путь через затронутые слои (например, схема -> API -> UI -> тесты), который можно продемонстрировать или проверить сам по себе. У каждого item один **DRI** по главной acceptance boundary и список contributing ролей/слоёв; неоднозначного DRI выбирает architect. Горизонтальный план «сначала вся БД, потом весь UI» не подходит.

Исключение — широкий механический rename/retype с blast radius по всей базе. Планируй его через **expand-contract**:

1. добавить новую форму рядом со старой, ничего не ломая;
2. мигрировать call sites небольшими пачками с зелёными gates после каждой;
3. удалить старую форму последним item, когда ссылок не осталось.

## Правила grounded-оценки полного трека

- Только S/M/L/XL + confidence + риск-факторы; часы и дни не выдумывать.
- Каждая contributing роль даёт оценку своего layer slice с evidence. DRI возвращает один итоговый S/M/L/XL для всего vertical item и коротко объясняет синтез, включая integration/coordination risk; размеры не складываются механически.
- XL любого layer slice или итогового item означает «разрезать work item» и вернуться к decomposition.
- Product сводит layer estimates и DRI synthesis, но не переоценивает техническую работу сам.
- Каждая оценка ссылается на evidence: файлы, тестовое покрытие, интеграционные точки, reference class из git или `memory/decisions.md`.
- Оценка без evidence не принимается.

## Handoff contract

- Полный трек: `plan.md` ссылается на `prd.md` и заканчивается готовым prompt для `$qtim-team-up` или `$qtim-team-lazy`.
- Fast-path: `feature-brief.md` — единый источник scope, acceptance criteria, gates и prompt для `$qtim-team-lazy`.
- Реализующая команда переводит плановый документ и связанные артефакты в `In Development`, затем `Done` после gates.
- Отклонения от плана с обоснованием и новые edge cases пишутся в «Историю изменений» планового документа (`plan.md` или `feature-brief.md`).
- В `memory/decisions.md` добавляется одна строка-указатель на утверждённую фичу.

## Anti-Patterns

- Полный трек для S/M-хотелки без развилок или fast-path при сработавшем Fork Test.
- Decomposition/estimate без обследования кода нужными владельцами слоёв.
- Product или PM-конвейер пишет production code, SQL или тесты.
- Куски кода/SQL внутри артефактов: документы хранят контракты, инварианты и acceptance criteria, не будущий diff.
- Отдельные checkpoints для decomposition и estimate вместо одного решения.
- Спавн всех consult-ролей по привычке, даже когда их слои не затронуты.
- Горизонтальная нарезка по слоям вместо проверяемых вертикальных срезов.
- Пропуск checkpoint «потому что очевидно».
- Перезапуск существующего slug с нуля.
- Молчаливое отклонение от планового документа без строки в истории.
