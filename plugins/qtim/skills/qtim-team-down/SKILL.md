---
name: qtim-team-down
description: Use when the user asks to finish or shut down the active qtim Codex team. Closes no-longer-needed subagent threads, records durable state in memory, and reports unfinished work honestly.
---

# qtim Team Down

In Codex there is no persistent team object on disk; "down" means close active agent threads and preserve useful state.

**Перед сворачиванием:** для завершённого эпика режима C/D сначала предложи `$qtim-team-retro` — уроки эпика дистиллируются в память, пока контекст сессии ещё цел.

## Steps

1. List the active qtim agent threads you have in current context.
2. Ask any running thread for a concise final status if needed.
3. Close completed or no-longer-needed threads when the close tool is available.
4. Update `memory/` with durable decisions, bug findings, review notes, or test artifacts.
5. Эпик не завершён -> запиши `memory/epic-state.md` (его читает `$qtim-team-up` в новой сессии и предлагает продолжить):

   ```markdown
   # Epic state: <название эпика>
   Обновлено: <дата> · Фаза: design | impl | test | review
   ## Сделано
   ## В полёте (задача — роль — статус — следующий шаг)
   ## Открытые вопросы / блокеры
   ## Следующий шаг при продолжении
   ```

   Эпик завершён — **удали** устаревший `epic-state.md`, не оставляй ложного «в полёте».
6. Mark any unfinished work clearly in the visible plan or final report.
7. Tell the user what remains open and whether a new Codex thread/session is recommended.

## Rules

- Do not delete `.codex/team-charter.md`, `.codex/agents`, hooks, or memory.
- Do not pretend an agent thread survived a restart if you no longer have its id.
- Do not leave important conclusions only in chat. Put durable project knowledge into `memory/`.
