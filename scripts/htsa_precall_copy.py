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
    print("Looking forward to connecting. Here is a quick page to look at before we talk:")
    print()
    print(f"Click Here to Review the Pre-Call Page: {url}")
    print()
    print(
        "The 4 minute clip at the top is four of our members talking about getting "
        "placed and having more than one offer to choose from. It is not homework, "
        "just a look at what is possible."
    )
    print()
    print("Come with your real situation and your real questions, and we will dive right in.")
    print()
    print("Best,")
    print()
    print("CJ Clay")
    print("HTSA, Senior Career Transformation Coach")
    print("(616) 612-1735")
    print("cj@highticketsalesacademy.com")
    print()
    print("=== TEXT ===")
    print("Hey, looking forward to our call! Here is a quick page to look at before we talk:")
    print()
    print(url)
    print()
    print(
        "The 4 minute clip is four of our members talking about getting placed. "
        "Not homework, just come with your real questions and we will dive right in."
    )
