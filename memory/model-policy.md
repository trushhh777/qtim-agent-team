# Model policy

## Default matrix

| Role | Pair |
|---|---|
| Main team-lead | `gpt-5.6-sol` + `ultra` |
| Architect, reviewer | `gpt-5.6-sol` + `xhigh` |
| Database, frontend, product | `gpt-5.6-sol` + `high` |
| Testing | `gpt-5.6-terra` + `medium` |
| Built-in explorer | `gpt-5.6-luna` + `medium` |
| Ephemeral ADR adversary | `gpt-5.6-sol` + `xhigh`; `max` iff irreversible + documented invariant |

Source: `plugins/qtim/reference/model-profiles.md:7-17`. Template exact pairs дополнительно кодируются в `.github/scripts/check_codex_agents.py:13-20,134-155`.

Локальный roster репозитория намеренно исключает database/frontend из `.codex/agents/`, потому что соответствующих application layers нет. Generic plugin templates остаются полным набором.

## Инварианты

- qtim не переключает уже открытую main task; если runtime показывает не Sol/Ultra, fan-out останавливается: `plugins/qtim/reference/model-profiles.md:3,21-26`.
- Profile atomic: `model` и `model_reasoning_effort` вместе; `model = "inherit"` и half-pair невалидны: `plugins/qtim/reference/model-profiles.md:19,28-30`.
- Template pair копируется дословно. Недоступный slug не заменяется guessed alias: после сообщения пользователю используется bounded fallback, а migration остаётся pending: `plugins/qtim/reference/model-profiles.md:30-31`.
- Catalog-supported user override сохраняется до показанного diff; migration fingerprint не перезаписывает его молча: `plugins/qtim/reference/model-profiles.md:32-33`.
- `Ultra` принадлежит team-lead; `max` зарезервирован для clean-context ADR adversary: `plugins/qtim/reference/model-profiles.md:23-26`.

## Исторический reference class

- 2.7 (`634890b`) — первые explicit GPT-5.6 pins.
- 2.9 (`cb911ae`) — inheritance представлен отсутствием обоих полей.
- 2.10 (`c584a16`) — explicit tier-aware pairs возвращены, fallback стал fail-visible; testing сохранил Terra/medium.

Evidence: `docs/claude-port-map.md:45-48`, `CHANGELOG.md:5-24`.

При следующем model-generation upgrade сначала проверить current runtime catalog и official guidance, затем аудитировать compensating recipes, но сохранить structural invariants, risk gates, durable memory и verification contracts: `AGENTS.md:30-32`.
