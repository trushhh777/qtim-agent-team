#!/usr/bin/env python3
"""Frontmatter каждого SKILL.md валиден и совместим с plugin ingestion.

Использует PyYAML, если он установлен; иначе — консервативный fallback-парсер,
который ловит главный класс ошибок: незакавыченный скаляр с `: ` внутри
(ровно то, что роняет ingestion-валидатор Codex). Авторитетная проверка —
validate_plugin.py из Codex plugin-creator.
"""
import pathlib
import re
import sys

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")

bad = []


def parse_fallback(path, body):
    """Строгое подмножество YAML: однострочные `key: value`, plain или в кавычках."""
    data = {}
    for line in body.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = KEY_RE.match(line)
        if m is None:
            bad.append(f"{path}: строка не является простой парой key: value: `{line}`")
            continue
        key, value = m.group(1), m.group(2).strip()
        if value.startswith(('"', "'")):
            if len(value) < 2 or value[-1] != value[0]:
                bad.append(f"{path}: незакрытая кавычка в `{key}`")
                continue
            value = value[1:-1]
        elif ": " in value or value.endswith(":"):
            bad.append(
                f"{path}: `{key}` содержит `: ` в незакавыченном значении — "
                "невалидный YAML для ingestion, возьми значение в кавычки"
            )
            continue
        data[key] = value
    return data


for skill_dir in sorted(pathlib.Path("plugins").glob("*/skills/*")):
    if not skill_dir.is_dir() or skill_dir.name.startswith("."):
        continue
    path = skill_dir / "SKILL.md"
    if not path.is_file():
        bad.append(f"{skill_dir}: нет SKILL.md")
        continue
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        bad.append(f"{path}: должен начинаться с YAML frontmatter")
        continue
    end = text.find("\n---", 4)
    if end == -1:
        bad.append(f"{path}: frontmatter не закрыт")
        continue
    body = text[4:end]
    if yaml is not None:
        try:
            data = yaml.safe_load(body)
        except yaml.YAMLError as err:
            bad.append(f"{path}: невалидный YAML frontmatter: {err}")
            continue
        if not isinstance(data, dict):
            bad.append(f"{path}: frontmatter должен быть YAML-объектом")
            continue
    else:
        data = parse_fallback(path, body)
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        bad.append(f"{path}: `name` должен быть непустой строкой")
    elif name != skill_dir.name:
        bad.append(f"{path}: `name` ({name}) не совпадает с директорией ({skill_dir.name})")
    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        bad.append(f"{path}: `description` должен быть непустой строкой")

if bad:
    print("Skill frontmatter validation failed:")
    print("\n".join(bad))
    sys.exit(1)

mode = "PyYAML" if yaml is not None else "fallback-парсер (PyYAML не установлен)"
print(f"OK: frontmatter всех SKILL.md валиден ({mode})")
