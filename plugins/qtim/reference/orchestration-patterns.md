# Паттерны оркестрации qtim для Codex

> Этот файл читает team-lead. Subagents получают только свой bounded prompt и ссылки на `.codex/team-charter.md` / `memory/`.

Codex subagents запускаются явно. Вызов `$qtim-team-up` или `$qtim-team-lazy` является явной просьбой пользователя на соответствующий subagent workflow.

## Execution Depth

| Mode | Когда | Codex-механика |
|---|---|---|
| A Direct | простая правка, вопрос, небольшой поиск | main thread |
| B Single subagent | изоляция контекста или одна bounded работа | один `explorer`/`worker`/custom agent |
| C Lazy team | несколько ролей, один проход без петель | spawn нужных ролей по мере необходимости |
| D Full team-up | implement -> test -> fix -> retest -> review | параллельный warm-up ролей + циклы |

При сомнении стартуй дешевле и эскалируй вверх.

## Patterns

### 1. Tournament

Когда есть несколько валидных архитектурных или UX-подходов. Spawn 2-4 independent agents with different angles, then synthesize in main thread or a reviewer/judge agent.

Rules:

- every candidate gets the same rubric;
- rubric references `memory/invariants.md`;
- main thread decides and records the winning ADR in `memory/decisions.md`.

### 2. Loop Until Done

Когда нужен повтор до stop condition: flaky bug, browser reproduction, performance threshold.

Rules:

- set max iterations and time budget;
- tester owns reproduction evidence;
- implementation agent fixes only after the bug is localized;
- record final trace and fix in `memory/bug-log.md`.

### 3. Classify And Act

Когда нужно разложить backlog, bug list, failing tests, routes, tables or components by owner.

Rules:

- use explorer/classifier first for read-heavy triage;
- main thread assigns owners;
- P0/P1 can trigger immediate worker tasks;
- lower priority items go to memory/backlog rather than spawning unnecessary agents.

### 4. Fan-Out And Synthesize

Когда есть независимые scopes: routes, tables, packages, UI screens, risk lenses.

Rules:

- one agent per independent scope;
- disjoint write sets for write tasks;
- read-only audit scopes can run broadly;
- main thread deduplicates and verifies file:line claims.

### 5. Independent Review / Adversarial Verification

Когда изменение security-critical, money-critical, public API, migration, auth, tenant/scope visibility, or hard to rollback.

Use `independent-review.md`. Spawn one or more read-only reviewer threads with a narrow prompt. They do not edit code. Main thread verifies every finding.

### 6. Generate And Filter

Когда нужно много дешёвых вариантов: copy, names, empty states, UX labels, test scenario names.

Rules:

- generator produces many candidates;
- filter/judge uses explicit rubric;
- top-K only enters implementation;
- record final choice if product-visible.

## Global Rules

- Do not spawn subagents unless the user explicitly asked via qtim skill or direct delegation request.
- Do not paste full orchestration rules into subagent prompts.
- Do not run parallel writers over overlapping files.
- Subagent output is evidence, not truth.
- Durable decisions go into `memory/`.
- Close completed threads when they are no longer needed.
