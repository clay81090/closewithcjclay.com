# HANDOFF FOR CLAUDE (Copilot / Claude v3) — Special offer self-enroll page

**Date written:** Sept 3, 2026  
**Author context:** Cursor agent (Composer) just over-edited `special-offer.html` while CJ needed a hurry-up self-enroll blast. CJ wants Claude to rebuild this **better and simpler**, using what already worked.  
**Repo root:** `/Users/charlesclay/Desktop/closewithcjclay.com/closewithcjclay.com`  
**Live site:** `https://closewithcjclay.com` (GitHub Pages from `main`)

**Paste this whole file into Claude.** Then open the paths in section 8 before writing code.

---

## 0. What CJ needs RIGHT NOW (the job)

CJ cannot phone everyone in the reactivation batch before **Thursday, Sept 4, 2026** (special offer deadline). He needs **one shareable link** people can:

1. Understand the special offer and deadline  
2. See the 30-day path (goal, not obligation)  
3. Pick payment ($5k PIF / $1,750 × 3 / ClarityPay $500/mo → $6k)  
4. Either **call CJ live** OR **self-enroll** with the proven 5-step post-pay checklist  
5. Not get confused by a second “enrollment page” email later — **THIS page is it**

North star from CJ: **February-style self-enroll worked.** Karissa Rodriguez, David Fielder, Amy Grochala (and others) enrolled alone off a clear page. Recent Cursor passes overcomplicated `special-offer.html`. Prefer **restore clarity** over inventing new layout systems.

Tone: honest, warm, not mean. No “High Ticket” in the closing quote about time passing. People were hand-selected for the discount. Do not invent “4 spots left” unless CJ asks. Internal word **reactivation** must never appear in URLs, titles, or prospect-facing copy.

---

## 1. Page map (do not mix these)

Canonical rule: `.cursor/rules/htsa-page-map.mdc`

| CJ says | What it is | Path pattern |
|---|---|---|
| **offer link** | Booking page for people who have NOT booked | `<firstname>-and-cj.html` or `special-offer-book-with-cj.html` |
| **pre call link** | Already booked; warm-up resources | `r/<first>_<last>/index.html` |
| **enroll link / close page** | On the phone, verbal yes → short confirm + pay | `htsa-enrollment-<first>-<last>.html` from `templates/_TEMPLATE-close.html` |
| **game plan** | Shared 30-day / 24-day roadmap | `30-day-roadmap.html`, `24-day-roadmap.html` |
| **special offer (self-serve blast)** | ONE shared page for the Sept 4 discount cohort | **`special-offer.html`** ← the problem file |
| **meet-cj** | Referral landing + OG preview card | `meet-cj.html` + `og-meet-cj.jpg` |
| **legacy long invoice** | Old long enrollment (~10k px, Terms gate, Member Voices) | `htsa-enrollment-*.html` from frozen `templates/htsa-placement-0X-*.html` |

**Before Aug 20 / early era:** long invoices were the main enroll instrument. Self-enrollers used those long pages (or early short variants) with clear payment + “what happens next.”

**After ~Aug 20–Sept 1:** system split into four page types + short close template + pre-call template + shared roadmaps. Reactivation campaign added booking pages under internal `reactivation/` and public `special-offer-book-with-cj.html`.

**Sept 3, 2026:** Cursor built `special-offer.html` as a self-serve wrap of offer + plan + pricing. Multiple redesign passes in one evening. CJ says it went backwards.

---

## 2. Pricing that MUST be on the self-enroll special offer

From `templates/HTSA-SECONDARY-PAYMENT-OPTIONS.md` and `OFFERS.reactivation` in close template:

| Option | Amount | Whop checkout |
|---|---|---|
| PIF | $5,000 | `https://whop.com/checkout/plan_gdThsrGLXqaDF?d2c=true` |
| 3-pay | 3 × $1,750 = $5,250 | `https://whop.com/checkout/plan_YrqGOXMxGbOVa?d2c=true` |
| ClarityPay | $500/mo × 12 = $6,000 | `https://whop.com/checkout/plan_VUSDju20gTBCg/` |

Do **not** use standard closer 4-pay `plan_m6yk0QLbxWaak` or standard ClarityPay `$600/mo / $7,200` (`…/1ba2LjGOo3B1Wpp4jf-eF61-w5X4-yCzD-25zhqI3VcVLf/`) on this page.

Deadline copy: **Thursday, Sept 4** then standard pricing.

---

## 3. How start options MUST work (CJ corrected this tonight)

**Option A — only this:** Call or text CJ. Do enrollment **live** together. Stay on the phone, narrate the tap, do not go quiet at Whop.

**Option B — exactly this accordion** (already proven on short close pages; screenshot CJ attached matches Jayden / Amy Schleper style):

**Summary line:** `Doing this on your own? Here's exactly what happens next`

1. **Text CJ, Payment made** → SMS `(616) 612-1735` body `Payment made`  
2. **Two emails hit inbox** — Welcome (modules, Zoom Tues 12 PM EST / Wed 5 PM EST) + Login (temp password)  
3. **Nothing after 10 minutes?** Spam check, text CJ. Do not re-pay. Do not create second account.  
4. **Book kickoff with Mark** → `https://meetings.hubspot.com/chad-aleo/member-success-team-kickoff-call`  
5. **Join Mastermind** → Facebook group request `https://www.facebook.com/groups/1039656943556821` (680+ members wording)

Reference HTML to copy verbatim for Option B markup:

- `htsa-enrollment-jayden-lepper.html` (search `Doing this on your own`)
- Also present on: `htsa-enrollment-amy-schleper.html`, `htsa-enrollment-karissa-rodriguez-short.html`, many short closes

**Wrong:** telling them CJ will “send another enrollment page” after they text. **This page is the enrollment page.**

**Wrong (what Composer did mid-page):** inventing a shortened 4-bullet Option B that dropped email boxes, spam step, and Mastermind.

Minimal fix already applied on live `special-offer.html` (build stamp `special-offer-build:1788481000`): Option A = call/text live; Option B = full 5-step `<details class="next-wrap">`. Claude may still redesign the rest of the page, but **do not break Option B again.**

---

## 4. What worked for self-enroll (February / early long invoices)

CJ named these as people who enrolled **on their own**:

| Person | File (still in repo) | Style |
|---|---|---|
| Karissa Rodriguez | `htsa-enrollment-karissa-rodriguez.html` (~1632 lines, long invoice) + `htsa-enrollment-karissa-rodriguez-short.html` | Setter / long then short |
| David Fielder | `htsa-enrollment-david-fielder.html` (~1674 lines) | Closer long invoice |
| Amy Grochala | `htsa-enrollment-amy-grochala.html` (~1637 lines) | Closer long invoice |

**Why it worked (CJ’s words):** clear, not overcomplicated. Payment links + what happens after pay. People finished alone.

**Lesson for Claude:** self-enroll pages win on **procedure clarity**, not on stacking every marketing section. Prefer one scroll path: why / plan / pay / what happens next. Collapse extras.

Also useful long-invoice pattern for Terms gate + Member Voices (if you need reviews): `htsa-enrollment-joseph-golen.html` (Janaye “To CJ” personal review CJ loves).

---

## 5. Timeline of systems (so Claude does not “fix” the wrong era)

### Era A — Pre Aug 20, 2026 (approx)

- Primary enroll = **long** `htsa-enrollment-*.html` from placement shells / Amy-aligned templates  
- Rules: `.cursor/rules/htsa-enrollment-invoice-workflow.mdc`  
- Skill: `.cursor/skills/htsa-enrollment-invoice/SKILL.md`  
- Terms gate above locked pay zone; orange performance guarantee; Member Voices strip  
- Self-enrollers used these pages successfully (Feb cohort and later)

### Era B — Late Aug 2026 (page system rebuild)

- Short **close page** template: `templates/_TEMPLATE-close.html`  
- Rule: `.cursor/rules/htsa-close-page.mdc` (takes priority when CJ says “close page”)  
- Pre-call: `r/_TEMPLATE-precall.html` + `.cursor/rules/htsa-precall-page.mdc`  
- Roadmaps moved to root: `30-day-roadmap.html` (closer), later `24-day-roadmap.html` (setter)  
- Referral landing: `meet-cj.html` + OG `og-meet-cj.jpg` (“Someone put your name forward”)  
- Page map rule added after booked vs book bugs: `.cursor/rules/htsa-page-map.mdc`  
- Reactivation outreach materials (internal, not prospect URLs):  
  - Repo: `reactivation/book-with-cj.html`, `book-with-cj-v2.html`, `book-with-cj-v3.html`  
  - CJ’s OS / Downloads (outside this repo, CJ may attach):  
    - `~/CJ_AI_OS/03_REVENUE_ENGINE/06_Show_Rate_And_JustCall_Messaging/reactivation/`  
    - `~/Downloads/Reactivation Campaign - HTSA/` (SOP v1–v3, responses PDF, frameworks PDF)

### Era C — Early Sept 2026 (close page UX experiments)

- Walk-first layout: game plan iframe first, pricing in dropdown (`b583eba`, Martina / Maria J style)  
- Short closes with reactivation pricing for named people (Diego Quintero, Jay Webb, Martina Evans, Astrid Thomas, Maria J, Anabel Villa, etc.)  
- Flexxbuy tips added on some personal pages (not required on shared blast unless CJ asks)

### Era D — Sept 3 night (Composer on `special-offer.html`) — WHAT WENT WRONG

Git commits on `special-offer.html`:

1. `758910e` — First shared special-offer: deadline, intro, start card, roadmap **iframe**, pricing dropdown, start steps  
2. `a29aec1` — Big rewrite: killed iframe, **inline 4 phase cards**, giant Member Voices grid, Terms gold card, CJ quote, standalone CJ card outside footer, claimed “THIS IS IT”  
3. `70a10cb` — Shrink reviews to Janaye strip; remove duplicate “What you’re getting” list; green Terms button; compact referral form + OG thumb; CJ card back **inside** footer right  
4. Tonight (after 70a10cb) — Option A/B corrected to call-live vs full 5-step accordion (build `1788481000`)

**CJ’s feedback that still applies:**

- Do not say you will send another enrollment page  
- Footer quote: if nothing changed since last talk, it will not change by 2027… begin remote sales career (warm, no “High Ticket” in that sentence)  
- Reviews: one simple horizontal Janaye (or move), **not** a huge grid  
- Referral: keep the **text/form** that opens SMS with meet-cj preview link + **$250 first 3 / $500 after** — compact, near footer, not half the page  
- Terms: highlighted; no ugly black buttons (navy/green brand)  
- “What’s in the program” belongs in the modal/tab next to Terms, not duplicated as a giant checklist under Terms  
- Stop changing ten things when CJ asked for one  

---

## 6. Current live file state (as of this handoff)

**File:** `special-offer.html`  
**URL:** `https://closewithcjclay.com/special-offer.html`  
**Optional personalization:** `?n=Firstname` greets in intro  

Rough section order now:

1. Top / deadline / CJ intro (hand-selected, Sept 4)  
2. Part 1 — inline 30-day phase cards (NOT the full roadmap iframe)  
3. Part 2 — What we need from you  
4. Compact Janaye voice strip  
5. Part 3 — Option A call/text live; Option B = 5-step next-wrap accordion  
6. Part 4 — reactivation pricing + guarantee  
7. Part 5 — Terms card + curriculum modal  
8. Compact referral form (tiers + fields + `og-meet-cj.jpg` thumb + SMS)  
9. CJ quote band  
10. Footer: HTSA left, **CJ business card right** (enrollment-page pattern)

JS still wires Whop choose → confirm sheet → terms agree → `recordTermsAgreement` + checkout. Referral posts `recordReferral` to Apps Script. Build stamp comment: `special-offer-build:…`

**Known tension:** page is long/continuous because Composer replaced the roadmap iframe with inline phases + many Parts. CJ liked scrolling sections but hated duplication and vertical bloat. Claude should decide whether to:

- Go back toward **first good version** (`758910e` spirit: iframe roadmap + short start + pricing), **or**  
- Keep inline plan but much tighter, **or**  
- Hybrid: short phase summary + link/iframe to `30-day-roadmap.html`

CJ’s stated preference tonight: **hurry**, get self-enroll working like February, stop thrashing.

---

## 7. What Claude should build (recommended brief)

Treat this as a **CEO approval** page, not a playground.

**Must keep**

- Reactivation checkouts and Sept 4 deadline  
- Option A = live call/text only  
- Option B = exact 5-step accordion (copy from Jayden)  
- One enroll URL; never promise a second page  
- Confirm sheet + Terms agreement before Whop  
- Footer CJ card on the **right inside** dark footer  
- Referral SMS + meet-cj OG preview near bottom, compact, $250/$500  
- Brand: navy `#0a1628`, green `#00c97a` / `#61e38b`, gold sparingly for Terms  

**Should cut or collapse**

- Giant review grids  
- Duplicate program include lists  
- Anything that feels like a second “what we need” section  
- Over-long Part headers if they inflate height  

**Should study before redesigning**

1. First commit version of special-offer if needed: `git show 758910e:special-offer.html`  
2. Proven self-enroll long pages: Karissa / David Fielder / Amy Grochala  
3. Proven short close Option B: Jayden lepper next-wrap  
4. Close template: `templates/_TEMPLATE-close.html`  
5. Roadmap asks + referral: `30-day-roadmap.html` (referral JS + tiers)  
6. Meet card: `meet-cj.html` + `og-meet-cj.jpg`  

**Do not**

- Edit live named client enrollment pages unless CJ names them  
- Put “reactivation” in prospect-facing copy  
- Put real prospect phones in test/examples (use `+15555550100`)  
- Force-push or rewrite git history  
- Reintroduce “I’ll send your enrollment page”  

---

## 8. Paths Claude must open (checklist)

### Rules (read first)

- `.cursor/rules/htsa-page-map.mdc`  
- `.cursor/rules/htsa-close-page.mdc`  
- `.cursor/rules/htsa-precall-page.mdc`  
- `.cursor/rules/htsa-enrollment-invoice-workflow.mdc`  
- `.cursor/rules/no-dashes-in-client-copy.mdc`  
- `.cursor/rules/htsa-phone-test-number.mdc`  
- `.cursor/HANDOFF.md` (older deal handoff; different task, but system context)

### Templates & pricing

- `templates/_TEMPLATE-close.html`  
- `r/_TEMPLATE-precall.html`  
- `templates/HTSA-SECONDARY-PAYMENT-OPTIONS.md`  
- `templates/HTSA-ENROLLMENT-PLACEMENT-NOTES.md`  
- `templates/htsa-placement-01-closer-cash-only.html` … `06-…` (frozen long shells)

### The contested page + references

- `special-offer.html` ← current live blast page  
- `special-offer-book-with-cj.html` ← booking/offer page (different job: pick a time)  
- `htsa-enrollment-jayden-lepper.html` ← Option B accordion source of truth  
- `htsa-enrollment-karissa-rodriguez.html`  
- `htsa-enrollment-david-fielder.html`  
- `htsa-enrollment-amy-grochala.html`  
- `htsa-enrollment-joseph-golen.html` ← Janaye review markup  
- `30-day-roadmap.html` / `24-day-roadmap.html`  
- `meet-cj.html` / `og-meet-cj.jpg` / `cj-headshot-600.png`

### Scripts (if shipping named closes again)

- `scripts/htsa-paste-close.py`  
- `scripts/htsa-send-pack.py`  
- `scripts/htsa-instantiate-close.py`  
- `scripts/htsa-paste-invoice.py` / `htsa-instantiate-invoice.py`  
- `scripts/precall-resource.py`

### Internal reactivation (not public URLs)

- `reactivation/book-with-cj-v3.html` (and v1/v2)  
- Outside repo (CJ may attach):  
  - `~/Downloads/Reactivation Campaign - HTSA/reactivation-campaign-sop-v3.md`  
  - `~/Downloads/Reactivation Campaign - HTSA/REACTIVATION CAMPAIGN - RESPONSES (8:26).pdf`  
  - `~/CJ_AI_OS/03_REVENUE_ENGINE/06_Show_Rate_And_JustCall_Messaging/reactivation/REACTIVATION_TRANSCRIPT_INVENTORY.md`

### Tracking endpoint (do not break)

- Apps Script: `https://script.google.com/macros/s/AKfycbxeyf0Q_wiM-d6pq5DnBNKUDVTvMvzFwD60DPpjMEm60LnIQ2tjSkGmy5u1Gt5sQa4Jng/exec`  
- Terms version: `HTSA-TOS-PDF-closewithcjclay-2026-04`  
- Terms PDF: `https://closewithcjclay.com/HTSA-Terms-of-Service.pdf`

---

## 9. Suggested Claude working order

1. Read this file + `htsa-page-map.mdc`  
2. Open `git show 758910e:special-offer.html` and current `special-offer.html` side by side  
3. Open Jayden Option B block; confirm Option A/B contract  
4. Open one February-era self-enroll page (Amy Grochala or David Fielder) and note what made solo checkout obvious  
5. Propose a **short written structure** (max 8 sections) for CJ approval in 5 bullets — then implement **one** coherent page  
6. Ship: commit `special-offer.html` only, push `main`, poll until build stamp live, give CJ the URL  
7. Also give CJ paste-ready TEXT + EMAIL (black on white HTML, no em dashes) pointing at **one** enroll link  

---

## 10. Paste-ready prompt CJ can send Claude

```
Read docs/SPECIAL-OFFER-SELF-ENROLL-HANDOFF-FOR-CLAUDE.md end to end.
Open every path in section 8 that you need.

Job: rebuild special-offer.html so reactivation people can self-enroll tonight
before Sept 4, as cleanly as February (Karissa, David Fielder, Amy Grochala).

Hard constraints:
- Option A = call/text CJ and enroll live only
- Option B = exact 5-step "Doing this on your own" accordion from Jayden
- This page IS the enrollment page (never say you'll send another)
- Pricing = reactivation Whop links only ($5k / 3x1750 / Clarity $500)
- Keep footer CJ card inside footer on the right
- Keep compact referral SMS + meet-cj preview near bottom
- Do not thrash. Prefer simplicity over new UI systems.
- Show me a 5-bullet structure first, then ship one file.
```

---

## 11. Honest note to Claude about the prior agent

Cursor Composer made large multi-section redesigns when CJ asked for small fixes. That burned tokens and confidence. Prefer **surgical diffs**, match existing proven blocks, and ask one clarifying question only when page type is ambiguous.

CJ is mid-campaign and needs the self-enroll path working **now**.

---

*End of handoff.*
