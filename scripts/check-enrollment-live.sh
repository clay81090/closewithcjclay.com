#!/usr/bin/env sh
# After git push: confirm GitHub Pages is serving the invoice (expect HTTP 2xx).
# Usage (from repo root):
#   sh scripts/check-enrollment-live.sh adam-rodriguez
#   sh scripts/check-enrollment-live.sh adam-rodriguez https://closewithcjclay.com

set -e
slug="${1:?usage: check-enrollment-live.sh <slug> [base-url]}"
base="${2:-https://closewithcjclay.com}"
url="${base}/htsa-enrollment-${slug}.html"
printf 'Checking %s\n' "$url"
curl -sS -o /dev/null -w '%{http_code}\n' "$url"
