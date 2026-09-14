"""Shared send-pack copy for close pages.

Voice rule: mostly commas and periods so it reads human. Use a hyphen or an em
dash only when it is genuinely the clearest way to say a thing (compound
adjectives like "30-day", or a single em dash inside a long sentence). Never
use dashes for stylistic filler.
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

    Voice: warm, direct, human. Commas and periods most of the time.
    A single em dash is fine when the sentence genuinely needs it.
    """
    print("=== EMAIL SUBJECT ===")
    print("Your enrollment page")
    print("=== EMAIL ===")
    print(f"Hi {first},")
    print()
    print(
        "Good conversation today. You asked good questions, "
        "which is the reason I'm sending this instead of just a link."
    )
    print()
    print(
        "You've made enough decisions with real money behind them to know the difference "
        "between a program that sounds right and one that holds up when you check it. "
        "So here's your page, and here's how to check it."
    )
    print()
    print("Your enrollment page:")
    print()
    print(enroll)
    print()
    print(
        "Two things to look at while you're in there. "
        "The 30-day action plan at the bottom is the part most people skip and it's the part "
        "that matters. It's the actual sequence from day one to placed, with dates attached, "
        "not a promise. And the proof section is there so you don't have to take my word for "
        "anything I said on our call: video testimonials from members, testimonials from the "
        "companies that hire out of our network, Chad's book, our reviews. I'd rather you "
        "validate it yourself than believe me."
    )
    print()
    print("The three things worth verifying before you commit to anything:")
    print()
    print(
        "Placement is a person's job here, not a job board. Nate's entire role is getting you "
        "in front of companies already looking. Ask anyone in the reviews about that specifically."
    )
    print()
    print(
        "It's backed in writing. If we don't place you inside 50 interviews or six months, "
        "you get refunded. The longest it's ever taken us is 15 interviews."
    )
    print()
    print(
        "There's nothing recurring. No monthly to stay in, no fees after placement, lifetime "
        "access to the training and coaching, and lifetime placement. We'll move you to a better "
        "offer in a year if you've earned it."
    )
    print()
    print(
        "If anything on that page raises a question, call or text me directly. "
        "I'd rather answer it now than have you sit on it."
    )
    print()
    print("CJ Clay")
    print("HTSA, Career Transformation Coach")
    print("(616) 612-1735")
    print("cj@highticketsalesacademy.com")
    print()
    print("=== TEXT (send right after the email) ===")
    print(
        f"{first}, just emailed you everything we walked through. "
        f"Link's in there, or here if it's easier: {enroll}"
    )
    print()
    print(
        "Worth pulling up on a computer rather than your phone. The 30-day plan and the proof "
        "section are both at the bottom and they read a lot better on a real screen. "
        "Any questions, call or text me directly."
    )
    print()
    print("CJ")
