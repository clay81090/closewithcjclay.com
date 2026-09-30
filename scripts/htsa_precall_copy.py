"""Fail-safe pre-call email + text — zero variables, generic URL."""

from __future__ import annotations

GENERIC_PRECALL_URL = "https://closewithcjclay.com/before-our-call"

PRECALL_EMAIL_SUBJECT = "Before our call / HTSA pre-call page"


def print_precall_pack() -> None:
    """Email first, then one text. No name variables."""
    url = GENERIC_PRECALL_URL
    print("=== EMAIL SUBJECT ===")
    print(PRECALL_EMAIL_SUBJECT)
    print("=== EMAIL ===")
    print("Hi,")
    print()
    print(f"Click Here to Review the Pre-Call Page: {url}")
    print()
    print(
        "Looking forward to connecting on our call! I put together a quick 4-minute "
        "clip on that page for you to check out beforehand."
    )
    print()
    print(
        "It is not homework at all, just a brief look at four of our members talking "
        "about getting placed, what it actually took, and having multiple offers to "
        "choose from."
    )
    print()
    print(
        "Walk in with your real situation and your real questions, and we will dive right in."
    )
    print()
    print("Best,")
    print()
    print("CJ Clay")
    print("HTSA, Senior Career Transformation Coach")
    print("(616) 612-1735")
    print("cj@highticketsalesacademy.com")
    print()
    print("=== TEXT ===")
    print("Hey, looking forward to connecting on our call!")
    print()
    print(url)
    print()
    print(
        "Put together a quick 4-minute clip on that page for you to check out beforehand. "
        "Not homework at all, just a brief look at four of our members talking about "
        "getting placed and having multiple offers to choose from. Walk in with your "
        "real questions and we will dive right in!"
    )
