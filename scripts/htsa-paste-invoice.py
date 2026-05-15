#!/usr/bin/env python3
"""
Read CJ's paste block from stdin (or a file), then run htsa-instantiate-invoice.py.

Expected paste shape (blank lines OK):

  Full Name

  Email: someone@example.com

  Phone Number: +1 (978) 404-0928

  Setter - Cash Only
  # OR: templates/htsa-placement-03-setter-cash-only.html
  # OR: Setter - Cash Only or templates/htsa-placement-03-setter-cash-only.html

From repo root — paste, then EOF (Ctrl-D) or use a here-doc:

  python3 scripts/htsa-paste-invoice.py <<'EOF'
  ...
  EOF

Options:
  --no-ship     Write HTML only (no git commit/push)
  --dry-run     Print parsed fields and exit
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTANTIATE = ROOT / "scripts/htsa-instantiate-invoice.py"


def to_e164(raw: str) -> str:
    """Best-effort US-ish E.164; keeps international if already + and digits."""
    s = raw.strip()
    digits = re.sub(r"\D", "", s)
    if not digits:
        raise ValueError(f"No digits in phone: {raw!r}")
    if len(digits) == 10:
        return "+1" + digits
    if len(digits) == 11 and digits.startswith("1"):
        return "+" + digits
    return "+" + digits


def extract_email(text: str) -> str | None:
    m = re.search(
        r"(?im)^\s*e-?mail\s*[:;]?\s*(\S+@\S+)",
        text,
    )
    if not m:
        m = re.search(r"([a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})", text, re.I)
    if not m:
        return None
    return m.group(1).strip().rstrip(",.;)")


def extract_phone_display(text: str) -> str | None:
    m = re.search(
        r"(?im)^\s*(?:phone\s*(?:number)?|mobile|cell)\s*[:;]?\s*(.+?)\s*$",
        text,
    )
    if m:
        return m.group(1).strip()
    # fallback: labeled inline
    m = re.search(r"(?i)phone\s*(?:number)?\s*[:;]?\s*([+\d\s().-]{10,})", text)
    return m.group(1).strip() if m else None


def extract_template_path(fragment: str) -> str | None:
    m = re.search(
        r"(templates/)?htsa-placement-[0-9]{2}-[a-z0-9-]+\.html",
        fragment,
        re.I,
    )
    if not m:
        return None
    path = m.group(0)
    if not path.lower().startswith("templates/"):
        path = "templates/" + path
    return path


def financing_phrase(s: str) -> bool:
    t = s.lower()
    if re.search(r"cash\s*only", t) and "financ" not in t:
        return False
    return bool(
        re.search(
            r"financ|clarity|flexx|cash\s*\+\s*financ|cash\s+and\s+financ",
            t,
        )
    )


def dual_program(s: str) -> bool:
    t = s.lower()
    if "closer" in t and "setter" in t:
        return True
    return " & " in t or re.search(r"\bsetter\b.*\bcloser\b|\bcloser\b.*\bsetter\b", t)


def setter_only(s: str) -> bool:
    t = s.lower()
    return "setter" in t and "closer" not in t


def closer_only(s: str) -> bool:
    t = s.lower()
    return "closer" in t and "setter" not in t


def phrase_to_placement_id(line: str) -> str:
    raw = line.strip()
    fin = financing_phrase(raw)
    if dual_program(raw):
        return "06" if fin else "05"
    if setter_only(raw):
        return "04" if fin else "03"
    if closer_only(raw):
        return "02" if fin else "01"
    # bare hints
    if "setter" in raw.lower():
        return "04" if fin else "03"
    if "closer" in raw.lower():
        return "02" if fin else "01"
    raise SystemExit(
        f"Could not map program line to placement 01–06: {raw!r}\n"
        "Use e.g. 'Setter - Cash only' or a full templates/htsa-placement-….html path."
    )


def resolve_placement_line(line: str) -> str:
    """Return template path or 01–06 for instantiate first arg."""
    line = line.strip()
    if not line:
        raise SystemExit("Empty program / placement line.")
    parts = re.split(r"\s+or\s+", line, flags=re.I)
    for p in reversed(parts):
        p = p.strip()
        tp = extract_template_path(p)
        if tp and (ROOT / tp).is_file():
            return tp
    first = parts[0].strip()
    tp = extract_template_path(first)
    if tp and (ROOT / tp).is_file():
        return tp
    return phrase_to_placement_id(first)


def infer_name(text: str, placement_raw: str) -> str:
    """First non-empty line that is not the program line, email, or phone."""
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    pr = placement_raw.strip()
    for line in lines:
        if line == pr:
            continue
        if re.match(r"(?i)^e-?mail\b", line):
            continue
        if re.match(r"(?i)^(?:phone|mobile|cell)\b", line):
            continue
        return line
    raise SystemExit(
        "Could not find full name. Put the client's **full name** on its own line "
        "above Email / Phone / program type."
    )


def infer_placement_line(text: str) -> str:
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    for line in reversed(lines):
        if extract_template_path(line):
            return line
        low = line.lower()
        if "htsa-placement" in low:
            return line
        if re.search(r"(?i)\b(setter|closer)\b", line):
            return line
    raise SystemExit(
        "Could not find program type line (e.g. 'Setter - Cash only' or templates/... path)."
    )


def parse_paste(text: str) -> tuple[str, str, str, str, str]:
    """full_name, email, phone_display, phone_e164, template_arg"""
    email = extract_email(text)
    if not email:
        raise SystemExit("Could not find an email (use a line like Email: x@y.com).")
    phone_disp = extract_phone_display(text)
    if not phone_disp:
        raise SystemExit("Could not find phone (use a line like Phone Number: +1 (…) ).")
    try:
        phone_e164 = to_e164(phone_disp)
    except ValueError as e:
        raise SystemExit(str(e)) from e
    placement_raw = infer_placement_line(text)
    name = infer_name(text, placement_raw)
    template_arg = resolve_placement_line(placement_raw)
    return name, email, phone_disp, phone_e164, template_arg


def main() -> None:
    ap = argparse.ArgumentParser(description="Parse CJ paste → instantiate invoice.")
    ap.add_argument(
        "file",
        nargs="?",
        type=Path,
        help="Optional file with paste (default: read stdin)",
    )
    ap.add_argument(
        "--no-ship",
        action="store_true",
        help="Do not git commit/push (only write HTML).",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Print parsed values and exit.",
    )
    args = ap.parse_args()

    if args.file:
        text = args.file.read_text(encoding="utf-8")
    else:
        if sys.stdin.isatty():
            print("Paste CJ block, then press Ctrl-D (empty line + Ctrl-D on some systems):", file=sys.stderr)
        text = sys.stdin.read()

    name, email, phone_disp, phone_e164, template_arg = parse_paste(text)

    if args.dry_run:
        print("full_name:", name)
        print("email:", email)
        print("phone_display:", phone_disp)
        print("phone_e164:", phone_e164)
        print("template:", template_arg)
        return

    cmd = [
        sys.executable,
        str(INSTANTIATE),
        template_arg,
        "--full-name",
        name,
        "--email",
        email,
        "--phone-e164",
        phone_e164,
        "--phone-display",
        phone_disp,
        "--overwrite",
    ]
    if not args.no_ship:
        cmd.append("--ship")

    subprocess.run(cmd, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
