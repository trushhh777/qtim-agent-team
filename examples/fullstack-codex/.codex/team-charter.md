<!-- qtim-version: 2.11.0 -->
# qtim team charter — fullstack golden

## Roles and model matrix

Team-lead `gpt-5.6-sol` + `ultra`; architect/reviewer Sol+xhigh;
database/frontend/product Sol+high; testing Terra+medium; explorer Luna+medium.

## Working rules

Main thread owns fan-out. Role outputs are advisory until verified. Reviewer is mechanically
read-only. Tester owns `npm run dev`. ADRs receive a clean-context Sol adversary.

<!-- qtim:track:dev:start -->
## Dev track

Implement → test → independent review. Blocking browser evidence is configured in
`.codex/screenshots-gate.json`.
<!-- qtim:track:dev:end -->

<!-- qtim:track:pm:start -->
## PM track

Производная self-contained сводка канона `reference/feature-pipeline.md`: fast
`feature-brief.md` или full PRD/decomposition/estimate/plan, vertical slices with DRI.
Stage 6 сначала пишет handoff artifacts, затем строку в `memory/decisions.md` записывает
последним completion marker. Approved artifact без marker означает interrupted handoff и resume Stage 6.
<!-- qtim:track:pm:end -->

## Memory layout

См. `memory/MEMORY.md`.
