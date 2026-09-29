"""Shared send-pack copy for close pages.

Voice rule: mostly commas and periods so it reads human. Use a hyphen or an em
dash only when it is genuinely the clearest way to say a thing (compound
adjectives like "30-day", or a single em dash inside a long sentence). Never
use dashes for stylistic filler.

Default pack (Sept 2026+): brief email + short text. Enrollment page only.
Mention green "After you pay" (self enroll or 5 min call with CJ) when relevant.
"""

from __future__ import annotations

import re
from pathlib import Path

LIVE = "https://closewithcjclay.com"


def file_slug(full_name: str) -> str:
    return "-".join(re.findall(r"[a-z0-9]+", full_name.strip().lower()))


def first_name(full_name: str) -> str:
    parts = full_name.strip().split()
    return parts[0] if parts else ""


def game_url(first: str) -> str:
    return f"{LIVE}/30-day-roadmap.html?n={first}"


def enroll_url_from_name(full_name: str) -> str:
    return f"{LIVE}/htsa-enrollment-{file_slug(full_name)}.html"


def page_path(root: Path, full_name: str) -> Path:
    return root / f"htsa-enrollment-{file_slug(full_name)}.html"


def first_name_from_html(html: str) -> str:
    m = re.search(r'firstName:\s*"([^"]+)"', html)
    return m.group(1) if m else ""


def print_send_pack(first: str, enroll: str) -> None:
    """Default post-call send pack. Send the EMAIL first, then the TEXT.

    Brief format: link up front, 30-day plan + green After you pay note.
    """
    print("=== EMAIL SUBJECT ===")
    print("Your enrollment page")
    print("=== EMAIL ===")
    print(f"Hi {first},")
    print()
    print(
        "Good talking with you today. Here is your enrollment page with the payment "
        "options we covered."
    )
    print()
    print(enroll)
    print()
    print(
        "The 30-day action plan is at the bottom. If you finish on your own, open the "
        "green \"After you pay\" section. You can self enroll or grab a 5 minute call "
        "with me to walk through it."
    )
    print()
    print("Any questions, call or text me.")
    print()
    print("CJ Clay")
    print("HTSA, Career Transformation Coach")
    print("(616) 612-1735")
    print("cj@highticketsalesacademy.com")
    print()
    print("=== TEXT (send right after the email) ===")
    print(
        f"{first}, just emailed you your enrollment page. "
        f"Link's in there, or here if it's easier: {enroll}"
    )
    print()
    print(
        "Worth pulling up on a computer. The 30-day plan and green \"After you pay\" "
        "section are at the bottom. Any questions, call or text me directly."
    )
    print()
    print("CJ")
