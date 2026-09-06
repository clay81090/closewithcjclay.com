# closewithcjclay.com · Prospect page version index

**For Notion.** Paste this page as-is. Master live index:

https://closewithcjclay.com/prospect-version-history.html

Special-offer only (extended):

https://closewithcjclay.com/special-offer-history.html

Rule used for versions: **major change only** = final state before the next layout / structure / offer-flow change. Tiny bold/wording tweaks are skipped.

Archive pages have a red **ARCHIVE PREVIEW** bar. Live send links stay unchanged.

---

## Quick map (what you send people)

| What you say | Live URL | What it is |
|---|---|---|
| Special offer enroll (reactivation prices) | https://closewithcjclay.com/special-offer.html | Self-enroll, no call required |
| Regular self-enroll (standard prices) | https://closewithcjclay.com/enroll.html | Twin of special-offer, standard pricing |
| Close / enroll link (on a call) | `htsa-enrollment-<first>-<last>.html` | Short close page from `_TEMPLATE-close.html` |
| Pre call link | `https://closewithcjclay.com/r/<slug>/` | Already booked resources page |
| Game plan / 30 day | https://closewithcjclay.com/30-day-roadmap.html | Shared, `?n=First` |
| Referral / meet CJ | https://closewithcjclay.com/meet-cj.html | Friend intro landing |
| Offer link (still need to book) | `<name>-and-cj.html` or special-offer-book-with-cj | HubSpot calendar |

---

## 1. Special offer self-enroll

**Live:** https://closewithcjclay.com/special-offer.html  
**History:** https://closewithcjclay.com/special-offer-history.html

### Cursor / git (shipped or were on the live path)

| Ver | Commit | Preview | What changed |
|---|---|---|---|
| V1 | `758910e` | [/special-offer-v1-preview.html](https://closewithcjclay.com/special-offer-v1-preview.html) | First shared page: plan + pricing + start steps |
| V2 | `a29aec1` | [/special-offer-v2-preview.html](https://closewithcjclay.com/special-offer-v2-preview.html) | Hand-selected framing, inline plan, member voices, Terms |
| V3 | `70a10cb` | [/special-offer-v3-preview.html](https://closewithcjclay.com/special-offer-v3-preview.html) | Compact Janaye, referral form + meet-cj card, footer card (green “what we need” era) |
| V4 | `002a745` | [/special-offer-v4-preview.html](https://closewithcjclay.com/special-offer-v4-preview.html) | Option B fixed to proven 5-step self-enroll |
| V5 | `f1afb52` | [/special-offer-v5-preview.html](https://closewithcjclay.com/special-offer-v5-preview.html) | Dual pricing + Sheet tracking |
| V6 | `fc9cc72` | [/special-offer-v6-preview.html](https://closewithcjclay.com/special-offer-v6-preview.html) | Collapsible Parts |
| **V6B live Cursor** | `62143be` | [/special-offer-v6b-preview.html](https://closewithcjclay.com/special-offer-v6b-preview.html) | **Current live.** Basic game plan, courtesy intro, pricing earlier |

### Claude Code sandbox (NOT shipped to live)

Source folder: `/Users/charlesclay/Documents/SPECIAL-OFFER-CLAUDE-SANDBOX/WORK/`

| Ver | Preview | Status |
|---|---|---|
| Claude V7 | [/special-offer-claude-v7-preview.html](https://closewithcjclay.com/special-offer-claude-v7-preview.html) | You liked this direction. Janaye removed. 90-day value stack + return box. Pricing before start. |
| Claude V8 | [/special-offer-claude-v8-preview.html](https://closewithcjclay.com/special-offer-claude-v8-preview.html) | Pipe/plumber footer quote + 40/70 message |
| Claude V9 | [/special-offer-claude-v9-preview.html](https://closewithcjclay.com/special-offer-claude-v9-preview.html) | Ink-blue buttons/footer + accordion exclusivity. **You do not like this.** |

Transcript used: `Downloads/Claud-Code (Enrollment Page) Full Transcript (Up to v9) .txt`

**Note:** Live `special-offer.html` is V6B (Cursor simplify), **not** Claude V9.

---

## 2. Regular self-enroll (`enroll.html`)

Twin of special-offer with **standard** pricing ($6k / 4×$1750 / $600 Clarity). Major structure commits: `f1afb52`, `fc9cc72`. Same Part layout as special-offer V5–V6 era.

Live: https://closewithcjclay.com/enroll.html

---

## 3. Close / enrollment page (short close template)

**Template:** `templates/_TEMPLATE-close.html`  
**Preview person:** https://closewithcjclay.com/htsa-enrollment-cj-clay.html  
**Archives:** `/archive/prospect-versions/close-page/`

| Ver | Commit | What changed |
|---|---|---|
| V1 | `6609d07` | First close template saved |
| V2 | `ae94391` | Guarantee-ready template + close-page rule |
| V3 | `e781d3d` | After-pay next steps for solo closes |
| V4 | `439e165` | Hide next steps until checkout |
| V5 | `b583eba` | Game plan first, pricing last in dropdown |
| V6 | `c4d7b6c` | Amy-style 2-way enroll steps; remove “what we need from you” |
| V7 | `558c1dc` | Reorder getting → HTSA needs → pricing → next steps (**felt like overreach / iframe issue**) |

Open a version:  
https://closewithcjclay.com/archive/prospect-versions/close-page/close-page-v5.html  
(swap `v5` for `v1`…`v7`)

**Legacy long invoices** (`htsa-enrollment-*.html` Terms-gate, ~10k px) are a **separate system**. Not the short close page. Frozen shells live in `templates/htsa-placement-01`…`06`.

---

## 4. 30 day action plan / game plan

**Live:** https://closewithcjclay.com/30-day-roadmap.html  
**Also on disk:** `30-day-roadmap-v2.html` (older sibling file)  
**Archives:** `/archive/prospect-versions/roadmap-30/`

| Ver | Commit | What changed |
|---|---|---|
| V1 | `0c46895` | Moved to root, generalized |
| V2 | `7c73882` | Post-placement = 90-day ramp |
| V3 | `0eabb29` | Expandable dropdown sections |
| V4 | `c4d7b6c` | Removed “Bet on yourself” mid-page |
| V5 | `558c1dc` | Standout Outcome box; removed “Your side of it” |

Setter twin: https://closewithcjclay.com/24-day-roadmap.html

---

## 5. Referral / meet-CJ preview card

**Live:** https://closewithcjclay.com/meet-cj.html  
**Archives:** `/archive/prospect-versions/meet-cj/`

| Ver | Commit | What changed |
|---|---|---|
| V1 | `134491f` | First referral landing |
| V2 | `0634592` | Visible Meet Chad + Website + Taylor, Trustpilot, book, more stories |
| V3 | `0def31f` | Aligned cards, smaller book banner, cleaned More resources |

---

## 6. Pre-call resource pages

**Template:** `r/_TEMPLATE-precall.html`  
**People:** `r/<first>_<last>/` e.g. Gracie https://closewithcjclay.com/r/gracie_brooks/  
**Archives:** `/archive/prospect-versions/precall/`

| Ver | Commit | What changed |
|---|---|---|
| V1 | `4620d30` | Reusable template + assets + rule |
| V2 | `e8f5c37` | Booked default fixed (critical), page map rule |
| V3 | `98798de` | Visible Taylor + Brianna + resources dropdown |

Named pages (product variants, not every name): Lynda-style resources, Gracie (DIY groups framing + Book Appointment), etc.

---

## 7. Offer booking pages (pre-call, still need a slot)

**Live shared:** https://closewithcjclay.com/special-offer-book-with-cj.html  
**Named:** `*-and-cj.html`  
**Internal drafts:** `reactivation/book-with-cj.html`, `v2`, `v3` (folder is internal; never say “reactivation” to prospects)  
**Archives:** `/archive/prospect-versions/offer-booking/`

| Ver | Commit | What changed |
|---|---|---|
| V1 | `19b847a` | First booking page |
| V2 | `629b44a` | Hero = 10 upcoming spots |
| V3 | `ea2f892` | Hero = earning a spot |
| V4 | `5b4d852` | HubSpot `/charles660/cj` |

---

## 8. Also in this repo (ops / internal, not prospect send)

| Item | Path | Notes |
|---|---|---|
| God script v5 | `private/htsa-god-script-v5.html` | Internal. Also root `htsa-god-script.html` |
| Claude fence / handoffs | `docs/CLAUDE_CODE_HARD_FENCE.md`, `docs/SPECIAL-OFFER-SELF-ENROLL-HANDOFF-FOR-CLAUDE.md`, `docs/PASTE_THIS_PROMPT_TO_CLAUDE.md` | Sandbox instructions |
| Invoice InstantQuote workspace | sibling repo `HTSA Invoice` | Separate from closewithcjclay Pages |

---

## What is NOT in this closewithcjclay.com repo

Pulled from your Downloads transcript + Documents scan. These live **elsewhere**. Cursor in this chat does not own their version history unless you bring them in.

| Thing | Where it actually lives | Notes |
|---|---|---|
| Claude special-offer V7–V9 working files | `Documents/SPECIAL-OFFER-CLAUDE-SANDBOX/WORK/` | Now mirrored into archive previews above |
| Claude enrollment transcript (to v9) | `Downloads/Claud-Code (Enrollment Page) Full Transcript (Up to v9) .txt` | Conversation log, not a page |
| Live Call Lab | `Documents/HTSA_LIVE_CALL_LAB/` | On-call / Cursor / Claude / Codex / Genspark / NotebookLM lanes |
| Co-Pilot v3 for Claude | `Documents/CJ-CO-PILOT-V3-FOR-CLAUDE/` | Product brain, not prospect pages |
| Live AI Co-Pilot product folder | inside Co-Pilot workspace `06_LIVE_AI_COPILOT_PRODUCT` | Different product |
| Co-Pilot audits / briefs / zips | `Documents/` (many `.pages`, `.zip`, `COPILOT_*`) | Chat exports |
| Home Co-Pilot folders | `~/HTSA CO-PILOT`, `~/CLAUDE CO-PILOT`, `~/CJ_AI_OS`, `~/COPILOT:GENSPSRK` | Outside this site |
| God script originals / copies | `Documents/HTSA_GOD_SCRIPT_V5.html` + repo `private/` | Prefer one canonical copy |
| Continuous Improvement calls | `Documents/Continuous Improvement - HTSA Calls.*` | Process docs |
| HTSA Invoice app | `~/HTSA Invoice` | Quoting / invoices product |
| Older long enrollment invoices | many `htsa-enrollment-*.html` on live site | Legacy Terms-gate system; not short close template versions |
| Private Claude artifact preview URLs | claude.ai/code/artifact/… | Expire / not durable; use sandbox files instead |

**If another chat built “Live Console” or “Live Co-Pilot” UI pages for the site, they are not under this repo’s git history as prospect send pages.** Bring that chat’s folder or URLs if you want them indexed the same way.

---

## Recommended next moves (only if you ask)

1. Push this archive set so all `/archive/...` and history URLs go live on GitHub Pages.
2. Decide special-offer direction: stay on **V6B live**, roll toward **Claude V7** (liked), or rebuild from V6/V7 without V9.
3. Optionally snapshot close-page **V5** or **V6** as your “trusted before overreach” restore point.

---

*Generated for CJ · archives under `archive/prospect-versions/` · Notion-ready markdown: this file.*
