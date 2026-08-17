# Команды проекта

Запускать из корня репозитория.

## Полный validation

```bash
python3 -m json.tool .agents/plugins/marketplace.json > /dev/null
python3 -m json.tool plugins/qtim/.codex-plugin/plugin.json > /dev/null
python3 -m json.tool plugins/qtim/hooks/hooks.json > /dev/null
python3 -m json.tool plugins/qtim/reference/project-hooks.json > /dev/null
python3 .github/scripts/check_hooks.py
python3 .github/scripts/check_placeholders.py
python3 .github/scripts/check_skills.py
python3 .github/scripts/check_links.py
python3 .github/scripts/check_codex_agents.py
```

Назначение:

- четыре `json.tool` проверяют JSON syntax;
- `check_hooks.py` — event sets, matchers, nested command schema, Unix/Windows execution и event-specific JSON output;
- `check_placeholders.py` — восемь разрешённых setup placeholders и баланс braces;
- `check_skills.py` — frontmatter, bundled metadata и cross-document workflow markers;
- `check_links.py` — существование относительных Markdown targets в `plugins/`;
- `check_codex_agents.py` — TOML shape, forbidden tokens, self-contained templates и exact model pairs.

CI выполняет тот же набор и отдельно повторяет `check_hooks.py` на Windows: `.github/workflows/validate.yml:8-55`.

## Release validation

После полного validation и перед release запустить доступный локальный:

```bash
python3 <codex-plugin-creator>/scripts/validate_plugin.py plugins/qtim
```

Не угадывать путь к локальной установке: получить его из текущего Codex runtime.

Локальная среда на 2026-07-27:

- default `python3` не имеет `tomllib`; generated TOML успешно парсится через `python3.12`;
- PyYAML отсутствует у обоих интерпретаторов; `check_skills.py` использует консервативный fallback (`.github/scripts/check_skills.py:4-7,120-121,262`);
- `plugin-creator/scripts/validate_plugin.py` требует PyYAML и без него не стартует. Это pre-release gap среды, а не зелёный результат validator.

## Git/deploy

```bash
git status --short --branch
git diff --check
git push origin main
```

Deploy допускается только после conventional commit и зелёного validation. Application dev/build/typecheck/migrations/E2E команд нет.
