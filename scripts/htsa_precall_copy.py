"""Fail-safe pre-call email + text — zero variables, generic URL."""

from __future__ import annotations

# Tier 1 is the default page, so the link stays clean (no tier word for the prospect to see).
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
    print("CJ here with High Ticket Sales Academy. Looking forward to speaking with you.")
    print()
    print(
        "I put a few resources together to help you get a better understanding of what "
        "we do before we connect."
    )
    print()
    print(f"Take a Look Before Our Call: {url}")
    print()
    print(
        "Start with the short live coaching clip where four members discuss their placement "
        "experiences. I've also included an employer's perspective, independent reviews, "
        "and member stories if you'd like to explore further."
    )
    print()
    print(
        "When we connect, my goal is to understand where you are, where you want to go, "
        "and whether high-ticket sales is the right direction for you."
    )
    print()
    print("If it is, I'll walk you through what the path looks like.")
    print()
    print("Talk soon,")
    print()
    print("CJ Clay")
    print("Senior Career Transformation Coach")
    print("High Ticket Sales Academy")
    print("(616) 612-1735")
    print("cj@highticketsalesacademy.com")
    print()
    print("=== TEXT ===")
    print("Hey, CJ with High Ticket Sales Academy. Looking forward to our call.")
    print()
    print(
        "I put a few resources together for you. Start with the 4-minute clip of our "
        "members discussing placement on a live call with Chad:"
    )
    print()
    print(url)
    print()
    print("What's the biggest thing you want clarity on when we speak?")
