---
name: qtim-doctor
description: "Use when a qtim Codex team misbehaves or after a plugin/Codex update: read-only diagnostics of the generated state — charter version stamp and track markers, agent TOMLs (parse, placeholders, plugin-internal paths), hooks.json, memory, docs/features — with a pass/warn/fail table and concrete fixes."
---

# qtim Doctor — самодиагностика

Read-only диагностика: ничего не чинит без подтверждения. Запускай при «что-то не работает», после обновления плагина или Codex, или при онбординге коллеги в проект с qtim-командой.

## Чеклист (прогони все пункты, собери в таблицу pass / warn / fail)

1. **Плагин.** `../../.codex-plugin/plugin.json` читается? Зафиксируй `version`. Не читается — плагин установлен нештатно: переустановка командами из `$qtim-update`.
2. **Charter.** `.codex/team-charter.md` существует (нет -> `$qtim-setup`); первой строкой stamp `<!-- qtim-version: X.Y.Z -->` (нет -> legacy-состояние, предложи `$qtim-update`); версия stamp совпадает с версией плагина (расходится -> `$qtim-update`); track-маркеры `qtim:track:*` парные; обязательные секции на месте (roles table, working rules, memory layout; для PM-трека — блок pipeline между PM-маркерами).
3. **Агенты.** Для каждой роли из charter (кроме встроенных `explorer`/`worker` — им свой файл не требуется): `.codex/agents/<name>.toml` существует; TOML парсится (`tomllib` при наличии Python 3.11+); `name` в TOML совпадает с именем агента из charter; первой строкой `# qtim-version: ...`; в теле нет неподставленных плейсхолдеров `{{...}}` (остались -> генерация не подставила стек: `$qtim-update` или поправить руками); нет plugin-internal путей (`../../...`) — сгенерированные файлы должны быть самодостаточны; если independent review в charter помечен заглушкой «выключен» — в TOML ролей не осталось требований independent review gate (остались -> warn: вырезать или включить гейт повторным `$qtim-setup`).
4. **Hooks.** `.codex/hooks.json` — валидный JSON (`python3 -m json.tool`); напомни, что Codex hooks требуют trust review через `/hooks`; проверь, что проектные hooks не дублируют hooks плагина (двойной SessionStart-анонс -> убрать проектный дубль).
5. **Память.** `memory/MEMORY.md` существует; файлы, на которые ссылается индекс, существуют; `memory/epic-state.md` не содержит заведомо устаревшего «в полёте» (эпик давно завершён -> warn, предложить убрать).
6. **PM-трек** (если включён в charter). Артефакты в `docs/features/*/` имеют шапку со Status; строки-указатели в `memory/decisions.md` ведут на существующие каталоги фич.
7. **Skills.** Skills, предписанные ролям в charter, доступны в текущем окружении (проверь по списку доступных skills); недоступные -> warn: mandatory-invoke несуществующего skill ломает старт роли — убрать из charter или установить.

## Вывод

Таблица: пункт · статус · что именно не так · конкретный фикс (skill, команда или правка файла).

После таблицы предложи применить **безопасные** фиксы (создание недостающего `MEMORY.md`, устаревший `epic-state.md`, двойной анонс hooks) — по подтверждению пользователя, по одному классу за раз. Миграцию версий не делай сам — отправляй в `$qtim-update`. Ничего не удаляй без подтверждения; сомнительное — только показывай.
