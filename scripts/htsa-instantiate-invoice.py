#!/usr/bin/env python3
# Replaces {{HTSA_*}} placeholders in a frozen template and writes a new root-level invoice.
# Usage (from repo root):
#   python3 scripts/htsa-instantiate-invoice.py templates/htsa-placement-01-closer-cash-only.html \
#     --full-name "Jane Doe" --email "jane@example.com" --phone-e164 "+15551234567" \
#     --phone-display "+1 (555) 123-4567"
#
# Then: open the new file, quick visual check, git add/commit/push that file only.

from __future__ import annotations

import argparse
import re
from pathlib import Path


def client_slug(full_name: str) -> str:
    return "-".join(full_name.strip().lower().split())


def default_storage_key(full_name: str) -> str:
    parts = full_name.strip().lower().split()
    if len(parts) >= 2:
        return f"hts_terms_gate_{parts[0]}_{parts[-1]}_v1"
    if parts:
        return f"hts_terms_gate_{parts[0]}_v1"
    return "hts_terms_gate_client_v1"


def first_name(full_name: str) -> str:
    parts = full_name.strip().split()
    return parts[0] if parts else ""


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description="Create htsa-enrollment-{slug}.html from a frozen template.")
    ap.add_argument(
        "template",
        type=Path,
        help="Path under templates/, e.g. templates/htsa-placement-01-closer-cash-only.html",
    )
    ap.add_argument("--full-name", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--phone-e164", required=True, help="E.164, match data-phone e.g. +15551234567")
    ap.add_argument(
        "--phone-display",
        default="",
        help="Shown next to tel: link; defaults to --phone-e164",
    )
    ap.add_argument(
        "--client-slug",
        default="",
        help="URL slug; default: lower hyphenated full name",
    )
    ap.add_argument(
        "--storage-key",
        default="",
        help="sessionStorage key; default: hts_terms_gate_first_last_v1",
    )
    args = ap.parse_args()

    tpl = args.template if args.template.is_absolute() else root / args.template
    if not tpl.is_file():
        raise SystemExit(f"Template not found: {tpl}")

    slug = (args.client_slug or client_slug(args.full_name)).strip().lower()
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    storage = (args.storage_key or default_storage_key(args.full_name)).strip()
    display = (args.phone_display or args.phone_e164).strip()
    fn = first_name(args.full_name)

    text = tpl.read_text(encoding="utf-8")
    repl = {
        "{{HTSA_FULL_NAME}}": args.full_name.strip(),
        "{{HTSA_FIRST_NAME}}": fn,
        "{{HTSA_EMAIL}}": args.email.strip(),
        "{{HTSA_PHONE_E164}}": args.phone_e164.strip(),
        "{{HTSA_PHONE_DISPLAY}}": display,
        "{{HTSA_CLIENT_SLUG}}": slug,
        "{{HTSA_STORAGE_KEY}}": storage,
    }
    for k, v in repl.items():
        text = text.replace(k, v)

    # Production titles should not say "(template)".
    text = text.replace(" (template)</title>", "</title>")

    out = root / f"htsa-enrollment-{slug}.html"
    if out.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {out}")

    out.write_text(text, encoding="utf-8")
    url = f"https://closewithcjclay.com/htsa-enrollment-{slug}.html"
    print(out)
    print(url)
    print()
    print("Live URL will 404 until this file is on origin/main and GitHub Pages finishes building.")
    print("Required:")
    print(
        f'  git add {out.name} && git commit -m "Add HTSA enrollment invoice for {args.full_name.strip()}." && git push origin main'
    )
    print("After push: wait 1–5 minutes if you still see 404; then hard-refresh (⌘⇧R / Ctrl+Shift+R).")
    print(f'Verify: curl -sI "{url}" | head -1   # should show HTTP/2 200')


if __name__ == "__main__":
    main()
