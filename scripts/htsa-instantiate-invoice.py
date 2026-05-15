#!/usr/bin/env python3
# Replaces {{HTSA_*}} placeholders in a frozen template and writes a new root-level invoice.
#
# Template: full path, or placement shorthand 01–06 / 1–6 / placement-02 / p02
#
# From repo root:
#   python3 scripts/htsa-instantiate-invoice.py 02 \
#     --full-name "Jane Doe" --email "jane@example.com" --phone-e164 "+15551234567" \
#     --phone-display "+1 (555) 123-4567" --overwrite --ship
#
# --ship runs git add / commit / push for this file only (main). Use when you need the link live fast.

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


PLACEMENT_TEMPLATES: dict[str, str] = {
    "01": "templates/htsa-placement-01-closer-cash-only.html",
    "02": "templates/htsa-placement-02-closer-cash-financing.html",
    "03": "templates/htsa-placement-03-setter-cash-only.html",
    "04": "templates/htsa-placement-04-setter-cash-financing.html",
    "05": "templates/htsa-placement-05-closer-setter-cash-only.html",
    "06": "templates/htsa-placement-06-closer-setter-cash-financing.html",
}


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


def normalize_placement_key(raw: str) -> str | None:
    """Return '01'..'06' if raw is a placement alias, else None."""
    s = raw.strip().lower()
    if not s:
        return None
    s = s.removeprefix("templates/")
    if s.endswith(".html"):
        return None
    s = s.replace("placement-", "p")
    if s.startswith("p") and len(s) >= 2:
        s = s[1:]
    if s.isdigit() and 1 <= int(s) <= 9:
        n = int(s)
        if 1 <= n <= 6:
            return f"{n:02d}"
    if re.fullmatch(r"0[1-6]", s):
        return s
    return None


def resolve_template(arg: str, root: Path) -> Path:
    p = Path(arg)
    if p.is_absolute() and p.is_file():
        return p
    rel = root / arg
    if rel.is_file():
        return rel
    key = normalize_placement_key(arg)
    if key and key in PLACEMENT_TEMPLATES:
        return root / PLACEMENT_TEMPLATES[key]
    raise SystemExit(
        f"Template not found: {arg}\n"
        f"Use a path like templates/htsa-placement-01-….html or a placement id: 01, 02, … 06."
    )


def run_git_ship(root: Path, filename: str, message: str) -> None:
    subprocess.run(["git", "add", filename], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=root, check=True)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description="Create htsa-enrollment-{slug}.html from a frozen template.")
    ap.add_argument(
        "template",
        help="templates/htsa-placement-….html or placement id 01–06 (e.g. 02, placement-02, p2)",
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
    ap.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing htsa-enrollment-{slug}.html if present (same client refresh).",
    )
    ap.add_argument(
        "--ship",
        action="store_true",
        help="git add, commit, and push only this file to origin/main after writing.",
    )
    ap.add_argument(
        "--commit-message",
        default="",
        help="With --ship, custom commit subject (default: auto from client name).",
    )
    args = ap.parse_args()

    tpl = resolve_template(args.template, root)

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
    if out.exists() and not args.overwrite:
        raise SystemExit(f"Refusing to overwrite existing file: {out}\nPass --overwrite to replace.")

    out.write_text(text, encoding="utf-8")
    url = f"https://closewithcjclay.com/htsa-enrollment-{slug}.html"
    print(out)
    print(url)
    print()

    if args.ship:
        msg = args.commit_message.strip() or f"Update HTSA enrollment invoice for {args.full_name.strip()}."
        try:
            run_git_ship(root, out.name, msg)
        except subprocess.CalledProcessError as e:
            print("git ship failed — commit/push yourself.", file=sys.stderr)
            raise SystemExit(e.returncode) from e
        print("Pushed to origin/main. Allow 1–5 minutes for GitHub Pages, then hard-refresh.")
    else:
        print("Live URL will 404 until this file is on origin/main and GitHub Pages finishes building.")
        print("Or rerun with --ship to add, commit, and push in one step.")
        print("Required (manual):")
        print(
            f'  git add {out.name} && git commit -m "Add HTSA enrollment invoice for {args.full_name.strip()}." && git push origin main'
        )
        print("After push: wait 1–5 minutes if you still see 404; then hard-refresh (⌘⇧R / Ctrl+Shift+R).")

    print(f'Verify: curl -sI "{url}" | head -1   # should show HTTP/2 200 after deploy')


if __name__ == "__main__":
    main()
