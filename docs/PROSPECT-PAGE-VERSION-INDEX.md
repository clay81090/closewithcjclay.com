# HTSA · Master version index (Notion)

**Paste this page into Notion as-is.**

This is the full map of what CJ sends to prospects **and** the on-call / Co-Pilot tools that live outside the public site.

Rule for versions: **major change only** = final state before the next layout, structure, or offer-flow change. Tiny bold / wording tweaks are skipped.

Archive pages on the site have a red **ARCHIVE PREVIEW** bar so you never mix them with live send links.

---

## Live history hubs (closewithcjclay.com)

| Hub | URL |
|---|---|
| Master (prospect pages) | https://closewithcjclay.com/prospect-version-history.html |
| Special offer self-enroll | https://closewithcjclay.com/special-offer-history.html |
| Pre-call / resources | https://closewithcjclay.com/precall-version-history.html |
| Long enrollment eras (technical) | https://closewithcjclay.com/long-enrollment-version-history.html |

Source markdown in the site repo: `docs/PROSPECT-PAGE-VERSION-INDEX.md`

---

## Quick map · what you send people

| What you say | Live URL | What it is |
|---|---|---|
| Special offer enroll | https://closewithcjclay.com/special-offer.html | Self-enroll, reactivation prices |
| Regular self-enroll | https://closewithcjclay.com/enroll.html | Same page shape, standard prices |
| Close / enroll link (short, Aug 31+) | `htsa-enrollment-<first>-<last>.html` from `_TEMPLATE-close.html` | On-call confirmation page |
| Long enrollment invoice (older style) | Named `htsa-enrollment-*.html` (see §3) | Full invoice: Terms, investment, curriculum |
| Pre call link | `https://closewithcjclay.com/r/<slug>/` | Already booked resources |
| Earnings calculator | https://closewithcjclay.com/pre-call/HTSA-earnings-calculator.html | Projected earnings helper |
| Game plan / 30 day | https://closewithcjclay.com/30-day-roadmap.html | Shared, `?n=First` |
| Referral / meet CJ | https://closewithcjclay.com/meet-cj.html | Friend intro landing |
| Offer link (still need to book) | `<name>-and-cj.html` or special-offer-book-with-cj | HubSpot calendar |

**Internal only (never prospect send links):** Live Call Console, Co-Pilot V3 app, God Script, Gap Math. See §9.

---

## 1. Special offer self-enroll

**Live send:** https://closewithcjclay.com/special-offer.html  
**History:** https://closewithcjclay.com/special-offer-history.html

### Cursor / git (on the live path)

| Ver | Commit | Preview | What changed |
|---|---|---|---|
| V1 | `758910e` | [preview](https://closewithcjclay.com/special-offer-v1-preview.html) | First shared page: plan + pricing + start |
| V2 | `a29aec1` | [preview](https://closewithcjclay.com/special-offer-v2-preview.html) | Hand-selected framing, inline plan, member voices, Terms |
| V3 | `70a10cb` | [preview](https://closewithcjclay.com/special-offer-v3-preview.html) | Compact Janaye, referral form + meet-cj card, footer card |
| V4 | `002a745` | [preview](https://closewithcjclay.com/special-offer-v4-preview.html) | Option B = proven 5-step self-enroll |
| V5 | `f1afb52` | [preview](https://closewithcjclay.com/special-offer-v5-preview.html) | Dual pricing + Sheet tracking |
| V6 | `fc9cc72` | [preview](https://closewithcjclay.com/special-offer-v6-preview.html) | Collapsible Parts |
| **V6B live** | `62143be` | [preview](https://closewithcjclay.com/special-offer-v6b-preview.html) | **Current live.** Basic game plan, courtesy intro, pricing earlier |

### Claude Code sandbox (NOT current live)

Source: `/Users/charlesclay/Documents/SPECIAL-OFFER-CLAUDE-SANDBOX/WORK/`  
Transcript: `Downloads/Claud-Code (Enrollment Page) Full Transcript (Up to v9) .txt`

| Ver | Preview | Notes |
|---|---|---|
| Claude V7 | [preview](https://closewithcjclay.com/special-offer-claude-v7-preview.html) | Liked direction. 90-day value stack + return box. Pricing before start. |
| Claude V8 | [preview](https://closewithcjclay.com/special-offer-claude-v8-preview.html) | Pipe/plumber footer quote + 40/70 |
| Claude V9 | [preview](https://closewithcjclay.com/special-offer-claude-v9-preview.html) | Ink-blue buttons/footer + accordion. **Do not like. Not shipped.** |

**Live is V6B (Cursor), not Claude V9.**

---

## 2. Regular self-enroll (`enroll.html`)

Twin of special-offer with **standard** pricing ($6k / 4×$1750 / $600 Clarity).

**Live:** https://closewithcjclay.com/enroll.html  
Major structure locks with special-offer V5–V6 era (`f1afb52`, `fc9cc72`).

---

## 3. Long enrollment invoices (CJ’s hand-picked timeline)

These are the **full invoices** you sent before the short close-page style. Not every name (200+ still live). Just the milestones you named.

| When | Person | Live link | Notes |
|---|---|---|---|
| Apr 3, 2026 | Bianca Zirwes | https://closewithcjclay.com/htsa-enrollment-bianca-zirwes.html | Early closer invoice |
| Apr 21, 2026 | Amy Grochala | https://closewithcjclay.com/htsa-enrollment-amy-grochala.html | Proven solo / self-enroll long page |
| May 14, 2026 | Nicole Sultana | https://closewithcjclay.com/htsa-enrollment-nichole-sultana.html | Filename uses `nichole-sultana` |
| May 22, 2026 | Christina Nichols | https://closewithcjclay.com/htsa-enrollment-christina-nichols.html | |
| May 26, 2026 | Rebecca Hemion | https://htsa-closer-enrollment-rebecca-hemion.netlify.app/ | **Netlify** (outside closewithcjclay.com) |
| Jun 1, 2026 | Myli Campbell | https://closewithcjclay.com/htsa-enrollment-myli-campbell.html | |
| Jun 2, 2026 | Miranda Mestas | https://closewithcjclay.com/htsa-enrollment-miranda-mestas.html | |
| Jun 13, 2026 | Trisha Ziemba | https://closewithcjclay.com/pre-call/HTSA-earnings-calculator.html | You sent the **earnings calculator** (not a named invoice in this list) |
| Aug 4, 2026 | Cal Halliburton | Enrollment: https://closewithcjclay.com/htsa-enrollment-cal-halliburton.html · Calculator: https://closewithcjclay.com/pre-call/HTSA-earnings-calculator.html | Both pieces |
| Aug 11, 2026 | Charity Diaz | https://closewithcjclay.com/htsa-enrollment-charity-diaz.html | Late long-invoice era, before short close push |

**Amy first-ship archive (Apr 7 git):** https://closewithcjclay.com/enrollment-amy-grochala-first-preview.html

**Technical layout eras** (Marie → Amy template wave → Terms gate → placement shells → Member Voices): https://closewithcjclay.com/long-enrollment-version-history.html

**After this era:** short close pages (§4), starting ~Aug 31, 2026.

---

## 4. Short close pages (Aug 31+)

**Different product from Amy’s long invoice.**

**Template:** `templates/_TEMPLATE-close.html`  
**Preview:** https://closewithcjclay.com/htsa-enrollment-cj-clay.html  
**Archives:** https://closewithcjclay.com/archive/prospect-versions/close-page/

| Ver | Commit | What changed |
|---|---|---|
| V1 | `6609d07` | First close template |
| V2 | `ae94391` | Guarantee-ready + close-page rule |
| V3 | `e781d3d` | After-pay next steps for solo closes |
| V4 | `439e165` | Hide next steps until checkout |
| V5 | `b583eba` | Game plan first, pricing last in dropdown |
| V6 | `c4d7b6c` | Amy-style 2-way enroll steps; remove “what we need from you” |
| V7 | `558c1dc` | Reorder getting → HTSA needs → pricing → next steps (felt like overreach) |

Example: https://closewithcjclay.com/archive/prospect-versions/close-page/close-page-v5.html

---

## 5. 30 day game plan

**Live:** https://closewithcjclay.com/30-day-roadmap.html  
**Archives:** https://closewithcjclay.com/archive/prospect-versions/roadmap-30/

| Ver | Commit | What changed |
|---|---|---|
| V1 | `0c46895` | Moved to root, generalized |
| V2 | `7c73882` | Post-placement = 90-day ramp |
| V3 | `0eabb29` | Expandable dropdown sections |
| V4 | `c4d7b6c` | Removed “Bet on yourself” mid-page |
| V5 | `558c1dc` | Standout Outcome box; removed “Your side of it” |

Setter twin: https://closewithcjclay.com/24-day-roadmap.html

---

## 6. Referral / meet-CJ

**Live:** https://closewithcjclay.com/meet-cj.html  
**Archives:** https://closewithcjclay.com/archive/prospect-versions/meet-cj/

| Ver | Commit | What changed |
|---|---|---|
| V1 | `134491f` | First referral landing |
| V2 | `0634592` | Meet Chad + Website + Taylor, Trustpilot, book, more stories |
| V3 | `0def31f` | Aligned cards, smaller book, cleaned More resources |

---

## 7. Pre-call / resource pages (Tammy → Lynda → now)

**History hub:** https://closewithcjclay.com/precall-version-history.html  
**Live Lynda (current):** https://closewithcjclay.com/r/lynda_perez/  
**Lynda first ship (Mark layout):** https://closewithcjclay.com/precall-lynda-mark-preview.html

| Ver | Commit | Preview | What changed |
|---|---|---|---|
| V01 | `71bc82c` | [Tammy first](https://closewithcjclay.com/archive/prospect-versions/precall-resources/precall-v01-tammy-first.html) | First resource-link page (opaque slug) |
| V02 | `507f2f4` | [CJ reviews](https://closewithcjclay.com/archive/prospect-versions/precall-resources/precall-v02-tammy-cj-reviews.html) | CJ personal reviews on resource pages |
| V03 | `83f001f` | [Tammy Aug 7 final](https://closewithcjclay.com/archive/prospect-versions/precall-resources/precall-v03-tammy-aug7-final.html) | End of first-day rebuilds |
| V04 | `3767665` | [Sarah mid-Aug](https://closewithcjclay.com/archive/prospect-versions/precall-resources/precall-v04-sarah-midaug.html) | Mid-Aug rebuild era |
| V05 | `2883153` | [Blue reviews](https://closewithcjclay.com/archive/prospect-versions/precall-resources/precall-v05-blue-reviews.html) | Blue personal review cards |
| V06 | `d22f8a6` | [White reviews](https://closewithcjclay.com/archive/prospect-versions/precall-resources/precall-v06-white-reviews.html) | White CJ Reviews + centered banner |
| V07 | `f9cb1f1` | [Story cards](https://closewithcjclay.com/archive/prospect-versions/precall-resources/precall-v07-story-cards.html) | 3 white story + 2 blue Top 20 / website |
| V08 | `7c10ecf` | [Mark layout](https://closewithcjclay.com/archive/prospect-versions/precall-resources/precall-v08-mark-layout.html) | Aug 25 Mark-style long precall |
| V09 | `f223105` | [Jane slim](https://closewithcjclay.com/archive/prospect-versions/precall-resources/precall-v09-jane-slim.html) | Jane Bates slim layout |
| V10 | `4620d30` | [Template](https://closewithcjclay.com/archive/prospect-versions/precall-resources/precall-v10-reusable-template.html) | Reusable `_TEMPLATE-precall.html` |
| V11 | `98798de` | [Visible videos](https://closewithcjclay.com/archive/prospect-versions/precall-resources/precall-v11-visible-videos.html) | Taylor + Brianna visible + resources dropdown |
| V12 | `9af6b39` | [Lynda Mark](https://closewithcjclay.com/precall-lynda-mark-preview.html) | Lynda **first** ship |
| V13 | `7c67483` | [Lynda meet-cj](https://closewithcjclay.com/archive/prospect-versions/precall-resources/precall-v13-lynda-meetcj.html) | Lynda → meet-cj 3-up (current shape) |
| V14 | `62143be` | [Gracie](https://closewithcjclay.com/archive/prospect-versions/precall-resources/precall-v14-gracie.html) | DIY-groups framing + Book Appointment |

People live under `/r/<slug>/`. This list is **layout eras**, not every name.

### Related pre-call tools on the site

| Tool | URL |
|---|---|
| Earnings calculator | https://closewithcjclay.com/pre-call/HTSA-earnings-calculator.html |
| OOCEMR decision framework | https://closewithcjclay.com/pre-call/HTSA-oocemr-decision-framework.html |
| Universal resources (older) | https://closewithcjclay.com/pre-call/HTSA-pre-call-resources-universal.html |

---

## 8. Offer booking pages (still need a slot)

**Live shared:** https://closewithcjclay.com/special-offer-book-with-cj.html  
**Named:** `*-and-cj.html`  
**Archives:** https://closewithcjclay.com/archive/prospect-versions/offer-booking/

| Ver | Commit | What changed |
|---|---|---|
| V1 | `19b847a` | First booking page |
| V2 | `629b44a` | Hero = 10 upcoming spots |
| V3 | `ea2f892` | Hero = earning a spot |
| V4 | `5b4d852` | HubSpot `/charles660/cj` |

Internal drafts: `reactivation/book-with-cj.html` (+ v2, v3). Never say “reactivation” to prospects.

---

## 9. On-call / Co-Pilot tools (NOT on the public site yet)

These came back from **CJ AI OS**, **CJ-CoPilot-Lab**, and **HTSA Live Call Lab**. Internal only. No prospect send URL on closewithcjclay.com today.

### A. HTSA Live Call Console

Single-file browser on-call script (phases, track chips, objections, setter upload, stories).

**Canonical folder (prefer this over Lab if dates disagree):**  
`/Users/charlesclay/CJ_AI_OS/06_LIVE_AI_COPILOT_PRODUCT/co-pilot-v4/`  
GitHub: `https://github.com/clay81090/CJ-AI-OS` (private) · branch with consoles: `cursor/jul-3-revenue-prep-and-call-vault`

| Ver | File | When | Notes |
|---|---|---|---|
| original | `htsa-live-call-console.original.html` | Sep 2, 2026 ~3:45 PM | Claude/Codex export backup |
| v4 | `htsa-live-call-console.html` | Sep 2, 2026 | Dark UI / Career Launcher spine (`aac5c1a`) |
| v5 | `htsa-live-call-console-v5.html` | Sep 2–4, 2026 | Codex merge: paper stage, sidebar intel, routes, objection loop, close sequence. Prefer if you want the fuller sidebar UI. |
| **v6 preferred** | `htsa-live-call-console-v6.html` | Sep 2–4, 2026 | Claude rebuild / simpler dark UI; stories + track-lock Sep 4. **Current preferred for latest edits.** |

Also mirrored (may lag OS):

- Lab on-call: `/Users/charlesclay/Documents/HTSA_LIVE_CALL_LAB/00_ON_CALL/htsa-live-call-console-v6.html` (Sep 2 snapshot, older than OS v6)
- Lab versions museum: `…/HTSA_LIVE_CALL_LAB/_VERSIONS/2026-09-02_htsa-live-call-console*.html`
- Claude Lab sandbox: `/Users/charlesclay/Documents/CJ-CO-PILOT-V3-FOR-CLAUDE/co-pilot-v4/htsa-live-call-console*.html`

**No v7 found. Not deployed to closewithcjclay.com.**

Handoff note: `…/co-pilot-v4/V5_MERGE_HANDOFF.md`

---

### B. Co-Pilot V3 Live Call app

Full Live AI Co-Pilot web app (Deepgram/loopback, pattern index). Title: “CJ CO-PILOT V3 — Live Call”.

| | |
|---|---|
| Path | `/Users/charlesclay/CJ_AI_OS/06_LIVE_AI_COPILOT_PRODUCT/co-pilot-v3/index.html` |
| Launcher | `…/launchers/start-co-pilot.sh` |
| Restore log | `co-pilot-v3/RESTORE_HISTORY.md` |
| Versions | Folder named v3; file date ~Jul 23, 2026. Exact majors beyond that: unknown. |
| Prefer | `co-pilot-v3` for the product app; Live Call Console (§9A) for no-API call sheets |
| Prospects? | **No** |

---

### C. God Script

| Ver | Where | Notes |
|---|---|---|
| Genspark V1 + Apr 8 snapshot | `/Users/charlesclay/Documents/CJ-CO-PILOT-V3-FOR-CLAUDE/GENSPARK-V1/htsa-god-script/` | Early UI + `_snapshot-2026-04-08-notes-and-mobile-bar/` |
| v2 → v3 → v5 evolution | `/Users/charlesclay/Documents/HTSA_LIVE_CALL_LAB/_VERSIONS/god_script_evolution/` | `htsa-god-script-v2.html`, `v3`, `v5` |
| Parallel Sep 2 builds | Lab `_VERSIONS/` + `03_CODEX/` + `04_GENSPARK/` | Codex generic + Genspark dated builds |
| **V5 product canonical** | `/Users/charlesclay/CJ_AI_OS/06_LIVE_AI_COPILOT_PRODUCT/co-pilot-v4/brain/HTSA_GOD_SCRIPT_V5.html` | Aug 11, 2026 + `HTSA_GOD_SCRIPT_V5_CONTENT.md` |
| V5 site copy | `closewithcjclay.com/private/htsa-god-script-v5.html` (+ root `htsa-god-script.html`) | Sibling of product brain. Diff before assuming identical. |
| V5 Documents standalone | `/Users/charlesclay/Documents/HTSA_GOD_SCRIPT_V5.html` | Same era. Dedupe vs site private. |
| V6 | Instructions only: `…/co-pilot-v4/GOD_SCRIPT_V6_BUILD_INSTRUCTIONS.md` (Aug 25, 2026) | **No complete God Script v6 HTML found** |

**Preferred:** product brain `HTSA_GOD_SCRIPT_V5.html` for builder canonical; Lab `_READ_ONLY_AMMO/03_god_script/HTSA_GOD_SCRIPT_V5.html` for official ammo.  
**Prospects?** No.

---

### D. Gap Math (on-call helpers)

`/Users/charlesclay/Documents/HTSA_LIVE_CALL_LAB/_READ_ONLY_AMMO/11_gap_math/`

| File | Role |
|---|---|
| `gap-math-v2.html` | Older |
| `gap-math-v3.html` | Mid |
| `gap-math-live.html` | Name suggests current |
| `dina-the-math.html` | Dina-specific |

Usually internal / screen-share. Preferred among v2/v3/live: unknown until compared.

---

### E. Codex pre-call experience (builder only)

Not the same as prospect `/r/` pages already indexed.

- `/Users/charlesclay/Documents/HTSA_LIVE_CALL_LAB/03_CODEX/HTSA-pre-call-experience.html`
- `/Users/charlesclay/Documents/HTSA_LIVE_CALL_LAB/03_CODEX/HTSA-pre-call-cursor-restored.html`

Which superseded which: unknown. Prospects? No.

---

## 10. Other projects on disk (indexed lightly)

| Project | Path | What it is | Prospects? |
|---|---|---|---|
| HTSA Invoice app | `/Users/charlesclay/HTSA Invoice/` | Quoting / invoice product | Yes (quote outputs), separate from enrollment HTML |
| Home HTSA CO-PILOT | `/Users/charlesclay/HTSA CO-PILOT/` | Older product / docs / KB | No |
| CLAUDE CO-PILOT | `/Users/charlesclay/CLAUDE CO-PILOT/` | Present | No |
| COPILOT:GENSPSRK | `/Users/charlesclay/COPILOT:GENSPSRK/` (+ zip) | Genspark co-pilot workspace | No |
| Continuous Improvement | `/Users/charlesclay/Documents/Continuous Improvement - HTSA Calls.pdf` (+ `.pages`) | Process docs | No |
| Lab Documents site mirror | `/Users/charlesclay/Documents/CJ-CO-PILOT-V3-FOR-CLAUDE/closewithcjclay.com/` | ~200+ enrollment copies | Backup only. **Site git is source of truth.** Diff before re-indexing. |
| Special-Offer Claude Sandbox | `/Users/charlesclay/Documents/SPECIAL-OFFER-CLAUDE-SANDBOX/WORK/` | Claude V7–V9 working files | Already mirrored into site archive previews |

Home Co-Pilot folders need a dedicated pass before claiming exact version numbers.

---

## 11. Still missing / open

| Item | Status |
|---|---|
| Hosted Live Console or Co-Pilot URL on closewithcjclay.com | **Not deployed** (handoff still open) |
| Live Console v7+ | **None found** |
| Complete God Script v6 HTML | **None found** (instructions only) |
| God Script v1 / v4 in Lab evolution folder | **Jump is v2 → v3 → v5** (Genspark V1 exists separately) |
| Durable Claude artifact preview URLs | Not stored as files |
| Exact majors inside home Co-Pilot folders | Not audited file-by-file |
| Tiny wording history for consoles | Intentionally skipped |

---

## How the pieces fit (one glance)

```
PROSPECT-FACING (closewithcjclay.com)
  Special offer / enroll.html
  Long invoices (Bianca → Charity timeline above)
  Short close pages (Aug 31+)
  Pre-call /r/ pages + earnings calculator
  30-day roadmap · meet-cj · offer booking

ON-CALL / INTERNAL (not public site)
  Live Call Console original → v4 → v5 → v6   ← prefer CJ_AI_OS v6
  Co-Pilot V3 app
  God Script (Genspark V1 → Lab v2/v3/v5 → product V5)
  Gap Math · Codex pre-call experiments

OTHER PRODUCTS
  HTSA Invoice app
  Home Co-Pilot folders (needs deeper pass)
```

---

## Recommended next (only if you ask)

1. Special offer: stay on **V6B**, lean toward **Claude V7**, avoid **V9**.
2. Short close: treat **V5 or V6** as the trusted restore point before V7 overreach.
3. Deploy Live Console v6 (or v5 sidebar) to a private closewithcjclay URL when ready.
4. Diff product brain God Script V5 vs `private/htsa-god-script-v5.html` and keep one canonical.
5. Optional: dedicated version pass on home Co-Pilot folders + HTSA Invoice.

---

*Master index for CJ · Notion-ready · updated with CJ AI OS / Lab / Co-Pilot inventory + hand-picked long-enrollment timeline.*
