---
name: htsa-enrollment-invoice
description: >-
  Builds a new live HTSA enrollment invoice HTML by copying Margarita-era
  or gold templates in closewithcjclay.com, then personalizing name, email,
  phone, program, payment setup, optional orange guarantee. Use when the user
  asks for an HTSA invoice link, enrollment page, or pastes CJ’s client fields.
---

# HTSA enrollment invoice (new client page)

## Goal

Ship a new **`htsa-enrollment-firstname-lastname.html`** in the **repo root** so **only** the new client’s details change. **Never overwrite** another person’s file.

---

## 1. Legacy invoices are frozen

- Do **not** retrofit old `htsa-enrollment-*.html` pages for the Margarita-era Terms gate, guarantee placement, or copy unless **CJ explicitly requests** edits to **that exact file**.
- Treat **already sent** invoices as immutable for layout experiments.
- **`htsa-enrollment-margarita-de-la-rosa.html`** is the **first real client** page using the **new Terms agreement gate** (`Margarita De La Rosa`).
- **`htsa-enrollment-cj-clay-practice.html`** is the **sandbox** (Terms + simulated payment for Apps Script rehearsal). Default **production** invoices for paying clients mirror **Margarita’s** Terms gate patterns and **omit** simulated payment.

---

## 2. CJ’s inputs — every NEW invoice

Collect (or reuse from HubSpot/text):

| Field | Notes |
|--------|-------|
| Full name | Matches invoice + WhatsApp naming |
| Email | `mailto:` + billing display |
| Phone | `tel:` digits only in `href` |
| **Program** | Closer **or** Setter **or** both |
| **Orange performance guarantee** | **Yes / No** — **only** the optional `.enrollment-guarantee-banner` (see §3) |
| **Payment setup** | **In-house cash only** (Whop PIF / 4-pay / Splitit as in template) **or** **in-house + financing** (add ClarityPay / Flexxbuy-style sections per gold snippet) |
| **Special notes** | Only wording CJ explicitly asked for |

Slug: **`firstname-lastname`**, lowercase, hyphenated filename.

---

## 3. “Guarantee yes/no” ↔ orange banner only

- CJ’s **guarantee** question refers **only** to adding/removing the **orange** **`enrollment-guarantee-banner`** (Timi-/Erick-tier copy as **reference** — **do not edit those files**).
- It **does not** toggle the **Terms agreement gate**. The Terms gate (Margarita-style) stays the standard legal prerequisite on **new** invoices.

---

## 4. Terms agreement gate — standard on NEW invoices

Implement **before** invest/pay zones unlock:

1. **Terms PDF link** (`HTSA-Terms-of-Service.pdf`, same host path as Margarita unless CJ changes policy).  
2. **Lifetime access / coaching / AI** clarification block (reuse Margarita wording structure).  
3. Checkbox acknowledgment + **Record agreement** (or labeled equivalent) wired to **`fetch`** the **existing** Google Apps Script **web app URL** on the page (payload form posts as already implemented).  
4. **Google Sheet** logging is **Terms acknowledgment only** — **do not** label that step as payment success.  
5. **Do not** copy the **CJ practice** “Simulate payment” / trial lab onto **production** invoice pages—that flow is limited to **`htsa-enrollment-cj-clay-practice.html`**.

After **Welcome to the HTSA Family**, continue to stories/footer—**no** second duplicate Terms section under the welcome band.

---

## 5. NEW invoice build + ship checklist

1. **Pick gold template** (program + payment pattern). For the current standard: duplicate **`htsa-enrollment-margarita-de-la-rosa.html`** → new path. Pull investment/guarantee **snippets** from Timi/Jocelyn/etc. only by **copying into the new file**, never by editing gold sources.  
2. **`cp`** (or write-once) to **`htsa-enrollment-{slug}.html`**.  
3. Replace **only** client fields, `data-*` on the Terms panel, invest links, and hero/steps that name the buyer.  
4. **`grep`** old template first names → **zero** unintended hits.  
5. **Smoke:** Terms checkbox → Apps Script reachable (staging); unlocked pay zone; real Whop/checkout links match CJ’s pricing story.  
6. **`git add`** → **only** the new HTML (and `.cursor/rules` / `.cursor/skills` if touched in same task). **Never** `git add` legacy invoices or scratch files (**§6**).  
7. **Commit**, **push** `main` when CJ is ready for live deploy.  
8. Return **one** HTTPS link:

   **`https://closewithcjclay.com/htsa-enrollment-{slug}.html`** — **no `?v=` parameter** unless CJ explicitly requests cache busting (`?v=` + short git SHA acceptable only when asked).

---

## 6. Git hygiene — do not stage junk or legacy churn

Never run blind `git add -A`. Avoid:

| Do **not** `git add` | Reason |
|------------------------|--------|
| `Untitled` | Scratch file |
| `HTSA-Terms-of-Service-cleaned-review.html` / `.pdf` | Review drafts, not invoices |
| Other legacy `htsa-enrollment-*.html` pages (not explicitly updated) | Leave unchanged |

---

## Pick the gold template (read — duplicate — never overwrite)

| User wants | Duplicate from |
|-------------|------------------|
| **Current standard** — Margarita-era Terms gate + closer invest | **`htsa-enrollment-margarita-de-la-rosa.html`** |
| Apps Script rehearsal / simulated pay | **`htsa-enrollment-cj-clay-practice.html`** (not for copying trial pay to clients) |
| Closer **+** Setter dual stacks | **`htsa-enrollment-jocelyn-navarro.html`** |
| Cash + optional orange guarantee snippets | **`htsa-enrollment-timi-bonner-mccourt.html`** (read-only snippets) |
| Setter stack | **`htsa-enrollment-kaitlyn-hall.html`** |
| Orange wording tone | **`htsa-enrollment-erick-brower.html`** |

**Setter vs Closer:** curriculum + investment stacks must align with what they purchased.

---

## Safety rules

1. Never search-replace across the whole enrollment folder.  
2. One new filename per buyer.  
3. No bonus “three calls with Chad” lines unless CJ explicitly asks.  

---

## How to implement (preferred)

```bash
cd /path/to/closewithcjclay.com
cp htsa-enrollment-margarita-de-la-rosa.html htsa-enrollment-firstname-lastname.html
# edit ONLY the new path
```

Non-terminal works if the assistant **`read`s** gold **`write`s** new file then patches.

---

## Fields to change in the new file

- `<title>HTSA Invoice — {Full Name}</title>`  
- Hero + steps using `{FirstName}`  
- `billing-name`, `mailto:`, `tel:`  
- Terms panel `data-full-name`, `data-email`, `data-client-slug` (and phone if used)  
- Investment / financing blocks per CJ’s **payment setup**  
- Optional orange banner only if **guarantee yes**  

`grep` away stray old names.

---

## Step 2 — “Welcome Email” sub-card (unchanged standard)

Source: **`htsa-enrollment-amanda-perez.html`**

- Title: `Welcome Email`  
- Body must include **live group coaching** Zoom detail + star email + **Tuesday 12:00 PM EST** + **Wednesday 5:00 PM EST** calendar hint.  
- Second card: `Login Credentials Email` (temp password flow).

---

## End-to-end validation

Same as **§5** plus: when feasible, **`curl`** / fetch the **clean URL** and confirm buyer identity strings in HTML responses.

Live verification impossible → say what was verified locally.

---

## Related

- Canonical rule snippets: **`htsa-enrollment-invoice-workflow.mdc`**  
- Mastermind headline: **`htsa-mastermind-member-count.mdc`** (490+ members)

---

## Agent vs chat note

Agent mode excels at **`cp`**, targeted edits, **`grep`**, **`git`**—best for closing calls.

---

## One-line trigger (paste in chat)

```text
@htsa-enrollment-invoice New HTSA invoice:
Name:
Email:
Phone:
Program: Closer | Setter | Closer & Setter
Orange performance banner only: Yes | No
Payment: in-house cash only | in-house + financing
Special note (explicit only): 
Push GitHub now: Yes | No
Cache-bust (?v=): ONLY if CJ asks
Do NOT touch legacy invoice files.
```

(Adjust `@` if your Cursor build names this skill differently.)
