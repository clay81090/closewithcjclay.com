#!/usr/bin/env python3
"""
Rebuild templates/htsa-placement-*.html from production reference HTML.
Does not modify any htsa-enrollment-*.html at repo root except when you separately run
scripts/rebuild-htsa-demo-enrollment-pages.py (refreshes htsa-enrollment-demo-*.html).

Sources (read-only):
  - Closer cash: htsa-enrollment-val-tappan.html → three in-house options (PIF · Splitit · 4-pay)
  - Closer cash + financing: htsa-enrollment-thomas-rulof.html + same three-option closer stack
    (Closer ClarityPay must stay on the $7,200 Whop checkout — never the Setter plan.)
  - Setter: htsa-enrollment-trameil-lee.html
  - Dual header/curriculum chunk: htsa-enrollment-jocelyn-navarro.html (layout only; terms/pay zone = Val/Thomas+Trameil)
  - Member stories CSS+HTML + footer (HTML + footer-link CSS): htsa-enrollment-wayne-wintermute.html

Run from repo root: python3 scripts/build-htsa-invoice-templates.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
SNIPPETS = TEMPLATES / "snippets"
# Canonical layout: testimonials strip, colored footer icons, Trustpilot band.
CANONICAL_LAYOUT_REF = ROOT / "htsa-enrollment-wayne-wintermute.html"

# Success Coach kickoff (Mark) — default for new invoices. Chris link is temporary fallback only.
MARK_KICKOFF_URL = "https://meetings.hubspot.com/chad-aleo/member-success-team-kickoff-call"
CHRIS_KICKOFF_URL = (
    "https://meetings.hubspot.com/chris-vadinsky/chris-15-minute-kickoff-call-"
    "?uuid=518022ce-e2ba-4363-b678-470f8f9bce70"
)
_KICKOFF_MARK_BLOCK = f"""        <h4>Book Your Kickoff Call with Mark (Success Coach)</h4>
        <p>Mark is your Success Coach Director. This 15-minute Zoom call maps out your placement goals and makes sure you have everything you need before you begin the modules.</p>
        <a href="{MARK_KICKOFF_URL}" class="step-link" target="_blank">Book Kickoff Call →</a>"""
_KICKOFF_CHRIS_BLOCK = f"""        <h4>Book Your Kickoff Call with Chris (Success Coach)</h4>
        <p>Chris is one of our Success Coaches. This 15-minute Zoom call maps out your placement goals and makes sure you have everything you need before you begin the modules.</p>
        <a href="{CHRIS_KICKOFF_URL}" class="step-link" target="_blank" rel="noopener noreferrer">Book Kickoff Call →</a>"""


def apply_success_coach_kickoff_mark(html: str) -> str:
    """Replace Chris (or legacy) kickoff step with Mark (Success Coach) + HubSpot link."""
    if _KICKOFF_MARK_BLOCK in html:
        return html
    if _KICKOFF_CHRIS_BLOCK in html:
        return html.replace(_KICKOFF_CHRIS_BLOCK, _KICKOFF_MARK_BLOCK, 1)
    # Legacy / partial variants
    html = re.sub(
        r"<h4>Book Your Kickoff Call with Chris \(Success Coach\)</h4>\s*"
        r"<p>Chris is one of our Success Coaches\..*?</p>\s*"
        r'<a href="[^"]*" class="step-link"[^>]*>Book Kickoff Call →</a>',
        _KICKOFF_MARK_BLOCK,
        html,
        count=1,
        flags=re.DOTALL,
    )
    if _KICKOFF_MARK_BLOCK not in html:
        html = re.sub(
            r"<h4>Book Your Kickoff Call with Mark \(Success Coach\)</h4>\s*"
            r"<p>Mark is your Success Coach Director\..*?</p>\s*"
            r'<a href="[^"]*" class="step-link"[^>]*>Book Kickoff Call →</a>',
            _KICKOFF_MARK_BLOCK,
            html,
            count=1,
            flags=re.DOTALL,
        )
    return html


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


def sync_ref_strip_from_wayne(html: str, wayne_text: str) -> str:
    """Replace ref-strip CSS + HTML with Wayne's six-card Member voice layout (no Trinity column)."""
    css_start = "  /* Subtle member stories + book (above footer; site / Trustpilot / YouTube stay in footer) */\n"
    css_end = "  /* Enrollment-specific performance guarantee callout (orange) — optional; include HTML block only when needed */\n"
    html_start = "  <!-- Member stories & book (subtle; site / Trustpilot / YouTube in footer) -->\n"
    html_end = "  <!-- FOOTER -->\n"

    ws, we = wayne_text.find(css_start), wayne_text.find(css_end)
    if ws == -1 or we == -1:
        raise RuntimeError("sync_ref_strip: Wayne CSS markers not found")
    new_css = wayne_text[ws:we]

    hs, he = html.find(css_start), html.find(css_end)
    if hs == -1 or he == -1:
        raise RuntimeError("sync_ref_strip: target CSS markers not found")
    html = html[:hs] + new_css + html[he:]

    whs, whe = wayne_text.find(html_start), wayne_text.find(html_end)
    if whs == -1 or whe == -1:
        raise RuntimeError("sync_ref_strip: Wayne HTML markers not found")
    new_body = wayne_text[whs:whe]

    hhs, hhe = html.find(html_start), html.find(html_end)
    if hhs == -1 or hhe == -1:
        raise RuntimeError("sync_ref_strip: target HTML markers not found")
    html = html[:hhs] + new_body + html[hhe:]
    return html


def apply_footer_bc_title(html: str) -> str:
    """CJ business card title on enrollment footers."""
    html = html.replace(
        '<div class="footer-bc-title">HTSA Closer</div>',
        '<div class="footer-bc-title">HTSA - Career Transformation Coach</div>',
    )
    html = html.replace(
        '<div class="footer-bc-title">HTSA Closer &amp; Setter</div>',
        '<div class="footer-bc-title">HTSA - Career Transformation Coach &amp; Setter</div>',
    )
    return html


def apply_canonical_enrollment_copy(html: str) -> str:
    """Trustpilot line + Mastermind member count — single source of truth for new invoices."""
    html = html.replace(
        "Trustpilot Reviews — 4.9 out of 5",
        "Trustpilot Reviews — 4.9 stars out of 5",
    )
    html = re.sub(
        r"posted and \d+\+ members support each other",
        "posted and 590+ members support each other",
        html,
    )
    return html


TERMS_MASTERMIND_LINES = {
    "closer": "<strong>Facebook Mastermind</strong> — lifetime access to the closers community.",
    "setter": "<strong>Facebook Mastermind</strong> — lifetime access to the setters community.",
    "dual": "<strong>Facebook Mastermind</strong> — lifetime access to the closers and setters communities.",
}

ORANGE_GUARANTEE_BEFORE_TERMS = """  <!-- Performance guarantee — confirmed for this enrollment -->
  <div class="enrollment-guarantee-banner enrollment-guarantee-banner--pre-terms">
    <div class="enrollment-guarantee-banner-title">Performance Guarantee — Confirmed for This Enrollment</div>
    <p><strong>This performance guarantee applies to you.</strong> HTSA is <strong>confirming the program’s performance guarantee</strong> for your enrollment, provided you complete <strong>all</strong> required steps, milestones, and obligations exactly as described on this page and in your enrollment materials.</p>
  </div>

"""


def refresh_terms_gate_css(html: str) -> str:
    """Replace or insert scroll/banner/pdf CSS from templates/snippets/terms-gate-quick-read.css."""
    css = (SNIPPETS / "terms-gate-quick-read.css").read_text(encoding="utf-8").strip() + "\n\n"
    start_markers = (
        "  /* Scrollable enrollment terms quick-read",
        "  /* Practice preview: scrollable TOS quick-read",
    )
    end_marker = "\n\n  /* Subtle member stories + book (above footer; site / Trustpilot / YouTube stay in footer) */"
    for start in start_markers:
        si = html.find(start)
        if si == -1:
            continue
        ei = html.find(end_marker, si)
        if ei == -1:
            continue
        return html[:si] + css + html[ei:]
    anchor = end_marker
    pos = html.find(anchor)
    if pos == -1:
        return html
    return html[:pos] + "\n" + css + html[pos:]


def inject_terms_scroll_css(html: str) -> str:
    return refresh_terms_gate_css(html)


def apply_terms_gate_quick_read(html: str, program: str = "closer") -> str:
    """Partnership-tone scroll summary; orange banner overrides PDF 2-year experience for this enrollment."""
    html = refresh_terms_gate_css(html)
    form = (SNIPPETS / "terms-gate-quick-read-form.html").read_text(encoding="utf-8")
    form = form.replace(
        "{{HTSA_TERMS_MASTERMIND_LINE}}",
        TERMS_MASTERMIND_LINES.get(program, TERMS_MASTERMIND_LINES["closer"]),
    )
    pattern = (
        r'<p class="hts-terms-agreement-lead">.*?</label>\s*\n\s*'
        r'<button type="button" id="hts-terms-confirm-btn"'
    )
    if not re.search(pattern, html, flags=re.DOTALL):
        return html
    replacement = form + '\n        <button type="button" id="hts-terms-confirm-btn"'
    return re.sub(pattern, replacement, html, count=1, flags=re.DOTALL)


def ensure_orange_guarantee_before_terms(html: str) -> str:
    if '<div class="enrollment-guarantee-banner enrollment-guarantee-banner--pre-terms">' in html:
        return html
    needle = '  <div class="hts-terms-agreement-wrap">'
    if needle not in html:
        return html
    return html.replace(needle, ORANGE_GUARANTEE_BEFORE_TERMS + needle, 1)


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
            "<title>HTSA Setter Invoice — Trameil Lee</title>",
            "<title>Certified HTS Setter — {{HTSA_FULL_NAME}} | Certified High Ticket Setter Program (template)</title>",
        ),
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
    """Strip third-party financing; keep header/billing Payment line short (Wayne layout).

    Full Whop amounts belong in Program Investment only — long Payment lines in the
    header broke flex layout and no longer matched canonical closer invoices.
    """
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

    wayne_payment_meta = '<p><strong>Payment:</strong> Select payment option below</p>'
    html = html.replace(
        "<p><strong>Payment:</strong> USD — in-house Whop ($3,000 PIF or $3,150 / 3-pay)</p>",
        wayne_payment_meta,
    )
    html = html.replace(
        "<p><strong>Payment:</strong> USD — select option below</p>",
        wayne_payment_meta,
    )

    hero_p2_trameil = (
        '<p style="margin-top:10px;">Everything you need to review and get started is right here. '
        "The biggest difference at HTSA is that you are not just another number — we are true experts in high ticket sales, "
        "with <strong>around-the-clock support</strong> and placement into roles from a network of 300+ partner companies. "
        "Take your time reviewing and reach out to CJ with any questions or assistance with enrollment.</p>"
    )
    hero_p2_wayne = (
        '<p style="margin-top:10px;">Everything you need to review and get started is right here. '
        "The biggest difference at HTSA is that you are not just another number — we are not influencers, but true experts "
        "in the field of high ticket sales. You have around-the-clock support, and once certified, our team walks you directly "
        "into roles from a network of 300+ partner companies. Take your time reviewing and reach out to CJ with any questions "
        "or assistance with enrollment.</p>"
    )
    html = html.replace(hero_p2_trameil, hero_p2_wayne)

    billing_wayne_tail = "Program: Certified HTS Setter<br>\n        Payment: Select payment option below"
    html = html.replace(
        "Program: Certified HTS Setter<br>\n        Pricing: <strong>U.S. dollars (USD)</strong><br>\n        Payment: Select option below (charged in USD)",
        billing_wayne_tail,
    )
    html = html.replace(
        "Program: Certified HTS Setter<br>\n        Pricing: <strong>U.S. dollars (USD)</strong><br>\n        Payment: In-house Whop — $3,000 PIF or $1,050 × 3-pay ($3,150 total); USD",
        billing_wayne_tail,
    )

    # Logo alt matches Wayne / Val (brand), not a personal name.
    if 'class="logo-icon"' in html and 'alt="Chad Aleo"' in html:
        html = html.replace('alt="Chad Aleo"', 'alt="High Ticket Sales Academy"', 1)
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


SPLITIT_WHOP_URL = (
    "https://whop.com/checkout/4PcFLUerpZ8E73EomZ-xA27-pI2s-WLo0-Wd4UsuNEfoL2/"
)

CLOSER_ACCESS_HINT = (
    'All three options include <strong style="color:rgba(255,255,255,0.75);">immediate access</strong> '
    "once your payment clears."
)

CLOSER_PIF_SUB = (
    "Best overall value — $6,000 one-time (save $600 vs. the 12-month Splitit plan)."
)

CLOSER_STEP1 = (
    "        <h4>Step 1 — Choose Your Payment</h4>\n"
    "        <p>{{HTSA_FIRST_NAME}}, review the in-house payment options in Program Investment above, then choose what fits you best — "
    "<strong>$6,000</strong> paid in full, <strong>Splitit at $550/month</strong> ($6,600 total over 12 months at 0% interest), "
    "or the <strong>$1,750 × 4-pay</strong> plan ($7,000 total). Once your payment clears, move to Step 2 below.</p>"
)


def splitit_option2_block() -> str:
    return f"""        <div class="invest-option-block invest-option-block--splitit">
          <div class="invest-badge invest-badge--popular">Option 2 · 0% for 12 months</div>
          <div class="invest-option-head invest-option-head--pay">
            <div>
              <div class="invest-option-title">Splitit — $550/month × 12 months</div>
              <div class="invest-option-sub">0% interest. No loan application. Start tonight — keep cash in your account while you train.</div>
            </div>
            <div class="invest-price-stack">
              <div class="invest-price-big">$550/month</div>
              <div class="invest-price-mini">$6,600 total program investment</div>
            </div>
          </div>
          <div class="invest-option-actions invest-option-actions--pay">
            <a href="{SPLITIT_WHOP_URL}" class="invest-btn" target="_blank" rel="noopener noreferrer">Start With Splitit — $550/month →</a>
          </div>
          <div class="invest-splitit-card">
            <div class="invest-splitit-head">How Splitit Works</div>
            <p class="invest-splitit-fine">Uses the existing limit on your Visa or Mastercard. No loan application and no hard credit pull.</p>
            <p class="invest-splitit-fine">A temporary authorization is placed for the total amount while you make your monthly payments. As each payment is made, that same amount is released back to your available credit.</p>
            <ul class="invest-splitit-bullets">
              <li>✔ Immediate access</li>
              <li>✔ 0% interest</li>
              <li>✔ No credit check</li>
              <li>✔ Keep cash available while training</li>
            </ul>
          </div>
        </div>

"""


CLOSER_CASH_CSS_BLOCK = """
  /* Closer in-house: Splitit Option 2 (featured) + orange explainer card */
  .invest-option-block--splitit {
    border: 1px solid rgba(255, 156, 122, 0.55);
    background: rgba(255, 156, 122, 0.06);
    box-shadow: 0 0 0 1px rgba(255, 156, 122, 0.12), 0 8px 24px rgba(255, 156, 122, 0.08);
  }

  .invest-badge--popular {
    background: rgba(255, 156, 122, 0.18);
    color: #ff9c7a;
    border: 1px solid rgba(255, 156, 122, 0.45);
    letter-spacing: 1.2px;
  }

  .invest-splitit-card {
    margin-top: 14px;
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

  .invest-splitit-fine {
    font-size: 10.5px;
    line-height: 1.6;
    color: rgba(255, 255, 255, 0.55);
    margin: 0 0 8px;
  }

  .invest-splitit-bullets {
    margin: 10px 0 0;
    padding: 0 0 0 16px;
    font-size: 11px;
    line-height: 1.65;
    color: rgba(255, 255, 255, 0.72);
  }
"""


def splitit_snippet() -> str:
    """Legacy snippet name — returns Option 2 block for snippets/ copy."""
    return splitit_option2_block()


def remove_legacy_splitit_under_pif(html: str) -> str:
    """Remove old nested Splitit block under Option 1 PIF (full wrap + card)."""
    pattern = (
        r"\n\s*<div class=\"invest-splitit-wrap\">"
        r"[\s\S]*?"
        r"<p class=\"invest-splitit-fine\">[\s\S]*?</p>\s*\n"
        r"\s*</div>\s*\n"
        r"\s*</div>"
    )
    return re.sub(pattern, "\n", html, count=0)


def has_splitit_option2_block(html: str) -> bool:
    return 'class="invest-option-block invest-option-block--splitit"' in html


def inject_closer_cash_css(html: str) -> str:
    if ".invest-option-block--splitit {" in html and ".invest-badge--popular {" in html:
        return html
    old_splitit_css = "  /* Splitit note + detail (under $6k PIF) */"
    if old_splitit_css in html:
        html = re.sub(
            r"  /\* Splitit note \+ detail \(under \$6k PIF\) \*/[\s\S]*?(?=  \.invest-grid \{)",
            CLOSER_CASH_CSS_BLOCK.lstrip("\n") + "\n\n",
            html,
            count=1,
        )
        return html
    anchor_css = (
        "    opacity: 0.92;\n"
        "  }\n\n"
        "  .invest-grid {\n"
        "    display: grid;"
    )
    if anchor_css not in html:
        raise RuntimeError("inject_closer_cash_css: CSS anchor not found")
    return html.replace(
        anchor_css,
        "    opacity: 0.92;\n  }" + CLOSER_CASH_CSS_BLOCK + "\n\n  .invest-grid {\n    display: grid;",
        1,
    )


def apply_closer_three_inhouse_options(html: str) -> str:
    """Closer cash stack: Option 1 PIF · Option 2 Splitit · Option 3 4-pay."""
    html = inject_closer_cash_css(html)
    html = remove_legacy_splitit_under_pif(html)
    html = html.replace(
        'Choose PIF — Pay $6,000 →</a>\n          </div>\n          </div>\n        </div>',
        'Choose PIF — Pay $6,000 →</a>\n          </div>\n        </div>',
    )

    html = html.replace(
        'Either option includes <strong style="color:rgba(255,255,255,0.75);">immediate access</strong> once your payment clears.',
        CLOSER_ACCESS_HINT,
    )
    html = html.replace(
        "Best value — pay the remainder by day 30 and your total is only $6,000.",
        CLOSER_PIF_SUB,
    )

    four_pay_opt2 = (
        '        <div class="invest-option-block">\n'
        '          <div class="invest-badge invest-badge--option">Option 2</div>\n'
        '          <div class="invest-option-head invest-option-head--pay">\n'
        '            <div>\n'
        '              <div class="invest-option-title">4 Monthly Payments</div>'
    )
    four_pay_opt3 = (
        '        <div class="invest-option-block">\n'
        '          <div class="invest-badge invest-badge--option">Option 3</div>\n'
        '          <div class="invest-option-head invest-option-head--pay">\n'
        '            <div>\n'
        '              <div class="invest-option-title">4 Monthly Payments</div>'
    )

    if not has_splitit_option2_block(html):
        if four_pay_opt2 not in html and four_pay_opt3 in html:
            html = html.replace(
                four_pay_opt3,
                splitit_option2_block() + four_pay_opt3,
                1,
            )
        elif four_pay_opt2 in html:
            html = html.replace(
                four_pay_opt2,
                splitit_option2_block() + four_pay_opt3,
                1,
            )
        else:
            raise RuntimeError("apply_closer_three_inhouse_options: 4-pay anchor not found")
    elif four_pay_opt2 in html:
        html = html.replace(
            four_pay_opt2,
            splitit_option2_block() + four_pay_opt3,
            1,
        )

    html = update_closer_step1_paragraphs(html)
    return html


CLOSER_FIN_ACCESS_HINT = (
    'Both options include <strong style="color:rgba(255,255,255,0.75);">immediate access</strong> once your payment clears.'
)
CLOSER_FIN_PIF_SUB = "Best overall value — $6,000 one-time (save $1,000 vs. the 4-pay plan)."
CLOSER_FIN_STEP1_P = (
    "{{HTSA_FIRST_NAME}}, review the payment and financing options in Program Investment above, then select what you want — "
    "<strong>$6,000</strong> paid in full, the <strong>$1,750 × 4-pay</strong> plan ($7,000 total), or "
    "<strong>ClarityPay</strong> at <strong>$600/month × 12 months</strong> (0% APR, $7,200 total — 620+ credit score to qualify). "
    "Once your payment clears or your financing is approved, move to Step 2 below."
)

_CLOSER_CLARITY_FINANCING_SECTION = """      <div class="invest-section-kicker invest-section-kicker--accent">Third-Party Financing</div>
      <div class="invest-note" style="margin-top:0;margin-bottom:14px;">The options above are HTSA in-house payment options. The option below is third-party financing through ClarityPay for pre-qualification.</div>

      <div class="invest-grid">

        <div class="invest-option-block financing">
          <div class="invest-badge financing">ClarityPay</div>
          <div class="invest-option-head">
            <div>
              <div class="invest-option-title">ClarityPay — 12 months at 0% APR</div>
              <div class="invest-option-sub">$600/month × 12 months — $7,200 total program investment. Need <strong>620+ credit score</strong> to qualify.</div>
            </div>
            <div class="invest-price-stack">
              <div class="invest-price-big">$600/month</div>
              <div class="invest-price-mini">$7,200 total · 12 months · 0% APR</div>
            </div>
          </div>
          <div class="invest-row">
            <span class="invest-label">Credit Requirement</span>
            <span class="invest-value">620+ credit score to qualify</span>
          </div>
          <div class="invest-row">
            <span class="invest-label">Interest Rate</span>
            <span class="invest-value">0% APR · no early payoff penalty</span>
          </div>
          <div class="invest-row">
            <span class="invest-label">Enrollment Timing</span>
            <span class="invest-value">Enroll same day if approved</span>
          </div>
          <div class="invest-option-actions">
            <a href="https://whop.com/checkout/1ba2LjGOo3B1Wpp4jf-eF61-w5X4-yCzD-25zhqI3VcVLf/" class="invest-btn secondary" target="_blank">Pre-Qualify with ClarityPay →</a>
          </div>
        </div>

      </div>

      <div class="invest-note" style="color:#ff9c7a;"><strong>★ Soft pre-qualification only.</strong> Once you complete one of the in-house payment options above or get approved through ClarityPay, text CJ right away so access can be granted.</div>"""


def apply_closer_cash_financing_modern_stack(html: str) -> str:
    """Closer cash + financing: PIF + 4-pay in-house; ClarityPay only ($600/mo × 12, 0% APR, $7,200). No Splitit or Flexxbuy."""
    html = html.replace(CLOSER_ACCESS_HINT, CLOSER_FIN_ACCESS_HINT)
    html = html.replace(CLOSER_PIF_SUB, CLOSER_FIN_PIF_SUB)
    if has_splitit_option2_block(html):
        html = re.sub(
            r"\n        <div class=\"invest-option-block invest-option-block--splitit\">[\s\S]*?"
            r"</div>\n\n        <div class=\"invest-option-block\">\n"
            r"          <div class=\"invest-badge invest-badge--option\">Option 3</div>",
            '\n        <div class="invest-option-block">\n'
            '          <div class="invest-badge invest-badge--option">Option 2</div>',
            html,
            count=1,
        )
    html = re.sub(
        r"      <div class=\"invest-section-kicker invest-section-kicker--accent\">Third-Party Financing Options?</div>[\s\S]*?"
        r"<div class=\"invest-note\" style=\"color:#ff9c7a;\"><strong>★ Soft pre-qualification only\.</strong> Once you complete one of the in-house payment options above or get approved through[^<]+</div>",
        _CLOSER_CLARITY_FINANCING_SECTION,
        html,
        count=1,
    )
    html = re.sub(
        r"<p>\{\{HTSA_FIRST_NAME\}\}, review the payment and financing options in Program Investment above[^<]+</p>",
        f"<p>{CLOSER_FIN_STEP1_P}</p>",
        html,
        count=1,
    )
    return html


def update_closer_step1_paragraphs(html: str) -> str:
    old_patterns = [
        (
            "{{HTSA_FIRST_NAME}}, review the in-house payment options in Program Investment above, then select what you want — "
            "<strong>$6,000</strong> paid in full or the <strong>$1,750 × 4-pay</strong> plan "
            "($7,000 total). Once your payment clears, move to Step 2 below."
        ),
        (
            "{{HTSA_FIRST_NAME}}, review the in-house payment options in Program Investment above, then select what you want — "
            "<strong>$6,000</strong> paid in full (or <strong>Splitit</strong> inside that same Whop checkout) or the "
            "<strong>$1,750 × 4-pay</strong> plan ($7,000 total). Once your payment clears, move to Step 2 below."
        ),
        (
            "{{HTSA_FIRST_NAME}}, review the in-house payment options in Program Investment above, then select what you want — "
            "<strong>$6,000</strong> paid in full, the <strong>$1,750 × 4-pay</strong> plan"
        ),
    ]
    step1_p = CLOSER_STEP1.split("<p>", 1)[1].rsplit("</p>", 1)[0]
    for old in old_patterns:
        if old in html:
            html = html.replace(old, step1_p, 1)
    return html


def inject_splitit_closer_invest_pay_zone(html: str) -> str:
    """Backward-compatible name — applies three-option closer cash stack."""
    return apply_closer_three_inhouse_options(html)


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


VAL_STEP1_SINGLE = CLOSER_STEP1

_PLACEMENT_01_HERO_OLD = (
    "{{HTSA_FIRST_NAME}}, I really enjoyed speaking with you earlier. Your background as a retired engineer came through in how thoughtfully "
    "you approached the opportunity, and it was clear from our conversation that you're someone who takes their future seriously and is ready "
    "to make a real change — exactly the kind of person we love working with here at High Ticket Sales Academy."
)

_PLACEMENT_01_HERO_NEW = (
    "{{HTSA_FIRST_NAME}}, I really enjoyed speaking with you earlier. It was clear from our conversation that you're someone who takes their "
    "future seriously and is ready to make a real change — and that's exactly the kind of person we love working with here at High Ticket Sales Academy."
)


def placement_01_closer_cash_only(html: str) -> str:
    """Closer cash-only shell 01: generic hero only (three-option stack applied earlier)."""
    return html.replace(_PLACEMENT_01_HERO_OLD, _PLACEMENT_01_HERO_NEW, 1)


DUAL_STEP1_CASH = (
    "        <h4>Step 1 — Choose Your Payment</h4>\n"
    "        <p>{{HTSA_FIRST_NAME}}, review the <strong>Closer</strong> and <strong>Setter</strong> payment options in Program Investment above. "
    "For <strong>Closer</strong>: <strong>$6,000</strong> paid in full, <strong>Splitit at $550/month</strong> ($6,600 total at 0% over 12 months), "
    "or the <strong>$1,750 × 4-pay</strong> plan ($7,000 total). For <strong>Setter</strong>: <strong>$3,000</strong> paid in full or the "
    "<strong>$1,050 × 3-pay</strong> plan ($3,150 total). Complete the payment for the program you are starting first, then move to Step 2.</p>"
)

DUAL_STEP1_FIN = (
    "        <h4>Step 1 — Choose Your Payment or Financing</h4>\n"
    "        <p>{{HTSA_FIRST_NAME}}, review <strong>Closer</strong> and <strong>Setter</strong> options in Program Investment above. "
    "For <strong>Closer</strong>: <strong>$6,000</strong> paid in full, the <strong>$1,750 × 4-pay</strong> plan ($7,000 total), or "
    "<strong>ClarityPay</strong> at <strong>$600/month × 12 months</strong> (0% APR, $7,200 total — 620+ credit score to qualify). "
    "For <strong>Setter</strong>: <strong>$3,000</strong> paid in full, the <strong>$1,050 × 3-pay</strong> plan ($3,150 total), or "
    "optional <strong>ClarityPay</strong> / <strong>Flexxbuy</strong> pre-qual links. "
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


def canonical_footer_assets() -> tuple[str, str]:
    """Footer link-row CSS + footer HTML from Wayne (colored icons, Trustpilot band)."""
    t = CANONICAL_LAYOUT_REF.read_text(encoding="utf-8")
    idx = t.find("  /* Footer HTSA column")
    if idx == -1:
        raise RuntimeError("canonical_footer_assets: CSS marker missing in Wayne reference HTML")
    header_media = t.find("  @media (max-width: 600px) {\n    .header {", idx)
    if header_media == -1:
        raise RuntimeError("canonical_footer_assets: could not find main layout @media block after footer CSS")
    footer_css = t[idx:header_media]
    fstart = t.find("  <!-- FOOTER -->")
    fend = t.find("<script>", fstart)
    if fstart == -1 or fend == -1:
        raise RuntimeError("canonical_footer_assets: footer HTML or <script> boundary missing")
    footer_html = t[fstart:fend].rstrip() + "\n\n"
    return footer_css, footer_html


def inject_canonical_footer(html: str, footer_css: str, footer_html: str) -> str:
    """Insert Wayne footer CSS (after business-card rules) and replace <!-- FOOTER -->…<script> region."""
    if "  /* Footer HTSA column" in html:
        return html
    anchor = "  .footer-bc-line--cal:hover {\n    color: var(--green-dark);\n  }\n\n"
    if anchor not in html:
        raise RuntimeError("inject_canonical_footer: expected CSS anchor not found (.footer-bc-line--cal:hover)")
    html = html.replace(anchor, anchor + footer_css, 1)
    fstart = html.find("  <!-- FOOTER -->")
    fend = html.find("<script>", fstart)
    if fstart == -1 or fend == -1:
        raise RuntimeError("inject_canonical_footer: footer region or <script> tag not found")
    return html[:fstart] + footer_html + html[fend:]


def main() -> None:
    TEMPLATES.mkdir(parents=True, exist_ok=True)
    SNIPPETS.mkdir(parents=True, exist_ok=True)

    (SNIPPETS / "payva-financing-block.html").write_text(payva_snippet(), encoding="utf-8")
    (SNIPPETS / "splitit-under-pif-closer.html").write_text(splitit_option2_block(), encoding="utf-8")

    val_raw = (ROOT / "htsa-enrollment-val-tappan.html").read_text(encoding="utf-8")
    jocelyn_raw = (ROOT / "htsa-enrollment-jocelyn-navarro.html").read_text(encoding="utf-8")
    thomas_raw = (ROOT / "htsa-enrollment-thomas-rulof.html").read_text(encoding="utf-8")
    trameil_raw = (ROOT / "htsa-enrollment-trameil-lee.html").read_text(encoding="utf-8")
    wayne_text = CANONICAL_LAYOUT_REF.read_text(encoding="utf-8")

    p01_val = add_noindex(multi_replace(val_raw, val_tappan_pairs()))
    p01_val = sync_ref_strip_from_wayne(p01_val, wayne_text)
    p01_val = apply_closer_three_inhouse_options(p01_val)
    p01 = placement_01_closer_cash_only(p01_val)
    p03 = add_noindex(multi_replace(trameil_raw, trameil_pairs()))
    p03 = setter_cash_only(p03)
    p03 = sync_ref_strip_from_wayne(p03, wayne_text)
    p04 = add_noindex(multi_replace(trameil_raw, trameil_pairs()))
    p04 = sync_ref_strip_from_wayne(p04, wayne_text)

    p02 = apply_closer_three_inhouse_options(
        add_noindex(multi_replace(thomas_raw, closer_invest_pay_zone_financing_pairs()))
    )
    p02 = apply_closer_cash_financing_modern_stack(p02)
    p02 = sync_ref_strip_from_wayne(p02, wayne_text)

    p05 = build_dual_template(
        val_src=val_raw,
        jocelyn_src=jocelyn_raw,
        closer_html=p01_val,
        setter_html=p03,
        financing=False,
    )
    p05 = sync_ref_strip_from_wayne(p05, wayne_text)
    p06 = build_dual_template(
        val_src=val_raw,
        jocelyn_src=jocelyn_raw,
        closer_html=p02,
        setter_html=p04,
        financing=True,
    )
    p06 = sync_ref_strip_from_wayne(p06, wayne_text)

    strip_legacy_templates()

    footer_css, footer_html = canonical_footer_assets()
    p01 = inject_canonical_footer(p01, footer_css, footer_html)
    p02 = inject_canonical_footer(p02, footer_css, footer_html)
    p03 = inject_canonical_footer(p03, footer_css, footer_html)
    p04 = inject_canonical_footer(p04, footer_css, footer_html)
    p05 = inject_canonical_footer(p05, footer_css, footer_html)
    p06 = inject_canonical_footer(p06, footer_css, footer_html)
    dual_footer_title = (
        '<div class="footer-bc-title">HTSA - Career Transformation Coach</div>',
        '<div class="footer-bc-title">HTSA - Career Transformation Coach &amp; Setter</div>',
    )
    p05 = p05.replace(dual_footer_title[0], dual_footer_title[1], 1)
    p06 = p06.replace(dual_footer_title[0], dual_footer_title[1], 1)

    p01 = apply_canonical_enrollment_copy(p01)
    p02 = apply_canonical_enrollment_copy(p02)
    p03 = apply_canonical_enrollment_copy(p03)
    p04 = apply_canonical_enrollment_copy(p04)
    p05 = apply_canonical_enrollment_copy(p05)
    p06 = apply_canonical_enrollment_copy(p06)

    p01 = apply_terms_gate_quick_read(p01, "closer")
    p02 = apply_terms_gate_quick_read(p02, "closer")
    p03 = apply_terms_gate_quick_read(p03, "setter")
    p04 = apply_terms_gate_quick_read(p04, "setter")
    p05 = apply_terms_gate_quick_read(p05, "dual")
    p06 = apply_terms_gate_quick_read(p06, "dual")

    p01 = apply_success_coach_kickoff_mark(p01)
    p02 = apply_success_coach_kickoff_mark(p02)
    p03 = apply_success_coach_kickoff_mark(p03)
    p04 = apply_success_coach_kickoff_mark(p04)
    p05 = apply_success_coach_kickoff_mark(p05)
    p06 = apply_success_coach_kickoff_mark(p06)

    p01, p02, p03, p04, p05, p06 = [
        apply_footer_bc_title(p) for p in (p01, p02, p03, p04, p05, p06)
    ]

    practice_path = ROOT / "htsa-enrollment-cj-clay-practice.html"
    if practice_path.is_file():
        practice_html = practice_path.read_text(encoding="utf-8")
        practice_html = ensure_orange_guarantee_before_terms(practice_html)
        practice_html = apply_terms_gate_quick_read(practice_html, "closer")
        practice_html = apply_canonical_enrollment_copy(practice_html)
        practice_html = apply_success_coach_kickoff_mark(practice_html)
        practice_path.write_text(practice_html, encoding="utf-8")

    (TEMPLATES / "htsa-placement-01-closer-cash-only.html").write_text(p01, encoding="utf-8")
    (TEMPLATES / "htsa-placement-02-closer-cash-financing.html").write_text(p02, encoding="utf-8")
    (TEMPLATES / "htsa-placement-03-setter-cash-only.html").write_text(p03, encoding="utf-8")
    (TEMPLATES / "htsa-placement-04-setter-cash-financing.html").write_text(p04, encoding="utf-8")
    (TEMPLATES / "htsa-placement-05-closer-setter-cash-only.html").write_text(p05, encoding="utf-8")
    (TEMPLATES / "htsa-placement-06-closer-setter-cash-financing.html").write_text(p06, encoding="utf-8")

    print("Wrote htsa-placement-01…06, snippets. Removed legacy htsa-tpl-*.html if present.")


if __name__ == "__main__":
    main()
