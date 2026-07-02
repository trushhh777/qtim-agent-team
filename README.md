# qtim — команда Codex-субагентов под твой проект

Плагин для Codex, который разворачивает в проекте **команду специализированных subagents**: архитектор, database/backend, frontend, tester, reviewer и дополнительные роли под зрелые продукты. Вместо одного ассистента-универсала ты получаешь воспроизводимый workflow: проектирование, реализация, real-browser QA, ревью и фиксация решений в `memory/`.

qtim подстраивается под стек проекта: анализирует репозиторий, задаёт несколько вопросов и генерирует Codex custom agents под реальные фреймворки, команды и инварианты.

## Что это даёт

- **Разделение труда** — роли отвечают за свои слои: архитектура, данные, UI, тесты, ревью.
- **Codex-native упаковка** — плагин состоит из `.codex-plugin/plugin.json`, `skills/`, custom-agent templates и Codex hooks.
- **Подстройка под стек** — setup создаёт `.codex/team-charter.md` и `.codex/agents/*.toml` под проект.
- **Контроль качества** — встроены gates: typecheck/build/tests, real-browser evidence, independent review для рискованных изменений.
- **Гибкие режимы** — `$qtim-team-lazy` для точечных задач и `$qtim-team-up` для эпиков с циклами implement -> test -> review.

## Требования

Нужен Codex с поддержкой plugins, skills и subagents. Отдельный флаг Claude Agent Teams не нужен.

Codex subagents запускаются только по явной просьбе. Вызов `$qtim-team-up` или `$qtim-team-lazy` считается явным запросом на соответствующий subagent workflow.

## Установка

Из GitHub marketplace-репозитория:

```bash
codex plugin marketplace add toiiia/qtim-agent-team
codex plugin add qtim@qtim-agent-team
```

Локально из клона репозитория:

```bash
codex plugin marketplace add .
codex plugin add qtim@qtim-agent-team
```

После установки открой новую Codex thread/session, чтобы Codex подхватил skills плагина.

## Быстрый старт

1. Открой Codex в корне своего проекта.
2. Разверни команду:

   ```text
   $qtim-setup
   ```

3. После setup используй режим под задачу:

   ```text
   $qtim-team-up      # полный эпик с циклами implement -> test -> review
   $qtim-team-lazy    # роли по мере надобности
   $qtim-team-down    # закрыть активные agent threads и зафиксировать память
   ```

## Skills

| Skill | Когда использовать |
|---|---|
| `$qtim-setup` | Один раз в новом проекте: сгенерировать charter, custom agents, hooks и memory |
| `$qtim-team-up` | Крупная задача/эпик с обратной связью между implement/test/review |
| `$qtim-team-lazy` | Быстрая или средняя задача без полного прогрева команды |
| `$qtim-team-down` | Завершить активные agent threads и сохранить durable state |

## Что появится в проекте после setup

- `.codex/team-charter.md` — контракт команды, роли, инварианты и правила работы.
- `.codex/agents/*.toml` — Codex custom agents под стек проекта.
- `.codex/hooks.json` — опциональные reminders для SessionStart/SubagentStop/PostToolUse.
- `memory/` — карта проекта, команды, решения, инварианты, баги и review reports.
- `AGENTS.md` — указатель для Codex на qtim-команду и локальные правила проекта.

## Как это выглядит

```text
Ты:   $qtim-team-up, добавь раздел избранного: БД, API и UI
qtim: architect проектирует -> database делает схему -> frontend пишет UI ->
      testing проверяет браузером -> reviewer даёт APPROVED / NOT APPROVED
Ты:   получаешь результат, verification summary и обновлённую память проекта
```

## Лицензия

MIT
