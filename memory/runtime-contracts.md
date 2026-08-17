# Runtime и validation contracts

## Packaging

- Marketplace entrypoint публикует `qtim` из `./plugins/qtim`: `.agents/plugins/marketplace.json:2-18`.
- Plugin manifest содержит version, capabilities и skill root `./skills/`: `plugins/qtim/.codex-plugin/plugin.json:2-39`.
- Приложение, build и server runtime отсутствуют; исполняемые части репозитория — hooks и Python validators.

## Hook layers

| Layer | Events | Canonical matcher | Evidence |
|---|---|---|---|
| Plugin | `SessionStart`, `SubagentStop` | `startup\|resume\|clear\|compact`, `*` | `.github/scripts/check_hooks.py:34-45` |
| Project template | `PostToolUse` | `Edit\|Write\|apply_patch` | `.github/scripts/check_hooks.py:34-45` |

Canonical file содержит ровно ожидаемый event set, один matcher group и один `type: command` handler: `.github/scripts/check_hooks.py:87-152`.

Bundled hooks:

- ищут `.codex/team-charter.md` от Git root и молчат без него;
- `SessionStart` перечисляет максимум пять unfinished mission как passive advisory
  и никогда не вызывает resume/create/archive;
- Windows commands используют literal leaf path и UTF-8;
- `SubagentStop` печатает только UTF-8 JSON с непустым `systemMessage`.

Evidence: `plugins/qtim/hooks/hooks.json:3-31`, `.github/scripts/check_hooks.py:186-223,291-378`.

Project `PostToolUse` возвращает только JSON `hookSpecificOutput` с `hookEventName: PostToolUse` и непустым `additionalContext`: `plugins/qtim/reference/project-hooks.json:3-18`, `.github/scripts/check_hooks.py:380-417`. Plain stdout не выполняет contract.

## Validators

| Validator | Что реально кодирует |
|---|---|
| `check_hooks.py` | Exact event sets/matchers, nested schema, allowlisted keys, Unix/Windows execution и JSON output |
| `check_placeholders.py` | Allowlisted setup placeholders и отсутствие деформированных/несбалансированных braces |
| `check_skills.py` | SKILL frontmatter, bundled attribution/metadata и cross-document workflow markers |
| `check_missions.py` | Activation/routing, DAG edge contracts, state transitions, writer/lazy receipts, recovery classes и full mission markers |
| `check_links.py` | Существование относительных Markdown target paths в `plugins/` |
| `check_codex_agents.py` | Required TOML fields, multiline instructions, forbidden tokens/paths, exact role pairs и discipline markers |

Evidence: `.github/scripts/check_placeholders.py:12-43`, `.github/scripts/check_skills.py:20-134`, `.github/scripts/check_links.py:8-18`, `.github/scripts/check_codex_agents.py:12-20,84-155`.

## Известные пределы проверки

- CI ставит PyYAML best-effort (`|| true`); fallback parser намеренно консервативен: `.github/workflows/validate.yml:38-41`, `.github/scripts/check_skills.py:4-7,120-121,262`.
- `check_links.py` отбрасывает `#fragment` и проверяет только path, поэтому anchor existence остаётся вне gate: `.github/scripts/check_links.py:10-17`.
- `validate_plugin.py plugins/qtim` — отдельный pre-release gate и не входит в показанные CI jobs: `AGENTS.md:57`, `.github/workflows/validate.yml:8-55`.
- Scoped search 2026-07-27 не обнаружил literal `TODO`, `FIXME` или `HACK` в manifests/hooks/validators/CI.
