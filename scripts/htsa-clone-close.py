#!/usr/bin/env python3
"""
Clone an existing close/enrollment page for a new person in seconds.

Keeps layout, payment options, Splitit, Flexxbuy, referrals, proof tabs — everything.
Only swaps BUYER identity (name/email/phone/slug) and the close-build stamp.

  python3 scripts/htsa-clone-close.py \\
    --same-as Brigitte \\
    --full-name "Johnny Smith" \\
    --email johnny@example.com \\
    --phone-e164 +15555550100 \\
    --overwrite --ship

  python3 scripts/htsa-clone-close.py --same-as 4 --full-name "..." ...
  python3 scripts/htsa-clone-close.py --source htsa-enrollment-sarah-gomez.html ...
  python3 scripts/htsa-clone-close.py --source https://closewithcjclay.com/htsa-enrollment-erick-blakney.html ...
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from htsa_close_copy import game_url, print_send_pack  # noqa: E402
from htsa_close_recipes import resolve_recipe, source_to_path  # noqa: E402

LIVE_HOST = "https://closewithcjclay.com"
POLL_INTERVAL = 5
POLL_TIMEOUT = 180
BUYER_RE = re.compile(r"const BUYER = \{.*?\n\};", re.S)


def first_name(full_name: str) -> str:
    parts = full_name.strip().split()
    return parts[0] if parts else ""


def file_slug(full_name: str) -> str:
    return "-".join(re.findall(r"[a-z0-9]+", full_name.strip().lower()))


def buyer_slug(full_name: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", full_name.strip().lower()))


def run_git_ship(filename: str, message: str) -> None:
    subprocess.run(["git", "add", filename], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=True)


def http_get(url: str) -> tuple[int | None, str]:
    try:
        req = urllib.request.Request(url, method="GET", headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:
            body = ""
        return e.code, body
    except OSError:
        return None, ""


def wait_for_stamp(clean_url: str, stamp: str, timeout: int) -> str:
    deadline = time.monotonic() + timeout
    attempt = 0
    busted = f"{clean_url}?v={stamp}"
    print(f"Waiting for live stamp {stamp} (up to {timeout}s)…", file=sys.stderr)
    while time.monotonic() < deadline:
        attempt += 1
        for label, url in (("clean", clean_url), ("bust", busted)):
            code, body = http_get(url)
            has = stamp in body
            print(
                f"  attempt {attempt} {label}: HTTP {code} stamp={'yes' if has else 'no'}",
                file=sys.stderr,
            )
            if code and 200 <= code < 300 and has:
                return url
        time.sleep(POLL_INTERVAL)
    return ""


def extract_buyer_field(block: str, key: str, default: str = "") -> str:
    m = re.search(rf'{key}:\s*"([^"]*)"', block)
    return m.group(1) if m else default


def extract_show(block: str) -> str:
    m = re.search(r"show:\s*(\[[^\]]*\])", block)
    return m.group(1) if m else '["pif", "plan", "clarity"]'


def extract_intro(block: str) -> str:
    m = re.search(r'intro:\s*("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`)', block)
    if not m:
        return '""'
    return m.group(1)


def clone_page(
    *,
    source_path: Path,
    full_name: str,
    email: str,
    phone: str,
    overwrite: bool,
    track: str | None = None,
    offer: str | None = None,
) -> tuple[Path, str, str, str]:
    text = source_path.read_text(encoding="utf-8")
    m = BUYER_RE.search(text)
    if not m:
        raise SystemExit(f"No BUYER block in {source_path.name}")
    old = m.group(0)

    fn = first_name(full_name)
    fslug = file_slug(full_name)
    bslug = buyer_slug(full_name)
    stamp = str(int(time.time()))

    keep_track = track or extract_buyer_field(old, "track", "closer")
    keep_offer = offer or extract_buyer_field(old, "offer", "standard")
    keep_show = extract_show(old)
    keep_intro = extract_intro(old)

    block = (
        f"const BUYER = {{\n"
        f'  firstName: "{fn}",\n'
        f'  fullName:  "{full_name.strip()}",\n'
        f'  email:     "{email.strip()}",\n'
        f'  phone:     "{phone.strip()}",\n'
        f'  slug:      "{bslug}",\n'
        f'  track:     "{keep_track}",\n'
        f'  offer:     "{keep_offer}",\n'
        f"  show:      {keep_show},\n"
        f"  intro:     {keep_intro}\n"
        f"}};"
    )
    text = BUYER_RE.sub(block, text, count=1)

    # Fresh stamp so live poll cannot confuse this build with the source page
    if "close-build:" in text:
        text = re.sub(r"close-build:\d+", f"close-build:{stamp}", text)
    else:
        text = text.replace(
            "/* ============================================================\n"
            "   EDIT THIS BLOCK ONLY — one person per page.\n"
            "   ============================================================ */",
            "/* ============================================================\n"
            "   EDIT THIS BLOCK ONLY — one person per page.\n"
            f"   close-build:{stamp}\n"
            "   ============================================================ */",
            1,
        )

    out = ROOT / f"htsa-enrollment-{fslug}.html"
    if out.resolve() == source_path.resolve():
        raise SystemExit("Refusing to overwrite the source recipe page with itself.")
    if out.exists() and not overwrite:
        raise SystemExit(f"Refusing to overwrite {out.name}. Pass --overwrite.")
    out.write_text(text, encoding="utf-8")
    url = f"{LIVE_HOST}/htsa-enrollment-{fslug}.html"
    return out, url, stamp, fn


def main() -> None:
    ap = argparse.ArgumentParser(description="Clone a close page for a new person.")
    ap.add_argument("--same-as", help="Recipe id, alias, or person name (e.g. 4, Brigitte)")
    ap.add_argument("--source", help="Filename or live URL to clone")
    ap.add_argument("--full-name", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--phone-e164", required=True)
    ap.add_argument("--track", default=None, choices=("closer", "setter"))
    ap.add_argument("--offer", default=None, choices=("standard", "reactivation"))
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--ship", action="store_true")
    ap.add_argument("--no-wait-live", action="store_true")
    args = ap.parse_args()

    if not args.same_as and not args.source:
        raise SystemExit("Pass --same-as <recipe> or --source <file|url>")

    recipe_label = ""
    if args.same_as:
        recipe = resolve_recipe(args.same_as)
        source_path = source_to_path(recipe["source"])
        recipe_label = f'{recipe["id"]} ({recipe["name"]})'
    else:
        source_path = source_to_path(args.source)
        try:
            recipe = resolve_recipe(args.source)
            recipe_label = f'{recipe["id"]} ({recipe["name"]})'
        except ValueError:
            recipe_label = source_path.name

    out, url, stamp, fn = clone_page(
        source_path=source_path,
        full_name=args.full_name,
        email=args.email,
        phone=args.phone_e164,
        overwrite=args.overwrite,
        track=args.track,
        offer=args.offer,
    )
    print(f"Cloned from {recipe_label} → {out.name}", file=sys.stderr)
    print(f"GAME {game_url(fn)}")

    if not args.ship:
        print(url)
        print_send_pack(fn, url)
        print("Local only. Rerun with --overwrite --ship to publish.", file=sys.stderr)
        return

    msg = f"Add close page for {args.full_name.strip()} (clone {recipe_label})"
    try:
        run_git_ship(out.name, msg)
    except subprocess.CalledProcessError as e:
        raise SystemExit("git ship failed") from e
    print("Pushed.", file=sys.stderr)

    if args.no_wait_live:
        print(url)
        print_send_pack(fn, url)
        return

    live = wait_for_stamp(url, f"close-build:{stamp}", POLL_TIMEOUT)
    if not live:
        print(f"Push OK but stamp not live within {POLL_TIMEOUT}s.", file=sys.stderr)
        print(url, file=sys.stderr)
        print_send_pack(fn, url)
        raise SystemExit(2)
    print("READY")
    print(live)
    print_send_pack(fn, live)


if __name__ == "__main__":
    main()
