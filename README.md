# qtim — команда Codex-субагентов под твой проект

Плагин для Codex, который разворачивает в проекте **команду специализированных subagents**: архитектор, database/backend, frontend, tester, reviewer и дополнительные роли под зрелые продукты. Вместо одного ассистента-универсала ты получаешь воспроизводимый workflow: проектирование, реализация, real-browser QA, ревью и фиксация решений в `memory/`.

qtim двух-ролевой: **разработчик** получает dev-команду с циклами implement -> test -> review, **PM/аналитик** — конвейер `$qtim-feature`, который проводит хотелку через PRD, декомпозицию, grounded-оценку и план с документированием в `docs/features/`. Роли уживаются в одном проекте.

qtim подстраивается под стек проекта: анализирует репозиторий, задаёт несколько вопросов (первый — твоя роль) и генерирует Codex custom agents под реальные фреймворки, команды и инварианты.

## Что это даёт

- **Разделение труда** — роли отвечают за свои слои: архитектура, данные, UI, тесты, ревью.
- **PM-трек** — `$qtim-feature` проводит хотелку через PRD -> декомпозицию -> оценку (S/M/L с evidence из кода) -> план; артефакты версионируются в `docs/features/<slug>/`, декомпозицию и оценку дают профильные dev-агенты.
- **Продуктовая память** — `$qtim-product-onboard` собирает из кодовой базы карту разделов, модель акторов, словарь домена и реестр событий аналитики (плюс материалы ПМа из `docs/product-context/`, если есть) — intake и PRD опираются на факты, а не на пересказ.
- **Codex-native упаковка** — плагин состоит из `.codex-plugin/plugin.json`, `skills/`, custom-agent templates и Codex hooks.
- **Подстройка под стек** — setup создаёт `.codex/team-charter.md` и `.codex/agents/*.toml` под проект.
- **Контроль качества** — встроены gates: typecheck/build/tests, real-browser evidence, independent review для рискованных изменений.
- **Гибкие режимы** — `$qtim-team-lazy` для точечных задач и `$qtim-team-up` для эпиков с циклами implement -> test -> review.

## Требования

Нужен Codex с поддержкой plugins, skills и subagents. Отдельный флаг Claude Agent Teams не нужен.

Codex subagents запускаются только по явной просьбе. Вызов `$qtim-feature`, `$qtim-team-up` или `$qtim-team-lazy` считается явным запросом на соответствующий subagent workflow.

## Установка

Из GitHub marketplace-репозитория:

```bash
codex plugin marketplace add trushhh777/qtim-agent-team
codex plugin add qtim@qtim-agent-team
```

Локально из клона репозитория:

```bash
codex plugin marketplace add .
codex plugin add qtim@qtim-agent-team
```

После установки открой новую Codex thread/session, чтобы Codex подхватил skills плагина.

## Обновление и версии

Обновить сам плагин (Git-marketplace):

```bash
codex plugin marketplace upgrade qtim-agent-team   # обновить snapshot маркетплейса
codex plugin add qtim@qtim-agent-team              # переустановить плагин
```

После переустановки открой новую Codex thread — только она подхватит обновлённые skills.

Обновить команду в проекте: `$qtim-update` — сверяет версию установленного плагина с версией сгенерированной команды и мигрирует `.codex/team-charter.md`, `.codex/agents/*.toml` и hooks по upgrade notes, не затирая твои правки.

Где смотреть версии:

- плагин — `codex plugin list`;
- команда в проекте — stamp `<!-- qtim-version: ... -->` первой строкой `.codex/team-charter.md` (SessionStart hook показывает её при старте сессии);
- `$qtim-update` печатает обе версии и вердикт.

## Быстрый старт

1. Открой Codex в корне своего проекта.
2. Разверни команду (первым вопросом setup спросит твою роль: Developer, PM/Analyst или обе):

   ```text
   $qtim-setup
   ```

3. После setup используй режим под задачу:

   ```text
   $qtim-onboard          # dev: один раз наполнить память картой, инвариантами и конвенциями
   $qtim-product-onboard  # PM: один раз собрать продуктовую память из кода
   $qtim-feature          # PM/аналитик: хотелка -> PRD -> декомпозиция -> оценка -> план
   $qtim-team-up          # полный эпик с циклами implement -> test -> review
   $qtim-team-lazy        # роли по мере надобности
   $qtim-team-retro       # после эпика: дистиллировать уроки в память
   $qtim-team-down        # закрыть активные agent threads и зафиксировать память
   ```

## Skills

| Skill | Когда использовать |
|---|---|
| `$qtim-setup` | Один раз в новом проекте: выбрать роль, сгенерировать charter, custom agents, hooks и memory |
| `$qtim-feature` | PM/аналитик: провести хотелку от идеи до плана — PRD, декомпозиция, оценка, handoff в реализацию |
| `$qtim-team-up` | Крупная задача/эпик с обратной связью между implement/test/review |
| `$qtim-team-lazy` | Быстрая или средняя задача без полного прогрева команды |
| `$qtim-onboard` | После setup на существующей кодовой базе: наполнить dev-память картой, инвариантами и конвенциями с `file:line` |
| `$qtim-product-onboard` | После setup с PM-дорожкой: собрать продуктовую память из кода — разделы, акторы, словарь домена, события аналитики |
| `$qtim-team-retro` | После завершённого эпика (до team-down): дистиллировать уроки «триггер -> действие» в память проекта и ролей |
| `$qtim-team-down` | Завершить активные agent threads и сохранить durable state; незавершённый эпик фиксируется в `memory/epic-state.md` |
| `$qtim-doctor` | «Что-то не работает» или после обновления: read-only диагностика charter/агентов/hooks/памяти с таблицей фиксов |
| `$qtim-update` | Проверить версии плагина/команды и мигрировать сгенерированные файлы на текущую версию |

## Что появится в проекте после setup

- `.codex/team-charter.md` — контракт команды с track-блоками под выбранные роли, инварианты и правила работы.
- `.codex/agents/*.toml` — Codex custom agents под стек проекта (включая `qtim-product` для PM-трека).
- `.codex/hooks.json` — опциональные reminders для SessionStart/SubagentStop/PostToolUse.
- `memory/` — карта проекта, команды, решения, инварианты, баги и review reports; при работе команды сюда добавляются `epic-state.md` (handoff незавершённого эпика между сессиями), `retro-log.md` и `lessons.md` (уроки ретроспектив).
- `AGENTS.md` — указатель для Codex на qtim-команду и локальные правила проекта.
- `docs/features/<slug>/` — появляется при работе `$qtim-feature`: intake, PRD, декомпозиция, оценка, план.

## Как это выглядит

```text
Ты:   $qtim-team-up, добавь раздел избранного: БД, API и UI
qtim: architect проектирует -> database делает схему -> frontend пишет UI ->
      testing проверяет браузером -> reviewer даёт APPROVED / NOT APPROVED
Ты:   получаешь результат, verification summary и обновлённую память проекта
```

PM/аналитик:

```text
Ты:   $qtim-feature, хотим избранное для товаров
qtim: intake-вопросы -> PRD -> dev-агенты смотрят реальный код ->
      декомпозиция -> оценки S/M/L с evidence -> план по фазам
Ты:   утверждаешь каждую стадию; на выходе docs/features/favorites/
      и готовый handoff-prompt для $qtim-team-up
```

## Лицензия

MIT
