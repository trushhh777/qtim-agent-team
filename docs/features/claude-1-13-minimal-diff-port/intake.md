Feature: Семантический порт Claude qtim 1.13.0
Slug: claude-1-13-minimal-diff-port
Status: In Development
Дата: 2026-07-30

# Intake

## Исходная хотелка

Изучить changelog нового релиза родительского Claude Code-плагина и подготовить
implementation-ready план доработки Codex-плагина qtim. На этой стадии production/plugin
code не меняется: результатом должен стать утверждённый набор feature-артефактов.

## Проблема

Claude-родитель выпустил версию
[1.13.0](https://github.com/toiiia/qtim-agent-team/commit/887975fb3324506a64428311d79e533579b1c70d),
а Codex-плагин остаётся на 2.12.0. Новый релиз — связанный пакет, а не изолированный текст
одного skill:

- новая дисциплина `minimal-diff`;
- её обязательные точки вызова и проверки в ролевых шаблонах;
- доставка практик в generated charter и миграция существующих команд;
- advisory-диагностика актуальности состава команды;
- сбор маркеров осознанных упрощений на retro;
- инвентаризация call sites перед нетривиальным bug fix;
- CI-проверка резолвинга ссылок на skills и полное MIT notice.

Без семантического порта Codex-версия расходится с родителем по дисциплине объёма решения,
generated-state contract и диагностическим/ретроспективным feedback loops.

## Пользователи

- Maintainer Codex-плагина, которому нужен проверяемый и мигрируемый релиз.
- Developer и Both-пользователи qtim, чьи роли проектируют, реализуют и проверяют изменения.
- Владельцы уже сгенерированных qtim-команд, которым `$qtim-update` должен показать
  безопасную миграцию без перезаписи пользовательских overrides.

PM/Analyst получает косвенную пользу через более точный handoff и architect consult, но
новая дисциплина не должна превращаться в ещё один PM-orchestrator.

## Желаемый результат

Codex-native релиз сохраняет продуктовый смысл Claude 1.13.0:

1. `$qtim-minimal-diff` доступен как role-agnostic bundled discipline с Codex metadata.
2. Architect применяет лестницу при сравнении вариантов; code-writing templates —
   перед нетривиальной реализацией; reviewer классифицирует лишний объём как рекомендацию,
   не как автоматический blocker.
3. Защищённые зоны, согласованный scope и обязательная минимальная самопроверка
   нетривиальной логики не могут быть «срезаны» дисциплиной.
4. Setup и `$qtim-update` доставляют новые mandatory practices в generated state,
   сохраняя track markers, ручной текст и model overrides.
5. `$qtim-doctor` только предупреждает о расхождении roster с фактами репозитория;
   изменение состава остаётся явным повторным `$qtim-setup`.
6. Retro поднимает сработавшие `minimal-diff:` маркеры в проверяемый follow-up, а
   debug-loop проверяет все call sites и соседние пути до фикса.
7. CI ловит неверное имя skill и нерезолвящиеся `$qtim-*` ссылки; legal notice и
   release/port-map документация соответствуют фактическому источнику.

## Evidence

### Upstream

- Changelog 1.13.0 и commit `887975f` перечисляют 24 изменённых файла и все связанные
  поверхности: новый skill, четыре role templates, doctor/setup/team-retro/team-sync,
  debug-loop, migration, CI, golden example и notices.
- Upstream явно отделяет `minimal-diff` от prototype/brainstorm: дисциплина выбирает объём
  остающегося решения, но не сужает согласованные acceptance criteria и не отменяет design
  или verification gates.
- Источник `DietrichGebert/ponytail` распространяется по MIT и требует полного notice,
  а не одной строки attribution.

### Текущий Codex-репозиторий

- `plugins/qtim/.codex-plugin/plugin.json` имеет версию `2.12.0`.
- В `plugins/qtim/skills/` есть 15 workflows/disciplines; `qtim-minimal-diff` отсутствует.
- `plugins/qtim/skills/qtim-setup/SKILL.md` знает четыре Layer 0 disciplines и доставляет
  mandatory practices только для brainstorm/debug-loop.
- `plugins/qtim/agents/architect.toml`, `database.toml`, `frontend.toml` и
  `reviewer.toml` не содержат контракта объёма решения.
- `plugins/qtim/skills/qtim-team-retro/SKILL.md` не собирает `minimal-diff:` markers;
  `qtim-debug-loop/SKILL.md` не требует перед фиксом инвентаризировать все call sites.
- `plugins/qtim/skills/qtim-doctor/SKILL.md` проверяет существование bundled skills,
  но не сопоставляет roster с фактами репозитория.
- `.github/scripts/check_skills.py` уже валидирует совпадение frontmatter `name` с
  каталогом и metadata, но не проверяет общий резолвинг всех `$qtim-*` ссылок. Значит,
  Claude `check_skill_refs.py` нельзя копировать буквально: нужен Codex-native контракт
  без namespace команд.
- `plugins/qtim/THIRD_PARTY_NOTICES.md` содержит notice Matt Pocock, но не содержит
  Dietrich Gebert / ponytail.
- Reference class: порт четырёх disciplines в релизе 2.9.0 затронул 36 файлов
  (792 добавления, 202 удаления); релиз 2.11.0 с generated-state migration и golden
  contract затронул 41 файл. Новый порт уже по changelog пересекает skill, roles,
  setup/update, doctor/retro, CI, golden и release docs.

## Предлагаемый scope

1. **Public discipline contract:** Codex-адаптация `qtim-minimal-diff`, UI metadata,
   attribution и границы с brainstorm/prototype.
2. **Role and generated-state contract:** architect/database/frontend/reviewer templates,
   mandatory practices setup, additive re-run semantics, versioned upgrade notes и golden
   generated state.
3. **Operational feedback loops:** doctor roster audit, retro marker harvesting и
   call-site inventory в debug-loop.
4. **Repository enforcement and release:** skill-reference validation, plugin validation
   coverage, notice, README/CHANGELOG/port map, version bump.

Этот scope предполагает порт всего семантически переносимого релиза 1.13.0, а не только
нового `SKILL.md`.

## Ограничения

- Репозиторий остаётся Codex-native: без `.claude/*`, slash commands, Agent Teams,
  `Task*`, Claude agent-memory и standalone-copy механики.
- Перенос семантический; текст и runtime-specific схемы upstream не копируются.
- Bundled discipline остаётся role-agnostic practice и не получает main-thread fan-out,
  persistent-team assumptions или ownership qtim workflow.
- Generated state сохраняет dev/PM track markers, пользовательский текст вне managed
  regions и атомарные model-pair overrides.
- Изменение generated state требует version bump, `CHANGELOG.md` и новой секции
  `plugins/qtim/reference/upgrade-notes.md`.
- Doctor не меняет roster автоматически; setup не удаляет существующие роли.
- Текущий worktree уже содержит пользовательские untracked `.codex/`, `memory/` и другую
  незавершённую feature-папку; эта фича владеет только своим каталогом документов до
  отдельного запуска реализации.

## Совместимость и обратимость

- Установка нового bundled skill обратимо расширяет plugin surface.
- Старые generated команды продолжают работать без миграции, но не вызывают новую
  дисциплину; `$qtim-update` должен показать scoped diff и оставить неоднозначные
  overrides в `pending`.
- Rollback релиза не должен требовать удаления пользовательских ролей или переписывания
  памяти. Маркеры `minimal-diff:` остаются обычными комментариями, если новый retro
  больше недоступен.

## Non-goals

- Перенос Claude-only синтаксиса, tools/frontmatter, standalone mode или golden layout.
- Перепроектирование `$qtim-mission` и cross-dialog runtime.
- Автоматическое удаление, переименование или создание ролей по результатам doctor.
- Новая продуктовая аналитика: в `memory/product-metrics.md` нет runtime events; success
  проверяется acceptance criteria, generated fixtures и repo-local gates.
- Реализация plugin/source changes внутри PM pipeline.

## Критерии успеха для будущей реализации

- Новый skill проходит ingestion/plugin validation и доступен по точному Codex-имени.
- Все engine-managed ссылки на bundled qtim skills резолвятся; намеренная опечатка валит CI.
- Role templates и golden project согласованно отражают mandatory practice, но reviewer
  не блокирует diff только за рекомендацию по объёму.
- Миграция из 2.12.0 применяется region-by-region, сохраняет foreign/manual content и
  обновляет stamps только после завершения обязательных шагов.
- Doctor выдаёт воспроизводимые warn по roster drift без мутаций.
- Retro различает marker с уже сработавшим trigger и несработавшую заметку; follow-up
  имеет владельца и проверяемый источник.
- Полный repo validation и `validate_plugin.py plugins/qtim` зелёные.

## Предварительная оценка

- Размер: **L**.
- Confidence: **medium-high**.
- Предварительно: **3 проверяемые фазы** — public discipline/roles; generated-state и
  diagnostics/feedback loops; CI/release integration.

Основание: минимум четыре самостоятельные поверхности и две reference classes крупных
портов (2.9.0 и 2.11.0). Точный состав вертикальных work items и layer estimates появится
после PRD и selective architect/testing consult.

## Fork Test

Сработал:

- появляется новая externally visible skill surface;
- меняется публичный контракт обязательных практик ролей;
- меняется generated project state и нужна versioned migration;
- исходную хотелку можно разумно трактовать как «перенести только minimal-diff» или
  «сохранить parity всего релиза 1.13.0».

Не сработали money/billing, data deletion/transformation, authorization boundary и
необратимая runtime migration. Большая часть изменений обратима, но публичная поверхность
и сохранность пользовательских generated-state overrides требуют полного design path.

## Рекомендация по треку

**Полный трек:** `intake.md -> prd.md -> decomposition.md + estimate.md -> plan.md`.

Fast-path недопустим: размер правдоподобно L, фаз больше одной, а Fork Test сработал на
новой внешней поверхности и generated-state contract.

## Решения на checkpoint

1. Scope подтверждён: портировать весь семантически переносимый пакет Claude 1.13.0,
   а не только новый `minimal-diff` skill.
2. Подтверждён полный трек.

Следующая стадия — Draft PRD от `qtim-product`.

## История изменений

- 2026-07-30 — Draft r1: intake собран по upstream changelog/commit 1.13.0,
  текущему Codex 2.12.0, product memory, port map и git reference classes.
- 2026-07-30 — Approved r2: пользователь подтвердил полный семантический scope
  Claude 1.13.0 и полный feature track.
