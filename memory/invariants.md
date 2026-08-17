# Инварианты

1. **Codex-native.** Claude-only tokens и plugin-relative `../` запрещены в agent templates; target state использует Codex skills/agents/charter: `.github/scripts/check_codex_agents.py:98-106`, `AGENTS.md:20-24`.
2. **Явная авторизация.** qtim fan-out начинается только по skill invocation или прямой просьбе; `Ultra` не расширяет scope: `plugins/qtim/reference/orchestration-patterns.md:127-134`, `plugins/qtim/reference/model-profiles.md:23-25`.
3. **Main-thread ownership.** A/B/C/D измеряется глубиной coordination loops; main владеет graph, child agents не спавнят qtim descendants, output остаётся evidence: `plugins/qtim/reference/orchestration-patterns.md:7-25,127-135`.
4. **Task-scoped threads.** Main проверяет доступные descendants, соблюдает cap и закрывает завершённые threads; скрытой постоянной команды нет: `plugins/qtim/reference/orchestration-patterns.md:20-25`.
5. **Track safety.** Dev/PM blocks имеют парные markers; setup меняет только свой block и сохраняет ручной текст вне markers: `plugins/qtim/skills/qtim-setup/SKILL.md:130-145`.
6. **Hook ownership и schema.** Bundled file содержит ровно `SessionStart`/`SubagentStop`, project template — ровно `PostToolUse`; canonical matcher group имеет один `type: command` handler: `.github/scripts/check_hooks.py:24-46,87-152`.
7. **Hook runtime output.** `SubagentStop` возвращает только непустой UTF-8 JSON `systemMessage`; `PostToolUse` — только `hookSpecificOutput.additionalContext`: `.github/scripts/check_hooks.py:361-378,403-417`.
8. **Cross-platform hooks.** Bundled commands резолвят Git root; Windows variant использует literal leaf path и UTF-8: `.github/scripts/check_hooks.py:186-223`.
9. **Self-contained generation.** Agent templates не содержат plugin-relative paths; setup-generated charter/roles/memory переносят нужную механику внутрь target project: `.github/scripts/check_codex_agents.py:102-106`, `plugins/qtim/skills/qtim-setup/SKILL.md:112-155`.
10. **Atomic model profiles.** Exact `model` + `model_reasoning_effort` задаются вместе; `inherit`, half-pair, guessed alias и silent fallback запрещены, override сохраняется через diff: `plugins/qtim/reference/model-profiles.md:19,28-33`, `.github/scripts/check_codex_agents.py:108-144`.
11. **ADR gate.** Каждый настоящий ADR проходит `$qtim-grill`, затем clean-context read-only Sol adversary; `skipped` не является pass: `plugins/qtim/reference/independent-review.md:14-27`.
12. **Independent code review.** Canonical high-risk matrix требует read-only review; low-risk skip фиксируется явно, любой runtime failure остаётся skipped/failure: `plugins/qtim/reference/independent-review.md:29-44,71-88`.
13. **Feature continuity.** Существующий slug продолжается с первого неутверждённого artifact; fast→full transition и plan deviations фиксируются append-only: `plugins/qtim/reference/feature-pipeline.md:12-14,27-38,94-100`.
14. **Atomic upgrade.** Миграции применяются oldest→newest; при первом `pending` дальнейшие версии не применяются, stamps остаются на последней полностью завершённой: `plugins/qtim/skills/qtim-update/SKILL.md:34-43`.
15. **Durable memory.** Решения и approved-feature pointers живут в `memory/`, feature artifacts — в `docs/features/`; subagent chat не является источником истины: `plugins/qtim/reference/intake-protocol.md:27-30`, `plugins/qtim/reference/feature-pipeline.md:12-14,94-100`.
16. **Release migration contract.** Generated-state impact синхронно отражается в version, `CHANGELOG.md` и `upgrade-notes.md`; иначе явно указывается отсутствие миграции: `AGENTS.md:61-65`.
17. **Source of truth.** Этот репозиторий является deploy point; Claude sibling портируется семантически, `.claude/` остаётся local state: `AGENTS.md:35-40`, `docs/claude-port-map.md:1-12,50-55`.
