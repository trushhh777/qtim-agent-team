#!/usr/bin/env python3
"""Validate Codex custom agent TOML templates."""
import pathlib
import re
import sys

try:
    import tomllib  # Python 3.11+
except ImportError:
    tomllib = None

REQUIRED = {"name", "description", "developer_instructions"}
FORBIDDEN = [
    ".claude",
    "CLAUDE_PLUGIN_ROOT",
    "SendMessage",
    "TaskCreate",
    "TaskUpdate",
    "TeamCreate",
    "TeamDelete",
    "team_name",
]

bad = []
root = pathlib.Path("plugins/qtim/agents")

for path in sorted(root.glob("*.toml")):
    text = path.read_text(encoding="utf-8")

    if tomllib is not None:
        try:
            tomllib.loads(text)
        except tomllib.TOMLDecodeError as err:
            bad.append(f"{path}: invalid TOML: {err}")
            continue

    payload = {
        match.group(1): match.group(2).strip()
        for match in re.finditer(r"^([A-Za-z0-9_]+)\s*=\s*(.+)$", text, re.MULTILINE)
    }

    missing = sorted(REQUIRED - payload.keys())
    if missing:
        bad.append(f"{path}: missing required fields: {', '.join(missing)}")

    for key in ("name", "description"):
        value = payload.get(key, "")
        if not re.match(r'^".+"$', value):
            bad.append(f"{path}: `{key}` must be a non-empty string")

    if "developer_instructions = '''" not in text:
        bad.append(f"{path}: `developer_instructions` must be a multiline literal string")
    elif text.count("'''") < 2:
        bad.append(f"{path}: `developer_instructions` multiline string is not closed")

    for token in FORBIDDEN:
        if token in text:
            bad.append(f"{path}: forbidden Claude-only token `{token}`")

    if "../" in text:
        bad.append(
            f"{path}: plugin-relative path (`../`) — шаблон копируется в целевой проект, "
            "где внутренние пути плагина не резолвятся; ссылайся на charter или memory/"
        )

if not list(root.glob("*.toml")):
    bad.append(f"{root}: no Codex custom agent templates found")

if bad:
    print("Codex agent template validation failed:")
    print("\n".join(bad))
    sys.exit(1)

print("OK: Codex custom agent templates are valid")
