# App smoke receipt: qtim mission 2.12

Дата: 2026-07-29
Среда: Codex desktop App, local git project
Mission marker: `qtim:qtim-mission-release-smoke-20260728:*`
Политика cleanup: задачи оставлены видимыми; archive/delete не выполнялись

Receipt намеренно не хранит opaque `threadId`, `hostId`, cursors, абсолютные
App-worktree paths или `clientThreadId`. Их exact mapping проверялся через
callable App tools и оставался только runtime evidence.

## Capability и reconciliation

- callable `create_thread`, `list_threads`, `wait_threads`, `read_thread` и
  rename surface подтверждены;
- asynchronous worktree creation возвращала pending `clientThreadId`, после чего
  exact project + mission marker + node + attempt однозначно reconciled usable
  `threadId`; pending id не передавался в calls для `threadId`;
- одинаковый title у повторных attempts оказался недостаточен для identity:
  coordinator сверял exact marker, attempt, project и source snapshot;
- status использовал bounded list/read snapshot и не создавал новых tasks;
- resume старой попытки честно обнаружил stale isolated snapshot; coordinator не
  угадывал handle и создал новую attempt в пределах budget;
- callable stop control на этой surface не был обнаружен. Результат записан как
  `unavailable`: stop не симулировался, tasks не удалялись и не архивировались.

## Read-only contract attempts

1. Первая attempt успешно проверила основной contract, но последующий resume
   корректно вернул `NOT APPROVED`: её isolated snapshot не содержал более новых
   coordinator fixes.
2. Вторая attempt вернула `FAILED`: отсутствовали negative fixtures для exact
   marker/base recovery.
3. Третья attempt на новом snapshot вернула `SUCCEEDED` после добавления fixtures.

Это подтверждает fail-visible retry: failure/stale result не был переименован в
validated success.

## Lazy node

1. Первая attempt вернула `BLOCKED / ESCALATION_REQUEST`, потому что prompt не
   содержал exact Approved lead profile, хотя tool-level параметры были заданы.
2. Вторая attempt получила явный `gpt-5.6-sol` + `ultra`, вызвала ровно один
   local `$qtim-team-lazy` level с ролями architect + testing, вернула один
   aggregated receipt и не создала descendants.
3. До/после read-only hashes совпали.

## Writer DAG и integration

Зафиксированный mission base:
`47a4d78c50f18d2d1097db68d2a198dbc7b66ec0`.

| Этап | Проверенное evidence |
|---|---|
| Writer A | один non-merge commit `30cd775cbb579daf1558299bd20be84c1e9a69d3`; единственный parent = mission base; изменён только `docs/.qtim-mission-smoke/node-writer-a.md` |
| Integration A | transaction/integration revision `2702f9daca64f5fabccd32e1f2cb3c7f4462825e`; affected gate green |
| Writer B | один non-merge commit `c206fc143bac0bc50715b4736657442208cc976f`; единственный parent = integrated A; изменён только `docs/.qtim-mission-smoke/node-writer-b.md` |
| Integration B | transaction/Approved revision `a47925d34d814bdb42a1400d6f78b9264726b735`; affected gate green; promotion выполнен `--ff-only` |
| Final verifier | отдельная clean-context read-only task вернула `APPROVED`; base → A → B содержит ровно два scoped non-merge content commits, B действительно зависит от integrated A |

Writer commits и smoke integration branch не переносились в release branch: это
изолированный runtime probe. Red gate, conflict abort, monotonic three-checkpoint
APPROVED chain плюс четвёртый post-delivery Done checkpoint, dirty-crash
`blocked` с нулевыми side effects, competing
ownership/promotion locks, exact-old drift rejection и exact full-subtree final
portable evidence delivery с deletion/APPROVED/durable-Done reconciliation gates дополнительно
воспроизводятся repository-local temp-git fixtures в
`.github/scripts/check_missions.py`.

## Финальный detached/ref timing probe

На итоговом hardened snapshot повторно вызван App `create_thread` с
`target.kind=worktree` и preflight-only prompt без edits/ref operations:

- create вернул только pending `clientThreadId`, usable `threadId` не
  подставлялся вручную;
- `list_threads` однозначно reconciled visible task по exact marker/project/
  attempt и показал созданный App worktree;
- независимый `git worktree list --porcelain` показал exact mission base и
  `detached`; `for-each-ref` до/после не показал нового shared writer ref;
- task завершилась `systemError` до model output из-за исчерпанного runtime usage
  quota, поэтому probe не объявлен успешным writer receipt и повторно не
  запускался обходным способом;
- systemError оставлен fail-visible, задача не архивирована. Предыдущий
  two-writer smoke выше остаётся evidence commit/parent/scope/integration, а
  final probe отдельно подтверждает новый App creation invariant:
  `detached expectedBase`, zero shared attempt refs.

После этого probe contract усилен до обязательного двухфазного writer startup:
no-edit `WRITER PREFLIGHT READY`, coordinator baseline всей wave и exact
follow-up authorization. Из-за указанного quota `systemError` полный live
READY→follow-up цикл в этом запуске не подтверждён и не объявляется PASS; он
покрыт fail-closed semantic fixtures. Поэтому следующий runtime smoke должен был
проверить его первым; результат записан ниже.

## Fresh двухфазный release smoke 2026-07-29

После восстановления runtime capability создана новая видимая worktree-задача с
marker `qtim:mission-release-2-12-final:writer-preflight`, attempt `1` и exact
base `47a4d78c50f18d2d1097db68d2a198dbc7b66ec0`:

1. Initial prompt был строго preflight-only и запрещал edits/commit/ref
   operations. Задача вернула exact `WRITER PREFLIGHT READY` с совпавшими
   marker/attempt/HEAD, `detached=true`, `clean=true`.
2. Coordinator reconciled единственный target wave и независимо снял baseline:
   exact `.git` marker fingerprint, git-dir/common-dir, protected refs и raw
   worktree hashes. Shared protected refs совпали с preflight snapshot.
3. Только после baseline был отправлен отдельный exact marker+attempt follow-up.
   Он разрешил один файл
   `docs/.qtim-mission-smoke/final-two-phase.md` и один commit с отключёнными
   repository hooks.
4. Writer вернул canonical commit
   `4388538c2031349a397d2d80fbcad590edb362d0`; coordinator независимо подтвердил:
   sole parent равен exact base, changed path ровно один, content exact, HEAD
   detached и равен commit, status clean including untracked, `.git` marker
   fingerprint неизменен, ни один protected/shared ref не содержит commit.
5. Задача осталась видимой; archive/delete не выполнялись.

Этот fresh trace закрывает ранее незавершённый live
`READY -> coordinator baseline -> exact follow-up -> bounded writer receipt`
release gate. Smoke commit не переносится в release branch.

Именно поэтому 2.12 не конструирует branch name для writer. Shared refs frozen
на writer wave; единственное допустимое исключение — exact state checkpoint из
coordinator-owned journal, переданного validator отдельно от worker receipt.

## Итог

- App read-only, lazy, two-writer dependency, final verifier, status и stale
  resume paths подтверждены;
- `clientThreadId -> threadId` reconciliation подтверждён;
- App worktree creation подтверждён как detached без shared writer ref; финальная
  model phase была fail-visible `systemError`, а не ложный PASS;
- новый двухфазный READY→baseline→follow-up contract подтверждён fresh App smoke
  до bounded detached writer commit/receipt;
- неподдерживаемый stop остался fail-visible `unavailable`;
- ни одна mission/review task не была скрыта автоматическим archive;
- App smoke не заменяет semantic fixtures, `$qtim-grill` и независимый release
  review; все четыре gate обязательны перед публикацией.
