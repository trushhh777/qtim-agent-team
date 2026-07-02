---
name: qtim-team-lazy
description: "Use when the user explicitly asks for qtim lazy mode in Codex: spawn only the role agents needed for the current task, without warming the full team."
---

# qtim Team Lazy

Invocation of this skill is explicit permission to spawn only the Codex subagents needed for the current task.

## When

Use lazy mode for mode C:

- the task crosses more than one concern but can complete in one pass;
- there is no expected implement -> test -> fix -> review loop;
- you want isolation or parallel read-heavy exploration without warming every role.

Use direct work for trivial tasks. Escalate to `$qtim-team-up` if feedback loops appear.

## Steps

1. Read `.codex/team-charter.md`. If missing, ask for `$qtim-setup`.
2. Classify the task and choose only the needed role(s).
3. Spawn the needed custom agents when available; otherwise use `worker` or `explorer` fallback with inline role instructions.
4. Give each subagent a concrete scope and expected output.
5. Wait only when the next step is blocked on the result.
6. Integrate results locally, verify, and update `memory/` when durable knowledge was produced.

## Escalation

Escalate from lazy to full team-up when:

- tester finds bugs that require implementation rework;
- reviewer blocks approval;
- more roles become necessary than originally expected;
- an irreversible or ambiguous product decision appears.

Do not restart already useful agent threads. Continue them when possible; spawn missing roles only.

## Anti-Patterns

- Spawning every role in lazy mode.
- Asking an agent to do broad undefined work.
- Delegating the immediate critical-path task when you are blocked on it.
- Treating subagent conclusions as final without checking changed files and project invariants.
