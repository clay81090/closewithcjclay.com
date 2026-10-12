#!/bin/zsh
# Starts the Resale build. Claude writes the app. This script puts back anything
# it changes outside resale/, and restores the plan, seed, and site memory.
set -u
ROOT="/Users/charlesclay/closewithcjclay.com"
cd "$ROOT" || exit 1

echo ""
echo "CJ Resale build"
echo "Claude will write the app inside resale/."
echo "It is not allowed to commit. If it touches anything else, this script puts it back."
echo ""

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude is not available in this terminal. Stop and tell Cursor."
  exit 1
fi

GUARD="$(mktemp -d /tmp/cj-resale-guard.XXXXXX)"
git status --porcelain -u > "$GUARD/before.txt"
mkdir -p "$GUARD/copy/memory" "$GUARD/copy/seed"
cp "$ROOT/resale/PLAN.md" "$ROOT/resale/CLAUDE.md" "$ROOT/resale/BUILD_TASK.md" \
  "$ROOT/resale/claude-settings.json" "$ROOT/resale/start-build.sh" "$GUARD/copy/"
cp -R "$ROOT/resale/memory/." "$GUARD/copy/memory/"
cp -R "$ROOT/resale/seed/." "$GUARD/copy/seed/"
if [ -f "$ROOT/.cursor/rules/resale-app.mdc" ]; then
  mkdir -p "$GUARD/copy/rules"
  cp "$ROOT/.cursor/rules/resale-app.mdc" "$GUARD/copy/rules/resale-app.mdc"
fi

STAMP="$GUARD/stamp"
touch "$STAMP"

set +e
claude --model sonnet \
  --effort high \
  --permission-mode dontAsk \
  --settings "$ROOT/resale/claude-settings.json" \
  --append-system-prompt-file "$ROOT/resale/CLAUDE.md" \
  --name "cj-resale-build" \
  -p "$(cat "$ROOT/resale/BUILD_TASK.md")"
CLAUDE_EXIT=$?
set -e

python3 - "$ROOT" "$GUARD" "$STAMP" "$CLAUDE_EXIT" << 'PY'
import hashlib, os, pathlib, shutil, subprocess, sys

root = pathlib.Path(sys.argv[1])
guard = pathlib.Path(sys.argv[2])
stamp = os.stat(sys.argv[3]).st_mtime
claude_exit = sys.argv[4]
copy = guard / "copy"

restored = []
warned = []
quarantined = []

def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def restore_tree(src: pathlib.Path, dest: pathlib.Path):
    if src.is_dir():
        for child in src.rglob("*"):
            if child.is_file():
                target = dest / child.relative_to(src)
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists() or sha(target) != sha(child):
                    target.write_bytes(child.read_bytes())
                    restored.append(str(target.relative_to(root)))
    else:
        if not dest.exists() or sha(dest) != sha(src):
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(src.read_bytes())
            restored.append(str(dest.relative_to(root)))

for name in ["PLAN.md", "CLAUDE.md", "BUILD_TASK.md", "claude-settings.json", "start-build.sh"]:
    restore_tree(copy / name, root / "resale" / name)
restore_tree(copy / "memory", root / "resale" / "memory")
restore_tree(copy / "seed", root / "resale" / "seed")
rule_src = copy / "rules" / "resale-app.mdc"
if rule_src.exists():
    restore_tree(rule_src, root / ".cursor" / "rules" / "resale-app.mdc")

before = set()
for line in (guard / "before.txt").read_text().splitlines():
    if len(line) < 4:
        continue
    path = line[3:].strip().strip('"')
    if " -> " in path:
        path = path.split(" -> ", 1)[1].strip().strip('"')
    before.add(path)

newer = []
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d != ".git"]
    for filename in filenames:
        path = pathlib.Path(dirpath) / filename
        try:
            if path.stat().st_mtime <= stamp:
                continue
        except OSError:
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("resale/") or rel.startswith(".git/"):
            continue
        newer.append(rel)

for rel in newer:
    path = root / rel
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", rel],
        cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0
    if tracked and rel not in before:
        subprocess.run(["git", "restore", "--source=HEAD", "--worktree", "--", rel], cwd=root)
        restored.append(rel + " (put back)")
        continue
    if not tracked and rel not in before:
        dest = root / "resale" / "_guardrail_quarantine" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(dest))
        quarantined.append(rel)
        continue
    warned.append(rel)

report = root / "resale" / "GUARDRAIL_REPORT.md"
lines = [
    "# Guardrail report",
    "",
    f"Claude exit code: {claude_exit}",
    "",
    "Protected files (plan, seed, site memory, this script) were checked and put back if Claude changed them.",
    "",
]
if restored:
    lines.append("## Put back")
    lines.extend(f"- {item}" for item in restored)
    lines.append("")
if quarantined:
    lines.append("## Moved out of the HTSA site into resale/_guardrail_quarantine")
    lines.extend(f"- {item}" for item in quarantined)
    lines.append("")
if warned:
    lines.append("## Left alone, but Claude touched an existing file outside resale")
    lines.append("These were already changed or untracked before the build, so they were not overwritten.")
    lines.extend(f"- {item}" for item in warned)
    lines.append("")
if not restored and not quarantined and not warned:
    lines.append("Nothing outside the app files needed to be put back.")
    lines.append("")
report.write_text("\n".join(lines))
print("\n".join(lines))
PY

echo ""
echo "Build step finished (Claude exit $CLAUDE_EXIT)."
echo "Open resale/BUILD_REPORT.md and resale/GUARDRAIL_REPORT.md."
echo "Come back to the Cursor chat and say the build finished. Do not push yet."
exit "$CLAUDE_EXIT"
