---
name: qtim-setup
description: Use when the user wants to install or bootstrap qtim for the current Codex project. Asks for the user role (Developer, PM/Analyst, or both), then generates .codex/team-charter.md with track blocks, .codex/agents/*.toml, optional .codex/hooks.json, memory files, and an AGENTS.md pointer after project discovery and user confirmation.
---

# qtim Setup For Codex

Ты bootstrap-инженер qtim для Codex. Твоя задача — развернуть в текущем проекте Codex-native команду субагентов: charter, custom agents, memory baseline, hooks и указатель в `AGENTS.md`.

Не создавай legacy `.claude/*`, не пиши `CLAUDE.md`, не используй legacy Agent Teams primitives. Codex-цель — `.codex/*`, `AGENTS.md`, skills и Codex subagent workflows.

## Plugin Resources

Перед генерацией прочитай только нужные ресурсы:

- Role templates: `../../agents/architect.toml`, `../../agents/database.toml`, `../../agents/frontend.toml`, `../../agents/testing.toml`, `../../agents/reviewer.toml`, `../../agents/product.toml`.
- Model policy: `../../reference/model-profiles.md`.
- Shared mechanics: `../../reference/intake-protocol.md`, `../../reference/orchestration-patterns.md`, `../../reference/independent-review.md`, `../../reference/feature-pipeline.md`.
- Plugin version для stamps: поле `version` из `../../.codex-plugin/plugin.json`.

## Phase 1: Discovery

Сначала только читай проект. Не записывай файлы и не задавай вопросов.

Собери за 5-10 tool calls:

- root structure: `ls -la`;
- top-level `AGENTS.md`, `README.md`, legacy `CLAUDE.md` if present;
- package/workspace markers: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `Gemfile`, `composer.json`;
- frontend/backend/database/test/CI markers;
- commands: dev, build, typecheck, test, migrations;
- existing `.codex/agents`, `.codex/hooks.json`, `.codex/team-charter.md`, `memory/`;
- existing `docs/features/` и track-маркеры `qtim:track:dev` / `qtim:track:pm` в существующем charter.

Сведи placeholders role templates к фактам проекта:

- `{{FRONTEND_FRAMEWORK}}`
- `{{BACKEND}}`
- `{{DATABASE}}`
- `{{FILE_STORAGE}}`
- `{{BUILD_CMD}}`
- `{{TYPECHECK_CMD}}`
- `{{TEST_RUNNER}}`
- `{{E2E_TOOL}}`

Если технологии нет, вырежи стек-условные требования из соответствующего agent template при генерации.

## Phase 1b: Codex Skills, Plugins, MCP Matching

Подбери уже доступные Codex skills из текущего контекста под стек и роли. Не устанавливай ничего сам.

Приоритеты:

- frontend: frontend/design/framework skills;
- backend/API: backend/API/security/error-handling skills;
- database: database/query/security skills;
- testing: browser/e2e/accessibility skills;
- reviewer: code review/security/performance skills.

Плагины и MCP только рекомендуй в финале. Для приватных систем и live-data источников предпочитай Codex connectors/MCP вместо веб-поиска.

Best-effort проверь пары role templates по локальному model catalog, который показывает текущий Codex (`codex debug models`, если команда доступна, или model controls текущего runtime). Не делай сетевой lookup частью setup. Catalog доступен и пары нет -> предложи наследование; catalog недоступен -> пометь профиль unverified в плане и по умолчанию удали оба поля, если пользователь не подтвердил pin.

## Phase 2: Decisions

Задай пользователю короткий набор вопросов. Если доступен структурированный question tool, используй его; иначе спроси обычным сообщением и дождись ответа.

**Первый вопрос — роль пользователя:**

- **Developer** — команда разработки: architect/database/frontend/testing/reviewer, workflow `$qtim-team-up` / `$qtim-team-lazy`;
- **PM/Analyst** — продуктовый трек: роль `qtim-product` и pipeline `$qtim-feature` (хотелка -> PRD -> декомпозиция -> оценка -> план) с артефактами в `docs/features/`;
- **Оба** — обе дорожки в одном charter.

Роль гейтит остальные вопросы. Если charter уже существует и содержит только другой track, предложи дописать недостающий track, не пересоздавая существующий.

Нужные решения (Developer и Оба — полный набор; PM/Analyst — только project name, autonomy, memory baseline, hooks):

- project name for charter;
- team shape: Compact, Standard, Extended (только dev track);
- autonomy: design approval first, phase-by-phase confirmation, or full autonomy; для PM track это режим checkpoints конвейера;
- memory baseline: project map, commands, safety, domain invariants;
- independent review gate: enabled or disabled (только dev track; при disabled charter получает секцию-заглушку «выключен», а independent-review-требования шаблонов вырезаются из генерируемых агентов — включить позже можно повторным `$qtim-setup`);
- hooks: SessionStart, SubagentStop, optional PostToolUse reminder after edits;
- skill recommendations: write selected skills into charter/agent instructions or keep roles standalone.

PM/Analyst-состав команды не спрашивается — он определяется стеком: `qtim-product` + `qtim-architect` + профильные `qtim-database`/`qtim-frontend`/`qtim-testing` (какие есть в стеке) + built-in `explorer`. Dev-роли нужны PM-конвейеру как read-only консультанты для точной декомпозиции и оценки, даже если пользователь код не пишет. `qtim-reviewer` в PM-only setup не генерируется — поэтому PM-состав рассчитан на конвейер документов, не на реализацию: перед запуском handoff-плана в разработку (`$qtim-team-up`, режим D с петлёй через reviewer) состав дополняется dev-дорожкой повторным `$qtim-setup` (он дописывает, не пересоздаёт). Эту пометку зафиксируй в PM track block charter.

Рекомендованный default для большинства fullstack проектов: Standard, design approval first, project map + commands + safety + invariants, independent review enabled, SessionStart + SubagentStop hooks enabled.

Модельный профиль не является отдельным обязательным вопросом: по умолчанию используй пары `model` + `model_reasoning_effort` из templates и покажи их в плане. Спрашивай только если пользователь просит override или точный slug недоступен. `Max`, `Ultra` и Fast — настройки главного task/session; setup не включает их сам.

## Phase 3: Plan Confirmation

Покажи компактный план до записи файлов:

- detected stack and project name;
- selected tracks (dev / pm / оба) и что будет добавлено или обновлено между track-маркерами charter, а что останется нетронутым;
- files to create or update;
- selected roles and custom agent filenames;
- model/reasoning profile каждой роли и fallback на наследование главного task, если точный slug недоступен;
- memory files;
- hooks;
- selected skills per role;
- any collisions in existing `.codex/agents` or `memory/`.

Ничего не записывай до явного подтверждения пользователя. Если пользователь просит правки, обнови план и переспроси.

## Phase 4: Generation

### `.codex/team-charter.md`

Первой строкой charter поставь version stamp с версией плагина: `<!-- qtim-version: X.Y.Z -->`. По нему `$qtim-update` и SessionStart hook определяют версию команды.

Создай проектный контракт команды. Общие секции (вне track-блоков):

- purpose and project context;
- fixed stack and commands;
- roles table: role, Codex custom agent name, mission, triggers, do-not-touch, read-on-start, skills, mandatory practices;
- domain invariants;
- independent review gates — при включённом гейте перенеси в charter суть `../../reference/independent-review.md` (когда запускать, prompt shape, integration), чтобы сгенерированные агенты не зависели от файлов плагина; при выключенном — секция из одной строки-заглушки «independent review выключен (выбор setup); включить — повторный `$qtim-setup`», по ней `$qtim-team-up` и роли понимают, что гейт не настроен;
- working rules: qtim subagent workflows авторизуются явным вызовом skill или прямой просьбой, а сами subagents остаются task-scoped agent threads без скрытой постоянной команды; выбранный пользователем `Ultra` может делегировать внутри разрешённого scope, но не меняет execution depth A/B/C/D и не разрешает child agents рекурсивно поднимать команду; main thread проверяет доступные descendants перед повторным spawn и уважает runtime thread cap; модель/reasoning/Fast главного task qtim не переключает; use custom agents when loaded, otherwise `worker`/`explorer` fallback with inline role instructions; session handoff: незавершённый эпик фиксируется в `memory/epic-state.md` (`$qtim-team-down` пишет, `$qtim-team-up` читает и предлагает продолжить), уроки retro — в `memory/retro-log.md` и `memory/lessons.md`;
- memory layout.

Track-блоки — между HTML-маркерами, по выбранным ролям:

```text
<!-- qtim:track:dev:start -->
...dev track: intake/autonomy mode, специфичные dev-правила...
<!-- qtim:track:dev:end -->

<!-- qtim:track:pm:start -->
...pm track: feature pipeline...
<!-- qtim:track:pm:end -->
```

PM track block должен содержать перенесённую суть `../../reference/feature-pipeline.md` (стадии и checkpoints, схема `docs/features/<slug>/` со статусами Draft -> Approved -> In Development -> Done, правило dev-consult на декомпозиции/оценке, правила grounded-оценки S/M/L/XL, handoff contract) — сгенерированные агенты не зависят от файлов плагина. При PM-only составе — также пометку из Phase 2: перед реализацией handoff-плана состав дополняется dev-дорожкой повторным `$qtim-setup`.

Re-run rule: при повторном setup заменяй содержимое только между маркерами своего track; чужой track block и ручные правки пользователя вне маркеров не трогай. В общей roles table добавляй строки, не удаляя существующие.

### `.codex/agents/*.toml`

Для каждой выбранной роли создай custom agent TOML из template. Первой строкой каждого сгенерированного файла добавь комментарий `# qtim-version: X.Y.Z` с версией плагина. Каждый файл должен иметь:

- `name`;
- `description`;
- `developer_instructions`;
- optional `model`, `model_reasoning_effort`, `nickname_candidates`.

**Пару `model` + `model_reasoning_effort` копируй из template дословно — не подставляй значения из собственных знаний** (боевой инцидент: сгенерированный `model = "gpt-5"` не существует, и все субагенты не стартовали). Переопределяй только по явному выбору пользователя. Если локальный catalog подтверждает, что точный slug/effort из template недоступен, либо catalog недоступен и пользователь не подтвердил pin, **удали оба поля**: агент унаследует модель и reasoning главного task. Не оставляй pinned reasoning без pinned model и не включай `max`, `ultra` или `service_tier = "fast"` без явного выбора пользователя.

**Gate-условные блоки шаблонов:** требования independent review gate у reviewer/architect/database (блок «Independent review gate», пункты чеклистов про independent review, секция отчёта «Independent review») переноси только при включённом гейте; при выключенном вырезай целиком, как стек-условные — роли не должны требовать гейт, от которого пользователь отказался.

Имена по умолчанию:

- `qtim-architect`;
- `qtim-database`;
- `qtim-frontend`;
- `qtim-testing`;
- `qtim-reviewer`;
- `qtim-product` (PM track).

Состав по трекам: Developer — architect/database/frontend/testing/reviewer по team shape; PM/Analyst — `qtim-product` + `qtim-architect` + профильные dev-роли по стеку (без reviewer); Оба — объединение. Для `explorer` обычно используй встроенного Codex `explorer`, отдельный TOML не нужен. Для `devops`, `auditor` создай узкие custom agents только если пользователь выбрал Extended.

### `.codex/hooks.json`

Создай или смержи осторожно. Не затирай чужие hooks.

Рекомендуемые hooks:

- `SessionStart`: если есть `.codex/team-charter.md`, показать версию команды из stamp и напомнить про `$qtim-feature` / `$qtim-team-up` / `$qtim-team-lazy` / `$qtim-update` (упоминай skills сгенерированных треков; образец команды — в hooks.json плагина);
- `SubagentStop`: напомнить main agent проверить реальные артефакты subagent thread;
- optional `PostToolUse` matcher `Edit|Write|apply_patch`: короткое напоминание про typecheck/build, без долгого запуска.

Codex hooks требуют trust review через `/hooks`; упомяни это в handoff.

### `memory/`

Создай `memory/MEMORY.md` как индекс и выбранные файлы:

- `memory/project-map.md`;
- `memory/commands.md`;
- `memory/safety.md`;
- `memory/invariants.md`;
- `memory/decisions.md`;
- `memory/review-report.md`;
- `memory/bug-log.md`.

Файлы `memory/epic-state.md`, `memory/retro-log.md` и `memory/lessons.md` setup не создаёт — их создают `$qtim-team-down` и `$qtim-team-retro` по мере надобности; упомяни их назначение в `MEMORY.md`.

При PM track уточни в `MEMORY.md`, что `decisions.md` служит также реестром указателей на утверждённые фичи в `docs/features/<slug>/`. Саму директорию `docs/features/` setup не создаёт — её создаёт `$qtim-feature` per-slug. Продуктовую память (`memory/product-map.md`, `product-actors.md`, `product-glossary.md`, `product-metrics.md`) setup тоже не создаёт — её наполняет `$qtim-product-onboard`; упомяни эти файлы в PM track block charter как read-on-start роли `product` («если созданы»).

### `AGENTS.md`

Если `AGENTS.md` есть, добавь секцию `Команда qtim`. Если нет — создай. Секция должна ссылаться на `.codex/team-charter.md`, `.codex/agents/*.toml`, `$qtim-team-up`, `$qtim-team-lazy`, `$qtim-team-down`, `$qtim-team-retro` (ретроспектива эпика до team-down), `$qtim-update` (проверка версии и обновление команды), `$qtim-onboard` (глубокий онбординг dev-памяти) и `$qtim-doctor` (диагностика), а при PM track — на `$qtim-feature` и конвенцию `docs/features/<slug>/`.

Если есть legacy `CLAUDE.md`, не переписывай его. Можно добавить в `AGENTS.md` заметку, что Codex читает `AGENTS.md`, а `CLAUDE.md` является legacy source only if the repo already uses it.

## Phase 5: Verification And Handoff

Проверь:

- JSON files parse: `python3 -m json.tool .codex/hooks.json` when created;
- TOML custom agents parse using Python `tomllib` if available;
- пара `model` + `model_reasoning_effort` каждого сгенерированного TOML совпадает с template, является явно подтверждённым пользователем catalog-supported override или оба поля удалены; одинокое поле, неподтверждённый догаданный alias или слаг вида `gpt-5` без минорной версии — ошибка;
- generated files contain no unresolved qtim placeholders;
- generated files do not reference plugin-internal paths (`../../reference/...`, `../../agents/...`) — вся нужная механика должна быть в charter или `memory/`;
- track-маркеры `qtim:track:*` в charter парные; при re-run оба track block целы, PM block содержит механику pipeline;
- при выключенном independent review: charter содержит секцию-заглушку «выключен», в сгенерированных TOML нет требований independent review gate;
- version stamps на месте: `<!-- qtim-version: ... -->` в charter, `# qtim-version: ...` в каждом сгенерированном TOML, версия совпадает с `../../.codex-plugin/plugin.json`;
- links in `AGENTS.md` point to existing files.

Финальный ответ: что создано, как пользоваться, какие hooks надо trust через `/hooks`, и что после создания custom agents лучше открыть новую задачу Codex, чтобы она загрузила их чисто. На существующей кодовой базе порекомендуй следом прогнать `$qtim-onboard` (dev track) — глубокое наполнение `memory/` картой, инвариантами и конвенциями, а при PM track — `$qtim-product-onboard`, который наполнит продуктовую память (разделы, акторы, словарь, аналитика), без которой intake/PRD опираются только на ответы пользователя. Упомяни `$qtim-doctor` как первый шаг при «что-то не работает».

## Critical Rules

- Do not generate `.claude/*`.
- Do not use Claude-only tools or primitives: `Agent({ name })`, `SendMessage`, `TaskCreate`, `TaskUpdate`, `TeamCreate`, `TeamDelete`, `team_name`.
- qtim subagent workflows require explicit user authorization through the skill or a direct delegation request. Root `Ultra` may proactively delegate only inside that authorized scope. Agent threads are task-scoped; verify runtime descendants before reuse, and never imply a hidden persistent team.
- Generated project files (`.codex/*`, `memory/*`, `AGENTS.md`) must be self-contained: no relative paths into the installed plugin.
- При повторном запуске обновляй только блок своего track между маркерами `qtim:track:*`; второй track и ручные правки пользователя сохраняются.
- Preserve existing user files. On collisions, ask before overwrite, skip, or rename.
