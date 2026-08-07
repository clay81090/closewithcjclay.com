#!/usr/bin/env python3
"""Private revocable resource pages at closewithcjclay.com/r/<slug>.

Usage:
  python3 scripts/resource-link.py create tammy-berry [--ship]
  python3 scripts/resource-link.py kill <slug> [--ship]
  python3 scripts/resource-link.py list
  python3 scripts/resource-link.py rebuild [--ship]
  python3 scripts/resource-link.py rebuild-all [--ship]

Set RESOURCE_LINK_TRACK_TOKEN (GitHub fine-grained PAT, contents:write on
resource-links/registry.json) to enable client-side view_count tracking.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import secrets
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "resource-links" / "data"
REGISTRY_PATH = ROOT / "resource-links" / "registry.json"
MANIFEST_PATH = ROOT / "r" / "_manifest.json"
R_DIR = ROOT / "r"
EXPIRED_TEMPLATE = ROOT / "resource-links" / "templates" / "expired.html"
ASSETS_DIR = ROOT / "resource-links" / "assets"
ENROLLMENT_SHELL = ROOT / "htsa-enrollment-chad-beldon.html"

EXPIRE_DAYS = 14
SLUG_MIN_LEN = 16
CUSTOM_SLUG_RE = re.compile(r"^[a-z0-9_-]{3,40}$")


def normalize_custom_slug(raw: str) -> str:
    slug = raw.strip().lower().replace(" ", "_")
    if not CUSTOM_SLUG_RE.match(slug):
        raise SystemExit("Custom slug must be 3–40 chars: lowercase letters, numbers, underscore, hyphen")
    return slug


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_registry() -> dict:
    if REGISTRY_PATH.exists():
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {"links": {}, "updated_at": iso(utcnow())}


def save_registry(reg: dict) -> None:
    reg["updated_at"] = iso(utcnow())
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
    write_manifest(reg)


def write_manifest(reg: dict) -> None:
    """Public manifest: status + expiry only (no content)."""
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


def gen_slug() -> str:
    return secrets.token_urlsafe(24).replace("-", "x").replace("_", "y")[:24]


def load_prospect_data(prospect_id: str) -> dict:
    path = DATA_DIR / f"{prospect_id}.json"
    if not path.is_file():
        raise SystemExit(f"Data file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def logo_html() -> str:
    snippet = ASSETS_DIR / "logo-snippet.html"
    if snippet.is_file():
        return snippet.read_text(encoding="utf-8").strip()
    if ENROLLMENT_SHELL.is_file():
        html = ENROLLMENT_SHELL.read_text(encoding="utf-8")
        m = re.search(r"<div class=\"logo-wrap\">.*?</div>\s*</div>", html, re.DOTALL)
        if m:
            return m.group(0)
    return """<div class="logo-wrap"><div><div class="logo-text">High Ticket<br>Sales Academy</div><div class="logo-sub">Where Sales Reps Meet Their Forever Career</div></div></div>"""


def enrollment_css() -> str:
    path = ASSETS_DIR / "enrollment-styles.css"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    html = ENROLLMENT_SHELL.read_text(encoding="utf-8")
    return re.search(r"<style>(.*?)</style>", html, re.DOTALL).group(1)


def enrollment_snippet(name: str) -> str:
    path = ASSETS_DIR / name
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""


def render_curriculum_compact_html(items: list) -> str:
    cards = []
    for item in items:
        cards.append(
            f"""<div class="rl-cur-item">
  <div class="rl-cur-icon">{item["icon"]}</div>
  <div class="rl-cur-body"><h5>{item["title"]}</h5><p>{item["desc"]}</p></div>
</div>"""
        )
    return f'<div class="rl-curriculum-grid">{"".join(cards)}</div>'


def render_questions_html(questions: list, curriculum_items: list | None = None) -> str:
    parts = []
    for i, q in enumerate(questions, 1):
        probes = q.get("probes") or []
        probe_html = ""
        if probes:
            items = "".join(f"<li>{p}</li>" for p in probes)
            probe_html = f"<ul>{items}</ul>"
        subtitle = q.get("subtitle", "")
        sub_html = f'<p class="rl-q-sub">{subtitle}</p>' if subtitle else ""
        ours = q["ours_html"]
        if q.get("include_curriculum") and curriculum_items:
            ours += render_curriculum_compact_html(curriculum_items)
        parts.append(
            f"""<div class="rl-q-item">
  <h4>{i}. {q["title"]}</h4>
  {sub_html}
  {probe_html}
  <div class="rl-q-ours">{ours}</div>
</div>"""
        )
    return "\n".join(parts)


def resource_card(href: str, badge: str, title: str, desc: str, cta: str, variant: str = "compact") -> str:
    cls = "cj-resource-card"
    if variant == "featured":
        cls += " cj-resource-card--featured"
    elif variant == "placement":
        cls += " cj-resource-card--placement"
    elif variant == "compact":
        cls += " cj-resource-card--compact"
    badge_html = f'<div class="cj-resource-card-badge">{badge}</div>' if badge else ""
    return f"""<a href="{escape(href)}" class="{cls}" target="_blank" rel="noopener noreferrer">
  {badge_html}
  <div class="cj-resource-card-title">{title}</div>
  <p class="cj-resource-card-desc">{desc}</p>
  <span class="cj-resource-card-cta">{cta}</span>
</a>"""


def render_resources_html(first_name: str) -> str:
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
    feat_grid = "\n".join(featured)
    place_grid = "\n".join(placement)
    compact_grid = "\n".join(compact)
    return f"""
  <div class="cj-resources-wrap">
    <p class="cj-resources-lead"><strong>{escape(first_name)}</strong> — start with the ⭐ picks below. These are the videos and links I most want you to review.</p>
    <p class="cj-resources-kicker">⭐ Start here — CJ's top picks</p>
    <div class="cj-resources-featured">{feat_grid}</div>
    <p class="cj-resources-kicker">⭐ Placement — why our members get results</p>
    <div class="cj-resources-featured">{place_grid}</div>
    <p class="cj-resources-kicker">More success stories from our network</p>
    <div class="cj-resources-grid">{compact_grid}</div>
  </div>"""


def render_personal_reviews_html(reviews: list, title: str = "A few of CJ's Personal Reviews") -> str:
    """Build ref-strip from prospect-specific personal review quotes."""
    def card_html(r: dict) -> str:
        context = r.get("context", "shared with HTSA")
        return f"""          <div class="ref-strip-quote ref-strip-quote--compact">
            <div class="ref-strip-quote-meta">To CJ</div>
            <blockquote class="ref-strip-quote-body">{r["body"]}</blockquote>
            <p class="ref-strip-quote-attr">— {r["name"]} · {context}</p>
          </div>"""

    left_reviews = [r for r in reviews if not r.get("bottom_right")]
    right_reviews = [r for r in reviews if r.get("bottom_right")]

    if not right_reviews:
        mid = (len(reviews) + 1) // 2
        left_reviews = reviews[:mid]
        right_reviews = reviews[mid:]

    left = "\n".join(card_html(r) for r in left_reviews)
    right = "\n".join(card_html(r) for r in right_reviews)
    right_wrap_class = "ref-strip-quote-wrap ref-strip-quote-wrap--pin-bottom" if right_reviews else "ref-strip-quote-wrap"
    return f"""<!-- CJ personal reviews (prospect-specific) -->
  <div class="ref-strip">
    <div class="ref-strip-inner">
      <div class="ref-strip-links-col">
        <div class="ref-strip-label">{title}</div>
        <p style="font-size:12px;line-height:1.6;color:var(--muted);margin:0 0 14px;max-width:320px;">Real messages and posts from people who worked directly with CJ, not copied from Trustpilot.</p>
        <div class="ref-strip-mini-stack">
{left}
        </div>
      </div>
      <div class="{right_wrap_class}" style="gap:14px;">
{right}
      </div>
    </div>
  </div>"""


GAS_TRACKING_ENDPOINT = (
    "https://script.google.com/macros/s/AKfycbxeyf0Q_wiM-d6pq5DnBNKUDVTvMvzFwD60DPpjMEm60LnIQ2tjSkGmy5u1Gt5sQa4Jng/exec"
)


def resource_tracking_script(slug: str, data: dict) -> str:
    """Log page opens, confirm clicks, and resource link clicks to Google Sheets via Apps Script."""
    prospect_name = data.get("prospect_name", "")
    email = data.get("email", "")
    phone = data.get("phone_e164", "")
    prospect_id = data.get("prospect_id", "")
    confirm_label = data.get("confirm_call_label", "Confirm 2pm Call (30 minutes)")
    scheduled = data.get("scheduled_call_note", "2pm EST")

    return f"""<script>
(function(){{
  var GAS_ENDPOINT = {json.dumps(GAS_TRACKING_ENDPOINT)};
  var slug = {json.dumps(slug)};
  var confirmLabel = {json.dumps(confirm_label)};
  var scheduledNote = {json.dumps(scheduled)};
  var meta = {{
    fullName: {json.dumps(prospect_name)},
    email: {json.dumps(email)},
    phone: {json.dumps(phone)},
    clientSlug: {json.dumps(prospect_id)},
    resourceSlug: slug
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

  if (!sessionStorage.getItem('htsa_rl_open_'+slug)) {{
    sessionStorage.setItem('htsa_rl_open_'+slug, '1');
    if(!document.getElementById('email-gate')) postEvent('page_open');
  }}

  window.__htsaRlUnlock=function(){{
    if(sessionStorage.getItem('htsa_rl_open_'+slug)) return;
    sessionStorage.setItem('htsa_rl_open_'+slug, '1');
    postEvent('page_open');
  }};

  var confirmBtn = document.getElementById('rl-confirm-call');
  if (confirmBtn) {{
    confirmBtn.addEventListener('click', function() {{
      if (confirmBtn.getAttribute('data-confirmed') === '1') return;
      confirmBtn.setAttribute('data-confirmed', '1');
      confirmBtn.textContent = 'Confirmed — see you at 2pm EST ✓';
      confirmBtn.classList.add('invest-btn--confirmed');
      var note = document.getElementById('rl-confirm-note');
      if (note) note.textContent = 'Thank you, Tammy. I got it — see you soon.';
      postEvent('call_confirm', {{ scheduledCall: scheduledNote }});
    }});
  }}

  document.querySelectorAll('.cj-resource-card').forEach(function(card) {{
    card.addEventListener('click', function() {{
      var titleEl = card.querySelector('.cj-resource-card-title');
      postEvent('link_click', {{
        linkLabel: titleEl ? titleEl.textContent.trim() : '',
        linkUrl: card.getAttribute('href') || ''
      }});
    }});
  }});

  document.querySelectorAll('.rl-member-card').forEach(function(card) {{
    card.addEventListener('click', function() {{
      var nameEl = card.querySelector('.rl-member-name');
      postEvent('member_text_click', {{
        linkLabel: nameEl ? nameEl.textContent.trim() : '',
        linkUrl: card.getAttribute('href') || ''
      }});
    }});
  }});
}})();
</script>"""


def tracking_script(slug: str) -> str:
    token = os.environ.get("RESOURCE_LINK_TRACK_TOKEN", "").strip()
    if not token:
        return """<script>
(function(){
  var slug=""" + json.dumps(slug) + """;
  if(sessionStorage.getItem('htsa_rv_'+slug)) return;
  sessionStorage.setItem('htsa_rv_'+slug,'1');
  fetch('/r/_manifest.json?v='+Date.now()).then(function(r){return r.json();}).then(function(m){
    if(!m.links||!m.links[slug]) return;
    m.links[slug]._local_viewed_at=new Date().toISOString();
  }).catch(function(){});
})();
</script>"""
    enc = base64.b64encode(token.encode()).decode()
    return f"""<script>
(function(){{
  var slug={json.dumps(slug)};
  var token=atob({json.dumps(enc)});
  if(sessionStorage.getItem('htsa_rv_'+slug)) return;
  sessionStorage.setItem('htsa_rv_'+slug,'1');
  var path='resource-links/registry.json';
  var api='https://api.github.com/repos/clay81090/closewithcjclay.com/contents/'+path;
  fetch(api,{{headers:{{Authorization:'Bearer '+token,Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}}}})
    .then(function(r){{return r.json();}})
    .then(function(file){{
      if(!file.content) return;
      var reg=JSON.parse(atob(file.content.replace(/\\n/g,'')));
      if(!reg.links||!reg.links[slug]||reg.links[slug].status!=='active') return;
      reg.links[slug].view_count=(reg.links[slug].view_count||0)+1;
      reg.links[slug].last_viewed_at=new Date().toISOString();
      return fetch(api,{{
        method:'PUT',
        headers:{{Authorization:'Bearer '+token,Accept:'application/vnd.github+json','Content-Type':'application/json','X-GitHub-Api-Version':'2022-11-28'}},
        body:JSON.stringify({{
          message:'Resource link view '+slug,
          content:btoa(unescape(encodeURIComponent(JSON.stringify(reg,null,2)+'\\n'))),
          sha:file.sha
        }})
      }});
    }}).catch(function(){{}});
}})();
</script>"""


def email_gate_overlay(data: dict) -> str:
    """Email gate overlay HTML only (script runs at end of body)."""
    first_name = escape(data.get("first_name", "Friend"))
    return f"""<div id="email-gate" class="email-gate">
  <div class="email-gate-card">
    <div class="email-gate-badge">Private Page</div>
    <p class="email-gate-lead">Prepared for {first_name}</p>
    <p class="email-gate-sub">This link is personal. Enter the email address it was sent to and only that address will open it.</p>
    <label for="email-gate-input">Your email</label>
    <input id="email-gate-input" type="email" autocomplete="email" inputmode="email" placeholder="you@email.com" />
    <button type="button" id="email-gate-btn" class="invest-btn">Open my page</button>
    <p id="email-gate-err" class="email-gate-err" hidden>This page is not available for that email. If someone forwarded this link, it will not work without the original recipient email.</p>
    <p class="email-gate-foot">Do not share this link. It is intended for {first_name} only.</p>
  </div>
</div>"""


def email_gate_init_script(slug: str, data: dict) -> str:
    """Initialize email gate after #main-content exists in the DOM."""
    allowed = list(data.get("allowed_emails") or [])
    prospect_email = (data.get("email") or "").strip().lower()
    if prospect_email and prospect_email not in [e.lower() for e in allowed]:
        allowed.append(prospect_email)
    for owner in data.get("owner_emails") or ["cj@highticketsalesacademy.com"]:
        owner = owner.strip().lower()
        if owner and owner not in [e.lower() for e in allowed]:
            allowed.append(owner)
    allowed_json = json.dumps([e.lower() for e in allowed])
    storage_key = f"htsa_rl_email_{slug}"

    return f"""<script>
(function(){{
  var allowed={allowed_json};
  var storageKey={json.dumps(storage_key)};
  var gate=document.getElementById('email-gate');
  var main=document.getElementById('main-content');
  if(!gate||!main) return;

  function normEmail(v){{ return (v||'').trim().toLowerCase(); }}
  function isAllowed(v){{ return allowed.indexOf(normEmail(v))!==-1; }}

  function unlock(){{
    gate.remove();
    main.hidden=false;
    if(window.__htsaRlUnlock) window.__htsaRlUnlock();
  }}

  if(sessionStorage.getItem(storageKey)==='1'){{ unlock(); return; }}

  main.hidden=true;
  document.getElementById('email-gate-btn').addEventListener('click',function(){{
    var v=normEmail(document.getElementById('email-gate-input').value);
    if(isAllowed(v)){{ sessionStorage.setItem(storageKey,'1'); unlock(); }}
    else document.getElementById('email-gate-err').hidden=false;
  }});
  document.getElementById('email-gate-input').addEventListener('keydown',function(e){{
    if(e.key==='Enter') document.getElementById('email-gate-btn').click();
  }});
}})();
</script>"""


def email_gate_script(slug: str, data: dict) -> str:
    """Soft lock overlay + init script (init is placed at end of body in render)."""
    return email_gate_overlay(data)


def gate_script(first_name: str, enabled: bool) -> str:
    if not enabled:
        return ""
    fn = escape(first_name)
    return f"""<div id="name-gate" class="name-gate">
  <div class="name-gate-card">
    <p class="name-gate-lead">This page was prepared for <strong>{fn}</strong>.</p>
    <label for="gate-input">Enter your first name to continue</label>
    <input id="gate-input" type="text" autocomplete="given-name" inputmode="text" />
    <button type="button" id="gate-btn" class="invest-btn">Continue</button>
    <p id="gate-err" class="name-gate-err" hidden>That doesn't match. If this page wasn't meant for you, please close it.</p>
  </div>
</div>
<script>
(function(){{
  function init(){{
    var expected={json.dumps(first_name.lower())};
    var gate=document.getElementById('name-gate');
    var main=document.getElementById('main-content');
    if(!gate||!main) return;
    main.hidden=true;
    document.getElementById('gate-btn').addEventListener('click',function(){{
      var v=(document.getElementById('gate-input').value||'').trim().toLowerCase();
      if(v===expected){{ gate.remove(); main.hidden=false; }}
      else document.getElementById('gate-err').hidden=false;
    }});
    document.getElementById('gate-input').addEventListener('keydown',function(e){{
      if(e.key==='Enter') document.getElementById('gate-btn').click();
    }});
  }}
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init);
  else init();
}})();
</script>"""


def manifest_guard_script(slug: str) -> str:
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


def render_active_page(slug: str, data: dict) -> str:
    first_name = escape(data.get("first_name", data["prospect_name"].split()[0]))
    prospect_name = escape(data["prospect_name"])
    email = escape(data.get("email", ""))
    phone_display = escape(data.get("phone_display", ""))
    phone_e164 = escape(data.get("phone_e164", ""))
    prepared_date = escape(data.get("prepared_date", ""))
    calendar_url = escape(data.get("calendar_url", "https://meetings.hubspot.com/charles660/cj"))
    ask_heading = escape(data.get("ask_heading", "What I'm asking for"))
    ask_body = data.get("ask_body_html", "")
    confirm_label = escape(data.get("confirm_call_label", "Confirm 2pm Call (30 minutes)"))
    scheduled_note = escape(data.get("scheduled_call_note", "2pm EST"))
    if data.get("email_gate"):
        gate_html = email_gate_script(slug, data)
        gate_init_html = email_gate_init_script(slug, data)
    elif data.get("first_name_gate"):
        gate_html = gate_script(data.get("first_name", "Friend"), True)
        gate_init_html = ""
    else:
        gate_html = ""
        gate_init_html = ""
    main_hidden = " hidden" if data.get("email_gate") or data.get("first_name_gate") else ""

    opener_parts = []
    for p in data.get("opener_paragraphs", []):
        opener_parts.append(f"<p>{p}</p>")
    if data.get("questions_intro"):
        opener_parts.append(f"<p>{data['questions_intro']}</p>")
    opener_html = "\n    ".join(opener_parts)

    ref_strip = (
        render_personal_reviews_html(
            data["personal_reviews"],
            data.get("personal_reviews_title", "A few of CJ's Personal Reviews"),
        )
        if data.get("personal_reviews")
        else enrollment_snippet("ref-strip-snippet.html").replace(
            "Section 4 above", "the video picks above"
        )
    )
    footer_html = enrollment_snippet("footer-snippet.html")
    logo = logo_html()
    css = enrollment_css()

    email_line = f'<a href="mailto:{email}">{email}</a><br>' if email else ""
    phone_line = f'<a href="tel:{phone_e164}">{phone_display}</a><br>' if phone_display else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="robots" content="noindex,nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
<title>HTSA — {prospect_name}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
{css}
</style>
{manifest_guard_script(slug)}
</head>
<body>
{gate_html}
<div class="page" id="main-content"{main_hidden}>

  <!-- HEADER -->
  <div class="header">
    <div>
      {logo}
      <div class="header-tagline" style="margin-top:12px;">Certification &nbsp;·&nbsp; Coaching &nbsp;·&nbsp; Placement</div>
    </div>
    <div class="invoice-meta">
      <div class="invoice-badge">Private Resource Page</div>
      <p><strong>Prepared by:</strong> CJ Clay</p>
      <p><strong>Prepared for:</strong> {prospect_name}</p>
      <p><strong>Date:</strong> {prepared_date}</p>
    </div>
  </div>
  <div class="accent-bar"></div>

  <!-- EMAIL INTRO -->
  <div class="hero-band hero-band--letter">
    {opener_html}
  </div>

  <!-- BILLING -->
  <div class="billing-grid">
    <div class="billing-cell">
      <div class="billing-label">Prepared For</div>
      <div class="billing-name">{prospect_name}</div>
      <div class="billing-detail">
        {email_line}
        {phone_line}
        Private resource page — for {first_name} only
      </div>
    </div>
    <div class="billing-cell">
      <div class="billing-label">Prepared By</div>
      <div class="billing-name">CJ Clay</div>
      <div class="billing-detail">
        HTSA Career Coach<br>
        (616) 612-1735<br>
        <a href="mailto:cj@highticketsalesacademy.com">cj@highticketsalesacademy.com</a><br>
        Call scheduled: 2pm EST
      </div>
    </div>
  </div>

  <!-- QUESTIONS -->
  <div class="sec-head">
    <div class="sec-num">1</div>
    <h3>Questions That Tell Them Apart</h3>
  </div>
  <div class="rl-q-wrap">
{render_questions_html(data.get("questions", []), data.get("curriculum_items"))}
  </div>

  <!-- ASK -->
  <div class="sec-head">
    <div class="sec-num">2</div>
    <h3>{ask_heading}</h3>
  </div>
  <div class="rl-ask-wrap">
    {ask_body}
    <p style="margin-top:16px;">
      <button type="button" id="rl-confirm-call" class="invest-btn">{confirm_label}</button>
    </p>
    <p id="rl-confirm-note" class="rl-confirm-note">One tap — no forms. Just lets me know you saw this.</p>
  </div>

  <!-- RESOURCES -->
  <div class="sec-head">
    <div class="sec-num">3</div>
    <h3>Videos, Proof &amp; Member Stories</h3>
  </div>
{render_resources_html(data.get("first_name", data["prospect_name"].split()[0]))}

  {ref_strip}

  {footer_html}

</div>
{gate_init_html}
{resource_tracking_script(slug, data)}
</body>
</html>"""


def render_expired_page() -> str:
    return EXPIRED_TEMPLATE.read_text(encoding="utf-8")


def write_active(slug: str, html: str) -> None:
    out_dir = R_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")


def write_killed(slug: str) -> None:
    out_dir = R_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(render_expired_page(), encoding="utf-8")


def git_ship(paths: list[str], message: str) -> None:
    for p in paths:
        subprocess.run(["git", "add", p], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=True)


def cmd_create(args: argparse.Namespace) -> None:
    data = load_prospect_data(args.prospect_id)
    reg = load_registry()
    if args.slug:
        slug = normalize_custom_slug(args.slug)
    else:
        slug = gen_slug()
        if len(slug) < SLUG_MIN_LEN:
            raise SystemExit(f"Auto slug must be {SLUG_MIN_LEN}+ chars")
    if slug in reg.get("links", {}):
        raise SystemExit(f"Slug already exists: {slug}")

    created = utcnow()
    expires = created + timedelta(days=EXPIRE_DAYS)
    reg.setdefault("links", {})[slug] = {
        "slug": slug,
        "prospect_id": args.prospect_id,
        "prospect_name": data["prospect_name"],
        "email": data.get("email"),
        "phone_e164": data.get("phone_e164"),
        "phone_display": data.get("phone_display"),
        "created_at": iso(created),
        "expires_at": iso(expires),
        "status": "active",
        "view_count": 0,
        "last_viewed_at": None,
    }
    save_registry(reg)
    html = render_active_page(slug, data)
    write_active(slug, html)

    # Shared expired page
    (R_DIR / "_expired.html").write_text(render_expired_page(), encoding="utf-8")

    url = f"https://closewithcjclay.com/r/{slug}/"
    print(f"Created: {url}")
    print(f"Slug: {slug}")
    print(f"Expires: {iso(expires)}")

    if args.ship:
        git_ship(
            [
                f"r/{slug}/index.html",
                "r/_manifest.json",
                "r/_expired.html",
                "resource-links/registry.json",
            ],
            f"Add resource link for {data['prospect_name']} (/r/{slug}).",
        )
        print("Pushed to origin/main.")


def cmd_kill(args: argparse.Namespace) -> None:
    reg = load_registry()
    link = reg.get("links", {}).get(args.slug)
    if not link:
        raise SystemExit(f"Unknown slug: {args.slug}")
    link["status"] = "killed"
    link["killed_at"] = iso(utcnow())
    save_registry(reg)
    write_killed(args.slug)
    print(f"Killed: /r/{args.slug}/")
    if args.ship:
        git_ship(
            [f"r/{args.slug}/index.html", "r/_manifest.json", "resource-links/registry.json"],
            f"Kill resource link /r/{args.slug}.",
        )
        print("Pushed to origin/main.")


def cmd_list(_: argparse.Namespace) -> None:
    reg = load_registry()
    links = reg.get("links", {})
    if not links:
        print("No resource links.")
        return
    for slug, link in sorted(links.items(), key=lambda x: x[1].get("created_at", ""), reverse=True):
        print(
            f"{slug}\t{link.get('status')}\tviews={link.get('view_count', 0)}\t"
            f"{link.get('prospect_name')}\texpires={link.get('expires_at')}"
        )
        if link.get("email"):
            print(f"  email: {link['email']}")
        if link.get("phone_display"):
            print(f"  phone: {link['phone_display']}")
        if link.get("last_viewed_at"):
            print(f"  last viewed: {link['last_viewed_at']}")


def cmd_rebuild(args: argparse.Namespace) -> None:
    reg = load_registry()
    for slug, link in reg.get("links", {}).items():
        if link.get("status") == "active":
            data = load_prospect_data(link["prospect_id"])
            write_active(slug, render_active_page(slug, data))
        else:
            write_killed(slug)
    (R_DIR / "_expired.html").write_text(render_expired_page(), encoding="utf-8")
    write_manifest(reg)
    print("Rebuilt all resource link pages.")
    if args.ship:
        git_ship(["r/", "resource-links/registry.json"], "Rebuild resource link pages.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Private revocable resource pages (/r/<slug>).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_create = sub.add_parser("create", help="Create a new resource link from data/<prospect_id>.json")
    p_create.add_argument("prospect_id")
    p_create.add_argument("--slug", help="Custom slug (default: random 24 chars)")
    p_create.add_argument("--ship", action="store_true", help="Commit and push")
    p_create.set_defaults(func=cmd_create)

    p_kill = sub.add_parser("kill", help="Kill a resource link immediately")
    p_kill.add_argument("slug")
    p_kill.add_argument("--ship", action="store_true")
    p_kill.set_defaults(func=cmd_kill)

    p_list = sub.add_parser("list", help="List all resource links")
    p_list.set_defaults(func=cmd_list)

    p_rebuild = sub.add_parser("rebuild", help="Rebuild all pages from registry + data")
    p_rebuild.add_argument("--ship", action="store_true")
    p_rebuild.set_defaults(func=cmd_rebuild)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
