# Independent Review Protocol For Codex

> In Codex, qtim does not call "Codex as an external second opinion." Codex is the host. Independent review means a separate read-only reviewer agent thread with a narrow prompt, ideally using a different role/model/reasoning profile where available.

## Principles

1. Advisory, not authoritative.
2. Main thread verifies every finding against opened code.
3. Domain invariants in `.codex/team-charter.md`, `AGENTS.md`, and `memory/` win over reviewer opinion.
4. Review threads are read-only unless the user explicitly asks for a fix worker.
5. Fail soft: if a reviewer thread cannot run, record that and continue with local review unless project policy says otherwise.
6. Use only at gate points and proportionally to the actual diff risk, not on every tiny edit.

## When To Use

Independent review is mandatory to request when the actual diff matches any item in this canonical high-risk matrix:

- security/auth/tenant-scope visibility;
- money/billing/account state;
- documented domain invariants or public contracts;
- data-transform or destructive migrations;
- critical browser flows before release;
- high-risk performance/reliability changes;
- another demonstrably hard-to-rollback decision.

For a low-risk diff limited to copy, styles, documentation or an internal refactor without contract/invariant changes, the reviewer may skip it and must record `independent review: skipped (low-risk diff)`. Setup, role templates and orchestration copy this matrix without adding or removing categories.

For money-critical work, require convergence of two independent traces when runtime review is available. If it cannot run, record the failure and follow the fail-open/fail-closed policy from the project charter; do not silently call the gate passed.

## Prompt Shape

Use tight prompts:

```text
You are an independent read-only reviewer.

Scope: <files/diff/ADR/feature>.
Read first: AGENTS.md, .codex/team-charter.md, memory/invariants.md.
Do not edit files.

Find defects in:
- correctness;
- security/authorization;
- data visibility;
- migrations/idempotency;
- race conditions;
- missing tests;
- rollback and error states.

Return findings only when grounded in code or documented invariants.
For each finding: file:line, severity P0-P3, invariant/rule, concrete fix.
Mark hypotheses explicitly.
```

## Integration

1. Main thread reads the review result.
2. Open each referenced file/line.
3. Confirm or reject each finding.
4. Route confirmed blockers to the owning role.
5. Record summary in `memory/review-report.md`:
   - findings confirmed;
   - findings rejected and why;
   - skipped reason for a low-risk diff or if review could not run.

## Anti-Patterns

- Blindly applying independent reviewer advice.
- Asking for broad "look at the whole project" review.
- Letting a review thread edit code during review.
- Blocking all progress because an advisory review thread failed.
- Keeping raw review conclusions out of memory when they affect future decisions.
