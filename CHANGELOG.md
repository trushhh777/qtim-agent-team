# Changelog

Версии соответствуют `version` в `plugins/qtim/.codex-plugin/plugin.json` (semver).

## 2.1.0 — 2026-07-02

### Добавлено

- **Ролевой вход**: `$qtim-setup` первым вопросом спрашивает роль пользователя (Developer / PM-Analyst / Оба) и генерирует команду под неё; charter стал track-aware — dev и PM треки живут между маркерами `qtim:track:*`, повторный setup обновляет только свой трек.
- **Skill `$qtim-feature`** — PM-конвейер: intake -> PRD -> декомпозиция -> оценка -> план -> handoff в `$qtim-team-up`/`$qtim-team-lazy`; checkpoints у пользователя на каждой стадии; resume по статусам артефактов при существующем slug.
- **Шаблон `agents/product.toml`** (`qtim-product`) — product/analyst роль: PRD, декомпозиция, сведение оценок, план; production code не пишет.
- **`reference/feature-pipeline.md`** — контракт конвейера: артефакты и статусная машина, правила grounded-оценки (S/M/L/XL + confidence + evidence, без выдуманных часов), handoff contract. Setup переносит суть в charter (self-contained).
- **Конвенция `docs/features/<slug>/`** — intake/prd/decomposition/estimate/plan версионируются в docs; в `memory/decisions.md` — только строки-указатели.
- **Dev-consult на декомпозиции и оценке**: точность описания задачи обеспечивают профильные dev-агенты (architect + database/frontend/testing по слоям, read-only) — размер work item даёт владелец слоя, PM-роль сводит; поэтому PM-only setup тоже генерирует dev-роли по стеку (без reviewer).

### Изменено

- SessionStart hook упоминает `$qtim-feature` (текст остался статическим: grep-условие по track-маркеру спрятало бы skill в charter'ах 2.0.0 без маркеров).
- `$qtim-team-up` / `$qtim-team-lazy` читают `docs/features/<slug>/plan.md` и `prd.md` как источник scope и acceptance criteria и обновляют Status артефактов по завершении.
- README и plugin.json переписаны под двух-ролевую концепцию; `defaultPrompt` включает feature pipeline.
- Публичные repository/homepage/install-ссылки указывают на `trushhh777/qtim-agent-team`.

## 2.0.0 — 2026-07-02

### Исправлено (pre-release ревью)

- **Невалидный YAML frontmatter `qtim-team-lazy`** — незакавыченное `description` с `:` внутри роняло ingestion-валидатор Codex; значение взято в кавычки.
- **`reviewer.toml` ссылался на `../../reference/independent-review.md`** — шаблон копируется setup'ом в `.codex/agents/` целевого проекта, где внутренние пути плагина не резолвятся (регрессия бага, чинившегося в 1.2.0); теперь ссылка на independent review gates в `.codex/team-charter.md`. В `qtim-setup` добавлено требование самодостаточности генерируемых файлов (Phase 4, Phase 5, Critical Rules).
- **CI не ловил оба класса багов**: добавлен `check_skills.py` (frontmatter всех SKILL.md, PyYAML с fallback-парсером), `check_codex_agents.py` теперь парсит TOML через `tomllib` (Python 3.11+) и запрещает `../`-пути в шаблонах агентов.

### Изменено

- Плагин полностью перенесён на Codex packaging: `.agents/plugins/marketplace.json` + `plugins/qtim/.codex-plugin/plugin.json`.
- Claude slash-команды `/qtim:*` заменены на Codex skills: `$qtim-setup`, `$qtim-team-up`, `$qtim-team-lazy`, `$qtim-team-down`.
- Claude Agent Teams runtime заменён на Codex subagent workflow: explicit spawn, session-local agent threads, custom agents в `.codex/agents/*.toml`.
- Шаблоны ролей перенесены из Claude agent Markdown/frontmatter в Codex custom agent TOML templates.
- `codex-consult.md` заменён на `independent-review.md`: в Codex больше нет внешнего "Codex second-opinion", review делает отдельный read-only agent thread.
- Generated project state теперь живёт в `.codex/team-charter.md`, `.codex/agents`, `.codex/hooks.json`, `memory/` и `AGENTS.md`; `.claude/*` больше не генерируется.
- README и repo instructions переписаны под Codex install/use flow.

### Удалено

- `.claude-plugin/*`, `plugins/qtim/.claude-plugin/*`, `plugins/qtim/commands/*` и Claude-only role templates.

### Добавлено

- Codex plugin manifest validation target.
- CI-проверка Codex custom agent TOML templates.
- Repo `AGENTS.md` с правилами поддержки Codex-native версии.

## 1.2.0 — 2026-07-02

### Исправлено

- **Workflow-примеры теряли данные между стадиями** (`reference/orchestration-patterns.md`): judge/synth/filter/classifier в паттернах 1, 3, 4, 5, 6 теперь получают результаты предыдущих стадий интерполяцией в промпт; добавлены жёсткое правило движка B и anti-pattern «судья вслепую».
- **Субагенты не находили протокол codex-consult**: setup теперь записывает в charter абсолютный путь к `reference/codex-consult.md` (плейсхолдер плагин-рута вне файлов плагина не резолвится); промпт спавна в team-up и шаблоны ролей ссылаются на путь из charter; в Standalone — на локальную копию.
- **Невалидный `permissions.deny` baseline** в setup: голые glob'ы (`.env*`, `~/.ssh/**`) заменены на формат `Tool(паттерн)` — `Read(./.env*)`, `Edit(./.env*)`, `Read(~/.ssh/**)`, `Edit(~/.ssh/**)`.
- **SubagentStop-hook плагина** срабатывал во всех проектах — теперь, как и SessionStart, только при наличии `.claude/team-charter.md`; в description честно помечен как advisory для человека (stdout SubagentStop в контекст модели не инжектится).
- **`tools` шаблонов ролей**: убраны несуществующие/упразднённые `Computer`, `MultiEdit` и двусмысленный `Task`; добавлены `TaskCreate`/`TaskUpdate`/`SendMessage`, которых требуют промпты ролей (баг-флоу tester'а, маршрутизация reviewer'а, нотификации db→front), а по итогам независимого ревью — ещё `Skill` во все роли (промпты предписывают mandatory-invoke skills) и `Write` reviewer'у (пишет review-report в `memory/`).
- **Дубль hooks**: Q7 SessionStart/SubagentStop генерируются только при Q6=Standalone — в Plugin-linked их уже даёт `hooks.json` плагина.
- **Universal skills больше не захардкожены** в team-up: фактический список — из charter («Правила работы»), недоступные в окружении skills в промпты спавна не включаются (mandatory-invoke несуществующего skill ломал старт ролей); при пустом списке строка опускается целиком. `brainstorming`/`grill-me` в шаблоне architect помечены «если доступен».
- Из PostToolUse-примера setup убран упразднённый `MultiEdit`; указатель канона в charter — `/qtim:team-up` вместо пути файла; в Standalone команды указываются локальными именами, а путь к codex-протоколу — абсолютным и на локальную копию; в перечень сохраняемого frontmatter (setup 4.2) добавлен `color`.
- Удалён несуществующий `$schema` из `marketplace.json`.

### Добавлено

- **CI-валидация** (`.github/workflows/validate.yml` + `.github/scripts/`): JSON-манифесты, запрет call-синтаксиса упразднённых примитивов, плейсхолдеры по белому списку (включая детектор деформированных — пробелы/нижний регистр), целостность относительных ссылок; push-триггер только для `main`, чтобы PR не гонял job дважды.
- `CHANGELOG.md`.
- Секция **Intake-режим** (ответ Q3) в структуре charter — раньше ответ было некуда записывать, а `intake-protocol.md` читает дефолты именно из charter.
- **Каркасы cross-cutting ролей** `devops`/`product`/`auditor` в setup 4.2 — Extended-состав больше не генерируется «с нуля».
- **Стек-условные пометки** в шаблонах ролей + явный список условных блоков и безусловного ядра в setup 4.2 (шаблоны несут терминологию RLS/presign/realtime, нерелевантную части стеков).
- Setup создаёт `.claude/agent-memory/<role>-agent/MEMORY.md` для ролей с включённой памятью (первый спавн больше не шумит ошибкой чтения).
- Рекомендация по выбору `model` per-роль в setup 4.2.
- Чеклист «при обновлении Claude Code» в `CLAUDE.md`.

## 1.1.x и ранее

См. `git log` (conventional commits): автоподбор skills и плагинов/MCP под стек (1.1.x), исходный движок team-up/team-lazy/team-down + генератор setup + hooks (1.0.0).
