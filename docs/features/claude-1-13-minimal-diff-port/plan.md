Feature: Семантический порт Claude qtim 1.13.0
Slug: claude-1-13-minimal-diff-port
Status: Done
Дата: 2026-07-30

# Plan

## Основание и границы

План реализует утверждённые:

- `docs/features/claude-1-13-minimal-diff-port/prd.md`;
- `docs/features/claude-1-13-minimal-diff-port/decomposition.md`;
- `docs/features/claude-1-13-minimal-diff-port/estimate.md`.

Acceptance criteria остаются в PRD, ownership и grounding — в decomposition,
размеры и риски — в estimate. Этот документ задаёт порядок вертикальных фаз,
write scopes, gates, rollout и rollback. Он не содержит production diff,
будущий код или временные оценки.

Ограничения исполнения:

- только Codex-native Markdown, JSON, TOML, YAML и repo-local Python validation;
- никакого application runtime, build/typecheck/browser/E2E gate: этих
  поверхностей в marketplace-репозитории нет;
- main thread владеет fan-out, интеграцией, подтверждением evidence и изменением
  статусов feature artifacts;
- subagent output advisory до проверки source и команд main thread;
- новый scope, irreversible fork или нарушение утверждённого PRD возвращается
  пользователю, а не поглощается реализацией;
- workflow recommendation и auto-start не входят в Stage 5 Draft.

## Порядок неопределённости

Read-only preflight сначала фиксирует baseline, candidate semver, владельцев и
verification oracles, но не принимает необратимых решений и ничего не пишет.
Затем стабилизируется канонический contract MD-01. Сразу после него, до
расширения на operational workflows, проверяются две наиболее рискованные
интеграционные границы в отдельных фазах MD-02/MD-03:

1. migration preservation/fingerprints и semver/stamp coupling MD-02/MD-03;
2. техническая форма MD-07: отдельный checker или расширение существующего,
   точная scan surface и negative oracle.

Scan boundary уже утверждена PRD. Ранний шаг выбирает только implementation
point и единственный validator owner; сам fail-closed gate реализуется в Phase 5,
когда все новые engine-managed references стабилизированы.

## Единоличное владение write scopes

Один физический файл имеет одного writer owner на всём протяжении feature.
DRI вертикального item отвечает за acceptance boundary, но не получает право
параллельно писать файл другого owner.

| Writer owner | Эксклюзивный write scope |
|---|---|
| Discipline/role writer — DRI MD-01 | `plugins/qtim/skills/qtim-minimal-diff/**`; `plugins/qtim/agents/architect.toml`; `database.toml`; `frontend.toml`; `reviewer.toml` |
| Generated-state/migration writer — DRI MD-02, writer MD-03 | `plugins/qtim/skills/qtim-setup/SKILL.md`; `plugins/qtim/skills/qtim-update/SKILL.md`; верхняя target section `plugins/qtim/reference/upgrade-notes.md`; `examples/fullstack-codex/.codex/team-charter.md`; все `examples/fullstack-codex/.codex/agents/*.toml` для semantic updates и финальных version stamps |
| Doctor writer — DRI MD-04 | `plugins/qtim/skills/qtim-doctor/SKILL.md` |
| Retro writer — DRI MD-05 | `plugins/qtim/skills/qtim-team-retro/SKILL.md` |
| Debug writer — DRI MD-06 | `plugins/qtim/skills/qtim-debug-loop/SKILL.md` |
| Validation owner — DRI MD-07 (`qtim-testing`) | `.github/scripts/check_skills.py`; `.github/scripts/check_codex_agents.py`; `.github/scripts/check_golden.py`; `.github/scripts/check_migrations.py`; новый `.github/scripts/check_skill_refs.py`, если выбран; `.github/workflows/validate.yml` |
| Release owner — DRI MD-08 | `plugins/qtim/THIRD_PARTY_NOTICES.md`; `AGENTS.md`; `plugins/qtim/.codex-plugin/plugin.json`; `README.md`; `CHANGELOG.md`; `docs/claude-port-map.md` |
| Main thread | Статусы/append-only history в `docs/features/claude-1-13-minimal-diff-port/`; подтверждённые review findings в `memory/review-report.md`; финальная интеграция |

Правила пересечений:

- MD-04/MD-05 передают setup requirements generated-state writer; сами
  `qtim-setup/SKILL.md` не редактируют.
- MD-01/MD-03 передают validator requirements validation owner; сами
  `.github/scripts/*` не редактируют.
- Release owner единолично меняет manifest/release metadata только в финальной
  фазе; generated-state owner после этого синхронизирует golden stamps.
- Runtime smoke для retro использует disposable target fixture и не записывает
  production `memory/retro-log.md` этого репозитория.

## Зависимости и parallel lanes

```text
Preflight: read-only baseline / ownership / oracles
    |
    v
Phase 1: MD-01
    v
Phase 2: MD-02
    |
    v
Phase 3: MD-03 + early MD-07 implementation-point freeze
    |
    v
Phase 4: MD-04 || MD-05 || MD-06
    |          serial setup-region integration by MD-02 owner
    v
Phase 5: MD-07
    |
    v
Phase 6: MD-08 + full integration/review
```

- MD-02 предшествует MD-03: migration targets должны соответствовать fresh
  generated contract.
- После Phase 3 MD-04, MD-05 и MD-06 выполняются параллельно в непересекающихся
  primary files.
- Setup additions MD-04/MD-05 интегрируются последовательно одним
  generated-state writer после стабилизации обеих lane contracts.
- MD-07 ждёт MD-04/05/06, чтобы сканировать окончательный набор
  engine-managed references.
- MD-08 закрывается только после зелёного MD-07 и полного integration diff.

## Preflight — read-only baseline

Outcome: команда знает фактическую стартовую версию, чистый feature scope,
владельцев файлов, применимые gates и disposable fixtures до первой записи.

Проверки:

1. Прочитать фактические manifest/changelog/upgrade versions и подтвердить
   candidate target по semver rebase rule, не меняя files.
2. Снять `git status` и отделить пользовательские/параллельные изменения от
   feature write scopes; чужие изменения не включать и не откатывать.
3. Зафиксировать baseline полного repo-local validation; существующий red signal
   маршрутизировать владельцу до feature implementation либо явно отделить как
   pre-existing blocker.
4. Подготовить disposable target fixtures/oracles для:
   - fresh/re-run setup preservation;
   - clean/override/ambiguous/resume migration;
   - doctor zero-diff;
   - retro marker classifications;
   - debug multi-call-site inventory;
   - MD-07 positive/negative scan.
5. Подтвердить single-writer matrix выше и отсутствие application
   build/typecheck/browser gates.

Preflight gate:

- baseline и pre-existing failures записаны;
- candidate version является предположением, а не опубликованным reservation;
- каждый пересекающийся файл имеет одного owner;
- fixtures не пишут production memory/source и могут быть удалены без потери
  evidence.

## Phase 1 — Каноническая дисциплина и роли

Items: **MD-01**.

Outcome: новый skill одновременно discoverable, безопасен по scope и реально
встроен в четыре role contracts; reviewer semantics не превращает рекомендацию
по объёму в blocker.

Работа:

1. Создать Codex skill contract и UI metadata с точным именем
   `$qtim-minimal-diff`.
2. Зафиксировать лестницу, protected zones, minimal self-check, marker
   trigger/action, escalation спорного scope и границы с brainstorm/prototype.
3. Встроить role-specific behavior в architect/database/frontend/reviewer,
   сохранив их модельные пары, report formats и обязательные gates.
4. Validation owner проверяет текущими ingestion/TOML validators и фиксирует
   требования к будущему cross-reference gate без преждевременного расширения
   scan surface.

Phase gates:

- `python3 .github/scripts/check_skills.py`;
- `python3 .github/scripts/check_codex_agents.py`;
- manual contract matrix `skill ↔ architect ↔ database ↔ frontend ↔ reviewer`
  не содержит противоречий по protected zones и review severity;
- skill/roles не содержат `.claude/*`, slash commands, Agent Teams, persistent
  team assumptions или fan-out ownership;
- exact atomic model pairs и существующие brainstorm/debug/review gates
  сохранены;
- изменение только объёма остаётся recommendation; нарушение PRD/invariant/gate
  остаётся blocker.

Stop condition:

- любая неоднозначность о том, можно ли сокращать утверждённый scope, блокирует
  переход к generated state и возвращается к PRD; implementation choice внутри
  уже утверждённой лестницы такого checkpoint не требует.

## Phase 2 — Fresh и additive generated state

Items: **MD-02**.

Outcome: fresh/re-run setup производит канонический generated contract и
доказывает preservation до проектирования migration.

1. Generated-state/migration writer обновляет Layer 0/mandatory practices и fresh
   generation для применимых roles.
2. Тот же owner принимает MD-04/05-independent базовые re-run rules: соседний
   track, manual text и существующие роли сохраняются.
3. Golden charter и четыре семантически затронутых role TOML синхронизируются с
   source templates. Version stamps пока не продвигаются: manifest остаётся
   release-owner scope финальной фазы.
4. Validation owner усиливает только необходимые golden/agent markers в своём
   эксклюзивном scope.

Phase gates:

- `python3 .github/scripts/check_golden.py`;
- `python3 .github/scripts/check_codex_agents.py`;
- fresh fixture содержит новый mandatory-practice contract;
- re-run fixture сохраняет второй track, manual text, existing roles и exact
  model overrides;
- setup plan до записи показывает additions и ничего не удаляет.

## Phase 3 — Incremental migration preservation

Items: **MD-03**. Ранний технический freeze будущего MD-07 не завершает
validator item.

Outcome: migration contract для candidate 2.12.0 → 2.13.0 доказуемо сохраняет
project state и останавливается на ambiguity; live manifest/stamps остаются
нетронутыми до release closure.

1. Architect и generated-state/migration writer подтверждают matrix
   распознаваемых anchors: clean managed region, user override, переименованная
   роль, отсутствующий target и неоднозначно изменённый block.
2. Generated-state/migration writer добавляет candidate newest-first target
   section с точными
   fingerprints/anchors и обновляет update workflow только в необходимой мере.
3. Validation owner добавляет migration/skill markers и positive/ambiguous
   evidence в своём scope.
4. Main thread проверяет четыре обязательных пути:
   - clean 2.12.0 → target;
   - foreign/manual content preservation;
   - compatible atomic model override;
   - ambiguous region → `pending`, no target stamp, no next version.
5. Повторный update после `pending` начинает с незавершённого шага и не
   дублирует уже применённые regions.
6. Validation owner выбирает один MD-07 implementation point:
   рекомендуемый default — отдельный `check_skill_refs.py` для full-token
   cross-surface resolution, тогда как `check_skills.py` сохраняет
   skill/migration markers. Если evidence подтверждает меньший единый contract
   через расширение `check_skills.py`, отдельный checker не создаётся.
7. Implementation point, included/excluded surfaces и negative oracle
   фиксируются в append-only history plan; PRD scan boundary не меняется.

Phase gates:

- `python3 .github/scripts/check_skills.py`;
- positive target, preservation, override, ambiguous/pending и resume evidence
  сохранены в target-parametrized verification report;
- неизвестная region не имеет fallback «заменить весь файл»;
- validator design имеет один source of truth, full-token negative oracle,
  zero-coverage и missing-surface failure;
- отсутствует удаление ролей, memory или foreign hooks/content.

Manifest-coupled `check_migrations.py`, финальные stamps и live target smoke
намеренно отложены до Phase 6: release owner ещё не менял version. Это
dependency, а не skipped pass.

Stop condition:

- нераспознаваемые реальные 2.12.0 fingerprints снижают automation до
  `pending`; они не разрешают whole-file overwrite и не расширяют feature scope.

## Phase 4 — Operational feedback loops

Items: **MD-04, MD-05, MD-06**.

Outcome: три независимых workflow behavior доступны и проверяемы сами по себе;
общий setup получает их integration wording только после стабилизации lanes.

### Lane A — MD-04 Doctor roster audit

Writer: doctor writer.

- Добавить evidence-backed roster signals и `warn` semantics.
- Сохранить doctor read-only/no-mutation.
- Supported role направляет в confirmed re-run setup; unsupported responsibility
  становится decision-owner gap без выдуманного template/auto-fix.

Lane gate:

- positive signals CI/data/public/monorepo и inverse «роль без слоя»;
- clean target без ложного warning;
- `git diff` disposable target до/после doctor пуст;
- wording имеет форму signal → gap → safe action.

### Lane B — MD-05 Retro marker lifecycle

Writer: retro writer.

- Ограничить marker search доказуемым epic diff.
- Различать triggered/not-triggered/unknown/malformed/protected.
- Создавать durable follow-up только для triggered marker в текущем
  `memory/retro-log.md`: source, trigger evidence, один owner, next action.
- Не создавать внешний issue или новый backlog/memory file автоматически.

Lane gate:

- пять classification scenarios воспроизводимы;
- triggered follow-up записывается в disposable target retro-log;
- not-triggered/unknown не создают ложную задачу;
- повторный retro не дублирует запись без нового evidence;
- protected-zone marker возвращается как contract violation.

### Lane C — MD-06 Debug-loop call-site inventory

Writer: debug writer.

- После repro/hypotheses и до fix назвать root seam, все обнаружимые repository
  call sites и adjacent paths.
- Dynamic/generated/external consumers оставить явными coverage gaps.
- Сохранить test-before-fix, root-cause preference, cleanup и bounded write scope.

Lane gate:

- multi-call-site scenario показывает inventory до fix;
- red/green signal доказывает root cause и применимые соседние пути;
- dynamic gap не называется проверенным;
- исходные debug-loop phases и cleanup contract сохранены.

### Serial setup integration

После lane gates MD-04/05 DRI передают requirements generated-state writer.
Только он обновляет setup regions:

- additive roster/re-run explanation для doctor;
- on-demand ownership/reference `memory/retro-log.md` для retro;
- без изменения Layer 0 semantics, уже закрытых MD-02.

Phase integration gates:

- `python3 .github/scripts/check_skills.py`;
- `python3 .github/scripts/check_golden.py`;
- targeted inspection setup не содержит конфликтующих владельцев memory/roster;
- `git diff --name-only` подтверждает lane write scopes и единственного writer
  setup-файла.

## Phase 5 — Fail-closed skill-reference gate

Items: **MD-07**.

Outcome: все стабилизированные engine-managed `$qtim-*` references разрешаются
полным токеном, а validator не проходит молча при исчезновении coverage.

Работа:

1. Validation owner реализует implementation point, зафиксированный Gate 2A.
2. Scan включает engine-managed plugin/reference/templates, generated fixtures
   и user-facing release surfaces; `docs/features/**` как historical prose
   исключён.
3. Checker проверяет полное имя, неизвестный suffix, missing required surface и
   ненулевое число references.
4. CI запускает тот же repo-local command, что и локальная проверка.
5. Negative evidence создаётся безопасной fixture/temporary copy, не оставляя
   намеренную опечатку в production source.

Phase gates:

- positive repository run зелёный и сообщает ненулевой coverage;
- неизвестное имя и valid-prefix-plus-invalid-suffix дают красный exit;
- missing surface и zero references дают красный exit;
- declared skill name ↔ directory contract остаётся проверяемым ровно одним
  каноном;
- `.github/workflows/validate.yml` вызывает checker;
- `python3 .github/scripts/check_skills.py`;
- новый `python3 .github/scripts/check_skill_refs.py`, если выбран отдельный
  checker; иначе документированный единый `check_skills.py` command;
- `python3 .github/scripts/check_links.py`.

Stop condition:

- неожиданные refs внутри утверждённой scan surface исправляются у их file
  owner; расширять scan на feature prose для получения «полноты» запрещено без
  возврата к PRD.

## Phase 6 — Legal, release и integration verification

Items: **MD-08**, финальная интеграция **MD-01–MD-07**.

Outcome: target release юридически целостен, версии/миграция/stamps согласованы,
полный Codex validation и независимый review подтверждают готовность к deploy.

Работа:

1. Release owner добавляет полный применимый MIT notice ponytail и maintainer
   rule для будущих MIT adaptations.
2. README/CHANGELOG/port map описывают user outcome, protected zones,
   migration, doctor/retro/debug feedback loops, новую Codex task и
   неперенесённые Claude-only mechanics.
3. Release owner повторно применяет semver rebase rule и только теперь записывает
   manifest target и согласованные release headings.
4. Generated-state/migration writer приводит target upgrade section и все
   golden stamps к фактической manifest version; validation owner запускает
   manifest-coupled migration/golden gates.
5. Main thread собирает единый diff, проверяет file ownership и отсутствие
   случайных/чужих изменений.
6. Testing выполняет полный local/CI/manual gate bundle.
7. После зелёных gates запускается отдельный read-only independent reviewer,
   потому что меняются public и generated-state contracts. Main thread открывает
   каждую указанную строку, подтверждает/отклоняет findings и маршрутизирует
   blockers владельцам.

### Repo-local gates

```bash
python3 -m json.tool .agents/plugins/marketplace.json > /dev/null
python3 -m json.tool plugins/qtim/.codex-plugin/plugin.json > /dev/null
python3 -m json.tool plugins/qtim/hooks/hooks.json > /dev/null
python3 -m json.tool plugins/qtim/reference/project-hooks.json > /dev/null
python3 .github/scripts/check_hooks.py
python3 .github/scripts/check_placeholders.py
python3 .github/scripts/check_skills.py
python3 .github/scripts/check_missions.py
python3 .github/scripts/check_links.py
python3 .github/scripts/check_codex_agents.py
python3 .github/scripts/check_migrations.py
python3 .github/scripts/check_golden.py
```

Если MD-07 выбрал отдельный checker, дополнительно:

```bash
python3 .github/scripts/check_skill_refs.py
```

### CI gate

- `.github/workflows/validate.yml` запускает тот же набор применимых repo-local
  checks, включая MD-07;
- CI на final integration commit зелёный;
- локальный pass не заменяет красный/не запущенный CI.

### Manual contract gates

- новая Codex task видит точное имя `$qtim-minimal-diff` и UI metadata;
- skill/role matrix сохраняет protected zones и recommendation-only review;
- fresh setup и additive re-run дают согласованный generated state;
- clean/preservation/override/ambiguous/resume migration scenarios соответствуют
  Phase 3 и повторены с фактической manifest version;
- doctor даёт `warn` и zero diff;
- retro различает marker states и создаёт только допустимый durable follow-up;
- debug-loop инвентаризирует несколько call sites и coverage gap до fix;
- MD-07 negative typo/suffix/zero-surface scenarios действительно красные;
- новая Codex task используется после изменения agent TOMLs; hot reload не
  обещается.

### Plugin validation

- доступный локальный `validate_plugin.py plugins/qtim` из Codex
  `plugin-creator` проходит;
- техническая недоступность фиксируется как `skipped — <reason>`, никогда как
  pass;
- ingestion/manual smoke остаётся обязательным даже при зелёном repo-local CI.

### Independent review gate

Scope: полный final diff, PRD, charter invariants и validation evidence.

Reviewer проверяет:

- Codex-native packaging и отсутствие Claude runtime leakage;
- public skill/role consistency;
- generated-state preservation, pending/stamp semantics и rollback;
- doctor read-only authority;
- retro durable-memory ownership;
- validator false-pass/false-positive boundaries;
- legal/release/version parity;
- отсутствие случайных изменений вне feature write scopes.

Verdict:

- `APPROVED` — только после подтверждения main thread и закрытия blockers;
- `NOT APPROVED` — любой подтверждённый public/generated-state blocker возвращает
  соответствующую фазу;
- unavailable review фиксируется как skipped/failure и не проходит release gate.

## Rollout

Rollout начинается только после Approved plan, отдельного handoff и завершённой
реализации; этот Draft ничего не запускает.

1. Реализовать фазы в указанном порядке, сохраняя зелёный gate каждой завершённой
   фазы.
2. Собрать final integration diff и validation/review evidence.
3. Подготовить conventional release commit с русским описанием.
4. Deploy выполняется только разрешённым `git push origin main` из этого
   source-of-truth репозитория; промежуточные копии/deploy folders не создаются.
5. После опубликованного release пользователь обновляет marketplace/plugin:
   `codex plugin marketplace upgrade qtim-agent-team`, затем
   `codex plugin add qtim@qtim-agent-team`, открывает новую Codex task.
6. Existing generated teams запускают `$qtim-update`, проверяют displayed
   plan/diff и подтверждают migration. Doctor warning о roster не изменяет team;
   пользователь отдельно запускает `$qtim-setup`.

Canary/percentage rollout неприменимы: hosted runtime и feature flags
отсутствуют. Безопасность rollout обеспечивают versioned migration,
user-confirmed diff, pending semantics и новая task.

## Semver rebase rule

2.13.0 — grounded target только пока manifest остаётся 2.12.0.

Перед первым version-bearing write release owner:

1. перечитывает `plugins/qtim/.codex-plugin/plugin.json` и верх
   `CHANGELOG.md`/`upgrade-notes.md`;
2. если 2.13.0 уже занята промежуточным release, выбирает следующий свободный
   minor target по repository convention;
3. одним coordinated integration change release owner обновляет manifest target
   и CHANGELOG heading, generated-state owner — target upgrade section и все
   generated/golden stamps; write ownership не передаётся между ними;
4. migration source остаётся 2.12.0 только если это подтверждено фактическим
   upgrade range; иначе notes описывают последовательный диапазон без пропуска
   промежуточной версии;
5. повторяет migration, golden и full validation gates.

Semver rebase не меняет PRD scope, work items или оценки. Любая попытка
перезаписать уже опубликованную version/tag вместо нового target запрещена.

## Rollback и обратимость

### До deploy

- красный phase gate останавливает продвижение, но не откатывает чужие изменения;
- исправление остаётся внутри file owner scope;
- если phase outcome отвергнут, удаляется/отменяется только feature-owned
  изменение через обычный reviewable diff или отдельный `git revert` после
  явного решения, без destructive reset;
- manifest/stamps не продвигаются дальше незавершённой migration.

### После deploy

- downgrade generated team не выполняется: `$qtim-update` запрещает проектный
  stamp новее plugin;
- source rollback выполняется только reviewable VCS revert feature/release
  commit, без destructive reset или ручного выдёргивания отдельных строк;
- если release уже опубликован, VCS revert не даунгрейдит generated projects и
  не переиспользует опубликованный semver: исправленное состояние публикуется
  следующим semver release с новой migration section;
- pending project остаётся на последней полностью применённой версии и безопасно
  повторяет незавершённый диапазон после fix release;
- уже применённый project не требует удаления пользовательских ролей, memory или
  ручного текста; managed practice корректируется следующей region-aware
  migration;
- `minimal-diff:` comments остаются обычными безопасными комментариями, если
  retro contract временно недоступен;
- новый skill и doctor/debug/retro instructions обратимы новой plugin version,
  потому что runtime/storage schema не вводятся.

## Критерий Done

Feature считается `Done`, только если одновременно:

1. MD-01–MD-08 достигли acceptance boundaries из decomposition/PRD.
2. Target version выбран по semver rule; manifest, CHANGELOG, upgrade notes и
   все golden stamps согласованы.
3. Fresh/re-run setup и migration preservation/override/pending/resume scenarios
   имеют проверяемое evidence.
4. Doctor, retro и debug-loop manual contract scenarios пройдены.
5. MD-07 positive и все обязательные negative scenarios пройдены.
6. Все repo-local и CI gates зелёные.
7. Plugin validation зелёный либо недоступность честно зафиксирована; при этом
   остальные release gates не ослаблены.
8. Independent reviewer дал подтверждённый `APPROVED`; blockers отсутствуют.
9. Diff не содержит Claude-only primitives, неожиданных файлов или изменений
   вне закреплённых write scopes.
10. README, notice, changelog и port map отражают фактическое поведение.
11. При старте реализации feature artifacts переведены в `In Development`, а
    после всех gates — в `Done`; отклонения и новые edge cases добавлены
    append-only в историю этого plan.
12. Main thread сообщил outcome и exact verification evidence, не называя
    skipped/unavailable проверки passed.

## Handoff

PRD и acceptance criteria:
`docs/features/claude-1-13-minimal-diff-port/prd.md`.

Обнови Status артефактов: `In Development` при старте, `Done` после gates.

Отклонения и новые edge cases фиксируй в «Истории изменений» этого `plan.md`.

## Что запускать дальше

Рекомендация: `$qtim-mission`.

Почему: feature содержит три самостоятельных operational outcomes
MD-04/MD-05/MD-06, непересекающиеся writer scopes и producer → consumer
зависимости MD-01 → MD-02 → MD-03 → MD-07 → MD-08; их нужно свести на одной
проверенной integration revision.

Топология: read-only preflight → MD-01 → MD-02 → MD-03 →
(MD-04 ∥ MD-05 ∥ MD-06) → MD-07 → MD-08 → independent verification.

Команда: `$qtim-mission, preview Approved feature docs/features/claude-1-13-minimal-diff-port/.`

Альтернатива: `$qtim-team-up` для последовательной реализации как одного
связного outcome с циклом implement → test → fix → review.

Режим `preview` выбран потому, что mission ещё должна подтвердить base и
integration target, writer/lazy/runtime choices и budgets. Этот handoff ничего
не запускает: peer tasks появляются только после явного вызова `$qtim-mission`
и последующего утверждения полного mission preview.

## История изменений

- 2026-07-30 — Draft r1: восемь Approved work items собраны в пять вертикальных
  фаз; migration/validator uncertainty вынесена сразу после MD-01; закреплены
  dependencies, parallel lanes, единоличные file owners, полный gate bundle,
  rollout, semver rebase, roll-forward rollback и Done. Stage 6 handoff оставлен
  явным placeholder без auto-start.
- 2026-07-30 — Draft r2: по architect skeleton добавлены read-only preflight и
  шесть execution phases; setup/update/upgrade-notes/golden объединены под одним
  generated-state owner, все validation files — под testing owner, а
  manifest/release metadata и финальные manifest-coupled gates перенесены в
  MD-08. Rollback уточнён как reviewable VCS revert без auto-downgrade.
- 2026-07-30 — Approved: пользователь утвердил plan; добавлен Stage 6 handoff.
  По обязательному topology gate выбран `$qtim-mission` в режиме `preview`:
  независимые MD-04/MD-05/MD-06 сходятся с producer → consumer цепочкой и
  финальной независимой проверкой. Реализация автоматически не запускалась.
- 2026-07-30 — In Development: после неуспешного запуска mission из-за
  ограничений runtime пользователь явно выбрал прямую реализацию. Фазы и
  acceptance boundaries сохранены, но выполняются последовательно в чистой
  integration-ветке без новых task/subagent fan-out.
- 2026-07-30 — MD-07 implementation point: выбран отдельный
  `.github/scripts/check_skill_refs.py`. `check_skills.py` остаётся единственным
  каноном frontmatter `name` ↔ directory, новый checker владеет только полным
  `$qtim-*` token, required surfaces и non-zero coverage. Scan включает
  `plugins/qtim/**`, `examples/fullstack-codex/**`, README/CHANGELOG/AGENTS и
  `docs/claude-port-map.md`; `docs/features/**` исключён как historical prose.
  Self-test использует disposable fixtures и доказывает typo, invalid suffix,
  zero references и missing surface.
- 2026-07-30 — Edge case миграции: текущий golden использует filenames
  `architect.toml`/`database.toml`, поэтому legacy glob
  `.codex/agents/qtim-*.toml` не является достаточным evidence. `$qtim-update`
  теперь просматривает все agent TOML, но меняет только роль с согласованными
  charter/filename/`name = "qtim-..."`; foreign custom agents и их stamps
  сохраняются.
- 2026-07-30 — Validation environment: системный Python не содержит PyYAML,
  поэтому обязательные `quick_validate.py` и `validate_plugin.py` запущены с
  PyYAML 6.0.2 из disposable `/private/tmp` dependency path; оба дали реальный
  pass, а не `skipped`.
- 2026-07-30 — Main-thread review: исправлены два blocker-class риска —
  call-site inventory стоял после инструкции внести fix, а migration искала
  canonical roles через несовместимый glob и недостаточно отделяла foreign
  agents. После исправлений полный local bundle зелёный. Independent review и
  installed-plugin smoke не выдаются за пройденные; feature остаётся
  `In Development` до этих release gates.
- 2026-07-30 — Independent review round 1: reviewer подтвердил blocker в
  миграции Extended custom roles — template-only update мог поставить charter
  stamp `2.13.0`, оставив generated custom code-writing role на `2.12.0`.
  `$qtim-update`, doctor и upgrade notes расширены fail-closed классификацией;
  добавлен positive/ambiguous/resume fixture contract.
- 2026-07-30 — Independent review rounds 2–3: первый migration oracle сохранял
  только sentinel, затем не сравнивал manual bytes ambiguous pending state.
  Финальный checker нормализует только exact target stamp/block/cell, сравнивает
  foreign и ambiguous before/after file sets побайтно и тем же oracle отвергает
  manual role/charter mutations, foreign near-miss, premature stamps и extra
  files. Оба подтверждённых blocker исправлены до публикации.
- 2026-07-30 — Installed runtime smoke: fresh isolated Codex task загрузил
  установленный `qtim:qtim-minimal-diff`; полный A–G scenario без skipped шагов
  подтвердил minimal-diff, fresh/additive setup, positive/pending/resume update,
  read-only doctor для Extended и PM-only, retro marker states, debug-loop
  call-site inventory и source isolation. Итог — `SMOKE_APPROVED`. Обычный
  App catalog этого профиля превысил документированный skills context budget
  2%; smoke повторён через поддерживаемый per-command `skills.config` с
  отключением посторонних user skills, без изменения plugin source.
- 2026-07-30 — Done: exact candidate
  `52fd0240766f0c89705e8b5de876b22a40a860f5` прошёл полный repo-local bundle,
  PyYAML и fallback frontmatter paths, official skill/plugin validators,
  installed-plugin smoke и новый clean-context independent review с вердиктом
  `APPROVED`. После fast-forward push GitHub Actions run `30555480634` завершил
  `validate` и `validate-windows-hooks` со статусом `success`; MD-01–MD-08
  закрыты, blockers отсутствуют.
