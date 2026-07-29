# Mission state schema

Portable Markdown хранит решения и проверенные результаты. Machine-local JSON
хранит только last-known opaque runtime handles и никогда не доказывает live state.

До формирования любого path/ref/marker `slug == missionId`, mission/node ids
обязаны пройти grammar lowercase ASCII kebab
<code>[a-z0-9]&#40;[a-z0-9-]*[a-z0-9]&#41;?</code> длиной 1–64.
Separators, colon, dot/control,
option forms и aliases запрещены; node ids и markers
`qtim:<missionId>:<nodeId>` уникальны. State ref точно выводится как
`refs/heads/codex/qtim-mission-state-<slug>`, integration target — отдельный
canonical `refs/heads/*`; оба проверяются `git check-ref-format`. Integration
target не занимает и не D/F-conflict-ит с reserved state namespace. Writer App
worktrees detached и не получают shared attempt refs.

## Portable evidence

```text
memory/missions/<slug>/
├─ mission.md
├─ receipts.md
├─ decisions.md
└─ verification.md
```

`mission.md` содержит:

- mission id/title, source artifact и repository identity без absolute path;
- source/base revision, Approved integration target и global gates;
- immutable raw snapshot digest, exact current-mission registry fingerprint и
  common-worktree admin baseline needed for fail-closed resume; если baseline
  потерян, receipt validation блокируется, а не реконструируется из worker output;
- acceptance criteria, nodes, dependencies и total exact edge-contract map:
  все и только DAG edges, значение `evidence | integrated`;
- минимум две content nodes и отдельный reserved `terminalVerifier`, чей
  `dependsOn` в точности равен множеству всех required outcomes и который не
  участвует в обычных scheduler waves;
- read/write scope, `execution: direct | lazy`, Approved lazy profile/roles;
- expected receipts, integration order, retry/fix budgets, stop conditions;
- status `Draft | Approved | Running | Needs input | Blocked | Verifying | Done |
  Stopped`;
- append-only transition history с timestamp/reason.

`receipts.md` содержит coordinator-validated summaries и integrated commit ids.
`decisions.md` хранит mission-local развилки. `verification.md` содержит gates,
confirmed/rejected findings и последний completion marker `APPROVED`.

Для git writer mission portable path живёт в отдельной state branch/worktree
`codex/qtim-mission-state-<slug>`. State ref создаётся до fan-out, затем никогда
не удаляется/пересоздаётся. Каждый подтверждённый transition имеет
монотонный sequence и scoped checkpoint commit только по этому path. Crash
recovery доверяет последнему clean commit; незакоммиченный partial diff блокирует
resume. После final `APPROVED` последний checkpoint доставляется в Approved
integration branch одним scoped bundle commit через detached transaction
worktree без shared transaction ref, затем fenced
exact-old promotion. Только после подтверждения exact delivered subtree state
branch получает следующий монотонный checkpoint с `status: Done`,
`stateSequence: n+1` и `deliveredEvidenceRevision: <exact promoted SHA>`.
`deliveredEvidenceRevision` обязана быть canonical 40/64-hex Git object id,
совпасть с независимо перечитанным promoted HEAD, причём обе revisions должны
разрешиться как commits; пустая, abbreviated, syntactically invalid или
unresolved revision блокирует transition.
Промежуток после promotion до этого commit остаётся durable `Verifying`;
`resume` сверяет revision/subtree и либо идемпотентно создаёт Done checkpoint,
либо блокирует mismatch. Этот terminal checkpoint не доставляется повторно:
authoritative mission state остаётся на state branch, а Approved branch хранит
неизменный exact APPROVED evidence bundle.

## Runtime registry

`.codex/qtim-runtime/missions/<slug>.json`:

```json
{
  "schemaVersion": 1,
  "missionId": "example",
  "status": "running",
  "projectId": "opaque",
  "baseRevision": "git-sha",
  "integrationTarget": "codex/qtim-mission-example",
  "integrationWorktreeTarget": "opaque",
  "stateTarget": "codex/qtim-mission-state-example",
  "stateWorktreeTarget": "opaque",
  "stateSequence": 4,
  "ownership": {
    "coordinatorThreadId": "opaque",
    "hostId": "opaque",
    "generation": 1,
    "acquiredAt": "RFC3339"
  },
  "nodes": {
    "a": {
      "status": "running",
      "executionMode": "lazy",
      "threadId": "opaque",
      "hostId": "opaque",
      "waitCursor": "opaque",
      "clientThreadId": null,
      "attempt": 1,
      "expectedBase": "git-sha",
      "worktreeTarget": "opaque"
    }
  },
  "refJournal": {
    "sequence": 7,
    "authorizedTransitions": {
      "refs/heads/codex/qtim-mission-state-example": {
        "old": "full-git-sha",
        "new": "full-git-sha"
      }
    }
  },
  "updatedAt": "RFC3339"
}
```

Правила:

- ids, hosts, cursors и worktree targets opaque;
- `clientThreadId` — только pending creation handle, не usable `threadId`;
- coordinator — единственный writer registry; перед fan-out/integration он
  повторно читает ownership и требует exact owner + generation;
- до registry create/takeover каждый component `.codex/qtim-runtime/` проходит
  lstat/realpath containment: только real non-symlink/non-junction directories
  внутри exact project root. Registry, adjacent temp и ownership lock находятся
  на том же filesystem (`same filesystem`); unsafe path даёт `unavailable` без external write.
  Portable `memory/missions/<slug>/` в state worktree проходит тот же guard;
- first-run parents создаются от exact root по одному component с revalidation
  после exclusive create или `already exists`; unverified recursive `mkdir -p`
  запрещён. Первый registry под canonical ownership lock записывается в
  exclusive adjacent temp, `fsync`-ится и публикуется atomic no-clobber
  primitive, затем fsync parent и exact final read. Existing registry/temp
  collision = `ambiguous`; если host не доказывает no-clobber, init
  `unavailable`;
- canonical adjacent paths строго равны `<slug>.json`,
  `<slug>.ownership.lock`, `<slug>.promotion.lock`. Promotion lock bind-ит owner
  token + generation + integration target; разные caller-chosen locks запрещены;
- takeover другого coordinator возможен только после явного `resume`, доказанного
  non-running прежнего owner, exclusive adjacent ownership lock, повторного чтения
  generation под lock и file
  `fsync + atomic replace + parent-directory fsync` `generation: n -> n+1`.
  До снятия lock final read подтверждает exact regular single-link registry,
  mission/new owner/host и новую generation;
- transition пишется после подтверждённого tool/git result;
- read-only raw proof разрешает изменение только этого exact canonical registry
  file по coordinator transition journal: before/after type-mode-topology-bytes
  fingerprint + owner thread/host/generation. Final bytes повторно читаются и
  JSON ownership сверяется; parent directories, sibling/foreign runtime entries
  не исключаются из snapshot;
- `refJournal` coordinator-owned и не выводится из worker receipt. Он разрешает
  только exact state checkpoint текущей mission; state delete/recreate и
  integration/foreign moves запрещены,
  integration ref frozen на время writer wave;
- fenced promotion получает canonical locks только в порядке
  `ownership -> promotion`, затем перечитывает owner/generation под обоими locks;
  takeover race блокирует CAS без ref move;
- `expectedBase` фиксируется coordinator до создания writer attempt: mission base
  для root writer или verified integration HEAD после code dependencies;
- portable evidence пишется/коммитится только в clean state worktree и не влияет
  на `integrationTarget`/content `expectedBase` до final bundle delivery;
- registry gitignored, не содержит portable решений и не коммитится;
- повреждение/потеря registry не разрешает конструировать ids;
- если ignore ownership не определена, registry не создаётся, cross-session resume
  честно `unavailable`.

## Node state machine

```text
pending -> ready -> creating -> running
creating -> preflight-ready             # writer, no edits
preflight-ready -> running              # exact coordinator follow-up
running -> needs_input | failed | succeeded
succeeded -> validated
validated -> integrated        # writer
validated -> verified          # read-only
integrated -> verified         # writer after final gate
```

Служебные/терминальные: `blocked | cancelled | superseded`.

Writer registry в `preflight-ready` хранит no-edit READY evidence и reconciled
worktree target, но не write authorization. Только после capture всех wave
baselines coordinator записывает authorization marker/attempt и отправляет exact
follow-up; отсутствие callable follow-up делает writer mode `unavailable`.

Недопустимые переходы отклоняются. `succeeded != validated != integrated !=
verified`. Evidence edge требует `validated`; code edge — `integrated`. `Done`
существует только на mission level после final `APPROVED`, подтверждённой
portable-evidence delivery и clean checkpoint с совпавшим
`deliveredEvidenceRevision`. Stop не удаляет tasks, worktrees и portable evidence.

## Resume classification

- `live` — project + marker + attempt + thread/host подтверждены, base не drifted;
- `pending` — есть creation handle, usable thread ещё не подтверждён;
- `stale` — thread найден, но source/base/attempt не совпадает;
- `orphan` — portable node есть, runtime thread не найден;
- `ambiguous` — несколько exact-enough кандидатов;
- `unavailable` — surface/host/registry не позволяет проверку.
- `blocked` — state worktree dirty или checkpoint sequence не монотонен; до
  explicit reconciliation запрещены scheduler/integration side effects.

Post-delivery reconciliation отдельно fail-closed: `Verifying` + exact promoted
APPROVED subtree разрешает ровно один следующий Done checkpoint; уже совпавший
Done — no-op; пустой/invalid/unresolved или другой revision, subtree или status —
`blocked`.

Только `live` продолжается автоматически. Title similarity недостаточна. Respawn
создаёт новую attempt в пределах budget и помечает прежнюю `superseded`.

## Coordinator ownership

- `owned` — current coordinator thread/host и generation совпали;
- `takeover` — explicit resume, прежний owner подтверждён как non-running и
  generation атомарно увеличена под exclusive ownership lock;
- `ambiguous` — прежний owner ещё running или найдено несколько владельцев;
- `stale` — generation изменилась между проверкой и записью;
- `unavailable` — прежний owner/host или atomic replace нельзя проверить.

До `owned | takeover` запрещены task creation, follow-up, registry transitions и
Git promotion. После takeover coordinator повторно читает registry; каждый
последующий side effect требует ту же generation. Занятый или непроверяемый
ownership lock не удаляется best-effort и даёт `ambiguous | unavailable`.

## Mission recovery invariants

- `status` read-only;
- `resume` не меняет integration target/base без нового approval;
- `resume` не допускает двух scheduler/integrator owners;
- `stop` запрещает новый fan-out и сохраняет last-known state;
- SessionStart bounded: сканирует максимум 50 portable candidates, показывает
  максимум 5 и `+more`, ничего не запускает. Для portable `Verifying` он читает
  exact derived state ref и подавляет advisory, если authoritative checkpoint
  уже `Done`;
- archive/delete/cleanup не входят в status/resume/stop.
