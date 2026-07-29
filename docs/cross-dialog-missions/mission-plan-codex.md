# Mission Plan Codex

Единый план cross-dialog missions для qtim: от завершения `$qtim-feature` и выбора
следующего workflow до peer-задач, вложенных lazy-команд, dependency handoff,
интеграции и общего verification gate.

Дата: 2026-07-29
Статус: Release gate 2.12.0 пройден; App smoke, `$qtim-grill` и independent review зелёные, ожидается commit/push
Размер реализации capability: **XL**, реализован вертикальными этапами в одном релизе
Порог запуска: **не зависит от размера задачи** — определяется формой работы

Визуальная карта согласования: [plan-review-board.html](plan-review-board.html)
Runtime/integration decision: [ADR-001](adr-001-mission-state-and-git-integration.md)

## Статус согласования

Экспорт пользователя от 2026-07-28:

| Решение | Статус |
|---|---|
| State ADR | Согласовано: portable evidence — монотонные scoped checkpoint commits в отдельной clean state branch/worktree; opaque handles и owner generation — в `.codex/qtim-runtime/` |
| Integration ADR | Согласовано: transaction cherry-pick → affected gate → exclusive promotion lock → exact-old/ff-only/exact-final; handoff не DAG merge |
| Surface contract | Согласовано: App-first full mode + честный CLI/IDE fallback |
| Model contract | Согласовано: обычные peer-задачи используют configured default; override только после явного выбора |
| Cleanup contract | Согласовано: задачи остаются видимыми, archive только после отдельного подтверждения |
| Nested lazy contract | Согласовано: demand-driven число peer-задач и local agents, без plugin hard cap; waves по фактическим runtime limits |
| Feature completion routing | Согласовано как требование: `$qtim-feature` рекомендует следующий workflow и готовую команду, но ничего не запускает без явного разрешения |
| Lazy node profile | Согласовано для 2.12: Sol/Ultra только как exact pair в Approved preview/spec |

## Единая карта плана

```text
$qtim-feature завершена и Approved
        |
        v
Execution Recommendation Gate
        |
        +-- один bounded результат ------------------------------> direct
        +-- один результат + несколько точечных ролей ----------> $qtim-team-lazy
        +-- один связный outcome + implement/test/fix loop -----> $qtim-team-up
        `-- несколько самостоятельных outcomes / A -> B --------> $qtim-mission
                                                                  |
                                                                  v
                                                   Mission Preview / AUTO-START
                                                                  |
                                                                  v
                                           ready peer-задачи + local lazy teams
                                                                  |
                                                                  v
                                               receipts -> handoff -> integration
                                                                  |
                                                                  v
                                                   clean-context verification gate
```

Весь product contract сводится к трём последовательным решениям:

1. `$qtim-feature` определяет **какая форма исполнения нужна** и показывает одну
   рекомендуемую команду.
2. Выбранный workflow определяет **кто владеет координацией**: одна задача,
   team lead или mission coordinator.
3. Общий completion contract определяет **какое evidence превращает работу в Done**.

Размер `S/M/L/XL` помогает оценить стоимость и необходимость декомпозиции, но не
выбирает workflow самостоятельно. Небольшая интеграция API и SDK с зависимостью
может требовать mission; большой, но тесно связанный рефакторинг может остаться
одним `$qtim-team-up`.

## Outcome

Новый явно вызываемый `$qtim-mission` превращает утверждённую цель и DAG work items
в несколько видимых peer-задач Codex App:

```text
Mission coordinator
├─ создаёт готовые peer-задачи в worktrees
│  ├─ простая node -> node lead работает напрямую
│  └─ высокоуровневая node -> node lead вызывает локальный $qtim-team-lazy
│     ├─ выбирает только нужные роли
│     ├─ синтезирует и проверяет их результаты
│     └─ возвращает один NODE RECEIPT coordinator
├─ ждёт status/final result и проверяет receipts
├─ разблокирует downstream nodes по DAG
├─ передаёт bounded context packs и commits/artifacts
├─ последовательно интегрирует изменения
└─ создаёт clean-context verification-задачу
   ├─ APPROVED -> exact evidence bundle -> fenced delivery
   │  -> durable Done checkpoint с delivered revision -> mission Done
   └─ NOT APPROVED -> bounded fix nodes -> повторный gate
```

Skill invocation является явным разрешением на создание только тех задач, которые
описаны в утверждённом mission graph. Worker-задачи остаются видимыми пользователю
peer-задачами. Никакой скрытой постоянной команды не появляется.
Одобренная node с `execution: lazy` дополнительно разрешает main thread этой
peer-задачи поднять только локальную `$qtim-team-lazy` в пределах node scope.

## Практическая ценность

Cross-dialog mission нужна не ради самого количества диалогов. Она снимает с
пользователя ручную работу координатора:

- не нужно самостоятельно создавать задачи A, B и verifier, копировать между ними
  контекст и помнить, кто от кого зависит;
- независимые workstreams могут идти параллельно, а зависимые не стартуют на
  непроверенных или устаревших результатах;
- каждый writer изолирован в своём worktree, поэтому параллельность не превращается
  в гонку за общий checkout;
- длинная миссия не раздувает один контекст: исследование, реализация и проверка
  получают отдельные bounded prompts;
- результат каждой задачи проходит receipt validation, а не принимается на веру;
- пользователь получает один итоговый verdict с evidence и единым verification
  gate вместо нескольких несвязанных «готово»;
- состояние миссии можно показать, продолжить или безопасно остановить без
  восстановления графа по памяти.

Практический эффект особенно заметен, когда цена неправильного порядка, потерянной
зависимости или непроверенной интеграции выше стоимости создания нескольких задач.
Mission не обещает, что любая работа станет быстрее: для маленькой задачи
координационный overhead будет больше пользы.

Node-local lazy team позволяет формулировать диалогам задачи на уровне результата
— например «реализовать backend-срез с контрактом и тестовым evidence», — а не
заранее дробить каждое действие на микрозадачи. Node lead сам выбирает нужные роли,
но внешний DAG по-прежнему оперирует одной проверяемой node.

### Простыми словами: mission или team-up

`$qtim-team-up` — это **один главный диалог с внутренними помощниками**. Главный
диалог хранит цель, раздаёт работу subagents, проводит implement -> test -> fix ->
review loop и возвращает один итог. Выбирать его нужно, когда вся работа остаётся
одним связным результатом в одном контексте.

`$qtim-mission` — это **координатор нескольких самостоятельных диалогов**. У каждого
диалога собственный контекст, outcome и при необходимости worktree. Coordinator
решает, когда стартовать следующий диалог, какой проверенный результат передать
ему и когда проводить общий gate.

Аналогия:

- `team-up` — одна проектная комната: lead и специалисты вместе доводят одну задачу;
- `mission` — программа из нескольких комнат: coordinator управляет очередностью,
  контрактами между командами и общей приёмкой.

| Вопрос | `$qtim-team-up` | `$qtim-mission` |
|---|---|---|
| Сколько верхнеуровневых диалогов | Один | Два и более видимых peer-диалога |
| Где живут помощники | Subagents внутри одной задачи | У каждого peer-диалога могут быть свои bounded lazy subagents |
| Главная ценность | Глубокий цикл доводки одного результата | Разделение контекстов, worktrees и зависимостей между результатами |
| Зависимости A -> B | Lead управляет внутри своего контекста | DAG не создаёт B до validated receipt A |
| Параллельные writers | Возможны, но координируются одной задачей | Изолированы по peer worktrees и интегрируются topologically |
| Resume и наблюдаемость | Возобновляется одна задача и её доступные descendants | Сохраняется mission graph, статусы peer-задач и handoff evidence |
| Цена | Ниже | Выше: больше задач, контекста, worktrees и verification |

Правило выбора:

1. **Один outcome и ожидается implement -> test -> fix loop?** Запускать
   `$qtim-team-up`.
2. **Есть два самостоятельных результата, разные worktrees или зависимость A -> B?**
   Запускать `$qtim-mission`.
3. **Нужно несколько ролей, но только один проход?** Запускать `$qtim-team-lazy`
   без mission.

Mission не является «более мощным team-up». Это более дорогой координатор для
другой формы работы. Например, исправление одной checkout-фичи с тестами — team-up;
миграция API, где backend выпускает контракт, SDK ждёт его, docs обновляются отдельно,
а затем всё интегрируется и проверяется, — mission.

### Execution Recommendation Gate после `$qtim-feature`

Каждая успешно завершённая и согласованная `$qtim-feature` заканчивается обязательным
блоком **«Что запускать дальше»**. Это единая точка маршрутизации для обоих основных
сценариев — `$qtim-team-up` и `$qtim-mission` — а также для direct и
`$qtim-team-lazy`.

Gate оценивает:

- сколько самостоятельных outcomes нужно получить;
- нужен ли отдельный контекст или worktree для каждого outcome;
- есть ли зависимость producer -> consumer или возможность безопасной параллельности;
- ожидается ли один связный implement -> test -> fix -> review loop;
- нужны ли независимый общий verifier, resume и durable handoff;
- какова стоимость координации относительно самой реализации.

Обязательный результат gate:

```text
Рекомендация: $qtim-mission
Почему: backend и SDK — самостоятельные outcomes; SDK зависит от validated
backend contract; после topological integration нужен общий verifier.
Топология: backend -> SDK -> integration -> verification
Команда: $qtim-mission, запусти Approved feature docs/features/payments/.
Альтернатива: $qtim-team-up, если outcomes нельзя безопасно разделить.
```

Gate не запускает workflow. Короткое «Запускай предложенное» выбирает
рекомендованный workflow, но для `$qtim-mission` после простой feature
recommendation сначала открывает `PREVIEW`: peer-задачи ещё не создаются.
`AUTO-START` разрешён только явной displayed `$qtim-mission` командой, которая
ссылается на Approved source или описывает multi-peer shape, либо отдельным
approval после непосредственно предшествующего полного Approved
mission preview с base/targets/scopes/budgets/gates. Для остальных workflows
действует их собственный activation contract.

Матрица выбора:

| Форма работы | Следующий workflow |
|---|---|
| Один bounded outcome, достаточно main task | Direct execution |
| Один outcome, нужны несколько точечных ролей без длинного feedback loop | `$qtim-team-lazy` |
| Один связный outcome, общий контекст и implement -> test -> fix -> review | `$qtim-team-up` |
| Два и более самостоятельных outcomes, разные контексты/worktrees или A -> B | `$qtim-mission` |

Размер — вторичный сигнал:

| Размер | Типичное действие |
|---|---|
| S | Обычно direct; mission только при реальной межконтекстной зависимости |
| M | Direct или team-lazy; mission допустима при двух самостоятельных outcomes |
| L | Team-up либо mission — выбор определяется топологией |
| XL | Сначала декомпозиция; затем один или несколько team-up/mission workflows |

Ни размер `XL`, ни количество затронутых файлов сами по себе не активируют mission.
Для `L/XL` `$qtim-feature` может сильнее подсветить рекомендацию, но остаётся в
режиме `RECOMMEND` до явного запуска.

### Когда выбирать mission

| Ситуация | Почему mission полезна |
|---|---|
| Фича затрагивает независимые backend, frontend и docs workstreams | Независимые nodes идут параллельно, общий контракт проверяется перед интеграцией |
| Миграция API имеет цепочку producer -> consumers -> compatibility gate | DAG не запускает consumers до подтверждения нового контракта |
| Нужно исследовать проблему с разных сторон, затем сделать синтез | Read-only задачи сохраняют независимость контекстов, synthesis получает проверенные выводы |
| Монорепозиторий позволяет менять разные packages в отдельных worktrees | Writer-задачи изолированы, commits интегрируются в заданном порядке |
| Требуются implement -> test -> security/performance review -> fix loops | Общий verifier принимает решение по интегрированному результату |
| Долгая работа должна пережить смену coordinator-задачи | Portable evidence и runtime handles дают проверяемый resume на поддерживаемой поверхности |

Mission обычно не нужна для:

- локальной правки одного файла или короткого последовательного fix;
- двух writers, которые неизбежно одновременно меняют одни и те же строки;
- цели с нерешённой продуктовой развилкой, когда сначала нужно принять решение;
- запроса только на объяснение, ревью или составление плана;
- поверхности без peer thread tools, если отдельные видимые задачи обязательны.

Быстрая эвристика: выбирать mission, когда есть минимум два осмысленно отделимых
workstreams и хотя бы одна из причин — параллельность, зависимость, изоляция
контекста/worktree или независимый общий gate. Иначе использовать обычную задачу,
`$qtim-team-lazy` или `$qtim-team-up`.

## Как запускать

Ниже описан доступный UX `$qtim-mission` версии 2.12. Full mode требует Codex App
peer thread tools; на других surfaces используется честный `$qtim-team-up`
fallback без заявления о созданных peer-задачах.

### Запуск из завершённой feature

По умолчанию `$qtim-feature` завершает работу рекомендацией:

```text
Что запускать дальше: $qtim-team-up
Причина: один связный outcome и общий implement -> test -> fix loop.
Команда: $qtim-team-up, реализуй Approved feature docs/features/checkout/.
```

или:

```text
Что запускать дальше: $qtim-mission
Причина: backend contract -> SDK consumer -> общий compatibility gate.
Команда: $qtim-mission, запусти Approved feature docs/features/payments/.
```

Пользователь отвечает «Запускай предложенное» либо выполняет показанную команду.
Рекомендация остаётся read-only и сама по себе не является authorization.
Короткий ответ после одной рекомендации переводит mission в `PREVIEW`; выполнение
показанной explicit mission-команды либо approval после полного Approved preview
может дать `AUTO-START`.

### Новый запуск

Самый точный способ — явно назвать skill и действие:

```text
$qtim-mission, запусти утверждённый план docs/features/payments/plan.md.
Создай отдельные задачи для backend и SDK, SDK зависит от backend.
После интеграции проведи общий verification gate.
```

Другие допустимые примеры:

```text
$qtim-mission, реализуй Approved feature brief docs/features/search/brief.md.

$qtim-mission, разбей миграцию API на producer, consumers и compatibility verifier.

Создай qtim-миссию из нескольких видимых задач Codex:
сначала исследование A, затем зависящая от него реализация B, после неё общий verifier.

$qtim-mission, запусти фичу отдельными backend и client задачами.
Обе задачи высокоуровневые: внутри каждой разреши $qtim-team-lazy выбрать нужные роли.
```

Прямой запрос естественным языком считается разрешением только тогда, когда в нём
однозначно сказано создать несколько отдельных Codex задач/диалогов и провести
их как одну qtim mission. Одна обычная задача/диалог, planning/evaluation-only
запрос и «реализуй сложную фичу» такого разрешения не дают. Отрицание самой
координации (`не проводи`, `не пользуйся/без использования qtim-миссии`),
отложенное условие (`по завершении`, `как только`, `через неделю`,
`после релиза`, `при условии`, `в случае если`,
`через N секунд/полчаса/пару минут/сутки`) и
natural-language команда с любым quote/code marker — парным, одиночным,
fullwidth или незакрытым — всегда fail-closed.

Coordinator:

1. Проверяет проект, доступность thread tools, git state и исходный артефакт.
2. Строит bounded mission preview: nodes, зависимости, write scopes, нужные роли,
   retry/fix budgets и gates.
3. Либо запускает уже одобренный и однозначный граф, либо просит подтвердить preview.
4. Создаёт только ready-задачи; следующие появляются по мере подтверждения
   dependencies.
5. Показывает итоговый status и ссылку/название задачи, требующей внимания.

### Управление существующей mission

```text
$qtim-mission, status
$qtim-mission, resume payments-sdk
$qtim-mission, stop payments-sdk
```

- `status` ничего не создаёт и показывает DAG, running/blocked nodes и следующий gate;
- `resume` сначала подтверждает единственного coordinator owner/generation,
  затем runtime handles и продолжает только подтверждённое состояние;
- `stop` прекращает новый fan-out, сохраняет evidence и не удаляет чужие задачи;
- очистка или архивирование mission-owned задач остаётся отдельным подтверждаемым
  действием.

## Когда запуск автоматический

«Автоматический» здесь означает: после явного разрешения пользователя coordinator
сам создаёт следующие задачи и передаёт результаты по DAG. Это не означает скрытый
запуск qtim из любого сложного запроса.

### Три режима активации

| Режим | Условие | Поведение |
|---|---|---|
| `AUTO-START` | Пользователь явно сказал «запусти» через `$qtim-mission` и сослался на Approved source либо описал multi-peer shape; недвусмысленно попросил провести несколько Codex peer tasks как одну mission; или ответил «Запускай предложенное» на непосредственно предшествующий полный Approved mission preview; источник `Approved`; граф однозначен; preflight зелёный | Coordinator начинает создание ready-задач без второго подтверждения |
| `PREVIEW` | Mission вызвана явно, но цель сырая, артефакт не утверждён, граф/бюджет неоднозначен или preflight нашёл развилку | Coordinator показывает mission preview и ждёт подтверждения до первого `create_thread` |
| `RECOMMEND` | `$qtim-feature`, `$qtim-team-up` или обычная работа обнаружили хороший кандидат для нескольких диалогов | qtim объясняет выбор, показывает topology и готовую команду `$qtim-mission`, но не создаёт задачи |

Размер feature никогда не переводит `RECOMMEND` в `AUTO-START`. После feature
recommendation короткий approval переводит mission в `PREVIEW`; переход к
`AUTO-START` разрешает displayed explicit command или approval полного Approved
mission preview. Завершение `$qtim-feature` и уровень `XL` сами по себе не
являются authorization. Implicit skill loading нужен только чтобы распознать
такую команду и не является скрытым разрешением.

Для `AUTO-START` одновременно обязательны:

1. Есть явный глагол исполнения: «запусти», «создай задачи», «начни миссию» или
   эквивалент; explicit skill-команда ссылается на Approved source либо описывает
   несколько peer tasks; запрос не ограничен планированием/оценкой.
2. Есть `Approved` plan/brief с acceptance criteria и без открытых Fork Tests.
3. Текущий App project разрешён однозначно, а required thread tools доступны.
4. Base revision или working-tree snapshot понятен; write scopes и worktrees безопасны.
5. DAG ацикличен, retry/fix budgets утверждены, а требуемые роли можно выполнить
   сразу или runtime waves.
6. Для каждой `execution: lazy` node в Approved mission spec явно утверждён профиль
   node lead `gpt-5.6-sol` + `ultra`.
7. Запрос не требует нового model override, destructive integration или решения от
   имени пользователя.

После перехода mission в `Running` coordinator автоматически:

- создаёт node, когда все её dependencies получили валидный receipt;
- внутри `execution: lazy` node запускает только нужные локальные роли и собирает
  их в один проверенный node outcome;
- передаёт downstream только проверенный context pack и artifact/commit ids;
- повторяет технически некорректный handoff в пределах retry budget;
- интегрирует проверенные commits в утверждённом порядке;
- запускает affected gates и отдельную final verification-задачу;
- создаёт bounded fix node по подтверждённому finding, если owner и scope
  однозначны и fix budget не исчерпан.

Coordinator останавливается и возвращает управление пользователю, если:

- задача запросила approval, permission или продуктовый ответ;
- появился новый необратимый выбор либо upstream результат опроверг premise миссии;
- dirty checkout, конфликт integration или scope overlap требуют выбора стратегии;
- worker вышел за scope, runtime потерял handle или retry/fix budget исчерпан;
- для продолжения нужно расширить исходный scope миссии.

`SessionStart` может только напомнить о незавершённой миссии: bounded scan
максимум 50 candidates, максимум 5 records и `+more`. Portable `Verifying`
проверяется по exact derived state ref; authoritative `Done` подавляет reminder,
поскольку terminal checkpoint намеренно не доставляется повторно. Hook не выполняет
`resume` и не создаёт новые задачи без явного `$qtim-mission, resume <slug>`.
Упоминание `$qtim-mission` в документации, цитате, вопросе «что это?» или отрицании
«не запускай mission» также никогда не активирует workflow.

## Основание

Подтверждённый текущий Codex App tool surface предоставляет:

- создание peer-задачи в local project или worktree;
- чтение, ожидание и продолжение существующей задачи;
- переименование, archive/pin controls и handoff git state;
- асинхронное создание, при котором результат может временно содержать только
  `clientThreadId`;
- ожидание максимум восьми targets за один вызов.

Нативные subagents остаются отдельной механикой внутри одной задачи. Cross-dialog
mission строится поверх peer-задач, а не переименовывает subagents в диалоги.

Официальные источники:

- [Projects and chats](https://learn.chatgpt.com/docs/projects)
- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)
- [Codex App Server](https://developers.openai.com/codex/app-server)

Точная callable surface проверяется через `reference/runtime-compat.md` и runtime
probes: plugin не должен считать App tools универсально доступными в CLI/IDE.

## Scope v1

### В scope

- один coordinator и DAG без циклов;
- execution recommendation gate в финале `$qtim-feature`;
- shape-based routing между direct, `$qtim-team-lazy`, `$qtim-team-up` и
  `$qtim-mission`;
- read-only и writer nodes;
- App project threads;
- отдельный worktree для каждой writer node в git-проекте;
- node-local `$qtim-team-lazy` для явно помеченных высокоуровневых nodes;
- demand-driven fan-out: столько peer tasks и local agents, сколько обосновано
  mission graph и node scope;
- wave-based scheduling;
- dependency context packs;
- worker receipts;
- последовательная интеграция результатов;
- clean-context final verification;
- bounded fix loop;
- resume на том же host, когда runtime позволяет найти сохранённые threads;
- fail-visible single-task fallback на поверхностях без peer thread tools.

### Вне scope v1

- собственный daemon, MCP scheduler, SQLite state или app-server client;
- tmux и смешанные Codex/Claude worker teams;
- рекурсивные mission graphs, создаваемые workers;
- node-local `$qtim-team-up` и третий уровень fan-out;
- cloud task orchestration и cross-host code handoff;
- автоматические approvals или ответы на вопросы от имени пользователя;
- автоматическое удаление/архивация чужих задач;
- циклические DAG;
- одновременная интеграция нескольких commits в один checkout;
- обещание resume, если runtime больше не exposes сохранённый thread.

## Архитектура

### 1. Mission coordinator

Coordinator — main thread, в котором явно вызван `$qtim-mission`.

Обязанности:

- проверить `gpt-5.6-sol` + `ultra` prerequisite текущей задачи;
- прочитать charter, `memory/`, feature artifacts и незавершённые missions;
- получить approval mission spec до создания peer-задач;
- вызвать `list_projects` и однозначно разрешить текущий project;
- проверить thread capabilities и git/worktree preconditions;
- владеть DAG, scheduling, retries, integration и final verdict;
- проверять все worker claims по source/commit/artifacts;
- не передавать worker-задаче право создавать другие mission tasks;
- разрешать node-local fan-out только для nodes с `execution: lazy`.

### 2. Двухуровневая оркестрация

Разрешены ровно два orchestration ownership boundary:

```text
Уровень 1: mission coordinator
└─ владеет peer-задачами, DAG, dependencies, integration и final gate

Уровень 2: main thread отдельной peer-задачи (node lead)
└─ при execution: lazy владеет локальными qtim subagents этой node
   └─ subagents не делегируют дальше
```

Peer-задача является самостоятельным main thread Codex, поэтому может выполнять
`$qtim-team-lazy`, не получая права управлять mission graph. Это не рекурсивная
команда: coordinator не видит локальные роли как DAG nodes, а node lead возвращает
наружу один агрегированный receipt.

`execution` каждой node задаётся в утверждённом mission spec:

```yaml
concurrency:
  policy: demand-driven
  overflow: runtime-waves

execution: direct | lazy
lazy:
  rolePolicy: minimum-sufficient
  leadProfile:
    model: gpt-5.6-sol
    reasoning: ultra
    approvedIn: mission-preview
  allowedRoles: [qtim-architect, qtim-testing]
  writeScopes:
    qtim-architect: []
    qtim-testing: [".github/scripts/check_example.py"]
  escalation: return-to-mission-coordinator
```

Правила `execution: lazy`:

- node должна быть высокоуровневой, но bounded: один outcome, один owner, один
  worktree и один node receipt;
- lazy выбирается, если работа пересекает несколько concerns и укладывается в один
  проход без implement -> test -> fix loop;
- node lead читает `$qtim-team-lazy`, выбирает только нужные роли и сам проверяет
  их claims;
- direct nodes используют configured default и не получают model override;
- lazy node lead получает `gpt-5.6-sol` + `ultra` только после явного approval
  профиля в mission preview или Approved mission spec. Это approval разрешает
  coordinator передать `model` + `thinking` в `create_thread`;
- если Approved profile отсутствует или destination host отклоняет пару, node
  остаётся в `PREVIEW`/`Blocked`; переход в `direct` требует явного изменения spec;
- каждая local role явно объявляет `write_policy: writer | read-only`; writer
  получает непустые `write_scopes`, read-only — ровно пустые `write_scopes: []`
  и явные `read_scopes`; falsey scope всегда отклоняется;
- локальные writers получают непересекающиеся scopes внутри общего node worktree;
- локальный subagent не вызывает `$qtim-team-lazy`, `$qtim-team-up`,
  `$qtim-mission` и не создаёт peer-задачи;
- если появляется полноценная feedback loop, node lead возвращает
  `ESCALATION_REQUEST`; только mission coordinator решает, разрезать node, создать
  fix/review nodes или запросить изменение графа;
- feedback/product-fork/new-role/scope-overlap escalation всегда возвращает
  `status: BLOCKED`; `SUCCEEDED` escalation не валидируется и не разблокирует
  downstream; в обратную сторону любой `ESCALATION_REQUEST` требует `BLOCKED`;
- coordinator не вводит hard cap на количество peer-задач или local agents и не
  заявляет, что видит live descendants внутри другой peer-задачи;
- каждая node получает минимально достаточный набор ролей по реальному scope, а не
  фиксированный roster и не числовую квоту;
- coordinator запускает все ready peer nodes, которые принимает runtime. Node lead
  запускает все нужные роли, которые помещаются в фактический per-session cap;
- оставшиеся ready nodes/roles выполняются следующими waves. Недоступный slot меняет
  порядок, но не удаляет нужную роль и не создаёт дополнительную глубину nesting.

### 3. Mission specification

Portable канон:

```text
memory/missions/<slug>/
├─ mission.md          # цель, scope, non-goals, base, DAG, budgets
├─ receipts.md         # проверенные результаты nodes
├─ decisions.md        # mission-local развилки и решения
└─ verification.md     # project gates, reviewer findings, verdict
```

`mission.md` содержит:

- mission id и human title;
- project/repository identity без machine-specific абсолютных путей;
- base revision или явно утверждённый working-tree snapshot;
- acceptance criteria и global verification commands;
- node list, dependency edges и total exact edge-contract map (`evidence |
  integrated`) без missing/extra/unknown entries;
- read/write scope каждой node;
- execution policy `direct | lazy`, role policy и обоснованный набор local roles;
- expected artifact/receipt;
- retry budget и stop conditions;
- integration order;
- status `Draft | Approved | Running | Blocked | Verifying | Done | Stopped`.

### 4. Runtime registry

Рекомендуемый локальный слой:

```text
.codex/qtim-runtime/missions/<slug>.json
```

Минимальные поля:

```json
{
  "schemaVersion": 1,
  "missionId": "example",
  "status": "running",
  "projectId": "opaque",
  "integrationWorktreeTarget": "opaque",
  "stateTarget": "codex/qtim-mission-state-example",
  "stateWorktreeTarget": "opaque",
  "stateSequence": 4,
  "ownership": {
    "coordinatorThreadId": "opaque",
    "hostId": "opaque",
    "generation": 1
  },
  "refJournal": {
    "sequence": 7,
    "authorizedTransitions": {}
  },
  "nodes": {
    "a": {
      "status": "running",
      "executionMode": "lazy",
      "rolePolicy": "minimum-sufficient",
      "threadId": "opaque",
      "hostId": "opaque",
      "waitCursor": "opaque",
      "attempt": 1
    }
  },
  "updatedAt": "RFC3339"
}
```

Правила:

- ids/cursors всегда opaque: не конструировать и не преобразовывать;
- registry — last-known hints, а не доказательство live state;
- перед `wait`, follow-up, handoff или resume handle проверяется через runtime;
- coordinator — единственный writer registry; owner/generation проверяется перед
  каждым fan-out и Git promotion;
- `.codex/qtim-runtime` и portable `memory/missions/<slug>` проходят
  component-wise lstat/realpath containment: real directories, без symlink/
  junction, внутри exact worktree. Registry/temp/ownership lock adjacent и на
  одном filesystem; unsafe layout даёт `unavailable` без external write;
- missing first-run parents создаются от exact root по одному component с
  post-create lstat/realpath/same-filesystem revalidation; unverified recursive
  `mkdir -p` запрещён. Initial registry под canonical ownership lock использует
  exclusive adjacent temp, file fsync, atomic no-clobber publication,
  parent-directory fsync и exact final read. Existing registry/temp collision
  даёт `ambiguous`, недоказанный host primitive — `unavailable`;
- другой coordinator получает ownership только по explicit resume, после
  подтверждённого non-running прежнего owner, получения exclusive ownership
  lock, повторного чтения generation под lock, file `fsync + atomic replace` и
  parent-directory fsync; до снятия lock final read требует exact regular
  single-link registry с mission/new owner/host/new generation;
- canonical siblings строго равны `<slug>.json`, `<slug>.ownership.lock` и
  `<slug>.promotion.lock`. Promotion lock bind-ит owner token, generation и
  integration target; caller-chosen альтернативные locks запрещены;
- переходы записываются после подтверждённого tool result;
- raw baseline снимается после registry init + owner reread. Из сравнения можно
  исключить только exact current-mission registry file по coordinator-owned
  before/after fingerprint journal и final JSON read owner/host/generation;
  parent directories, sibling/foreign runtime files остаются frozen;
- coordinator-owned ref journal передаётся validator отдельно от worker receipt и
  допускает только exact state checkpoint текущей mission. State ref не
  удаляется/пересоздаётся; integration ref frozen
  на активную writer wave;
- promotion получает locks только `ownership -> promotion` и перечитывает
  owner/generation под обоими непосредственно перед CAS;
- runtime state не коммитится; gitignore/ownership решается ADR;
- portable transition получает следующий `stateSequence` и scoped checkpoint
  commit только по `memory/missions/<slug>/` до следующего external side effect;
  partial state diff после crash блокирует resume;
- повреждённый registry не приводит к угадыванию handles: восстановление через
  `list_threads`, mission markers и подтверждение пользователя при неоднозначности.

### 5. Node state machine

```text
pending
  -> ready
  -> creating
  -> running
  -> needs_input | failed | succeeded
  -> validated
     -> verified                         (read-only node)
     -> integrated -> verified           (writer node)
```

Дополнительные терминальные состояния:

- `blocked` — зависимость/approval/runtime gap;
- `cancelled` — остановлено пользователем;
- `superseded` — заменено новой attempt/fix node.

Недопустимые переходы отклоняются. `succeeded` от worker не равно `validated`;
Read-only ветка: `validated -> verified (read-only)`. Writer-ветка:
`validated -> integrated -> verified (writer)`. `validated` не равно
`integrated`; `integrated` не равно `verified`.

### 6. DAG scheduler

Алгоритм:

1. Проверить acyclic graph и уникальность node ids.
   До формирования path/ref/marker потребовать `slug == missionId`; mission и
   node ids — lowercase ASCII kebab длиной 1–64 без separators/colon/dot/control
   и option/alias forms. Проверить уникальность markers
   `qtim:<missionId>:<nodeId>`, exact derived state ref и отдельный canonical
   integration `refs/heads/*` через `git check-ref-format`; integration target не
   D/F-conflict-ит с reserved state namespace. Writer App worktree detached и не
   создаёт shared attempt ref.
2. Проверить total exact edge-contract map; overlapping writer scopes требуют
   прямой `integrated` edge. Затем найти `ready`: все dependencies имеют
   `validated` или `integrated` согласно edge contract.
3. Создать все ready nodes, которые принимает runtime; остальные оставить `ready`
   и запустить следующей wave.
4. Git writer task стартует только preflight-only без edits/commit. После
   `WRITER PREFLIGHT READY` coordinator reconciles всю wave, проверяет detached
   exact base/clean/refs, снимает post-create admin/filesystem/submodule
   baselines и только exact follow-up marker+attempt авторизует запись.
   До этого state `preflight-ready`; без callable follow-up writer mode
   `unavailable`.
5. Для direct node не задавать model/thinking в `create_thread`. Для lazy node
   передать Sol/Ultra только если exact pair явно утверждена в mission preview или
   Approved spec; иначе перевести запуск в `PREVIEW`.
6. Передать `execution: lazy`, role policy и обоснованные scopes в initial prompt
   только для одобренной lazy node.
7. Обработать `threadId` немедленно или reconciliation `clientThreadId`.
8. Назвать задачу `qtim:<mission-id>:<node-id>`.
9. Ждать targets batches до восьми, сохраняя cursors.
10. При `needs_input` не отвечать за пользователя: показать нужную задачу и вопрос.
11. После completion прочитать bounded result, проверить receipt и только затем
    разблокировать downstream nodes.

### 7. Worker prompt и receipt

Initial prompt содержит только bounded context:

Для writer это сначала отдельный preflight-only prompt: никаких edits/commit;
вернуть READY после detached exact base, clean including untracked и unchanged
refs. Следующий bounded prompt приходит только exact follow-up после baseline.

```text
Mission: <mission-id>
Node: <node-id>
Coordinator owns the mission graph. Never create peer tasks or another qtim mission.
Execution: direct | lazy
If lazy: invoke $qtim-team-lazy for this node only. Select every role materially
needed for the acceptance criteria; do not add roles without a concrete responsibility.
Local subagents must not delegate further. Return escalation to the coordinator.

Read first:
1. AGENTS.md
2. .codex/team-charter.md
3. <role-specific memory/artifacts>

Base: <revision/snapshot>
Dependencies: <validated context pack>
Scope: <files/layer/behavior>
Write policy: read-only | isolated worktree writer
Lazy policy: <minimum-sufficient roles, local write scopes, or not allowed>
Acceptance criteria: <node criteria>
Verification: <commands/evidence>

Return WORKER RECEIPT only after checking real artifacts.
```

Receipt:

```text
WORKER RECEIPT
mission/node:
status: SUCCEEDED | BLOCKED | FAILED
base revision:
changed files:
commit SHA: <writer only>
artifacts:
verification commands/results:
dependency outputs consumed:
execution used: direct | lazy
local roles used: <none | bounded list>
local results checked by node lead:
open blockers:
escalation request:
handoff summary:
```

Coordinator не доверяет receipt автоматически:

- проверяет commit принадлежность ожидаемому base/worktree;
- открывает changed files или artifacts;
- сверяет commands и result;
- прогоняет writer/lazy/spec scopes через единый canonical safe repo-relative
  parser до containment/overlap check;
- отклоняет raw backslash, drive/UNC/scheme, ASCII/Unicode control,
  basic/extended glob, `$HOME`/`%USERPROFILE%`/`~user`, component-wise
  case-folded `.git`/trailing-dot aliases, Windows
  `CON/PRN/AUX/NUL/COM1..9/LPT1..9`, traversal и option-like aliases;
- считает NFC/case-fold aliases пересечением и отклоняет target scope при
  symlink/junction component или realpath escape;
- проверяет, что каждая поднятая роль нужна acceptance criteria, а scopes не
  пересекаются; отсутствие числового cap не разрешает декоративный fan-out;
- отклоняет output, вышедший за scope;
- для Git read-only target требует canonical expected commit, exact
  `HEAD == expected revision`, пустой tree diff и clean status с untracked
  files с `GIT_OPTIONAL_LOCKS=0`, exact raw filesystem
  type/mode/device/inode/link-count/bytes fingerprint; exact pre/post protected refs (кроме
  runtime-owned ephemeral `refs/codex/*`), local common-config и common-control
  плюс root `.git`/resolved git-dir/common-dir, per-worktree Git admin (`HEAD`,
  raw index, config.worktree, sparse metadata, operation heads/log) и весь
  common `.git/worktrees/*` registry snapshots сравниваются. Common-control
  включает `packed-refs` и real identity roots
  `objects/refs/logs/info/hooks/modules`, поэтому
  assume-unchanged bytes/index flags,
  committed/shared-ref/config/hooks drift отклоняется даже при clean status;
- для writer требует unchanged shared refs и допускает только отдельно
  coordinator-journaled state checkpoint текущей mission; state delete/recreate,
  integration/foreign drift запрещены;
- требует strict true для detached `HEAD == commit`, clean including untracked,
  filesystem == commit tree, single-link regular content, contained scopes,
  unchanged common Git config/control и green node gates. Writer post-create
  baseline фиксирует exact admin identity, frozen controls, assigned wave
  entries, canonical index flags и initialized/uninitialized submodule state
  вместе с nested common config/control/hooks/packed-refs; foreign/extra admin
  paths frozen;
- raw filesystem preflight ограничен 50 000 entries / 512 MiB regular bytes;
  FIFO/socket/device, root/directory junction и превышение бюджета блокируют
  fan-out; реальные Windows junctions проверяются отдельным CI fixture;
- сохраняет только подтверждённое резюме в `receipts.md`.

### 8. Dependency handoff

Downstream context pack включает:

- подтверждённый outcome upstream node;
- commit/artifact identifiers;
- изменившиеся контракты;
- обязательные инварианты и unresolved blockers;
- запрещённые интерпретации;
- точные acceptance criteria downstream node.

Полные transcripts не передаются. Result task считается недоверенным входом до
проверки coordinator.

### 9. Code integration

Root writer создаётся от mission base. Downstream writer создаётся от exact
текущего Approved integration HEAD после всех integrated code dependencies; этот
SHA становится immutable per-attempt `expectedBase`.

Реализованный v1 контракт:

1. Worker создаёт один bounded commit без чужих изменений.
2. Coordinator проверяет commit и node gates.
3. От текущего Approved integration HEAD создаётся disposable detached
   transaction worktree без shared transaction ref; `cherry-pick` выполняется
   только там и строго topologically.
4. Минимальный affected gate запускается в transaction worktree.
5. Green gate разрешает fenced compare-and-swap promotion только из clean
   integration worktree: coordinator требует canonical full 40/64-hex commits,
   получает canonical locks строго `ownership -> promotion`, перечитывает
   owner/generation под обоими, повторно проверяет exact old Approved target/HEAD
   и ff-only ancestry, требует exact symbolic attachment
   worktree к `refs/heads/<Approved target>`, атомарно выполняет exact-target-ref
   CAS, синхронизирует transaction tree и независимо проверяет target ref + HEAD
   + clean status. Detached/wrong-branch worktree отклоняется. Ошибка после CAS
   требует доказанного rollback target ref/tree, иначе состояние `ambiguous`;
   dirty state, drift/занятый lock блокируют promotion. Red gate оставляет
   Approved target неизменным.
6. При конфликте transaction cherry-pick abort-ится; conflict-fix становится
   отдельной Approved node.

ADR-001 выбрал coordinator-managed transactional cherry-pick. Native
`handoff_thread` остаётся UX/recovery primitive и не используется как DAG merge.
Portable `memory/missions/<slug>/` обновляется монотонными scoped checkpoint
commits в отдельной clean state branch/worktree, поэтому evidence не загрязняет
Git gate и не меняет writer `expectedBase`. После final `APPROVED` последний
checkpoint доставляется одним scoped evidence bundle commit через тот же fenced
promotion. После подтверждённой exact delivery следующий монотонный state
checkpoint записывает `Done`, новый `stateSequence` и
`deliveredEvidenceRevision`; это canonical 40/64-hex Git object id, совпадающий
с независимо перечитанным promoted HEAD; обе revisions разрешаются как commits.
Crash между promotion и checkpoint остаётся
`Verifying` и восстанавливается идемпотентно после проверки exact
revision/subtree; mismatch блокирует resume.

Shared-checkout parallel writers запрещены даже при разных диалогах.

### 10. Final verification gate

После интеграции всех обязательных nodes:

Mission содержит минимум две content nodes. `terminalVerifier` заранее описан в
Approved spec как reserved gate, его `dependsOn` в точности перечисляет все
required content nodes; пустой или частичный список запрещён. Verifier не
является обычной content node и не участвует в general ready waves. Final phase
создаёт ровно одну отдельную clean-context task только после terminal state всех
required outcomes и зелёных global gates.

1. Coordinator запускает полный project validation.
2. Фиксирует integrated revision и verification context pack.
3. Создаёт отдельную clean-context read-only verification-задачу.
4. Verifier проверяет:
   - mission acceptance criteria;
   - dependency contracts;
   - фактический integrated diff;
   - tests/build/typecheck/browser evidence;
   - security/public-contract/generated-state gates;
   - отсутствие unrelated edits.
5. Coordinator подтверждает или отклоняет каждый finding по source.
   Verdict читается только как exact full-line `verdict: APPROVED` или
   `verdict: NOT APPROVED`; indentation, tabs, лишние пробелы и malformed suffix
   отклоняются, после colon допустим ровно один ASCII space, последняя exact
   запись является итоговой.
6. `NOT APPROVED` создаёт fix nodes с ограниченным scope.
7. После fixes повторяются affected gates и clean verification.
8. Loop ограничен mission retry budget; exhausted budget -> `Blocked`, не ложный Done.
9. `APPROVED` записывается в `verification.md` и checkpoint-ится в state worktree.
10. Последний clean checkpoint доставляется одним scoped evidence bundle commit
    через transaction gate/fenced promotion.
11. После подтверждения exact delivered subtree следующий clean scoped checkpoint
    фиксирует `status: Done`, новый `stateSequence` и exact
    `deliveredEvidenceRevision`, проверенный как canonical 40/64-hex commit.
    Crash-window reconciliation делает этот шаг
    один раз; уже совпавший checkpoint — no-op, mismatch — `Blocked`.

Final mission verification не заменяет обязательный ADR stress-test и risk-based
independent review из charter.

## Вертикальные этапы реализации

### Этап 0 — ADR и runtime probes

Размер: M
DRI: architect
Зависимости: нет

Решить и проверить:

- portable/runtime state split и gitignore ownership;
- handoff против commit integration;
- reconciliation `clientThreadId -> threadId`;
- отдельная clean state branch/worktree с scoped checkpoint commits и crash
  reconciliation;
- transactional promotion после affected gate под exclusive lock с
  exact-old/ff-only/exact-final checks;
- coordinator takeover generation под ownership lock с file
  `fsync + atomic replace + parent-directory fsync`;
- граница поддерживаемых поверхностей App/CLI/IDE;
- модель peer-задач: configured default для direct и явный Approved override для
  lazy node leads;
- nested delegation contract: два уровня ownership, demand-driven fan-out и
  runtime waves по фактическим caps.

Артефакты:

- ADR;
- `$qtim-grill`;
- обязательный clean-context Sol stress-test;
- обновление `reference/runtime-compat.md`;
- reproducible App probe receipt.

Gate: ни один runtime assumption не остаётся только предположением.

### Этап 1 — Read-only mission MVP

Размер: L
DRI: main implementation owner
Contributors: architect, testing

Сделать:

- `plugins/qtim/skills/qtim-mission/SKILL.md`;
- UI metadata;
- user-facing quick start, practical-use guide и activation contract
  `AUTO-START | PREVIEW | RECOMMEND`;
- обязательный `$qtim-feature` completion block «Что запускать дальше»;
- shape-based routing и готовую команду для direct/team-lazy/team-up/mission;
- mission spec и receipt reference;
- capability detection;
- list project -> create two read-only tasks -> wait -> validate receipts;
- DAG `A -> B`;
- bounded dependency context pack;
- final read-only synthesis без code integration;
- semantic fixtures: явный запуск активирует workflow, упоминание/цитата/отрицание
  и режим `RECOMMEND` не создают peer-задачи;
- routing fixtures: M feature с независимыми producer/consumer outcomes получает
  mission recommendation, а XL feature с одним feedback loop — team-up.

Smoke scenario:

```text
A: проанализировать hooks contract
B: используя подтверждённый результат A, проверить migration implications
Final: сопоставить оба результата с charter
```

Gate: B не создаётся до validated receipt A; отсутствие thread tools даёт честный
fallback; завершение feature возвращает объяснённую рекомендацию и точную команду,
но не создаёт задачи.

### Этап 2 — Node-local lazy team

Размер: L
DRI: orchestration contract owner
Contributors: architect, testing

Сделать:

- `execution: direct | lazy` в mission spec и runtime state;
- mission-child режим в `$qtim-team-lazy`;
- явную передачу lazy authorization, allowed roles и local write scopes;
- явное approval Sol/Ultra pair в Preview/Approved spec и передачу exact pair в
  `create_thread`;
- demand-driven scheduler без plugin hard cap на число peer tasks/local agents;
- проверку `minimum-sufficient`: у каждой поднятой роли есть concrete responsibility
  и expected output;
- проверку фактического per-session cap силами node lead;
- агрегированный receipt с local roles и проверкой node lead;
- `ESCALATION_REQUEST` вместо запуска node-local `$qtim-team-up`;
- semantic guard против третьего уровня fan-out.

Smoke scenario:

```text
A (execution: lazy, read-only):
  node lead выбирает architect + testing
  -> проверяет два role reports
  -> возвращает один A receipt
B:
  стартует только после validation агрегированного A receipt
```

Gate: высокоуровневая node действительно использует локальный `$qtim-team-lazy`,
но ни node lead, ни его subagents не создают peer mission tasks; все необходимые
роли либо выполнены, либо явно поставлены в runtime waves.

### Этап 3 — Isolated writer и integration

Размер: L/XL, при росте разрезать
DRI: implementation owner
Contributors: architect, testing, reviewer

Сделать:

- git preflight и base capture;
- writer task в worktree;
- commit receipt;
- commit/handoff validation;
- transactional integration через disposable worktree и `--ff-only` promotion;
- conflict node;
- affected gate до promotion Approved branch;
- запрет shared-checkout parallel writers.

Smoke scenario:

```text
A: изменить независимый reference doc от mission base
Transaction A -> gate -> promote A
B: изменить validator fixture от integrated A
Transaction B -> gate -> promote B
```

Gate: в Approved integration worktree появляются только commits с зелёным gate;
portable evidence живёт отдельно, red gate не сдвигает Approved HEAD, конфликт не
перезаписывается автоматически.

### Этап 4 — Общий verification loop

Размер: M/L
DRI: reviewer contract owner
Contributors: testing

Сделать:

- clean-context verification task;
- deterministic APPROVED/NOT APPROVED contract;
- confirmed/rejected findings;
- bounded fix nodes;
- final completion marker;
- `verification.md`.

Gate: worker success без общего verifier никогда не превращается в mission Done.

### Этап 5 — Resume, status и recovery

Размер: L
DRI: implementation owner
Contributors: testing

Сделать:

- `$qtim-mission, status`;
- `$qtim-mission, resume <slug>`;
- runtime handle verification;
- coordinator owner/generation takeover с exclusive ownership lock, повторным
  чтением generation и atomic replace;
- reconstruction через `list_threads`;
- stale/orphan/ambiguous classifications;
- SessionStart advisory о незавершённой mission;
- mission checks в `$qtim-doctor`;
- stop flow без удаления чужих tasks или portable evidence.

Gate: новая coordinator-задача либо безопасно продолжает миссию, либо показывает
точный recovery blocker; она не угадывает thread ids.

### Этап 6 — Release и generated-state migration

Размер: M
DRI: maintainer
Contributors: testing, reviewer

Изменить:

- plugin manifest: следующий свободный minor после текущего 2.11.0;
- `README.md`, skill table и quick start;
- `CHANGELOG.md`;
- `reference/upgrade-notes.md`;
- setup/update/doctor contracts;
- generated charter и `memory/MEMORY.md`, если mission layout становится частью
  target-project state;
- validators и semantic golden;
- `reference/runtime-compat.md`.

Gate: все repo-local проверки и `validate_plugin.py plugins/qtim` зелёные; новая
Codex task видит `$qtim-mission`.

## Предполагаемый file map

Новые:

- `plugins/qtim/skills/qtim-mission/SKILL.md`
- `plugins/qtim/skills/qtim-mission/agents/openai.yaml`
- `plugins/qtim/reference/mission-protocol.md`
- `plugins/qtim/reference/mission-receipt.md`
- `plugins/qtim/reference/mission-state-schema.md`
- `.github/scripts/check_missions.py`

Изменяемые:

- `plugins/qtim/.codex-plugin/plugin.json`
- `plugins/qtim/skills/qtim-setup/SKILL.md`
- `plugins/qtim/skills/qtim-update/SKILL.md`
- `plugins/qtim/skills/qtim-doctor/SKILL.md`
- `plugins/qtim/skills/qtim-feature/SKILL.md`
- `plugins/qtim/skills/qtim-team-lazy/SKILL.md`
- `plugins/qtim/skills/qtim-team-down/SKILL.md`
- `plugins/qtim/reference/intake-protocol.md`
- `plugins/qtim/reference/model-profiles.md`
- `plugins/qtim/reference/orchestration-patterns.md`
- `plugins/qtim/reference/runtime-compat.md`
- `plugins/qtim/reference/upgrade-notes.md`
- `plugins/qtim/hooks/hooks.json`
- `.github/scripts/check_skills.py`
- `.github/workflows/validate.yml`
- `README.md`
- `CHANGELOG.md`

Точный список сокращается после ADR. В частности, team-down не должен поглотить
mission lifecycle, если это размоет его текущий subagent-only контракт.

## Validation matrix

| Case | Ожидаемый результат |
|---|---|
| App tools доступны, git project clean | Full mission mode, writer worktrees |
| App tools доступны, dirty checkout | Blocking base/snapshot decision до writers |
| `create_thread` вернул `clientThreadId` | Reconciliation или fail-visible pending |
| Нет peer thread tools | Предложен team-up fallback, peer tasks не заявлены |
| Non-git project, read-only nodes | Допустим peer read-only mode |
| Non-git project, несколько writers | Blocked или строго single-writer mode |
| A зависит от B и B от A | DAG validation fail до создания задач |
| Worker вышел за write scope | Receipt rejected, integration не выполняется |
| Worker требует approval | Mission `Needs input`, решение оставлено пользователю |
| Thread disappeared | Verify/list recovery, затем respawn или explicit blocker |
| Два commits конфликтуют | Отдельная conflict node, никакого force overwrite |
| Verifier нашёл P1 | NOT APPROVED, bounded fix node |
| Retry budget исчерпан | Mission Blocked, не Done |
| Resume на другом/недоступном host | Portable state сохранён, runtime recovery честно unavailable |
| Чужой похожий thread title | Не управлять без id/project/marker confirmation |
| Явный запуск + `Approved` artifact + зелёный preflight | `AUTO-START`, без второго checkpoint |
| Явный запуск + raw goal или открытый Fork Test | `PREVIEW`, ни одной peer-задачи до подтверждения |
| Mission-worthy план найден другим qtim workflow | Только `RECOMMEND`, без `create_thread` |
| Skill упомянут в цитате, вопросе или отрицании | Workflow не активируется |
| Running node требует approval/permission | Mission `Needs input`, coordinator не отвечает за пользователя |
| Approved node имеет `execution: lazy` и зелёный Sol/Ultra preflight | Node lead вызывает локальный `$qtim-team-lazy` |
| Lazy node пересекает несколько concerns, но не требует feedback loop | Выбраны только нужные роли, наружу возвращён один receipt |
| Lazy node потребовала implement -> test -> fix loop | `ESCALATION_REQUEST` coordinator, не node-local team-up |
| Ready peer nodes больше текущей runtime capacity | Запустить принятые nodes, остальные оставить `ready` для следующей wave |
| Нужных local roles больше фактического per-session cap | Выполнить роли локальными waves; не отбрасывать и не создавать третий уровень |
| Node lead поднял роль без concrete responsibility | Receipt rejected как декоративный fan-out |
| Local subagent пытается создать peer task или qtim descendant | Нарушение контракта, node receipt отклонён |
| Approved feature имеет один outcome и feedback loop | Рекомендован `$qtim-team-up` с объяснением и командой; ничего не запущено |
| Approved feature имеет producer -> consumer и отдельные outcomes | Рекомендован `$qtim-mission` с topology и командой; ничего не запущено |
| M и XL features имеют одинаковую execution topology | Выбран одинаковый workflow; размер влияет на декомпозицию, не на тип оркестрации |

## Acceptance criteria

1. Явный `$qtim-mission` может создать минимум две видимые peer-задачи Codex App.
2. Создаются только nodes, ставшие ready по валидному acyclic DAG.
3. Каждая созданная задача имеет уникальный mission/node marker и bounded prompt.
4. Worker не получает право создавать peer mission tasks; lazy node lead может
   создать только явно разрешённых локальных subagents.
5. Downstream node получает только проверенный dependency context pack.
6. Read-only и writer policies механически/процедурно разделены.
7. Каждый writer изолирован worktree и возвращает проверяемый commit receipt.
8. Integration последовательна и прекращается при конфликте или scope violation.
9. Worker `SUCCEEDED` не считается общим успехом до final verifier.
10. Final verifier работает в отдельной clean-context read-only задаче.
11. Каждый finding verifier проверяется coordinator по фактическому source.
12. `Done` записывается последним durable checkpoint только после зелёных gates,
    `APPROVED` и подтверждённой fenced delivery точного final evidence bundle;
    checkpoint хранит exact `deliveredEvidenceRevision`.
13. Runtime state можно проверить и восстановить на поддерживаемой поверхности.
14. Потерянный handle, unavailable tool или failed worker не маскируется как success.
15. Workflow не меняет model/thinking peer-задачи без явного пользовательского выбора.
16. Workflow не подтверждает approvals и продуктовые развилки вместо пользователя.
17. Mission stop не удаляет и не архивирует чужие задачи.
18. CLI/IDE fallback назван fallback и не обещает отдельные диалоги.
19. Generated-state migration сохраняет foreign content, track blocks и user overrides.
20. Repo validation, mission fixtures, plugin validation и App smoke matrix проходят.
21. README и skill объясняют практическую пользу, подходящие/неподходящие кейсы,
    новый запуск, `status`, `resume` и `stop`.
22. `AUTO-START` возможен только после явного разрешения и зелёного preflight
    утверждённого графа.
23. `PREVIEW` не вызывает `create_thread` до подтверждения пользователя.
24. `RECOMMEND`, SessionStart, цитата, вопрос и отрицание никогда не создают
    peer-задачи.
25. Высокоуровневая node с `execution: lazy` вызывает `$qtim-team-lazy` и возвращает
    один агрегированный, проверенный node receipt.
26. Число peer tasks и local agents определяется задачей, а не plugin hard cap;
    превышение runtime capacity обрабатывается waves.
27. Local subagents не создают descendants, peer-задачи или новую mission.
28. Lazy node с feedback loop эскалирует решение coordinator вместо скрытого
    перехода в node-local `$qtim-team-up`.
29. Каждая завершённая Approved `$qtim-feature` содержит блок «Что запускать дальше».
30. Routing выбирает workflow по outcomes, dependencies, context/worktree isolation
    и feedback loops, а не только по размеру.
31. Recommendation содержит выбранный workflow, краткое объяснение, topology,
    готовую команду запуска и допустимую альтернативу.
32. Один связный outcome маршрутизируется в direct/team-lazy/team-up; несколько
    самостоятельных outcomes или A -> B — в mission.
33. Feature completion, размер `L/XL` и режим `RECOMMEND` не запускают subagents или
    peer-задачи без явного разрешения пользователя.
34. Edge-contract map точно покрывает DAG; overlapping writer scopes
    сериализованы прямым `integrated` edge.
35. App writer проходит no-edit `preflight-ready -> exact follow-up`, остаётся
    detached от exact `expectedBase` до commit и не создаёт shared attempt ref;
    без callable follow-up writer mode unavailable.
36. Coordinator-owned ref journal не доверяет worker receipt и разрешает только
    exact state checkpoint текущей mission; integration/foreign refs frozen.
37. Raw filesystem/common-control proof включает type/mode/topology/bytes,
    non-refreshing Git reads, exact `.git` identity, common-worktree + registry
    journals, no-clobber first-run registry init, single-link writer content,
    frozen admin/index и nested submodule control baselines; он ограничен budget
    и fail-closed на special files, hardlink/symlink/junction escapes и
    case/Unicode aliases. Реальные Windows junctions покрыты CI.
38. SessionStart не объявляет authoritative Done state-ref mission незавершённой.

## Риски

### App-only tool surface

Риск: `$qtim-mission` окажется непереносимым в CLI/IDE.

Мера: capability detection, App-first support label и явный single-task fallback.

### Peer tasks не являются subagents

Риск: пользователь ожидает скрытую иерархию и автоматическое наследование контекста.

Мера: видимые titles, bounded prompts, coordinator-owned graph и documentation.

### Асинхронное создание worktree

Риск: `clientThreadId` нельзя использовать в wait/read/send.

Мера: runtime probe и deterministic reconciliation до production skill; если это
невозможно — v1 ограничивает создание состояниями, которые сразу возвращают threadId.

### Git integration

Риск: conflicts, dirty checkout, red affected gate после cherry-pick и случайный
перенос чужих изменений.

Мера: captured base, isolated commits, scoped checkpoint state worktree, clean
integration worktree, transaction gate и exclusive promotion lock с
exact-old/ff-only/exact-final checks, scope validation и отдельные conflict nodes.

### Нестабильные/недоверенные worker outputs

Риск: downstream получает неверное утверждение как факт.

Мера: receipt contract, source verification и минимальный context pack.

### Раздувание состояния и UX

Риск: mission создаёт слишком много задач и файлов.

Мера: explicit concurrency/task budget, wave scheduling, один public skill, optional
cleanup и portable/runtime state split.

### Ошибочная маршрутизация по размеру

Риск: любая XL feature автоматически превращается в mission, а небольшая задача с
настоящей producer -> consumer зависимостью остаётся без нужной координации.

Мера: `$qtim-feature` классифицирует execution topology по outcomes, dependencies,
изоляции и feedback loops. Размер влияет на декомпозицию и стоимость, но никогда не
является единственным триггером workflow или authorization.

### Взрыв вложенного fan-out

Риск: несколько peer-задач одновременно поднимут lazy teams, резко увеличат расход,
начнут конкурировать за файлы или создадут непредсказуемую рекурсию.

Мера: ровно два ownership level; demand-driven `minimum-sufficient` roster; один
worktree на node; disjoint local write scopes; runtime caps превращают fan-out в
waves; node-local team-up запрещён, escalation возвращается mission coordinator.

### Неподходящий профиль node lead

Риск: peer-задача получает высокоуровневую lazy node, но запущена не на обязательном
`gpt-5.6-sol` + `ultra` и не может честно выполнять роль team lead.

Мера: direct node использует configured default. Exact Sol/Ultra pair для lazy node
становится частью явно утверждённого mission preview/spec, после чего coordinator
имеет право передать `model` + `thinking` в `create_thread`. Без такого approval
node остаётся в `PREVIEW`/`Blocked`; скрытой замены и ложного lazy mode нет.

## Решения и рекомендуемая финализация

1. **State ADR — согласовано:** `.codex/qtim-runtime/` — локальный некоммитируемый
   слой; `memory/missions/` — portable evidence.
2. **Integration ADR — согласовано:** bounded commits в topological order; handoff
   проверяется probe-ом и не является основным v1 transport без evidence.
3. **Surface contract — согласовано:** App-first full mode + честный CLI/IDE fallback.
4. **Model contract — согласовано:** direct peer tasks используют configured default;
   никакого общего скрытого override.
5. **Cleanup contract — согласовано:** worker-задачи остаются видимыми; archive только
   после отдельного подтверждения.
6. **Nested lazy contract — согласовано:** ровно два ownership level; количество
   peer tasks и local agents определяется scope и acceptance criteria без plugin
   hard cap; scheduler поднимает минимально достаточные роли и при фактическом
   runtime limit выполняет их waves; node-local `$qtim-team-up` и третий уровень
   запрещены.
7. **Lazy node profile — согласовано для 2.12:** lazy node lead — исключение из
   общего default-model правила. Exact `gpt-5.6-sol` + `ultra` показывается в Preview
   и один раз явно утверждается пользователем; Approved spec сохраняет это разрешение,
   поэтому AUTO-START не требует повторного вопроса. Недоступная pair -> `Blocked`,
   не скрытый fallback.

Отдельный согласованный product contract: каждая Approved `$qtim-feature`
рекомендует direct, team-lazy, team-up или mission по форме работы, показывает
объяснение и готовую команду, но остаётся read-only до явного «Запускай
предложенное».

Реализация v1 следует этим решениям. Исторический App smoke подтвердил
read-only/lazy/two-writer/recovery surface; fresh smoke 2026-07-29 дополнительно
прошёл live `WRITER PREFLIGHT READY -> coordinator baseline -> exact follow-up
-> bounded detached writer receipt`. Свежие `$qtim-grill` и clean-context
independent review финального snapshot вернули `PASS`; остаются один
conventional commit и push.
Полный локальный repository suite и официальный plugin validator зелёные на
snapshot 2026-07-29.
