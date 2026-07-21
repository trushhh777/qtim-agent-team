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
EXPECTED_MODEL_POLICIES = {
    "architect.toml": (None, None),
    "database.toml": (None, None),
    "frontend.toml": (None, None),
    "product.toml": (None, None),
    "reviewer.toml": (None, None),
    "testing.toml": ("gpt-5.6-terra", "medium"),
}
EXPECTED_MARKERS = {
    "architect.toml": [
        "$qtim-brainstorm",
        "$qtim-prototype",
        "$qtim-grill",
        "дорого откатить",
        "будущий читатель",
        "реальный trade-off",
        "expand-contract",
    ],
    "database.toml": ["$qtim-debug-loop"],
    "frontend.toml": ["$qtim-debug-loop"],
    "product.toml": ["вертикальный срез", "DRI", "contributing", "expand-contract"],
    "reviewer.toml": [
        "Canonical high-risk matrix",
        "обязательный запрос",
        "skipped (low-risk diff)",
    ],
    "testing.toml": ["$qtim-debug-loop"],
}
REASONING_EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
MODEL_REASONING_EFFORTS = {
    "gpt-5.6-sol": {"low", "medium", "high", "xhigh", "max", "ultra"},
    "gpt-5.6-terra": {"low", "medium", "high", "xhigh", "max", "ultra"},
    "gpt-5.6-luna": {"low", "medium", "high", "xhigh", "max"},
    "gpt-5.5": {"low", "medium", "high", "xhigh"},
    "gpt-5.4": {"low", "medium", "high", "xhigh"},
    "gpt-5.4-mini": {"low", "medium", "high", "xhigh"},
    "gpt-5.3-codex-spark": {"low", "medium", "high", "xhigh"},
}
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
paths = sorted(root.glob("*.toml"))

for path in paths:
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

    m = re.search(r'^model\s*=\s*"([^"]*)"', text, re.MULTILINE)
    if m and not re.fullmatch(r"gpt-\d+\.\d+(-[a-z0-9-]+)?", m.group(1)):
        bad.append(
            f"{path}: `model = \"{m.group(1)}\"` — слаг без минорной версии или не gpt-семейство; "
            "боевой инцидент: `gpt-5` не существует, субагенты не стартуют"
        )

    reasoning = re.search(
        r'^model_reasoning_effort\s*=\s*"([^"]*)"', text, re.MULTILINE
    )
    if bool(m) != bool(reasoning):
        bad.append(
            f"{path}: `model` and `model_reasoning_effort` must be present together or both omitted"
        )
    if reasoning and reasoning.group(1) not in REASONING_EFFORTS:
        bad.append(
            f"{path}: unsupported `model_reasoning_effort = \"{reasoning.group(1)}\"`"
        )

    supported_efforts = MODEL_REASONING_EFFORTS.get(m.group(1)) if m else None
    if reasoning and supported_efforts and reasoning.group(1) not in supported_efforts:
        bad.append(
            f"{path}: `{m.group(1)}` does not support reasoning effort "
            f"`{reasoning.group(1)}`"
        )

    expected = EXPECTED_MODEL_POLICIES.get(path.name)
    if expected:
        actual = (
            m.group(1) if m else None,
            reasoning.group(1) if reasoning else None,
        )
        if actual != expected:
            bad.append(
                f"{path}: expected qtim model policy {expected[0]}/{expected[1]}, "
                f"found {actual[0]}/{actual[1]}"
            )

    for marker in EXPECTED_MARKERS.get(path.name, []):
        if marker not in text:
            bad.append(f"{path}: missing qtim 2.9 discipline marker `{marker}`")

if not paths:
    bad.append(f"{root}: no Codex custom agent templates found")

missing_templates = sorted(set(EXPECTED_MODEL_POLICIES) - {path.name for path in paths})
if missing_templates:
    bad.append(f"{root}: missing expected templates: {', '.join(missing_templates)}")

if bad:
    print("Codex agent template validation failed:")
    print("\n".join(bad))
    sys.exit(1)

print("OK: Codex custom agent templates are valid")
