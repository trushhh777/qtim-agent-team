Feature: Семантический порт Claude qtim 1.13.0
Slug: claude-1-13-minimal-diff-port
Status: Done
Дата: 2026-07-30

# Estimate

## Метод

Оценки относительные: `S/M/L/XL`, без часов и дней. Architect и testing оценили
только свои layer slices; product оценивает лишь user-facing wording/durable
shape там, где действительно contributes. DRI синтезирует один размер
вертикального item с учётом integration risk; размеры слоёв не складываются.

Confidence:

- `high` — surface и acceptance boundary известны, есть близкий repository
  precedent;
- `medium-high` — surface известна, остаётся ограниченный integration choice;
- `medium` — основной риск находится в сценариях preservation/ambiguity или
  cross-surface consistency, которые нужно доказать реализацией.

XL-срезов нет. MD-03 остаётся L, но имеет одну неделимую acceptance boundary:
безопасный переход 2.12.0 → 2.13.0 с preservation и fail-visible `pending`.

## Reference classes

| Reference class | Фактический размер diff | Релевантность |
|---|---|---|
| Codex 2.9.0, commit `cb911ae` | 36 files, 792 additions, 202 deletions | Порт четырёх bundled disciplines, role templates, setup/update, validators, notices и release docs |
| Codex 2.11.0, commit `6b492b3` | 41 files, 795 additions, 47 deletions | Generated-state contract, migration/golden validators, role/runtime changes и release closure |
| Claude 1.13.0, commit `887975f` | 24 files, 588 additions, 22 deletions | Прямой semantic source: minimal-diff, четыре роли, setup/sync, doctor/retro/debug, CI и legal |

Reference classes подтверждают общий feature size `L`: затрагивается широкий
набор Markdown/YAML/TOML/Python/release surfaces, но после нарезки ни один item,
кроме migration boundary, не требует L/XL сам по себе.

## Layer estimates и DRI synthesis

### MD-01 — Discoverable discipline + role behavior

| Слой / роль | Размер | Confidence | Evidence и риски |
|---|---|---|---|
| Architect / public и role contract | M | high | Семантика утверждена PRD и upstream `887975f`; затронуты новый skill и четыре существующих role templates. Риск — размыть protected zones или превратить recommendation reviewer'а в blocker |
| Testing / ingestion и agent validation | M | high | Существуют `.github/scripts/check_skills.py` и `check_codex_agents.py`, а четыре bundled disciplines дают metadata precedent. Риск — новый marker не будет защищён валидатором или нарушит exact model-pair contract |
| DRI synthesis | **M** | **high** | Один связный public outcome: skill одновременно discoverable и фактически вызывается ролями. Integration шире одного файла, но contracts и validators уже существуют; размеры слоёв не складываются |

### MD-02 — Fresh/re-run setup + generated golden

| Слой / роль | Размер | Confidence | Evidence и риски |
|---|---|---|---|
| Architect / generated-state invariants | M | medium | Setup уже генерирует Layer 0 practices, track-aware charter и role TOMLs. Риск — fresh и re-run разойдутся либо additive update затронет соседний track/manual text |
| Testing / setup и golden scenarios | M | medium-high | `check_golden.py` уже сверяет stamps, markers и role semantics на `examples/fullstack-codex/`. Риск — golden докажет fresh state, но пропустит preservation re-run |
| DRI synthesis | **M** | **medium** | Outcome вертикальный: producer setup → generated fixture → validation. Размер удерживается M существующим генерационным contract, но confidence снижает необходимость доказать оба режима без clobber |

### MD-03 — Safe 2.12.0 → 2.13.0 migration

| Слой / роль | Размер | Confidence | Evidence и риски |
|---|---|---|---|
| Architect / migration boundary | L | medium | `qtim-update`, newest-first `upgrade-notes.md`, region fingerprints, atomic model overrides и incremental stamps уже образуют сложный contract. Риск — ambiguity ошибочно применится или version range продолжится после pending |
| Testing / preservation и ambiguity | L | medium | `check_migrations.py` проверяет наличие versioned notes, `check_skills.py` — pending/incremental markers; нужны positive, preservation, ambiguous и resume scenarios. Риск — happy path зелёный при потере foreign/manual content |
| DRI synthesis | **L** | **medium** | Это один неделимый migration outcome: частичная «успешная» миграция без preservation/pending semantics не имеет пользовательской ценности. L обусловлен state matrix и rollback, не суммой двух L-slices; XL не требуется, потому что target один и механизм incremental migration уже существует |

### MD-04 — Doctor roster audit

| Слой / роль | Размер | Confidence | Evidence и риски |
|---|---|---|---|
| Architect / authority и setup boundary | M | medium | Doctor уже read-only и setup уже владеет roster generation. Риск — warning станет скрытой мутацией или обещает unsupported role template |
| Testing / diagnostic scenarios | M | medium | Нужны positive/negative сигналы для CI/data/public/monorepo и нулевой diff. Риск — эвристики создадут ложные warnings на repository markers |
| Product / warning wording | S | high | PRD утвердил форму signal → responsibility gap → action и правило для unsupported template. Риск ограничен неоднозначной формулировкой auto-fix |
| DRI synthesis | **M** | **medium** | Plugin logic, безопасный UX и no-mutation evidence должны поставляться вместе. Product slice мал, но integration doctor↔setup и heuristic matrix удерживают итог M |

### MD-05 — Retro marker lifecycle

| Слой / роль | Размер | Confidence | Evidence и риски |
|---|---|---|---|
| Architect / memory ownership | M | medium | Existing retro пишет `memory/retro-log.md` on demand через main thread; новый storage layer не нужен. Риск — marker harvesting выйдет за epic scope или создаст конкурирующий backlog contract |
| Testing / lifecycle scenarios | M | medium | Нужны triggered/untriggered/unknown/malformed/protected и dedup scenarios. Риск — write-only marker либо шумовой follow-up без evidence |
| Product / durable follow-up shape | S | high | PRD утвердил source + trigger evidence + owner + next action в текущем retro-log. Риск — terminology не различит `unknown` и `triggered` |
| DRI synthesis | **M** | **medium** | Один полный lifecycle от marker в epic diff до durable follow-up. Существующий memory owner ограничивает scope, но classification/dedup требуют M |

### MD-06 — Debug-loop call-site inventory

| Слой / роль | Размер | Confidence | Evidence и риски |
|---|---|---|---|
| Architect / root-seam boundary | S | high | Изменяется одна существующая discipline phase; PRD уже определил inventory до fix и coverage gaps. Риск — формулировка поощрит patch всех call sites вместо root fix |
| Testing / multi-call-site evidence | S | medium-high | Один targeted scenario доказывает несколько call sites, adjacent paths и dynamic gap. Риск — статический поиск будет назван полным при dynamic/generated consumer |
| DRI synthesis | **S** | **medium-high** | Один файл и одна bounded behavioral addition, без generated-state migration. Нужен сценарий, но integration surface минимальна |

### MD-07 — Engine-managed skill-reference gate

| Слой / роль | Размер | Confidence | Evidence и риски |
|---|---|---|---|
| Architect / namespace и scan boundary | M | medium-high | PRD утвердил engine-managed/release surfaces и исключил feature prose. Implementation choice отдельного checker или расширения существующего не меняет boundary. Риск — два расходящихся канона |
| Testing / validator и CI | M | high | `check_skills.py`, `check_links.py` и `validate.yml` дают готовые integration points; требуются full-token, zero coverage, missing surface и negative typo checks. Риск — prefix match или молчаливая деградация scan |
| DRI synthesis (`qtim-testing`) | **M** | **high** | Один fail-closed repository gate с понятной positive/negative oracle. Итог M из-за scan/parser/CI integration, но существующая validation framework снижает риск |

### MD-08 — Legal/release/parity closure

| Слой / роль | Размер | Confidence | Evidence и риски |
|---|---|---|---|
| Architect / release invariants | M | high | Manifest/version/stamps/migration/changelog и Codex-native port boundary документированы в AGENTS/charter/port map. Риск — version-dependent files расходятся |
| Testing / release validation | S | high | Полный список repo-local commands фиксирован в `AGENTS.md`; plugin validator доступен best effort. Риск — skipped ошибочно выдан за passed |
| Product / outcome и migration docs | M | high | README, CHANGELOG и port map должны согласованно объяснить discoverability, protected zones, migration и неперенесённые Claude mechanics. Риск — документация обещает hot reload или auto-fix |
| DRI synthesis | **M** | **high** | Release closure затрагивает несколько docs/version files, но не создаёт новую product behavior. Много файлов — coordination factor, а не основание L |

## Сводка DRI

| id | Итоговый размер | Confidence | Главный integration risk |
|---|---|---|---|
| MD-01 | M | high | Расхождение public skill и четырёх role contracts |
| MD-02 | M | medium | Fresh/re-run preservation и golden semantic parity |
| MD-03 | L | medium | Потеря manual/track/model state или ложное продвижение stamp |
| MD-04 | M | medium | Ложный roster signal либо unsupported auto-fix promise |
| MD-05 | M | medium | Marker без доказуемого trigger превращается в шум/вечный TODO |
| MD-06 | S | medium-high | Inventory ошибочно назван полным или поощряет patches по call sites |
| MD-07 | M | high | Prefix false-pass, zero-coverage pass или слишком широкая scan surface |
| MD-08 | M | high | Несогласованные version/release/migration/golden surfaces |

## Общий размер feature

**L, confidence medium-high.**

Синтез основан не на сложении восьми items, а на форме интеграции:

- один public contract проходит через roles, setup, migration и validation;
- пять outcomes после MD-01 частично независимы, но сходятся в MD-07/MD-08;
- единственный L-item — безопасная migration со state-preservation matrix;
- три близких reference class подтверждают широкий release diff в 24–41 файл,
  но существующие setup/update/validator mechanics не требуют нового runtime или
  XL-нарезки.

## Главные риски оценки

1. Реальные fingerprints 2.12.0 generated role regions могут оказаться менее
   однозначными, чем следует из текущего `upgrade-notes.md`; это снижает
   confidence MD-03, но должно приводить к `pending`, а не к расширению scope.
2. Setup — общий integration point MD-02/04/05. Неуправляемая параллельная запись
   увеличит coordination risk без увеличения продуктового объёма; scopes нужно
   разделить по regions или сериализовать.
3. Validator implementation choice может обнаружить неожиданные engine-managed
   `$qtim-*` references. PRD scan boundary фиксирована, поэтому historical prose
   не должно раздувать item.
4. Если target version перестанет быть 2.13.0 из-за промежуточного release,
   MD-03/08 требуют semver/stamp rebase, но не новой декомпозиции.

## Checkpoint стадий 3–4

Этот файл утверждается только вместе с `decomposition.md`. Если пользователь
меняет состав любого work item, layer estimates и DRI synthesis затронутых items
пересчитываются до повторного общего checkpoint.

## История изменений

- 2026-07-30 — Draft r1: selective consult разложен по architect/testing/product
  slices; DRI синтезировал S/M/L размеры с confidence, risks и repository
  evidence; общий feature size подтверждён как L без XL-items и без временных
  оценок.
- 2026-07-30 — Approved r2: пользователь единым решением утвердил work items,
  layer estimates, DRI synthesis и общий размер L с confidence medium-high.
