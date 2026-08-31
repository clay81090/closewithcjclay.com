#!/usr/bin/env python3
"""
Paste CJ's enroll block on stdin, build the close page, ship it.

  python3 scripts/htsa-paste-close.py --ship <<'EOF'
  Test Person
  Email: test@example.com
  Phone Number: +1 (555) 555-0100
  3 pay = $5250
  Clarity Pay $500/mo
  EOF

Promo prices ($5k PIF, $1750 3-pay, $500/mo Clarity) flip offer=reactivation.
Only the options he names go on the page. No name → no option.
If he names none, show pif+plan+clarity at standard prices.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTANTIATE = ROOT / "scripts/htsa-instantiate-close.py"


def to_e164(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if not digits:
        raise ValueError(f"No digits in phone: {raw!r}")
    if len(digits) == 10:
        return "+1" + digits
    if len(digits) == 11 and digits.startswith("1"):
        return "+" + digits
    return "+" + digits


def parse(text: str) -> dict:
    email_m = re.search(r"(?im)^\s*e-?mail\s*[:;]?\s*(\S+@\S+)", text)
    if not email_m:
        email_m = re.search(r"([a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})", text, re.I)
    phone_m = re.search(
        r"(?im)^\s*(?:phone\s*(?:number)?|mobile|cell)\s*[:;]?\s*(.+?)\s*$",
        text,
    )
    name = ""
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if re.match(r"(?i)^(e-?mail|phone|mobile|cell)\b", s):
            continue
        if "@" in s:
            continue
        if re.search(r"(?i)clarity|3\s*-?\s*pay|4\s*-?\s*pay|pif|paid in full|\$", s):
            continue
        name = s
        break
    if not name:
        raise SystemExit("Could not find a name on the first real line.")
    if not email_m:
        raise SystemExit("Could not find Email:")
    if not phone_m:
        raise SystemExit("Could not find Phone Number:")

    blob = text.lower()
    show: list[str] = []
    if re.search(r"\bpif\b|paid in full|\$5,?000|5k pif", blob):
        show.append("pif")
    if re.search(r"3\s*-?\s*pay|\$5,?250|\$1,?750", blob):
        show.append("plan")
    if re.search(r"clarity|\$500\s*/?\s*mo", blob):
        show.append("clarity")
    # $6000 alone without "clarity" is the PIF total on promo, already handled.

    promo = bool(
        re.search(r"\$5,?000|5k|\$5,?250|3\s*-?\s*pay|\$500\s*/?\s*mo", blob)
    )
    if re.search(r"\$6,?000", blob) and "clarity" in blob:
        promo = True

    if not show:
        show = ["pif", "plan", "clarity"]
        promo = False

    track = "setter" if re.search(r"\bsetter\b", blob) and not re.search(r"\bcloser\b", blob) else "closer"
    return {
        "full_name": name,
        "email": email_m.group(1).strip().rstrip(",.;)"),
        "phone": to_e164(phone_m.group(1)),
        "track": track,
        "offer": "reactivation" if promo else "standard",
        "show": show,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ship", action="store_true", default=True)
    ap.add_argument("--no-ship", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    raw = sys.stdin.read()
    if not raw.strip():
        raise SystemExit("Paste the block on stdin, then Ctrl-D.")
    fields = parse(raw)
    if args.dry_run:
        print(fields)
        return
    cmd = [
        sys.executable,
        str(INSTANTIATE),
        "--full-name", fields["full_name"],
        "--email", fields["email"],
        "--phone-e164", fields["phone"],
        "--track", fields["track"],
        "--offer", fields["offer"],
        "--show", ",".join(fields["show"]),
        "--overwrite",
    ]
    if args.ship and not args.no_ship:
        cmd.append("--ship")
    raise SystemExit(subprocess.call(cmd, cwd=ROOT))


if __name__ == "__main__":
    main()
