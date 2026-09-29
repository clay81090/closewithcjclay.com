"""Fail-safe pre-call text copy — zero variables, generic URL."""

from __future__ import annotations

GENERIC_PRECALL_URL = "https://closewithcjclay.com/before-our-call"

PRECALL_EMAIL_SUBJECT = "Before our call / HTSA pre-call page"


def print_precall_pack() -> None:
    """Single recommended text (Option 1)."""
    print("=== TEXT (recommended — single message) ===")
    print(
        "Hey — CJ here. Looking forward to connecting on our call! Here is a quick "
        "pre-call page to review before we jump on Zoom:"
    )
    print()
    print(GENERIC_PRECALL_URL)
    print()
    print(
        "If you only open one thing, check out the 4-minute clip at the top—four of "
        "our members talking about getting placed, and every one of them had multiple "
        "offers to choose from. See you soon!"
    )
