Feature: Семантический порт Claude qtim 1.13.0
Slug: claude-1-13-minimal-diff-port
Status: Approved
Дата: 2026-07-30

# PRD

## Контекст

Claude qtim 1.13.0 добавил не только дисциплину `minimal-diff`, но и связанный
контракт её применения: ролевые точки вызова, доставку mandatory practices в
generated state, безопасную миграцию существующих команд, advisory-проверку
roster, сбор маркеров упрощений на retro, инвентаризацию call sites при
диагностике, CI-защиту ссылок на skills и полный MIT notice.

Codex qtim 2.12.0 этих поверхностей не имеет. Изолированный перенос одного
`SKILL.md` сделал бы новую дисциплину доступной, но фактически неиспользуемой
ролями и уже сгенерированными командами. Утверждённый intake поэтому задаёт
полный семантически переносимый scope релиза 1.13.0 с Codex-native адаптацией.

Источник scope: `docs/features/claude-1-13-minimal-diff-port/intake.md`.
Upstream evidence: Claude commit
`887975fb3324506a64428311d79e533579b1c70d` и его `CHANGELOG.md`.

## Цели

1. Добавить discoverable Codex-дисциплину `$qtim-minimal-diff`, которая помогает
   выбрать наименьший полноценный объём решения до написания кода.
2. Встроить дисциплину в architect/database/frontend/reviewer contracts так,
   чтобы она применялась в нужный момент и не становилась новым orchestrator.
3. Зафиксировать пределы минимизации: согласованный scope, доменные инварианты,
   защищённые зоны и обязательная минимальная самопроверка нетривиальной логики
   не сокращаются.
4. Доставить mandatory practices в новые и существующие generated teams через
   `$qtim-setup` и `$qtim-update` без потери соседнего track, ручного текста и
   model overrides.
5. Замкнуть operational feedback loops: doctor обнаруживает roster drift, retro
   поднимает сработавшие маркеры упрощений, debug-loop проверяет все call sites
   до исправления.
6. Сделать строковые вызовы bundled skills проверяемым repository contract:
   неверное имя или нерезолвящаяся engine-managed ссылка должны останавливать CI.
7. Выпустить юридически и документально целостный релиз: полный MIT notice,
   versioned migration notes, changelog, пользовательская документация и port map.

## Не-цели

- Перенос `.claude/*`, slash commands, Agent Teams, `Task*`, Claude
  agent-memory, standalone mode или Claude golden layout.
- Текстовое копирование upstream-файлов или его runtime-specific схем.
- Перепроектирование `$qtim-mission`, execution depth A–D или ownership fan-out.
- Превращение `$qtim-minimal-diff` в orchestration workflow, новую custom role,
  отдельный формат ролевого отчёта или замену `$qtim-brainstorm`,
  `$qtim-prototype`, `$qtim-debug-loop` и review gates.
- Право исполнителя молча сокращать утверждённый scope или acceptance criteria.
- Автоматическое добавление, удаление или переименование ролей по результату
  `$qtim-doctor`.
- Полное test coverage как обязанность дисциплины: она требует минимальный
  доказательный сигнал, а системная матрица проверок остаётся у testing/reviewer.
- Новая telemetry, analytics events, hosted storage или post-release usage
  dashboard.
- Реализация plugin/source, agent TOML или validation tests внутри PM pipeline.

## Пользователи и потребности

| Пользователь | Потребность | Ожидаемый результат |
|---|---|---|
| Maintainer Codex-плагина | Перенести upstream-релиз без смешения runtime contracts | Codex-native release с зелёными repo gates, notice и traceable port-map записью |
| Developer | Не строить лишние слои и зависимости, сохраняя корректность | Лестница выбора объёма до нетривиальной реализации и понятные protected zones |
| Architect | Сравнивать варианты не только по trade-offs, но и по необходимому объёму | Лишняя сущность/слой снимаются до ADR; необходимая новая граница названа явно |
| Reviewer | Отделять избыточность от нарушения инварианта | Лишний объём попадает в рекомендации и сам по себе не блокирует verdict |
| Владелец существующей generated team | Получить новые practices без перезаписи своих настроек | Scoped migration diff, сохранённые track/manual/model overrides и честный `pending` |
| Project owner / decision owner | Понимать, соответствует ли roster фактическим слоям проекта | Read-only doctor warning и явный путь через повторный `$qtim-setup` |
| PM/Analyst | Получать более сфокусированный architect consult и handoff | Косвенная польза без нового PM-orchestrator и без сокращения утверждённого PRD |

## Продуктовый контракт minimal-diff

### Что выбирает дисциплина

Перед нетривиальным design/implementation решением исполнитель последовательно
проверяет:

1. нужна ли новая функциональность или сущность вообще;
2. нет ли решения уже в проекте;
3. нет ли штатного решения в используемой библиотеке;
4. не закрывает ли задачу возможность платформы или фреймворка;
5. не закрывает ли её уже установленная зависимость;
6. достаточно ли одной локальной строки/операции;
7. если нет — какая минимальная реализация полностью решает согласованную задачу.

Лестница сравнивает уже сформированные варианты по остающемуся объёму. Она не
заменяет исследование потока, discovery вариантов, ADR filter или проверку
инвариантов.

### Где сокращение запрещено

Обязательство фиксируется целиком, если оно относится хотя бы к одной зоне:

- валидация на границе доверия;
- обработка ошибок, предотвращающая потерю данных;
- безопасность и разграничение доступа;
- базовая доступность пользовательской поверхности;
- явно запрошенное пользователем поведение;
- утверждённые acceptance criteria и документированные инварианты проекта.

Для этих зон лестница выбирает минимальный полноценный способ исполнения, но не
уменьшает само обязательство. Сомнение в необходимости требования возвращается
как open question team-lead'у или decision owner, а не реализуется молчаливым
сокращением.

### Маркер осознанного упрощения

Если у выбранного простого решения известен практический потолок, автор может
оставить marker вида:

`minimal-diff: <потолок> — <проверяемый триггер и действие после него>`

Marker допустим только для обратимого упрощения вне protected zones. Заметка без
проверяемого триггера не считается полезным marker. Сработавший триггер должен
стать видимым follow-up с источником и владельцем на retro.

### Минимальная самопроверка

Нетривиальная логика не считается готовой без одной минимальной проверки,
которая действительно падает при поломке поведения. Используется существующий
test runner; при его отсутствии допустим минимальный запускаемый assertion.
Дисциплина не требует нового test suite, framework или fixture infrastructure
ради одного сигнала. Полное coverage и regression matrix остаются отдельными
verification gates.

## Пользовательские сценарии

### Сценарий A — выбрать объём архитектурного варианта

Architect формирует варианты решения и применяет лестницу к каждому. Вариант с
новым слоем или зависимостью остаётся только при предъявленной границе,
инварианте или доказанной невозможности использовать уже имеющееся средство.
Если такое решение нужно, оно явно попадает в design brief/ADR.

### Сценарий B — реализовать нетривиальное изменение

Database или frontend role перед записью проверяет существующие helpers,
platform primitives и зависимости, выбирает минимальную полноценную реализацию,
не сокращает protected zones и добавляет минимальный red/green signal для
нетривиальной логики.

### Сценарий C — проверить объём на review

Reviewer находит абстракцию под единственный вызов, дублирование существующей
логики или ненужную зависимость. Такая находка отражается как рекомендация и не
блокирует verdict сама по себе. Нарушение acceptance criteria, protected zone,
инварианта или verification gate остаётся blocker по обычному review contract.

### Сценарий D — создать или дозаполнить generated team

Пользователь запускает `$qtim-setup`. Plan до записи показывает новые mandatory
practices и роли, которые будут добавлены/обновлены. Re-run дозаполняет выбранный
состав и managed track regions, не пересоздавая команду, не удаляя роли и не
затирая соседний track или ручной текст.

### Сценарий E — мигрировать team с 2.12.0

После обновления plugin пользователь запускает `$qtim-update`, видит versioned
plan и scoped diff по generated state, затем подтверждает применение.
Однозначные managed regions получают новые practices; неоднозначные локальные
изменения остаются `pending`. Version stamps повышаются только после полного
применения обязательных шагов.

### Сценарий F — обнаружить roster drift

Пользователь запускает `$qtim-doctor`. Doctor сопоставляет текущие роли с
проверяемыми признаками слоёв/обязанностей репозитория, возвращает `warn` с
evidence и рекомендацией. Он ничего не меняет; изменение состава начинается
только отдельным повторным `$qtim-setup` с обычным plan/approval.

### Сценарий G — вернуть сработавшее упрощение в работу

После эпика `$qtim-team-retro` ищет `minimal-diff:` markers в доказуемом diff
эпика. Несработавшие триггеры остаются информативными. Для сработавшего триггера
retro создаёт durable follow-up с точным marker/source, evidence срабатывания,
владельцем и следующим проверяемым действием.

### Сценарий H — исправить нетривиальный баг

После воспроизведения и проверки гипотез, но до фикса, `$qtim-debug-loop`
инвентаризирует все обнаружимые call sites изменяемой функции и соседние пути
через неё. Regression signal покрывает root cause, а не только путь из исходного
репорта; неизвестные динамические/внешние вызовы отмечаются как coverage gap.

### Сценарий I — выпустить и проверить релиз

Maintainer запускает repo-local validation и доступный plugin validator.
CI подтверждает совпадение имён skills с каталогами и резолвинг engine-managed
`$qtim-*` ссылок. Release docs описывают outcome и migration, port map фиксирует
semantic parity, а THIRD_PARTY_NOTICES содержит полный требуемый MIT notice.

## Acceptance criteria

### AC-1. Public discipline surface

1. В установленном plugin существует ровно один новый bundled skill с точным
   пользовательским именем `$qtim-minimal-diff`.
2. Skill имеет валидные Codex metadata и discoverable описание, отличающее
   дисциплину объёма от prototype, brainstorm и orchestration workflows.
3. Skill остаётся role-agnostic practice: не владеет main-thread fan-out, не
   запускает роли и не обещает persistent team state.
4. Контракт содержит семиступенчатую лестницу, protected zones, marker с
   trigger/action, минимальную самопроверку, escalation при споре о scope и
   границы с `$qtim-prototype`/`$qtim-brainstorm`.
5. Skill не вводит собственную обязательную схему отчёта. Информация об объёме
   добавляется в существующий role output только когда есть значимое решение,
   риск или open question.

### AC-2. Role behavior

1. Architect применяет лестницу при сравнении design-вариантов и явно обосновывает
   необходимый новый слой/зависимость; brainstorm и ADR gates при этом сохраняются.
2. Database применяет дисциплину перед нетривиальной миграцией, route или helper,
   предпочитая существующий pattern и native constraint/index/trigger, когда они
   полностью обеспечивают требование.
3. Frontend применяет дисциплину перед нетривиальной реализацией и проверяет
   отсутствие существующего component/composable/utility или platform primitive.
4. Reviewer проверяет лишние abstraction/duplication/dependency как класс
   рекомендаций. Такие findings сами по себе не меняют verdict на
   `NOT APPROVED`.
5. Минимальная самопроверка нетривиальной логики не классифицируется reviewer'ом
   как лишний объём; лишней может считаться только недоказанная новая test
   infrastructure сверх нужного сигнала.
6. Ни одна роль не использует minimal-diff для обхода security, data integrity,
   accessibility, explicit scope, domain invariants или своих обязательных gates.
7. Согласованное требование, которое роль считает избыточным, возвращается как
   open question; роль не закрывает задачу как Done на сокращённом scope.

### AC-3. Setup и generated state

1. `$qtim-setup` считает `$qtim-minimal-diff` bundled Layer 0 discipline, а не
   optional external dependency.
2. Setup plan до записи перечисляет изменяемые mandatory practices и additions
   roster; никакая роль не добавляется или удаляется молча.
3. Generated charter содержит применимые minimal-diff practices для текущего
   roster и сохраняет уже обязательные brainstorm/debug-loop/ADR practices.
4. Generated role TOML self-contained, использует Codex exact atomic model pairs
   и не получает Claude paths, tools или orchestration primitives.
5. Повторный setup добавляет недостающую поддерживаемую роль/managed practice,
   но не пересоздаёт team, не удаляет существующую роль, не перезаписывает другой
   `qtim:track:*` block и не меняет ручной текст вне managed regions.
6. Golden generated project отражает тот же mandatory-practice contract, что
   setup/templates, и проходит применимый golden validator.

### AC-4. Versioned migration

1. Изменение generated state сопровождается version bump, release entry и новой
   последовательной секцией в `plugins/qtim/reference/upgrade-notes.md`.
2. `$qtim-update` показывает installed/project versions, migration plan и diff
   до записи; применение начинается только после подтверждения пользователя.
3. Миграция из 2.12.0 обновляет managed charter/role regions, сохраняя dev/PM
   track markers, foreign/manual content и пользовательские atomic model
   overrides.
4. Переименованный, отсутствующий или локально изменённый role target
   сопоставляется только при достаточном evidence; неоднозначность становится
   `pending`, а не догадкой или созданием дубликата.
5. При любом обязательном `pending` дальнейшие version steps не применяются, а
   stamps остаются на последней полностью применённой версии.
6. Проекты без миграции продолжают работать по старым contracts; документация
   честно объясняет, что skill доступен после plugin update, но generated roles
   не вызывают его до `$qtim-update`/setup.
7. Rollback не требует удаления пользовательских ролей, ручной перезаписи memory
   или очистки `minimal-diff:` comments.

### AC-5. Doctor roster audit

1. Doctor остаётся read-only и добавляет отдельную проверку соответствия roster
   фактам репозитория.
2. Каждый warning содержит наблюдаемый repository signal, отсутствующую или
   лишнюю responsibility/role и конкретный следующий шаг; неподтверждённые stack
   предположения не выдаются за факты.
3. Отсутствующий владелец CI/operations, data/migrations, public/product surface
   или отдельного стека монорепозитория может породить `warn`; наличие роли без
   соответствующего слоя также может породить `warn`.
4. Roster drift никогда не становится `fail` сам по себе и не изменяет charter,
   agent files или memory.
5. Для роли, которую текущий setup умеет добавить, warning ведёт к повторному
   `$qtim-setup`. Для неподдерживаемого названия doctor сообщает responsibility
   gap и требует явного решения владельца, а не обещает несуществующий template.
6. Повторный setup после warning сохраняет обычные discovery, displayed plan,
   collision handling и user approval.

### AC-6. Retro marker harvesting

1. Retro ищет markers только в подтверждаемом scope текущего эпика/diff и
   приводит source location; repository-wide совпадения без связи с эпиком не
   приписываются текущей работе.
2. Marker парсится как `потолок + проверяемый триггер/действие`; marker без
   триггера помечается как некорректный follow-up candidate, а не как готовая
   задача.
3. Retro различает `trigger не сработал`, `trigger сработал` и
   `недостаточно evidence`.
4. Сработавший marker получает durable follow-up в retro evidence с source,
   trigger evidence, одним владельцем и проверяемым следующим действием.
5. Несработавший marker не создаёт шумовую задачу; недостаток evidence отражается
   честно и не называется срабатыванием.
6. Marker в protected zone не легализует отложенное обязательство и возвращается
   как нарушение исходного contract.

### AC-7. Debug-loop call-site inventory

1. До production fix нетривиального бага debug-loop называет изменяемый root seam,
   все обнаруженные repository call sites и соседние пути через него.
2. Поиск охватывает статические references и релевантные project conventions;
   динамические, generated или external consumers отмечаются как coverage gaps.
3. Исправление общего root cause предпочтительно множеству одинаковых patches,
   но не расширяет согласованный write scope без отдельного решения.
4. Regression test или иной минимальный red/green signal доказывает исходный
   symptom и применимые соседние пути; отсутствие корректного test seam
   фиксируется по действующему debug-loop contract.
5. Call-site inventory дополняет, а не заменяет существующие фазы repro,
   hypotheses, one-variable probes, test-before-fix и cleanup.

### AC-8. Skill-reference enforcement

1. Repository validation проверяет, что declared `name` каждого bundled skill
   совпадает с именем его каталога.
2. Каждая engine-managed ссылка вида `$qtim-<name>` в определённой validator
   scan surface резолвится в существующий Codex skill; Claude command namespace
   не считается допустимым fallback.
3. Reference matcher захватывает полное имя, поэтому намеренная опечатка/суффикс
   не проходит как валидный prefix.
4. Нулевое число просмотренных ссылок или исчезновение обязательной scan surface
   считается деградацией validator и приводит к fail.
5. Негативная fixture/проверка доказывает, что нерезолвящаяся ссылка действительно
   делает соответствующий CI gate красным.
6. Новый gate входит в локальный и CI validation contract и не дублирует
   конфликтующим образом существующие проверки skills/links.

### AC-9. Legal, documentation и release

1. `THIRD_PARTY_NOTICES.md` содержит полный применимый copyright и MIT permission
   notice для Dietrich Gebert / ponytail, а не только attribution-ссылку.
2. Maintainer guidance требует полного notice при будущей адаптации
   third-party MIT skills.
3. README/пользовательская документация объясняет, когда вызывать
   `$qtim-minimal-diff`, его отличие от prototype/brainstorm и необходимость
   новой Codex task после plugin update.
4. `CHANGELOG.md` описывает пользовательский outcome, protected zones,
   generated-state migration, diagnostics/retro/debug изменения и compatibility.
5. `docs/claude-port-map.md` получает строку semantic parity с Claude 1.13.0 и
   явно перечисляет не перенесённые Claude-only механики.
6. Plugin version, generated stamps и migration section согласованы.

### AC-10. Codex-native verification

1. В diff отсутствуют `.claude/*`, `.claude-plugin/*`, slash commands, Claude
   tools/frontmatter, Agent Teams и standalone-copy mechanics.
2. Сохраняются доменные инварианты plugin/project hook ownership, track markers,
   self-contained generated files, main-thread fan-out и exact model pairs.
3. Проходят все repo-local validation commands из `AGENTS.md`, включая JSON,
   hooks, placeholders, skills, missions, links, agent TOML, migrations и golden.
4. Доступный `validate_plugin.py plugins/qtim` проходит перед release;
   техническая недоступность записывается `skipped — <reason>` и не называется
   passed.
5. Smoke в новой Codex task подтверждает discoverability
   `$qtim-minimal-diff`; smoke migration подтверждает сохранность foreign/manual
   content, соседнего track и model override.
6. Independent reviewer проверяет фактический diff как изменение публичного и
   generated-state contracts; его findings имеют `file:line`, severity и
   подтверждаются main thread до release verdict.

## UX/DX-заметки

### Discoverability

Короткое описание skill должно отвечать на вопрос «когда использовать»:
перед нетривиальным design/implementation выбором, когда есть риск лишнего слоя,
дублирования или зависимости. Название и copy не должны обещать автоматическое
уменьшение любого diff или экономию за счёт качества.

### Выход дисциплины

Minimal-diff встраивается в существующий workflow роли. Если лестница ничего не
изменила, отдельный отчёт не нужен. Если решение изменилось, роль кратко называет
выбранную ступень, отвергнутый лишний объём и оставшийся риск/marker. Спор о scope
видим как open question.

### Review semantics

Пользователь должен отличать:

- `blocker`: нарушены scope, protected zone, инвариант или обязательный gate;
- `recommendation`: решение корректно, но оставляет доказанно лишний объём;
- `no finding`: минимальный и полный вариант совпадают.

Слово «minimal» не должно визуально или текстово понижать blocker до совета.

### Migration UX

До подтверждения пользователь видит, какие generated regions изменятся, какие
model overrides сохранятся и где возник `pending`. Успешный plugin update не
выдаётся за успешную миграцию project team. Для подхвата нового skill после
установки/upgrade явно требуется новая Codex task.

### Doctor UX

Roster audit остаётся строкой в обычной таблице `pass/warn/fail` и использует
`warn`, а не тревожный false blocker. Сообщение связывает signal → responsibility
gap → безопасное действие и не обещает автоматический fix.

### Marker и retro UX

Хороший marker читается без контекста автора: предел, наблюдаемый триггер и
действие. Retro показывает source и отдельно результат проверки trigger. Это
делает осознанное упрощение обслуживаемым контрактом, а не вечным TODO.

## Метрики и проверка успеха

В `memory/product-metrics.md` нет analytics events, event schema, hosted
telemetry или product usage store. Поэтому adoption, частота вызова
`$qtim-minimal-diff`, число предотвращённых абстракций и post-release defect rate
этой фичей автоматически не измеряются.

### Release-level measures

| Мера | Критерий | Источник evidence |
|---|---|---|
| Discoverability | `$qtim-minimal-diff` доступен по точному имени в новой Codex task | Plugin validation + manual smoke |
| Contract coverage | Лестница, protected zones, marker, self-check и escalation присутствуют и согласованы в skill/roles/generated fixture | Acceptance review + golden validation |
| Role coverage | Architect, database, frontend и reviewer демонстрируют ожидаемую семантику без нового orchestrator | Template/golden inspection |
| Migration preservation | Fixture 2.12.0 сохраняет foreign text, соседний track и model override; ambiguous case остаётся `pending` | Migration validation evidence |
| Roster audit safety | Doctor scenario выдаёт воспроизводимый `warn` и нулевой diff | Scenario smoke + `git diff` |
| Marker lifecycle | Triggered/untriggered/unknown fixtures получают разные результаты, triggered follow-up имеет source и owner | Retro scenario evidence |
| Call-site coverage | Debug scenario перечисляет несколько call sites и coverage gaps до фикса | Scenario evidence |
| Reference enforcement | Валидный repository проходит, намеренная опечатка делает gate красным | Positive/negative validator evidence |
| Legal completeness | Полный MIT notice присутствует и maintainer contract его требует | Notice/release review |
| Repository health | Все применимые repo-local gates и plugin validator зелёные либо честно skipped по недоступности | CI/local command evidence |

Эти measures подтверждают качество и целостность релиза, но не являются
продуктовой аналитикой или доказательством пользовательской ценности после
установки.

### Measurement gap

Post-release usage evaluation потребовала бы отдельного решения о privacy,
opt-in, storage, actor identity и источнике событий. Tracking work item в scope
этой фичи не добавляется, потому что утверждённый non-goal запрещает новую
analytics substrate. До отдельного discovery допустимы только operational
proxies: version/changelog, migration evidence, artifact history, review report,
bug log и retro records.

## Риски и меры снижения

| Риск | Последствие | Мера снижения |
|---|---|---|
| «Минимальный» ошибочно читается как «неполный» | Срезаются acceptance criteria, security или data integrity | Protected zones и explicit-scope rule повторяются в skill, roles и review |
| Дисциплина дублирует brainstorm/prototype/debug-loop | Противоречивые процессы и лишняя церемония | Явные границы назначения; skill не владеет orchestration/report schema |
| Reviewer делает style-рекомендацию release blocker | Correct diff застревает без нарушения инварианта | Отдельный recommendation class; blockers остаются по действующему contract |
| Mandatory practices расходятся между setup, templates, migration и golden | Новые и существующие teams ведут себя по-разному | Один семантический contract + cross-surface validation/golden gate |
| Миграция перезаписывает ручные правки или model overrides | Потеря пользовательской конфигурации | Region-aware diff, explicit approval, ambiguity -> `pending`, stamps after complete |
| Doctor рекомендует роль, которую setup не умеет создать | Пользователь получает тупиковый «фикс» | Различать supported role и responsibility gap; для второго требовать owner decision |
| Roster heuristics дают ложные warnings | Пользователь перестаёт доверять doctor | Только repository evidence, advisory severity, отсутствие мутаций |
| `minimal-diff:` превращается в write-only TODO | Известный потолок всплывает инцидентом | Trigger/action schema и retro harvesting по доказуемому epic diff |
| Retro создаёт шум из несработавших маркеров | Backlog захламляется преждевременной работой | Follow-up только при evidence сработавшего trigger |
| Call-site inventory создаёт ложное ощущение полноты | Динамический consumer остаётся сломанным | Coverage gaps для dynamic/generated/external calls |
| Новый validator ловит документационные примеры как runtime calls | Ложные CI failures | Явная engine-managed scan surface и позитивные/негативные fixtures |
| MIT attribution неполна | License compliance risk | Полный notice и maintainer rule для следующих адаптаций |
| Порт тянет Claude runtime vocabulary | Нарушается Codex-native contract | Port-map rules, Codex ingestion validation и independent review |
| Нет runtime analytics | Нельзя доказать adoption/value количественно | Не обещать post-release метрики; использовать только release evidence |

## Подтверждённые решения

- Портируется весь семантически переносимый пакет Claude 1.13.0, а не только
  новый skill.
- Используется полный feature track.
- `$qtim-minimal-diff` — role-agnostic bundled discipline, не orchestrator.
- Protected zones, утверждённый scope, acceptance criteria и обязательная
  минимальная самопроверка не сокращаются.
- Findings только о лишнем объёме — рекомендации, не автоматические blockers.
- Doctor остаётся advisory/read-only; roster меняется только отдельным
  подтверждённым `$qtim-setup`.
- Generated-state change получает versioned `$qtim-update` migration с
  сохранением track/manual/model overrides и fail-visible `pending`.
- Новая продуктовая analytics substrate не входит в scope.

## Решения checkpoint

1. Сработавший `minimal-diff:` marker получает durable follow-up в текущем
   `memory/retro-log.md` с source, trigger, owner и next action; внешняя issue
   создаётся только по отдельной просьбе. Новый backlog-файл не вводится.
2. Для нужной responsibility без готового Codex role template doctor называет
   responsibility gap и просит decision owner назначить существующего владельца
   или отдельно расширить setup; не обещает автоматический fix.
3. Validator scan boundary охватывает engine-managed plugin/reference/templates,
   generated fixtures и пользовательские release surfaces; исторические feature
   artifacts как prose evidence исключаются.

## История изменений

- 2026-07-30 — Draft r1: утверждённый полный scope Claude qtim 1.13.0
  развёрнут в пользовательский contract дисциплины, role/generated-state
  acceptance criteria, operational feedback loops, release measures, риски и
  checkpoint-вопросы; runtime analytics явно не предполагается.
- 2026-07-30 — Approved r2: пользователь утвердил PRD и рекомендованные contracts
  для durable marker follow-up, responsibility gap doctor и validator scan boundary.
