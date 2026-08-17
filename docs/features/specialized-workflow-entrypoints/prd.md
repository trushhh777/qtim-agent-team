Feature: Специализированные workflow-входы qtim
Slug: specialized-workflow-entrypoints
Status: Draft
Дата: 2026-07-27

# PRD

## Контекст

qtim уже даёт общие режимы delivery (`$qtim-team-lazy`, `$qtim-team-up`), дисциплину диагностики (`$qtim-debug-loop`) и проектный roster ролей. Однако для пяти повторяющихся намерений — security review, починки build/CI, contract review, измеренной оптимизации и TDD — пользователь пока должен сам собирать последовательность действий, write-boundary, роли, gates и формат результата.

Фича добавляет пять самостоятельных, явно вызываемых Codex skills. Это orchestration-входы поверх существующих ролей и инвариантов, а не новые постоянные агенты и не замена общим командным режимам.

Источник утверждённого scope: `docs/features/specialized-workflow-entrypoints/intake.md`.

## Цели

1. Дать Developer и Project owner / decision owner пять discoverable входов с понятным условием выбора.
2. Сделать каждый workflow воспроизводимым: до начала известны scope, write-policy, preconditions, selective roster, stop conditions и verification gates.
3. Защитить пользователя от ложного успеха:
   - security verdict без проверяемых findings/evidence;
   - зелёный build через отключение gates;
   - contract approval без трассировки consumers;
   - performance-оптимизация без сопоставимых замеров;
   - TDD без подтверждённого RED.
4. Сохранить qtim-native orchestration: main thread владеет fan-out, использует только реально нужные доступные роли и проверяет advisory-результаты по source.
5. Сохранить совместимость с проектами qtim 2.10: новые skills не требуют пяти новых agent TOML, а любые изменения generated project state мигрируются только через `$qtim-update`.

## Не-цели

- Создание `security`, `build`, `contract`, `performance` или `tdd` custom-agent TOML.
- Автоматическое исправление результатов `$qtim-security-review` или `$qtim-contract-review`.
- Замена `$qtim-team-up`, `$qtim-team-lazy`, `$qtim-debug-loop` либо перенос их orchestration ownership в bundled discipline.
- Гарантия отсутствия уязвимостей, полноты динамически обнаруживаемых consumers или универсального улучшения производительности.
- Отключение lint/typecheck/tests, массовые suppressions или слепое обновление зависимостей ради зелёного результата.
- Оптимизация без определённого сценария, baseline и повторного измерения.
- Production-изменение в `$qtim-tdd` до наблюдаемого RED, падающего по ожидаемой причине.
- Скрытое переключение model/reasoning открытой задачи, рекурсивный child fan-out или обещание persistent team state.
- Claude Code primitives либо одновременный текстовый порт в sibling repository.
- Добавление telemetry/analytics substrate в рамках этой фичи.

## Пользователи и потребности

| Пользователь | Потребность | Подходящий вход |
|---|---|---|
| Developer | Локализовать и минимально исправить сломанный build, typecheck, lint или CI | `$qtim-build-fix` |
| Developer | Реализовать конкретное поведение коротким test-first циклом | `$qtim-tdd` |
| Developer / technical lead | Найти доказанный bottleneck и улучшить его без регрессии корректности | `$qtim-performance` |
| Project owner / decision owner | Получить проверяемую оценку security-риска без неожиданных изменений | `$qtim-security-review` |
| Project owner / decision owner | Понять совместимость изменения публичного/внутреннего контракта и безопасный путь миграции | `$qtim-contract-review` |

Конкретные application-роли, permissions, tenant model, API и performance budgets не предполагаются заранее: workflow обнаруживает их из target project source или явно помечает как неизвестные.

## Общий пользовательский контракт

### Запуск

- Каждый workflow запускается самостоятельным явным вызовом `$qtim-*`; предварительный вызов `$qtim-team-up` или `$qtim-team-lazy` не требуется.
- Явный вызов разрешает только действия внутри названного workflow и bounded scope. Он не расширяет исходную задачу.
- До fan-out main thread показывает или однозначно фиксирует:
  - выбранный workflow;
  - проверяемый target scope;
  - режим `read-only` или разрешённый write scope;
  - preconditions и stop condition;
  - выбранные роли и verification gates.
- Если безопасный scope нельзя вывести из запроса и repository evidence, workflow задаёт один блокирующий вопрос до записи. Read-only discovery для уточнения scope разрешён.

### Write-policy

- `$qtim-security-review` и `$qtim-contract-review` по умолчанию не меняют target source. Исправление или миграция требуют отдельной явной просьбы и запуска подходящего write-workflow.
- `$qtim-build-fix`, `$qtim-performance` и `$qtim-tdd` могут менять файлы только внутри явно названного или подтверждённого scope вызова.
- Обнаружение соседней проблемы не разрешает расширить write scope: она возвращается как blocker, risk или рекомендуемый следующий шаг.
- Временная диагностика допустима только в write-enabled workflow, должна быть маркирована и полностью удалена до успешного завершения.

### Selective orchestration

- Main thread напрямую выбирает из ролей, реально доступных в project charter, только владельцев затронутых слоёв; отсутствие database/frontend роли в compact project не является ошибкой.
- Main thread единолично владеет fan-out, учитывает runtime thread cap, запускает независимые scopes batches при необходимости и проверяет результаты по файлам/командам.
- Child agents не создают qtim descendants и не превращают workflow в скрытый `$qtim-team-up`.
- Role agents используют точные atomic model pairs из TOML; workflow не создаёт новые role templates и не меняет профиль уже открытой задачи.
- Результат subagent является evidence для main thread, а не финальным решением. Финальный отчёт синтезирует main thread.

### Общий формат результата

Каждый workflow завершает ответом, из которого однозначно видны:

1. проверенный scope и фактически выбранные роли;
2. write-policy и список изменённых файлов либо явное `изменений нет`;
3. воспроизводимое evidence: `file:line`, команды, trace/profile/benchmark или test output в зависимости от workflow;
4. пройденные и непройденные gates;
5. итоговый verdict/status без маскировки skipped или unavailable проверки как passed;
6. blockers, остаточные риски и следующий безопасный шаг.

## Сценарии

### Сценарий A — read-only security review

Пользователь указывает поверхность или риск. Workflow уточняет границы, выбирает только нужные review/layer роли, исследует source без записи и возвращает дедуплицированные P0–P3 findings с exploitation story и итоговым verdict.

### Сценарий B — минимальная починка build/CI

Пользователь передаёт failing command или CI signal. Workflow воспроизводит исходный RED, локализует причину через `$qtim-debug-loop`, вносит минимальную scoped правку и повторяет исходную и связанные проверки.

### Сценарий C — review изменения контракта

Пользователь называет contract или предполагаемое изменение. Workflow находит producer и consumers, классифицирует совместимость, отмечает неизвестные call sites и без записи выдаёт migration/expand-contract путь и необходимые tests.

### Сценарий D — измеренная performance-работа

Пользователь задаёт сценарий и проблему. Workflow фиксирует метрику и budget/target, снимает baseline, локализует bottleneck по profile/trace/benchmark, делает минимальное scoped изменение и сравнивает сопоставимые замеры до и после.

### Сценарий E — реализация поведения через TDD

Пользователь формулирует наблюдаемое поведение. Workflow выбирает test seam, добавляет минимальный тест, подтверждает RED по ожидаемой причине, затем выполняет `GREEN → REFACTOR → VERIFY` в заданном scope.

## Acceptance criteria: `$qtim-security-review`

1. Skill объявляет read-only default до начала проверки и при обычном запуске не изменяет ни target source, ни конфигурацию проекта.
2. До анализа зафиксированы проверяемые границы: поверхность/файлы или риск-lens; неизвестные application actors, permissions и tenant semantics отмечаются как гипотезы, а не как факты.
3. Selective roster выводится из затронутых слоёв и project charter; workflow не требует отсутствующих ролей и не запускает весь roster по умолчанию.
4. Каждый подтверждённый finding содержит:
   - severity `P0`, `P1`, `P2` или `P3`;
   - точное evidence `file:line`;
   - нарушенное правило/invariant или ожидаемую security boundary;
   - реалистичный exploitation/failure scenario;
   - impact и concrete remediation;
   - рекомендуемого владельца исправления из существующего roster.
5. Непроверяемые подозрения отделены от findings и явно помечены `гипотеза` с недостающим evidence.
6. Дубликаты одного root cause объединены; affected call sites перечислены внутри одного finding.
7. Финальный verdict равен:
   - `APPROVED`, только если в проверенном scope нет подтверждённых blocking findings и обязательные проверки выполнены;
   - `NOT APPROVED`, если есть P0/P1, иной подтверждённый blocker или обязательную проверку нельзя выполнить.
8. Skipped/unavailable область перечислена как coverage gap и не трактуется как проверенная.
9. Workflow не исправляет findings без нового явного write-запроса.

## Acceptance criteria: `$qtim-build-fix`

1. До production-изменения зафиксированы failing command/CI job, релевантное окружение и исходный RED output. Если воспроизведение невозможно, workflow останавливает write-phase и возвращает exact evidence gap.
2. Для нетривиальной или flaky причины применяется последовательность `$qtim-debug-loop`: минимальный repro, 3–5 ранжированных фальсифицируемых гипотез и probes по одной переменной.
3. Правка ограничена доказанной причиной и согласованным write scope; unrelated failures не исправляются молча.
4. Workflow не объявляет успех, если зелёный сигнал получен отключением gate, удалением проверки, массовой suppression или ослаблением assertion.
5. Dependency/lockfile update допустим только когда связь с root cause доказана, изменение входит в явный scope и после него повторены связанные regression/security gates.
6. До успешного завершения повторно проходят:
   - исходная failing command или эквивалентный локальный repro;
   - связанные build/typecheck/lint/tests, которые могла затронуть правка;
   - cleanup временных `[DEBUG-*]` и созданных одноразовых harness-файлов.
7. Финальный status — `FIXED` только при зелёном исходном сигнале и связанных gates; иначе `BLOCKED` с последним наблюдаемым signal, проверенными гипотезами и следующим probe.
8. Отчёт перечисляет root cause, минимальный diff scope, все выполненные команды и изменённые файлы.

## Acceptance criteria: `$qtim-contract-review`

1. Skill объявляет read-only default и при обычном запуске не меняет target source или contract artifacts.
2. До review назван сам contract и его producer; если producer не найден однозначно, результат останавливается на `UNKNOWN`, а не предполагает контракт.
3. Workflow прослеживает producer → все обнаружимые consumers в repository scope и для каждого приводит `file:line`; механизмы динамического, внешнего или generated consumption явно перечисляются как coverage gaps.
4. Предлагаемое изменение получает одну классификацию:
   - `COMPATIBLE`;
   - `CONDITIONALLY COMPATIBLE` с условиями;
   - `BREAKING`;
   - `UNKNOWN` при недостаточном evidence.
5. Классификация рассматривает применимые формы контракта: schema/types, request/response, events, CLI/config, persisted/generated format и documented public behavior — только если они реально присутствуют.
6. Для `BREAKING` или `CONDITIONALLY COMPATIBLE` результат содержит:
   - несовместимые consumers/call sites;
   - migration order;
   - rollback/compatibility window;
   - необходимые contract/regression tests.
7. Широкая миграция или rename/retype описывается через expand-contract: новая форма рядом со старой → миграция consumers небольшими пачками с зелёными gates → удаление старой формы последним шагом.
8. Verdict не равен `COMPATIBLE`, если остались неизвестные обязательные consumers; такой случай остаётся `UNKNOWN` либо `CONDITIONALLY COMPATIBLE` с явно указанным условием.
9. Реализация migration plan начинается только по отдельному явному write-запросу.

## Acceptance criteria: `$qtim-performance`

1. До оптимизации зафиксированы:
   - пользовательский сценарий/workload;
   - измеряемая метрика;
   - performance budget или целевой порог;
   - сопоставимое окружение и способ повторного замера.
2. До production-изменения снят baseline с сырым evidence и единицами измерения. Если baseline или target получить нельзя, workflow остаётся в диагностическом режиме и не вносит «оптимизацию».
3. Bottleneck локализован через подходящий profile, trace, query plan или benchmark; корреляция без локализующего evidence помечается как гипотеза.
4. Изменяется только доказанный bottleneck в явном write scope; один experiment по возможности меняет одну переменную.
5. Замер после изменения использует тот же workload, метрику, единицы и сопоставимое окружение; отчёт показывает `до → после` и отклонение от budget/target.
6. Успех объявляется только при выполненном target/budget и зелёных correctness/regression gates затронутого поведения.
7. Если метрика не улучшилась, нестабильна или correctness gate регрессировал, изменение не выдаётся за успех: workflow откатывает только собственный безопасно обратимый experiment либо возвращает blocker без расширения scope.
8. Временное profiling/debug instrumentation удалено; оставшееся production instrumentation требует явного scope и объяснения.
9. Финальный отчёт содержит baseline, after measurement, методику, изменённые файлы, correctness gates и известные ограничения измерения.

## Acceptance criteria: `$qtim-tdd`

1. До цикла сформулировано одно наблюдаемое поведение и выбран проверяемый seam; scope не превращается в общий rewrite.
2. `RED` наблюдается до production-изменения: добавленный/изменённый тест падает по ожидаемой причине, а не из-за syntax, fixture, environment или unrelated failure.
3. Если ожидаемый RED нельзя получить или поведение уже реализовано, workflow не фабрикует падение и не меняет production source: возвращает precondition gap или предлагает отдельный characterization/regression сценарий.
4. `GREEN` достигается минимальным production-изменением внутри явного write scope; тест не ослабляется для получения зелёного сигнала.
5. `REFACTOR` выполняется только при сохранении зелёного целевого теста после каждого содержательного шага; отсутствие нужного рефакторинга допустимо и явно отмечается.
6. `VERIFY` повторяет целевой тест и релевантные regression gates затронутого слоя.
7. Каждый этап отчёта содержит команду и наблюдаемый результат `RED / GREEN / REFACTOR / VERIFY`; skipped этап имеет объяснение и не считается выполненным.
8. Unrelated failing tests сохраняются как отдельные blockers и не чинятся без расширения scope.
9. Финальный status — `DONE` только если целевое поведение и regression gates зелёные; иначе указывается последний честно завершённый этап цикла.

## Общие acceptance criteria: orchestration и compatibility

1. В plugin доступны ровно пять новых самостоятельных skill-входов:
   - `$qtim-security-review`;
   - `$qtim-build-fix`;
   - `$qtim-contract-review`;
   - `$qtim-performance`;
   - `$qtim-tdd`.
2. У каждого skill есть валидный Codex skill contract и UI metadata с уникальными name/description/default prompt; название и описание позволяют отличить его от role и от `$qtim-team-up`/`$qtim-team-lazy`.
3. Ни в `plugins/qtim/agents/`, ни в generated `.codex/agents/` не появляется новая постоянная роль из-за этой фичи.
4. Каждый skill содержит preconditions, trigger, selective roster, read/write boundary, этапы, stop conditions, verification gates, формат результата, escalation и anti-patterns.
5. Skills переиспользуют канонические qtim contracts через согласованные формулировки/ссылки и не создают конфликтующие версии:
   - main-thread fan-out и runtime thread cap;
   - exact atomic model pairs;
   - запрет recursive child teams;
   - `$qtim-debug-loop`;
   - canonical high-risk review matrix;
   - expand-contract;
   - durable evidence и main-thread verification.
6. Самостоятельный вход напрямую делегирует только нужным существующим ролям; обязательного промежуточного вызова team-up/lazy нет.
7. Workflow корректно работает с Compact/Standard/Extended roster: отсутствующий необязательный layer role не блокирует запуск, а действительно недостающий владелец отражается как gap/escalation.
8. Skills остаются self-contained для target project и не требуют Claude primitives, plugin-internal относительных путей в generated state или скрытой persistence.
9. Установка/обновление новых skills требует новой Codex task для их загрузки; документация не обещает hot reload в уже открытой задаче.

## Общие acceptance criteria: release и verification

1. Пять workflow-входов перечислены в пользовательской документации с коротким «когда использовать» и write-policy.
2. Plugin version увеличена, а `CHANGELOG.md` описывает пользовательский outcome, границы записи и совместимость.
3. `plugins/qtim/reference/upgrade-notes.md` содержит versioned release section:
   - с миграцией через `$qtim-update`, если реализация меняет generated project state;
   - с явным «миграция не требуется», если generated state не меняется.
4. При generated-state change migration:
   - сохраняет foreign/manual content и соседний track;
   - показывает plan/diff до записи;
   - сохраняет user model overrides;
   - оставляет version stamp на последней полностью применённой версии при `pending`.
5. Проходят все repo-local проверки из `AGENTS.md`, включая JSON, hooks, placeholders, skills, links и agent TOML validation.
6. Перед release проходит доступный `validate_plugin.py plugins/qtim`; недоступность фиксируется как `skipped — <reason>`, а не как passed.
7. Smoke-проверка в новой Codex task подтверждает discoverability всех пяти `$qtim-*` имён и отсутствие пяти новых project agent templates.

## UX-заметки

### Выбор входа

Пользователь должен различать workflows по намерению, а не по внутренней роли:

| Намерение | Вход | Default |
|---|---|---|
| «Найди security-риски» | `$qtim-security-review` | Read-only |
| «Верни build/CI в зелёное состояние» | `$qtim-build-fix` | Scoped write |
| «Совместимо ли изменение контракта?» | `$qtim-contract-review` | Read-only |
| «Улучши доказанный bottleneck» | `$qtim-performance` | Scoped write после baseline |
| «Реализуй поведение test-first» | `$qtim-tdd` | Scoped write после RED |

### Первый ответ workflow

Первый содержательный ответ должен быть коротким и предсказуемым:

```text
Workflow: <name>
Scope: <target>
Mode: read-only | scoped write
Roles: <selected existing roles>
Evidence/gates: <what must be observed>
Stop condition: <when no write / no approval is possible>
```

Если данных не хватает, workflow спрашивает только решение, которое нельзя безопасно вывести из source: например, target contract, допустимый write scope или performance budget. Факты о структуре проекта, командах и consumers он сначала ищет сам.

### Failure states

- `BLOCKED` означает конкретный отсутствующий input/evidence, а не общий отказ.
- `UNKNOWN` в contract review и coverage gap в security review видимы рядом с verdict.
- Read-only workflow не предлагает «я уже исправил»; write-enabled workflow всегда перечисляет изменённые файлы.
- Workflow не показывает внутренний agent chatter и не называет запуск ролей «созданием команды».

## Метрики и проверка успеха

В qtim нет подтверждённых analytics events, event schema или hosted telemetry. Поэтому post-release adoption, completion rate и время до результата этой фичей не измеряются автоматически.

### Release-level measures

| Мера | Критерий | Источник |
|---|---|---|
| Discoverability coverage | 5 из 5 skill имён доступны в новой Codex task и имеют UI metadata | Smoke-check + skill validation |
| Contract coverage | 5 из 5 skills содержат обязательные preconditions, boundaries, gates, result и anti-patterns | PRD acceptance review |
| Read-only safety | В smoke-сценариях security/contract review нет project file diff | `git diff` до/после |
| Scoped-write safety | В smoke-сценариях build/performance/TDD нет изменений вне заявленного scope | `git diff --name-only` + отчёт workflow |
| Evidence honesty | Все skipped/unavailable gates обозначены явно; ни один не назван passed | Reviewer gate |
| Repository health | Все применимые repo-local validators зелёные | CI/local command evidence |
| Roster compatibility | Новые agent TOML отсутствуют; выбор ролей основан на charter | File inventory + smoke-check |

### Measurement gap

Реальное использование пяти входов после release нельзя доказать существующей инфраструктурой. Добавление telemetry потребует отдельного решения о privacy, opt-in, storage, actor identity и источнике данных; оно не входит в текущий scope. До появления такого решения допустимы только operational proxies — changelog/version, artifact history, review report и bug evidence — и они не должны называться продуктовой аналитикой.

## Риски и меры снижения

| Риск | Последствие | Мера снижения |
|---|---|---|
| Пять skills дублируют и со временем расходятся с общими qtim contracts | Противоречивые gates и orchestration | Переиспользовать canonical references; validator/reviewer проверяет обязательные markers |
| Формулировка «review» создаёт ложное ощущение полноты | Пропущенная уязвимость или consumer воспринимается как безопасный | Coverage gaps, `UNKNOWN`, гипотезы отдельно от findings, запрет безусловной гарантии |
| Неявный scope превращает write-workflow в широкую починку | Unrelated diff и дорогой rollback | До записи фиксировать bounded scope; расширение только отдельным решением |
| Build-fix маскирует symptom | Хрупкий зелёный CI | Исходный RED, root-cause evidence, запрет отключения gates, повтор связанных checks |
| Performance measurement нестабилен | Шум объявляется улучшением | Сопоставимый workload/environment, budget, baseline и after evidence |
| TDD невозможно честно применить к текущему seam | Искусственный RED или тест реализации вместо поведения | Stop condition; characterization вынести как отдельный явно названный сценарий |
| Contract consumers динамические или внешние | Неполная migration map | Явный coverage gap и `UNKNOWN`/conditional verdict |
| Selective fan-out незаметно становится fan-out всего roster | Лишняя стоимость и нарушение compact model | Main-thread roster rationale, runtime cap, no recursive spawning |
| Изменение charter ради discoverability повреждает generated state | Проекты 2.10 расходятся или теряют ручные правки | Не менять generated state без необходимости; при изменении — versioned `$qtim-update` migration |
| Пользователь ожидает skills в уже открытой task | «Команда не видит» новую возможность | Release/install UX явно требует новую Codex task |

## Подтверждённые решения

- Security review и contract review — read-only по умолчанию.
- Build-fix, performance и TDD могут писать только в явном scope.
- Каждый workflow — самостоятельный вход с прямым selective fan-out, без обязательного вызова team-up/lazy.
- Текущий release scope — только Codex plugin.
- Generated-state changes мигрируются через `$qtim-update`; без таких изменений release notes явно говорят, что миграция не требуется.
- Пять новых постоянных TOML ролей не создаются.

## Открытые вопросы checkpoint

1. Что именно означает read-only default для `$qtim-security-review` и `$qtim-contract-review`:
   - рекомендуемый вариант — никаких project filesystem writes, включая `memory/`; durable отчёт сохраняется только отдельной явной просьбой;
   - альтернатива — разрешить запись только в согласованный evidence-файл `memory/`, не меняя target source.
2. Как задавать достаточную устойчивость performance-замера:
   - рекомендуемый вариант — использовать существующую project benchmark convention; если её нет, workflow фиксирует число повторов и разброс, но не навязывает универсальный порог;
   - альтернатива — ввести единый минимальный repetition/stability threshold для всех target projects, хотя их workloads и инструменты различаются.
3. Нужен ли единый машинно-проверяемый result schema для пяти workflows в первом release:
   - рекомендуемый вариант — нет, достаточно обязательных Markdown-полей и validator markers;
   - альтернатива — сразу ввести общий schema/template, что расширит публичный контракт и migration/validation surface.

## История изменений

- 2026-07-27 — Draft: создан PRD стадии 2; утверждённый intake развёрнут в отдельные acceptance contracts пяти workflows, общие orchestration/compatibility/release gates, UX, измерение, риски и checkpoint-вопросы.
