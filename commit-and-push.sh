#!/usr/bin/env bash
# Saves all file changes, commits with an automatic message, and pushes to GitHub.
# Usage: double-click commit-and-push.command (Mac) OR run: ./commit-and-push.sh

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

git add -A

# Nothing changed?
if git diff --cached --quiet; then
  echo "Nothing new to save — no changes since last commit."
  exit 0
fi

MSG="${1:-Site update $(date '+%Y-%m-%d %H:%M')}"
git commit -m "$MSG"
git push origin main

echo ""
echo "Done. Pushed to GitHub. If Pages is on, your site updates in ~1–2 minutes."
