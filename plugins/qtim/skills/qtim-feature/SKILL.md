---
name: qtim-feature
description: "Use when a PM or analyst wants to turn a raw feature idea into implementation-ready, versioned artifacts in docs/features/<slug>/: select a risk-proportional fast-path feature brief or the full intake -> PRD -> grounded decomposition and estimate -> plan pipeline, then hand off to $qtim-team-lazy or $qtim-team-up."
---

# qtim Feature Pipeline

Веди хотелку от идеи до утверждённого handoff. Этот вызов явно разрешает нужный read-only fan-out: `qtim-product`, `qtim-architect`, владельцы затронутых dev-слоёв и built-in `explorer`.

Production code не пиши. Артефакты содержат требования, evidence, контракты, инварианты и gates, а не будущие диффы.

## Preconditions

1. Прочитай `.codex/team-charter.md`. Если файла или PM track marker `<!-- qtim:track:pm:start -->` нет, остановись и предложи `$qtim-setup`.
2. Прочитай `../../reference/feature-pipeline.md` и `../../reference/intake-protocol.md`.
3. Прочитай `../../reference/model-profiles.md`. qtim team-lead должен работать на `gpt-5.6-sol` + `ultra`; не переключай уже открытый task скрыто. Если runtime exposes другой профиль, остановись до fan-out и попроси открыть новый task на Sol/Ultra. `Ultra` не расширяет scope и не отменяет checkpoints.
4. Определи kebab-case slug.
5. Если `docs/features/<slug>/` существует, прочитай статусы и «Историю изменений». `feature-brief.md` означает fast-path, `prd.md`/полный набор — полный трек. Продолжи с первого незавершённого обязательного артефакта, не начинай заново.

Если custom agent не стартует именно из-за model pair, не удаляй пару и не заменяй её inheritance молча. Отличающийся override сохрани; продолжи через `worker` с inline role instructions только на явно подтверждённой доступной pair. Built-in `explorer` используй на `gpt-5.6-luna` + `medium`; не угадывай slug и не считай auth/network ошибку несовместимостью модели.

## Artifacts

Общий файл — `intake.md`. Полный трек добавляет `prd.md`, `decomposition.md`, `estimate.md`, `plan.md`; fast-path — один `feature-brief.md` вместо этих четырёх. Шапка, статусы Draft -> Approved -> In Development -> Done и append-only «История изменений» — по feature-pipeline reference. `memory/decisions.md` хранит только указатель на утверждённую фичу.

## Stage 1: Intake And Track

Сначала прочитай продуктовую память, если создана: `memory/product-map.md`, `product-actors.md`, `product-glossary.md`, `product-metrics.md`. Если её нет в существующей кодовой базе, предложи `$qtim-product-onboard`, но не блокируй работу.

Проведи итеративное интервью порциями по 1-3 решения. Факты из кода, `memory/`, git и документации добывай сам. Сначала выясни проблему, пользователя и желаемый результат; затем критерии успеха, ограничения, совместимость и non-goals. Остановись, когда ответы перестали менять понимание.

Запиши `intake.md`. На checkpoint покажи:

- сводку понимания;
- предварительный размер и число фаз с evidence;
- результат Fork Test из intake protocol;
- рекомендуемый трек.

Предлагай **fast-path** только для S/M, одной фазы и без Fork Test triggers. Иначе — полный трек. Пользователь подтверждает понимание и может переопределить трек; зафиксируй выбор и переведи intake в Approved.

## Fast-path: Feature Brief

Собери `feature-brief.md` сам. Обязательного веера ролей нет: evidence найди чтением и точечным `explorer`; уже активную профильную роль используй только по реально затронутому слою. DRI и contributing роли/слои здесь задают ownership реализации, а не обязательный planning fan-out. Единый размер S/M обоснуй кодовым evidence; если уже консультировал профильную роль, учти её оценку как signal. Не можешь обосновать contributing layer или видишь правдоподобный L/XL — переходи на полный трек.

Brief включает:

- проблему, желаемый результат, сценарии с acceptance criteria и non-goals;
- work items с DRI, contributing ролями/слоями и привязкой к файлам;
- размер S/M с evidence-обоснованием;
- одну проверяемую фазу: gates, rollback/обратимость, Done;
- `## Handoff` для `$qtim-team-lazy`.

**Единственный checkpoint вместо стадий 2-5:** пользователь утверждает brief целиком; Status -> Approved.

Если при сборке возникла развилка, L/XL или больше одной фазы, разверни полный трек: сохрани intake, переименуй незавершённый brief в `prd.md`, перестрой его как Draft PRD, запиши причину перехода в историю и продолжи со стадии PRD. Не поддерживай одновременно два конкурирующих плановых документа.

После approval переходи к Handoff.

## Full Track Stage 2: PRD

Spawn `qtim-product` (fallback: `worker` с PM-инструкциями из charter) с read-first на charter PM track и `intake.md`.

`prd.md` содержит цели, non-goals, сценарии и acceptance criteria, UX-заметки, метрики, риски, open questions. Метрики связывай с реальными событиями из `memory/product-metrics.md`; отсутствующее событие — задача на tracking, не факт. **Checkpoint:** пользователь утверждает PRD; Status -> Approved.

## Full Track Stage 3: Grounded Decomposition

Состав consult пропорционален задетым слоям:

1. Spawn read-only `qtim-architect` для слоёв/data flow/инвариантов и только нужные `qtim-database`, `qtim-frontend`, `qtim-testing`; узкая фича обычно требует architect + одного владельца слоя. `explorer` — broad search. Уважай runtime cap и запускай batches; child agents не делегируют дальше.
2. `qtim-product` агрегирует `decomposition.md`: `id | вертикальный work item | DRI | contributing роли/слои | зависимости | grounding (файлы)`. DRI владеет главной acceptance boundary; неоднозначный ownership разрешает architect.

Каждый work item — проверяемый вертикальный срез через затронутые слои. Для широкого механического rename/retype используй expand-contract. Отдельного checkpoint здесь нет.

## Full Track Stage 4: Grounded Estimation

Каждая contributing роль даёт S/M/L/XL + confidence + риски для своего layer slice с evidence (файлы, покрытие, интеграционные точки, reference class из git или `memory/decisions.md`). DRI возвращает один итоговый размер vertical item с явным синтезом integration/coordination risk; не складывай размеры механически. Без evidence оценка не принимается; XL любого slice или item означает вернуться к decomposition и разрезать item.

`qtim-product` сводит `estimate.md`. **Общий checkpoint стадий 3-4:** пользователь одним решением утверждает work items и оценки; оба артефакта -> Approved. Если состав изменён, пересчитай оценки затронутых items до повторного checkpoint.

## Full Track Stage 5: Plan

`qtim-product` + `qtim-architect` собирают `plan.md`:

- проверяемые вертикальные фазы с work items;
- disjoint write scopes, которые можно параллелить;
- typecheck/build/tests/browser gates;
- rollout, rollback и обратимость;
- критерий Done.

Сначала ставь решения с высокой неопределённостью (данные, API-контракты, UX-развилки), механическую доводку — позже. Широкий рефактор планируй expand-contract.

Если architect создал ADR, **до** финального checkpoint main thread запускает новый read-only thread без истории на `gpt-5.6-sol` + `xhigh`; при сочетании «необратимо + затронут документированный инвариант» — `max`. Findings возвращаются architect для проверки, а ADR получает строку `adr-stress-test:`. Optional code-review gate этот шаг не отключает.

**Checkpoint:** финальное approval; Status -> Approved.

## Stage 6: Handoff

1. Добавь одну строку-указатель в `memory/decisions.md`.
2. Для полного трека заверши `plan.md`:

```text
$qtim-team-up: реализуй Phase 1 из docs/features/<slug>/plan.md.
PRD и acceptance criteria: docs/features/<slug>/prd.md.
Обнови Status артефактов: In Development при старте, Done после gates.
Отклонения и новые edge cases фиксируй в «Истории изменений» plan.md.
```

3. Для fast-path заверши brief:

```text
$qtim-team-lazy: реализуй docs/features/<slug>/feature-brief.md.
Scope, acceptance criteria и gates находятся в этом документе.
При старте переведи Status в In Development, после всех gates — в Done.
Отклонения и новые edge cases фиксируй там же.
```

4. Рекомендуй `$qtim-team-up` для многофазного полного трека, `$qtim-team-lazy` для fast-path и однофазного S/M.
5. Если charter содержит только PM track и нет `qtim-reviewer`, предупреди: перед реализацией нужно повторно вызвать `$qtim-setup` и добавить dev track, иначе режим D останется без финального gate.
6. Если реализацию запускает другой человек, попроси его использовать готовый prompt в новой задаче Codex.

## Anti-Patterns

- Full track на простой S/M-хотелке без развилок или fast-path при Fork Test trigger.
- Отдельные approvals decomposition и estimate.
- Fan-out всех ролей независимо от затронутых слоёв.
- Горизонтальные work items «вся БД / весь UI» вместо вертикальных срезов.
- Production code, SQL, тесты или будущие диффы в артефактах.
- Перезапуск существующего slug с нуля.
- Выдуманные часы вместо относительной оценки с evidence.
- Пропуск checkpoint «потому что очевидно».
