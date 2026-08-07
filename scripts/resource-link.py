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
PAGE_TEMPLATE = ROOT / "resource-links" / "templates" / "page.html"
LOGO_SNIPPET_PATH = ROOT / "resource-links" / "assets" / "logo-snippet.html"

EXPIRE_DAYS = 14
SLUG_MIN_LEN = 16


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
    if LOGO_SNIPPET_PATH.is_file():
        return LOGO_SNIPPET_PATH.read_text(encoding="utf-8").strip()
    return """<div class="logo-wrap">
        <div>
          <div class="logo-text">High Ticket<br>Sales Academy</div>
          <div class="logo-sub">Where Sales Reps Meet Their Forever Career</div>
        </div>
      </div>"""


def render_questions_html(questions: list) -> str:
    parts = []
    for i, q in enumerate(questions, 1):
        probes = q.get("probes") or []
        probe_html = ""
        if probes:
            items = "".join(f"<li>{p}</li>" for p in probes)
            probe_html = f"<ul class=\"q-probes\">{items}</ul>"
        subtitle = q.get("subtitle", "")
        sub_html = f'<p class="q-sub">{subtitle}</p>' if subtitle else ""
        parts.append(
            f"""<details class="q-item">
  <summary><span class="q-num">{i}</span><span class="q-title">{q["title"]}</span></summary>
  <div class="q-body">
    {sub_html}
    {probe_html}
    <div class="q-ours">{q["ours_html"]}</div>
  </div>
</details>"""
        )
    return "\n".join(parts)


def render_videos_html(videos: list) -> str:
    parts = []
    for v in videos:
        featured = v.get("featured")
        feat_cls = " video-card--featured" if featured else ""
        feat_badge = (
            f'<div class="video-badge">{escape(v.get("featured_label", "Featured"))}</div>'
            if featured
            else ""
        )
        if v.get("is_link_card"):
            parts.append(
                f"""<a class="video-card video-card--link{feat_cls}" href="{escape(v["external_url"])}" target="_blank" rel="noopener noreferrer">
  {feat_badge}
  <div class="video-card-title">{escape(v["title"])}</div>
  <div class="video-card-desc">{v["description"]}</div>
  <span class="video-link-cta">Open Trustpilot →</span>
</a>"""
            )
            continue
        yid = v.get("youtube_id")
        if not yid:
            continue
        parts.append(
            f"""<div class="video-card{feat_cls}">
  {feat_badge}
  <div class="video-embed"><iframe src="https://www.youtube-nocookie.com/embed/{escape(yid)}" title="{escape(v["title"])}" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>
  <div class="video-card-title">{escape(v["title"])}</div>
  <div class="video-card-desc">{v["description"]}</div>
</div>"""
        )
    return "\n".join(parts)


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
    tpl = PAGE_TEMPLATE.read_text(encoding="utf-8")
    opener = "".join(f"<p>{p}</p>" for p in data.get("opener_paragraphs", []))
    subs = {
        "SLUG": slug,
        "PROSPECT_NAME": escape(data["prospect_name"]),
        "FIRST_NAME": escape(data.get("first_name", data["prospect_name"].split()[0])),
        "PREPARED_DATE": escape(data.get("prepared_date", "")),
        "LOGO_HTML": logo_html(),
        "OPENER_HTML": opener,
        "QUESTIONS_INTRO": data.get("questions_intro", ""),
        "QUESTIONS_HTML": render_questions_html(data.get("questions", [])),
        "VIDEOS_HTML": render_videos_html(data.get("videos", [])),
        "ASK_HEADING": escape(data.get("ask_heading", "What I'm asking for")),
        "ASK_BODY_HTML": data.get("ask_body_html", ""),
        "CALENDAR_URL": escape(data.get("calendar_url", "https://meetings.hubspot.com/charles660/cj")),
        "FOOTER_NOTE": escape(data.get("footer_note", "High Ticket Sales Academy")),
        "GATE_HTML": gate_script(data.get("first_name", "Friend"), data.get("first_name_gate", False)),
        "MANIFEST_GUARD": manifest_guard_script(slug),
        "TRACKING_SCRIPT": tracking_script(slug),
    }
    out = tpl
    for k, v in subs.items():
        out = out.replace("{{" + k + "}}", v)
    return out


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
    slug = args.slug or gen_slug()
    if len(slug) < SLUG_MIN_LEN:
        raise SystemExit(f"Slug must be {SLUG_MIN_LEN}+ chars")
    if slug in reg.get("links", {}):
        raise SystemExit(f"Slug already exists: {slug}")

    created = utcnow()
    expires = created + timedelta(days=EXPIRE_DAYS)
    reg.setdefault("links", {})[slug] = {
        "slug": slug,
        "prospect_id": args.prospect_id,
        "prospect_name": data["prospect_name"],
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
