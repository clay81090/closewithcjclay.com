"""Shared send-pack copy for close pages.

Fail-safe post-call follow-up (Sept 2026+): zero name variables in body copy.
Single generic enrollment URL for everyone: https://closewithcjclay.com/access
"""

from __future__ import annotations

import re
from pathlib import Path

LIVE = "https://closewithcjclay.com"
GENERIC_ENROLL_URL = f"{LIVE}/access"

EMAIL_SUBJECT = "Your HTSA enrollment page is ready"


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
    print(f"Click Here to Access Your HTSA Portal: {url}")
    print()
    print(
        "The page has the payment options we covered, plus the enrollment bonuses "
        "from our call. Those bonuses stay on the page through Thursday, "
        "October 1st at 8pm EST."
    )
    print()
    print(
        "Once you enroll, access unlocks right away. Use the green After You Pay "
        "section to self-enroll, or text me and we can do a quick 5-minute walkthrough."
    )
    print()
    print(
        "In your moments of decision, life stops happening to you and starts "
        "happening for you the second you step into position."
    )
    print()
    print("Call or text anytime if questions come up.")
    print()
    print("Best,")
    print()
    print("CJ Clay")
    print("HTSA, Senior Career Transformation Coach")
    print("(616) 612-1735")
    print("cj@highticketsalesacademy.com")
    print()
    print("=== TEXT (send right after the email) ===")
    print("Hey, really enjoyed our call. You're a great fit for what we're building here.")
    print()
    print(url)
    print()
    print(
        "The enrollment bonuses we talked about are on that page through Thursday, "
        "October 1st at 8pm EST."
    )
    print()
    print(
        "Show up and execute, and we won't let you fail, but you have to meet us halfway. "
        "In your moments of decision, life stops happening to you and starts happening "
        "for you the second you step into position. Unlock your access above when you're ready!"
    )
