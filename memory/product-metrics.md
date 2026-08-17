# Продуктовые метрики и instrumentation

## Текущий реестр

| Категория | Подтверждённое состояние |
|---|---|
| Analytics events | Нет подтверждённых runtime tracking calls или event schema |
| Feature flags | Нет подтверждённого flag provider или реестра flags |
| Тарифы / subscription limits | Нет продуктовой billing/subscription модели |
| `docs/product-context/` | Каталог отсутствует; интервью, тикеты и metric exports не предоставлены |

Основание: repository-wide inventory 2026-07-27 по `analytics`, `track`, `gtag`, `metrika`, `segment`, `amplitude`, `mixpanel`, `posthog`, `feature flag`, тарифам/subscription не нашёл implementation substrate. Найденные упоминания описывают generic product-onboard/review policy и открытый будущий metrics loop, а не события qtim: `plugins/qtim/skills/qtim-product-onboard/SKILL.md:34-40,47-54`, `docs/pm-track-backlog.md:119-123`.

## Правило для PRD

Product role связывает success metrics только с реальными событиями из этого файла. Отсутствующее событие оформляется как tracking work item, а не выдаётся за существующий факт: `plugins/qtim/skills/qtim-feature/SKILL.md:59-64`, `plugins/qtim/agents/product.toml:48-50`.

Пока registry пуст, `$qtim-feature` должен:

1. формулировать желаемый outcome и способ ручной проверки;
2. явно отмечать measurement gap;
3. при необходимости добавлять instrumentation в scope;
4. не обещать post-release metric evaluation без источника данных.

## Доступные operational proxies — не продуктовая аналитика

Эти сигналы помогают проверить процесс, но не измеряют adoption/value:

| Proxy | Что подтверждает | Source |
|---|---|---|
| Feature artifact status/history | Прохождение checkpoints и отклонения реализации | `plugins/qtim/reference/feature-pipeline.md:27-38,94-100` |
| `memory/review-report.md` | Quality verdict и independent-review evidence | `plugins/qtim/reference/independent-review.md:64-70` |
| `memory/bug-log.md` | Reproduction/fix/retest evidence | `plugins/qtim/skills/qtim-debug-loop/SKILL.md:47-59` |
| `retro-log.md` / `lessons.md` | Повторяющиеся coordination patterns после C/D | `plugins/qtim/skills/qtim-team-retro/SKILL.md:28-39` |
| Version stamp / changelog | Installed/generated-state evolution, не usage | `plugins/qtim/skills/qtim-update/SKILL.md:10-23`, `CHANGELOG.md:1-7` |

## Кандидаты на будущую instrumentation

Это гипотезы для discovery, а не текущие события:

- funnel `installed -> setup confirmed -> onboard completed -> first workflow`;
- доля fast/full feature paths и completion до handoff;
- время/число возвратов между checkpoints;
- escalation lazy -> team-up и число fix/retest loops;
- доля migrations с `pending`, model fallback и hook trust issues;
- post-release PRD/actual reconciliation и accepted-vs-rejected review findings.

Перед реализацией нужны решения о privacy, opt-in, storage, actor identity и источнике данных. PM backlog уже отмечает post-release metrics loop как open opportunity с низкой confidence из-за необходимости доступа к аналитике: `docs/pm-track-backlog.md:119-123,131-135`.
