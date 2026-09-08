# CLAUDE CODE — HARD FENCE (READ BEFORE ANY EDIT)

**Created:** Sept 3, 2026 · for the special-offer self-enroll job only  
**CJ:** Charles Clay · (616) 612-1735  

You are **not** redesigning Cursor’s live site project. You are **not** rewriting Co-Pilot V3. You are **not** dumping transcripts into git.

---

## STOP — if you see this in the Commit UI

If Cursor / Claude Code shows something like:

```text
HTSA_LIVE_CALL_L…   +112,348  −0
```

**DO NOT CLICK COMMIT.**

That is the wrong project / wrong files (almost certainly `Documents/HTSA_LIVE_CALL_LAB` or a giant text dump). Committing it will pollute git with ~100k+ lines of vault/ammo/transcripts.

**CJ action:** click Discard / Unstage All on that commit card. Do not push.

---

## 1. Your ONLY workspace for this job

Open **this folder** as the project / workspace root (File → Open Folder):

```text
/Users/charlesclay/Documents/SPECIAL-OFFER-CLAUDE-SANDBOX/
```

Layout:

```text
SPECIAL-OFFER-CLAUDE-SANDBOX/
├── CLAUDE_CODE_HARD_FENCE.md          ← this file (rules)
├── PASTE_THIS_PROMPT_TO_CLAUDE.md     ← short prompt for CJ
├── READ_ONLY/                         ← read, never rewrite history of these
│   ├── SPECIAL-OFFER-SELF-ENROLL-HANDOFF-FOR-CLAUDE.md
│   └── Final-Special-Offer-Total-Offer-Enrollment.txt   ← from Downloads (copied here so you do NOT need Downloads access)
├── REFERENCE/                         ← read only
│   ├── OPTION-B-ACCORDION-EXACT.html  ← copy this markup into Option B
│   ├── jayden-lepper-OPTION-B-SOURCE.html
│   ├── HTSA-SECONDARY-PAYMENT-OPTIONS.md
│   ├── meet-cj.html
│   └── og-meet-cj.jpg
└── WORK/
    └── special-offer.html             ← THE ONLY FILE YOU MAY EDIT
```

### Allowed write

| Path | Permission |
|---|---|
| `WORK/special-offer.html` | **EDIT THIS ONLY** |
| Optional: `WORK/NOTES-FOR-CJ.md` | You may create short notes for CJ |

### Allowed read

Everything under `READ_ONLY/` and `REFERENCE/`.

### Forbidden

Everything else on the Mac. Full list in section 3.

---

## 2. What this job is

Rebuild / tighten **one page**: the shared special-offer self-enroll blast for people who already got the discount outreach, deadline **Thursday Sept 4, 2026**.

Live URL after CJ merges your file (CJ / Cursor ships, not you):

```text
https://closewithcjclay.com/special-offer.html
```

Hard product constraints (non-negotiable):

1. **Option A** = call or text CJ and enroll **live** only.  
2. **Option B** = exact 5-step accordion from `REFERENCE/OPTION-B-ACCORDION-EXACT.html`  
   (Payment made → two emails → spam/10 min → Mark kickoff → Mastermind).  
3. This page **IS** the enrollment page. Never say CJ will send another enroll link.  
4. Pricing = reactivation only: **$5,000 PIF** · **3 × $1,750** · **ClarityPay $500/mo ($6,000)** — URLs in `REFERENCE/HTSA-SECONDARY-PAYMENT-OPTIONS.md` (Promotion / reactivation section).  
5. Footer: CJ business card on the **right inside** the dark footer.  
6. Compact referral SMS near bottom (meet-cj preview) with **$250 first 3 / $500 after**.  
7. Prefer simplicity (February self-enroll energy). Do not invent a new design system.  
8. Show CJ a **5-bullet structure** first, then edit `WORK/special-offer.html` only.

Read first:

1. `READ_ONLY/SPECIAL-OFFER-SELF-ENROLL-HANDOFF-FOR-CLAUDE.md`  
2. `READ_ONLY/Final-Special-Offer-Total-Offer-Enrollment.txt` (CJ’s brief from Downloads; already copied here)  
3. `REFERENCE/OPTION-B-ACCORDION-EXACT.html`

---

## 3. NEVER TOUCH (off limits — decline any tool request)

### A. Live GitHub Pages site (Cursor production)

```text
/Users/charlesclay/Desktop/closewithcjclay.com/closewithcjclay.com/
```

Including but not limited to:

- `special-offer.html` in that repo (live) — CJ copies YOUR `WORK/` file in later  
- every `htsa-enrollment-*.html`  
- every `r/*/index.html`  
- `templates/`, `scripts/`, `.cursor/rules/`, `30-day-roadmap.html`, `meet-cj.html`  
- git commit / push on that repo  

**Never rewrite an existing Cursor project.** This live site is Cursor’s domain.

### B. Live Co-Pilot / CJ_AI_OS (production)

```text
/Users/charlesclay/CJ_AI_OS/
```

Especially:

```text
/Users/charlesclay/CJ_AI_OS/06_LIVE_AI_COPILOT_PRODUCT/
```

There is already a Co-Pilot sandbox with its own rules:

```text
/Users/charlesclay/Documents/CJ-CO-PILOT-V3-FOR-CLAUDE/
```

**Do not open Co-Pilot V3 for this special-offer job.** Wrong product.

### C. Live Call Lab / vaults (this is what caused the +112k staging)

```text
/Users/charlesclay/Documents/HTSA_LIVE_CALL_LAB/
```

Do not add files there. Do not commit there. Do not “helpfully” import transcripts.

### D. Other Cursor / Codex / Genspark mirrors (read only if CJ says; default = no)

```text
/Users/charlesclay/Documents/CJ-CO-PILOT-V3-FOR-CODEX copy/
/Users/charlesclay/Documents/CJ-CO-PILOT-V3-FOR-CLAUDE/
/Users/charlesclay/Desktop/July 9th 2026/
/Users/charlesclay/Desktop/UPLOAD_TO_CLAUDE_PROJECT_NOW/
```

### E. Downloads / Desktop dumps

You do **not** need Downloads access for this job. The Final Offer txt is already in:

```text
READ_ONLY/Final-Special-Offer-Total-Offer-Enrollment.txt
```

Do not copy giant `.txt` / PDF / transcript files into any git repo.

### F. Secrets

Never create or commit API keys, `config.js` with keys, `.env`, or Whop admin secrets.

---

## 4. How CJ should open Claude Code for this job

1. Close any workspace that is `HTSA_LIVE_CALL_LAB` or `closewithcjclay.com`.  
2. **File → Open Folder** → `Documents/SPECIAL-OFFER-CLAUDE-SANDBOX`  
3. Paste the prompt from `PASTE_THIS_PROMPT_TO_CLAUDE.md`  
4. When Claude finishes, CJ (or Cursor chat in the live site) copies:

```bash
cp "/Users/charlesclay/Documents/SPECIAL-OFFER-CLAUDE-SANDBOX/WORK/special-offer.html" \
   "/Users/charlesclay/Desktop/closewithcjclay.com/closewithcjclay.com/special-offer.html"
```

Then Cursor commits **only** that one HTML file to `main` and pushes. Claude Code does **not** push the live site.

---

## 5. Access / permissions (what “Allow” means)

CJ hit Allow for Downloads and web URLs. That does **not** mean you should write into Downloads or browse the whole disk.

| Access | Use |
|---|---|
| This sandbox folder | Yes — your home for the job |
| Web / Whop / closewithcjclay.com URLs | Yes — to verify live pages if asked |
| Downloads | **Not needed** — file already copied into `READ_ONLY/` |
| Live site repo | **No write** |
| CJ_AI_OS | **No** |
| HTSA_LIVE_CALL_LAB | **No** |

If a tool asks for a path outside the sandbox: **refuse** and say you only work in `SPECIAL-OFFER-CLAUDE-SANDBOX`.

---

## 6. Commit rules inside the sandbox (if any)

Preferred: **do not init git** in the sandbox. Just edit `WORK/special-offer.html`.

If you must use git in the sandbox:

- Commit **only** `WORK/special-offer.html` (+ optional `WORK/NOTES-FOR-CJ.md`)  
- Never add `READ_ONLY/Final-Special-Offer-*.txt` (too big / not for Pages)  
- Never add files from outside the sandbox  

---

## 7. Done checklist

- [ ] Only `WORK/special-offer.html` changed  
- [ ] Option A = live call/text only  
- [ ] Option B markup matches `REFERENCE/OPTION-B-ACCORDION-EXACT.html`  
- [ ] Reactivation Whop links only  
- [ ] No “I’ll send your enrollment page”  
- [ ] No commit to HTSA_LIVE_CALL_LAB or closewithcjclay.com  
- [ ] Short note for CJ: what changed, how to copy file back to live repo  

---

*End hard fence.*
