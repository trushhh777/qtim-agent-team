---
name: qtim-team-down
description: Use when the user asks to finish or shut down the active qtim Codex team. Closes no-longer-needed subagent threads, records durable state in memory, and reports unfinished work honestly.
---

# qtim Team Down

In Codex there is no persistent team object on disk; "down" means close active agent threads and preserve useful state.

## Steps

1. List the active qtim agent threads you have in current context.
2. Ask any running thread for a concise final status if needed.
3. Close completed or no-longer-needed threads when the close tool is available.
4. Update `memory/` with durable decisions, bug findings, review notes, or test artifacts.
5. Mark any unfinished work clearly in the visible plan or final report.
6. Tell the user what remains open and whether a new Codex thread/session is recommended.

## Rules

- Do not delete `.codex/team-charter.md`, `.codex/agents`, hooks, or memory.
- Do not pretend an agent thread survived a restart if you no longer have its id.
- Do not leave important conclusions only in chat. Put durable project knowledge into `memory/`.
