---
name: qtim-team-up
description: Use when the user explicitly asks to run a full qtim team in Codex for a substantial task or epic. Reads .codex/team-charter.md, spawns the selected role agents in parallel when subagent tools are available, coordinates implementation/test/review loops, and reports results.
---

# qtim Team Up

Invocation of this skill is explicit permission to run a Codex subagent workflow for the roles defined in `.codex/team-charter.md`.

Use Codex subagent threads and custom agents. Do not assume a hidden persistent team object.

## Preconditions

1. Read `.codex/team-charter.md`.
2. If it does not exist, stop and ask the user to run `$qtim-setup`.
3. Read only the needed shared references:
   - `../../reference/intake-protocol.md`;
   - `../../reference/orchestration-patterns.md`;
   - `../../reference/independent-review.md`;
   - `../../reference/model-profiles.md`.
4. Проверь `memory/epic-state.md` (его пишет `$qtim-team-down` при незавершённом эпике): если файл есть и эпик не закрыт — после подъёма команды покажи резюме и предложи продолжить с зафиксированного места, восстановив задачи из «В полёте» в видимом плане с их ролями.
5. Если задача ссылается на фичу из `docs/features/<slug>/`, прочитай `plan.md` + `prd.md` полного трека или единый `feature-brief.md` fast-path как источник scope и acceptance criteria. До работы переведи плановый документ и связанные артефакты в `In Development`; только после gates — в `Done`. Отклонения с обоснованием и новые edge cases фиксируй в «Истории изменений» выбранного планового документа.

## Decision Matrix

Use full team-up only for mode D:

- there is an epic or substantial change;
- implementation crosses roles;
- there will likely be loops: implement -> test -> fix -> retest -> review.

If the task is a single pass without feedback loops, switch to `$qtim-team-lazy`. If it is trivial, handle it directly.

## Liveness Model

Codex subagents are task-scoped agent threads, not durable named team members.

- Track the current roster in your own context: `role -> agent id`.
- Before spawning after resume or context loss, inspect descendants when the runtime exposes Active/Done agent threads; reuse the matching reachable thread and spawn only missing roles.
- If you still have a live agent id, send follow-up input to that thread.
- Never assume a remembered handle is live or a missing handle is gone: verify through the current runtime, then recover or respawn.
- Close completed threads when no longer needed so the next batch has capacity.

## Spawning

Spawn only currently needed roles in parallel when the subagent tool is available; batch the roster when independent work exceeds the available thread slots.

Use custom agent types from `.codex/agents/*.toml` when Codex exposes them. If the current task has not loaded custom agents yet, either ask the user to start a new Codex task or use `worker` / `explorer` fallback with the role instructions embedded in the prompt.

Если spawn custom agent падает именно из-за model pair, не останавливай эпик и не стирай override вслепую. Сравни пару с template и локальным catalog. Только когда это доказанно неизменённый qtim-default, которого нет в catalog, сообщи пользователю, удали **оба** поля `model` + `model_reasoning_effort` и повтори с наследованием main profile. Любую отличающуюся/непроверенную пару сохрани: используй `worker` / `explorer` fallback с inline role instructions, покажи нужный diff и отправь системную починку в `$qtim-update`. Транзиентную auth/network ошибку не классифицируй как недоступную модель.

## Model And Reasoning Policy

- Не переключай модель, reasoning или Fast главного task: это пользовательские controls.
- Используй role policy из загруженных TOML: отсутствие model pair означает наследование session profile, явная pair — осознанный pin. Не повышай child agents до `max`/`ultra` без прямой просьбы пользователя.
- `Ultra` у main task разрешает Codex proactively делегировать внутри scope этого вызова, но не означает «спавнить все роли». Execution depth A/B/C/D, roster и write scopes по-прежнему определяет main thread.
- Child agents не спавнят qtim-команду рекурсивно. Дополнительные роли спавнит main thread; fan-out ограничивай доступными slots и разбивай на batches, если независимых работ больше.

Default Standard roster:

- `architect` -> `qtim-architect`;
- `db` -> `qtim-database`;
- `front` -> `qtim-frontend`;
- `tester` -> `qtim-testing`;
- `reviewer` -> `qtim-reviewer`;
- `explorer` -> built-in `explorer`.

Compact and Extended rosters come from the charter, not this file.

## Prompt Template Per Role

Use a compact prompt. Do not paste the whole charter into every subagent.

```text
Ты роль <role> команды qtim для проекта <project>.

Read first:
1. AGENTS.md
2. .codex/team-charter.md: sections for <role>, domain invariants, working rules
3. role-specific read-on-start files from the charter
4. memory/lessons.md, секция своей роли — если файл существует (уроки прошлых retro)

Mission: <role mission from charter>.
Do not touch: <do-not-touch from charter>.
Skills/practices: <skills and mandatory practices from charter>.

Return concise artifacts, changed files if any, verification performed, blockers, and memory updates needed.
```

For implementation agents, remind them that other agents may edit in parallel and they must not revert unrelated changes.

## Coordination Flow

1. Run design first for non-trivial work: architect produces brief/ADR and open questions.
2. Ask for user approval before irreversible or ambiguous work, following `intake-protocol.md`.
3. Parallelize only disjoint work scopes; `Ultra` не отменяет этот gate и не является причиной увеличить fan-out.
4. Route implementation by ownership.
5. Tester verifies with real browser for UI changes.
6. Reviewer runs final gates. При активной секции independent review в charter он классифицирует фактический diff по canonical high-risk matrix: security/auth/tenant-scope visibility; money/billing/account state; documented domain invariants/public contracts; data-transform/destructive migrations; critical browser flows; high-risk performance/reliability; другое доказанно hard-to-rollback изменение. Любое совпадение требует отдельного read-only review thread; low-risk diff допускает зафиксированный `skipped (low-risk diff)`. Секции нет или она помечена «выключен» -> не требуй gate.
7. Main agent integrates and checks all results. Subagent output is input, not authority.
8. Commit durable decisions to `memory/`.

## Reporting

Final report should be result-first:

- files changed and user-visible outcome;
- gates run and status;
- findings fixed or left open;
- memory files updated;
- если работа шла по фиче из `docs/features/<slug>/` — отмеченные пункты `plan.md` или `feature-brief.md`, обновлённый Status (`In Development` / `Done`) и зафиксированные в «Истории изменений» отклонения;
- если в preconditions найден незавершённый epic-state — его резюме и предложение продолжить;
- active agent threads closed or still running.

Do not report a raw transcript of agent chatter.
