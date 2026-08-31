#!/usr/bin/env python3
"""Print text + email for an existing close page. Does not rebuild anything.

  python3 scripts/htsa-send-pack.py --full-name "Test Person"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from htsa_close_copy import (  # noqa: E402
    enroll_url_from_name,
    first_name,
    first_name_from_html,
    game_url,
    page_path,
    print_send_pack,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full-name", required=True)
    args = ap.parse_args()
    path = page_path(ROOT, args.full_name)
    if not path.is_file():
        raise SystemExit(
            f"No close page at {path.name}. Need Email, Phone, and which options."
        )
    html = path.read_text(encoding="utf-8")
    first = first_name_from_html(html) or first_name(args.full_name)
    enroll = enroll_url_from_name(args.full_name)
    print_send_pack(first, enroll, game_url(first))


if __name__ == "__main__":
    main()
