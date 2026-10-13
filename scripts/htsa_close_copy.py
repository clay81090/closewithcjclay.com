"""Shared send-pack copy for close pages.

Fail-safe post-call follow-up (Sept 2026+): zero name variables in body copy.
Single generic enrollment URL for everyone: https://closewithcjclay.com/access
"""

from __future__ import annotations

import re
from pathlib import Path

LIVE = "https://closewithcjclay.com"
GENERIC_ENROLL_URL = f"{LIVE}/access"

EMAIL_SUBJECT = "Your HTSA enrollment page"


def file_slug(full_name: str) -> str:
    return "-".join(re.findall(r"[a-z0-9]+", full_name.strip().lower()))


def first_name(full_name: str) -> str:
    parts = full_name.strip().split()
    return parts[0] if parts else ""


def game_url(first: str) -> str:
    return f"{LIVE}/30-day-roadmap.html?n={first}"


def enroll_url_from_name(full_name: str) -> str:
    return GENERIC_ENROLL_URL


def page_path(root: Path, full_name: str) -> Path:
    return root / f"htsa-enrollment-{file_slug(full_name)}.html"


def first_name_from_html(html: str) -> str:
    m = re.search(r'firstName:\s*"([^"]+)"', html)
    return m.group(1) if m else ""


def print_send_pack(first: str, enroll: str | None = None) -> None:
    """Default post-call send pack. Send EMAIL first, then TEXT.

    `first` is kept for script compatibility but is not used in client copy.
    `enroll` is ignored; everyone gets GENERIC_ENROLL_URL.
    """
    url = GENERIC_ENROLL_URL
    print("=== EMAIL SUBJECT ===")
    print(EMAIL_SUBJECT)
    print("=== EMAIL ===")
    print("Hi,")
    print()
    print(
        "Thank you for the time on our call. I appreciate you talking it through "
        "with me. Your enrollment page is here:"
    )
    print()
    print(f"Click Here to Access Your HTSA Portal: {url}")
    print()
    print(
        "The options on the page: $7,000 paid in full, four payments of $1,950, "
        "or ClarityPay at $700 a month at 0% interest. Depending on approval, "
        "ClarityPay may offer lower monthly options."
    )
    print()
    print(
        "Once you enroll, access unlocks right away. Text me anytime and we can "
        "do a quick 5-minute walkthrough."
    )
    print()
    print("Best,")
    print()
    print("CJ Clay")
    print("HTSA, Senior Career Transformation Coach")
    print("(616) 612-1735")
    print("cj@highticketsalesacademy.com")
    print()
    print("=== TEXT (send right after the email) ===")
    print("Hey, really appreciate the time on our call. Here is your enrollment page:")
    print()
    print(url)
    print()
    print(
        "$7,000 paid in full, four payments of $1,950, or ClarityPay at $700 a "
        "month at 0%. Lower monthly options may be available depending on "
        "approval. Text me anytime if you want a quick walkthrough."
    )
