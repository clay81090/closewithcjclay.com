#!/usr/bin/env python3
"""Write six live demo enrollment pages (placement 01–06) from frozen templates.

Each page uses the same demo persona but a unique client slug / storage key so Terms
gate sessionStorage never collides. Pages stay noindex from the templates.

Run from repo root after rebuilding shells:
  python3 scripts/build-htsa-invoice-templates.py
  python3 scripts/rebuild-htsa-demo-enrollment-pages.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"

# (template file, output filename stem -> htsa-enrollment-{stem}.html, client slug, storage key suffix)
ROWS: list[tuple[str, str, str, str]] = [
    ("htsa-placement-01-closer-cash-only.html", "demo-01-closer-cash-only", "demo-01-closer-cash-only", "demo_01_closer_cash_only"),
    ("htsa-placement-02-closer-cash-financing.html", "demo-02-closer-cash-financing", "demo-02-closer-cash-financing", "demo_02_closer_cash_financing"),
    ("htsa-placement-03-setter-cash-only.html", "demo-03-setter-cash-only", "demo-03-setter-cash-only", "demo_03_setter_cash_only"),
    ("htsa-placement-04-setter-cash-financing.html", "demo-04-setter-cash-financing", "demo-04-setter-cash-financing", "demo_04_setter_cash_financing"),
    ("htsa-placement-05-closer-setter-cash-only.html", "demo-05-closer-setter-cash-only", "demo-05-closer-setter-cash-only", "demo_05_dual_cash_only"),
    ("htsa-placement-06-closer-setter-cash-financing.html", "demo-06-closer-setter-cash-financing", "demo-06-closer-setter-cash-financing", "demo_06_dual_cash_financing"),
]

DEMO_FULL_NAME = "Jordan Example"
DEMO_FIRST_NAME = "Jordan"
DEMO_EMAIL = "enrollment-demo@highticketsalesacademy.com"
DEMO_PHONE_E164 = "+15555550100"
DEMO_PHONE_DISPLAY = "+1 (555) 555-0100"

TITLE_BY_STEM = {
    "demo-01-closer-cash-only": "HTSA Demo — 01 Closer, cash only (no Splitit)",
    "demo-02-closer-cash-financing": "HTSA Demo — 02 Closer, cash + financing (+ Splitit under PIF)",
    "demo-03-setter-cash-only": "HTSA Demo — 03 Setter, cash only",
    "demo-04-setter-cash-financing": "HTSA Demo — 04 Setter, cash + financing",
    "demo-05-closer-setter-cash-only": "HTSA Demo — 05 Closer + Setter, cash only",
    "demo-06-closer-setter-cash-financing": "HTSA Demo — 06 Closer + Setter, cash + financing",
}


def main() -> None:
    for tpl_name, stem, slug, sk_suffix in ROWS:
        tpl = TEMPLATES / tpl_name
        if not tpl.is_file():
            raise SystemExit(f"Missing template: {tpl}")

        text = tpl.read_text(encoding="utf-8")
        repl = {
            "{{HTSA_FULL_NAME}}": DEMO_FULL_NAME,
            "{{HTSA_FIRST_NAME}}": DEMO_FIRST_NAME,
            "{{HTSA_EMAIL}}": DEMO_EMAIL,
            "{{HTSA_PHONE_E164}}": DEMO_PHONE_E164,
            "{{HTSA_PHONE_DISPLAY}}": DEMO_PHONE_DISPLAY,
            "{{HTSA_CLIENT_SLUG}}": slug,
            "{{HTSA_STORAGE_KEY}}": f"hts_terms_gate_{sk_suffix}_v1",
        }
        for k, v in repl.items():
            text = text.replace(k, v)

        # Production-style title: drop "(template)" and use clear demo label.
        text = text.replace(" (template)</title>", "</title>")
        new_title = TITLE_BY_STEM[stem]
        text = re.sub(r"<title>[^<]*</title>", f"<title>{new_title}</title>", text, count=1)

        out = ROOT / f"htsa-enrollment-{stem}.html"
        out.write_text(text, encoding="utf-8")
        print(f"Wrote {out.name}")

    print("Done. Live URLs: https://closewithcjclay.com/htsa-enrollment-{stem}.html (after push)")


if __name__ == "__main__":
    main()
