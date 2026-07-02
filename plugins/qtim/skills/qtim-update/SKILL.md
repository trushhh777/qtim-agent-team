---
name: qtim-update
description: "Use when the user wants to check the qtim version or upgrade qtim in Codex: reports installed plugin version vs generated team version, prints the plugin upgrade commands, and migrates .codex/team-charter.md, .codex/agents/*.toml and hooks to the current plugin version without clobbering user edits."
---

# qtim Update

Ты обновляешь qtim на двух уровнях: сам плагин (Codex marketplace snapshot) и сгенерированное состояние команды в проекте (`.codex/*`, `AGENTS.md`). Плагин обновляется командами Codex CLI, состояние проекта мигрируешь ты.

## Step 1: Determine Versions

1. Версия установленного плагина: прочитай `../../.codex-plugin/plugin.json`, поле `version`.
2. Версия команды в проекте: stamp `<!-- qtim-version: X.Y.Z -->` в первой строке `.codex/team-charter.md`.
   - Charter отсутствует — команды в проекте нет: предложи `$qtim-setup` и остановись.
   - Charter есть, stamp отсутствует — состояние legacy (сгенерировано qtim < 2.2.0): определи фактический уровень по признакам из `../../reference/upgrade-notes.md` (track-маркеры есть -> 2.1.0, нет -> 2.0.0 или старше).

## Step 2: Report

Покажи пользователю компактную сводку:

- installed plugin version;
- project team version (или legacy + определённый уровень);
- вердикт: `up to date` / `project state outdated` / `plugin outdated`.

Команды обновления самого плагина (печатай всегда, выполняй сам только по явной просьбе пользователя):

```bash
codex plugin marketplace upgrade qtim-agent-team   # обновить Git-marketplace snapshot
codex plugin add qtim@qtim-agent-team              # переустановить плагин из свежего snapshot
```

После переустановки плагина нужна новая Codex thread/session — только она подхватит обновлённые skills; предупреди об этом.

## Step 3: Migrate Project State

Только если plugin version новее project version. Если stamp проекта новее плагина — не даунгрейдь: скажи, что устарел сам плагин, дай команды из Step 2 и остановись.

1. Прочитай `../../reference/upgrade-notes.md` и собери шаги всех версий между project version и plugin version (сверху вниз по возрастанию версий).
2. Сравни сгенерированные `.codex/agents/qtim-*.toml` с текущими templates `../../agents/*.toml` (с поправкой на подставленные плейсхолдеры стека). Файлы, которые пользователь менял руками, не перезаписывай молча: покажи diff и спроси.
3. Покажи план миграции: какие файлы и какие блоки меняются (в charter — только между маркерами и общие структурные блоки, ручные правки вне них не трогаются), что остаётся нетронутым. Дождись подтверждения.
4. Применяй шаги. `memory/` и `docs/features/` не переписываются.
5. Обнови stamps: charter и все `# qtim-version:` в TOML — на версию плагина.

## Step 4: Verify And Report

- JSON/TOML parse для изменённых файлов (`python3 -m json.tool`, `tomllib` если доступен);
- `model` каждого `.codex/agents/*.toml` — валидный слаг (совпадает с template или доступен в окружении); невалидный (например `gpt-5`) — почини или удали поле;
- track-маркеры парные, stamps обновлены;
- в изменённых файлах нет plugin-internal путей (`../../...`);
- финальный ответ: версии до/после, изменённые файлы, что пропущено по решению пользователя, нужна ли новая thread.

## Rules

- Не выполняй `codex plugin ...` без явной просьбы пользователя.
- Не трогай `memory/`, `docs/features/` и правки пользователя вне qtim-маркеров.
- Не выдумывай шаги миграции: только `upgrade-notes.md` и фактический diff с templates.
- Конфликт или сомнение — спроси, не перезаписывай.
