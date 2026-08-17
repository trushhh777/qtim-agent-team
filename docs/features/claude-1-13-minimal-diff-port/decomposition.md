Feature: Семантический порт Claude qtim 1.13.0
Slug: claude-1-13-minimal-diff-port
Status: Approved
Дата: 2026-07-30

# Decomposition

## Основание

Декомпозиция следует утверждённым:

- `docs/features/claude-1-13-minimal-diff-port/intake.md`;
- `docs/features/claude-1-13-minimal-diff-port/prd.md`.

Selective consult ограничен реально затронутыми слоями: architect проверил
plugin/generated-state boundaries и зависимости; testing — validation surface и
негативные сценарии. Product добавляет только wording/durable-shape slices в
doctor, retro и release documentation. Application frontend/backend/database
слоёв в самом marketplace-репозитории нет.

Каждый item ниже — отдельный проверяемый outcome с одним DRI. Технические
результаты consult остаются evidence; финальные acceptance boundaries заданы
утверждённым PRD и доменными инвариантами charter.

## Вертикальные work items

| id | вертикальный work item | DRI | contributing роли/слои | зависимости | grounding (файлы) |
|---|---|---|---|---|---|
| MD-01 | Добавить discoverable `$qtim-minimal-diff` и довести один и тот же contract до architect/database/frontend/reviewer: лестница, protected zones, minimal self-check, escalation при споре о scope и recommendation-only review | Main thread / plugin-source writer | `qtim-architect`: public/role contract; `qtim-testing`: ingestion и agent validation | — | Новый `plugins/qtim/skills/qtim-minimal-diff/SKILL.md`; новый `plugins/qtim/skills/qtim-minimal-diff/agents/openai.yaml`; `plugins/qtim/agents/architect.toml`; `database.toml`; `frontend.toml`; `reviewer.toml`; `.github/scripts/check_skills.py`; `.github/scripts/check_codex_agents.py` |
| MD-02 | Сделать fresh setup и additive re-run источником тех же mandatory practices и доказать generated outcome на golden project | Main thread / generated-contract writer | `qtim-architect`: generated-state/track invariants; `qtim-testing`: fresh/re-run и golden validation | MD-01 | `plugins/qtim/skills/qtim-setup/SKILL.md`; `examples/fullstack-codex/.codex/team-charter.md`; golden `architect.toml`, `database.toml`, `frontend.toml`, `reviewer.toml`; `.github/scripts/check_golden.py` |
| MD-03 | Провести безопасную incremental migration 2.12.0 → 2.13.0 для charter/roles: preservation, ambiguity → `pending`, stamp только после полного применения | Main thread / migration writer | `qtim-architect`: migration boundaries и rollback; `qtim-testing`: positive/ambiguous/preservation scenarios | MD-01, MD-02 | `plugins/qtim/skills/qtim-update/SKILL.md`; верхняя секция `plugins/qtim/reference/upgrade-notes.md`; `.github/scripts/check_migrations.py`; migration markers в `.github/scripts/check_skills.py`; golden target smoke в `examples/fullstack-codex/` |
| MD-04 | Добавить read-only doctor roster audit от repository signals до actionable `warn`, включая responsibility gap без поддерживаемого template и явный возврат в additive setup | Main thread / plugin writer | `qtim-architect`: authority/setup boundary; `qtim-testing`: warn/no-mutation scenarios; `qtim-product`: user-facing signal → gap → action wording | MD-02 | `plugins/qtim/skills/qtim-doctor/SKILL.md`; roster/re-run integration в `plugins/qtim/skills/qtim-setup/SKILL.md` |
| MD-05 | Замкнуть lifecycle `minimal-diff:` marker: epic-scoped поиск, trigger classification и durable follow-up в `memory/retro-log.md` с source/owner/next action | Main thread / plugin writer | `qtim-architect`: memory ownership и scope boundary; `qtim-testing`: triggered/untriggered/unknown/protected scenarios; `qtim-product`: durable follow-up shape | MD-01 | `plugins/qtim/skills/qtim-team-retro/SKILL.md`; runtime target `memory/retro-log.md` как создаваемый workflow artifact, не production edit; memory ownership/reference в `plugins/qtim/skills/qtim-setup/SKILL.md` |
| MD-06 | Перед нетривиальным bug fix добавить в debug-loop инвентаризацию всех обнаружимых call sites и соседних путей с явными coverage gaps | Main thread / plugin writer | `qtim-architect`: root-seam boundary; `qtim-testing`: reproducible multi-call-site scenario | MD-01 | `plugins/qtim/skills/qtim-debug-loop/SKILL.md` |
| MD-07 | Сделать engine-managed `$qtim-*` references fail-closed contract: полное имя, установленная scan boundary, ненулевой coverage и красная negative fixture | `qtim-testing` | `qtim-architect`: namespace/scan boundary; validation/CI layer — `qtim-testing` | MD-01, MD-02, MD-04, MD-05, MD-06 | Новый `.github/scripts/check_skill_refs.py` либо осознанное расширение `.github/scripts/check_skills.py`; `.github/workflows/validate.yml`; engine-managed plugin/reference/templates, generated fixtures и user-facing release surfaces по PRD |
| MD-08 | Закрыть legal/release/parity contract для 2.13.0 и подтвердить согласованность всего вертикального пакета | Main thread / release owner | `qtim-architect`: release/invariant review; `qtim-testing`: полный validation evidence; `qtim-product`: outcome/migration/discoverability wording | MD-01–MD-07 | `plugins/qtim/THIRD_PARTY_NOTICES.md`; `AGENTS.md`; `plugins/qtim/.codex-plugin/plugin.json`; `README.md`; `CHANGELOG.md`; `docs/claude-port-map.md`; version-dependent stamps в `examples/fullstack-codex/.codex/team-charter.md` и golden TOMLs |

## Acceptance boundary и verification evidence

### MD-01 — Discoverable discipline + role behavior

Acceptance boundary:

- `$qtim-minimal-diff` имеет точное Codex skill name и UI metadata;
- skill остаётся role-agnostic practice без fan-out или собственного report
  schema;
- architect сравнивает design-варианты, database/frontend применяют лестницу до
  нетривиальной реализации, reviewer относит чистую избыточность к рекомендациям;
- protected zones, согласованный scope и minimal self-check не сокращаются;
- role templates сохраняют exact atomic model pairs и остальные mandatory gates.

Verification evidence:

- `check_skills.py` подтверждает ingestion metadata и skill structure;
- `check_codex_agents.py` подтверждает TOML/model/required markers;
- targeted inspection показывает одинаковую семантику discipline/roles и
  recommendation-only reviewer contract;
- negative inspection подтверждает отсутствие Claude syntax и orchestration
  ownership в discipline.

### MD-02 — Fresh/re-run setup + generated golden

Acceptance boundary:

- fresh setup включает `$qtim-minimal-diff` в Layer 0 и записывает применимые
  mandatory practices;
- re-run дозаполняет managed regions/roles, не пересоздаёт team, не удаляет роли,
  не затирает соседний `qtim:track:*` block и manual text;
- golden charter и четыре затронутых role TOML отражают source contract;
- существующие brainstorm/debug-loop/ADR practices не регрессируют.

Verification evidence:

- `check_golden.py` проходит на fresh generated target;
- targeted re-run scenario сравнивает before/after для второго track, manual
  text и существующих ролей;
- generated TOMLs остаются self-contained и сохраняют model pairs;
- setup plan явно показывает additions до записи.

### MD-03 — Safe 2.12.0 → 2.13.0 migration

Acceptance boundary:

- upgrade notes содержат newest-first секцию 2.13.0 с fingerprints/anchors для
  каждого mandatory generated-state шага;
- update применяет диапазон oldest → newest и показывает plan/diff до записи;
- foreign/manual content, оба track block и user-approved atomic model override
  сохраняются;
- неоднозначная или переименованная target region остаётся `pending`;
- при `pending` stamps не переходят на 2.13.0 и дальнейшие версии не применяются;
- полностью применённая migration согласует charter, role TOMLs и stamps.

Verification evidence:

- `check_migrations.py` связывает generated-state producer changes, version bump
  и новую migration section;
- `check_skills.py` подтверждает incremental/pending markers;
- positive smoke достигает 2.13.0; preservation smoke не меняет foreign/manual
  content и override; ambiguous smoke остаётся на 2.12.0;
- повторный update начинает с незавершённого диапазона, не дублируя applied
  regions.

### MD-04 — Doctor roster audit

Acceptance boundary:

- doctor выводит только evidence-backed `warn`, а не `fail`, для roster drift;
- warning имеет форму repository signal → responsibility/role gap → safe action;
- doctor не меняет charter, agents или memory;
- поддерживаемая роль ведёт к повторному `$qtim-setup`; responsibility без
  template возвращается decision owner без обещания auto-fix;
- setup остаётся additive и требует displayed plan/approval.

Verification evidence:

- сценарии с CI/data/public/monorepo signals дают воспроизводимые warnings;
- обратный сценарий «роль без слоя» также advisory;
- clean scenario не даёт ложного warning;
- `git diff` до/после doctor пуст;
- wording review подтверждает отсутствие выдуманных application actors и
  несуществующего template.

### MD-05 — Retro marker lifecycle

Acceptance boundary:

- retro ищет markers только в доказуемом epic diff и приводит source;
- marker различает потолок и проверяемый trigger/action;
- outcomes `triggered`, `not triggered`, `unknown` не смешиваются;
- только triggered marker получает durable follow-up в текущем
  `memory/retro-log.md` с source, trigger evidence, одним owner и next action;
- marker в protected zone возвращается как contract violation;
- внешний issue/backlog и новый memory-файл автоматически не создаются.

Verification evidence:

- targeted fixtures покрывают triggered/untriggered/unknown/malformed/protected
  cases;
- runtime retro output и созданная запись `memory/retro-log.md` согласованы;
- setup-generated memory reference объясняет on-demand ownership retro-log;
- повторный retro не дублирует уже зафиксированный follow-up без нового evidence.

### MD-06 — Debug-loop call-site inventory

Acceptance boundary:

- после repro/hypotheses и до fix назван root seam;
- перечислены все обнаружимые repository call sites и соседние пути;
- dynamic/generated/external consumers отмечены coverage gap;
- inventory усиливает test-before-fix и cleanup, не заменяя остальные фазы;
- общий root fix не расширяет write scope молча.

Verification evidence:

- scenario с несколькими call sites показывает inventory до правки;
- regression signal краснеет на root cause и зеленеет после scoped fix;
- неизвестный dynamic consumer остаётся явным gap;
- skill validation подтверждает сохранность исходных debug-loop phases.

### MD-07 — Engine-managed skill-reference gate

Acceptance boundary:

- validator проверяет declared skill name и полное `$qtim-<name>` token;
- scan boundary соответствует PRD: engine-managed plugin/reference/templates,
  generated fixtures и user-facing release surfaces; feature artifacts как prose
  evidence исключены;
- отсутствующая обязательная scan surface и zero checked references дают fail;
- неизвестное полное имя/суффикс даёт fail, а не совпадает по валидному prefix;
- implementation выбирает либо отдельный checker, либо расширение
  `check_skills.py` без двух расходящихся канонов.

Verification evidence:

- positive repository run зелёный и сообщает ненулевой coverage;
- negative fixture с намеренной опечаткой красная;
- fixture с валидным prefix и ошибочным suffix тоже красная;
- CI запускает тот же repo-local contract, что используется локально.

### MD-08 — Legal/release/parity closure

Acceptance boundary:

- target release — 2.13.0, если до implementation не появится новый plugin
  release; изменение этого предположения требует только последовательного
  semver/stamp rebase, не пересмотра feature scope;
- THIRD_PARTY_NOTICES содержит полный применимый MIT notice ponytail;
- maintainer guidance требует полного notice для будущих MIT adaptations;
- manifest, README, CHANGELOG, upgrade notes, port map и golden stamps
  согласованы;
- release docs объясняют discoverability, protected zones, migration и новую
  Codex task после update;
- Claude-only mechanics явно не перенесены.

Verification evidence:

- полный validation contract из `AGENTS.md` зелёный;
- доступный `validate_plugin.py plugins/qtim` зелёный либо честно
  `skipped — <reason>`;
- manifest version, changelog heading, migration target и generated stamps
  совпадают;
- independent read-only review фактического public/generated-state diff даёт
  проверенный release verdict.

## Зависимости и disjoint scope hints

```text
MD-01 ─┬─> MD-02 ─┬─> MD-03 ───────────────┐
       │          └─> MD-04 ──────────┐     │
       ├─> MD-05 ─────────────────────┤     │
       └─> MD-06 ─────────────────────┼─> MD-07 ─> MD-08
                                      └───────────────┘
```

- После стабильного MD-01 параллельны MD-05 и MD-06; их production write scopes
  не пересекаются.
- MD-02 и MD-04 оба затрагивают setup: MD-02 владеет Layer 0/mandatory
  practices и golden generation, MD-04 — additive roster/re-run wording.
  Параллельная запись в один файл не рекомендуется; при параллельной работе
  нужны disjoint regions и последовательная интеграция.
- MD-05 затрагивает setup только в memory ownership/reference region; его можно
  отделить от MD-02/MD-04 точным region ownership, иначе сериализовать.
- MD-03 владеет update/upgrade-notes и может идти после интеграции MD-01/02,
  независимо от doctor/retro/debug implementation.
- MD-07 начинается после стабилизации всех новых engine-managed references, иначе
  его scan evidence преждевременно.
- MD-08 единственный владеет release version/docs и финальными golden stamps.
  MD-02 меняет golden semantics, но не закрывает version stamp до MD-08.

## ADR

ADR не требуется. Product/public contract и три спорные границы уже утверждены в
PRD; порт не вводит новый runtime, storage layer, destructive data transform или
дорогое в откате архитектурное решение. Если implementation обнаружит новый
необратимый trade-off за пределами этих решений, он возвращается на design
checkpoint и не поглощается этой декомпозицией.

## Checkpoint стадий 3–4

Отдельного checkpoint для этого файла нет. Пользователь одним решением утверждает
work items из `decomposition.md` и grounded estimates из `estimate.md`. До этого
оба артефакта остаются `Draft`.

## История изменений

- 2026-07-30 — Draft r1: selective architect/testing/product evidence
  синтезирован в восемь независимых вертикальных outcomes с одним DRI,
  acceptance boundaries, verification evidence, зависимостями и disjoint scope
  hints; ADR признан ненужным.
- 2026-07-30 — Approved r2: пользователь единым решением утвердил восемь
  vertical work items и связанные grounded estimates.
