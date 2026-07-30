#!/usr/bin/env python3
"""Validate the 2.12 -> 2.13 Extended/custom-role migration contract."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURE = ROOT / ".github/fixtures/update-2.13-extended"
BEFORE = FIXTURE / "before/.codex"
AFTER = FIXTURE / "after/.codex"
BAD = []


def need(condition, message):
    if not condition:
        BAD.append(message)


def text(path):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        BAD.append(f"missing fixture file: {path.relative_to(ROOT)}")
        return ""


def track_block(charter, track):
    match = re.search(
        rf"<!-- qtim:track:{track}:start -->.*?<!-- qtim:track:{track}:end -->",
        charter,
        re.DOTALL,
    )
    return match.group(0) if match else None


def parse_role(body):
    values = {
        match.group(1): match.group(2)
        for match in re.finditer(r'^([A-Za-z0-9_]+)\s*=\s*"([^"]*)"', body, re.MULTILINE)
    }
    instructions = re.search(
        r'^developer_instructions\s*=\s*"""(.*?)"""',
        body,
        re.MULTILINE | re.DOTALL,
    )
    values["developer_instructions"] = instructions.group(1) if instructions else ""
    return values


before_charter = text(BEFORE / "team-charter.md")
after_charter = text(AFTER / "team-charter.md")
need(before_charter.startswith("<!-- qtim-version: 2.12.0 -->"), "before charter stamp mismatch")
need(after_charter.startswith("<!-- qtim-version: 2.13.0 -->"), "after charter stamp mismatch")
for track in ("dev", "pm"):
    need(track_block(before_charter, track) is not None, f"before charter missing {track} track")
    need(
        track_block(before_charter, track) == track_block(after_charter, track),
        f"{track} track was not preserved byte-for-byte",
    )
need(
    "| devops | qtim-devops | Writes deployment and CI code |" in before_charter,
    "fixture does not identify the generated custom role through the charter roster",
)
need(
    "| devops | qtim-devops | Writes deployment and CI code |" in after_charter
    and "$qtim-minimal-diff" in after_charter,
    "after charter does not add minimal-diff to the custom code-writing role cell",
)

before_role_path = BEFORE / "agents/qtim-devops.toml"
after_role_path = AFTER / "agents/qtim-devops.toml"
before_role_text = text(before_role_path)
after_role_text = text(after_role_path)
before_role = parse_role(before_role_text)
after_role = parse_role(after_role_text)
need(before_role.get("developer_instructions"), "before custom role has no multiline instructions")
need(after_role.get("developer_instructions"), "after custom role has no multiline instructions")

need(before_role_text.startswith("# qtim-version: 2.12.0"), "before custom role stamp mismatch")
need(after_role_text.startswith("# qtim-version: 2.13.0"), "after custom role stamp mismatch")
need(before_role.get("name") == after_role.get("name") == "qtim-devops", "custom role name drift")
need(
    (before_role.get("model"), before_role.get("model_reasoning_effort"))
    == (after_role.get("model"), after_role.get("model_reasoning_effort"))
    == ("gpt-5.6-terra", "high"),
    "custom role user model override was not preserved",
)
need(
    "MANUAL-ROLE-TEXT: preserve byte-for-byte." in before_role.get("developer_instructions", "")
    and "MANUAL-ROLE-TEXT: preserve byte-for-byte." in after_role.get("developer_instructions", ""),
    "manual custom-role instruction was not preserved",
)
for marker in (
    "$qtim-minimal-diff",
    "Approved scope",
    "protected zones",
    "disputed scope",
    "одну минимальную breaking check",
    "без новой test infrastructure",
):
    need(marker in after_role.get("developer_instructions", ""), f"custom role missing `{marker}`")

for relative in ("agents/foreign-agent.toml", "hooks.json"):
    before_bytes = (BEFORE / relative).read_bytes() if (BEFORE / relative).is_file() else b""
    after_bytes = (AFTER / relative).read_bytes() if (AFTER / relative).is_file() else b""
    need(before_bytes == after_bytes and before_bytes, f"{relative} was not preserved byte-for-byte")
try:
    json.loads(text(AFTER / "hooks.json"))
except json.JSONDecodeError as err:
    BAD.append(f"after foreign hook fixture is invalid JSON: {err}")

contract_markers = {
    ROOT / "plugins/qtim/skills/qtim-update/SKILL.md": (
        "qtim-generated custom role без bundled template",
        "code-writing role получает только явно описанный",
        "Foreign custom agents не меняй",
        "stamps **всех** однозначно сопоставленных qtim role TOML",
    ),
    ROOT / "plugins/qtim/reference/upgrade-notes.md": (
        "одна charter row",
        "единственный multiline `developer_instructions`",
        "одну минимальную breaking check без новой",
        "charter и все qtim role stamps остаются `2.12.0`",
    ),
    ROOT / "plugins/qtim/skills/qtim-doctor/SKILL.md": (
        "PM-only roster без reviewer/testing не является drift",
        "qtim-generated custom role без bundled template",
        "не считай foreign agent qtim-owned",
    ),
}
for path, markers in contract_markers.items():
    body = text(path)
    for marker in markers:
        need(marker in body, f"{path.relative_to(ROOT)} missing migration marker `{marker}`")

if BAD:
    print("Extended update fixture validation failed:\n- " + "\n- ".join(BAD))
    sys.exit(1)
print("OK: 2.12 -> 2.13 Extended custom-role fixture preserves tracks, foreign state, manual text, and model override")
