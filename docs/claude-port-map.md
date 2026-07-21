# Карта портирования: Codex-версия -> Claude Code-версия

Этот репозиторий (Codex-native) — **источник смысла**: продуктовые фичи рождаются и обкатываются здесь. Claude Code-версия — отдельный проект с собственной структурой: upstream [toiiia/qtim-agent-team](https://github.com/toiiia/qtim-agent-team), рабочий клон — `../qtim-agent-team-claude` (форк `trushhh777/qtim-agent-team-1`, remote `upstream` -> toiiia). Правки транслируются **семантически** — переписыванием под конвенции целевого репозитория, не копированием текста.

## Процесс порта

1. Фича реализуется и обкатывается здесь (Codex-версия), деплой в `trushhh777/qtim-agent-team`.
2. В клоне `../qtim-agent-team-claude`: `git fetch upstream && git merge --ff-only upstream/main` (владелец toiiia активно мержит — main уходит вперёд), ветка `feat/<фича>` от `main`.
3. Переписать фичу под конвенции Claude-версии по таблице ниже, читая актуальные файлы upstream (владелец адаптирует влитое — не полагаться на нашу последнюю версию).
4. Прогнать их CI локально: `python3 .github/scripts/check_placeholders.py`, `check_links.py`, `node .github/scripts/check_workflows.mjs plugins/qtim/workflows/*.mjs`, JSON-манифесты, grep канона рантайма.
5. Соблюсти их версионирование: запись `## → <версия>` в `reference/migrations.md` (если меняется сгенерированное), строка «team-sync: …» в CHANGELOG, минорный бамп `plugin.json`.
6. Push ветки в `origin` (форк) -> PR в `toiiia/qtim-agent-team` (`gh pr create --repo toiiia/qtim-agent-team --head trushhh777:<ветка>`).

## Таблица соответствий

| Сущность | Codex (здесь) | Claude Code (toiiia) | Отличия |
|---|---|---|---|
| Упаковка | `.codex-plugin/plugin.json`, marketplace `.agents/plugins/` | `.claude-plugin/plugin.json`, marketplace `.claude-plugin/` | у Claude нет `interface`-блока и строгого ingestion-валидатора |
| Команды пользователя | skills `plugins/qtim/skills/<имя>/SKILL.md`, вызов `$qtim-<имя>` | slash-команды `plugins/qtim/commands/<имя>.md`, вызов `/qtim:<имя>` | frontmatter: у skills `name`+`description` (кавычки при `:` внутри), у commands `description`+`argument-hint` |
| Bundled disciplines | skills `qtim-debug-loop` / `qtim-prototype` / `qtim-brainstorm` / `qtim-grill`, вызов `$qtim-<имя>` | skills `debug-loop` / `prototype` / `brainstorm` / `grill`, вызов `qtim:<имя>` | это не пользовательские slash-команды и не optional stack skills; templates ролей ссылаются напрямую |
| Шаблоны ролей | `agents/*.toml`: `name`, `description`, optional atomic `model` + `model_reasoning_effort`, `developer_instructions ='''…'''`; оба model-поля отсутствуют = inherit session | `agents/*-agent.md`: frontmatter `name`, `description` c `<example>`-блоками, `model: inherit` или дешёвый alias, `color`, `memory`, `tools`; тело — markdown | в Codex нельзя писать `model = "inherit"`; у Claude есть persistent agent-memory, в Codex — общий `memory/`; GPT-5.6/Max/Ultra — Codex-специфика |
| Оркестрация | qtim workflow авторизуется skill/direct request; root `Ultra` может proactive delegation внутри scope; task-scoped agent threads, custom agents из `.codex/agents`, fan-out принадлежит main thread | рантайм Agent Teams: `Agent({name, subagent_type, prompt})`, `SendMessage`, `Task*`; `TeamCreate`/`team_name` упразднены — не употреблять | Codex descendants можно восстановить, только если их показывает runtime; скрытой persistent-команды нет; канон Claude описан в их `commands/team-up.md` («Модель оркестрации») |
| Сгенерированное состояние | `.codex/team-charter.md` (track-маркеры `qtim:track:*`), `.codex/agents/*.toml`, optional `.codex/hooks.json`, `memory/`, `AGENTS.md` | `.claude/team-charter.md`, `.claude/agents/*-agent.md`, `.claude/settings.local.json`, `memory/`, `CLAUDE.md` | у Claude нет track-маркеров — PM-дорожка просто секция «PM-конвейер»; есть Standalone-режим (Q6) с копированием движка |
| Hooks | plugin `hooks/hooks.json` владеет `SessionStart` / `SubagentStop`; project `.codex/hooks.json` — только optional `PostToolUse`/user hooks; nested `type: command`, event-specific JSON output | plugin-linked использует bundled hooks; Standalone копирует их в `.claude/settings.local.json` | Codex складывает plugin/project layers и требует `/hooks` trust; `PostToolUse` plain stdout игнорируется, `SubagentStop` требует JSON; текст hook-конфигов между рантаймами не копировать |
| Версионный штамп | `<!-- qtim-version: X.Y.Z -->` в charter, `# qtim-version:` в TOML | `generated-by: qtim vX.Y.Z · mode: <plugin-linked\|standalone>` в шапке charter | формат строки — контракт с их hook и team-sync, не менять |
| Миграции | `reference/upgrade-notes.md` + skill `$qtim-update` | `reference/migrations.md` + `/qtim:team-sync` | у Claude контракт maintainer'а описан в их CLAUDE.md § Версионирование |
| Роль-вопрос setup | Phase 2, первый вопрос | Q0 (нумерация Q0 — чтобы не сдвигать ссылки на Q1-Q8) | состав PM-трека одинаковый: product + architect + профильные dev, без reviewer |
| Ссылки между файлами | skills ссылаются на `../../reference/...` (внутри плагина легально); в agent TOML `../` запрещён (CI) | commands ссылаются относительно `[](../reference/...)`; в charter пути к протоколам — **абсолютные** (паттерн codex-consult) | и там и там: сгенерированные файлы самодостаточны |
| CI | `.github/scripts/`: check_placeholders, check_skills, check_links, check_codex_agents (+ model-слаг), check_hooks (schema + runtime output) | check_placeholders (+ examples/), check_links, check_workflows.mjs, grep канона | белый список плейсхолдеров `{{...}}` одинаковый (8 имён); hook validators runtime-specific |
| Golden-пример | нет | `examples/nuxt-supabase/` — при правке шаблонов/структуры charter обновить эталон | CI проверяет отсутствие плейсхолдеров в examples |

## Соответствие фич (состояние на 2026-07-21)

| Фича | Codex | Claude | Статус |
|---|---|---|---|
| Ролевой вход + PM-конвейер + product-роль | 2.1.0 | 1.5.0 | влит владельцем (PR #1 -> коммит 80a9475) |
| Версионирование + update | 2.2.0 | 1.3.0 (team-sync, их собственная реализация) | сошлись независимо; портировать нечего |
| Продуктовая память + product-onboard | 2.3.0 | 1.7.0 — [PR #3](https://github.com/toiiia/qtim-agent-team/pull/3) влит владельцем (8ff7606 + пост-фиксы 1a2d145) | адаптация владельца минимальна (оговорка migrations про dev-only standalone — Claude-специфика, обратный порт не нужен) |
| onboard/doctor/team-retro/epic-state | 2.4.0 (порт ИЗ Claude) | 1.4.0 (оригинал) | обратное направление: их фичи портированы к нам |
| Фикс model-слагов setup | 2.4.0 | — | Codex-специфика (слаги `gpt-X.Y`); Claude использует алиасы `opus`/`sonnet`, не подвержен |
| Аудит-фиксы: fail-closed гейты рецептов, канон оси A/B/C/D, screenshots-gate (front-selfcheck), выключенный review-гейт (их Q5=No), пометка PM-состава, канон `decisions.md`, CI-детектор скобок, README S/M/L/XL | 2.5.0 (порт ИЗ Claude) | 1.6.0 (оригинал, 92985d1) | обратное направление; Codex-специфичное не портировано — перечень в CHANGELOG 2.5.0 «Не портировано» |
| Режим UX-AUDIT у product | 2.5.0 | 1.5.0 (адаптация владельца при слиянии PR #1) | выровнено с отставанием в один релиз |
| Doctor: проверка продуктовой памяти при PM-дорожке | 2.6.0 (порт ИЗ Claude) | 1.7.1 (оригинал, 1b122b6 — финдинг ревью PR #3) | обратное направление; в Codex — пункт «PM-трек» doctor (он условный), у Claude — пункт «Память» |
| PM-конвейер: intake-интервью, фиксация отклонений от plan.md, порядок фаз по неопределённости | 2.6.0 (порт ИЗ Claude) | 1.8.0 (оригинал, 6c4608f) | обратное направление; бамп golden-примера не портирован (нет examples/); цитата канона intake — своя в каждой версии |
| GPT-5.6 Sol/Terra profiles, Max/Ultra-aware orchestration, task-scoped descendants и pair fallback | 2.7.0 | — | Codex-специфика; exact pins intelligence-heavy ролей superseded в 2.9.0 наследованием session, testing Terra/medium и atomic fallback сохранены |
| Codex hooks: разделение plugin/project layers, JSON output и CI schema checker | 2.8.0 | уже разделено Plugin-linked/Standalone | Исправление регрессии Codex-порта; обратный порт не нужен, форматы hook output различаются |
| Frontier-model адаптация + fast-path PM-конвейера + четыре bundled disciplines + факт/решение + ADR filter + vertical slices | 2.9.0 (порт ИЗ Claude) | 1.9.0 + 1.10.0 (один upstream-коммит [fc0f8e9](https://github.com/toiiia/qtim-agent-team/commit/fc0f8e9b7a1bb2d9c4ab27f2dd14cef72331833a)) | `model: inherit` адаптирован как отсутствие обоих Codex fields у intelligence-heavy ролей; testing остаётся Terra/medium; Codex second-opinion = отдельный read-only agent thread; Standalone/golden example не портированы; front composable уже был компактным |

## Правила

- Не полагаться на текст своего прошлого порта — владелец адаптирует влитое (пример: v1.5.0 добавил UX-AUDIT-секцию и resume-фиксы); перед новой веткой перечитывать затрагиваемые файлы upstream.
- Язык, тон и плотность — как в целевом файле; у Claude-версии коммиты conventional с русским описанием (их CLAUDE.md).
- Не тащить Codex-термины в Claude-файлы (skills, `$qtim-*`, `.codex/`) и наоборот.
- Этот файл обновлять при каждом порте (таблица фич) и при изменении конвенций любой из сторон.
