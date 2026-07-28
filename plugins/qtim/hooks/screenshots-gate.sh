#!/bin/sh
# Opt-in SubagentStop gate. No config means no-op; stop_hook_active prevents loops.
python3 -c '
import json, pathlib, subprocess, sys, time
try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if payload.get("stop_hook_active") is True:
    sys.exit(0)
try:
    root = pathlib.Path(subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True,
        stderr=subprocess.DEVNULL).strip())
except Exception:
    root = pathlib.Path.cwd()
if not (root / ".codex" / "team-charter.md").is_file():
    sys.exit(0)
config_path = root / ".codex" / "screenshots-gate.json"
if not config_path.is_file():
    sys.exit(0)
try:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    directory = pathlib.PurePosixPath(config["directory"])
    minutes = int(config.get("freshnessMinutes", 180))
except Exception as exc:
    print(f"qtim screenshot gate: invalid .codex/screenshots-gate.json: {exc}", file=sys.stderr)
    sys.exit(2)
if config.get("mode") != "blocking":
    sys.exit(0)
if directory.is_absolute() or ".." in directory.parts or minutes <= 0:
    print("qtim screenshot gate: directory must be safe repo-relative and freshnessMinutes > 0", file=sys.stderr)
    sys.exit(2)
target = root.joinpath(*directory.parts)
cutoff = time.time() - minutes * 60
extensions = {".png", ".jpg", ".jpeg", ".webp"}
fresh = any(
    path.is_file()
    and path.suffix.lower() in extensions
    and not path.name.startswith("front-selfcheck-")
    and path.stat().st_mtime >= cutoff
    for path in (target.rglob("*") if target.is_dir() else ())
)
if fresh:
    sys.exit(0)
print(
    f"qtim screenshot gate: no fresh tester screenshots in {directory}. "
    "Run the real-browser sweep and save PNG/JPG/WEBP evidence; if UI is objectively N/A, "
    "state that explicitly and finish once more.",
    file=sys.stderr,
)
sys.exit(2)
'
