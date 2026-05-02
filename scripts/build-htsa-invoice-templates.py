#!/usr/bin/env python3
"""
One-off / maintenance: rebuild templates/*.html from current production sources.
Does not modify any htsa-enrollment-*.html at repo root.
Run from repo root: python3 scripts/build-htsa-invoice-templates.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
SNIPPETS = TEMPLATES / "snippets"


def add_noindex(html: str) -> str:
    if "noindex" in html:
        return html
    return html.replace(
        '<meta charset="UTF-8">',
        '<meta charset="UTF-8">\n<meta name="robots" content="noindex,nofollow">',
        1,
    )


def multi_replace(html: str, pairs: list[tuple[str, str]]) -> str:
    for old, new in sorted(pairs, key=lambda x: -len(x[0])):
        html = html.replace(old, new)
    return html


def matthew_pairs() -> list[tuple[str, str]]:
    return [
        ("hts_terms_gate_matthew_hedden_v1", "{{HTSA_STORAGE_KEY}}"),
        (
            "clientSlug: (panel.getAttribute('data-client-slug') || 'matthew-hedden').trim(),",
            "clientSlug: (panel.getAttribute('data-client-slug') || '{{HTSA_CLIENT_SLUG}}').trim(),",
        ),
        ('data-client-slug="matthew-hedden">', 'data-client-slug="{{HTSA_CLIENT_SLUG}}">'),
        ('data-phone="+16096516528"', 'data-phone="{{HTSA_PHONE_E164}}"'),
        ('data-email="hedden9414@gmail.com"', 'data-email="{{HTSA_EMAIL}}"'),
        ('data-full-name="Matthew Hedden"', 'data-full-name="{{HTSA_FULL_NAME}}"'),
        ("<title>HTSA Invoice — Matthew Hedden</title>", "<title>HTSA Invoice — {{HTSA_FULL_NAME}} (template)</title>"),
        ("Matthew Hedden</div>", "{{HTSA_FULL_NAME}}</div>"),
        (
            '<a href="mailto:hedden9414@gmail.com">hedden9414@gmail.com</a>',
            '<a href="mailto:{{HTSA_EMAIL}}">{{HTSA_EMAIL}}</a>',
        ),
        (
            '<a href="tel:+16096516528">+1 (609) 651-6528</a>',
            '<a href="tel:{{HTSA_PHONE_E164}}">{{HTSA_PHONE_DISPLAY}}</a>',
        ),
        ("Matthew, I really enjoyed", "{{HTSA_FIRST_NAME}}, I really enjoyed"),
        ("Matthew, review the payment options", "{{HTSA_FIRST_NAME}}, review the payment options"),
        (
            "Welcome to the <span>HTSA Family,</span> Matthew. 🎉",
            "Welcome to the <span>HTSA Family,</span> {{HTSA_FIRST_NAME}}. 🎉",
        ),
    ]


def angela_pairs() -> list[tuple[str, str]]:
    return [
        ("hts_terms_gate_angela_verdone_v1", "{{HTSA_STORAGE_KEY}}"),
        (
            "clientSlug: (panel.getAttribute('data-client-slug') || 'angela-verdone').trim(),",
            "clientSlug: (panel.getAttribute('data-client-slug') || '{{HTSA_CLIENT_SLUG}}').trim(),",
        ),
        ('data-client-slug="angela-verdone">', 'data-client-slug="{{HTSA_CLIENT_SLUG}}">'),
        ('data-phone="+17087521848"', 'data-phone="{{HTSA_PHONE_E164}}"'),
        ('data-email="angiejohnson040213@gmail.com"', 'data-email="{{HTSA_EMAIL}}"'),
        ('data-full-name="Angela Verdone"', 'data-full-name="{{HTSA_FULL_NAME}}"'),
        ("<title>HTSA Invoice — Angela Verdone</title>", "<title>HTSA Invoice — {{HTSA_FULL_NAME}} (template)</title>"),
        ("Angela Verdone</div>", "{{HTSA_FULL_NAME}}</div>"),
        (
            '<a href="mailto:angiejohnson040213@gmail.com">angiejohnson040213@gmail.com</a>',
            '<a href="mailto:{{HTSA_EMAIL}}">{{HTSA_EMAIL}}</a>',
        ),
        (
            '<a href="tel:+17087521848">+1 (708) 752-1848</a>',
            '<a href="tel:{{HTSA_PHONE_E164}}">{{HTSA_PHONE_DISPLAY}}</a>',
        ),
        ("Angela, I really enjoyed", "{{HTSA_FIRST_NAME}}, I really enjoyed"),
        ("<p>Angela, review the payment and financing options", "<p>{{HTSA_FIRST_NAME}}, review the payment and financing options"),
        (
            "Welcome to the <span>HTSA Family,</span> Angela. 🎉",
            "Welcome to the <span>HTSA Family,</span> {{HTSA_FIRST_NAME}}. 🎉",
        ),
        (
            "https://whop.com/checkout/1ba2LjGOo3B1Wpp4jf-eF61-w5X4-yCzD-25zhqI3VcVLf/",
            "https://whop.com/checkout/plan_z5iuUhSgm9seH",
        ),
    ]


def closer_invest_pay_zone_financing_pairs() -> list[tuple[str, str]]:
    """Placeholder-ize production HTML (invest-pay-zone + Whop + ClarityPay + Flexxbuy). Source file on disk is only the structural duplicate."""
    return [
        ("hts_terms_gate_thomas_rulof_v1", "{{HTSA_STORAGE_KEY}}"),
        (
            "clientSlug: (panel.getAttribute('data-client-slug') || 'thomas-rulof').trim(),",
            "clientSlug: (panel.getAttribute('data-client-slug') || '{{HTSA_CLIENT_SLUG}}').trim(),",
        ),
        ('data-client-slug="thomas-rulof">', 'data-client-slug="{{HTSA_CLIENT_SLUG}}">'),
        ('data-phone="+18046831541"', 'data-phone="{{HTSA_PHONE_E164}}"'),
        ('data-email="thomasrulof@gmail.com"', 'data-email="{{HTSA_EMAIL}}"'),
        ('data-full-name="Thomas Rulof"', 'data-full-name="{{HTSA_FULL_NAME}}"'),
        ("(Thomas enrollment only)", "(TEMPLATE — set client data before deploy)"),
        ("<title>HTSA Invoice — Thomas Rulof</title>", "<title>HTSA Invoice — {{HTSA_FULL_NAME}} (template)</title>"),
        ("Thomas Rulof</div>", "{{HTSA_FULL_NAME}}</div>"),
        (
            '<a href="mailto:thomasrulof@gmail.com">thomasrulof@gmail.com</a>',
            '<a href="mailto:{{HTSA_EMAIL}}">{{HTSA_EMAIL}}</a>',
        ),
        (
            '<a href="tel:+18046831541">+1 (804) 683-1541</a>',
            '<a href="tel:{{HTSA_PHONE_E164}}">{{HTSA_PHONE_DISPLAY}}</a>',
        ),
        ("Thomas, I really enjoyed", "{{HTSA_FIRST_NAME}}, I really enjoyed"),
        (
            "Thomas, review the payment and financing options",
            "{{HTSA_FIRST_NAME}}, review the payment and financing options",
        ),
        (
            "Welcome to the <span>HTSA Family,</span> Thomas. 🎉",
            "Welcome to the <span>HTSA Family,</span> {{HTSA_FIRST_NAME}}. 🎉",
        ),
    ]


def trameil_pairs() -> list[tuple[str, str]]:
    return [
        ("hts_terms_gate_trameil_lee_v1", "{{HTSA_STORAGE_KEY}}"),
        (
            "clientSlug: (panel.getAttribute('data-client-slug') || 'trameil-lee').trim(),",
            "clientSlug: (panel.getAttribute('data-client-slug') || '{{HTSA_CLIENT_SLUG}}').trim(),",
        ),
        ('data-client-slug="trameil-lee">', 'data-client-slug="{{HTSA_CLIENT_SLUG}}">'),
        ('data-phone="+13144436372"', 'data-phone="{{HTSA_PHONE_E164}}"'),
        ('data-email="tleelhs@gmail.com"', 'data-email="{{HTSA_EMAIL}}"'),
        ('data-full-name="Trameil Lee"', 'data-full-name="{{HTSA_FULL_NAME}}"'),
        (
            "<title>Certified HTS Setter — Trameil Lee | Certified High Ticket Setter Program</title>",
            "<title>Certified HTS Setter — {{HTSA_FULL_NAME}} | Certified High Ticket Setter Program (template)</title>",
        ),
        ("(Trameil Lee enrollment only)", "(TEMPLATE — set client data before deploy)"),
        ("Trameil Lee</div>", "{{HTSA_FULL_NAME}}</div>"),
        (
            '<a href="mailto:tleelhs@gmail.com">tleelhs@gmail.com</a>',
            '<a href="mailto:{{HTSA_EMAIL}}">{{HTSA_EMAIL}}</a>',
        ),
        (
            '<a href="tel:+13144436372">+1 (314) 443-6372</a>',
            '<a href="tel:{{HTSA_PHONE_E164}}">{{HTSA_PHONE_DISPLAY}}</a>',
        ),
        ("Trameil, I really enjoyed", "{{HTSA_FIRST_NAME}}, I really enjoyed"),
        (
            "<p>Trameil, review the <strong>Setter</strong> payment and financing options",
            "<p>{{HTSA_FIRST_NAME}}, review the <strong>Setter</strong> payment and financing options",
        ),
        (
            "Welcome to the <span>HTSA Family,</span> Trameil. 🎉",
            "Welcome to the <span>HTSA Family,</span> {{HTSA_FIRST_NAME}}. 🎉",
        ),
    ]


def strip_orange_guarantee(html: str) -> str:
    pattern = re.compile(
        r"\s*<div class=\"enrollment-guarantee-banner enrollment-guarantee-banner--pre-terms\">\s*"
        r"<div class=\"enrollment-guarantee-banner-title\">.*?</div>\s*<p>.*?</p>\s*</div>\s*",
        re.DOTALL,
    )
    html = pattern.sub("\n\n", html, count=1)
    html = html.replace(
        "  <!-- Performance guarantee — confirmed for this enrollment -->\n\n<div class=\"hts-terms-agreement-wrap\">",
        "  <!-- Orange performance guarantee omitted (no-guarantee template variant). -->\n\n  <div class=\"hts-terms-agreement-wrap\">",
        1,
    )
    return html


def setter_cash_only(html: str) -> str:
    marker_start = (
        '\n      <hr class="invest-zone-rule" aria-hidden="true">\n\n'
        '      <div class="invest-section-kicker invest-section-kicker--accent">Third-Party Financing Options</div>'
    )
    marker_note = (
        '      <div class="invest-note" style="color:#ff9c7a;"><strong>★ Soft pre-qualification only.</strong> '
        "Once you complete one of the Setter in-house payment options above or get approved through one of the financing options, "
        "text CJ right away so Setter access can be granted.</div>"
    )
    i = html.find(marker_start)
    j = html.find(marker_note)
    if i == -1 or j == -1:
        raise RuntimeError("setter_cash_only: could not find financing block markers")
    new_note = (
        '      <div class="invest-note" style="color:#ff9c7a;"><strong>★ Payment required.</strong> '
        "Once you complete one of the Setter in-house payment options above, text CJ right away so Setter access can be granted.</div>"
    )
    html = html[:i] + new_note + html[j + len(marker_note) :]
    html = html.replace(
        "<p><strong>Payment:</strong> USD — select option below</p>",
        "<p><strong>Payment:</strong> USD — in-house Whop ($3,000 PIF or $3,150 / 3-pay)</p>",
    )
    html = html.replace(
        "Payment: Select option below (charged in USD)",
        "Payment: In-house Whop — $3,000 PIF or $1,050 × 3-pay ($3,150 total); USD",
    )
    html = html.replace(
        "<p>{{HTSA_FIRST_NAME}}, review the <strong>Setter</strong> payment and financing options in Program Investment above — <strong>$3,000</strong> paid in full, the <strong>$1,050 × 3-pay</strong> plan ($3,150 total), or a soft pre-qualification link for <strong>ClarityPay</strong> or <strong>Flexxbuy</strong>. Once your payment clears or your financing is approved, move to Step 2 below.</p>",
        "<p>{{HTSA_FIRST_NAME}}, review the <strong>Setter</strong> payment options in Program Investment above — <strong>$3,000</strong> paid in full or the <strong>$1,050 × 3-pay</strong> plan ($3,150 total). Once your payment clears, move to Step 2 below.</p>",
    )
    return html


def payva_snippet() -> str:
    return """      <div class="invest-option-block financing">
        <div class="invest-badge financing">Financing Option (PayVa)</div>
        <div class="invest-option-head">
          <div>
            <div class="invest-option-title">PayVa</div>
            <div class="invest-option-sub">Strong option for higher credit profiles who want instant approval and immediate checkout.</div>
          </div>
          <div class="invest-price-stack">
            <div class="invest-price-big" style="font-size:22px;">Instant</div>
            <div class="invest-price-mini">decision path</div>
          </div>
        </div>
        <div class="invest-row">
          <span class="invest-label">Typical Credit Profile</span>
          <span class="invest-value">Higher credit profiles</span>
        </div>
        <div class="invest-row">
          <span class="invest-label">Enrollment Timing</span>
          <span class="invest-value">Same-day checkout when approved</span>
        </div>
        <div class="invest-option-actions">
          <a href="https://app.payva.com/checkout/overview/3ELuF3gxhI" class="invest-btn secondary" target="_blank" rel="noopener noreferrer">Pre-Qualify with PayVa →</a>
        </div>
      </div>
"""


def splitit_snippet() -> str:
    return """          <div class="invest-splitit-wrap">
            <p class="invest-splitit-intro">On the Whop checkout page, scroll to the <strong>bottom of the payment options</strong> — you'll see <strong>Splitit</strong> (monthly payments on your card). That's where you can set up the plan below.</p>
            <div class="invest-splitit-card">
              <div class="invest-splitit-head">Splitit — $500/month × 12 months</div>
              <p class="invest-splitit-apply"><strong>Apply here:</strong> use the same <strong>green "Choose PIF — Pay $6,000"</strong> button above, then select <strong>Splitit</strong> at the bottom of Whop's payment methods to complete setup.</p>
              <p class="invest-splitit-fine">No credit check — uses the existing limit on your Visa or Mastercard. A hold is placed on your card for the total amount. As you make each $500 monthly payment, that same amount is released back to your available credit.</p>
            </div>
          </div>
"""


SPLITIT_CSS_BLOCK = """
  /* Splitit note + detail (under $6k PIF) */
  .invest-splitit-wrap {
    margin-top: 16px;
    padding-top: 14px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  .invest-splitit-intro {
    font-size: 11.5px;
    line-height: 1.55;
    color: rgba(255, 255, 255, 0.55);
    margin: 0 0 12px;
  }

  .invest-splitit-intro strong {
    color: rgba(255, 255, 255, 0.88);
  }

  .invest-splitit-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 156, 122, 0.4);
    border-radius: 10px;
    padding: 14px 16px;
  }

  .invest-splitit-head {
    font-size: 13px;
    font-weight: 700;
    color: #ff9c7a;
    margin-bottom: 8px;
    letter-spacing: 0.02em;
  }

  .invest-splitit-apply {
    font-size: 11.5px;
    color: rgba(255, 255, 255, 0.78);
    margin: 0 0 10px;
    line-height: 1.55;
  }

  .invest-splitit-fine {
    font-size: 10.5px;
    line-height: 1.6;
    color: rgba(255, 255, 255, 0.48);
    margin: 0;
  }
"""


def inject_splitit_closer_invest_pay_zone(html: str) -> str:
    """Add Splitit CSS + under-PIF block + step copy (all closer shells include Splitit on cash)."""
    anchor_css = (
        "    opacity: 0.92;\n"
        "  }\n\n"
        "  .invest-grid {\n"
        "    display: grid;"
    )
    if anchor_css not in html:
        raise RuntimeError("inject_splitit: CSS anchor not found")
    if ".invest-splitit-wrap" in html:
        return html
    html = html.replace(
        anchor_css,
        "    opacity: 0.92;\n  }" + SPLITIT_CSS_BLOCK + "\n\n  .invest-grid {\n    display: grid;",
        1,
    )
    pif_then_opt2 = (
        '            <a href="https://whop.com/checkout/plan_hDgy1h7nsgiim?d2c=true" class="invest-btn" target="_blank" rel="noopener noreferrer">Choose PIF — Pay $6,000 →</a>\n'
        "          </div>\n"
        "        </div>\n\n"
        '        <div class="invest-option-block">\n'
        '          <div class="invest-badge invest-badge--option">Option 2</div>'
    )
    if pif_then_opt2 not in html:
        raise RuntimeError("inject_splitit: PIF / Option 2 anchor not found")
    html = html.replace(
        pif_then_opt2,
        '            <a href="https://whop.com/checkout/plan_hDgy1h7nsgiim?d2c=true" class="invest-btn" target="_blank" rel="noopener noreferrer">Choose PIF — Pay $6,000 →</a>\n'
        "          </div>\n"
        + splitit_snippet()
        + "        </div>\n\n"
        '        <div class="invest-option-block">\n'
        '          <div class="invest-badge invest-badge--option">Option 2</div>',
        1,
    )
    html = html.replace(
        "then select what you want — <strong>$6,000</strong> paid in full, the <strong>$1,750 × 4-pay</strong> plan",
        "then select what you want — <strong>$6,000</strong> paid in full (or <strong>Splitit</strong> inside that same Whop checkout), the <strong>$1,750 × 4-pay</strong> plan",
        1,
    )
    return html


def main() -> None:
    TEMPLATES.mkdir(parents=True, exist_ok=True)
    SNIPPETS.mkdir(parents=True, exist_ok=True)

    (SNIPPETS / "payva-financing-block.html").write_text(payva_snippet(), encoding="utf-8")
    (SNIPPETS / "splitit-under-pif-closer.html").write_text(splitit_snippet(), encoding="utf-8")

    t01 = add_noindex(multi_replace((ROOT / "htsa-enrollment-matthew-hedden.html").read_text(encoding="utf-8"), matthew_pairs()))
    (TEMPLATES / "htsa-tpl-01-closer-cash.html").write_text(t01, encoding="utf-8")

    t01b = strip_orange_guarantee(t01)
    (TEMPLATES / "htsa-tpl-01b-closer-cash-no-guarantee.html").write_text(t01b, encoding="utf-8")

    # Legacy second filename: identical to tpl-01 (closer cash always includes Splitit + 4-pay).
    (TEMPLATES / "htsa-tpl-02-closer-cash-splitit-4pay.html").write_text(t01, encoding="utf-8")

    t03 = add_noindex(multi_replace((ROOT / "htsa-enrollment-angela-verdone.html").read_text(encoding="utf-8"), angela_pairs()))
    (TEMPLATES / "htsa-tpl-03-closer-whop-plus-financing-splitit.html").write_text(t03, encoding="utf-8")

    t04 = add_noindex(multi_replace((ROOT / "htsa-enrollment-trameil-lee.html").read_text(encoding="utf-8"), trameil_pairs()))
    (TEMPLATES / "htsa-tpl-04-setter-cash-financing.html").write_text(t04, encoding="utf-8")

    t05 = setter_cash_only(t04)
    (TEMPLATES / "htsa-tpl-05-setter-cash-only.html").write_text(t05, encoding="utf-8")

    t06 = inject_splitit_closer_invest_pay_zone(
        add_noindex(
            multi_replace(
                (ROOT / "htsa-enrollment-thomas-rulof.html").read_text(encoding="utf-8"),
                closer_invest_pay_zone_financing_pairs(),
            )
        )
    )
    (TEMPLATES / "htsa-tpl-06-closer-whop-financing-invest-pay-zone.html").write_text(t06, encoding="utf-8")

    t06b = strip_orange_guarantee(t06)
    (TEMPLATES / "htsa-tpl-06b-closer-whop-financing-invest-pay-zone-no-guarantee.html").write_text(t06b, encoding="utf-8")

    for old_name in (
        "htsa-tpl-06-closer-whop-financing-thomas-ui.html",
        "htsa-tpl-06b-closer-whop-financing-thomas-ui-no-guarantee.html",
    ):
        old_path = TEMPLATES / old_name
        if old_path.exists():
            old_path.unlink()

    print("Wrote templates and snippets OK.")


if __name__ == "__main__":
    main()
