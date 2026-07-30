#!/usr/bin/env python3
"""Fail closed when engine-managed `$qtim-*` references do not resolve.

`check_skills.py` is the single owner of frontmatter-name ↔ directory
validation. This checker owns only cross-surface resolution, full-token
matching, required scan surfaces, and non-zero coverage.
"""

import argparse
import pathlib
import re
import sys
import tempfile

DEFAULT_ROOT = pathlib.Path(__file__).resolve().parents[2]
REF_RE = re.compile(r"(?<![A-Za-z0-9_-])\$qtim-([A-Za-z0-9_-]+)")
TEXT_SUFFIXES = {".md", ".toml", ".json", ".yaml", ".yml", ".sh", ".py"}
REQUIRED_DIRS = (
    "plugins/qtim/skills",
    "plugins/qtim/agents",
    "plugins/qtim/reference",
    "examples/fullstack-codex",
)
REQUIRED_FILES = (
    "README.md",
    "CHANGELOG.md",
    "AGENTS.md",
    "docs/claude-port-map.md",
)


def skill_names(root, problems):
    skills_dir = root / "plugins/qtim/skills"
    if not skills_dir.is_dir():
        return set()

    names = set()
    for skill_dir in sorted(path for path in skills_dir.iterdir() if path.is_dir()):
        manifest = skill_dir / "SKILL.md"
        if not manifest.is_file():
            problems.append(f"{manifest.relative_to(root)}: missing SKILL.md")
            continue
        names.add(skill_dir.name)
    if not names:
        problems.append("plugins/qtim/skills: no bundled skills found")
    return names


def scan_files(root, problems):
    for relative in REQUIRED_DIRS:
        path = root / relative
        if not path.is_dir():
            problems.append(f"{relative}: required scan surface is missing")

    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.is_file():
            problems.append(f"{relative}: required scan surface is missing")

    seen = set()
    for relative in ("plugins/qtim", "examples/fullstack-codex"):
        base = root / relative
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                seen.add(path)

    for relative in REQUIRED_FILES:
        path = root / relative
        if path.is_file():
            seen.add(path)

    return sorted(seen)


def validate(root):
    root = root.resolve()
    problems = []
    skills = skill_names(root, problems)
    checked = 0

    for path in scan_files(root, problems):
        text = path.read_text(encoding="utf-8")
        for match in REF_RE.finditer(text):
            checked += 1
            full_name = f"qtim-{match.group(1)}"
            if full_name in skills:
                continue
            line = text.count("\n", 0, match.start()) + 1
            problems.append(
                f"{path.relative_to(root)}:{line}: `${full_name}` does not resolve "
                f"to plugins/qtim/skills/{full_name}/"
            )

    if checked == 0:
        problems.append(
            "checked 0 `$qtim-*` references: scan coverage or reference style "
            "degraded silently"
        )

    return problems, len(skills), checked


def build_fixture(root, reference="$qtim-alpha", missing_surface=None):
    for relative in REQUIRED_DIRS:
        if relative != missing_surface:
            (root / relative).mkdir(parents=True, exist_ok=True)
    for relative in REQUIRED_FILES:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# fixture\n", encoding="utf-8")

    skill = root / "plugins/qtim/skills/qtim-alpha/SKILL.md"
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text(
        "---\nname: qtim-alpha\ndescription: fixture\n---\n",
        encoding="utf-8",
    )
    if reference is not None:
        target = root / "plugins/qtim/agents/fixture.toml"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f'prompt = "{reference}"\n', encoding="utf-8")


def self_test():
    cases = (
        ("valid", "$qtim-alpha", None, False, None),
        ("unknown name", "$qtim-missing", None, True, "does not resolve"),
        ("invalid suffix", "$qtim-alpha_typo", None, True, "does not resolve"),
        ("zero coverage", None, None, True, "checked 0"),
        (
            "missing surface",
            "$qtim-alpha",
            "examples/fullstack-codex",
            True,
            "required scan surface is missing",
        ),
    )
    failures = []
    for label, reference, missing, should_fail, expected in cases:
        with tempfile.TemporaryDirectory(prefix="qtim-skill-refs-") as temp:
            root = pathlib.Path(temp)
            build_fixture(root, reference=reference, missing_surface=missing)
            problems, _, _ = validate(root)
        if should_fail and not problems:
            failures.append(f"{label}: expected failure, got pass")
        elif not should_fail and problems:
            failures.append(f"{label}: expected pass, got {problems}")
        elif expected and not any(expected in problem for problem in problems):
            failures.append(f"{label}: expected marker `{expected}`, got {problems}")

    if failures:
        print("Skill-reference self-test failed:\n- " + "\n- ".join(failures))
        return 1
    print("OK: skill-reference negative fixtures reject typo/suffix/zero/missing surface")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=pathlib.Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    problems, skill_count, checked = validate(args.root)
    if problems:
        print("Skill-reference validation failed:\n- " + "\n- ".join(problems))
        return 1
    print(
        f"OK: {checked} `$qtim-*` references resolve across required surfaces "
        f"to {skill_count} bundled skills"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
