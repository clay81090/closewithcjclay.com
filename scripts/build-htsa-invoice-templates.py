#!/usr/bin/env python3
"""
Rebuild templates/htsa-placement-*.html from production reference HTML.
Does not modify any htsa-enrollment-*.html at repo root.

Sources (read-only):
  - Closer cash: htsa-enrollment-val-tappan.html
  - Closer cash + financing: htsa-enrollment-thomas-rulof.html + Splitit under PIF + URL normalize
  - Setter: htsa-enrollment-trameil-lee.html
  - Dual header/curriculum chunk: htsa-enrollment-jocelyn-navarro.html (layout only; terms/pay zone = Val/Thomas+Trameil)
  - Footer (HTML + CSS): htsa-enrollment-kristijo-sherman.html (brand-colored links, IG, Trustpilot + stars row)

Run from repo root: python3 scripts/build-htsa-invoice-templates.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
SNIPPETS = TEMPLATES / "snippets"
KRISTIJO_FOOTER_REF = ROOT / "htsa-enrollment-kristijo-sherman.html"

CLARITY_LEGACY_URL = "https://whop.com/checkout/1ba2LjGOo3B1Wpp4jf-eF61-w5X4-yCzD-25zhqI3VcVLf/"
CLARITY_PLAN_URL = "https://whop.com/checkout/plan_z5iuUhSgm9seH?d2c=true"


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


def normalize_clarity_urls(html: str) -> str:
    return html.replace(CLARITY_LEGACY_URL, CLARITY_PLAN_URL)


def val_tappan_pairs() -> list[tuple[str, str]]:
    return [
        ("hts_terms_gate_val_tappan_v1", "{{HTSA_STORAGE_KEY}}"),
        (
            "clientSlug: (panel.getAttribute('data-client-slug') || 'val-tappan').trim(),",
            "clientSlug: (panel.getAttribute('data-client-slug') || '{{HTSA_CLIENT_SLUG}}').trim(),",
        ),
        ('data-client-slug="val-tappan">', 'data-client-slug="{{HTSA_CLIENT_SLUG}}">'),
        ('data-phone="+18014580179"', 'data-phone="{{HTSA_PHONE_E164}}"'),
        ('data-email="gwamaval@gmail.com"', 'data-email="{{HTSA_EMAIL}}"'),
        ('data-full-name="Val Tappan"', 'data-full-name="{{HTSA_FULL_NAME}}"'),
        ("<title>HTSA Invoice — Val Tappan</title>", "<title>HTSA Invoice — {{HTSA_FULL_NAME}} (template)</title>"),
        ("Val Tappan</div>", "{{HTSA_FULL_NAME}}</div>"),
        (
            '<a href="mailto:gwamaval@gmail.com">gwamaval@gmail.com</a>',
            '<a href="mailto:{{HTSA_EMAIL}}">{{HTSA_EMAIL}}</a>',
        ),
        (
            '<a href="tel:+18014580179">+1 (801) 458-0179</a>',
            '<a href="tel:{{HTSA_PHONE_E164}}">{{HTSA_PHONE_DISPLAY}}</a>',
        ),
        ("Val, I really enjoyed", "{{HTSA_FIRST_NAME}}, I really enjoyed"),
        ("Val, review the in-house payment options", "{{HTSA_FIRST_NAME}}, review the in-house payment options"),
        (
            "Welcome to the <span>HTSA Family,</span> Val. 🎉",
            "Welcome to the <span>HTSA Family,</span> {{HTSA_FIRST_NAME}}. 🎉",
        ),
    ]


def jocelyn_dual_header_pairs() -> list[tuple[str, str]]:
    """Placeholder-ize the Jocelyn header + hero + billing + curriculum chunk only."""
    return [
        ("Jocelyn Navarro</div>", "{{HTSA_FULL_NAME}}</div>"),
        (
            '<a href="mailto:jocelynnavarro9717955@gmail.com">jocelynnavarro9717955@gmail.com</a>',
            '<a href="mailto:{{HTSA_EMAIL}}">{{HTSA_EMAIL}}</a>',
        ),
        (
            '<a href="tel:+15749716184">(574) 971-6184</a>',
            '<a href="tel:{{HTSA_PHONE_E164}}">{{HTSA_PHONE_DISPLAY}}</a>',
        ),
        ("Jocelyn, I really enjoyed", "{{HTSA_FIRST_NAME}}, I really enjoyed"),
    ]


def closer_invest_pay_zone_financing_pairs() -> list[tuple[str, str]]:
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
    html = html.replace(
        "then record your acceptance to unlock payment and financing buttons below.",
        "then record your acceptance to unlock payment buttons below.",
    )
    html = html.replace(
        "Payment and financing buttons stay locked until your Terms agreement has been recorded above.",
        "Payment buttons stay locked until your Terms agreement has been recorded above.",
    )
    html = html.replace(
        "✓ Terms recorded successfully. Payment and financing buttons below are now active for this browser session.",
        "✓ Terms recorded successfully. Payment buttons below are now active for this browser session.",
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


def extract_between(html: str, start_marker: str, end_marker: str) -> str:
    a = html.find(start_marker)
    if a == -1:
        raise RuntimeError(f"extract_between: start not found: {start_marker!r}")
    b = html.find(end_marker, a)
    if b == -1:
        raise RuntimeError(f"extract_between: end not found: {end_marker!r}")
    return html[a:b]


def extract_pay_zone_inner(html: str) -> str:
    needle = 'id="invest-pay-zone">'
    if needle not in html:
        raise RuntimeError("invest-pay-zone id not found")
    start = html.find(needle) + len(needle)
    marker = "  <!-- NEXT STEPS -->"
    end = html.find(marker, start)
    if end == -1:
        raise RuntimeError("NEXT STEPS not found after invest-pay-zone")
    return html[start:end].strip()


def extract_first_invest_box(inner: str) -> str:
    token = '<div class="invest-box">'
    start = inner.find(token)
    if start == -1:
        raise RuntimeError("invest-box not found in pay zone inner")
    pos = start + len(token)
    depth = 1
    while depth and pos < len(inner):
        next_div = inner.find("<div", pos)
        next_close = inner.find("</div>", pos)
        if next_close < 0:
            raise RuntimeError("unclosed invest-box")
        if next_div >= 0 and next_div < next_close:
            depth += 1
            pos = next_div + 4
        else:
            depth -= 1
            if depth == 0:
                return inner[start : next_close + 6]
            pos = next_close + 6
    raise RuntimeError("invest-box parse failed")


def extract_terms_and_hint(val_html: str) -> tuple[str, str, str]:
    """Returns (guarantee+terms block, hint line full <p...>, invest header sec-head)."""
    inv_head = extract_between(val_html, "  <!-- INVESTMENT -->\n", "  <!-- Performance guarantee")
    g1 = "  <!-- Performance guarantee — confirmed for this enrollment -->\n"
    g2 = '  <p id="invest-pay-zone-hint"'
    chunk = extract_between(val_html, g1, g2)
    hint_para = extract_between(val_html, g2, '  <div class="invest-wrap invest-pay-zone')
    return (inv_head.strip(), chunk.strip(), hint_para.rstrip())


def adapt_terms_dual(terms_chunk: str, *, financing: bool) -> str:
    s = terms_chunk.replace(
        "<li>Lifetime access to the closers mastermind community</li>",
        "<li>Lifetime access to the closers and setters mastermind communities</li>",
    )
    s = s.replace(
        "if it helps your close rate.</li>",
        "if it helps your performance in your role.</li>",
    )
    s = multi_replace(
        s,
        [
            ('data-full-name="Val Tappan"', 'data-full-name="{{HTSA_FULL_NAME}}"'),
            ('data-email="gwamaval@gmail.com"', 'data-email="{{HTSA_EMAIL}}"'),
            ('data-phone="+18014580179"', 'data-phone="{{HTSA_PHONE_E164}}"'),
            ('data-client-slug="val-tappan">', 'data-client-slug="{{HTSA_CLIENT_SLUG}}">'),
        ],
    )
    if financing:
        s = s.replace(
            "then record your acceptance to unlock payment buttons below.",
            "then record your acceptance to unlock payment and financing buttons below.",
        )
        s = s.replace(
            "✓ Terms recorded successfully. Payment buttons below are now active for this browser session.",
            "✓ Terms recorded successfully. Payment and financing buttons below are now active for this browser session.",
        )
    return s


def adapt_hint_dual(hint_para: str, *, financing: bool) -> str:
    if financing:
        return hint_para.replace(
            "Payment buttons stay locked until your Terms agreement has been recorded above.",
            "Payment and financing buttons stay locked until your Terms agreement has been recorded above.",
        )
    return hint_para


def compose_dual_pay_zone(closer_box: str, setter_box: str) -> str:
    rule = '\n      <hr class="invest-zone-rule" aria-hidden="true">\n\n      '
    return (
        '<div class="invest-wrap invest-pay-zone invest-pay-zone--locked" id="invest-pay-zone">\n'
        f"      {closer_box.strip()}\n"
        f"{rule}"
        f"{setter_box.strip()}\n"
        "  </div>"
    )


VAL_STEP1_SINGLE = (
    "        <h4>Step 1 — Choose Your Payment</h4>\n"
    "        <p>{{HTSA_FIRST_NAME}}, review the in-house payment options in Program Investment above, then select what you want — "
    "<strong>$6,000</strong> paid in full (or <strong>Splitit</strong> inside that same Whop checkout) or the <strong>$1,750 × 4-pay</strong> plan "
    "($7,000 total). Once your payment clears, move to Step 2 below.</p>"
)

DUAL_STEP1_CASH = (
    "        <h4>Step 1 — Choose Your Payment</h4>\n"
    "        <p>{{HTSA_FIRST_NAME}}, review the <strong>Closer</strong> and <strong>Setter</strong> payment options in Program Investment above. "
    "For <strong>Closer</strong>: <strong>$6,000</strong> paid in full (or <strong>Splitit</strong> in that same Whop checkout) or the "
    "<strong>$1,750 × 4-pay</strong> plan ($7,000 total). For <strong>Setter</strong>: <strong>$3,000</strong> paid in full or the "
    "<strong>$1,050 × 3-pay</strong> plan ($3,150 total). Complete the payment for the program you are starting first, then move to Step 2.</p>"
)

DUAL_STEP1_FIN = (
    "        <h4>Step 1 — Choose Your Payment or Financing</h4>\n"
    "        <p>{{HTSA_FIRST_NAME}}, review <strong>Closer</strong> and <strong>Setter</strong> options in Program Investment above. "
    "Each program has in-house Whop checkout (<strong>Closer:</strong> $6k PIF with Splitit in checkout, or $1,750 × 4-pay; "
    "<strong>Setter:</strong> $3k PIF or $1,050 × 3-pay) plus optional <strong>ClarityPay</strong> and <strong>Flexxbuy</strong> pre-qual links. "
    "Complete payment or financing for the program you are starting first, then move to Step 2.</p>"
)


def strip_legacy_templates() -> None:
    for p in TEMPLATES.glob("htsa-tpl-*.html"):
        p.unlink()


def build_dual_template(
    *,
    val_src: str,
    jocelyn_src: str,
    closer_html: str,
    setter_html: str,
    financing: bool,
) -> str:
    dual_top = extract_between(jocelyn_src, "  <!-- HEADER -->", "  <!-- CLOSER INVESTMENT -->")
    dual_top = multi_replace(dual_top, jocelyn_dual_header_pairs())

    inv_head, terms_chunk_raw, hint_raw = extract_terms_and_hint(val_src)
    terms_dual = adapt_terms_dual(terms_chunk_raw, financing=financing)
    hint_dual = adapt_hint_dual(hint_raw, financing=financing)
    closer_box = extract_first_invest_box(extract_pay_zone_inner(closer_html))
    setter_box = extract_first_invest_box(extract_pay_zone_inner(setter_html))
    pay_zone = compose_dual_pay_zone(closer_box, setter_box)

    investment_body = (
        "  <!-- INVESTMENT -->\n"
        + inv_head
        + "\n\n  "
        + terms_dual
        + "\n\n  "
        + hint_dual
        + "\n\n  "
        + pay_zone
        + "\n"
    )

    out = val_src
    old_upper = extract_between(out, "  <!-- HEADER -->", "  <!-- INVESTMENT -->")
    out = out.replace(old_upper, dual_top + "\n\n  <!-- INVESTMENT -->", 1)

    inv_mark = "  <!-- INVESTMENT -->\n"
    next_mark = "  <!-- NEXT STEPS -->"
    a = out.find(inv_mark)
    b = out.find(next_mark, a)
    if a == -1 or b == -1:
        raise RuntimeError("dual: could not find investment / next steps region")
    out = out[:a] + investment_body + "\n\n  " + out[b:]

    out = out.replace(
        '<div class="footer-bc-title">HTSA Closer</div>',
        '<div class="footer-bc-title">HTSA Closer &amp; Setter</div>',
    )

    out = multi_replace(out, val_tappan_pairs())
    if financing:
        out = out.replace(VAL_STEP1_SINGLE, DUAL_STEP1_FIN, 1)
    else:
        out = out.replace(VAL_STEP1_SINGLE, DUAL_STEP1_CASH, 1)
    return add_noindex(out)


def kristijo_footer_assets() -> tuple[str, str]:
    """Footer CSS block + footer HTML from Kristijo (reference-only file)."""
    t = KRISTIJO_FOOTER_REF.read_text(encoding="utf-8")
    idx = t.find("  /* Footer HTSA column")
    if idx == -1:
        raise RuntimeError("kristijo_footer_assets: CSS marker missing in reference HTML")
    header_media = t.find("  @media (max-width: 600px) {\n    .header {", idx)
    if header_media == -1:
        raise RuntimeError("kristijo_footer_assets: could not find main layout @media block after footer CSS")
    footer_css = t[idx:header_media]
    fstart = t.find("  <!-- FOOTER -->")
    fend = t.find("<script>", fstart)
    if fstart == -1 or fend == -1:
        raise RuntimeError("kristijo_footer_assets: footer HTML or <script> boundary missing")
    footer_html = t[fstart:fend].rstrip() + "\n\n"
    return footer_css, footer_html


def inject_kristijo_footer(html: str, footer_css: str, footer_html: str) -> str:
    """Insert Kristijo footer CSS (after business-card rules) and replace <!-- FOOTER -->…<script> region."""
    if "  /* Footer HTSA column" in html:
        return html
    anchor = "  .footer-bc-line--cal:hover {\n    color: var(--green-dark);\n  }\n\n"
    if anchor not in html:
        raise RuntimeError("inject_kristijo_footer: expected CSS anchor not found (.footer-bc-line--cal:hover)")
    html = html.replace(anchor, anchor + footer_css, 1)
    fstart = html.find("  <!-- FOOTER -->")
    fend = html.find("<script>", fstart)
    if fstart == -1 or fend == -1:
        raise RuntimeError("inject_kristijo_footer: footer region or <script> tag not found")
    return html[:fstart] + footer_html + html[fend:]


def main() -> None:
    TEMPLATES.mkdir(parents=True, exist_ok=True)
    SNIPPETS.mkdir(parents=True, exist_ok=True)

    (SNIPPETS / "payva-financing-block.html").write_text(payva_snippet(), encoding="utf-8")
    (SNIPPETS / "splitit-under-pif-closer.html").write_text(splitit_snippet(), encoding="utf-8")

    val_raw = (ROOT / "htsa-enrollment-val-tappan.html").read_text(encoding="utf-8")
    jocelyn_raw = (ROOT / "htsa-enrollment-jocelyn-navarro.html").read_text(encoding="utf-8")
    thomas_raw = normalize_clarity_urls(
        (ROOT / "htsa-enrollment-thomas-rulof.html").read_text(encoding="utf-8")
    )
    trameil_raw = (ROOT / "htsa-enrollment-trameil-lee.html").read_text(encoding="utf-8")

    p01 = add_noindex(multi_replace(val_raw, val_tappan_pairs()))
    p03 = add_noindex(multi_replace(trameil_raw, trameil_pairs()))
    p03 = setter_cash_only(p03)
    p04 = add_noindex(multi_replace(trameil_raw, trameil_pairs()))

    p02 = inject_splitit_closer_invest_pay_zone(
        add_noindex(multi_replace(thomas_raw, closer_invest_pay_zone_financing_pairs()))
    )
    p02 = normalize_clarity_urls(p02)

    p05 = build_dual_template(
        val_src=val_raw,
        jocelyn_src=jocelyn_raw,
        closer_html=p01,
        setter_html=p03,
        financing=False,
    )
    p06 = build_dual_template(
        val_src=val_raw,
        jocelyn_src=jocelyn_raw,
        closer_html=p02,
        setter_html=p04,
        financing=True,
    )

    strip_legacy_templates()

    footer_css, footer_html = kristijo_footer_assets()
    p01 = inject_kristijo_footer(p01, footer_css, footer_html)
    p02 = inject_kristijo_footer(p02, footer_css, footer_html)
    p03 = inject_kristijo_footer(p03, footer_css, footer_html)
    p04 = inject_kristijo_footer(p04, footer_css, footer_html)
    p05 = inject_kristijo_footer(p05, footer_css, footer_html)
    p06 = inject_kristijo_footer(p06, footer_css, footer_html)
    dual_footer_title = (
        '<div class="footer-bc-title">HTSA Closer</div>',
        '<div class="footer-bc-title">HTSA Closer &amp; Setter</div>',
    )
    p05 = p05.replace(dual_footer_title[0], dual_footer_title[1], 1)
    p06 = p06.replace(dual_footer_title[0], dual_footer_title[1], 1)

    (TEMPLATES / "htsa-placement-01-closer-cash-only.html").write_text(p01, encoding="utf-8")
    (TEMPLATES / "htsa-placement-02-closer-cash-financing.html").write_text(p02, encoding="utf-8")
    (TEMPLATES / "htsa-placement-03-setter-cash-only.html").write_text(p03, encoding="utf-8")
    (TEMPLATES / "htsa-placement-04-setter-cash-financing.html").write_text(p04, encoding="utf-8")
    (TEMPLATES / "htsa-placement-05-closer-setter-cash-only.html").write_text(p05, encoding="utf-8")
    (TEMPLATES / "htsa-placement-06-closer-setter-cash-financing.html").write_text(p06, encoding="utf-8")

    print("Wrote htsa-placement-01…06, snippets. Removed legacy htsa-tpl-*.html if present.")


if __name__ == "__main__":
    main()
