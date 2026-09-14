#!/bin/bash
# Double-click this file in Finder to save everything and upload to GitHub (Mac).
cd "$(dirname "$0")"
chmod +x ./commit-and-push.sh 2>/dev/null || true
./commit-and-push.sh
echo ""
read -p "Press Enter to close..."
