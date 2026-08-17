# Память qtim

Этот каталог хранит проверенные факты, решения и evidence, которые должны пережить отдельную задачу Codex. Чат и subagent threads не являются durable memory.

## Индекс

- [project-map.md](project-map.md) — карта репозитория и владельцы областей.
- [commands.md](commands.md) — проверенные команды validation и release.
- [safety.md](safety.md) — опасные операции, запреты и release-ограничения.
- [invariants.md](invariants.md) — архитектурные и доменные инварианты.
- [decisions.md](decisions.md) — краткий реестр решений и указателей на утверждённые `docs/features/<slug>/`.
- [runtime-contracts.md](runtime-contracts.md) — load topology, hooks schema/output и границы validation.
- [workflows.md](workflows.md) — state machine skills, feature/team lifecycle и update/resume.
- [model-policy.md](model-policy.md) — role matrix, overrides, fallback и исторические миграции.
- [product-map.md](product-map.md) — пользовательские поверхности и end-to-end journeys qtim.
- [product-actors.md](product-actors.md) — акторы, authority matrix и trust boundaries.
- [product-glossary.md](product-glossary.md) — продуктовые термины, артефакты и состояния.
- [product-metrics.md](product-metrics.md) — реестр аналитики и честно отмеченные measurement gaps.
- [review-report.md](review-report.md) — последний подтверждённый review и история значимых gates.
- [bug-log.md](bug-log.md) — воспроизводимые дефекты, fixes и retest evidence.

Workflows создают по мере надобности:

- `epic-state.md` — handoff незавершённого эпика между задачами (`$qtim-team-down` -> `$qtim-team-up`);
- `retro-log.md` — журнал ретроспектив;
- `lessons.md` — дистиллированные уроки формата trigger -> action.
- `missions/<slug>/` — portable spec, validated/integrated receipts, локальные
  решения и final verification явно запущенной `$qtim-mission`; opaque runtime
  handles живут только в gitignored `.codex/qtim-runtime/`.

## Правила обновления

1. Записывать только проверенные факты, утверждённые решения и воспроизводимое evidence.
2. Ссылаться на точные paths; для code/source findings добавлять `file:line`.
3. Не копировать сюда полный PRD или план: feature artifacts живут в `docs/features/<slug>/`, здесь хранится указатель.
4. Устаревшую запись исправлять с объяснением, а не накапливать противоречащие версии.
