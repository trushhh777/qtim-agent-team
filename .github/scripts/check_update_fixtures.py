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
AMBIGUOUS = FIXTURE / "ambiguous/.codex"
BAD = []
CUSTOM_BLOCK = (
    "\nПеред нетривиальной реализацией пройди `$qtim-minimal-diff`. "
    "Approved scope и protected zones не сокращаются; disputed scope возвращается "
    "main thread. Нетривиальная логика получает одну минимальную breaking check "
    "без новой test infrastructure.\n"
)
BEFORE_CHARTER_CELL = (
    "| devops | qtim-devops | Writes deployment and CI code | "
    "Preserve deployment safety gates |"
)
AFTER_CHARTER_CELL = (
    "| devops | qtim-devops | Writes deployment and CI code | "
    "Preserve deployment safety gates; `$qtim-minimal-diff` before non-trivial implementation |"
)
CUSTOM_MARKERS = (
    "$qtim-minimal-diff",
    "Approved scope",
    "protected zones",
    "disputed scope",
    "одну минимальную breaking check",
    "без новой test infrastructure",
)


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


def custom_role_preserved(before, after):
    if after.count(CUSTOM_BLOCK) != 1:
        return False
    normalized = after.replace("# qtim-version: 2.13.0", "# qtim-version: 2.12.0", 1)
    normalized = normalized.replace(CUSTOM_BLOCK, "", 1)
    return normalized == before


def charter_preserved(before, after):
    if after.count(AFTER_CHARTER_CELL) != 1:
        return False
    normalized = after.replace("<!-- qtim-version: 2.13.0 -->", "<!-- qtim-version: 2.12.0 -->", 1)
    normalized = normalized.replace(AFTER_CHARTER_CELL, BEFORE_CHARTER_CELL, 1)
    return normalized == before


def foreign_bytes_preserved(before, after):
    return bool(before) and before == after


def pending_state_held(charter, roles):
    if not charter.startswith("<!-- qtim-version: 2.12.0 -->"):
        return False
    if "2.13.0" in charter or any("2.13.0" in role for role in roles):
        return False
    if not roles or any(not role.startswith("# qtim-version: 2.12.0") for role in roles):
        return False
    names = [parse_role(role).get("name") for role in roles]
    if names.count("qtim-devops") < 2:
        return False
    return any(
        "$qtim-minimal-diff" in role
        and not all(marker in parse_role(role).get("developer_instructions", "") for marker in CUSTOM_MARKERS)
        for role in roles
    )


before_charter = text(BEFORE / "team-charter.md")
after_charter = text(AFTER / "team-charter.md")
need(before_charter.startswith("<!-- qtim-version: 2.12.0 -->"), "before charter stamp mismatch")
need(after_charter.startswith("<!-- qtim-version: 2.13.0 -->"), "after charter stamp mismatch")
need(
    charter_preserved(before_charter, after_charter),
    "charter changed outside the target stamp and one mandatory-practice cell",
)
for track in ("dev", "pm"):
    need(track_block(before_charter, track) is not None, f"before charter missing {track} track")
    need(
        track_block(before_charter, track) == track_block(after_charter, track),
        f"{track} track was not preserved byte-for-byte",
    )
need(
    BEFORE_CHARTER_CELL in before_charter,
    "fixture does not identify the generated custom role through the charter roster",
)
need(
    AFTER_CHARTER_CELL in after_charter,
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
need(
    custom_role_preserved(before_role_text, after_role_text),
    "custom role changed outside the target stamp and one exact additive minimal-diff block",
)
need(before_role.get("name") == after_role.get("name") == "qtim-devops", "custom role name drift")
need(
    (before_role.get("model"), before_role.get("model_reasoning_effort"))
    == (after_role.get("model"), after_role.get("model_reasoning_effort"))
    == ("gpt-5.6-terra", "high"),
    "custom role user model override was not preserved",
)
for marker in CUSTOM_MARKERS:
    need(marker in after_role.get("developer_instructions", ""), f"custom role missing `{marker}`")

for relative in ("agents/foreign-agent.toml", "agents/qtim-foreign-near-miss.toml", "hooks.json"):
    before_bytes = (BEFORE / relative).read_bytes() if (BEFORE / relative).is_file() else b""
    after_bytes = (AFTER / relative).read_bytes() if (AFTER / relative).is_file() else b""
    need(foreign_bytes_preserved(before_bytes, after_bytes), f"{relative} was not preserved byte-for-byte")
try:
    json.loads(text(AFTER / "hooks.json"))
except json.JSONDecodeError as err:
    BAD.append(f"after foreign hook fixture is invalid JSON: {err}")

ambiguous_charter = text(AMBIGUOUS / "team-charter.md")
ambiguous_roles = [
    text(path) for path in sorted((AMBIGUOUS / "agents").glob("qtim-devops*.toml"))
]
need(
    pending_state_held(ambiguous_charter, ambiguous_roles),
    "ambiguous/partial custom-role fixture did not hold charter and all qtim stamps at 2.12.0",
)

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

if "--self-test" in sys.argv[1:]:
    manual_loss = after_role_text.replace(
        "Change deployment and CI code only inside the approved scope.\n",
        "",
        1,
    )
    need(
        not custom_role_preserved(before_role_text, manual_loss),
        "negative oracle accepted deleted manual custom-role instruction",
    )
    changed_manual = after_role_text.replace(
        "MANUAL-ROLE-TEXT: preserve byte-for-byte.",
        "MANUAL-ROLE-TEXT: silently changed.",
        1,
    )
    need(
        not custom_role_preserved(before_role_text, changed_manual),
        "negative oracle accepted changed manual custom-role instruction",
    )
    before_near_miss = text(BEFORE / "agents/qtim-foreign-near-miss.toml")
    after_near_miss = text(AFTER / "agents/qtim-foreign-near-miss.toml")
    mutated_near_miss = after_near_miss.replace(
        "FOREIGN-QTIM-LOOKING-BYTES-MUST-NOT-CHANGE",
        "mutated",
        1,
    )
    need(before_near_miss == after_near_miss, "near-miss control fixture is not identical")
    need(
        not foreign_bytes_preserved(
            before_near_miss.encode("utf-8"),
            mutated_near_miss.encode("utf-8"),
        ),
        "negative oracle accepted mutation of qtim-looking foreign near-miss",
    )
    advanced_charter = ambiguous_charter.replace(
        "<!-- qtim-version: 2.12.0 -->",
        "<!-- qtim-version: 2.13.0 -->",
        1,
    )
    advanced_role = ambiguous_roles[0].replace(
        "# qtim-version: 2.12.0",
        "# qtim-version: 2.13.0",
        1,
    )
    need(
        not pending_state_held(advanced_charter, ambiguous_roles),
        "negative oracle accepted target charter stamp for ambiguous custom role",
    )
    need(
        not pending_state_held(ambiguous_charter, [advanced_role, *ambiguous_roles[1:]]),
        "negative oracle accepted target role stamp for partial custom region",
    )

if BAD:
    print("Extended update fixture validation failed:\n- " + "\n- ".join(BAD))
    sys.exit(1)
if "--self-test" in sys.argv[1:]:
    print("OK: update-fixture negative oracles reject manual loss, foreign near-miss mutation, and ambiguous target stamps")
else:
    print("OK: 2.12 -> 2.13 Extended custom-role fixture preserves all non-target bytes and holds ambiguous state at 2.12.0")
