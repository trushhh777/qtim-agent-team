# qtim — команда Codex-субагентов под твой проект

Плагин для Codex, который разворачивает в проекте **команду специализированных subagents**: архитектор, database/backend, frontend, tester, reviewer и дополнительные роли под зрелые продукты. Вместо одного ассистента-универсала ты получаешь воспроизводимый workflow: проектирование, реализация, real-browser QA, ревью и фиксация решений в `memory/`.

qtim двух-ролевой: **разработчик** получает dev-команду с циклами implement -> test -> review, **PM/аналитик** — конвейер `$qtim-feature`, который проводит хотелку через PRD, декомпозицию, grounded-оценку и план с документированием в `docs/features/`. Роли уживаются в одном проекте.

qtim подстраивается под стек проекта: анализирует репозиторий, задаёт несколько вопросов (первый — твоя роль) и генерирует Codex custom agents под реальные фреймворки, команды и инварианты.

## Что это даёт

- **Разделение труда** — роли отвечают за свои слои: архитектура, данные, UI, тесты, ревью.
- **PM-трек** — `$qtim-feature` проводит хотелку через PRD -> декомпозицию -> оценку (S/M/L/XL с evidence из кода) -> план; артефакты версионируются в `docs/features/<slug>/`, декомпозицию и оценку дают профильные dev-агенты.
- **Продуктовая память** — `$qtim-product-onboard` собирает из кодовой базы карту разделов, модель акторов, словарь домена и реестр событий аналитики (плюс материалы ПМа из `docs/product-context/`, если есть) — intake и PRD опираются на факты, а не на пересказ.
- **Codex-native упаковка** — плагин состоит из `.codex-plugin/plugin.json`, `skills/`, custom-agent templates и Codex hooks.
- **Подстройка под стек** — setup создаёт `.codex/team-charter.md` и `.codex/agents/*.toml` под проект.
- **Контроль качества** — встроены gates: typecheck/build/tests, real-browser evidence, independent review для рискованных изменений.
- **Гибкие режимы** — `$qtim-team-lazy` для точечных задач и `$qtim-team-up` для эпиков с циклами implement -> test -> review.

## Требования

Нужен Codex с поддержкой plugins, skills и subagents. Отдельный флаг Claude Agent Teams не нужен.

qtim запускает subagent workflow только по явной просьбе или вызову соответствующего skill. Если в главном task выбран `Ultra`, Codex может proactively делегировать внутри уже разрешённого scope; qtim не включает `Ultra` сам, не расширяет им задачу и не поднимает рекурсивные команды из child agents.

## Модели и reasoning

В qtim 2.7.0 роли используют точные GPT-5.6 profiles из актуального Codex catalog:

| Роли | Model | Reasoning |
|---|---|---|
| architect, database, reviewer, product | `gpt-5.6-sol` | `high` |
| frontend | `gpt-5.6-sol` | `medium` |
| testing | `gpt-5.6-terra` | `medium` |

Модель и reasoning главного task, включая `Max`, `Ultra` и Fast, выбирает пользователь в Codex. qtim не меняет эти controls и не закрепляет `max`/`ultra` в дочерних ролях. Если точный GPT-5.6 slug недоступен в окружении, setup/update удаляет из role TOML оба поля `model` + `model_reasoning_effort`, чтобы безопасно унаследовать профиль main task; явные пользовательские overrides сохраняются через diff-подтверждение.

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

После установки открой новую задачу Codex, чтобы она подхватила skills плагина.

## Обновление и версии

Обновить сам плагин (Git-marketplace):

```bash
codex plugin marketplace upgrade qtim-agent-team   # обновить snapshot маркетплейса
codex plugin add qtim@qtim-agent-team              # переустановить плагин
```

После переустановки открой новую задачу Codex — только она подхватит обновлённые skills.

Обновить команду в проекте: `$qtim-update` — сверяет версию установленного плагина с версией сгенерированной команды и мигрирует `.codex/team-charter.md`, `.codex/agents/*.toml` и hooks по upgrade notes, не затирая твои правки.

Если `$qtim-update` изменил `.codex/agents/*.toml`, после миграции открой ещё одну новую задачу Codex перед `$qtim-team-up`, `$qtim-team-lazy` или `$qtim-feature`: уже открытая задача не перезагружает custom-agent definitions на лету.

Где смотреть версии:

- плагин — `codex plugin list`;
- команда в проекте — stamp `<!-- qtim-version: ... -->` первой строкой `.codex/team-charter.md` (SessionStart hook показывает её при старте сессии);
- `$qtim-update` печатает обе версии и вердикт.

## Быстрый старт

1. Открой Codex в корне своего проекта — в ChatGPT desktop app, CLI или IDE extension.
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
      декомпозиция -> оценки S/M/L/XL с evidence -> план по фазам
Ты:   утверждаешь каждую стадию; на выходе docs/features/favorites/
      и готовый handoff-prompt для $qtim-team-up
```

## Лицензия

MIT
