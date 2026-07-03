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
| Шаблоны ролей | `agents/*.toml`: `name`, `description`, `model` (слаг `gpt-X.Y`), `model_reasoning_effort`, `developer_instructions ='''…'''` | `agents/*-agent.md`: frontmatter `name`, `description` c `<example>`-блоками, `model` (алиас `opus`/`sonnet`), `color`, `memory`, `tools`; тело — markdown | в Claude у роли есть persistent agent-memory (`.claude/agent-memory/<role>-agent/`) — личные наблюдения роли туда; в Codex — только общий `memory/` |
| Оркестрация | Codex subagent threads: explicit spawn, session-local, custom agents из `.codex/agents` | рантайм Agent Teams: `Agent({name, subagent_type, prompt})`, `SendMessage`, `Task*`; `TeamCreate`/`team_name` упразднены — не употреблять | канон описан в их `commands/team-up.md` («Модель оркестрации») |
| Сгенерированное состояние | `.codex/team-charter.md` (track-маркеры `qtim:track:*`), `.codex/agents/*.toml`, `.codex/hooks.json`, `memory/`, `AGENTS.md` | `.claude/team-charter.md`, `.claude/agents/*-agent.md`, `.claude/settings.local.json`, `memory/`, `CLAUDE.md` | у Claude нет track-маркеров — PM-дорожка просто секция «PM-конвейер»; есть Standalone-режим (Q6) с копированием движка |
| Версионный штамп | `<!-- qtim-version: X.Y.Z -->` в charter, `# qtim-version:` в TOML | `generated-by: qtim vX.Y.Z · mode: <plugin-linked\|standalone>` в шапке charter | формат строки — контракт с их hook и team-sync, не менять |
| Миграции | `reference/upgrade-notes.md` + skill `$qtim-update` | `reference/migrations.md` + `/qtim:team-sync` | у Claude контракт maintainer'а описан в их CLAUDE.md § Версионирование |
| Роль-вопрос setup | Phase 2, первый вопрос | Q0 (нумерация Q0 — чтобы не сдвигать ссылки на Q1-Q8) | состав PM-трека одинаковый: product + architect + профильные dev, без reviewer |
| Ссылки между файлами | skills ссылаются на `../../reference/...` (внутри плагина легально); в agent TOML `../` запрещён (CI) | commands ссылаются относительно `[](../reference/...)`; в charter пути к протоколам — **абсолютные** (паттерн codex-consult) | и там и там: сгенерированные файлы самодостаточны |
| CI | `.github/scripts/`: check_placeholders, check_skills, check_links, check_codex_agents (+ model-слаг) | check_placeholders (+ examples/), check_links, check_workflows.mjs, grep канона | белый список плейсхолдеров `{{...}}` одинаковый (8 имён) |
| Golden-пример | нет | `examples/nuxt-supabase/` — при правке шаблонов/структуры charter обновить эталон | CI проверяет отсутствие плейсхолдеров в examples |

## Соответствие фич (состояние на 2026-07-03)

| Фича | Codex | Claude | Статус |
|---|---|---|---|
| Ролевой вход + PM-конвейер + product-роль | 2.1.0 | 1.5.0 | влит владельцем (PR #1 -> коммит 80a9475) |
| Версионирование + update | 2.2.0 | 1.3.0 (team-sync, их собственная реализация) | сошлись независимо; портировать нечего |
| Продуктовая память + product-onboard | 2.3.0 | ветка `feat/product-onboard` (9ac01ec, помечена v1.6.0) | PR #2 закрыт до актуализации; **номер 1.6.0 теперь занят релизом владельца** — при актуализации ветки перевыпустить как 1.7.0 |
| onboard/doctor/team-retro/epic-state | 2.4.0 (порт ИЗ Claude) | 1.4.0 (оригинал) | обратное направление: их фичи портированы к нам |
| Фикс model-слагов setup | 2.4.0 | — | Codex-специфика (слаги `gpt-X.Y`); Claude использует алиасы `opus`/`sonnet`, не подвержен |
| Аудит-фиксы: fail-closed гейты рецептов, канон оси A/B/C/D, screenshots-gate (front-selfcheck), выключенный review-гейт (их Q5=No), пометка PM-состава, канон `decisions.md`, CI-детектор скобок, README S/M/L/XL | 2.5.0 (порт ИЗ Claude) | 1.6.0 (оригинал, 92985d1) | обратное направление; Codex-специфичное не портировано — перечень в CHANGELOG 2.5.0 «Не портировано» |
| Режим UX-AUDIT у product | 2.5.0 | 1.5.0 (адаптация владельца при слиянии PR #1) | выровнено с отставанием в один релиз |

## Правила

- Не полагаться на текст своего прошлого порта — владелец адаптирует влитое (пример: v1.5.0 добавил UX-AUDIT-секцию и resume-фиксы); перед новой веткой перечитывать затрагиваемые файлы upstream.
- Язык, тон и плотность — как в целевом файле; у Claude-версии коммиты conventional с русским описанием (их CLAUDE.md).
- Не тащить Codex-термины в Claude-файлы (skills, `$qtim-*`, `.codex/`) и наоборот.
- Этот файл обновлять при каждом порте (таблица фич) и при изменении конвенций любой из сторон.
