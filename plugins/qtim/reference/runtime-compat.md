# Runtime compatibility contract

Последняя сверка: **2026-07-28**, `codex-cli 0.144.1`.

Этот файл отделяет подтверждённые возможности Codex от проектных допущений qtim. После
обновления Codex его проверяет `$qtim-doctor`; догадка о runtime не превращается в скрытый
инвариант generated state.

## Подтверждено runtime и документацией

- `AGENTS.md` загружается Codex до начала работы. Поэтому setup пишет компактный
  самодостаточный qtim-контракт между `qtim:contract:*` markers, а подробности оставляет в
  `.codex/team-charter.md` и `memory/`.
- Project custom agents читаются из `.codex/agents/*.toml`; `sandbox_mode = "read-only"`
  механически ограничивает reviewer.
- Plugin hooks обнаруживаются через `hooks/hooks.json`; `$PLUGIN_ROOT` доступен командам.
- `SubagentStop` с exit `2` продолжает agent, а `stop_hook_active` позволяет не зациклить
  повторный stop. Exit `0` может вернуть JSON `systemMessage`.
- Project `PostToolUse` использует `hookSpecificOutput.additionalContext`, а не plain stdout.

## Проверяется этим репозиторием

`.github/scripts/check_hooks.py` исполняет POSIX/Windows handlers в временном git-проекте:
no-charter no-op, versioned SessionStart, JSON handoff, opt-in screenshot block, retry guard
и свежий tester artifact. `check_codex_agents.py` проверяет model pairs и read-only reviewer.

## Границы и fail-soft

- Matcher screenshot gate ожидает custom-agent type `qtim-testing`. Если будущий runtime
  изменит значение `agent_type`, gate останется advisory/no-op до обновления совместимости;
  `$qtim-doctor` должен показать это как `warn`, а не выдать непроверенный pass.
- Nested `AGENTS.md` зависит от рабочей директории, а не от каждого открытого файла. qtim не
  имитирует Claude path-scoped rules: критические инварианты дублируются компактно в role
  checklists и проверяются reviewer/CI.
- Полный charter не инжектируется hook-ом в каждый turn: автоматический корневой
  `AGENTS.md` даёт стартовый контракт, роли затем явно читают charter и нужную memory.

## Probe после обновления Codex

1. Запусти repo validation и `$qtim-doctor`.
2. В тестовом проекте создай marker agent `qtim-testing`, заверши его без screenshot и
   проверь один controlled retry.
3. Убедись, что reviewer не может писать в workspace.
4. Проверь `/hooks` и trust prompt; неизвестные команды не исполняй.
5. Обнови дату/версию выше только вместе с воспроизводимым evidence.
