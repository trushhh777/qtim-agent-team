# AGENTS.md

This repository is a Codex plugin marketplace with one plugin: `qtim`.

All content is primarily Russian. The repository has no build step and no application runtime; the source is Markdown, JSON, and TOML used by Codex.

## Structure

- `.agents/plugins/marketplace.json` — Codex marketplace manifest exposing `plugins/qtim`.
- `plugins/qtim/.codex-plugin/plugin.json` — Codex plugin manifest.
- `plugins/qtim/skills/` — Codex skills: `qtim-setup`, `qtim-team-up`, `qtim-team-lazy`, `qtim-team-down`.
- `plugins/qtim/agents/` — Codex custom agent TOML templates copied by `$qtim-setup` into target projects.
- `plugins/qtim/reference/` — shared mechanics for intake, orchestration patterns, and independent review.
- `plugins/qtim/hooks/hooks.json` — optional plugin-bundled Codex lifecycle hooks.

## Architecture Rules

- This is Codex-native. Do not add `.claude/*`, `.claude-plugin/*`, Claude slash commands, or Claude Agent Teams primitives.
- Use Codex skills instead of slash commands.
- Use `.codex/team-charter.md` and `.codex/agents/*.toml` for generated target-project state.
- Codex subagents are explicit and session-local. Do not imply hidden persistent team state.
- Main thread is the team lead; subagent outputs are advisory until checked.
- Durable project decisions belong in `memory/`, not only in chat.
- Independent review is a separate read-only Codex agent thread, not "Codex as an external consultant".

## Validation

Run locally before handing off changes:

```bash
python3 -m json.tool .agents/plugins/marketplace.json > /dev/null
python3 -m json.tool plugins/qtim/.codex-plugin/plugin.json > /dev/null
python3 -m json.tool plugins/qtim/hooks/hooks.json > /dev/null
python3 .github/scripts/check_placeholders.py
python3 .github/scripts/check_skills.py
python3 .github/scripts/check_links.py
python3 .github/scripts/check_codex_agents.py
```

In CI, use repo-local scripts only. Before release, also run Codex `plugin-creator`'s `validate_plugin.py plugins/qtim` from the local Codex skill installation if it is available.

## Release Notes

For meaningful plugin changes, bump `version` in `plugins/qtim/.codex-plugin/plugin.json` and update `CHANGELOG.md`.

Commit style: conventional commits with Russian descriptions, for example `feat(setup): ...`, `fix(agents): ...`, `docs(readme): ...`.
