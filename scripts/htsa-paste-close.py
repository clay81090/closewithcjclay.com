#!/usr/bin/env python3
"""
Paste CJ's enroll block on stdin, build the close page, ship it.

FAST ON-CALL (clone a page you already like — keeps layout/payments exact):

  python3 scripts/htsa-paste-close.py --ship <<'EOF'
  same as: Brigitte
  Johnny Smith
  Email: johnny@example.com
  Phone Number: +1 (555) 555-0100
  EOF

Also accepts: recipe: 4   OR   source: https://closewithcjclay.com/htsa-enrollment-….html

Blank-template build (only when he names prices, not a recipe):

  python3 scripts/htsa-paste-close.py --ship <<'EOF'
  Test Person
  Email: test@example.com
  Phone Number: +1 (555) 555-0100
  3 pay = $5250
  Clarity Pay $500/mo
  EOF
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTANTIATE = ROOT / "scripts/htsa-instantiate-close.py"
CLONE = ROOT / "scripts/htsa-clone-close.py"
SEND_PACK = ROOT / "scripts/htsa-send-pack.py"


def to_e164(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if not digits:
        raise ValueError(f"No digits in phone: {raw!r}")
    if len(digits) == 10:
        return "+1" + digits
    if len(digits) == 11 and digits.startswith("1"):
        return "+" + digits
    return "+" + digits


def extract_clone_token(text: str) -> tuple[str | None, str | None]:
    """Return (same_as_token, source_url_or_file) — at most one set."""
    m = re.search(
        r"(?im)^\s*(?:same\s*as|clone|recipe|like|copy)\s*[:#-]?\s*(.+?)\s*$",
        text,
    )
    if m:
        token = m.group(1).strip().strip("\"'")
        # "same as Brigitte for Johnny" → take first chunk before " for "
        token = re.split(r"\s+for\s+", token, maxsplit=1, flags=re.I)[0].strip()
        return token, None
    m = re.search(
        r"(?im)^\s*source\s*[:#-]?\s*(\S+)",
        text,
    )
    if m:
        return None, m.group(1).strip()
    # Bare enrollment URL anywhere in the paste
    m = re.search(
        r"(https?://(?:www\.)?closewithcjclay\.com/htsa-enrollment-[a-z0-9-]+\.html)",
        text,
        re.I,
    )
    if m and re.search(r"(?i)same\s*as|clone|like|copy|make\s+this|use\s+this", text):
        return None, m.group(1)
    return None, None


def parse(text: str) -> dict:
    same_as, source = extract_clone_token(text)

    email_m = re.search(r"(?im)^\s*e-?mail\s*[:;]?\s*(\S+@\S+)", text)
    if not email_m:
        email_m = re.search(r"([a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})", text, re.I)
    phone_m = re.search(
        r"(?im)^\s*(?:phone\s*(?:number)?|mobile|cell)\s*[:;]?\s*(.+?)\s*$",
        text,
    )
    name = ""
    skip_name = re.compile(
        r"(?i)^(e-?mail|phone|mobile|cell|same\s*as|clone|recipe|like|copy|source)\b"
    )
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if skip_name.match(s):
            continue
        if "@" in s and not re.match(r"(?i)^name\b", s):
            continue
        if re.search(r"(?i)clarity|3\s*-?\s*pay|4\s*-?\s*pay|pif|paid in full|\$|flexx|klarna|split", s):
            # Allow a line that is ONLY the person's name even if weird
            if re.search(r"(?i)(?:email|phone|http)", s):
                continue
            if "$" in s or re.search(r"(?i)pay|pif|clarity|flexx|klarna|split", s):
                continue
        # "Name: Johnny Smith"
        nm = re.match(r"(?i)^(?:full\s*)?name\s*[:#-]?\s*(.+)$", s)
        if nm:
            name = nm.group(1).strip()
            break
        name = s
        break
    if not name:
        raise SystemExit("Could not find a name on the first real line.")
    # Name only: reuse the page that is already live. Do not rebuild.
    if not email_m and not phone_m:
        return {"full_name": name, "send_only": True}
    if not email_m:
        raise SystemExit("Could not find Email:")
    if not phone_m:
        raise SystemExit("Could not find Phone Number:")

    base = {
        "full_name": name,
        "email": email_m.group(1).strip().rstrip(",.;)"),
        "phone": to_e164(phone_m.group(1)),
    }

    if same_as or source:
        out = dict(base)
        if same_as:
            out["same_as"] = same_as
        if source:
            out["source"] = source
        blob = text.lower()
        if re.search(r"\bsetter\b", blob) and not re.search(r"\bcloser\b", blob):
            out["track"] = "setter"
        elif re.search(r"\bcloser\b", blob):
            out["track"] = "closer"
        return out

    blob = text.lower()
    show: list[str] = []
    if re.search(r"\bpif\b|paid in full|\$5,?000|5k pif", blob):
        show.append("pif")
    if re.search(r"(?:3|4)\s*-?\s*pay|\$5,?250|\$1,?750|payment plan", blob):
        show.append("plan")
    if re.search(r"clarity|\$500\s*/?\s*mo|\$600\s*/?\s*mo", blob):
        show.append("clarity")
    if re.search(r"split\s*-?\s*it|splitit", blob):
        show.append("splitit")

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
        **base,
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
    if fields.get("send_only"):
        raise SystemExit(
            subprocess.call(
                [sys.executable, str(SEND_PACK), "--full-name", fields["full_name"]],
                cwd=ROOT,
            )
        )
    if "email" not in fields:
        raise SystemExit("Could not find Email:")
    if "phone" not in fields:
        raise SystemExit("Could not find Phone Number:")

    ship = args.ship and not args.no_ship

    if fields.get("same_as") or fields.get("source"):
        cmd = [
            sys.executable,
            str(CLONE),
            "--full-name", fields["full_name"],
            "--email", fields["email"],
            "--phone-e164", fields["phone"],
            "--overwrite",
        ]
        if fields.get("same_as"):
            cmd.extend(["--same-as", fields["same_as"]])
        if fields.get("source"):
            cmd.extend(["--source", fields["source"]])
        if fields.get("track"):
            cmd.extend(["--track", fields["track"]])
        if ship:
            cmd.append("--ship")
        raise SystemExit(subprocess.call(cmd, cwd=ROOT))

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
    if ship:
        cmd.append("--ship")
    raise SystemExit(subprocess.call(cmd, cwd=ROOT))


if __name__ == "__main__":
    main()
