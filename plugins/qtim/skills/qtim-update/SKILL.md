---
name: qtim-update
description: "Use when the user wants to check or upgrade qtim in Codex: reports plugin vs generated-team versions, prints plugin upgrade commands, migrates charter/agent TOMLs, and safely canonicalizes qtim-owned project hooks without clobbering user handlers."
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

После переустановки плагина нужна новая задача Codex — только она подхватит обновлённые skills; предупреди об этом.

## Step 3: Migrate Project State

Только если plugin version новее project version. Если stamp проекта новее плагина — не даунгрейдь: скажи, что устарел сам плагин, дай команды из Step 2 и остановись.

1. Прочитай `../../reference/upgrade-notes.md` и собери шаги всех версий между project version и plugin version. Применяй **oldest -> newest**; секции в notes лежат newest-first, поэтому нужный диапазон читается снизу вверх. Прямой upgrade не начинай с целевой версии.
2. Сравни сгенерированные `.codex/agents/qtim-*.toml` с текущими templates `../../agents/*.toml` (с поправкой на подставленные плейсхолдеры стека). Прежний template из Git history не считай доступным: engine-managed region распознавай только по fingerprints и соседним anchors конкретной секции upgrade notes. Если region не распознан однозначно, не заменяй весь файл: покажи diff и оставь шаг pending. Текущие templates имеют явные atomic model pairs; best-effort проверь их по локальному catalog. Ручные правки и user overrides не перезаписывай молча.
3. Если существует `.codex/hooks.json`, выполни hook-миграции из upgrade notes отдельно от agent templates. Распознавай qtim-owned handlers по совокупности fingerprints (guard `.codex/team-charter.md`, `[qtim` / `$qtim-*`, `qtim-version:`, тексты про реальные артефакты или проверку затронутого слоя), а не только по event/matcher. Сохраняй порядок и содержимое неизвестных пользовательских events/groups/handlers; если ownership неоднозначен, покажи entry и спроси.
4. Managed qtim contract в `AGENTS.md` изменяй только между `qtim:contract:start/end`; пользовательский текст вне markers сохраняй. `.codex/screenshots-gate.json` не создавай без нового explicit opt-in и валидируй как safe repo-relative policy.
4. Покажи план миграции: какие файлы, handlers и engine-managed блоки меняются (в charter — PM-механика только между её маркерами; roles table/independent-review policy — точечными строками без удаления внешних skills; ручные правки и второй track сохраняются), что остаётся нетронутым. Дождись подтверждения.
5. Применяй секции oldest -> newest. `memory/` и `docs/features/` не переписываются. Для каждой версии собери checklist applicable шагов со статусами `applied` / `compatible override confirmed` / `pending`.
6. Когда у очередной версии не осталось `pending`, атомарно подними charter и все TOML stamps до этой версии, затем переходи к следующей. Осознанно сохранённый catalog-supported override считается compatible; отложенный engine block — pending. При первом pending останови дальнейшие версии: stamps остаются на последней полностью завершённой версии, а следующий `$qtim-update` повторит только незавершённый диапазон.

## Step 4: Verify And Report

- JSON/TOML parse для изменённых файлов (`python3 -m json.tool`, `tomllib` если доступен);
- `.codex/hooks.json`, если существует: canonical root `hooks`, matcher groups с вложенным `hooks`, qtim handlers только `type: command` с `commandWindows`; нет qtim-owned project-дублей `SessionStart` / `SubagentStop`; qtim `PostToolUse` возвращает JSON `hookSpecificOutput.additionalContext`; пользовательские handlers и их порядок сохранены;
- model policy каждого `.codex/agents/*.toml`: exact current template pair либо user-approved catalog-supported override; half-pair и `model = "inherit"` невалидны; недоступный slug -> migration pending, не удаляй pair и не угадывай замену;
- `ultra` и `service_tier = "fast"` не появились в role TOML; charter фиксирует main team-lead `gpt-5.6-sol` + `ultra`, built-in explorer Luna+medium и ADR adversary Sol+xhigh/max;
- track-маркеры парные; все stamps единообразно указывают на последнюю полностью завершённую версию, а не на partial target;
- в изменённых файлах нет plugin-internal путей (`../../...`);
- финальный ответ: версии до/после, изменённые файлы, compatible overrides и pending; при pending явно скажи, что stamps остались на последней полностью завершённой версии и целевая migration не завершена. Если менялся любой `.codex/agents/*.toml`, новая задача Codex **обязательна** перед qtim workflow. Если менялись hooks, открой `/hooks`, заново review/trust изменённые definitions; если текущий runtime не подхватил их после review, открой новую задачу. Если agent TOML и hooks не менялись, дополнительный restart не нужен.

## Rules

- Не выполняй `codex plugin ...` без явной просьбы пользователя.
- Не трогай `memory/`, `docs/features/` и правки пользователя вне qtim-маркеров.
- Не удаляй и не переупорядочивай неизвестные пользовательские hook entries; распознанный qtim handler удаляй отдельно от соседних handlers и только после показанного diff.
- Не выдумывай шаги миграции: только `upgrade-notes.md` и фактический diff с templates.
- Считай `model` + `model_reasoning_effort` одной профильной парой: current qtim defaults явные; недоступная pair оставляет migration pending, пользовательские overrides требуют diff-подтверждения.
- Конфликт или сомнение — спроси, не перезаписывай.
