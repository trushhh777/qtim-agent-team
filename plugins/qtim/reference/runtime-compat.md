# Runtime compatibility contract

Последняя сверка: **2026-07-28**, `codex-cli 0.144.1`.

Этот файл отделяет подтверждённые возможности Codex от проектных допущений qtim. После
обновления Codex его проверяет `$qtim-doctor`; догадка о runtime не превращается в скрытый
инвариант generated state.

## Подтверждено runtime и документацией

- `AGENTS.md` загружается Codex до начала работы. Поэтому setup пишет компактный
  самодостаточный qtim-контракт между `qtim:contract:*` markers, а подробности оставляет в
  `.codex/team-charter.md` и `memory/`.
- Project custom agents читаются из `.codex/agents/*.toml`; `sandbox_mode = "read-only"`
  механически ограничивает reviewer.
- Plugin hooks обнаруживаются через `hooks/hooks.json`; `$PLUGIN_ROOT` доступен командам.
- `SubagentStop` с exit `2` продолжает agent, а `stop_hook_active` позволяет не зациклить
  повторный stop. Exit `0` может вернуть JSON `systemMessage`.
- Project `PostToolUse` использует `hookSpecificOutput.additionalContext`, а не plain stdout.
- Codex App поддерживает отдельные chats внутри local project; worktrees доступны
  только desktop App и изолируют git checkouts. Официальные границы:
  [Projects and chats](https://learn.chatgpt.com/docs/projects),
  [Worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees),
  [Codex App Server](https://learn.chatgpt.com/docs/app-server).

## Cross-dialog mission: App probe 2026-07-28

Проверка callable schemas в текущей Codex App задаче подтвердила:

- `list_projects` возвращает opaque `projectId` и признак git repository;
- `create_thread` создаёт peer task в project `local | worktree`; для direct task
  model/thinking нужно опускать, пока пользователь явно не выбрал override;
- готовая задача возвращает opaque `threadId` + `hostId`, а асинхронный worktree
  setup может временно вернуть только `clientThreadId`;
- `clientThreadId` нельзя передавать в `wait_threads`, `read_thread` или другие
  calls, ожидающие `threadId`;
- `wait_threads` принимает максимум восемь targets и cursor `afterCursor`;
- `read_thread`, `list_threads` и `set_thread_title` позволяют проверить bounded
  result, восстановить exact marker/project mapping и дать видимый title;
- `handoff_thread` переносит task/git state, но не является проверяемым
  topological merge primitive для нескольких commits;
- archive controls существуют, но mission автоматически их не вызывает.

Это evidence конкретной App surface, а не универсальная гарантия для CLI/IDE или
будущей версии. `$qtim-mission` каждый раз делает tool discovery и при отсутствии
peer tools предлагает честный single-task `$qtim-team-up` fallback.

Текущая `create_thread` schema не exposes sandbox override. Git read-only nodes
используют resolved current project `target.kind=local` без App-created branch,
prompt contract + immutable snapshot evidence,
которое coordinator проверяет через bounded `read_thread(includeOutputs=true)`:
canonical expected revision разрешается как commit, exact `HEAD` не изменился,
tree diff пуст, `git status --short --untracked-files=all` чист и raw filesystem
type/mode/device/inode/link-count/bytes fingerprint exact совпал. Все verification
Git reads идут с `GIT_OPTIONAL_LOCKS=0`, чтобы proof сам не refresh-ил index.
Один clean status недостаточен — assume-unchanged bytes
или commit могут скрыть правку, поэтому любой HEAD/ref/tree/raw drift отклоняет
receipt. Worktree read-only target разрешён лишь при доказанном detached exact
revision. Для non-git source нужен эквивалентный immutable
snapshot hash + no-change proof. Поскольку App worktrees делят common Git store,
coordinator также снимает pre/post protected-ref (все refs, кроме
runtime-owned ephemeral `refs/codex/*`), local common-config и common-control
snapshots, а также per-worktree Git admin (`HEAD`, raw index, config.worktree,
sparse metadata, operation heads/log). `assume-unchanged`/другие index flags —
side effect. Common-control включает `packed-refs` и real identity roots
`objects/refs/logs/info/hooks/modules`. Root `.git` marker, resolved
git-dir/common-dir и весь common
`.git/worktrees/*` registry тоже сравниваются. Journal разрешает exact новые App
entries assigned wave, но pre-existing/foreign entries frozen. Другой exact
coordinator journal разрешает current-mission registry before/after transition
только после final-read owner/host/generation; parent/sibling runtime paths
остаются в raw proof. Exact ref journal отдельно разрешает state checkpoint и
только его для текущей mission; receipt сам ничего не авторизует. State ref
нельзя удалить/пересоздать, integration/foreign refs frozen.
Raw proof ограничен 50 000 entries / 512 MiB и fail-closed для special files.
Это fail-closed postcondition, не механический read-only sandbox.

Writer contract 2.12 опирается на стандартные git invariants, а не на скрытую App
магию:

- Approved spec фиксирует base SHA, integration branch, отдельный clean
  coordinator-owned integration worktree и отдельную checkpoint-state
  branch/worktree с единственным scope `memory/missions/<slug>/`;
- dirty integration/state worktree блокирует writer start до решения пользователя;
  auto-stash и auto-commit запрещены;
- перед каждой writer attempt coordinator фиксирует exact `expectedBase`
  (mission base либо integration HEAD после upstream commits); отдельный App
  worktree создаётся detached без shared writer ref. Startup двухфазный:
  preflight-only task не пишет и возвращает READY после пустого
  `git symbolic-ref -q HEAD`, exact `HEAD == expectedBase`, clean/refs proof;
  coordinator reconciles всю wave и снимает baselines, затем exact follow-up
  marker+attempt авторизует edits. Без callable follow-up writer mode
  `unavailable`. После authorization writer возвращает один
  bounded non-merge commit с exact `expectedBase` parent и остаётся detached;
- coordinator проверяет ancestry, changed paths, clean raw tree,
  symlink/junction-free scope containment, common Git control и node gates.
  Post-create baseline связывает exact `.git` marker, git-dir/common-dir,
  frozen `config.worktree`/sparse/operation metadata, все assigned wave entries
  и submodule initialized/admin state. Mutable только canonical HEAD/index и
  optional reflog/commit-message files; они real/non-executable/single-link,
  index match commit без unsafe flags. Foreign/extra admin files frozen, а
  nested submodule common config/control/hooks/packed-refs тоже frozen;
  submodule transition требует отдельной заранее scoped authorization. Regular
  writer content files обязаны быть single-link. Затем
  выполняет `git cherry-pick` в disposable detached transaction worktree без
  shared transaction ref строго topologically;
- affected gate проходит до promotion. Только green разрешает canonical lock
  order `ownership -> promotion`, registry generation re-read под обоими locks,
  exact-old check + `--ff-only` + final-head check; red gate сохраняет прежний
  HEAD;
- конфликт останавливает transaction и abort-ится до отдельной Approved conflict
  node;
- `handoff_thread` не используется как DAG merge primitive, shared checkout
  parallel writers и force overwrite запрещены.

Исторический App smoke 2026-07-28 выполнен и записан без opaque handles в
[`docs/cross-dialog-missions/app-smoke-receipt.md`](../../../docs/cross-dialog-missions/app-smoke-receipt.md):

- подтверждены exact `clientThreadId -> threadId` reconciliation, marker/project/
  attempt identity, read-only A → B recovery attempts и fail-visible stale result;
- lazy attempt без Approved lead profile вернула `BLOCKED /
  ESCALATION_REQUEST`; повторная exact Sol/Ultra attempt использовала ровно один
  local architect + testing level и не создала descendants;
- два App worktree writers вернули scoped non-merge commits: A от mission base,
  B от integrated A; transaction gates прошли, отдельный clean verifier подтвердил
  итоговую цепочку;
- финальный preflight-only повтор подтвердил asynchronous `clientThreadId`,
  detached worktree на exact base и отсутствие нового shared writer ref.
  Model phase завершилась `systemError` из-за runtime usage quota до output;
  это записано как fail-visible incomplete probe, не PASS и не повод обходить
  ограничение;
- status был read-only; unavailable stop не симулировался; tasks не удалялись и
  не архивировались.

Этот исторический smoke не считался доказательством добавленного после него
обязательного двухфазного writer startup. Fresh release smoke 2026-07-29 отдельно
прошёл no-edit READY, coordinator baseline всей wave, exact follow-up и bounded
detached writer commit; детали записаны в том же receipt.

Конкретная App surface не предоставляет прямой способ детерминированно вызвать
конкурентный lock, red gate, conflict или crash между двумя filesystem writes.
Эти ветки воспроизводятся temp-git/runtime fixtures:

- три state checkpoints имеют exact parent chain и возрастающий `stateSequence`;
  partial diff после crash даёт `blocked`, не создаёт writer/ref side effects и
  оставляет последним durable source clean scoped checkpoint до explicit
  reconciliation;
- competing ownership/promotion locks дают `ambiguous`;
- generation drift и foreign Approved HEAD дают `stale`;
- red gate и conflict abort не сдвигают Approved HEAD;
- final portable bundle синхронизирует точное полное checkpoint subtree, включая
  удаления и `verification.md: APPROVED`, проходит fenced promotion и только
  после tree-identity check разрешает `Done`.
- SessionStart bounded scan смотрит максимум 50 candidates/5 records и для
  portable `Verifying` подавляет advisory, если exact state ref уже содержит
  authoritative `Done`.

После App/runtime upgrade production smoke повторяется. Coordinator takeover
по-прежнему обязан доказать non-running прежнего owner, получить exclusive
ownership lock, повторно прочитать generation и записать registry через file
`fsync + atomic replace + parent-directory fsync`, затем до снятия lock exact
final read regular single-link registry; live/unverifiable owner или lock
блокирует resume. Promotion берёт locks только `ownership -> promotion` и
перечитывает generation под обоими. `.codex/qtim-runtime` и
`memory/missions/<slug>` перед
любой записью проходят component-wise lstat/realpath containment без symlink/
junction; registry/temp/lock должны быть adjacent на том же filesystem.
Canonical names — `<slug>.json`, `<slug>.ownership.lock` и
`<slug>.promotion.lock`; promotion lock bind-ит owner token, generation и exact
integration target, поэтому разные lock paths не могут одновременно fence-ить
одну mission.
На first run missing parents создаются component-by-component с revalidation, а
первый registry публикуется под ownership lock через exclusive temp и atomic
no-clobber primitive; collision блокирует init, не заменяет чужой registry.
Raw snapshot отвергает root/directory junction до traversal; отдельный Windows CI
fixture создаёт реальные junctions. Writer tree отдельно отвергает same-bytes
hardlink через обязательный `st_nlink == 1`.

Невозможность доказать любой пункт блокирует соответствующую node/operation, но не
отключает заранее остальные проверяемые части mission.

## Проверяется этим репозиторием

`.github/scripts/check_hooks.py` исполняет POSIX/Windows handlers в временном git-проекте:
no-charter no-op, versioned SessionStart, JSON handoff, opt-in screenshot block, retry guard
и свежий tester artifact. `check_codex_agents.py` проверяет model pairs и read-only reviewer.

## Границы и fail-soft

- Matcher screenshot gate ожидает custom-agent type `qtim-testing`. Если будущий runtime
  изменит значение `agent_type`, gate останется advisory/no-op до обновления совместимости;
  `$qtim-doctor` должен показать это как `warn`, а не выдать непроверенный pass.
- Nested `AGENTS.md` зависит от рабочей директории, а не от каждого открытого файла. qtim не
  имитирует Claude path-scoped rules: критические инварианты дублируются компактно в role
  checklists и проверяются reviewer/CI.
- Полный charter не инжектируется hook-ом в каждый turn: автоматический корневой
  `AGENTS.md` даёт стартовый контракт, роли затем явно читают charter и нужную memory.

## Probe после обновления Codex

1. Запусти repo validation и `$qtim-doctor`.
2. В тестовом проекте создай marker agent `qtim-testing`, заверши его без screenshot и
   проверь один controlled retry.
3. Убедись, что reviewer не может писать в workspace.
4. Проверь `/hooks` и trust prompt; неизвестные команды не исполняй.
5. Через tool discovery повторно проверь project/thread schemas: local/worktree
   target, `threadId`/`clientThreadId`, batch limit и cursor.
6. Выполни read-only smoke `A -> B -> verification`, lazy smoke с агрегированным
   receipt и writer smoke `A commit -> gate -> B commit -> gate -> verification`
   только после явного запроса пользователя на отдельные задачи.
7. Проверь `status/resume/stop`: advisory не создаёт task, exact live handle
   продолжается, ambiguous/unavailable останавливается.
8. Обнови дату/версию выше только вместе с воспроизводимым evidence.
