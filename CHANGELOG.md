# Changelog

Версии соответствуют `version` в `plugins/qtim/.codex-plugin/plugin.json` (semver).

## 2.6.0 — 2026-07-06

Порт улучшений Claude Code-версии 1.7.1 и 1.8.0 ([toiiia/qtim-agent-team](https://github.com/toiiia/qtim-agent-team), коммиты 1b122b6 и 6c4608f) под Codex-конвенции. Сгенерированное состояние проектов не меняется — `reference/upgrade-notes.md`, запись «2.6.0» (миграция не требуется).

### Изменено

Три точечных усиления PM-конвейера по мотивам «Слепых зон в промптинге» (Thariq Shihipar, перевод на Хабре): стадии конвейера — это систематическое сокращение неизвестных, и в трёх местах оно протекало.

- **Intake как интервью** (`$qtim-feature`, Stage 1): вместо «структурированные вопросы одним компактным блоком» — итеративное интервью порциями по 1-3 вопроса, где каждая следующая порция строится на полученных ответах, а первыми идут вопросы, сильнее всего меняющие постановку; остановка — когда новые ответы перестают менять понимание. Выравнивает стадию с каноном intake-протокола («анализ и проектирование — пользователь в контуре»).
- **Фиксация отклонений от плана** (handoff contract): реализующая сторона записывает отклонения от `plan.md` с обоснованием и всплывшие edge cases строкой в append-only «Историю изменений» `plan.md` — раньше они испарялись в чате реализующей сессии. Даёт готовый материал ретроспективе и resume многофазных фич. Правило доставлено по всей цепочке: строка в handoff-шаблоне `$qtim-feature`, дубль на реализующей стороне (`$qtim-team-up` preconditions + reporting, `$qtim-team-lazy` шаг 2), новый источник фактов в `$qtim-team-retro`, контракт и анти-паттерн «молчаливое отклонение» в `reference/feature-pipeline.md`.
- **Порядок фаз плана по неопределённости** (`$qtim-feature`, Stage 5 + `feature-pipeline.md`): решения, которые вероятнее всего изменятся (модель данных, контракты API, UX-развилки), — в ранние фазы, механическая доводка — в хвост; так самое дорогое для переделки проверяется раньше всего.

### Добавлено

- **`$qtim-doctor`, пункт «PM-трек»** — проверка продуктовой памяти: созданные `memory/product-*.md`, не вписанные в read-on-start роли `product` в charter, -> warn (роль слепа к готовой памяти); отсутствие файлов -> info с рекомендацией `$qtim-product-onboard` (канон «если созданы» — не ошибка). Порт их 1.7.1 (финдинг ревью PR #3).

### Не портировано (Claude-специфика)

- Бамп штампа golden-примера — в Codex-версии нет каталога `examples/`.
- Оговорка migrations про dev-only standalone (адаптация владельца при слиянии PR #3) — в Codex-версии нет standalone-режима.

## 2.5.0 — 2026-07-03

Порт аудит-фиксов Claude Code-версии 1.6.0 ([toiiia/qtim-agent-team](https://github.com/toiiia/qtim-agent-team), коммит 92985d1) под Codex-конвенции + выравнивание с 1.5.0-адаптацией владельца (режим UX-AUDIT). Миграция сгенерированного состояния — `reference/upgrade-notes.md`, запись «2.5.0».

### Исправлено

- **Рецепты оркестрации стали fail-closed** (`reference/orchestration-patterns.md`, аналог их правок `ensemble-review.mjs`/`flaky-hunt.mjs` — у нас рецепты текстовые, исполняет main thread): в Ensemble Review сбой скептика или целой линзы больше не читается как «дефекта нет» — неопровергнутые findings идут в отчёт блоком «требуют ручной проверки», findings сверх лимита верификации не выбрасываются, а правило вердикта main thread применяет детерминированно сам (NOT APPROVED при любом подтверждённом **или неверифицированном** P0/P1 и при упавшей линзе — синтез может только ужесточить); в Flaky Hunt сбой прогона считается отдельно от зелёных, серия сбоев даёт честное «ни один прогон не состоялся» вместо ложного «стабильно».
- **Канон оси A/B/C/D**: Execution Depth явно меряется глубиной координации (петли implement -> test -> review), выбор режима подсчётом ролей — anti-pattern; в Classify And Act зафиксировано, что классификатору делегируется только слой/severity/владелец, а выбор execution depth — работа main thread (матрица субагенту недоступна).
- **Screenshots-gate различает tester и front**: self-check-скриншоты frontend получили префикс `front-selfcheck-`, tester именует sweep-скриншоты `<epic>-<phase>-<viewport>-<screen>` (падения — `-FAIL`), reviewer закрывает гейт только tester-скриншотами; маршрутизация блокеров reviewer'а явно ограничена ролями, реально существующими в charter (database/frontend/testing/devops при наличии).
- **Выключенный independent review согласован по конвейеру** (аналог их Q5=No): setup при disabled пишет в charter секцию-заглушку «выключен» и вырезает independent-review-требования из генерируемых агентов (reviewer/architect/database) как gate-условные блоки; `$qtim-team-up` не требует гейт при заглушке; `$qtim-doctor` ловит рассинхрон (заглушка в charter + требования гейта в TOML); Phase 5 setup проверяет согласованность.
- **PM-состав честен про реализацию**: setup и PM track block charter помечают, что PM-состав (без `qtim-reviewer`) рассчитан на конвейер документов — перед запуском handoff-плана в разработку состав дополняется dev-дорожкой повторным `$qtim-setup`; предупреждение продублировано в handoff `$qtim-feature` (Stage 6).
- **Реестр решений и фич канонизирован до конца**: `$qtim-onboard` (синтез) и `reference/intake-protocol.md` (шаг 8) ссылаются на `memory/decisions.md` по имени, как остальные потребители.
- **CI**: `check_placeholders.py` ловит несбалансированные скобки плейсхолдеров (`{{FOO}` / `{FOO}}`) в `*.md` и `*.toml`.
- **README**: шкала оценок PM-конвейера — S/M/L/XL (была занижена до S/M/L).

### Добавлено

- **Режим UX-AUDIT у роли `product`** (выравнивание с их 1.5.0: владелец сохранил UX-аудит из Extended-каркаса при слиянии PR #1): пост-релизный аудит UX и discoverability — findings P0-P3 в финальном отчёте, задачи исполнителям раздаёт team-lead (в Codex субагент не создаёт задачи сам).
- Запись «2.5.0» в upgrade-notes (миграция шаблонов ролей; для PM-only и disabled-review команд — правки charter).

### Не портировано (Codex-специфика)

- Правки Workflow-скриптов как код и CI-запреты `Date.now()`/`Math.random()` — в Codex нет Workflow-движка, семантика перенесена в текстовые рецепты (см. «Исправлено»).
- Standalone-ветки doctor/team-sync, локализация командных имён, Q7-дубли hooks — в Codex-версии нет standalone-режима.
- Проверка резолвинга абсолютных путей протоколов при переносе проекта — Codex-charter самодостаточен (протоколы инлайнятся, путей в charter нет).
- Якорение hooks на каталог проекта (`$CLAUDE_PROJECT_DIR`) — у Codex-рантайма нет подтверждённого аналога переменной; hooks остаются advisory echo и при запуске не из корня просто молчат.
- `sh -n` hook-скрипта и канон-grep по `examples/` — hooks инлайновые, каталога examples нет.
- `color: cyan` у tester — в Codex agent TOML нет поля `color`.

## 2.4.0 — 2026-07-02

Порт dev-улучшений Claude Code-версии плагина 1.3.0–1.4.0 ([toiiia/qtim-agent-team](https://github.com/toiiia/qtim-agent-team)) под Codex-конвенции. Аналоги `/qtim:team-sync` и `reference/migrations.md` не портировались — их роль уже закрывают `$qtim-update` и `reference/upgrade-notes.md` (2.2.0).

### Добавлено

- **Skill `$qtim-team-retro`** — ретроспектива эпика (порт `/qtim:team-retro`): анализ петель/блокеров/повторяющихся классов проблем по фактам сессии и дистилляция уроков «триггер -> действие» в `memory/retro-log.md` и в секции ролей `memory/lessons.md`. Вместо Claude agent-memory (в Codex нет per-role памяти) уроки ролей живут в `memory/lessons.md`, а prompt template `$qtim-team-up` включает секцию роли в read-first — уроки доживают до следующей сессии, хотя agent threads — нет.
- **Epic-state / handoff между сессиями** (порт из 1.4.0): `$qtim-team-down` при незавершённом эпике пишет `memory/epic-state.md` (фаза, сделано, «в полёте», следующий шаг) и удаляет его после завершённого; `$qtim-team-up` в новой сессии читает его и предлагает продолжить. Team-down перед сворачиванием напоминает про `$qtim-team-retro`.
- **Skill `$qtim-onboard`** — глубокий онбординг dev-памяти (порт `/qtim:onboard`): план -> подтверждение объёма -> fan-out read-only исследователей по подсистемам -> синтез карты/инвариантов/конвенций в `memory/` с прецедентами `file:line`. Дополняет `$qtim-product-onboard`: тот смотрит глазами пользователя, этот — инженера.
- **Skill `$qtim-doctor`** — read-only диагностика (порт `/qtim:doctor`, чеклист переписан под Codex): манифест плагина, stamp и track-маркеры charter, целостность `.codex/agents/*.toml` (TOML parse, плейсхолдеры, plugin-internal пути), hooks.json и trust, память и устаревший epic-state, артефакты PM-трека, доступность skills из charter. Вывод — таблица pass/warn/fail с конкретными фиксами; безопасные фиксы по подтверждению.
- **Рецепты оркестрации** в `reference/orchestration-patterns.md` (адаптация Workflow-скриптов 1.4.0 — в Codex нет Workflow-движка, рецепты исполняет main thread явными subagent threads): Ensemble Review (линзы -> скептик-верификация каждого finding -> синтез-вердикт), Access Audit (fan-out по сущностям -> карта видимости + щели на стыках), Flaky Hunt (loop-until-trace со stop-условиями).
- Setup: working rules charter описывают session handoff (epic-state, retro-log, lessons); генерируемая секция `AGENTS.md` и handoff упоминают новые skills; на существующей кодовой базе рекомендуется `$qtim-onboard` / `$qtim-product-onboard`, при проблемах — `$qtim-doctor`.
- Запись `-> 2.4.0` в upgrade-notes.

### Исправлено

- **Setup мог сгенерировать несуществующий `model` в агентах** (боевой инцидент: `model = "gpt-5"` — субагенты не стартовали, в шаблонах при этом корректный `gpt-5.5`/`gpt-5.4`): setup теперь обязан копировать `model` из template дословно, при сомнении в доступности слага — удалять поле (наследуется модель сессии); Phase 5 проверяет совпадение с template. `$qtim-team-up` при падении спавна из-за невалидной модели чинит TOML и продолжает эпик; `$qtim-update` проверяет слаги при миграции; CI (`check_codex_agents.py`) отклоняет слаги без минорной версии в шаблонах.

## 2.3.0 — 2026-07-02

### Добавлено

- **Skill `$qtim-product-onboard`** — глубокое наполнение продуктовой памяти из кодовой базы: fan-out read-only исследователей (разделы/экраны из роутера, акторы/права из auth, словарь домена из схемы, события аналитики и фичефлаги) + синтез материалов ПМа из опциональной `docs/product-context/` (интервью, тикеты, метрики — каждый вывод со ссылкой на источник). Выход: `memory/product-map.md`, `product-actors.md`, `product-glossary.md`, `product-metrics.md`; пишет только main thread, факты с прецедентами `file:line`, гипотезы помечаются.
- **Роль `product` использует и пополняет память**: продуктовая память в Read first; термины из глоссария, метрики PRD привязываются к реальным событиям из `product-metrics.md` (отсутствующее событие — задача на трекинг, не факт); обновления памяти — через предложения в финальном выходе, пишет team-lead.
- **Интеграция с конвейером**: `$qtim-feature` Stage 1 читает продуктовую память до вопросов пользователю и предлагает прогнать `$qtim-product-onboard`, если памяти нет; setup рекомендует его после генерации PM-дорожки.
- Запись `-> 2.3.0` в upgrade-notes (миграция только для команд с PM track; dev-only не затронуты).

## 2.2.0 — 2026-07-02

### Добавлено

- **Версионирование сгенерированного состояния**: `$qtim-setup` штампует версию плагина в charter (`<!-- qtim-version: X.Y.Z -->` первой строкой) и в каждый сгенерированный `.codex/agents/*.toml` (`# qtim-version: X.Y.Z`); версию плагин берёт из собственного манифеста.
- **Skill `$qtim-update`** — двухуровневое обновление: печатает версии плагина и команды с вердиктом, даёт проверенные команды обновления плагина (`codex plugin marketplace upgrade qtim-agent-team` + `codex plugin add qtim@qtim-agent-team`, затем новая thread) и мигрирует сгенерированные файлы проекта на текущую версию строго по upgrade notes — с diff-подтверждением для файлов, правленных пользователем; `memory/` и `docs/features/` не трогаются; даунгрейд запрещён.
- **`reference/upgrade-notes.md`** — журнал миграций сгенерированного состояния по версиям (2.0.0 -> 2.1.0 -> 2.2.0) + общие правила; ведение закреплено в release-чеклисте `AGENTS.md`.
- **Версия в SessionStart hook**: анонс показывает `[qtim vX.Y.Z]` из stamp charter (или `legacy` для команд, сгенерированных до 2.2.0) и упоминает `$qtim-update`.
- Раздел «Обновление и версии» в README: где смотреть версии (`codex plugin list`, stamp в charter) и как обновляться.

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
