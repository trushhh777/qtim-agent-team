# Mission receipt contract

Worker output недоверен до source/artifact/git проверки coordinator.

## Writer preflight

```text
WRITER PREFLIGHT READY
mission/node/marker/attempt:
HEAD detached and equals expectedBase: true
clean including untracked: true
shared refs unchanged: true
edits or commit made: false
```

Это не write authorization. Coordinator reconciles все targets wave, независимо
проверяет no-edit state, снимает Git/admin/submodule baselines и только exact
follow-up по marker + attempt разрешает edits. Без callable follow-up writer mode
`unavailable`; любой edit до authorization даёт `BLOCKED`.

## Worker receipt

```text
WORKER RECEIPT
mission/node:
marker:
attempt:
status: SUCCEEDED | BLOCKED | FAILED
execution used: direct | lazy
write policy: read-only | isolated-worktree-writer
base revision:
expected base for this attempt:
coordinator write authorization marker/attempt:
changed files:
commit SHA: <writer only>
shared refs-before / refs-after:
coordinator ref-journal checkpoint id observed:
common git config unchanged: true | false
common git control files unchanged: true | false
read-only per-worktree git control unchanged: true | false
assigned Git admin identity unchanged: true | false
writer frozen per-worktree Git control unchanged: true | false
common worktree admin matches coordinator journal: true | false
writer index matches commit without unsafe flags: true | false
writer submodule state matches coordinator baseline: true | false
writer nested submodule controls match baseline: true | false
writer HEAD equals commit: true | false
writer HEAD detached: true | false
writer worktree clean including untracked: true | false
writer filesystem matches commit tree: true | false
writer regular content files are single-link: true | false
target scopes contained without symlink/junction: true | false
node gates green: true | false
artifacts:
claims:
  - claim:
    evidence: <repo-relative path:line, artifact field or git object>
dependency outputs consumed:
verification commands/results:
approved local roles: <none | allowlist>
local roles used: <none | role: responsibility + explicit writer/read-only policy + scopes -> output>
scope overlap: none | exact conflicts
product fork: false | true
local results checked by node lead:
open blockers:
escalation request:
handoff summary:
```

Требования:

- mission slug/id и node id прошли canonical lowercase ASCII kebab grammar,
  marker однозначно равен `qtim:<missionId>:<nodeId>`; marker/attempt/spec
  совпадают;
- git read-only node сохранила immutable snapshot: canonical expected revision
  разрешается как commit, exact `HEAD == expected revision`, tree diff пуст и
  status с untracked files чист; clean status без exact HEAD недостаточен;
  exact pre/post protected refs (кроме runtime-owned ephemeral
  `refs/codex/*`), raw filesystem type/mode/device/inode/link-count/bytes,
  local common-config и common-control
  (`config`, `packed-refs`, `info/*`, alternates/shallow, hooks content/type/mode
  и real identity roots `objects/refs/logs/info/hooks/modules`) snapshots
  плюс root `.git` marker, resolved git-dir/common-dir и per-worktree Git admin
  (`HEAD`, raw index, config.worktree,
  sparse-checkout, operation heads/log) совпадают с учётом только exact
  coordinator-journaled state checkpoint текущей mission. Verification reads
  используют `GIT_OPTIONAL_LOCKS=0`. Common `.git/worktrees/*` registry frozen;
  journal разрешает только exact новые App entries wave. Отдельный registry
  transition journal разрешает только canonical current-mission file с exact
  before/after fingerprint и final-read owner/host/generation; соседние runtime
  paths не маскируются. Non-git target
  предъявляет эквивалентный
  immutable hash/no-change proof;
- writer возвращает один non-merge commit, единственный parent которого равен
  per-attempt `expectedBase`; mission base остаётся ancestor; writer paths и
  scopes проходят тот же canonical safe repo-relative parser, затем containment;
  App worktree остаётся detached от `expectedBase` до commit и не создаёт/двигает
  shared writer ref. Отдельный coordinator-owned journal, а не worker receipt,
  может разрешить только exact state checkpoint текущей mission. State delete/recreate,
  add/delete/move integration/foreign refs запрещены; integration frozen в
  writer wave;
- writer coordinator baseline отдельно от receipt фиксирует exact `.git`
  identity, common config/control, per-worktree control, assigned wave entries и
  submodule topology. Только canonical `HEAD`/index и optional reflog/
  commit-message paths assigned entries могут измениться; `config.worktree`,
  sparse/operation metadata, foreign/extra admin files frozen. Admin files real,
  non-executable, single-link; index exact match commit без assume-unchanged,
  skip-worktree/unmerged flags. Initialized/uninitialized submodule state +
  nested admin identity/worktree control/common config/control/hooks/packed-refs
  неизменны, кроме явно авторизованного scoped transition;
- writer postconditions являются строгими booleans: detached `HEAD == commit`, clean
  status including untracked, filesystem соответствует commit tree с clean
  filters/submodules, каждый regular content file single-link, target scopes
  contained без symlink/junction, common Git config/control неизменны, node gates
  green;
- каждый существенный claim имеет provenance;
- dependency inputs совпадают с validated context pack;
- каждая lazy role уникальна, входит в Approved allowlist, имеет concrete
  responsibility, output, explicit `write_policy: writer | read-only` и проверку
  node lead; writer имеет непустые canonical `write_scopes`, read-only — ровно
  пустые `write_scopes: []` и явные canonical `read_scopes`; falsey scopes не
  пропускаются; scopes нормализуются до pairwise overlap check, поэтому
  aliases/traversal не обходят gate; raw backslashes, drive/UNC/RFC3986 schemes,
  ASCII/Unicode control, basic/extended glob, env/home, case-folded `.git`,
  Windows reserved и option-like forms запрещены; NFC/case-fold aliases
  считаются overlap. Coordinator передаёт exact role
  responsibility/output/policy/read+write scopes отдельно от receipt;
  self-reported allowlist не авторизует роль;
- local agents не создали descendants; feedback loop, новая роль вне allowlist,
  scope overlap или product fork возвращены как `ESCALATION_REQUEST`;
- любой такой escalation receipt имеет `status: BLOCKED`; любой
  `ESCALATION_REQUEST` также требует `BLOCKED` даже при unknown reason;
  `SUCCEEDED` с escalation отклоняется, а `BLOCKED` никогда не разблокирует
  `succeeded -> validated`;
- `BLOCKED`/`FAILED` не маскируются пустым summary.

Raw filesystem proof включает type/full mode/device/inode/link count/bytes и
имеет hard limit 50 000 entries / 512 MiB regular-file bytes; FIFO/socket/device
или превышение бюджета блокирует validation fail-closed.

## Coordinator validation

1. Сверить runtime thread с project, marker и attempt.
2. Проверить claims и artifacts по source.
3. Для read-only — подтвердить immutable target, current-mission registry journal
   и отсутствие foreign common-worktree/runtime drift с non-refreshing Git reads.
4. Для writer — проверить существование commit, exact `expectedBase` parent,
   mission-base ancestry, ровно один non-merge commit, changed paths/scope,
   strict postconditions и gates. Pre/post App worktree должен оставаться
   detached; shared refs не получают attempt branch.
5. Сопоставить consumed dependencies с validated receipts.
6. Для lazy — проверить necessity и Approved allowlist ролей, pairwise disjoint
   write scopes, outputs, отсутствие descendants и обязательный
   `ESCALATION_REQUEST` для feedback loop/product fork.
7. Отклонить out-of-scope claims/changes и записать причину.
8. Записать в `receipts.md` только подтверждённое summary.
9. Перевести `succeeded -> validated` только после всех проверок.

## Dependency context pack

```text
DEPENDENCY CONTEXT PACK
mission / from node / validated outcome:
source, artifact and integrated commit ids:
contracts:
invariants:
unresolved blockers:
forbidden interpretations:
downstream acceptance criteria:
validated at:
```

Full transcript, tool chatter и непроверенные hypotheses не передаются.

## Integration receipt

```text
INTEGRATION RECEIPT
mission/node:
validated commit:
integration target / previous revision / transaction revision / resulting revision:
method: detached transaction-worktree cherry-pick (no shared transaction ref) + clean exact Approved target branch + exclusive lock + full-OID ancestry + atomic exact-target-ref CAS + exact-final clean tree
affected gate commands/results:
promotion lock / symbolic target identity / exact-old target check / final target-ref+HEAD check:
scope rechecked:
status: INTEGRATED | CONFLICT | REJECTED
```

`handoff_thread` не заменяет DAG integration. Conflict не разрешается force
overwrite; отдельная conflict node требует обновлённого Approved graph. `REJECTED`
после red affected gate сохраняет прежний Approved revision: transaction commit
не продвигается. Portable evidence обновляется scoped checkpoint commits в
отдельной state worktree; final bundle доставляется тем же fenced promotion.
После exact delivery следующий state checkpoint обязан записать `Done`,
увеличенный `stateSequence` и `deliveredEvidenceRevision`; до него durable status
остаётся `Verifying`. Delivery revision должна быть canonical 40/64-hex object
id, совпадать с независимо перечитанным promoted HEAD; обе revisions
разрешаются Git как commits.

## Mission verification receipt

```text
MISSION VERIFICATION
mission:
integrated/source revision:
verdict: APPROVED | NOT APPROVED
criteria checked:
dependency claims checked:
confirmed findings:
rejected claims:
missing evidence:
verification commands/results:
```

Verdict — literal exact full-line record, не substring: indentation, tabs, лишние
пробелы и suffix вроде `APPROVED-ish` запрещены; после colon ровно один ASCII
space. Последняя exact запись определяет итог. Coordinator проверяет каждый
finding. `NOT APPROVED` создаёт bounded fix node
только в пределах Approved budget. `Done` допустим лишь после подтверждённого
`APPROVED`, записанного последним в `verification.md`, exact fenced delivery и
clean post-delivery checkpoint с совпавшим `deliveredEvidenceRevision`.
