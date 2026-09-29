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
    print(
        "It was great speaking with you. I really appreciate how intentional and "
        "thorough you are as you evaluate this decision—that kind of diligence is "
        "the exact characteristic we look for in the members we partner with."
    )
    print()
    print(
        "Here is the link to your HTSA enrollment portal with the payment options "
        "we covered along with the enrollment bonuses discussed on our call:"
    )
    print()
    print(f"Click Here to Access Your HTSA Portal: {url}")
    print()
    print(
        "At the bottom of the page, you'll see our 30-Day Action Plan. Use that as "
        "a benchmark for what's possible—many of our members have actually beaten "
        "that timeline, but more importantly, remember that mastering a high-ticket "
        "skill isn't something to rush. Enjoy the process, get the absolute most out "
        "of every coaching session and AI sandbox rep, and feel good knowing you have "
        "our team and placement support in your corner for life."
    )
    print()
    print(
        "Once you complete your enrollment on the page, your portal access unlocks "
        "immediately. From there, you have two simple ways to finish setup:"
    )
    print()
    print(
        '1. Self-Enroll Setup: Follow the steps in the green "After You Pay" section '
        "right on the screen to set up your portal login and book your kickoff call."
    )
    print(
        "2. Text or Call Me for 5 Minutes: Shoot me a quick text as soon as you "
        "complete payment, and we can jump on a brief 5-minute call so I walk you "
        "through portal activation live."
    )
    print()
    print("If any questions come up while reviewing everything, call or text me anytime.")
    print()
    print("Best,")
    print()
    print("CJ Clay")
    print("HTSA, Senior Career Transformation Coach")
    print("(616) 612-1735")
    print("cj@highticketsalesacademy.com")
    print()
    print("=== TEXT (send right after the email) ===")
    print(
        "Hey — just sent over your enrollment portal link and payment options. Really "
        "appreciated how intentional you were on our call. Take a look when you get a "
        "second. Once you complete your enrollment on the page, your portal access "
        "unlocks right away—you can follow the post-payment steps on screen, or text "
        "me for a quick 5-min call to walk through portal activation together!"
    )
    print()
    print(url)
