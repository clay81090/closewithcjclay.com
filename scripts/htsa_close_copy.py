"""Shared send-pack copy for close pages. No dashes in client-facing lines."""

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
    """One enroll link. The 30 day plan lives at the bottom of that page."""
    print("=== TEXT ===")
    print(
        f"{first}, here is everything we just walked through. "
        "This is your enrollment page. The 30 day action plan is at the bottom. "
        "That is how we get you to the goal. Our goal is that you are our next testimonial."
    )
    print()
    print(enroll)
    print()
    print("=== EMAIL SUBJECT ===")
    print("Your enrollment page")
    print("=== EMAIL ===")
    print(f"Hi {first},")
    print()
    print("Here is everything we just walked through.")
    print()
    print(
        "This is your enrollment page. The 30 day action plan is at the bottom. "
        "That is how we get you to the goal. Our goal is that you are our next testimonial."
    )
    print()
    print(enroll)
    print()
    print("See you in there,")
    print()
    print("CJ Clay")
    print("HTSA, Career Transformation Coach")
    print("(616) 612-1735")
    print("cj@highticketsalesacademy.com")
