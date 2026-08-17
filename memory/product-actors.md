# Акторы, authority и trust

## Пользовательские режимы

| Актор | Цель | Что получает | Evidence |
|---|---|---|---|
| Developer | Реализовать изменение через специализированные роли | Dev track и lazy/team-up workflows | `plugins/qtim/skills/qtim-setup/SKILL.md:72-76` |
| PM/Analyst | Превратить идею в grounded handoff без написания production code | Product role, fast/full feature pipeline, `docs/features/` | `plugins/qtim/skills/qtim-setup/SKILL.md:72-90`, `plugins/qtim/skills/qtim-feature/SKILL.md:8-24` |
| Both | Планировать и реализовывать в одном проекте | Оба track blocks и объединённый roster | `plugins/qtim/skills/qtim-setup/SKILL.md:72-78,168` |
| Project owner / decision owner | Задать intent, scope и допустимый риск | Checkpoints и финальный handoff | `plugins/qtim/reference/intake-protocol.md:17-30,32-48` |

PM-only roster предназначен для документов и consult; перед mode D implementation нужен dev track с reviewer: `plugins/qtim/skills/qtim-setup/SKILL.md:90`, `plugins/qtim/skills/qtim-feature/SKILL.md:117-119`.

## Командные акторы

| Актор | Решает | Читает | Пишет | Spawn / approval boundary |
|---|---|---|---|---|
| Main team-lead | Execution depth, routing, synthesis и проверка evidence | Charter, code, memory, artifacts | Durable memory и main-thread synthesis | Единственный владелец fan-out; не заменяет user approval |
| Product | Формулирует intake/PRD, сводит grounded decomposition/estimate/plan | Product memory, feature artifacts, consult evidence | `docs/features/<slug>/` artifacts | Не пишет production code и возвращает product forks пользователю |
| Architect | Design/ADR и role-scoped decomposition | Invariants, decisions, code evidence | Docs/specs/memory в своём scope | Сам не запускает ADR adversary; draft возвращает main |
| Layer roles | Bounded technical choice своего слоя | Затронутый source и memory | Только свой согласованный write scope | Не создают рекурсивную qtim team |
| Testing | Reproduction и verification evidence | Test surface, commands, artifacts | Tests/fixtures и bug evidence | App fix маршрутизирует владельцу |
| Reviewer | Технический verdict `APPROVED`/`NOT APPROVED` | Diff, gates, invariants, evidence | Production code не пишет | Quality verdict не заменяет продуктовый checkpoint |
| Explorer | Read-heavy поиск/классификация | Только bounded context | Не пишет | Spawn main thread; output advisory |
| Independent reviewer / ADR adversary | Read-only findings | Узкий clean context | Не пишет | Не approves; main проверяет findings, architect обновляет ADR |

Evidence: `plugins/qtim/agents/product.toml:18-24,38-50`, `plugins/qtim/agents/architect.toml:18-36,51-62`, `plugins/qtim/agents/reviewer.toml:17-58`, `plugins/qtim/reference/model-profiles.md:16,23-31`, `plugins/qtim/reference/independent-review.md:14-27`.

## Решения пользователя

Пользователь остаётся в контуре для:

- setup plan и любых collisions;
- onboard researcher scope;
- Intake track и feature checkpoints;
- irreversible/ambiguous/product-visible/public-contract/security/money/migration forks;
- migration diff и model override;
- hook trust через `/hooks`.

Evidence: `plugins/qtim/skills/qtim-setup/SKILL.md:96-110`, `plugins/qtim/skills/qtim-product-onboard/SKILL.md:26-40`, `plugins/qtim/skills/qtim-feature/SKILL.md:26-39,53,63,78,94`, `plugins/qtim/reference/intake-protocol.md:32-48`, `plugins/qtim/skills/qtim-update/SKILL.md:36-43`, `plugins/qtim/skills/qtim-setup/SKILL.md:184`.

## Authority boundaries

- Workflow invocation или прямая просьба разрешает только bounded subagent scope; `Ultra` не расширяет задачу: `plugins/qtim/reference/model-profiles.md:23-25`.
- Main владеет agent graph; child agents запрашивают дополнительную роль у main и не спавнят descendants: `plugins/qtim/reference/orchestration-patterns.md:20-25,127-135`.
- Subagent/reviewer output — evidence, не истина; main открывает source и проверяет finding: `plugins/qtim/reference/independent-review.md:3-12,64-70`.
- Reviewer verdict — quality gate. User approval отдельно требуется для decision forks: `plugins/qtim/agents/reviewer.toml:17,43-58`, `plugins/qtim/reference/intake-protocol.md:26`.

## Install и hook trust

- Marketplace `AVAILABLE` + `ON_INSTALL` описывает установку/аутентификацию plugin connector, а не application RBAC: `.agents/plugins/marketplace.json:13-17`.
- Manifest объявляет capability `Write`, поэтому setup/feature/team workflows могут создавать project artifacts только в рамках явного workflow: `plugins/qtim/.codex-plugin/plugin.json:27-35`.
- Plugin owns `SessionStart`/`SubagentStop`; project `PostToolUse` optional. Изменённые hooks требуют review/trust через `/hooks`: `plugins/qtim/skills/qtim-setup/SKILL.md:170-184`.
- `SubagentStop` напоминает main проверить реальные файлы/отчёты/memory/logs, а не доверять сообщению agent thread: `plugins/qtim/hooks/hooks.json:18-30`.

## Отсутствующая application-модель

У самого qtim нет зарегистрированных пользователей, tenant IDs, application RBAC, auth provider или domain permissions. `security/auth/tenant-scope visibility` — generic review trigger для target projects, не доказательство такой модели внутри plugin: `plugins/qtim/reference/independent-review.md:29-44`.

Любые конкретные customer/admin/member permissions для будущего target project должны быть обнаружены из его source или записаны как гипотеза; product-onboard прямо запрещает неподтверждённые факты: `plugins/qtim/skills/qtim-product-onboard/SKILL.md:34-40,52-63`.

## Maintainer

Manifest называет автора/developer Антона Фокина; repository/homepage указывают на GitHub source: `plugins/qtim/.codex-plugin/plugin.json:5-9,21-26`. Maintainer управляет release source, но не получает скрытой authority внутри пользовательского project workflow.
