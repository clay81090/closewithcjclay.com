# HTSA Agent Handoff — Precall + Enrollment (CJ Clay)

**Who this is for:** A new Cursor chat continuing CJ’s daily work on **closewithcjclay.com**.  
**Repo (canonical git root):** `/Users/charlesclay/Desktop/closewithcjclay.com/closewithcjclay.com`  
**Live site:** `https://closewithcjclay.com/` (GitHub Pages from `main` on `clay81090/closewithcjclay.com`)  
**CJ:** Charles “CJ” Clay · (616) 612-1735 · cj@highticketsalesacademy.com  

**Read these first (authoritative):**
1. `.cursor/rules/htsa-enrollment-invoice-workflow.mdc`
2. `.cursor/skills/htsa-enrollment-invoice/SKILL.md`
3. `.cursor/rules/no-dashes-in-client-copy.mdc` (client texts/emails: **no em/en dashes**)
4. `templates/HTSA-ENROLLMENT-PLACEMENT-NOTES.md`
5. `templates/HTSA-SECONDARY-PAYMENT-OPTIONS.md` (only when CJ asks for secondary Whop plans)

**Terminal shortcut for enrollments:** `htsa` (loaded from `~/.htsa-shell/htsa.zsh` via `~/.zshrc`). Repo path inside that function: `$HOME/Desktop/closewithcjclay.com/closewithcjclay.com`.

---

## Non-negotiable operating rules (CJ)

1. **Always ship.** Every precall page and every enrollment invoice must be **git add → commit → push to `origin/main`** without CJ asking. Wait for **`READY`** (HTTP 200) before giving CJ the link. Never hand over a URL that 404s.
2. **Always mobile + web.** Layout must work on phone and desktop. Use existing CSS patterns (`@media (max-width: 600px)`, `playsinline` on video, full-width buttons on mobile).
3. **Always return a clickable absolute URL** in the reply, plus paste-ready **text** (and **email** when CJ wants both). Prefer **text-only** when CJ says “text only” or “same text only no email.”
4. **Never invent Whop plan IDs.** Copy URLs from frozen shells or `HTSA-SECONDARY-PAYMENT-OPTIONS.md`.
5. **Never edit an existing client’s deployed HTML to create a new person.** `cp` / instantiate / `precall-resource.py create` only.
6. **URL typo guard:** enrollment paths are **`htsa-enrollment-`** (with **a**). Pattern **`hts-enrollment-`** (no **a**) 404s except intentional redirect stubs. Prefer **one** canonical enrollment URL (no `?1` in what CJ sends).
7. **Client copy:** no em dashes (—), en dashes (–), or dash bullet lists in texts/emails. Commas, periods, short sentences. Amounts like `$6,000` and `×` are fine.

---

## Two products (do not confuse them)

| | **Precall resource page** | **Enrollment invoice** |
|---|---|---|
| **When** | Before the discovery call | After the call (they’re ready to enroll) |
| **URL shape** | `https://closewithcjclay.com/r/{first_last}/` | `https://closewithcjclay.com/htsa-enrollment-{slug}.html` |
| **Has pricing?** | **No** (resources only) | **Yes** (Whop / ClarityPay / etc.) |
| **Has curriculum / Terms gate?** | **No** curriculum, no Terms gate, no Whop | **Yes** full invoice + Terms gate + locked pay zone |
| **Script** | `python3 scripts/precall-resource.py create … --ship` | `python3 scripts/htsa-paste-invoice.py` / `htsa-instantiate-invoice.py … --overwrite --ship` or Terminal `htsa` |
| **Template / reference** | Match live practice: **`https://closewithcjclay.com/r/cj_clay/`** | Frozen shells `templates/htsa-placement-01` … `06` |
| **Copy after READY** | Short precall text (MUST WATCH tip). Email only if asked. | Longer enrollment text **and** email (unless “text only”) |

---

## A) Precall resource pages (before the call)

### What CJ pastes (complete work order)

```text
Full Name
Email: person@example.com
Phone Number: +1 (555) 123-4567
Appointment: Thursday August 20 at 10am EST
```

Optional: “text only”, “Zoom”, “Phone or Zoom”, day/date/time/timezone.

### Agent must do (no quiz)

1. Parse name, email, phone → display + E.164 (`+1…`).
2. Slug = `first_last` lowercase underscores (`mario_enoch`).
3. Run from **Desktop repo root**:

```bash
python3 scripts/precall-resource.py create \
  --full-name "Mario Enoch" \
  --email "marioenoch@yahoo.com" \
  --phone-e164 "+13366844385" \
  --phone-display "+1 (336) 684-4385" \
  --call-day "Thursday" \
  --call-date "Aug 20" \
  --call-time "10:00 AM" \
  --timezone "EST" \
  --call-format "Phone or Zoom" \
  --ship
```

4. Wait until stdout shows **`READY`** and the URL.
5. Reply with the **clickable** URL + paste-ready text.

### MUST WATCH video (critical)

- **Embedded in-page** under **Section 1 — Who Mentors You**, **above** Chad’s Meet Chad link / book / Trustpilot.
- Bright orange/red badge: **`MUST WATCH!!!`**
- Plays on the page (no new tab). `controls` + `playsinline`. Works on **phone and web**.
- Wired in `scripts/precall-resource.py`:
  - `WEEK_AT_HTSA_VIDEO = "/media/this-week-at-htsa-2026-08-18.mp4"`
  - `render_week_at_htsa_embed()` → used inside `render_about_htsa()`
- Styles live in `resource-links/assets/enrollment-styles.css` (`.htsa-proof-embed*`).
- **Current published file:** `media/this-week-at-htsa-2026-08-18.mp4`  
  Source on disk often named: `HTSA - Placement This Week (Aug 18th, 2026).mp4` (~**4:07**, ~35MB).  
  **Do not** use the old ~60MB full “This Week at HTSA” dump.
- **If CJ uploads a new MUST WATCH clip:** copy it over `media/this-week-at-htsa-2026-08-18.mp4` (or update the constant + filename), rebuild practice `/r/cj_clay/` if needed, commit + push the media + script/CSS, then new precalls pick it up automatically. GitHub warns above 50MB; keep clips short when possible.
- **Existing** precall pages do **not** auto-update unless rebuilt. New pages from the script get the current embed.

### Practice / gold reference

- Precall: `https://closewithcjclay.com/r/cj_clay/`
- Enrollment sandbox (pricing experiments): `htsa-enrollment-cj-clay.html` — **never** paste practice simulated-payment UI onto real clients.

### Precall page contents (standing template)

- Header, hero letter, call card + **Confirm I’ll be there**
- Billing Prepared For / By
- §1 Who Mentors You: **MUST WATCH video → Chad → book banner → Trustpilot**
- §2 Videos, Proof & Member Stories (featured + placement Canva cards + compact YouTube + HTSA site card)
- CJ personal reviews strip
- Footer (2026 style)
- **Forbidden:** curriculum grid, Whop checkout, Terms gate, pricing, email gate, “Need to reschedule,” calendar buttons (see `assert_clean` in `precall-resource.py`)

### Precall text pattern (default; no dashes)

```text
Hey {First}, looking forward to our call {day} at {time} {tz}. Here’s everything I want you to look at before we talk:

https://closewithcjclay.com/r/{slug}/

Start with the MUST WATCH video at the top. It’s about 4 minutes. Then glance at the rest if you have time. See you {tomorrow / soon}.
```

Adjust Zoom vs phone from the appointment line. **Text only** when CJ says so.

### Recent precall examples (Aug 19–20, 2026)

| Person | URL | Call |
|--------|-----|------|
| CJ Clay (practice) | `/r/cj_clay/` | practice |
| Mario Enoch | `/r/mario_enoch/` | Thu Aug 20 10:00 AM EST |
| Joe Goldstone | `/r/joe_goldstone/` | Thu Aug 20 3:00 PM EST Zoom |
| Briana Brewer | `/r/briana_brewer/` | Thu Aug 20 5:00 PM EST |

Data JSON: `resource-links/data/{prospect-id}.json` · registry: `resource-links/registry.json` · `r/_manifest.json`

---

## B) Enrollment invoices (after the call)

### What CJ pastes (complete work order)

```text
Full Name

Email: client@example.com

Phone Number: +1 (555) 123-4567

Closer - Cash only
```

Or: Closer / Setter / Closer & Setter + Cash / Financing / Both + optional pricing overrides.

### Mapping → frozen shells

| CJ says | ID | Template |
|---------|----|----------|
| Closer – Cash only | `01` | `templates/htsa-placement-01-closer-cash-only.html` |
| Closer – Cash + Financing | `02` | `templates/htsa-placement-02-closer-cash-financing.html` |
| Setter – Cash only | `03` | `templates/htsa-placement-03-setter-cash-only.html` |
| Setter – Cash + Financing | `04` | `templates/htsa-placement-04-setter-cash-financing.html` |
| Closer & Setter – Cash only | `05` | `templates/htsa-placement-05-closer-setter-cash-only.html` |
| Closer & Setter – Cash + Financing | `06` | `templates/htsa-placement-06-closer-setter-cash-financing.html` |

### Defaults (unless CJ overrides)

**Closer cash (`01`, dual closer stack in `05`):**
- Option 1: **$6,000** PIF  
- Option 2: Splitit **$550/mo × 12** ($6,600) — dedicated Whop checkout  
- Option 3: **$1,750 × 4** ($7,000)  
- Orange performance guarantee **ON**  
- Kickoff Step 3: **Mark** (HubSpot member-success kickoff) unless CJ says Chris  

**Closer cash + financing (`02`, dual closer in `06`):**
- **$6k PIF** + **$1,750 × 4** + **ClarityPay only** ($600/mo × 12, 0% APR, $7,200, 620+)  
- ClarityPay Whop: `https://whop.com/checkout/1ba2LjGOo3B1Wpp4jf-eF61-w5X4-yCzD-25zhqI3VcVLf/`  
- **No Flexxbuy** on Closer financing unless CJ asks  
- **No Splitit** on `02` financing stack (per current frozen-shell / workflow notes — follow placement shell)  

**Setter cash (`03`):**
- **$3,000** PIF · **$1,050 × 3** ($3,150)  
- Header/billing Payment line: short **Select payment option below**  

**Setter cash + financing (`04`):**
- Whop cash/plans + ClarityPay **$3,600** (`plan_z5iuUhSgm9seH?d2c=true`) + Flexxbuy  
- **Never** put Setter ClarityPay on Closer pages (or vice versa)

**Secondary Whop** (Action Taker 2-pay `plan_oMi6XYvybZY4F`, $5k PIF, etc.): only if CJ explicitly asks. See `templates/HTSA-SECONDARY-PAYMENT-OPTIONS.md`.

### Program Investment order (fixed)

1. Program Investment heading  
2. Orange guarantee (unless “no guarantee”)  
3. Terms gate (`#hts-terms-agreement-panel`) → PDF + clarifications + checkbox + **Record agreement & unlock payments**  
4. Locked `#invest-pay-zone` with **all** pay/finance buttons  

Terms endpoint + `termsVersion` + payload fields: see workflow rule. Unique `data-*` + `sessionStorage` key `hts_terms_gate_{first}_{last}_v1`.

### Member Voices (default)

Joseph / CJ trial layout: centered **Member voices** banner; Janaye first; blue personal cards (`ref-strip-quote--personal`, **To CJ**); white HTSA member cards. Synced from `htsa-enrollment-joseph-golen.html` via instantiate/build scripts.

### Enrollment ship flow

```bash
# Preferred paste path
python3 scripts/htsa-paste-invoice.py   # stdin = paste block, Ctrl-D; default --ship

# Or instantiate
python3 scripts/htsa-instantiate-invoice.py 02 \
  --full-name "…" --email "…" --phone-e164 "…" --phone-display "…" \
  --overwrite --ship
```

Poll: `sh scripts/check-enrollment-live.sh {slug}`  
Only return URL after **`READY`**.

### Enrollment copy

- **Different** from precall: longer, enrollment-focused, link to **`htsa-enrollment-{slug}.html`**, mention Terms + payment options + next steps.  
- Template seed: `templates/HTSA-ENROLLMENT-EMAIL-TEMPLATE.txt`  
- Still: **no dashes** in client-facing prose.

### Enrollment video (optional / case-by-case)

Alejandro’s closer invoice also embeds the MUST WATCH clip under Live Group Coaching with canonical-URL + one-time stale cache reload. **Do not** bulk-add to every old invoice unless CJ asks. New enrollments: add when CJ wants the same proof on the post-call page.

**Alejandro note:** Only send  
`https://closewithcjclay.com/htsa-enrollment-alejandro-ospina.html`  
(no `?1`, no `hts-enrollment-` typo). Pricing: $6k / $1,750 4-pay / ClarityPay $600. Medical note stays. Contact: ospinaland@gmail.com · +1 (561) 657-9297.

---

## C) Always commit + push (history)

For **this workstream**, treat ship as part of “done”:

- Precall: `precall-resource.py --ship` already commits listed paths and pushes.  
- Enrollment: instantiate/paste `--ship` does the same.  
- Manual edits: `git add` only the relevant HTML/media/script, commit with a clear message, `git push origin main`, then poll until live.  
- Do **not** leave finished client pages only on the laptop.  
- Do **not** bulk-commit unrelated dirty files (`.DS_Store`, emptied files, other clients’ invoices).  
- **HTSA Invoice** folder (`/Users/charlesclay/HTSA Invoice`) is a **different** repo; ignore `.DS_Store` noise there unless CJ is working that project.

**Conflict note:** Global Cursor “only commit when asked” yields to CJ’s HTSA rule: **ship enrollments and precalls always**.

---

## D) Repo / folder gotchas

- **Use the Desktop nested git repo** for all ships:  
  `/Users/charlesclay/Desktop/closewithcjclay.com/closewithcjclay.com`  
- There is also `/Users/charlesclay/closewithcjclay.com/` (Home copy / uploads). Videos often land there first; **copy into Desktop repo `media/`** before push.  
- `~/.htsa-shell/htsa.zsh` points at the Desktop path. New Terminal tabs needed if `htsa` is “command not found.”  
- GitHub Pages can take 1–5 minutes after push; always wait for **READY**.

---

## E) Quick decision tree for the new agent

```
CJ pastes name + email + phone + appointment / “precall”
  → precall-resource.py create --ship
  → return /r/{slug}/ + text (email only if asked)

CJ pastes name + email + phone + Closer/Setter + Cash/Financing/Both
  → paste/instantiate --overwrite --ship
  → return htsa-enrollment-{slug}.html + enrollment text (+ email unless text-only)

CJ says “like cj_clay” / “precall resources”
  → precall, not enrollment

CJ says “enrollment” / “after the call” / pricing numbers
  → enrollment invoice

CJ uploads a new Must Watch mp4
  → replace media file, push, confirm /r/cj_clay/ plays it
```

---

## F) Copy rules reminder (texts / emails)

- No em dash, en dash, or dash-as-punctuation.  
- No dash bullet lists. Use blank lines or `1. 2. 3.`  
- Always include the full `https://closewithcjclay.com/...` URL on its own line so it is tappable on phones.

---

## G) Suggested first message to paste into a new Cursor chat

```text
@/.cursor/HTSA-AGENT-HANDOFF.md
@/.cursor/rules/htsa-enrollment-invoice-workflow.mdc
@/.cursor/skills/htsa-enrollment-invoice/SKILL.md

Continue HTSA precall + enrollment work. Always --ship, wait for READY, return clickable URL + text. Precall uses /r/cj_clay/ template with MUST WATCH video. Enrollment uses placement 01–06. Client copy: no dashes.
```

Then paste the next client block.

---

*Last updated: Aug 20, 2026 — covers MUST WATCH placement clip, precall auto-flow, enrollment ship rules, Alejandro canonical URL, Mario/Joe/Briana precalls.*
