# Upgrade notes qtim для Codex

> Этот файл читает `$qtim-update` (и `$qtim-setup` при обнаружении устаревшего состояния). Для каждой версии описано, что меняется в **сгенерированном состоянии проекта** (`.codex/*`, `memory/`, `AGENTS.md`) и как мигрировать с предыдущей версии, не затирая правки пользователя. Изменения самого плагина живут в CHANGELOG репозитория и сюда не дублируются.

Правило ведения: при каждом релизе, меняющем сгенерированное состояние, добавляй секцию сверху. Если релиз не меняет сгенерированное состояние, добавляй секцию с пометкой «миграция не требуется».

## 2.4.0

Что нового в сгенерированном состоянии:

- working rules charter описывают session handoff: `memory/epic-state.md` (пишет `$qtim-team-down`, читает `$qtim-team-up`), уроки retro в `memory/retro-log.md` и `memory/lessons.md`;
- секция `Команда qtim` в `AGENTS.md` проекта упоминает `$qtim-team-retro`, `$qtim-onboard`, `$qtim-doctor`;
- `memory/MEMORY.md` описывает назначение `epic-state.md` / `retro-log.md` / `lessons.md` (сами файлы создаются skills по мере надобности, не setup).

Миграция с 2.3.0:

1. Добавь в working rules charter (общая секция, вне track-маркеров) описание session handoff — аккуратно, не перезаписывая ручные правки пользователя.
2. Добавь `$qtim-team-retro`, `$qtim-onboard`, `$qtim-doctor` в секцию `Команда qtim` в `AGENTS.md`.
3. Допиши в `memory/MEMORY.md` строки про `epic-state.md` / `retro-log.md` / `lessons.md`; существующие записи памяти не трогай.

Новые skills и рецепты оркестрации живут в плагине и миграции файлов проекта не требуют.

## 2.3.0

Что нового в сгенерированном состоянии:

- продуктовая память `memory/product-map.md` / `product-actors.md` / `product-glossary.md` / `product-metrics.md` — наполняется новым skill `$qtim-product-onboard` (setup её не создаёт);
- PM track block charter упоминает эти файлы как read-on-start роли `product` («если созданы»);
- шаблон `product.toml`: продуктовая память в Read first + правило «метрики PRD привязывать к событиям из product-metrics».

Миграция с 2.2.0 (только для команд с PM track):

1. Добавь в PM track block charter упоминание продуктовой памяти как read-on-start роли `product`.
2. Обнови `.codex/agents/qtim-product.toml` по текущему template (diff-подтверждение при ручных правках).
3. Порекомендуй пользователю прогнать `$qtim-product-onboard` на существующей кодовой базе.

Dev-only команды миграции не требуют.

## 2.2.0

Что нового в сгенерированном состоянии:

- version stamp: charter начинается с `<!-- qtim-version: X.Y.Z -->`, каждый сгенерированный `.codex/agents/*.toml` — с комментария `# qtim-version: X.Y.Z`;
- секция `Команда qtim` в `AGENTS.md` проекта упоминает `$qtim-update`;
- рекомендованный SessionStart hook показывает версию команды из stamp.

Миграция с 2.1.0:

1. Добавь `<!-- qtim-version: 2.2.0 -->` первой строкой `.codex/team-charter.md`.
2. Добавь `# qtim-version: 2.2.0` первой строкой каждого `.codex/agents/qtim-*.toml`.
3. Добавь `$qtim-update` в секцию `Команда qtim` в `AGENTS.md`.
4. Предложи обновить SessionStart hook на версионированный вариант (см. hooks плагина); пользовательские hooks не затирай.

## 2.1.0

Что нового в сгенерированном состоянии:

- charter стал track-aware: dev и PM треки между маркерами `<!-- qtim:track:dev:start/end -->` и `<!-- qtim:track:pm:start/end -->`;
- PM track: роль `qtim-product` (`.codex/agents/product -> qtim-product.toml`), механика feature pipeline в charter, конвенция `docs/features/<slug>/`.

Миграция с 2.0.0:

1. Оберни существующее dev-содержимое charter (roles table dev-ролей, intake/autonomy) в маркеры `qtim:track:dev`.
2. Спроси пользователя, нужен ли PM track; если да — добавь блок `qtim:track:pm` с механикой pipeline (стадии, статусы, правила grounded-оценки, handoff) и сгенерируй `qtim-product` из template.
3. Существующие правки пользователя в charter вне маркеров не трогай.

## 2.0.0

Baseline Codex-native упаковки: `.codex/team-charter.md`, `.codex/agents/*.toml`, `.codex/hooks.json`, `memory/`, `AGENTS.md`.

Миграция с 1.x (legacy `.claude/*`, `CLAUDE.md`): автоматической миграции нет — прогнать `$qtim-setup` заново; legacy-файлы не удалять без явной просьбы пользователя.

## Общие правила миграции

- Не даунгрейдить: если stamp проекта новее версии установленного плагина, обнови сам плагин, а не проект.
- `memory/` и `docs/features/` при миграции не переписываются.
- Изменённые пользователем файлы не перезаписывать молча: показать diff и спросить.
- После миграции обнови оба stamp (charter и TOML) на текущую версию плагина.
- При любой миграции проверяй `model` в сгенерированных `.codex/agents/*.toml`: слаг обязан совпадать с template или быть заведомо доступным в окружении. Боевой инцидент: setup сгенерировал несуществующий `model = "gpt-5"` (слаг без минорной версии), и все субагенты не стартовали. Фикс: валидный слаг из template или удалить поле `model` (агент унаследует модель сессии).
