#!/usr/bin/env python3
"""Remove only the orange performance-guarantee HTML block from an enrollment invoice.

Safe removal: deletes from the guarantee comment through the line before
hts-terms-agreement-wrap — never stops at the first inner </motion>.

Usage (repo root):
  python3 scripts/remove-guarantee-banner.py htsa-enrollment-haley-scott.html
"""
from __future__ import annotations

import sys
from pathlib import Path

START = "  <!-- Performance guarantee — confirmed for this enrollment -->\n"
END = "  <div class=\"hts-terms-agreement-wrap\">"


def remove_guarantee(html: str) -> str:
    i = html.find(START)
    if i == -1:
        if "enrollment-guarantee-banner--pre-terms" in html:
            raise SystemExit("Guarantee banner found but start comment missing — fix markers.")
        return html  # already removed
    j = html.find(END, i)
    if j == -1:
        raise SystemExit("Could not find hts-terms-agreement-wrap after guarantee block.")
    return html[:i] + html[j:]


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: remove-guarantee-banner.py htsa-enrollment-….html")
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    new = remove_guarantee(text)
    if new == text:
        print("No change (guarantee block already absent).")
        return
    path.write_text(new, encoding="utf-8")
    print(f"Removed guarantee block from {path.name}")


if __name__ == "__main__":
    main()
