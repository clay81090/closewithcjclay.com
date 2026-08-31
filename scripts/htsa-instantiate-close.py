#!/usr/bin/env python3
"""
Build a close page from templates/_TEMPLATE-close.html.

Only the BUYER block changes. Prices come from offer: standard | reactivation.

  python3 scripts/htsa-instantiate-close.py \
    --full-name "Test Person" --email test@example.com --phone-e164 +15555550100 \
    --offer reactivation --show plan,clarity --overwrite --ship

--ship commits, pushes, then waits until the LIVE html contains this build's
stamp. A 200 on an old cached invoice does not count. If the clean URL is still
stale, READY prints the same URL with ?v=<stamp> so Fastly misses.
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

TEMPLATE = ROOT / "templates/_TEMPLATE-close.html"
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
    """Return the URL that actually has the stamp (clean or ?v=stamp)."""
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


def write_page(
    *,
    full_name: str,
    email: str,
    phone: str,
    track: str,
    offer: str,
    show: list[str],
    overwrite: bool,
) -> tuple[Path, str, str, str]:
    if not TEMPLATE.is_file():
        raise SystemExit(f"Missing template: {TEMPLATE}")
    text = TEMPLATE.read_text(encoding="utf-8")
    if not BUYER_RE.search(text):
        raise SystemExit("Template has no BUYER block.")

    fn = first_name(full_name)
    fslug = file_slug(full_name)
    bslug = buyer_slug(full_name)
    stamp = str(int(time.time()))
    show_js = ", ".join(f'"{s}"' for s in show)
    block = (
        f"const BUYER = {{\n"
        f'  firstName: "{fn}",\n'
        f'  fullName:  "{full_name.strip()}",\n'
        f'  email:     "{email.strip()}",\n'
        f'  phone:     "{phone.strip()}",\n'
        f'  slug:      "{bslug}",\n'
        f'  track:     "{track}",\n'
        f'  offer:     "{offer}",\n'
        f'  show:      [{show_js}]\n'
        f"}};"
    )
    # Stamp lives in the JS comment so the live poll can tell new html from a cached old invoice.
    text = BUYER_RE.sub(block, text, count=1)
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
    if out.exists() and not overwrite:
        raise SystemExit(f"Refusing to overwrite {out.name}. Pass --overwrite.")
    out.write_text(text, encoding="utf-8")
    url = f"{LIVE_HOST}/htsa-enrollment-{fslug}.html"
    return out, url, stamp, fn


def main() -> None:
    ap = argparse.ArgumentParser(description="Instantiate a close page from the frozen template.")
    ap.add_argument("--full-name", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--phone-e164", required=True)
    ap.add_argument("--track", default="closer", choices=("closer", "setter"))
    ap.add_argument("--offer", default="standard", choices=("standard", "reactivation"))
    ap.add_argument("--show", default="pif,plan,clarity", help="Comma list: pif,plan,clarity")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--ship", action="store_true")
    ap.add_argument("--no-wait-live", action="store_true")
    args = ap.parse_args()

    show = [s.strip() for s in args.show.split(",") if s.strip()]
    allowed = {"pif", "plan", "clarity"}
    bad = [s for s in show if s not in allowed]
    if bad or not show:
        raise SystemExit(f"--show must be pif/plan/clarity, got {args.show!r}")

    out, url, stamp, fn = write_page(
        full_name=args.full_name,
        email=args.email,
        phone=args.phone_e164,
        track=args.track,
        offer=args.offer,
        show=show,
        overwrite=args.overwrite,
    )
    game = game_url(fn)
    print(out.name, file=sys.stderr)
    print(f"GAME {game}")

    if not args.ship:
        print(url)
        print_send_pack(fn, url, game)
        print("Local only. Rerun with --overwrite --ship to publish.", file=sys.stderr)
        return

    msg = f"Add close page for {args.full_name.strip()}"
    try:
        run_git_ship(out.name, msg)
    except subprocess.CalledProcessError as e:
        raise SystemExit("git ship failed") from e
    print("Pushed.", file=sys.stderr)

    if args.no_wait_live:
        print(url)
        print_send_pack(fn, url, game)
        return

    live = wait_for_stamp(url, f"close-build:{stamp}", POLL_TIMEOUT)
    if not live:
        print(f"Push OK but stamp not live within {POLL_TIMEOUT}s.", file=sys.stderr)
        print(url, file=sys.stderr)
        print_send_pack(fn, url, game)
        raise SystemExit(2)
    print("READY")
    print(live)
    print_send_pack(fn, live, game)


if __name__ == "__main__":
    main()
