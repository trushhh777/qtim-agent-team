# Red team: Mission runtime и Git integration

Дата: 2026-07-29
Статус: PASS — self-play и fail-first `$qtim-grill` завершены; findings
incorporated, App READY→follow-up smoke и два финальных fresh-snapshot
clean-context допуска пройдены
Proposal: [ADR-001](adr-001-mission-state-and-git-integration.md)

## Proposal Under Review

Выпустить в qtim 2.12 полный App-first `$qtim-mission`: portable evidence отдельно
от opaque runtime hints, isolated worktree на writer attempt, один проверенный
commit, transaction cherry-pick с affected gate до fenced
exact-old/ff-only/exact-final promotion, clean-context verifier и single-owner
fail-visible recovery.

Цель — несколько видимых Codex tasks с проверяемым общим результатом без daemon
или собственного scheduler runtime. Ошибка может смешать пользовательские правки,
интегрировать неверный commit, продолжить чужую task или объявить `Done` без
доказательств. Git-часть обратима через остановку до commit/integration; ошибочное
управление внешними tasks и опубликованный слабый contract дороже исправлять.

Decision maker — maintainer qtim. Двухфазный App smoke, финальный `$qtim-grill`
и independent fresh-snapshot release review пройдены; ADR принят.

## Adversarial Roles

1. **Git integrity engineer** — ищет смешение base, commits и чужих изменений.
2. **Runtime/SRE** — ломает asynchronous creation, handles, host и resume.
3. **Security/ownership reviewer** — проверяет authority, state leakage и
   неожиданные external actions.
4. **Node lead/user** — ищет runaway fan-out, неясный UX и ложный completion.
5. **Long-term maintainer** — проверяет migration drift и будущую смену App schema.

## Critiques

### Git integrity engineer

- App `create_thread` не принимает доказанный base SHA как отдельный параметр:
  worktree может открыться не на ожидаемом revision.
- Проверка лишь `missionBase is ancestor` пропускает лишние commits между base и
  worker commit.
- Downstream writer после upstream integration должен стартовать от нового
  integration HEAD, а не от исходного mission base.
- Portable receipts в том же checkout загрязнят integration worktree.
- Green cherry-pick с последующим red gate оставит неподтверждённый commit в
  Approved branch; conflict handling без abort оставит transaction в полусостоянии.

Стальная версия возражения: commit transport безопасен только при exact
per-attempt parent, scoped paths и воспроизводимом conflict abort.

### Runtime/SRE

- `clientThreadId` может не превратиться однозначно в usable `threadId`.
- Title similarity может связать coordinator с чужой task.
- После смены host или удаления worktree registry станет stale, хотя JSON всё ещё
  выглядит валидным.
- Wait overflow или повторное чтение без cursor может дублировать side effects.
- Новый coordinator может конкурировать с прежним scheduler/integrator без
  ownership generation.

Стальная версия: runtime registry должен оставаться hint, а не source of truth;
невозможность доказать live mapping обязана остановить operation.

### Security/ownership reviewer

- Opaque handles в Git раскроют machine-local state и позволят другой машине
  ошибочно использовать их.
- SessionStart advisory может незаметно превратиться в auto-resume/fan-out.
- `stop` или completion могут удалить/архивировать задачи без отдельного consent.
- Lazy node может расширить authority и создать peer tasks/третье поколение.
- Team-down может скопировать opaque handles в portable handoff.

Стальная версия: только coordinator пишет registry и управляет peer tasks;
advisory/status read-only, cleanup требует отдельного подтверждения.

### Node lead/user

- `SUCCEEDED` и красивый receipt могут быть приняты без проверки source.
- Несколько ролей в lazy node могут стать декоративным дорогим fan-out.
- Verifier finding может быть ложным, а fix loop — бесконечным.
- Dirty checkout блокирует mission, но auto-stash ради удобства уничтожит
  пользовательское понимание состояния.

Стальная версия: каждое состояние после worker output подтверждает coordinator;
budgets конечны, findings source-checked, dirty state возвращается пользователю.

### Long-term maintainer

- Setup, update, doctor, README и golden могут описывать разные поколения mission.
- Будущая App schema изменит worktree/handle semantics без compile-time ошибки.
- Handoff API может выглядеть удобнее и постепенно стать неявным merge path.

Стальная версия: semantic validators должны проверять общий contract, а runtime
compatibility и App smoke — повторяться после schema upgrades.

## Risk Register

Оценки — до указанных mitigation.

| # | Риск | S | L | Score | Категория |
|---|---|---:|---:|---:|---|
| 1 | Writer commit не от exact revision, особенно после upstream integration | 5 | 4 | 20 | Showstopper |
| 2 | Dirty/shared checkout смешивает пользовательские и mission changes | 5 | 3 | 15 | Showstopper |
| 3 | Stale/ambiguous handle управляет неверной peer task | 5 | 3 | 15 | Showstopper |
| 4 | Conflict оставляет coordinator в незавершённом cherry-pick | 4 | 3 | 12 | High |
| 5 | SessionStart/RECOMMEND создаёт tasks без явной authorization | 5 | 2 | 10 | High |
| 6 | Lazy node создаёт descendants или скрытый feedback loop | 4 | 2 | 8 | Monitor |
| 7 | Worker/verifier output принят без source check | 4 | 3 | 12 | High |
| 8 | Generated-state migration не защищает runtime registry | 3 | 3 | 9 | Monitor |
| 9 | App schema изменилась, а Markdown contract остался прежним | 4 | 3 | 12 | High |
| 10 | Red affected gate оставляет commit в Approved branch | 5 | 3 | 15 | Showstopper |
| 11 | Два coordinator одновременно планируют/integrate | 5 | 2 | 10 | High |

## Mitigations And Revisions

| Риск | Mitigation | Owner | Gate |
|---|---|---|---|
| 1 | Coordinator фиксирует per-attempt `expectedBase`; worker проверяет exact HEAD до edits; commit имеет единственного exact parent | mission coordinator | semantic + temp-git fixture + App smoke |
| 2 | Portable state получает монотонные scoped checkpoint commits в отдельной clean state branch/worktree; partial crash diff блокирует resume; writer всегда worktree; auto-stash/shared writers запрещены | mission coordinator | preflight + checkpoint/crash temp-git fixture |
| 3 | Exact project + marker + attempt + thread/host; single owner generation; `pending/stale/orphan/ambiguous/unavailable` fail-visible | mission coordinator | recovery/ownership fixtures + App smoke |
| 4 | Transaction cherry-pick, affected gate до promotion, обязательный abort; conflict node только после обновления Approved graph | mission coordinator | temp-git conflict fixture |
| 5 | Implicit-loaded fail-closed `AUTO-START/PREVIEW/RECOMMEND` classifier; referential approval требует preceding preview; SessionStart только bounded text advisory | hooks/testing | activation + hook runtime fixtures |
| 6 | Approved mission-child mode, minimum-sufficient responsibilities, один aggregated receipt, `ESCALATION_REQUEST` | node lead + coordinator | lazy semantic fixture + App smoke |
| 7 | `succeeded != validated`; coordinator проверяет claims/commit/findings; `Done` только после final APPROVED, fenced delivery и durable checkpoint с delivered revision | coordinator | state fixtures + clean verifier smoke |
| 8 | Exact `.codex/qtim-runtime/` ignore в setup/update/golden/doctor; tracked runtime оставляет migration pending | maintainer | golden + migration validation |
| 9 | Runtime compatibility probe после Codex upgrade; недоказанная capability блокирует только operation | maintainer | release App smoke |
| 10 | Fenced promotion только после green transaction gate: lock order `ownership -> promotion`, generation re-read под обоими, exact-old, `--ff-only`, exact-final; red сохраняет Approved HEAD | mission coordinator | lock/drift/generation-race/red-gate temp-git + App smoke |
| 11 | Takeover только после explicit resume, non-running прежнего owner и exclusive ownership lock; generation повторно читается, registry пишется через file `fsync + atomic replace + parent-directory fsync`, exact final read остаётся под lock | mission coordinator | competing-lock/ownership/final-read fixtures + recovery smoke |

Showstoppers закрыты в contract и локальных fixtures, включая exact Git/common
admin identity, nested submodule controls, single-link writer content, frozen
foreign worktree metadata, canonical registry/lock paths, ownership-before-
promotion generation fencing, component-wise portable/runtime init и real
Windows junction checks. Fresh App smoke доказал полный
`READY -> coordinator baseline -> follow-up -> bounded receipt` цикл.

## Rebuttals

- **«Использовать handoff и убрать cherry-pick».** Отклонено: schema существования
  handoff не доказывает multi-commit DAG merge/order/conflict semantics.
- **«Доверять title для recovery».** Отклонено: title изменяем и не уникален;
  marker/project/attempt обязательны.
- **«Запретить writers до следующего релиза».** Отклонено как продуктовый
  компромисс после решения выпускать весь plan одним релизом; риск снижен exact
  base/commit/gate contract и внешним smoke gate.
- **«Автоматически stash dirty state».** Отклонено: скрывает пользовательские
  изменения и меняет scope authority.

## Revised Proposal

Исходный split-state + cherry-pick сохраняется, но integration становится
транзакционной:

1. root writer получает mission base;
2. downstream writer после integrated dependencies получает текущий integration
   HEAD как immutable per-attempt `expectedBase`;
3. worker до edits подтверждает exact HEAD;
4. accepted commit — ровно один non-merge commit с exact parent;
5. portable evidence checkpoint-ится монотонными scoped commits в отдельной
   clean state branch/worktree; partial crash diff блокирует resume;
6. cherry-pick и affected gate выполняются в disposable transaction worktree;
   только green gate разрешает fenced promotion под exclusive lock с exact-old,
   ff-only и exact-final checks;
7. conflict всегда abort-ится, red gate сохраняет прежний Approved HEAD;
8. final `APPROVED` checkpoint доставляется одним scoped evidence bundle commit;
   после подтверждённой delivery отдельный монотонный checkpoint фиксирует
   `Done` и exact canonical 40/64-hex commit `deliveredEvidenceRevision`, равный
   независимо перечитанному promoted HEAD; crash-window reconciliation
   идемпотентна;
9. resume требует single owner generation и ownership lock; live/unverifiable
   прежний coordinator блокирует takeover;
10. writer App task сначала выполняет no-edit preflight; coordinator reconciles
    всю wave и снимает baselines, затем exact marker+attempt follow-up разрешает
    edits; без follow-up writer mode `unavailable`;
11. promotion держит locks `ownership -> promotion`, перечитывает generation под
    обоими и не допускает параллельный takeover до CAS;
12. App smoke и повторный independent review блокируют release, а не runtime
    fallback.

## Recommendation

**PROCEED TO RELEASE.** Fresh двухфазный App smoke пройден; последние
grill/reviewer rounds нашли promotion-generation, takeover final-read, portable
first-run, nested submodule, writer hardlink и Windows junction gaps, которые
внесены в финальный snapshot. Полный repository suite, Windows junction CI
contract и официальный plugin validator зелёные. Повторный `$qtim-grill` и новый
clean-context independent release review вернули `PASS`; runtime contract после
их допуска не менялся.

Первый App `$qtim-grill` и два clean-context release review уже выполнили
fail-first роль: state durability, promotion/ownership fencing, activation,
terminal verifier, mission-child escalation, Git admin/registry/lock containment
и двухфазный startup были усилены по их findings. Исторические `BLOCKED`
verdicts сохранены как fail-first evidence; отдельные новые проходы по
fresh-snapshot дали финальные `PASS`.
