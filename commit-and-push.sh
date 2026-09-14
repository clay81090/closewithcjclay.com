#!/usr/bin/env bash
# Saves all file changes, commits with an automatic message, and pushes to GitHub.
#
# Easy ways to run this:
#   • Mac: double-click commit-and-push.command in Finder
#   • In Cursor: open Terminal (Ctrl+`) then:  npm run push
#   • Or: Terminal menu → Run Task… → pick "Save & upload to GitHub (commit + push)"
# Note: Cmd+Shift+B opens a browser preview in Cursor — it does NOT run this script.

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
