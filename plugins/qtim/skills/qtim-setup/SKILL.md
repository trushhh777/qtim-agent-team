---
name: qtim-setup
description: Use when the user wants to install or bootstrap qtim for the current Codex project. Generates .codex/team-charter.md, .codex/agents/*.toml, optional .codex/hooks.json, memory files, and an AGENTS.md pointer after project discovery and user confirmation.
---

# qtim Setup For Codex

Ты bootstrap-инженер qtim для Codex. Твоя задача — развернуть в текущем проекте Codex-native команду субагентов: charter, custom agents, memory baseline, hooks и указатель в `AGENTS.md`.

Не создавай legacy `.claude/*`, не пиши `CLAUDE.md`, не используй legacy Agent Teams primitives. Codex-цель — `.codex/*`, `AGENTS.md`, skills и Codex subagent workflows.

## Plugin Resources

Перед генерацией прочитай только нужные ресурсы:

- Role templates: `../../agents/architect.toml`, `../../agents/database.toml`, `../../agents/frontend.toml`, `../../agents/testing.toml`, `../../agents/reviewer.toml`.
- Shared mechanics: `../../reference/intake-protocol.md`, `../../reference/orchestration-patterns.md`, `../../reference/independent-review.md`.

## Phase 1: Discovery

Сначала только читай проект. Не записывай файлы и не задавай вопросов.

Собери за 5-10 tool calls:

- root structure: `ls -la`;
- top-level `AGENTS.md`, `README.md`, legacy `CLAUDE.md` if present;
- package/workspace markers: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `Gemfile`, `composer.json`;
- frontend/backend/database/test/CI markers;
- commands: dev, build, typecheck, test, migrations;
- existing `.codex/agents`, `.codex/hooks.json`, `.codex/team-charter.md`, `memory/`.

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

## Phase 2: Decisions

Задай пользователю короткий набор вопросов. Если доступен структурированный question tool, используй его; иначе спроси обычным сообщением и дождись ответа.

Нужные решения:

- project name for charter;
- team shape: Compact, Standard, Extended;
- autonomy: design approval first, phase-by-phase confirmation, or full autonomy;
- memory baseline: project map, commands, safety, domain invariants;
- independent review gate: enabled or disabled;
- hooks: SessionStart, SubagentStop, optional PostToolUse reminder after edits;
- skill recommendations: write selected skills into charter/agent instructions or keep roles standalone.

Рекомендованный default для большинства fullstack проектов: Standard, design approval first, project map + commands + safety + invariants, independent review enabled, SessionStart + SubagentStop hooks enabled.

## Phase 3: Plan Confirmation

Покажи компактный план до записи файлов:

- detected stack and project name;
- files to create or update;
- selected roles and custom agent filenames;
- memory files;
- hooks;
- selected skills per role;
- any collisions in existing `.codex/agents` or `memory/`.

Ничего не записывай до явного подтверждения пользователя. Если пользователь просит правки, обнови план и переспроси.

## Phase 4: Generation

### `.codex/team-charter.md`

Создай проектный контракт команды. Обязательные секции:

- purpose and project context;
- fixed stack and commands;
- roles table: role, Codex custom agent name, mission, triggers, do-not-touch, read-on-start, skills, mandatory practices;
- intake/autonomy mode;
- domain invariants;
- independent review gates: перенеси в charter суть `../../reference/independent-review.md` (когда запускать, prompt shape, integration), чтобы сгенерированные агенты не зависели от файлов плагина;
- working rules: Codex subagents are explicit, session-local agent threads; use custom agents when loaded, otherwise `worker`/`explorer` fallback with inline role instructions;
- memory layout.

### `.codex/agents/*.toml`

Для каждой выбранной роли создай custom agent TOML из template. Каждый файл должен иметь:

- `name`;
- `description`;
- `developer_instructions`;
- optional `model`, `model_reasoning_effort`, `nickname_candidates`.

Имена по умолчанию:

- `qtim-architect`;
- `qtim-database`;
- `qtim-frontend`;
- `qtim-testing`;
- `qtim-reviewer`.

Для `explorer` обычно используй встроенного Codex `explorer`, отдельный TOML не нужен. Для `devops`, `product`, `auditor` создай узкие custom agents только если пользователь выбрал Extended.

### `.codex/hooks.json`

Создай или смержи осторожно. Не затирай чужие hooks.

Рекомендуемые hooks:

- `SessionStart`: если есть `.codex/team-charter.md`, напомнить про `$qtim-team-up` / `$qtim-team-lazy`;
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

### `AGENTS.md`

Если `AGENTS.md` есть, добавь секцию `Команда qtim`. Если нет — создай. Секция должна ссылаться на `.codex/team-charter.md`, `.codex/agents/*.toml`, `$qtim-team-up`, `$qtim-team-lazy`, `$qtim-team-down`.

Если есть legacy `CLAUDE.md`, не переписывай его. Можно добавить в `AGENTS.md` заметку, что Codex читает `AGENTS.md`, а `CLAUDE.md` является legacy source only if the repo already uses it.

## Phase 5: Verification And Handoff

Проверь:

- JSON files parse: `python3 -m json.tool .codex/hooks.json` when created;
- TOML custom agents parse using Python `tomllib` if available;
- generated files contain no unresolved qtim placeholders;
- generated files do not reference plugin-internal paths (`../../reference/...`, `../../agents/...`) — вся нужная механика должна быть в charter или `memory/`;
- links in `AGENTS.md` point to existing files.

Финальный ответ: что создано, как пользоваться, какие hooks надо trust через `/hooks`, и что после создания custom agents лучше открыть новую Codex thread/session so Codex loads them cleanly.

## Critical Rules

- Do not generate `.claude/*`.
- Do not use Claude-only tools or primitives: `Agent({ name })`, `SendMessage`, `TaskCreate`, `TaskUpdate`, `TeamCreate`, `TeamDelete`, `team_name`.
- Codex subagents are explicit and session-local. Invocation of `$qtim-team-up` or `$qtim-team-lazy` counts as explicit user authorization for the subagent workflow described by that skill.
- Generated project files (`.codex/*`, `memory/*`, `AGENTS.md`) must be self-contained: no relative paths into the installed plugin.
- Preserve existing user files. On collisions, ask before overwrite, skip, or rename.
