#!/usr/bin/env sh
# Confirm GitHub Pages is serving an enrollment invoice (HTTP 2xx).
#
# Usage (from repo root):
#   sh scripts/check-enrollment-live.sh haley-scott
#   sh scripts/check-enrollment-live.sh haley-scott https://closewithcjclay.com
#   sh scripts/check-enrollment-live.sh haley-scott https://closewithcjclay.com 360
#
# Args: slug [base-url] [max-wait-seconds]
# Default max wait: 360 (6 min), poll every 10s.
# Exit 0 when live; exit 1 on timeout or bad slug.

set -e
slug="${1:?usage: check-enrollment-live.sh <slug> [base-url] [max-wait-seconds]}"
base="${2:-https://closewithcjclay.com}"
max_wait="${3:-360}"
interval=10
url="${base}/htsa-enrollment-${slug}.html"

printf 'Checking %s (up to %ss)\n' "$url" "$max_wait"
elapsed=0
attempt=0
while [ "$elapsed" -lt "$max_wait" ]; do
  attempt=$((attempt + 1))
  code=$(curl -sS -o /dev/null -w '%{http_code}' "$url" || echo "000")
  if [ "$code" -ge 200 ] 2>/dev/null && [ "$code" -lt 300 ] 2>/dev/null; then
    printf 'READY — HTTP %s (attempt %s)\n' "$code" "$attempt"
    printf '%s\n' "$url"
    exit 0
  fi
  printf '  attempt %s: HTTP %s — retry in %ss…\n' "$attempt" "$code" "$interval"
  sleep "$interval"
  elapsed=$((elapsed + interval))
done

printf 'TIMEOUT — still not HTTP 2xx after %ss\n' "$max_wait" >&2
printf '%s\n' "$url" >&2
exit 1
