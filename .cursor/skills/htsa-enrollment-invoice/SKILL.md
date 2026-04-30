---
name: htsa-enrollment-invoice
description: >-
  Builds new HTSA enrollment invoices from modern Terms-gate templates (Closer vs Setter).
  Defaults: orange guarantee ON, mandatory Terms gate + Apps Script, financing ClarityPay +
  Flexxbuy unless Cash-only. After the HTML is ready: git add, commit, and push the new file
  so closewithcjclay.com serves it (otherwise the live URL 404s). Minimal CJ input: program
  type, cash/financing/both, name, email, phone. Never edits deployed client HTML unless
  CJ names the file.
---

# HTSA enrollment invoice (agent skill)

**Authoritative rules live in** `.cursor/rules/htsa-enrollment-invoice-workflow.mdc`. This skill adds implementation detail for Cursor agents.

---

## Minimal kickoff (what CJ can say)

CJ may provide only:

- **Program:** Closer **or** Setter  
- **Payment mode:** Cash **or** Financing **or** Both  
- **Client:** full name, email, phone  

The agent infers everything else from the **defaults below** unless CJ overrides.

**Cash** = Whop paid-in-full + Whop payment-plan options only (no ClarityPay / Flexxbuy tiles).  
**Financing** = ClarityPay + Flexxbuy only (no in-house Whop pay buttons) — *rare;* CJ usually means **Both**.  
**Both** = in-house Whop options **plus** ClarityPay + Flexxbuy.

---

## Default: orange performance guarantee

- **ON for every new Closer and Setter invoice.**
- Place **`enrollment-guarantee-banner enrollment-guarantee-banner--pre-terms`** directly under the **Program Investment** heading and **above** the Terms gate.
- Copy wording: match **`htsa-enrollment-zachary-taylor.html`** / **`htsa-enrollment-chad-aleo.html`** (reference only — do not edit those files to build a new client).
- **Omit the orange banner only if** CJ explicitly says **“no guarantee”** or **“omit orange guarantee.”**

---

## Mandatory Program Investment order

1. **Program Investment** heading  
2. **Orange performance guarantee** banner (unless explicitly omitted)  
3. **Terms of Service gate:** PDF link → clarifications → checkbox → **Record agreement & unlock payments**  
4. **Locked** `#invest-pay-zone` wrapping **all** money actions  

No payment or financing button may sit **outside** the locked zone. Unlock only after `recordTermsAgreement` POST succeeds; persist with **`sessionStorage`** using a **unique** key:

```text
hts_terms_gate_<firstname>_<lastname>_v1
```

(use underscore-separated slug words, e.g. `hts_terms_gate_jane_doe_v1`).

**Lock until Terms recorded (non-exhaustive):** Whop PIF, Whop installment plans, **ClarityPay**, **Flexxbuy**, **PayVa** (if CJ explicitly requested), **Splitit** (if CJ explicitly requested), any future checkout or pre-qual link.

---

## Google Sheets / Apps Script (mandatory)

Every new invoice must POST the Terms agreement to this **exact** endpoint:

`https://script.google.com/macros/s/AKfycbxeyf0Q_wiM-d6pq5DnBNKUDVTvMvzFwD60DPpjMEm60LnIQ2tjSkGmy5u1Gt5sQa4Jng/exec`

| Constant | Value |
|----------|--------|
| Terms PDF | `https://closewithcjclay.com/HTSA-Terms-of-Service.pdf` |
| `termsVersion` | `HTSA-TOS-PDF-closewithcjclay-2026-04` |

**Payload** (`payload=` URL-encoded JSON) must include: `action` (`recordTermsAgreement`), `fullName`, `email`, `phone`, `enrollmentPageUrl`, `clientSlug`, `termsUrl`, `termsVersion`, `userAgent`.

**References** (read-only): `htsa-enrollment-cj-clay-practice.html`, `hts-enrollment-webapp-google-apps-script-sample.gs` — for behavior only. **Never** copy the practice page’s simulated payment UI onto real client invoices.

---

## Financing defaults

- If CJ says **Financing** or **Both:** include **ClarityPay** and **Flexxbuy** by default. Spell **Flexxbuy** (two **x**’s).
- **Do not** include **PayVa** unless CJ explicitly says **PayVa**.
- **Do not** include **Splitit** unless CJ explicitly requests it.

---

## Closer defaults

- **Naming:** Certified HTS Closer / Certified High Ticket Closer Program (title, header, curriculum).  
- **Curriculum:** **50** modules; **five** levels of AI roleplay (closer wording).  
- **Default cash pricing:** PIF **$6,000**; **4-pay** **$1,750** today / **$7,000** total.  
- **UI:** Newest **Zachary-style** layout (spacing, mobile-ready Terms gate placement).  
- **Structural duplicate source:** prefer **`htsa-enrollment-james-chambers.html`** or **`htsa-enrollment-kristijo-sherman.html`** (2026 footer + Terms stack; **edit only** the new file).  
- **Whop plan URLs:** Match CJ-supplied links or those in the template you duplicated; do not invent checkout IDs.

---

## Setter defaults

- **Naming:** Certified HTS Setter / Certified High Ticket Setter Program; badge **Setter Program Overview**.  
- **Curriculum:** **30** core modules; **three** levels of AI roleplay; certification **Certified High Ticket Setter**; setter-specific placement copy (no closer wording).  
- **Default cash pricing:** PIF **$3,000**; **3-pay** **$1,050** today / **$3,150** total.  
- **Default Whop links:**  
  - PIF: `https://whop.com/checkout/plan_qzvfCCb1rIO0L?d2c=true`  
  - 3-pay: `https://whop.com/checkout/plan_oK3AajTKp0mXK?d2c=true`  
- **Financing links:**  
  - ClarityPay: `https://whop.com/checkout/plan_z5iuUhSgm9seH`  
  - Flexxbuy: `https://app.flexxbuy.com/high-ticket-sales-academy-llc/apply/`  
- **Flexxbuy setter note (include when Flexxbuy is on the page):**  
  *Flexxbuy — Setter: Request $3,500 when applying through Flexxbuy, for application purposes, exactly $500 more than the $3,000 program price.*  
- **Structural duplicate source:** e.g. **`htsa-enrollment-trameil-lee.html`** (reference only; **edit only the new file**).

---

## Mobile readiness

- Match **Zachary-style** spacing, breakpoints, and Terms/pay-zone behavior.  
- Preserve **Chad-style** mobile **`ref-strip`** + footer fixes (`htsa-enrollment-chad-aleo.html`) where applicable.  
- Do not ship desktop-only layouts.

---

## Footer layout (2026 default — use on new invoices)

When building **new** pages, **duplicate footer markup from** **`htsa-enrollment-james-chambers.html`** or **`htsa-enrollment-kristijo-sherman.html`** so the live site stays consistent:

- **HTSA column:** Site / YouTube / Instagram / Facebook as **inline SVG icons in brand colors** (globe blues & greens, YouTube red, Instagram gradient, Facebook blue) + link text — **`footer-htsa-link`** pattern.  
- **Do not** put Trustpilot in that small stack.  
- **Full-width row** below the main footer flex (**`footer-reviews-row`**): prominent Trustpilot link with **five gold stars** (**`#e2b227`**, not green) + “Trustpilot Reviews — 4.8 out of 5”, plus visible **`support@highticketsalesacademy.com`** (`mailto`).  
- Keep the **CJ business card** column as in those files.

---

## Legacy freeze

- Do **not** retrofit old invoices unless CJ names the **exact** `htsa-enrollment-*.html` path.  
- **Margarita** remains the historical “first Terms-gate” anchor; for **current** layout + **2026 footer** (social SVGs, gold Trustpilot row, support email), prefer **James Chambers** / **Kristijo Sherman** (Closer) or **Trameil** (Setter) as duplicate sources.

---

## Build steps

1. Choose duplicate source: **Closer** → prefer **`htsa-enrollment-james-chambers.html`** or **`htsa-enrollment-kristijo-sherman.html`** for **footer + guarantee + Terms order** parity; **Setter** → **`htsa-enrollment-trameil-lee.html`**. (Older templates lack the 2026 footer.)
2. `cp` → `htsa-enrollment-{slug}.html` — work **only** in the new file.  
3. Set client `data-*`, `STORAGE_KEY`, hero, billing, steps, investment blocks per defaults + CJ overrides.  
4. Run the **verification checklist** (below).  
5. `grep` for stray template names, emails, phones, slugs.  
6. **Deploy (mandatory for a working live URL):** `git add` **only** the new `htsa-enrollment-{slug}.html`, **`git commit`**, **`git push origin main`** (or the repo’s default publish branch). The site **closewithcjclay.com** serves files from this repo — if the file never gets pushed, **`https://closewithcjclay.com/htsa-enrollment-{slug}.html` returns 404**.  
7. **Skip commit/push only if** CJ explicitly says not to (e.g. draft only).  
8. Return: `https://closewithcjclay.com/htsa-enrollment-{slug}.html` — **no** `?v=` unless CJ asks.  
   - **Critical:** The path segment is **`htsa-enrollment-`** (letters **h-t-s-a**), **not** `hts-enrollment-`. Missing the **`a`** produces **404** on GitHub Pages.

---

## Verification checklist (before calling the invoice done)

- Correct **Closer vs Setter** program type and copy (modules / AI levels / certification).  
- **Cash / Financing / Both** reflected in what’s on the page.  
- **Orange guarantee** present unless CJ said to omit.  
- **Terms gate** above **all** pay/finance buttons; buttons inside locked zone only.  
- Apps Script **endpoint** + **`termsVersion`** + PDF URL correct; **payload includes `phone`**.  
- Unique **`data-full-name`**, **`data-email`**, **`data-phone`**, **`data-client-slug`** + **`sessionStorage`** key.  
- No stray prior-client data.  
- **No PayVa** unless CJ asked; **no Splitit** unless CJ asked.  
- **Flexxbuy** spelled with two x’s.  
- Mobile layout consistent with recent invoices (Zachary / Chad patterns).  
- **New invoice file is committed and pushed** so the live URL does not 404.

---

## Related

`.cursor/rules/htsa-enrollment-invoice-workflow.mdc` · `htsa-mastermind-member-count.mdc` (490+ mastermind wording)

---

## One-line kickoff prompt (updated)

```
@htsa-enrollment-invoice NEW invoice:
Closer OR Setter · Cash OR Financing OR Both · Full name · Email · Phone
(Duplicate modern template only — freeze all other client HTML unless named.)
After the file is correct: git add, commit, push the new HTML so the live URL works (404 if only local).
```
