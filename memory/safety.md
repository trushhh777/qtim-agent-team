# Safety

## Запреты

- Не создавать и не коммитить `.claude/*`, `.claude-plugin/*`, Claude slash commands или Claude Agent Teams primitives.
- Не копировать lifecycle hooks из plugin layer в project `.codex/hooks.json`: это создаёт двойные события.
- Не затирать пользовательские hook groups, track blocks, model overrides или ручные правки вне qtim markers.
- Не заменять точный model slug догаданным alias и не оставлять half-pair `model`/`model_reasoning_effort`.
- Не выполнять destructive git operations, force push или массовое удаление без отдельного явного разрешения.
- Не включать secrets, токены, локальные абсолютные пути или `.claude/` session state в commit.

## Generated-state changes

Если меняются `.codex/*`, `memory/` или секция project `AGENTS.md`, предназначенные для target projects:

1. поднять версию `plugins/qtim/.codex-plugin/plugin.json`;
2. обновить `CHANGELOG.md`;
3. добавить migration section в `plugins/qtim/reference/upgrade-notes.md`;
4. проверить version stamps и сохранение пользовательских overrides.

Если generated state не меняется, release notes должны явно говорить, что миграция не требуется.

## Hooks

Plugin layer владеет `SessionStart` и `SubagentStop`. Project layer допускает optional `PostToolUse` и foreign hooks. Любые новые или изменённые hooks требуют review/trust через `/hooks`.

## Deploy

Этот каталог — единственный source of truth и deploy point. Deploy: conventional commit с русским описанием и `git push origin main`. Не создавать промежуточные deploy-копии или zip.
