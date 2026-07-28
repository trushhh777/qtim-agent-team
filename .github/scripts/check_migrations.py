#!/usr/bin/env python3
"""Fail when generated-state producers change without a versioned migration."""
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def git(*args):
    return subprocess.run(
        ["git", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False
    )


def resolve_base():
    candidates = [
        os.environ.get("CHECK_MIGRATIONS_BASE"),
        sys.argv[1] if len(sys.argv) > 1 else None,
        "origin/main",
        "HEAD",
    ]
    for candidate in candidates:
        if not candidate or set(candidate) == {"0"}:
            continue
        probe = git("rev-parse", "--verify", candidate)
        if probe.returncode == 0:
            return candidate
    raise SystemExit("Migration gate: no resolvable base revision")


base = resolve_base()
changed = set(git("diff", "--name-only", base, "--").stdout.splitlines())
changed.update(git("ls-files", "--others", "--exclude-standard").stdout.splitlines())
producer_change = any(
    path.startswith("plugins/qtim/agents/")
    or path == "plugins/qtim/reference/project-hooks.json"
    for path in changed
)
setup_path = "plugins/qtim/skills/qtim-setup/SKILL.md"
base_setup = git("show", f"{base}:{setup_path}").stdout
current_setup = (ROOT / setup_path).read_text(encoding="utf-8")


def generation_section(text):
    start = text.find("## Phase 4: Generation")
    end = text.find("## Phase 5:", start)
    return text[start:end] if start >= 0 and end > start else None


if generation_section(base_setup) != generation_section(current_setup):
    producer_change = True

if not producer_change:
    print(f"OK: no generated-state producer changes against {base}")
    raise SystemExit(0)

manifest_path = "plugins/qtim/.codex-plugin/plugin.json"
current = json.loads((ROOT / manifest_path).read_text(encoding="utf-8"))["version"]
old_raw = git("show", f"{base}:{manifest_path}")
if old_raw.returncode != 0:
    raise SystemExit(f"Migration gate: cannot read base manifest at {base}")
old = json.loads(old_raw.stdout)["version"]

errors = []
if current == old:
    errors.append(f"plugin version was not bumped from {old}")
for path in ("CHANGELOG.md", "plugins/qtim/reference/upgrade-notes.md"):
    if path not in changed:
        errors.append(f"{path} was not changed")
    elif f"## {current}" not in (ROOT / path).read_text(encoding="utf-8"):
        errors.append(f"{path} has no `## {current}` section")
if errors:
    print("Migration gate failed:\n- " + "\n- ".join(errors))
    raise SystemExit(1)
print(f"OK: generated-state change has version {old} -> {current} and migration notes")
