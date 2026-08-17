# Карта продукта qtim

## Что является продуктом

qtim — интерактивный Codex plugin для развёртывания и использования project-specific subagent team. Его поверхности — marketplace card, skills, generated project files и lifecycle hooks; web UI и hosted service отсутствуют. Manifest объявляет `Interactive`/`Write`, четыре default prompts и пустой screenshots list: `plugins/qtim/.codex-plugin/plugin.json:20-38`.

## Дерево пользовательских поверхностей

```text
Marketplace / plugin card
└─ Установка и обновление
   ├─ Setup
   │  ├─ Dev track
   │  ├─ PM track
   │  └─ Both
   ├─ Onboarding
   │  ├─ Engineering memory
   │  └─ Product memory
   ├─ Planning
   │  └─ Feature: fast-path или full track
   ├─ Delivery
   │  ├─ Lazy team
   │  └─ Team-up
   ├─ Learning / shutdown
   │  ├─ Retro
   │  └─ Team-down
   └─ Recovery
      ├─ Doctor
      ├─ Update
      └─ Debug loop
```

Marketplace публикует один `qtim` plugin как `AVAILABLE`/`ON_INSTALL`: `.agents/plugins/marketplace.json:2-18`. Skill root и ключевые prompts подтверждены manifest: `plugins/qtim/.codex-plugin/plugin.json:20-35`.

## Journey 1 — установить и загрузить

1. Пользователь добавляет GitHub/local marketplace и устанавливает `qtim`.
2. Открывает новую задачу Codex, потому что уже открытая не подхватывает новые skills.
3. Запускает `$qtim-setup`.

Evidence: `README.md:43-59`.

Обновление: marketplace snapshot -> reinstall -> новая задача -> `$qtim-update` для generated project state. Update сначала показывает installed/project versions, затем plan/diff и ждёт подтверждения: `README.md:61-82`, `plugins/qtim/skills/qtim-update/SKILL.md:17-43`.

Recovery:

- missing charter -> setup;
- project stamp новее plugin -> downgrade запрещён;
- partial migration -> `pending`, stamps остаются на последней полностью применённой версии;
- изменённые hooks требуют `/hooks`, изменённые agents — новой задачи.

Evidence: `plugins/qtim/skills/qtim-update/SKILL.md:12-15,36-53`.

## Journey 2 — настроить команду

1. Setup проводит read-only discovery.
2. Первый выбор: Developer, PM/Analyst или обе роли.
3. Пользователь выбирает autonomy/memory/hooks и видит точный plan.
4. Запись начинается только после подтверждения.
5. Результат: track-aware charter, custom agents, memory baseline, AGENTS pointer и только выбранный optional project hook.

Evidence: `plugins/qtim/skills/qtim-setup/SKILL.md:23-35,68-110,142-184,186-204`.

Re-run обновляет выбранные track markers, сохраняя другой track и ручной текст: `plugins/qtim/skills/qtim-setup/SKILL.md:142-144`.

После setup существующий проект проходит два независимых enrichment journey:

- `$qtim-onboard` -> engineering memory: `plugins/qtim/skills/qtim-onboard/SKILL.md:16-51`;
- `$qtim-product-onboard` -> sections/actors/glossary/metrics: `plugins/qtim/skills/qtim-product-onboard/SKILL.md:20-64`.

Оба требуют подтверждения fan-out; researchers read-only, память синтезирует main thread.

## Journey 3 — превратить хотелку в handoff

`$qtim-feature` не пишет production code; он создаёт requirements/evidence/contracts/gates: `plugins/qtim/skills/qtim-feature/SKILL.md:8-10`.

```text
Intake checkpoint
├─ S/M + 1 phase + no Fork Test
│  └─ feature-brief.md -> one approval -> lazy handoff
└─ L/XL or multi-phase or Fork Test
   └─ prd.md -> approval
      -> decomposition.md + estimate.md -> shared approval
      -> plan.md -> final approval
      -> team-up/lazy handoff
```

Evidence: `plugins/qtim/skills/qtim-feature/SKILL.md:22-24,26-57,59-119`.

Общие outcomes:

- artifacts живут в `docs/features/<slug>/`;
- statuses: `Draft -> Approved -> In Development -> Done`;
- deviations остаются в append-only history;
- `memory/decisions.md` получает только pointer.

Resume: existing slug продолжается с первого незавершённого artifact. Fast-path разворачивается в full, если появляется fork, L/XL или больше одной фазы; конкурирующие plan documents не поддерживаются: `plugins/qtim/skills/qtim-feature/SKILL.md:17-24,53-55`.

## Journey 4 — реализовать

- `$qtim-team-lazy`: несколько concerns, один проход нужных ролей; при rework loop, review block, новой роли или irreversible ambiguity эскалирует в team-up: `plugins/qtim/skills/qtim-team-lazy/SKILL.md:10-18,20-44`.
- `$qtim-team-up`: substantial epic с implement -> test -> fix -> retest -> review loops и reuse доступных task-scoped threads: `plugins/qtim/skills/qtim-team-up/SKILL.md:25-51,93-115`.

Design forks возвращаются пользователю; настоящий ADR до approval проходит clean-context adversary: `plugins/qtim/skills/qtim-team-up/SKILL.md:12-23,95-103`.

Feature-linked delivery переводит brief/plan в `In Development`, после gates — `Done`, сохраняя deviations в history: `plugins/qtim/skills/qtim-team-lazy/SKILL.md:22-29`, `plugins/qtim/skills/qtim-team-up/SKILL.md:105-115`.

## Journey 5 — сохранить уроки и завершить

- `$qtim-team-retro` после C/D опирается на plan/review/bug/history evidence, пишет `retro-log.md` и role-scoped `lessons.md`, возвращает 3–5 уроков и epic metrics: `plugins/qtim/skills/qtim-team-retro/SKILL.md:6-39`.
- `$qtim-team-down` закрывает доступные threads и сохраняет unfinished handoff в `epic-state.md`; completed epic удаляет stale state: `plugins/qtim/skills/qtim-team-down/SKILL.md:6-31`.
- Следующий team-up предлагает продолжить сохранённый state: `plugins/qtim/skills/qtim-team-up/SKILL.md:22`.

## Journey 6 — диагностировать

- `$qtim-doctor` — read-only таблица pass/warn/fail и safe fixes только после подтверждения: `plugins/qtim/skills/qtim-doctor/SKILL.md:6-24`.
- `$qtim-update` — только versioned generated-state migration; plugin install-команды сам не выполняет без просьбы: `plugins/qtim/skills/qtim-update/SKILL.md:25-61`.
- `$qtim-debug-loop` — red signal -> minimal repro -> ranked falsifiable hypotheses -> one-variable probes -> regression test -> fix/cleanup: `plugins/qtim/skills/qtim-debug-loop/SKILL.md:14-59`.

## Явные отсутствующие поверхности

- Нет routes/pages/screens, dashboard, payments или hosted account model; plugin card не содержит screenshots: `plugins/qtim/.codex-plugin/plugin.json:27-38`.
- Нет persistent team entity: team-down закрывает task-scoped threads и сохраняет только durable state: `plugins/qtim/skills/qtim-team-down/SKILL.md:6-18`.
- Project hooks — не general automation UI: lifecycle hooks plugin-bundled, project `PostToolUse` только optional verification reminder: `plugins/qtim/skills/qtim-setup/SKILL.md:170-184`.
