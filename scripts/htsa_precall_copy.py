"""Fail-safe pre-call email + text — zero variables, generic URL."""

from __future__ import annotations

GENERIC_PRECALL_URL = "https://closewithcjclay.com/before-our-call"

PRECALL_EMAIL_SUBJECT = "Before our call"


def print_precall_pack() -> None:
    """Email first, then one text. No name variables."""
    url = GENERIC_PRECALL_URL
    print("=== EMAIL SUBJECT ===")
    print(PRECALL_EMAIL_SUBJECT)
    print("=== EMAIL ===")
    print("Hi,")
    print()
    print("CJ here with High Ticket Sales Academy. I am looking forward to connecting with you!")
    print()
    print("I put together a page with a few resources I would like you to see before our conversation.")
    print()
    print(f"Take a Look Before Our Call: {url}")
    print()
    print(
        "Start with the 4 minute video at the top. You will hear directly from four of our "
        "members about their experience getting placed into high ticket sales roles."
    )
    print()
    print(
        "When we connect, my goal is to learn more about your background and what you are "
        "looking to accomplish, and see whether high ticket sales is the right direction for you."
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
    print("Hey, CJ here with High Ticket Sales Academy. Looking forward to speaking with you!")
    print()
    print(
        "I put together a quick page to look through before our call. Start with the 4 minute "
        "video at the top. You will hear directly from four of our members about getting placed."
    )
    print()
    print(url)
    print()
    print("Quick question so I can come prepared: what made you book this call?")
