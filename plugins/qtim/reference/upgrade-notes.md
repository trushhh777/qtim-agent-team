# Upgrade notes qtim для Codex

> Этот файл читает `$qtim-update` (и `$qtim-setup` при обнаружении устаревшего состояния). Для каждой версии описано, что меняется в **сгенерированном состоянии проекта** (`.codex/*`, `memory/`, `AGENTS.md`) и как мигрировать с предыдущей версии, не затирая правки пользователя. Изменения самого плагина живут в CHANGELOG репозитория и сюда не дублируются.

Правило ведения: при каждом релизе, меняющем сгенерированное состояние, добавляй секцию сверху. Если релиз не меняет сгенерированное состояние, добавляй секцию с пометкой «миграция не требуется».

## 2.8.0

Что нового в сгенерированном состоянии:

- plugin-bundled `SessionStart` / `SubagentStop` больше не копируются в project `.codex/hooks.json`, потому что Codex складывает оба hook layers и запускает дубли;
- optional project `PostToolUse` использует canonical nested command schema из `reference/project-hooks.json` и возвращает JSON `hookSpecificOutput.additionalContext` вместо игнорируемого plain stdout;
- hook definitions получили отдельные POSIX/Windows commands; изменённые definitions нужно заново review/trust через `/hooks`.

Миграция с 2.7.0 и более ранних версий:

1. Если `.codex/hooks.json` отсутствует, не создавай его: исправленные `SessionStart` / `SubagentStop` придут из plugin layer.
2. Если файл есть, сначала сохрани его порядок и классифицируй каждый handler. qtim ownership определяй по совокупности fingerprints: guard `.codex/team-charter.md`; `[qtim` / `$qtim-*`; `qtim-version:`; тексты про реальные артефакты, затронутый слой или typecheck/build/test. Одного event name недостаточно.
3. Удали распознанные qtim `SessionStart` / `SubagentStop` из project layer как bundled-дубли. Если в matcher group есть пользовательские handlers, сохрани group и удали только qtim handler. Неоднозначные entries покажи пользователю и не меняй без решения.
4. Распознанный qtim `PostToolUse` в legacy top-level форме, с `type: reminder` / `message` или plain `echo` / `printf` замени handler из соседнего [project-hooks.json](project-hooks.json). Если он находится внутри matcher group с пользовательскими handlers, замени только qtim handler; group удаляй лишь когда после удаления qtim entries в нём ничего не осталось. Остальные handlers, PostToolUse groups и events сохрани без изменений.
5. Если после удаления qtim-дублей файл пуст и optional `PostToolUse` не выбран, предложи удалить `.codex/hooks.json`, покажи diff и дождись подтверждения. Не удаляй пустой файл молча.
6. Проверь canonical schema (`hooks -> Event[] -> hooks[] -> type: command`) и JSON output qtim `PostToolUse`; открой `/hooks` и заново review/trust изменённые definitions.
7. Обнови stamps charter и всех qtim TOML до `2.8.0`. Содержимое agent TOML, track blocks, `memory/`, `docs/features/` и секцию qtim в project `AGENTS.md` не меняй.

При прямой миграции с версии ниже 2.8.0 исторический шаг 2.2.0 про добавление project `SessionStart` пропусти: его заменяет plugin-bundled hook 2.8.0.

## 2.7.0

Что нового в сгенерированном состоянии:

- role profiles перешли на точные GPT-5.6 catalog slugs: architect/database/reviewer/product — `gpt-5.6-sol` + `high`, frontend — `gpt-5.6-sol` + `medium`, testing — `gpt-5.6-terra` + `medium`;
- `model` + `model_reasoning_effort` теперь считаются одной парой: если точный профиль недоступен, оба поля удаляются и роль наследует профиль главного task;
- working rules charter разделяют execution depth A/B/C/D и root reasoning: `Max`/`Ultra`/Fast выбирает пользователь, `Ultra` может делегировать только внутри разрешённого qtim scope, child agents не спавнят qtim descendants, main thread учитывает runtime thread cap и сначала проверяет доступные descendant threads;
- reviewer просит main thread поднять independent review вместо попытки спавнить descendant самостоятельно.

Миграция с 2.6.0:

1. Для каждого `.codex/agents/qtim-*.toml` сравни текущую пару с прежним qtim-default. Если она не менялась пользователем, обнови: `qtim-architect` / `qtim-database` / `qtim-reviewer` / `qtim-product` с `gpt-5.5` + `high` на `gpt-5.6-sol` + `high`; `qtim-frontend` с `gpt-5.5` + `medium` на `gpt-5.6-sol` + `medium`; `qtim-testing` с `gpt-5.4` + `medium` на `gpt-5.6-terra` + `medium`.
2. Если присутствует ровно одно из полей `model` / `model_reasoning_effort`, это broken half-pair (в том числе возможный legacy fallback 2.6.0), а не готовый override. Покажи diff и после подтверждения либо установи доступную template pair 2.7.0, либо удали оставшееся поле для полного наследования.
3. Если **оба** поля присутствуют и пара отличается от прежнего qtim-default, считай её пользовательским override: проверь по локальному catalog, покажи diff и не перезаписывай без подтверждения. Если выбранный GPT-5.6 profile недоступен в текущем Codex, удали **оба** поля вместо догаданной замены.
4. Обнови `qtim-reviewer` по template: independent review запрашивается у main thread; при выключенном гейте не возвращай вырезанный setup-ом gate-условный блок.
5. В общей working-rules секции `.codex/team-charter.md` добавь правила root reasoning/Ultra, task-scoped descendants, main-owned fan-out и batching по runtime cap. Ручные правки и оба track-блока не перезаписывай.
6. Обнови stamps charter и всех qtim TOML до `2.7.0`. `memory/`, `docs/features/` и секцию qtim в проектном `AGENTS.md` не меняй. Так как agent TOML изменились, перед qtim workflow обязательно открой новую задачу Codex.

## 2.6.0

Миграция не требуется — правки только движка (skills `qtim-feature` / `qtim-team-up` / `qtim-team-lazy` / `qtim-team-retro` / `qtim-doctor` и `reference/feature-pipeline.md`): intake-интервью, фиксация отклонений от `plan.md` в «Истории изменений», порядок фаз плана по неопределённости, проверка продуктовой памяти в doctor. Проекты получают их автоматически при следующем вызове skills; charter, шаблоны ролей и `memory/` не меняются. PM track block новых charter впитает обновлённый handoff contract сам — setup переносит суть `feature-pipeline.md`; в существующих charter дописывать ничего не нужно (правила доставляются движком в рантайме).

## 2.5.0

Что нового в сгенерированном состоянии:

- шаблоны ролей: у reviewer маршрутизация блокеров явно ограничена ролями из charter (database/frontend/testing/devops при наличии), screenshots-gate принимает только tester-скриншоты по конвенции `<epic>-<phase>-<viewport>-<screen>`; у frontend self-check-скриншоты получили префикс `front-selfcheck-` (гейт reviewer'а они не закрывают); у testing — конвенция имён скриншотов с суффиксом `-FAIL` для падений; у product — режим UX-AUDIT (пост-релизный аудит UX/discoverability);
- charter: при PM-only составе PM track block содержит пометку «перед реализацией дополнить состав dev-дорожкой повторным `$qtim-setup`»; при выключенном independent review — секция-заглушка «выключен», а independent-review-требования в сгенерированные агенты не переносятся.

Миграция с 2.4.0:

1. Обнови `.codex/agents/qtim-reviewer.toml`, `qtim-frontend.toml`, `qtim-testing.toml`, `qtim-product.toml` по текущим templates (diff-подтверждение при ручных правках пользователя).
2. PM-only команды (в charter нет dev-маркеров): добавь в PM track block пометку про доукомплектование dev-дорожкой перед реализацией handoff-плана.
3. Команды, собранные с выключенным independent review: добавь в charter строку-заглушку «independent review выключен; включить — повторный `$qtim-setup`» и вырежи требования гейта из сгенерированных TOML (reviewer/architect/database), если они там остались.
4. Dev-команды с включённым гейтом и без PM track — только шаг 1.

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
4. Только при target-версии ниже 2.8.0 предложи обновить project SessionStart на версионированный вариант. При target 2.8.0+ этот шаг superseded: project-дубль удаляется, версионированный SessionStart поставляет плагин.

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
- Пользовательские hook events/groups/handlers не удалять и не переупорядочивать; менять только распознанные qtim entries после показанного diff.
- После миграции обнови оба stamp (charter и TOML) на текущую версию плагина.
- При любой миграции проверяй атомарную пару `model` + `model_reasoning_effort` в сгенерированных `.codex/agents/*.toml`: это текущий template, явный пользовательский override, подтверждённый локальным catalog, либо оба поля отсутствуют для наследования main profile. Боевой инцидент: setup сгенерировал несуществующий `model = "gpt-5"` (слаг без минорной версии), и все субагенты не стартовали. Фикс: доступная pair из template/подтверждённого override или удалить **оба** поля; одинокий pinned model/reasoning не оставлять.
