# Intake-протокол qtim для Codex

> Generic reference qtim. Проектные инварианты и роли живут в `.codex/team-charter.md`; здесь — переносимая механика принятия задач.

## Принцип

Участие пользователя асимметрично:

- анализ и проектирование — пользователь в контуре;
- реализация, тесты и ревью — автопилот после approval;
- необратимые или неоднозначные развилки возвращаются пользователю даже во время реализации.

Codex main thread остаётся team-lead. qtim subagent workflow авторизуется явной просьбой пользователя или вызовом qtim skill. Agent threads живут в scope текущего task и могут быть восстановлены только когда runtime их показывает; скрытой постоянной команды нет. Если пользователь выбрал `Ultra`, Codex может proactively делегировать внутри уже разрешённого scope, но это не расширяет задачу и не выбирает execution depth вместо main thread.

## Pipeline

1. Classify task: feature, bug, refactor, audit, design, support.
2. Pick execution depth:
   - A Direct: main thread handles it.
   - B Single subagent: one bounded agent for isolated work.
   - C Lazy team: several roles, one-pass pipeline.
   - D Full team-up: iterative implement/test/review loops.
3. Decide whether design approval is required.
4. For non-trivial work, produce design brief or ADR.
5. Get approval for irreversible, ambiguous, product-visible, public API, security, money, or data migration decisions.
6. Execute with selected roles.
7. Verify with tests/browser/review.
8. Record durable decisions and findings in `memory/`; approved decisions and features get a pointer line in the `memory/decisions.md` registry.
9. Report outcome, not agent chatter.

## Fork Test

Bring a decision to the user when any condition is true:

- hard or expensive to roll back;
- data deletion or transformation;
- public API contract change;
- money/billing/account state;
- authorization, tenant/scope visibility, or security boundary;
- product behavior can reasonably mean two different things;
- conflict with `memory/` or `AGENTS.md`;
- new actor, role, channel, or externally visible surface.

Do not ask for:

- role selection;
- file naming when project conventions cover it;
- equivalent implementation details;
- reversible internal refactors;
- order of tool calls;
- report formatting.

## Design Brief

For non-trivial work, produce:

- goal in user language;
- affected layers;
- relevant invariants;
- risks and reversibility;
- 2-3 approach options if meaningful;
- recommended option;
- open questions that block safe execution;
- proposed roles and verification gates.

Use plan/approval features when available. Otherwise ask for direct confirmation in chat.

## Implementation Silence

After approval, keep moving until completion unless a new fork appears. Do not drip-feed low-value questions.

## Anti-Patterns

- Coding a non-trivial feature before design approval.
- Spawning full team for a one-file obvious fix.
- Letting subagents decide product requirements.
- Treating independent reviewer output as authoritative without verification.
- Leaving durable decisions only in conversation instead of `memory/`.
