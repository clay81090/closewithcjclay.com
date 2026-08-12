#!/usr/bin/env python3
"""Pre-call resource pages at closewithcjclay.com/r/<first_last>/.

Standing template from CURSOR_BUILD_PRECALL_RESOURCE_TEMPLATE.md.
No email gate, no pricing, no terms, no curriculum, no guarantee banner.

Usage:
  python3 scripts/precall-resource.py create \\
    --full-name "Sarah Nitterauer" \\
    --email "sarahnitterauer@gmail.com" \\
    --phone-e164 "+18282158111" \\
    --phone-display "+1 (828) 215-8111" \\
    --call-time "3:00 PM" --timezone "EST" --call-format "Phone or Zoom" \\
    --ship

  # Optional: --call-day "Wednesday" --call-date "Aug 12" --call-iso "2026-08-12T15:00:00-04:00"
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
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
HUBSPOT_RESCHEDULE = "https://meetings.hubspot.com/charles660/cj"
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
    """Base enrollment CSS with email-gate block removed (pre-call has no gate)."""
    css = (ASSETS_DIR / "enrollment-styles.css").read_text(encoding="utf-8")
    # Drop private-page email gate styles from embedded CSS.
    start = css.find("  /* Private page email gate */")
    if start != -1:
        # Cut through end of .email-gate-foot block
        end = css.find("  .rl-ask-wrap", start)
        if end != -1:
            css = css[:start] + css[end:]
    return css


def logo_html() -> str:
    html = (ASSETS_DIR / "logo-snippet.html").read_text(encoding="utf-8").strip()
    return html.replace('alt="Val Tappan"', 'alt="Chad Aleo"')


def footer_html() -> str:
    """Footer markup only — strip enrollment Terms-gate <script> leftovers."""
    raw = (ASSETS_DIR / "footer-snippet.html").read_text(encoding="utf-8")
    # Keep HTML through copyright bar; drop any trailing Terms scripts.
    cut = raw.find("<script>")
    html = raw[:cut] if cut != -1 else raw
    return html.strip()


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
    featured = [
        resource_card(
            "https://youtu.be/bd65afldLmE?si=e5Y6G5qMxX-Tx1kE",
            "⭐ If you only watch one",
            "Taylor Conroy (TEDx Coach) — why he hires our members",
            "Taylor is a TEDx coach who actively hires HTSA-certified closers. Hear directly from a hiring manager why he trusts our members.",
            "Watch on YouTube",
            "featured",
        ),
        resource_card(
            "https://youtu.be/FqlY37NaIsk?si=8__yr1PEtLQY-l9S",
            "⭐ CJ's #1 pick",
            "Dana — unsolicited personal review",
            "She recorded this completely on her own — we had no idea until she posted it. Life coach with a community of about 17,000 followers.",
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
        resource_card("https://youtu.be/eLAWEwE7pl4?si=VfiqAxeOKFnoJ_Mm", "", "Chad — in his own words", "Who actually trains you and why that matters.", "Watch on YouTube"),
        resource_card("https://www.highticketsalesacademy.com", "", "HTSA Website — more stories &amp; outcomes", "Many more member outcomes, screenshots, and program details on our main site.", "Visit highticketsalesacademy.com"),
        resource_card("https://www.amazon.com/Book-High-Ticket-Sales-Ultimate/dp/B0C6C6PSMH", "", "Chad's Book — <em>The Book on High Ticket Sales</em>", "The ultimate guide by HTSA founder Chad Aleo — available on Amazon.", "View on Amazon"),
        resource_card("https://lp.highticketsalesacademy.com/hubfs/Top%2020%20High%20Ticket%20Sales%20E-Learning%20Companies.pdf", "", "Top 20 Companies in High Ticket Sales", "Industry overview PDF — where HTSA fits in the landscape.", "Open PDF"),
    ]
    return f"""
  <div class="cj-resources-wrap">
    <p class="cj-resources-lead"><strong>{escape(first)}</strong> — if you only watch one thing before we talk, make it the first one.</p>
    <p class="cj-resources-kicker">⭐ Start here — CJ's top picks</p>
    <div class="cj-resources-featured">{"".join(featured)}</div>
    <p class="cj-resources-kicker">⭐ Placement — why our members get results</p>
    <div class="cj-resources-featured">{"".join(placement)}</div>
    <p class="cj-resources-kicker">More success stories from our network</p>
    <div class="cj-resources-grid">{"".join(compact)}</div>
  </div>"""


def render_personal_reviews_html(reviews: list, title: str) -> str:
    cards = []
    for r in reviews:
        context = r.get("context", "shared with HTSA")
        cards.append(
            f"""          <div class="ref-strip-quote ref-strip-quote--compact">
            <div class="ref-strip-quote-meta">To CJ</div>
            <blockquote class="ref-strip-quote-body">{r["body"]}</blockquote>
            <p class="ref-strip-quote-attr">— {r["name"]} · {context}</p>
          </div>"""
        )
    mid = (len(cards) + 1) // 2
    left = "\n".join(cards[:mid])
    right = "\n".join(cards[mid:])
    return f"""<!-- CJ personal reviews -->
  <div class="ref-strip">
    <div class="ref-strip-label">{escape(title)}</div>
    <p class="ref-strip-personal-intro">Real messages and posts from people who worked directly with CJ, not copied from Trustpilot.</p>
    <div class="ref-strip-inner ref-strip-inner--personal-reviews">
      <div class="ref-strip-mini-stack">
{left}
      </div>
      <div class="ref-strip-mini-stack">
{right}
      </div>
    </div>
  </div>"""


FAQ_ITEMS = [
    (
        "What does the program actually include?",
        "Self-paced modules plus five levels of AI roleplay on a real offer, live coaching twice a week with Chad, one-on-one certification assessment, resume and interview prep, one-on-one placement, and 90 days of post-hire call review. Lifetime access to training, coaching, and community.",
    ),
    (
        "How long until I'm placed?",
        "Certification takes most people about 30 days self-paced. Average time to land after that: <strong>38 days for closers, 23 days for setters.</strong>",
    ),
    (
        "Do I need sales experience?",
        "No. About half our members come in without it. Experienced reps come in for the reps, the placement network, and accountability rather than the fundamentals.",
    ),
    (
        "What kinds of companies?",
        "300+ partners across health and wellness, coaching, business services, financial services, AI and marketing agencies, and real estate education. Members have placed with teams at Tony Robbins, Alex Hormozi, Grant Cardone, John Maxwell, Taylor Conroy, and Samantha Skelly.",
    ),
    (
        "What does it pay?",
        "Typical partner offer is $8k–$12k, commission usually 10–15%. What you make is a function of how many conversations you take and how good you get. <strong>No income is promised and none is implied.</strong>",
    ),
    (
        "How much time does it take?",
        "Self-paced except Chad's two live calls a week, and those are recorded. Members with full-time jobs typically finish in three to six weeks.",
    ),
    (
        "How is placement handled?",
        "One-on-one. We introduce you directly to partner companies — you're not applying through a job board or paying a monthly fee for access to a list.",
    ),
]


def render_faq_html() -> str:
    parts = []
    for q, a in FAQ_ITEMS:
        parts.append(
            f"""<details class="rl-faq-item">
  <summary>{escape(q)}</summary>
  <div class="rl-faq-body">{a}</div>
</details>"""
        )
    return "\n".join(parts)


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


def has_call_details(data: dict) -> bool:
    return bool((data.get("call_time") or "").strip() or (data.get("call_day") or "").strip() or (data.get("call_date") or "").strip())


def resolve_call_iso(data: dict) -> str | None:
    """Return ISO datetime for ICS. If only time given, use next occurrence in America/New_York."""
    raw = (data.get("call_iso") or "").strip()
    if raw:
        return raw
    time_s = (data.get("call_time") or "").strip()
    if not time_s:
        return None
    m = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(AM|PM)$", time_s.strip(), re.I)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    ampm = m.group(3).upper()
    if ampm == "PM" and hour != 12:
        hour += 12
    if ampm == "AM" and hour == 12:
        hour = 0
    tz = ZoneInfo("America/New_York")
    now = datetime.now(tz)
    candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= now:
        candidate += timedelta(days=1)
    return candidate.isoformat()


def render_call_card(data: dict, first: str) -> str:
    if not has_call_details(data):
        return ""
    when = escape(call_when_line(data))
    fmt = escape((data.get("call_format") or "Zoom").strip())
    confirm_day = escape((data.get("call_day") or "soon").strip() or "soon")
    call_iso = resolve_call_iso(data) or ""
    return f"""
  <div class="rl-call-card" id="rl-call-card"
       data-call-iso="{escape(call_iso)}"
       data-page-url="https://closewithcjclay.com/r/{escape(data['slug'])}/"
       data-confirm-day="{confirm_day}">
    <div class="rl-call-card-kicker">📅 Your call with CJ</div>
    <div class="rl-call-card-when">{when}</div>
    <p class="rl-call-card-meta">About 45 minutes · {fmt}</p>
    <div class="rl-call-card-actions">
      <button type="button" id="rl-add-calendar" class="invest-btn">Add to Calendar</button>
      <button type="button" id="rl-confirm-call" class="invest-btn secondary">Confirm I'll be there</button>
      <a href="{HUBSPOT_RESCHEDULE}" id="rl-reschedule" class="step-link" target="_blank" rel="noopener noreferrer">Need to reschedule?</a>
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

  var reschedule = document.getElementById('rl-reschedule');
  if (reschedule) {{
    reschedule.addEventListener('click', function() {{
      postEvent('reschedule_click');
    }});
  }}

  function pad(n) {{ return String(n).padStart(2, '0'); }}
  function toIcsUtc(d) {{
    return d.getUTCFullYear() + pad(d.getUTCMonth()+1) + pad(d.getUTCDate()) + 'T' +
      pad(d.getUTCHours()) + pad(d.getUTCMinutes()) + pad(d.getUTCSeconds()) + 'Z';
  }}

  var calBtn = document.getElementById('rl-add-calendar');
  var callCard = document.getElementById('rl-call-card');
  if (calBtn && callCard) {{
    calBtn.addEventListener('click', function() {{
      var iso = callCard.getAttribute('data-call-iso') || '';
      var pageUrl = callCard.getAttribute('data-page-url') || canonicalUrl();
      if (!iso) {{
        window.open({json.dumps(HUBSPOT_RESCHEDULE)}, '_blank');
        postEvent('calendar_add', {{ fallback: 'hubspot' }});
        return;
      }}
      var start = new Date(iso);
      if (isNaN(start.getTime())) {{
        window.open({json.dumps(HUBSPOT_RESCHEDULE)}, '_blank');
        postEvent('calendar_add', {{ fallback: 'hubspot' }});
        return;
      }}
      var end = new Date(start.getTime() + 45*60*1000);
      var stamp = toIcsUtc(new Date());
      var uid = 'precall-' + slug + '@closewithcjclay.com';
      var desc = 'HTSA call with CJ Clay.\\nPhone: (616) 612-1735\\nPage: ' + pageUrl;
      var ics = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//HTSA//Pre-Call//EN',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        'BEGIN:VEVENT',
        'UID:' + uid,
        'DTSTAMP:' + stamp,
        'DTSTART:' + toIcsUtc(start),
        'DTEND:' + toIcsUtc(end),
        'SUMMARY:HTSA Call — CJ Clay',
        'DESCRIPTION:' + desc.replace(/\\n/g, '\\\\n'),
        'LOCATION:Phone or Zoom with CJ Clay',
        'END:VEVENT',
        'END:VCALENDAR'
      ].join('\\r\\n');
      var blob = new Blob([ics], {{ type: 'text/calendar;charset=utf-8' }});
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'htsa-call-cj-clay.ics';
      document.body.appendChild(a);
      a.click();
      a.remove();
      postEvent('calendar_add');
    }});
  }}

  document.querySelectorAll('details.rl-faq-item').forEach(function(el) {{
    el.addEventListener('toggle', function() {{
      if (el.open) {{
        var label = (el.querySelector('summary') || {{}}).textContent || '';
        postEvent('faq_open', {{ faqLabel: label.trim() }});
      }}
    }});
  }});

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
    call_note = escape(call_when_line(data)) if show_call else "Resources for your HTSA conversation"
    defaults = load_defaults()
    reviews = data.get("personal_reviews") or defaults.get("personal_reviews") or []
    reviews_title = data.get("personal_reviews_title") or defaults.get(
        "personal_reviews_title", "A few of CJ's Personal Reviews"
    )

    email_line = f'<a href="mailto:{email}">{email}</a><br>' if email else ""
    phone_line = f'<a href="tel:{phone_e164}">{phone_display}</a><br>' if phone_display else ""

    hero = f"""  <div class="hero-band hero-band--letter">
    <p>Hi <strong>{first}</strong> — looking forward to our call.</p>
    <p>I put this page together so you're not hunting through your inbox. Everything you'd want to look at before we talk is right here — what the program actually is, who trains you, and what people who've been through it say.</p>
    <p>Nothing here is a sales page. There's no pricing on this page and nothing to sign. Have a look at whatever's useful, ignore the rest, and bring your questions to the call.</p>
  </div>"""

    call_card = render_call_card(data, first) if show_call else ""

    expect = f"""  <div class="sec-head">
    <div class="sec-num">1</div>
    <h3>What to Expect on Our Call</h3>
  </div>
  <div class="rl-q-wrap">
    <div class="rl-q-item">
      <h4>What this call actually is</h4>
      <div class="rl-q-ours">
        <p>Forty-five minutes, straight questions, no pitch deck. I want to understand where you are, what you've tried, and what you actually want — then I'll tell you honestly whether this is a fit. <strong>I turn more people away from this than I put in it,</strong> and I'd rather find that out on a Tuesday than after you've spent money.</p>
        <p style="margin-top:12px;"><strong>One thing worth saying up front so we're not talking past each other:</strong> we're not a staffing agency and I'm not hiring you. HTSA certifies closers and then places them with partner companies who pay commission. It's a program you invest in, and then you go earn. I mention it now because I'd rather you know that before we talk than be surprised by it.</p>
      </div>
    </div>
    <div class="rl-q-item">
      <h4>How to be ready</h4>
      <ul class="rl-expect-list">
        <li><strong>Somewhere you can talk.</strong> Not the car, not a lobby. You'll want to think.</li>
        <li><strong>Forty-five uninterrupted minutes.</strong> If you've only got twenty, message me and we'll move it — a rushed call helps neither of us.</li>
        <li><strong>Something to write with.</strong> There'll be a few numbers.</li>
        <li><strong>If someone else is part of the decision, have them there.</strong> Easier than relaying it later.</li>
      </ul>
    </div>
  </div>"""

    faq = f"""  <div class="sec-head">
    <div class="sec-num">2</div>
    <h3>Quick Answers</h3>
  </div>
  <div class="rl-faq-wrap">
{render_faq_html()}
  </div>"""

    train = f"""  <div class="sec-head">
    <div class="sec-num">3</div>
    <h3>Who Actually Trains You</h3>
  </div>
  <div class="rl-q-wrap">
    <div class="rl-q-item">
      <div class="rl-q-ours">
        <p><strong>Chad Aleo.</strong> Roughly <strong>$28 million</strong> in revenue closed as a working closer before he built the academy. Mentored by Tony Robbins. Best-selling author on Amazon.</p>
        <p style="margin-top:12px;">He trains <strong>live twice a week</strong> — Tuesdays 12 PM EST and Wednesdays 5 PM EST — and he does your final one-on-one certification assessment personally. Not a coach who's six months ahead of you.</p>
        <p style="margin-top:14px;"><a href="https://www.amazon.com/Book-High-Ticket-Sales-Ultimate/dp/B0C6C6PSMH" target="_blank" rel="noopener noreferrer"><img class="rl-proof-img" src="https://closewithcjclay.com/resource-links/assets/chad-aleo-book-banner.png" alt="Chad Aleo, best-selling author of The Book on High Ticket Sales"></a></p>
        <div class="rl-proof-caption">Chad Aleo · Best-Selling Author · <em>The Book on High Ticket Sales</em></div>
        <p style="margin-top:14px;"><a href="https://www.trustpilot.com/review/highticketsalesacademy.com" class="rl-trustpilot-link" target="_blank" rel="noopener noreferrer"><span class="rl-trustpilot-stars" aria-hidden="true">★★★★★</span><span class="rl-trustpilot-text">Trustpilot Reviews — 4.9 stars out of 5</span></a></p>
      </div>
    </div>
  </div>"""

    resources = f"""  <div class="sec-head">
    <div class="sec-num">4</div>
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

{expect}
{faq}
{train}
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
    print(f"Waiting for live page (up to {LIVE_POLL_TIMEOUT_SEC // 60} min)…", file=__import__("sys").stderr)
    while time.monotonic() < deadline:
        attempt += 1
        code = http_status(url)
        if code is not None and 200 <= code < 300:
            print(f"  attempt {attempt}: HTTP {code} — ready.", file=__import__("sys").stderr)
            return True
        label = f"HTTP {code}" if code is not None else "no response"
        print(f"  attempt {attempt}: {label} — retry in {LIVE_POLL_INTERVAL_SEC}s…", file=__import__("sys").stderr)
        time.sleep(LIVE_POLL_INTERVAL_SEC)
    return False


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
        "call_iso": (args.call_iso or "").strip(),
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
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    if EXPIRED_TEMPLATE.is_file():
        (R_DIR / "_expired.html").write_text(EXPIRED_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")

    url = f"https://closewithcjclay.com/r/{slug}/"
    print(url)

    # Stale-string guard on rendered body (ignore unused CSS class names)
    body_only = html
    if "<style>" in html and "</style>" in html:
        body_only = re.sub(r"<style>.*?</style>", "", html, flags=re.DOTALL)
    bad_hits = []
    if 'id="email-gate"' in body_only or "id='email-gate'" in body_only:
        bad_hits.append("email-gate element")
    if "invest-pay-zone" in body_only:
        bad_hits.append("invest-pay-zone")
    if "hts-terms-agreement" in body_only:
        bad_hits.append("hts-terms-agreement")
    if "enrollment-guarantee-banner" in body_only:
        bad_hits.append("enrollment-guarantee-banner")
    if "Val Tappan" in body_only:
        bad_hits.append("Val Tappan")
    if "tammy_berry" in body_only:
        bad_hits.append("tammy_berry")
    if "chad_beldon" in body_only or "chad-beldon" in body_only:
        bad_hits.append("chad_beldon")
    if bad_hits:
        raise SystemExit("Stale strings found: " + ", ".join(bad_hits))

    if args.ship:
        git_ship(
            [
                f"r/{slug}/index.html",
                "r/_manifest.json",
                "r/_expired.html",
                "resource-links/registry.json",
                f"resource-links/data/{prospect_id}.json",
                "resource-links/data/_precall-defaults.json",
                "resource-links/assets/enrollment-styles.css",
                "resource-links/assets/logo-snippet.html",
                "scripts/precall-resource.py",
            ],
            f"Add pre-call resource page for {data['prospect_name']} (/r/{slug}).",
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
    p.add_argument("--call-iso", default="", help="ISO datetime for ICS, e.g. 2026-08-12T15:00:00-04:00")
    p.add_argument("--ship", action="store_true")
    p.set_defaults(func=cmd_create)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
