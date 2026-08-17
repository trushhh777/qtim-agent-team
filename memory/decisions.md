# Реестр решений

Формат:

```text
YYYY-MM-DD — <решение> — <почему> — <ADR или docs/features/<slug>/, если есть>
```

## Принятые решения

- 2026-07-27 — Локальная qtim-команда включает dev и PM дорожки — пользователь работает в обеих ролях; compact roster соответствует отсутствию application слоёв — `.codex/team-charter.md`.
- 2026-07-27 — Режим автономности `design approval first`; independent code review включён — подтверждённые defaults setup — `.codex/team-charter.md`.
- 2026-07-27 — Project-level `PostToolUse` отключён; lifecycle hooks остаются plugin-bundled — исключает дублирование `SessionStart`/`SubagentStop`.
- 2026-07-27 — В 2.10 role inheritance заменён явными atomic GPT-5.6 pairs и fail-visible fallback — недоступная pair оставляет migration pending, user override сохраняется через diff — `CHANGELOG.md:5-19`, `plugins/qtim/reference/model-profiles.md:19,28-33`.
- 2026-07-27 — Каждый созданный ADR получает `$qtim-grill` и отдельного clean-context Sol adversary независимо от code-review toggle — design independence и честный skipped contract — `CHANGELOG.md:15-24`.
- 2026-07-27 — Codex-репозиторий является источником смысла, Claude sibling получает семантический, а не текстовый порт — runtime contracts не смешиваются — `docs/claude-port-map.md:1-12,50-55`.
- 2026-07-28 — Первоначальный read-only vertical slice Mission Plan был выбран как
  промежуточное состояние 2.12; решение superseded до release следующей строкой —
  `docs/cross-dialog-missions/mission-plan-codex.md`.
- 2026-07-28 — 2.12 выпускает весь Mission Plan одним релизом: App-first DAG,
  node-local lazy, isolated writer worktrees, verified commits в topological
  order, bounded verification/fixes и fail-visible recovery; runtime registry
  остаётся opaque/gitignored, а App smoke и independent review — обязательные
  release gates — `docs/cross-dialog-missions/adr-001-mission-state-and-git-integration.md`,
  `plugins/qtim/skills/qtim-mission/SKILL.md`.
- 2026-07-30 — Утверждён план семантического порта Claude qtim 1.13.0 — Stage 6 handoff готов — `docs/features/claude-1-13-minimal-diff-port/`.

Утверждённые фичи добавляются одной строкой-указателем на `docs/features/<slug>/`; содержимое PRD/plan сюда не копируется.
