# ADR-001: Portable mission state и coordinator-managed commit integration

**Date:** 2026-07-29
**Status:** Accepted
**Author(s):** qtim maintainers
**Deciders:** qtim maintainer после runtime smoke, финального `$qtim-grill` и
clean-context independent review

## Context

`$qtim-mission` координирует несколько видимых Codex App tasks, включая
параллельных writers. App handles зависят от host/runtime и не должны попадать в
portable Git history, тогда как spec, решения, receipts и verification должны
переживать новую coordinator-задачу. Writer results нужно собрать в один
проверяемый revision без shared checkout races и без предположения, что App
handoff является DAG merge.

**Key constraints:**

- peer tasks и worktrees создаёт только mission coordinator;
- dirty пользовательский checkout нельзя stash/commit автоматически;
- handles/cursors opaque и могут стать stale;
- writer output недоверен до проверки Git objects, scope и gates;
- integration должна быть последовательной, recoverable и fail-visible;
- CLI/IDE без peer tools получают single-task fallback.

## Options Considered

### Option 1: Split state + transactional cherry-pick/promotion

**Description:** Durable evidence живёт в `memory/missions/<slug>/` на отдельной
state branch/worktree, runtime handles — в gitignored `.codex/qtim-runtime/`.
Каждый подтверждённый transition получает монотонный scoped checkpoint commit до
следующего внешнего side effect. Каждый writer возвращает один bounded commit из
отдельного worktree. Coordinator cherry-pick-ит commit в disposable transaction
worktree, запускает affected gate и только затем под exclusive promotion lock
проверяет clean state, canonical full commit ids и ff-only ancestry, атомарно
проверяет exact symbolic attachment worktree к canonical Approved target ref,
атомарно выполняет exact-target-ref CAS, синхронизирует transaction tree и
проверяет exact-final target ref + HEAD + clean Approved branch.

**Pros:**

- portable решения отделены от machine-local handles;
- Git ancestry, changed paths и integration order механически проверяемы;
- conflict можно abort в transaction, red gate не сдвигает Approved HEAD;
- несколько writers не делят checkout.

**Cons:**

- coordinator обязан поддерживать два слоя state;
- coordinator обязан управлять transaction worktrees и owner generation;
- App worktree/base semantics нужно подтверждать smoke после runtime upgrades.

### Option 2: Native `handoff_thread` для всех writers

**Description:** После worker completion передавать task/git state coordinator
через App handoff control.

**Pros:**

- нативный App UX;
- меньше явных Git operations в happy path.

**Cons:**

- callable schema не доказывает topological merge нескольких независимых commits;
- сложнее проверить порядок, ancestry и поведение при конфликте;
- handoff переносит task state шире bounded commit contract.

**Why this was ruled out:** handoff остаётся recovery/UX primitive, но не является
доказанным DAG integration primitive.

### Option 3: Shared coordinator checkout

**Description:** Все peer writers меняют один local checkout, scopes разводятся
текстовым контрактом.

**Pros:**

- нет отдельной integration операции;
- минимальная настройка.

**Cons:**

- races и смешение незакоммиченных изменений;
- невозможно надёжно атрибутировать результат node;
- конфликт повреждает общий рабочий контекст пользователя.

**Why this was ruled out:** нарушает isolation и делает receipt непроверяемым.

## Decision

**We will хранить portable evidence в `memory/missions/<slug>/` на отдельной
clean state branch/worktree с монотонными scoped checkpoint commits, opaque
runtime hints и coordinator owner generation — в gitignored
`.codex/qtim-runtime/`, изолировать каждого git writer в отдельном App worktree и
интегрировать один проверенный commit на node через transaction-worktree
`git cherry-pick` → affected gate → canonical `ownership -> promotion` locks →
owner/generation re-read → exact-old check + ff-only ancestry + exact symbolic
Approved target identity → atomic
exact-target-ref CAS → exact-final target ref + HEAD + clean tree check в
topological order.**

Dirty integration/state worktree, partial state diff после crash или overlap в
portable state блокирует writer mode/resume до решения пользователя.
`handoff_thread` не используется как DAG merge. Red gate оставляет Approved
branch неизменной. Любой недоказанный owner/handle, generation, base, scope, gate
или conflict останавливает только зависимую операцию fail-visible. После final
`APPROVED` последний clean state checkpoint доставляется одним scoped evidence
bundle commit через тот же fenced promotion. После exact delivery следующий
монотонный state checkpoint фиксирует `Done`, новый `stateSequence` и
`deliveredEvidenceRevision`, проверенный как canonical 40/64-hex Git commit и
exact независимо перечитанный promoted HEAD. Crash между promotion и checkpoint оставляет
durable status `Verifying`; reconciliation сверяет promoted subtree/revision и
идемпотентно создаёт checkpoint либо блокирует mismatch.

Writer startup двухфазный: первая App-задача выполняет только no-edit preflight и
возвращает exact `WRITER PREFLIGHT READY`; coordinator reconciles всю wave,
снимает immutable filesystem/Git-admin baselines и только затем посылает exact
marker+attempt follow-up, разрешающий edits. Без callable follow-up writer mode
`unavailable`. Runtime registry и ownership/promotion locks имеют только
канонические derived paths под `.codex/qtim-runtime/`; portable/runtime roots
проходят component-wise lstat/realpath/same-filesystem containment без
symlink/junction.

## Consequences

### Positive Consequences

- portable mission можно аудировать независимо от конкретного host;
- commit receipt и integration receipt имеют проверяемые Git invariants;
- parallel writers не затрагивают пользовательский checkout;
- crash recovery читает последний clean committed checkpoint и не принимает
  частичную запись за durable transition;
- post-delivery crash window имеет идемпотентную reconciliation и не объявляет
  `Done` только по in-memory predicate;
- portable evidence не загрязняет clean integration checkout до final delivery;
- affected gate становится транзакционным: red не продвигает Approved branch;
- exact-old/final проверки под lock не позволяют принять чужой descendant как
  собственный transaction result;
- recovery классифицирует stale/orphan/ambiguous state вместо угадывания.

### Negative Consequences / Accepted Tradeoffs

- runtime registry не гарантирует cross-host resume;
- coordinator выполняет больше validation и Git operations;
- state/transaction worktrees, checkpoint sequence и fenced owner/promotion
  operations усложняют recovery;
- conflict требует обновлённого Approved graph и отдельной node;
- full App smoke остаётся обязательным release gate для каждой изменившейся
  callable surface.

### Risks

- будущая App версия может изменить worktree creation или handle reconciliation;
- worktree может исчезнуть до чтения commit;
- пользователь может вручную изменить integration branch/base между waves.

Решение пересматривается, если App предоставит атомарный, документированный и
проверяемый multi-commit DAG integration API.

## Implementation Notes

- root `.gitignore` содержит `.codex/qtim-runtime/`;
- registry хранит `threadId`, `hostId`, cursors и pending `clientThreadId` opaque;
- registry хранит exact coordinator thread/host и положительную generation;
  first-run parents создаются component-by-component с post-create containment,
  а initial registry публикуется под canonical ownership lock через exclusive
  temp + fsync + atomic no-clobber + parent fsync + final read; collision
  `ambiguous`, недоказанный host primitive `unavailable`;
  takeover использует exclusive adjacent ownership lock, повторно читает
  generation под lock и пишет через file
  `fsync + atomic replace + parent-directory fsync`, затем до снятия lock
  подтверждает exact regular single-link registry с new owner/host/generation;
  live owner или
  занятый/непроверяемый lock блокирует takeover;
- current-mission registry transition проверяется отдельным coordinator journal:
  exact canonical `<slug>.json`, before/after raw fingerprint, final-read
  coordinator/host/generation; sibling/foreign runtime paths остаются frozen;
- writer preflight обязан завершиться без edits/ref drift; coordinator снимает
  baselines всей wave до exact follow-up authorization. Baseline связывает raw
  tree, `.git` marker, resolved git-dir/common-dir, common controls,
  `.git/worktrees/*`, per-worktree admin/index, single-link content и submodule
  topology плюс nested config/control/hooks/packed-refs; raw traversal
  fail-closed отвергает junction и отдельно проверяется на Windows;
- portable evidence пишется только в clean state worktree на
  `codex/qtim-mission-state-<slug>`; каждый transition получает монотонный
  sequence и scoped commit только по `memory/missions/<slug>/` до следующего
  external side effect; partial uncommitted diff блокирует resume;
- direct peer tasks не получают model override; Approved lazy lead получает exact
  Sol/Ultra pair;
- per-attempt `expectedBase` фиксируется после integrated dependencies; writer
  проверяет exact HEAD до edits, а один non-merge commit обязан иметь этот parent;
- affected gate выполняется в transaction worktree до promotion; green разрешает
  fenced compare-and-swap только из clean integration worktree, для canonical
  full commit ids, под locks только `ownership -> promotion` с registry
  owner/generation re-read и повторной проверкой exact Approved symbolic
  target/old HEAD/ff-only ancestry, atomic
  exact-target-ref CAS, exact tree sync и exact final target ref + HEAD + clean
  status; detached/wrong-branch worktree отклоняется; post-CAS failure требует
  доказанного rollback target ref/tree,
  иначе состояние `ambiguous`; red сохраняет прежний Approved HEAD;
- конфликт abort-ится в transaction worktree, force overwrite запрещён;
- final verifier читает integrated revision в clean context; его `APPROVED`
  checkpoint доставляется одним final evidence bundle commit, после чего
  coordinator подтверждает delivery и только тогда пишет следующий durable
  `Done` checkpoint с exact `deliveredEvidenceRevision`.

## Review Date

После первого полного App smoke и при каждом изменении project/thread/worktree
schemas Codex App.

## Quality Checks

- [x] Контекст объясняет почему разделены portable/runtime state.
- [x] Рассмотрены три варианта и причины отказа.
- [x] Зафиксированы отрицательные последствия и invalidation triggers.
- [x] Self-play red team завершён:
      [deliberation-debate-red-teaming.md](deliberation-debate-red-teaming.md).
- [x] `$qtim-grill` exact skill выполнен в отдельной clean-context App task;
      первый adversarial run нашёл state checkpoint, promotion fencing,
      ownership-lock и activation gaps; решения внесены, финальный fresh-snapshot
      pass получен 2026-07-29.
- [x] Два clean-context Sol release review завершены с blocking findings;
      все подтверждённые findings внесены, отдельный финальный clean-context
      review вернул `PASS — APPROVED` 2026-07-29.
- [x] Исторический App read-only/lazy/two-writer/final-verifier/status/
      stale-resume smoke завершён:
      [app-smoke-receipt.md](app-smoke-receipt.md).
- [x] Полный repository validation suite, mission semantic fixtures,
      migration/golden checks, shell syntax и официальный `validate_plugin.py`
      зелёные на локальном финальном snapshot 2026-07-29.
- [x] Финальный App smoke подтверждает новый двухфазный
      `WRITER PREFLIGHT READY -> coordinator baseline -> exact follow-up`
      contract до bounded detached writer commit/receipt:
      [app-smoke-receipt.md](app-smoke-receipt.md).
- [x] Свежие `$qtim-grill` и clean-context Sol review на финальном snapshot
      возвращают PASS после внесённых lock/takeover/portable/submodule/
      hardlink/junction findings.

`adr-stress-test: PASS — qtim-grill + clean-context Sol adversaries завершили fail-first rounds; App READY→follow-up smoke passed; lock/takeover/portable/submodule/hardlink/junction findings incorporated; final fresh-snapshot qtim-grill PASS и independent review PASS/APPROVED получены 2026-07-29`
