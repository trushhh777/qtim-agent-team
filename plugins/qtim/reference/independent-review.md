# Independent Review Protocol For Codex

> In Codex, qtim does not call "Codex as an external second opinion." Codex is the host. Independent review means a separate read-only reviewer agent thread with a narrow prompt, ideally using a different role/model/reasoning profile where available.

## Principles

1. Advisory, not authoritative.
2. Main thread verifies every finding against opened code.
3. Domain invariants in `.codex/team-charter.md`, `AGENTS.md`, and `memory/` win over reviewer opinion.
4. Review threads are read-only unless the user explicitly asks for a fix worker.
5. Fail soft: if a reviewer thread cannot run, record that and continue with local review unless project policy says otherwise.
6. Use only at gate points, not on every tiny edit.

## When To Use

Use independent review for:

- authorization or tenant/scope visibility;
- security-sensitive server routes;
- data migrations or destructive transformations;
- money/billing/account-state paths;
- public API contracts;
- critical browser flows before release;
- high-risk performance changes.

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
   - skipped reason if review could not run.

## Anti-Patterns

- Blindly applying independent reviewer advice.
- Asking for broad "look at the whole project" review.
- Letting a review thread edit code during review.
- Blocking all progress because an advisory review thread failed.
- Keeping raw review conclusions out of memory when they affect future decisions.
