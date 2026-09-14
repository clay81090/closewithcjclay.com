#!/bin/sh
# Ship game-plan call scripts + any pending enrollment pages.
# Run from repo root: sh scripts/ship-game-plan-and-pending.sh

set -e
cd "$(dirname "$0")/.."

echo "=== git status (before) ==="
git status --short

# Game-plan call prep (Jada, Colton, Angel, etc.)
git add sales-engine/game-plan/

# Elliott training-only enrollment (if present)
if [ -f htsa-enrollment-elliott-peaks.html ]; then
  git add htsa-enrollment-elliott-peaks.html
fi

# Do NOT add scratch / review artifacts
# Untitled, HTSA-Terms-of-Service-cleaned-review.*

if git diff --cached --quiet; then
  echo "Nothing staged — already committed or no changes."
  git status
  git log -1 --oneline
  exit 0
fi

git commit -m "$(cat <<'EOF'
Add game-plan one-call scripts and call prep snapshots.

Jada Covington, Colton Haskin, Angel Romero folders plus game-plan README; include Elliott training-only enrollment when present.
EOF
)"

git push origin main

echo ""
echo "=== done ==="
git status --short
git log -1 --oneline
