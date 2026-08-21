#!/usr/bin/env python3
"""Pre-call resource pages at closewithcjclay.com/r/<first_last>/.

Standing template: resources only. No discovery, no demo, no pricing, no gate.
Confirm button only on the call card.

Usage:
  python3 scripts/precall-resource.py create \\
    --full-name "Sarah Nitterauer" \\
    --email "sarahnitterauer@gmail.com" \\
    --phone-e164 "+18282158111" \\
    --phone-display "+1 (828) 215-8111" \\
    --call-day "Wednesday" --call-date "Aug 12" \\
    --call-time "3:00 PM" --timezone "EST" \\
    --call-format "Phone or Zoom" \\
    --ship
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "resource-links" / "data"
DEFAULTS_PATH = DATA_DIR / "_precall-defaults.json"
REGISTRY_PATH = ROOT / "resource-links" / "registry.json"
MANIFEST_PATH = ROOT / "r" / "_manifest.json"
R_DIR = ROOT / "r"
ASSETS_DIR = ROOT / "resource-links" / "assets"
EXPIRED_TEMPLATE = ROOT / "resource-links" / "templates" / "expired.html"

EXPIRE_DAYS = 90
GAS_ENDPOINT = (
    "https://script.google.com/macros/s/"
    "AKfycbxeyf0Q_wiM-d6pq5DnBNKUDVTvMvzFwD60DPpjMEm60LnIQ2tjSkGmy5u1Gt5sQa4Jng/exec"
)
CUSTOM_SLUG_RE = re.compile(r"^[a-z0-9_-]{3,40}$")
LIVE_POLL_INTERVAL_SEC = 10
LIVE_POLL_TIMEOUT_SEC = 360


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def client_slug(full_name: str) -> str:
    return "_".join(full_name.strip().lower().split())


def first_name(full_name: str) -> str:
    parts = full_name.strip().split()
    return parts[0] if parts else "Friend"


def normalize_slug(raw: str) -> str:
    slug = raw.strip().lower().replace(" ", "_")
    if not CUSTOM_SLUG_RE.match(slug):
        raise SystemExit("Slug must be 3–40 chars: lowercase letters, numbers, underscore, hyphen")
    return slug


def load_registry() -> dict:
    if REGISTRY_PATH.exists():
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {"links": {}, "updated_at": iso(utcnow())}


def write_manifest(reg: dict) -> None:
    manifest = {
        "updated_at": reg.get("updated_at", iso(utcnow())),
        "links": {},
    }
    for slug, link in reg.get("links", {}).items():
        manifest["links"][slug] = {
            "status": link.get("status", "killed"),
            "expires_at": link.get("expires_at"),
            "view_count": link.get("view_count", 0),
            "last_viewed_at": link.get("last_viewed_at"),
        }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def save_registry(reg: dict) -> None:
    reg["updated_at"] = iso(utcnow())
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
    write_manifest(reg)


def load_defaults() -> dict:
    if DEFAULTS_PATH.is_file():
        return json.loads(DEFAULTS_PATH.read_text(encoding="utf-8"))
    return {}


def enrollment_css() -> str:
    """Reuse Tammy CSS as-is (no edits). Email-gate CSS is unused without the HTML."""
    return (ASSETS_DIR / "enrollment-styles.css").read_text(encoding="utf-8")


def logo_html() -> str:
    html = (ASSETS_DIR / "logo-snippet.html").read_text(encoding="utf-8").strip()
    return html.replace('alt="Val Tappan"', 'alt="Chad Aleo"')


def footer_html() -> str:
    """Footer markup only — strip enrollment Terms-gate <script> leftovers."""
    raw = (ASSETS_DIR / "footer-snippet.html").read_text(encoding="utf-8")
    cut = raw.find("<script>")
    html = raw[:cut] if cut != -1 else raw
    return html.strip()


WEEK_AT_HTSA_VIDEO = "/media/this-week-at-htsa-2026-08-18.mp4"


def render_week_at_htsa_embed() -> str:
    """In-page player. Does not open a new tab."""
    src = escape(WEEK_AT_HTSA_VIDEO)
    return f"""    <div class="htsa-proof-embed">
      <div class="htsa-proof-embed-kicker">Recorded this week · Aug 18 · 4:07</div>
      <div class="htsa-proof-embed-must-watch">MUST WATCH!!!</div>
      <div class="htsa-proof-embed-title">HTSA · Placement This Week (Aug 18, 2026)</div>
      <p class="htsa-proof-embed-desc">Watch this before the testimonials below. Four people on our live group coaching call talking about getting placed with us. This is the level we operate at on placement, which is usually the biggest question people have. Play it right here. Pause anytime. Use the fullscreen control if you want it larger.</p>
      <video controls playsinline preload="metadata" controlslist="nodownload" title="HTSA Placement This Week, August 18, 2026. Members on live group coaching talking about placement.">
        <source src="{src}" type="video/mp4">
        Your browser does not play this video here. Open <a href="{src}">this file</a> instead.
      </video>
    </div>
"""


def resource_card(href: str, badge: str, title: str, desc: str, cta: str, variant: str = "compact") -> str:
    cls = "cj-resource-card"
    if variant == "featured":
        cls += " cj-resource-card--featured"
    elif variant == "placement":
        cls += " cj-resource-card--placement"
    else:
        cls += " cj-resource-card--compact"
    badge_html = f'<div class="cj-resource-card-badge">{badge}</div>' if badge else ""
    return f"""<a href="{escape(href)}" class="{cls}" target="_blank" rel="noopener noreferrer">
  {badge_html}
  <div class="cj-resource-card-title">{title}</div>
  <p class="cj-resource-card-desc">{desc}</p>
  <span class="cj-resource-card-cta">{cta}</span>
</a>"""


def render_resources_html(first: str) -> str:
    # Dana first (CJ's #1 pick). Chad's book lives in Part 1 only — do not duplicate here.
    featured = [
        resource_card(
            "https://youtu.be/FqlY37NaIsk?si=8__yr1PEtLQY-l9S",
            "⭐ CJ's #1 pick",
            "Dana — unsolicited personal review",
            "She recorded this completely on her own — we had no idea until she posted it. Life coach with a community of about 17,000 followers.",
            "Watch on YouTube",
            "featured",
        ),
        resource_card(
            "https://youtu.be/bd65afldLmE?si=e5Y6G5qMxX-Tx1kE",
            "⭐ If you only watch one",
            "Taylor Conroy (TEDx Coach) — why he hires our members",
            "Taylor is a TEDx coach who actively hires HTSA-certified closers. Hear directly from a hiring manager why he trusts our members.",
            "Watch on YouTube",
            "featured",
        ),
        resource_card(
            "https://drive.google.com/file/d/1Zo2ID5sdF8ZYP8rZD_fisNgj-eNpuQxM/view?usp=sharing",
            "⭐ Fresh placement story",
            "Taylor DeCourcey — newer member perspective",
            "Newer placement with a fresher perspective. Hear what the first months actually looked like after certification.",
            "Watch Taylor's story",
            "featured",
        ),
        resource_card(
            "https://www.trustpilot.com/review/highticketsalesacademy.com",
            "⭐ Verified reviews",
            "Trustpilot — 4.9 out of 5 stars",
            "Read what real members say about HTSA — unfiltered, third-party reviews from people who went through the program.",
            "Read Trustpilot reviews",
            "featured",
        ),
    ]
    placement = [
        resource_card(
            "https://canva.link/qcl7l45n7behw3k",
            "⭐ Placement proof",
            "Why Our Members Actually Get Placed",
            "See how one-on-one placement works in practice — real interviews, real companies, and what the process looks like step by step.",
            "View placement overview",
            "placement",
        ),
        resource_card(
            "https://canva.link/na9nxjm9a1e4vjz",
            "⭐ Real timeline",
            "Christa's Journey — Posted Month by Month",
            "Not a polished testimonial — her actual journey, posted step by step in our community as it happened.",
            "View Christa's timeline",
            "placement",
        ),
    ]
    compact = [
        resource_card("https://youtu.be/WOVqPR-ufYM?si=ncgvZym7RPX1O5Hf", "", "Cassie — single mom success story", "Relatable story — single mom who made the transition work around real life.", "Watch on YouTube"),
        resource_card("https://youtu.be/5pVlD6EKy1k?si=3YBFqk7WhgLW0Hib", "", "Josh — Alex Hormozi background", "High-profile sales background — hear how HTSA fit into his path.", "Watch on YouTube"),
        resource_card("https://youtu.be/TWacdj9x45o?si=7x5kInwdseoNPTE8", "", "Brianna — Tony Robbins team", "Credibility from a big-name organization — her HTSA experience.", "Watch on YouTube"),
        resource_card("https://lp.highticketsalesacademy.com/hubfs/Top%2020%20High%20Ticket%20Sales%20E-Learning%20Companies.pdf", "", "Top 20 Companies in High Ticket Sales", "Industry overview PDF — where HTSA fits in the landscape.", "Open PDF"),
    ]
    # Blue accent (footer globe / site blue) + thin Trustpilot-star gold outside — same card shape as featured/placement.
    website = (
        '<div style="display:flex;justify-content:center;margin-top:12px;">'
        '<a href="https://www.highticketsalesacademy.com" class="cj-resource-card cj-resource-card--compact" '
        'style="max-width:420px;width:100%;'
        "background:linear-gradient(135deg,#eff6ff 0%,#dbeafe 100%);"
        "border:3px solid #1976D2;border-left:5px solid #1565C0;"
        "box-shadow:0 0 0 1.5px #e2b227,0 4px 14px rgba(10,22,40,0.08);"
        '" target="_blank" rel="noopener noreferrer">'
        '<div class="cj-resource-card-title">HTSA Website — more stories &amp; outcomes</div>'
        '<p class="cj-resource-card-desc">Many more member outcomes, screenshots, and program details on our main site.</p>'
        '<span class="cj-resource-card-cta">Visit highticketsalesacademy.com</span>'
        "</a></div>"
    )
    return f"""
  <div class="cj-resources-wrap">
    <p class="cj-resources-lead"><strong>{escape(first)}</strong> — if you watch one thing before we talk, make it the first one.</p>
    <p class="cj-resources-kicker">⭐ Start here — CJ's top picks</p>
    <div class="cj-resources-featured">{"".join(featured)}</div>
    <p class="cj-resources-kicker">⭐ Placement — why our members get results</p>
    <div class="cj-resources-featured">{"".join(placement)}</div>
    <p class="cj-resources-kicker">More success stories from our network</p>
    <div class="cj-resources-grid">{"".join(compact)}</div>
    {website}
  </div>"""


def render_personal_reviews_html(reviews: list, title: str) -> str:
    """CJ-only personal reviews on precall pages. White cards (not blue enrollment Member Voices)."""

    def card_html(r: dict) -> str:
        context = r.get("context", "shared with HTSA")
        body = escape(r.get("body", "")).replace("\n", "<br>")
        return f"""          <div class="ref-strip-quote ref-strip-quote--compact">
            <div class="ref-strip-quote-meta">To CJ</div>
            <blockquote class="ref-strip-quote-body">{body}</blockquote>
            <p class="ref-strip-quote-attr">— {escape(r["name"])} · {escape(context)}</p>
          </div>"""

    # Prefer Janaye at the top of the right column (fills the shorter side).
    right_lead: list[dict] = []
    rest: list[dict] = []
    for r in reviews:
        name = (r.get("name") or "").strip().lower()
        if name.startswith("janaye") and not right_lead:
            right_lead.append(r)
        else:
            rest.append(r)

    mid = (len(rest) + 1) // 2
    left_reviews = rest[:mid]
    right_reviews = right_lead + rest[mid:]

    left = "\n".join(card_html(r) for r in left_reviews)
    right = "\n".join(card_html(r) for r in right_reviews)
    return f"""<!-- CJ personal reviews (precall: white cards only) -->
  <div class="ref-strip">
    <div class="ref-strip-banner">
      <div class="ref-strip-label">{escape(title)}</div>
      <p class="ref-strip-banner-desc">Real messages from people who worked directly with CJ.</p>
    </div>
    <div class="ref-strip-inner ref-strip-inner--personal-reviews">
      <div class="ref-strip-mini-stack">
{left}
      </div>
      <div class="ref-strip-mini-stack">
{right}
      </div>
    </div>
  </div>"""


def has_call_details(data: dict) -> bool:
    return bool(
        (data.get("call_time") or "").strip()
        or (data.get("call_day") or "").strip()
        or (data.get("call_date") or "").strip()
    )


def call_when_line(data: dict) -> str:
    day = (data.get("call_day") or "").strip()
    date = (data.get("call_date") or "").strip()
    time_s = (data.get("call_time") or "").strip()
    tz = (data.get("call_timezone") or "EST").strip()
    bits = []
    if day and date:
        bits.append(f"{day}, {date}")
    elif day:
        bits.append(day)
    elif date:
        bits.append(date)
    if time_s:
        bits.append(f"{time_s} {tz}".strip())
    return " · ".join(bits) if bits else "Time to be confirmed"


def billing_call_line(data: dict) -> str:
    day = (data.get("call_day") or "").strip()
    time_s = (data.get("call_time") or "").strip()
    tz = (data.get("call_timezone") or "EST").strip()
    if day and time_s:
        when = f"{day} at {time_s} {tz}"
    elif time_s:
        when = f"{time_s} {tz}"
    else:
        when = ""
    if data.get("missed_meeting"):
        return f"Missed · {when}" if when else "Missed meeting · reschedule below"
    if when:
        return when
    return "Call details on this page"


CJ_BOOKING_URL = "https://meetings.hubspot.com/charles660/cj"


def render_call_card(data: dict) -> str:
    if not has_call_details(data):
        return ""
    when = escape(call_when_line(data))
    fmt = escape((data.get("call_format") or "Zoom").strip())
    confirm_day = escape((data.get("call_day") or "soon").strip() or "soon")
    missed = bool(data.get("missed_meeting"))
    booking = escape((data.get("booking_url") or CJ_BOOKING_URL).strip() or CJ_BOOKING_URL)

    if missed:
        return f"""
  <div class="rl-call-card rl-call-card--missed" id="rl-call-card" data-call-status="missed">
    <p class="rl-call-card-kicker rl-call-card-kicker--missed">Missed meeting</p>
    <p class="rl-call-card-when">{when}</p>
    <p class="rl-call-card-meta">We didn’t connect at this time · {fmt}</p>
    <div class="rl-call-card-actions">
      <a href="{booking}" class="invest-btn" target="_blank" rel="noopener noreferrer">Reschedule Appointment →</a>
    </div>
  </div>"""

    return f"""
  <div class="rl-call-card" id="rl-call-card" data-confirm-day="{confirm_day}">
    <p class="rl-call-card-kicker">📅 Your call with CJ</p>
    <p class="rl-call-card-when">{when}</p>
    <p class="rl-call-card-meta">45 minutes · {fmt}</p>
    <div class="rl-call-card-actions">
      <button type="button" id="rl-confirm-call" class="invest-btn">Confirm I'll be there</button>
    </div>
  </div>"""


def render_about_htsa() -> str:
    """Part 1 — placement clip first, then Chad. Book banner + Trustpilot live here (not duplicated below)."""
    return f"""  <div class="sec-head">
    <div class="sec-num">1</div>
    <h3>Who Mentors You</h3>
  </div>
  <div class="rl-q-wrap">
    <div class="rl-q-item">
      <div class="rl-q-ours">
{render_week_at_htsa_embed()}
        <p>You're validated and placed directly by Chad Aleo himself — not a random coach.</p>
        <p style="margin-top:12px;"><a href="https://youtu.be/eLAWEwE7pl4?si=VfiqAxeOKFnoJ_Mm" class="step-link" target="_blank" rel="noopener noreferrer">⭐ Meet Chad — CEO &amp; Founder at HTSA</a></p>
        <p style="margin-top:14px;"><a href="https://www.amazon.com/Book-High-Ticket-Sales-Ultimate/dp/B0C6C6PSMH" target="_blank" rel="noopener noreferrer"><img class="rl-proof-img" src="https://closewithcjclay.com/resource-links/assets/chad-aleo-book-banner.png" alt="Chad Aleo, best-selling author of The Book on High Ticket Sales"></a></p>
        <div class="rl-proof-caption">Chad Aleo · <em>The Book on High Ticket Sales</em> — view on Amazon</div>
        <p style="margin-top:14px;"><a href="https://www.trustpilot.com/review/highticketsalesacademy.com" class="rl-trustpilot-link" target="_blank" rel="noopener noreferrer"><span class="rl-trustpilot-stars" aria-hidden="true">★★★★★</span><span class="rl-trustpilot-text">Trustpilot Reviews — 4.9 stars out of 5</span></a></p>
      </div>
    </div>
  </div>"""


def tracking_script(data: dict) -> str:
    slug = data["slug"]
    prospect_id = data.get("prospect_id", slug.replace("_", "-"))
    confirm_day = (data.get("call_day") or "soon").strip() or "soon"
    return f"""<script>
(function(){{
  var GAS_ENDPOINT = {json.dumps(GAS_ENDPOINT)};
  var slug = {json.dumps(slug)};
  var confirmDay = {json.dumps(confirm_day)};
  var meta = {{
    fullName: {json.dumps(data.get("prospect_name", ""))},
    email: {json.dumps(data.get("email", ""))},
    phone: {json.dumps(data.get("phone_e164", ""))},
    clientSlug: {json.dumps(prospect_id)},
    resourceSlug: slug,
    pageType: "precall"
  }};

  function canonicalUrl() {{
    try {{
      var u = new URL(window.location.href);
      return u.origin + u.pathname;
    }} catch (e) {{ return window.location.href.split('#')[0]; }}
  }}

  function postEvent(event, extra) {{
    var body = Object.assign({{
      action: 'recordResourcePageEvent',
      event: event,
      enrollmentPageUrl: canonicalUrl(),
      userAgent: navigator.userAgent || '',
      timestamp: new Date().toISOString()
    }}, meta, extra || {{}});
    var form = new URLSearchParams();
    form.set('payload', JSON.stringify(body));
    fetch(GAS_ENDPOINT, {{ method: 'POST', mode: 'no-cors', body: form, cache: 'no-store' }}).catch(function(){{}});
  }}

  if (!sessionStorage.getItem('htsa_precall_open_'+slug)) {{
    sessionStorage.setItem('htsa_precall_open_'+slug, '1');
    postEvent('page_open');
  }}

  var confirmBtn = document.getElementById('rl-confirm-call');
  if (confirmBtn) {{
    confirmBtn.addEventListener('click', function() {{
      if (confirmBtn.getAttribute('data-confirmed') === '1') return;
      confirmBtn.setAttribute('data-confirmed', '1');
      confirmBtn.textContent = 'Confirmed — see you ' + confirmDay + ' ✓';
      confirmBtn.classList.add('invest-btn--confirmed');
      postEvent('call_confirm');
    }});
  }}

  document.querySelectorAll('a.cj-resource-card').forEach(function(a) {{
    a.addEventListener('click', function() {{
      var title = (a.querySelector('.cj-resource-card-title') || {{}}).textContent || '';
      postEvent('link_click', {{ linkLabel: title.trim(), linkUrl: a.href }});
    }});
  }});
}})();
</script>"""


def manifest_guard(slug: str) -> str:
    return f"""<script>
(function(){{
  var slug={json.dumps(slug)};
  fetch('/r/_manifest.json?v='+Date.now(),{{cache:'no-store'}})
    .then(function(r){{return r.json();}})
    .then(function(m){{
      var link=m.links&&m.links[slug];
      var expired=!link||link.status!=='active'||(link.expires_at&&new Date(link.expires_at)<new Date());
      if(expired){{ window.location.replace('/r/_expired.html'); }}
    }}).catch(function(){{}});
}})();
</script>"""


def render_page(data: dict) -> str:
    slug = data["slug"]
    first = escape(data.get("first_name") or first_name(data["prospect_name"]))
    full = escape(data["prospect_name"])
    email = escape(data.get("email", ""))
    phone_display = escape(data.get("phone_display", ""))
    phone_e164 = escape(data.get("phone_e164", ""))
    prepared = escape(data.get("prepared_date", ""))
    show_call = has_call_details(data)
    badge = "Pre-Call Resources" if show_call else "Resources"
    call_note = escape(billing_call_line(data)) if show_call else "Resources for your HTSA conversation"
    defaults = load_defaults()
    reviews = data.get("personal_reviews") or defaults.get("personal_reviews") or []
    reviews_title = data.get("personal_reviews_title") or defaults.get(
        "personal_reviews_title", "A few of CJ's Personal Reviews"
    )

    email_line = f'<a href="mailto:{email}">{email}</a><br>' if email else ""
    phone_line = f'<a href="tel:{phone_e164}">{phone_display}</a><br>' if phone_display else ""

    custom_hero = data.get("hero_paragraphs")
    if custom_hero:
        parts = []
        for p in custom_hero:
            body = p if p.lstrip().startswith("<") else escape(p)
            parts.append(f"    <p>{body}</p>")
        hero = "  <div class=\"hero-band hero-band--letter\">\n" + "\n".join(parts) + "\n  </div>"
    else:
        hero = f"""  <div class="hero-band hero-band--letter">
    <p><strong>{first}</strong> — everything you'd want before we talk is right here.</p>
    <p>On the call we'll cover where you're at, what you're after, and whether this is the right move for your next chapter. High ticket sales is one of the few careers that travels — every company in every vertical needs someone who can close, and that's what makes a good closer invaluable in the marketplace. The world went remote, and the demand followed it.</p>
    <p>Have a look at whatever's useful. Look forward to connecting.</p>
  </div>"""

    call_card = render_call_card(data) if show_call else ""

    resources = f"""  <div class="sec-head">
    <div class="sec-num">2</div>
    <h3>Videos, Proof &amp; Member Stories</h3>
  </div>
{render_resources_html(data.get("first_name") or first_name(data["prospect_name"]))}"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="robots" content="noindex,nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
<title>HTSA — {full}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
{enrollment_css()}
</style>
{manifest_guard(slug)}
</head>
<body>
<div class="page" id="main-content">

  <div class="header">
    <div>
      {logo_html()}
      <div class="header-tagline" style="margin-top:12px;">Certification &nbsp;·&nbsp; Coaching &nbsp;·&nbsp; Placement</div>
    </div>
    <div class="invoice-meta">
      <div class="invoice-badge">{badge}</div>
      <p><strong>Prepared by:</strong> CJ Clay</p>
      <p><strong>Prepared for:</strong> {full}</p>
      <p><strong>Date:</strong> {prepared}</p>
    </div>
  </div>
  <div class="accent-bar"></div>

{hero}
{call_card}

  <div class="billing-grid">
    <div class="billing-cell">
      <div class="billing-label">Prepared For</div>
      <div class="billing-name">{full}</div>
      <div class="billing-detail">
        {email_line}
        {phone_line}
        {call_note}
      </div>
    </div>
    <div class="billing-cell">
      <div class="billing-label">Prepared By</div>
      <div class="billing-name">CJ Clay</div>
      <div class="billing-detail">
        HTSA Career Coach<br>
        (616) 612-1735<br>
        <a href="mailto:cj@highticketsalesacademy.com">cj@highticketsalesacademy.com</a>
      </div>
    </div>
  </div>

{render_about_htsa()}
{resources}

  {render_personal_reviews_html(reviews, reviews_title)}

  {footer_html()}

</div>
{tracking_script(data)}
</body>
</html>"""


def git_ship(paths: list[str], message: str) -> None:
    existing = [p for p in paths if (ROOT / p).exists()]
    for p in existing:
        subprocess.run(["git", "add", p], cwd=ROOT, check=True)
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if not staged:
        print("Nothing new to commit (already up to date).")
        return
    subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=True)


def http_status(url: str) -> int | None:
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method)
            with urllib.request.urlopen(req, timeout=25) as resp:
                return resp.status
        except urllib.error.HTTPError as e:
            return e.code
        except OSError:
            continue
    return None


def wait_for_live(url: str) -> bool:
    deadline = time.monotonic() + LIVE_POLL_TIMEOUT_SEC
    attempt = 0
    print(f"Waiting for live page (up to {LIVE_POLL_TIMEOUT_SEC // 60} min)…", file=sys.stderr)
    while time.monotonic() < deadline:
        attempt += 1
        code = http_status(url)
        if code is not None and 200 <= code < 300:
            print(f"  attempt {attempt}: HTTP {code} — ready.", file=sys.stderr)
            return True
        label = f"HTTP {code}" if code is not None else "no response"
        print(f"  attempt {attempt}: {label} — retry in {LIVE_POLL_INTERVAL_SEC}s…", file=sys.stderr)
        time.sleep(LIVE_POLL_INTERVAL_SEC)
    return False


def assert_clean(html: str) -> None:
    body = re.sub(r"<style>.*?</style>", "", html, flags=re.DOTALL)
    bad = []
    for needle, label in [
        ('id="email-gate"', "email-gate"),
        ("invest-pay-zone", "invest-pay-zone"),
        ("hts-terms-agreement", "terms gate"),
        ("enrollment-guarantee-banner", "guarantee banner"),
        ("Val Tappan", "Val Tappan"),
        ("tammy_berry", "tammy_berry"),
        ("chad_beldon", "chad_beldon"),
        ("chad-beldon", "chad-beldon"),
        ("rl-curriculum-grid", "curriculum grid"),
        ("rl-member-contacts", "member contacts"),
        ("whop.com/checkout", "Whop checkout"),
        ("Need to reschedule", "reschedule link"),
        ("Add to Calendar", "calendar button"),
        ("Don't be late", "don't be late"),
        ("$28 million", "$28M line"),
    ]:
        if needle.lower() in body.lower():
            bad.append(label)
    # Book Amazon link should appear once (Part 1 only)
    if body.count("Book-High-Ticket-Sales-Ultimate") != 1:
        bad.append("book link count != 1")
    if bad:
        raise SystemExit("Stale / forbidden content: " + ", ".join(bad))


def build_data(args: argparse.Namespace) -> dict:
    full = args.full_name.strip()
    slug = normalize_slug(args.slug or client_slug(full))
    prepared = datetime.now(ZoneInfo("America/New_York")).strftime("%b %-d, %Y")
    return {
        "page_type": "precall",
        "prospect_id": slug.replace("_", "-"),
        "prospect_name": full,
        "first_name": first_name(full),
        "email": args.email.strip(),
        "phone_e164": args.phone_e164.strip(),
        "phone_display": (args.phone_display or args.phone_e164).strip(),
        "prepared_date": prepared,
        "slug": slug,
        "call_day": (args.call_day or "").strip(),
        "call_date": (args.call_date or "").strip(),
        "call_time": (args.call_time or "").strip(),
        "call_timezone": (args.timezone or "EST").strip(),
        "call_format": (args.call_format or "Zoom").strip(),
        "missed_meeting": bool(getattr(args, "missed", False)),
        "booking_url": (getattr(args, "booking_url", None) or CJ_BOOKING_URL).strip(),
        "show_member_contacts": False,
    }


def cmd_create(args: argparse.Namespace) -> None:
    data = build_data(args)
    slug = data["slug"]
    prospect_id = data["prospect_id"]
    data_path = DATA_DIR / f"{prospect_id}.json"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    created = utcnow()
    expires = created + timedelta(days=EXPIRE_DAYS)
    reg = load_registry()
    reg.setdefault("links", {})[slug] = {
        "slug": slug,
        "prospect_id": prospect_id,
        "prospect_name": data["prospect_name"],
        "email": data["email"],
        "phone_e164": data["phone_e164"],
        "phone_display": data["phone_display"],
        "page_type": "precall",
        "created_at": iso(created),
        "expires_at": iso(expires),
        "status": "active",
        "view_count": 0,
        "last_viewed_at": None,
    }
    save_registry(reg)

    out_dir = R_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    html = render_page(data)
    assert_clean(html)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    if EXPIRED_TEMPLATE.is_file():
        (R_DIR / "_expired.html").write_text(EXPIRED_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")

    url = f"https://closewithcjclay.com/r/{slug}/"
    print(url)

    if args.ship:
        git_ship(
            [
                f"r/{slug}/index.html",
                "r/_manifest.json",
                "r/_expired.html",
                "resource-links/registry.json",
                f"resource-links/data/{prospect_id}.json",
                "resource-links/data/_precall-defaults.json",
                "resource-links/assets/logo-snippet.html",
                "resource-links/assets/enrollment-styles.css",
                "media/this-week-at-htsa-2026-08-18.mp4",
                "scripts/precall-resource.py",
            ],
            f"Rebuild pre-call resources for {data['prospect_name']} (/r/{slug}).",
        )
        if wait_for_live(url):
            print("READY")
            print(url)
        else:
            print("PUSHED but live poll timed out")
            print(url)


def main() -> None:
    ap = argparse.ArgumentParser(description="Build pre-call resource pages (/r/<slug>/).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("create", help="Create a pre-call page")
    p.add_argument("--full-name", required=True)
    p.add_argument("--email", required=True)
    p.add_argument("--phone-e164", required=True)
    p.add_argument("--phone-display", default="")
    p.add_argument("--slug", default="")
    p.add_argument("--call-day", default="")
    p.add_argument("--call-date", default="")
    p.add_argument("--call-time", default="")
    p.add_argument("--timezone", default="EST")
    p.add_argument("--call-format", default="Zoom")
    p.add_argument(
        "--missed",
        action="store_true",
        help="No-show / missed meeting card: red Missed meeting + green Reschedule button",
    )
    p.add_argument(
        "--booking-url",
        default=CJ_BOOKING_URL,
        help=f"HubSpot booking URL for reschedule button (default: {CJ_BOOKING_URL})",
    )
    p.add_argument("--ship", action="store_true")
    p.set_defaults(func=cmd_create)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
