<!-- qtim-version: 2.10.0 -->
# Командный контракт qtim: qtim-agent-team

## Назначение и контекст

Команда сопровождает Codex-native marketplace-репозиторий плагина `qtim`. Продукт состоит из Markdown, JSON и TOML; application runtime, frontend, backend, база данных и файловое хранилище отсутствуют. Главные результаты работы — корректные plugin/marketplace manifests, skills, custom-agent templates, hooks, reference-механика, документация и миграционные заметки.

qtim workflow запускается только явным вызовом qtim skill или прямой просьбой пользователя о делегировании. Main thread остаётся team-lead, проверяет результаты ролей и владеет финальным решением.

## Фиксированный стек и команды

- Контент: Markdown, JSON, TOML.
- Проверки: Python 3, стандартные `json.tool` и `tomllib`, repo-local scripts.
- CI: GitHub Actions, `.github/workflows/validate.yml`.
- Application build, typecheck, migrations и browser/E2E: не применимы.

Полный локальный validation:

```bash
python3 -m json.tool .agents/plugins/marketplace.json > /dev/null
python3 -m json.tool plugins/qtim/.codex-plugin/plugin.json > /dev/null
python3 -m json.tool plugins/qtim/hooks/hooks.json > /dev/null
python3 -m json.tool plugins/qtim/reference/project-hooks.json > /dev/null
python3 .github/scripts/check_hooks.py
python3 .github/scripts/check_placeholders.py
python3 .github/scripts/check_skills.py
python3 .github/scripts/check_links.py
python3 .github/scripts/check_codex_agents.py
```

Перед release дополнительно запускается доступный локальный `validate_plugin.py plugins/qtim` из Codex `plugin-creator`.

## Роли

| Роль | Codex custom agent | Миссия | Триггеры | Не трогает | Read on start | External skills | Обязательные практики |
|---|---|---|---|---|---|---|---|
| Team lead | main thread | Классификация глубины A/B/C/D, fan-out, синтез, проверка и handoff | Любой явно разрешённый qtim workflow | Не расширяет scope и не подменяет решения пользователя | `AGENTS.md`, этот charter, `memory/MEMORY.md` | нет | Проверяет факты и артефакты ролей; фиксирует durable state |
| Architect | `qtim-architect` | Архитектура плагина, ADR, границы plugin/project layers, декомпозиция | Нетривиальный дизайн, публичный контракт, generated-state migration | Не реализует role-owned production changes | `AGENTS.md`, charter, `memory/project-map.md`, `memory/invariants.md`, `memory/decisions.md` | нет | `$qtim-brainstorm` до ADR; `$qtim-grill` и обязательный clean-context Sol stress-test каждого ADR |
| Testing | `qtim-testing` | Repo validation, schema/placeholder/link/model checks, воспроизводимые дефекты | Любая содержательная правка плагина | Не исправляет source вне test/validation scripts без новой задачи | `AGENTS.md`, charter, `memory/project-map.md`, `memory/commands.md`, `memory/bug-log.md` | нет | `$qtim-debug-loop` для flaky или нетривиального repro; сохраняет command evidence |
| Reviewer | `qtim-reviewer` | Финальный read-only gate по diff, инвариантам и validation evidence | После реализации или перед release | Не пишет production/source content | `AGENTS.md`, charter, `memory/invariants.md`, `memory/commands.md`, `memory/review-report.md`, `memory/bug-log.md` | нет | Findings только с `file:line`; risk-based independent review; явный verdict |
| Product | `qtim-product` | Intake, fast brief или полный PRD/decomposition/estimate/plan | `$qtim-feature`, продуктовая развилка, handoff | Не пишет plugin source, TOML реализации или тесты | `AGENTS.md`, PM-блок charter, `memory/decisions.md`, product-memory если создана, текущий feature slug | нет | Grounded evidence, checkpoints, вертикальные slices, S/M/L/XL без выдуманных сроков |
| Explorer | built-in `explorer` | Широкое read-only исследование и первичная классификация | Broad search, codebase mapping | Не редактирует файлы | Bounded context из main thread | нет | Запускается main thread на Luna/medium; вывод advisory |

## Model matrix

| Назначение | Model | Reasoning |
|---|---|---|
| Team lead / main thread | `gpt-5.6-sol` | `ultra` |
| `qtim-architect` | `gpt-5.6-sol` | `xhigh` |
| `qtim-testing` | `gpt-5.6-terra` | `medium` |
| `qtim-reviewer` | `gpt-5.6-sol` | `xhigh` |
| `qtim-product` | `gpt-5.6-sol` | `high` |
| Built-in `explorer` | `gpt-5.6-luna` | `medium` |
| Ephemeral ADR adversary | `gpt-5.6-sol` | `xhigh`; `max` только для необратимого решения, затрагивающего документированный инвариант |

Для custom roles источником истины служит соответствующий TOML. Пара `model` + `model_reasoning_effort` атомарна; `inherit`, half-pair и молчаливая замена slug запрещены. qtim не переключает профиль уже открытой задачи.

## Доменные инварианты

1. Репозиторий остаётся Codex-native: не добавлять `.claude/*`, `.claude-plugin/*`, Claude slash commands или Claude Agent Teams primitives.
2. Plugin layer владеет qtim `SessionStart` и `SubagentStop`; project `.codex/hooks.json` предназначен только для optional `PostToolUse` или уже существующих пользовательских hooks.
3. Generated target-project state использует `.codex/team-charter.md`, `.codex/agents/*.toml`, `memory/` и секцию в `AGENTS.md`.
4. Dev и PM дорожки charter живут только между парными `qtim:track:*` markers; обновление одной дорожки не затирает вторую и ручные правки вне markers.
5. Сгенерированные файлы self-contained и не ссылаются на plugin-internal относительные пути.
6. Ролевые model-профили задаются точной атомарной парой; пользовательские overrides при миграции сохраняются до показанного diff и подтверждения.
7. Main thread владеет fan-out; child agents не создают рекурсивные qtim-команды. Результаты subagent thread advisory до проверки.
8. Durable решения, review findings и воспроизводимые баги фиксируются в `memory/`, а не остаются только в чате.
9. Изменение generated project state требует version bump, `CHANGELOG.md` и migration section в `plugins/qtim/reference/upgrade-notes.md`; при отсутствии миграции это явно отмечается.
10. Deploy выполняется только conventional commit и `git push origin main` из этого source-of-truth репозитория.

## Обязательный ADR stress-test

Этот design gate включён независимо от independent code review.

1. Architect создаёт ADR только для дорогого в откате решения с реальным trade-off и сначала проводит `$qtim-grill`.
2. До approval main thread запускает новый read-only thread без истории на `gpt-5.6-sol` + `xhigh`. Если решение одновременно необратимо и затрагивает документированный инвариант, используется `max`.
3. Оппонент получает только ADR, затронутые инварианты и проверяемые paths; он ищет нарушения инвариантов, пропущенные альтернативы, rollback/data-loss/security failure modes и open questions.
4. Architect проверяет каждый finding по source, charter и `memory/`, затем обновляет ADR.
5. ADR содержит `adr-stress-test: sol-adversary (xhigh|max) — N findings, M учтено`. Техническая недоступность фиксируется как `adr-stress-test: skipped — <reason>` и не считается пройденным gate.

## Independent review кода

Independent read-only review обязателен, если фактический diff совпадает хотя бы с одним пунктом:

- security/auth/tenant-scope visibility;
- money/billing/account state;
- documented domain invariants or public contracts;
- data-transform or destructive migrations;
- critical browser flows before release;
- high-risk performance/reliability changes;
- другое доказанно hard-to-rollback изменение.

Для low-risk diff, ограниченного copy/styles/documentation или внутренним refactor без изменения контрактов и инвариантов, reviewer может пропустить отдельный thread и записывает `independent review: skipped (low-risk diff)`. Для money-critical работы при доступном runtime требуются две независимые трассировки.

Узкий prompt review:

```text
You are an independent read-only reviewer.
Scope: <files/diff/ADR/feature>.
Read first: AGENTS.md, .codex/team-charter.md, memory/invariants.md.
Do not edit files.
Check correctness, security/authorization, visibility, idempotency,
race conditions, missing tests, rollback and error states.
For each grounded finding return file:line, severity P0-P3,
invariant/rule and concrete fix. Mark hypotheses explicitly.
```

Main thread открывает каждую указанную строку, подтверждает или отклоняет finding, маршрутизирует подтверждённые blockers и обновляет `memory/review-report.md`. Недоступный review фиксируется как skipped/failure и никогда не называется passed.

## Working rules

- qtim workflow требует явного вызова skill или прямой просьбы пользователя. Sol/Ultra team-lead может делегировать только внутри разрешённого scope.
- Execution depth: A Direct, B Single subagent, C Lazy team, D Full team-up. Его выбирает main thread по глубине координации, а не числу ролей.
- Custom agents используются после загрузки новой задачей Codex. При недоступности роли допустим `worker` с inline bounded instructions; broad read-heavy поиск выполняет built-in `explorer` на Luna/medium.
- Main thread проверяет доступные descendants перед повторным spawn, соблюдает runtime thread cap, разделяет write scopes и закрывает больше не нужные threads.
- Child agents возвращают запрос на дополнительную роль main thread и сами не создают qtim descendants.
- Незавершённый эпик переносится через `memory/epic-state.md`: `$qtim-team-down` записывает, `$qtim-team-up` читает и предлагает продолжить.
- `$qtim-team-retro` добавляет уроки в `memory/retro-log.md` и `memory/lessons.md`; эти файлы создаются по мере надобности.
- Team lead сообщает outcome и verification evidence, а не внутренний agent chatter.

## Memory layout

- `memory/MEMORY.md` — индекс и правила памяти.
- `memory/project-map.md` — структура и владельцы областей.
- `memory/commands.md` — проверенные команды.
- `memory/safety.md` — опасные операции и release-ограничения.
- `memory/invariants.md` — доменные и архитектурные инварианты.
- `memory/decisions.md` — реестр решений и указателей на утверждённые feature artifacts.
- `memory/review-report.md` — подтверждённые/отклонённые review findings.
- `memory/bug-log.md` — воспроизведение, evidence, fix и retest.
- `memory/epic-state.md`, `memory/retro-log.md`, `memory/lessons.md` — создаются workflows по мере надобности.
- `memory/product-map.md`, `memory/product-actors.md`, `memory/product-glossary.md`, `memory/product-metrics.md` — создаются `$qtim-product-onboard`; product читает их, если они существуют.

<!-- qtim:track:dev:start -->
## Dev track

### Autonomy и intake

Режим: **design approval first**. Для нетривиальной, необратимой, product-visible, public-contract, security или generated-state migration работы сначала готовится design brief/ADR и запрашивается approval. После approval реализация, validation и review идут автономно до результата, если не возникла новая развилка.

Team lead классифицирует задачу как feature, bug, refactor, audit, design или support и выбирает глубину:

- A Direct — очевидная локальная правка;
- B Single subagent — одна bounded роль;
- C `$qtim-team-lazy` — несколько ролей, один проход;
- D `$qtim-team-up` — implement -> test -> fix -> retest -> review.

Компактный roster: architect, testing, reviewer. Database/frontend роли отсутствуют, потому что соответствующих слоёв в проекте нет.

### Dev pipeline

1. Сверить задачу с `AGENTS.md`, charter и `memory/`.
2. Для нетривиальной работы architect готовит design brief; настоящий ADR проходит оба stress-test pass.
3. После approval назначить disjoint scope исполнителю в main thread или bounded worker.
4. Testing запускает релевантные JSON и repo-local проверки, сохраняет точные команды и output.
5. Reviewer проверяет diff, инварианты, отсутствие случайных изменений и применимость independent review.
6. Main thread подтверждает findings, доводит gates до зелёного состояния и обновляет память.

Done означает: запрошенное поведение/документация готовы, релевантные validation scripts зелёные, placeholders/links/model pairs/hooks schema проверены, reviewer дал `APPROVED`, а durable решения записаны.
<!-- qtim:track:dev:end -->

<!-- qtim:track:pm:start -->
## PM track

### Принцип и артефакты

PM track документирует, dev track реализует. `$qtim-feature` создаёт `docs/features/<slug>/`; setup не создаёт этот каталог заранее. Каждый артефакт имеет `Feature`, `Slug`, `Status`, дату и append-only секцию `История изменений`. Статусы: `Draft -> Approved -> In Development -> Done`.

После Intake main thread предлагает один путь:

- **Fast-path** — S/M, одна фаза, нет Fork Test-развилок. Выход: `intake.md` и единый `feature-brief.md`.
- **Полный трек** — L/XL, несколько фаз или хотя бы одна необратимая/product/security/public-contract развилка. Выход: `intake.md`, `prd.md`, `decomposition.md`, `estimate.md`, `plan.md`.

Если в fast-path обнаружена развилка или многофазность, сохраняется `intake.md`, незавершённый brief преобразуется в `prd.md`, а переход фиксируется в истории.

### Стадии и checkpoints

| Стадия | Результат | Checkpoint |
|---|---|---|
| Intake | `intake.md`: проблема, outcome, success, constraints, non-goals, выбранный путь | Пользователь подтверждает понимание и путь |
| Fast-path | `feature-brief.md`: PRD-lite, grounded work items, S/M evidence, одна фаза, gates, rollback, Done, handoff | Пользователь утверждает brief целиком |
| PRD | `prd.md`: цели, не-цели, сценарии, acceptance criteria, UX, метрики, риски | Пользователь утверждает PRD |
| Decomposition | `decomposition.md`: vertical work items, DRI, contributing roles/layers, files | Общий checkpoint с estimate |
| Estimation | `estimate.md`: layer evidence, DRI synthesis, S/M/L/XL, confidence, risks | Одним решением утверждаются work items и оценки |
| Plan | `plan.md`: вертикальные фазы, gates, rollback и handoff | Финальное approval |
| Handoff | Указатель в `memory/decisions.md` и prompt реализации | Без отдельного checkpoint |

### Grounding и consult

- В полном треке действует selective dev-consult: architect проверяет слои, data flow и инварианты; testing консультирует по validation surface. Привлекаются только реально затронутые роли. Consult read-only и возвращает files, integration points, похожие изменения и риски.
- Для broad read-heavy поиска используется built-in `explorer`; веер всех ролей по привычке запрещён.
- Work item и фаза — проверяемый вертикальный срез с одним DRI по главной acceptance boundary и списком contributing roles/layers.
- Каждая contributing роль оценивает свой layer slice с evidence. DRI синтезирует единый S/M/L/XL для item с confidence и integration risk; размеры не складываются механически.
- XL означает разрезать item и вернуться к decomposition. Часы и дни без проектного evidence не назначаются.
- Fast-path не требует fan-out: main thread обосновывает S/M по ключевым файлам, тестам, integration points или reference class. Недостаточное evidence или правдоподобный L/XL переводит фичу в полный трек.
- Широкий механический rename/retype планируется через expand-contract: новая форма рядом со старой -> миграция call sites небольшими пачками с зелёными gates -> удаление старой формы последним item.

### Handoff contract

Полный `plan.md` ссылается на PRD и содержит готовый prompt для `$qtim-team-up` или `$qtim-team-lazy`. Fast-path `feature-brief.md` является единым источником scope, acceptance criteria, gates и prompt для `$qtim-team-lazy`. Реализующая команда переводит документы в `In Development`, затем в `Done`; отклонения и новые edge cases добавляются в историю планового документа.

`memory/decisions.md` хранит одну строку-указатель на каждую утверждённую фичу. Product перед стартом читает product-memory, если она создана `$qtim-product-onboard`: `memory/product-map.md`, `memory/product-actors.md`, `memory/product-glossary.md`, `memory/product-metrics.md`.
<!-- qtim:track:pm:end -->
