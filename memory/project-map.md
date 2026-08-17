# Карта проекта

## Назначение

`qtim-agent-team` — source-of-truth и deploy point Codex plugin marketplace с одним плагином `qtim`. Основной язык контента — русский.

## Load topology

1. Marketplace публикует локальный `./plugins/qtim`: `.agents/plugins/marketplace.json:2-18`.
2. Manifest фиксирует версию и объявляет `./skills/`: `plugins/qtim/.codex-plugin/plugin.json:2-39`.
3. Skills исполняют workflows, role templates генерируются в target projects, reference-файлы задают общую механику.
4. Plugin layer загружает lifecycle hooks, а project template содержит только optional `PostToolUse`: `plugins/qtim/hooks/hooks.json:3-31`, `plugins/qtim/reference/project-hooks.json:3-18`.
5. `.github/workflows/validate.yml:3-55` проверяет content contracts на PR/push и отдельно выполняет Windows hook validation; application runtime отсутствует.

Подробности: [runtime-contracts.md](runtime-contracts.md), [workflows.md](workflows.md), [model-policy.md](model-policy.md).

## Области и владельцы

| Path | Назначение | Основной владелец |
|---|---|---|
| `.agents/plugins/marketplace.json` | Marketplace entrypoint | Architect / reviewer |
| `plugins/qtim/.codex-plugin/plugin.json` | Manifest, версия, capabilities и skill root | Architect / reviewer |
| `plugins/qtim/skills/` | Setup, feature, team lifecycle, onboard/update и role-agnostic disciplines | Product + architect |
| `plugins/qtim/agents/` | Канонические generic TOML-шаблоны ролей target projects | Architect |
| `plugins/qtim/reference/` | Intake/orchestration/feature/review/model contracts и upgrade notes | Architect |
| `plugins/qtim/hooks/hooks.json` | Plugin-owned `SessionStart` и `SubagentStop` | Architect / testing |
| `.github/scripts/` | Executable content-contract validators | Testing |
| `.github/workflows/validate.yml` | Linux validation и Windows hook runtime check | Testing |
| `README.md`, `CHANGELOG.md` | Пользовательский контракт и release provenance | Product / reviewer |
| `docs/pm-track-backlog.md` | PM research backlog; не источник runtime-инвариантов | Product |
| `docs/claude-port-map.md` | Семантический Codex↔Claude port contract | Architect |
| `.codex/` | Локальная qtim-команда этого репозитория | Team lead |
| `memory/` | Durable проектная память | Team lead |

## Отсутствующие слои

В проекте нет frontend, backend, базы данных, file storage, application runtime, build/typecheck и browser/E2E. Не добавлять требования этих стеков в локальные qtim-роли без появления соответствующего кода.

Plugin templates при этом остаются generic и включают database/frontend роли. Локальный compact roster намеренно содержит только architect/testing/reviewer/product; model defaults generic templates подтверждены `plugins/qtim/reference/model-profiles.md:7-17`.

## Внешний sibling

Claude sibling находится в `../qtim-agent-team-claude` и имеет отдельный git. Codex-репозиторий является источником смысла, но перенос выполняется семантически после чтения актуального upstream, без смешения runtime-терминов: `docs/claude-port-map.md:1-12,50-55`.
