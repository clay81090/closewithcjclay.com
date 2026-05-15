---
name: htsa-enrollment-invoice
description: >-
  Builds new HTSA enrollment invoices from modern Terms-gate templates (Closer vs Setter).
  CJ placement table: templates/HTSA-ENROLLMENT-PLACEMENT-NOTES.md. Defaults: orange guarantee ON,
  mandatory Terms gate + Apps Script, financing ClarityPay +
  Flexxbuy unless Cash-only. After the HTML is ready: git add, commit, and push the new file
  so closewithcjclay.com serves it (otherwise the live URL 404s). Minimal CJ input: program
  type, cash/financing/both, name, email, phone. Prefer frozen shells in templates/. Secondary
  Whop plans: templates/HTSA-SECONDARY-PAYMENT-OPTIONS.md (use only when CJ asks). Never
  edits deployed client HTML unless CJ names the file.
---

# HTSA enrollment invoice (agent skill)

**Authoritative rules live in** `.cursor/rules/htsa-enrollment-invoice-workflow.mdc`. This skill adds implementation detail for Cursor agents.

---

## Minimal kickoff (what CJ can say)

CJ may provide only:

- **Program:** Closer **or** Setter **or** **Closer & Setter** (both on one page)  
- **Payment mode:** Cash **or** Financing **or** Both  
- **Client:** full name, email, phone  

Or CJ can name the **placement row** verbatim: *Closer – Cash only*, *Closer – Cash + Financing*, *Setter – Cash only*, *Setter – Cash + Financing*, *Closer & Setter – Cash only*, *Closer & Setter – Cash + Financing* (maps to `templates/htsa-placement-0X-….html`).

The agent infers everything else from the **defaults below** unless CJ overrides.

---

## Frozen templates in `templates/` (fastest path)

**CJ defaults (frozen shells):** Orange performance guarantee **on** in **every** shell. **Omit** it **only** if CJ explicitly says **no guarantee**. **PayVa** is **never** baked into shells — use `templates/snippets/payva-financing-block.html` only when CJ says **PayVa**. **`htsa-placement-01` (Closer cash only)** has **no Splitit** — Whop PIF + 4-pay only. **Other Closer** frozen shells include **Splitit** under $6k PIF unless CJ says **no Splitit**; **Setter** has **no** Splitit. **`htsa-placement-03`** keeps header + billing `Payment:` as the short **Select payment option below** line (Wayne-style); amounts live only under Program Investment (`setter_cash_only` in the build script). Template HTML uses **`{{HTSA_*}}` placeholders only** — no personal names in filenames as “clients.”

| CJ row | File |
|--------|------|
| **Closer – Cash only** | `templates/htsa-placement-01-closer-cash-only.html` |
| **Closer – Cash + Financing** | `templates/htsa-placement-02-closer-cash-financing.html` |
| **Setter – Cash only** | `templates/htsa-placement-03-setter-cash-only.html` |
| **Setter – Cash + Financing** | `templates/htsa-placement-04-setter-cash-financing.html` |
| **Closer & Setter – Cash only** | `templates/htsa-placement-05-closer-setter-cash-only.html` |
| **Closer & Setter – Cash + Financing** | `templates/htsa-placement-06-closer-setter-cash-financing.html` |

**Instantiation:** Replace placeholders by hand, or run `python3 scripts/htsa-instantiate-invoice.py 01 …` from repo root — first arg can be **`01`–`06`** (or `templates/htsa-placement-….html`). Use **`--overwrite --ship`** on calls to replace the same slug and push one file. After `build-htsa-invoice-templates.py`, run **`rebuild-htsa-demo-enrollment-pages.py`** to refresh the six **`htsa-enrollment-demo-*`** URLs. See **`templates/README.md`**.

**CJ quick reference (Notion-friendly):** **`templates/HTSA-ENROLLMENT-PLACEMENT-NOTES.md`**.  
**CJ copy-paste prompts:** **`templates/README.md`**.

**Hard rule:** Materialize **`htsa-enrollment-{slug}.html`** at repo root only — never turn an existing client file into someone else.

---

## Secondary (alternate) Whop plans — `templates/HTSA-SECONDARY-PAYMENT-OPTIONS.md`

**Not** part of the main six shells. Stores CJ’s **other** Whop checkouts:

- **Closer:** $6,000 **2-pay** (Action Taker — on-call discount framing), **$6,600** 3-pay ($2,200×3), **$5,000 PIF** (experience / discount — **not** the default $6k PIF).
- **Setter:** **$3,000** 2-pay ($1,500 + $1,500 in 30 days).

**When to use:** Only if CJ names an offer from that list or says to add **secondary / other payment options**. **Do not** silently replace primary template links with secondary URLs.

**How to add on a page:** After the primary options (still inside `#invest-pay-zone`), add a horizontal rule + `invest-section-kicker` (match existing template wording style), then **duplicate** the same `invest-option` / `invest-row` / `invest-price-big` / `invest-btn` markup as the primary block — **only** change numbers, button copy, and `href`. Keeps font, height, and mobile behavior identical.

---

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

**Lock until Terms recorded (non-exhaustive):** Whop PIF, Whop installment plans, **ClarityPay**, **Flexxbuy**, **PayVa** (if CJ explicitly requested), **Splitit** (when on page; **not** on **`htsa-placement-01`**), any future checkout or pre-qual link.

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
- **ClarityPay Whop checkouts (do not swap):** **Closer** = **$7,200** `https://whop.com/checkout/1ba2LjGOo3B1Wpp4jf-eF61-w5X4-yCzD-25zhqI3VcVLf/`; **Setter** = **$3,600** `https://whop.com/checkout/plan_z5iuUhSgm9seH?d2c=true`. **Never** put the Setter Clarity plan on Closer-only stacks (or the Closer $7,200 link on Setter-only stacks).
- **Do not** include **PayVa** unless CJ explicitly says **PayVa**.
- **Splitit:** **`htsa-placement-01`** omits it. **Other Closer** frozen shells / ad-hoc closer cash: include under PIF unless CJ says **no Splitit**. **Do not** put Splitit on **Setter** invoices.

---

## Closer defaults

- **Naming:** Certified HTS Closer / Certified High Ticket Closer Program (title, header, curriculum).  
- **Curriculum:** **50** modules; **five** levels of AI roleplay (closer wording).  
- **Default cash pricing:** PIF **$6,000**; **4-pay** **$1,750** today / **$7,000** total.  
- **UI:** Newest **Zachary-style** layout (spacing, mobile-ready Terms gate placement).  
- **Structural duplicate source:** prefer **`htsa-enrollment-james-chambers.html`** or **`htsa-enrollment-kristijo-sherman.html`** (2026 footer + Terms stack; **edit only** the new file).  
- **Whop plan URLs:** Match CJ-supplied links or those in the template you duplicated; do not invent checkout IDs.
- **Closer + financing:** **ClarityPay** tile must use the **$7,200** checkout (`…/1ba2LjGOo3B1Wpp4jf-eF61-w5X4-yCzD-25zhqI3VcVLf/`), **not** `plan_z5iuUhSgm9seH` (Setter / $3,600).
- **Splitit** under PIF: **not** on **`htsa-placement-01`**. **Default on** other closer cash frozen shells (**02**, **05**, **06**, etc.) unless CJ says **no Splitit**. **Never** on setter.

---

## Setter defaults

- **Naming:** Certified HTS Setter / Certified High Ticket Setter Program; badge **Setter Program Overview**.  
- **Curriculum:** **30** core modules; **three** levels of AI roleplay; certification **Certified High Ticket Setter**; setter-specific placement copy (no closer wording).  
- **Default cash pricing:** PIF **$3,000**; **3-pay** **$1,050** today / **$3,150** total.  
- **Default Whop links:**  
  - PIF: `https://whop.com/checkout/plan_qzvfCCb1rIO0L?d2c=true`  
  - 3-pay: `https://whop.com/checkout/plan_oK3AajTKp0mXK?d2c=true`  
- **Financing links:**  
  - ClarityPay (**$3,600** at checkout): `https://whop.com/checkout/plan_z5iuUhSgm9seH?d2c=true`  
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
- **Full-width row** below the main footer flex (**`footer-reviews-row`**): prominent Trustpilot link with **five gold stars** (**`#e2b227`**, not green) + “Trustpilot Reviews — **4.9 stars** out of 5”, plus visible **`support@highticketsalesacademy.com`** (`mailto`).  
- Keep the **CJ business card** column as in those files.

---

## Legacy freeze

- Do **not** retrofit old invoices unless CJ names the **exact** `htsa-enrollment-*.html` path.  
- **Margarita** remains the historical “first Terms-gate” anchor; **frozen `htsa-placement-01…06`** get **Member voice** testimonials + **colored footer icons** from **`htsa-enrollment-wayne-wintermute.html`** via `scripts/build-htsa-invoice-templates.py`. For one-off edits without rebuilding, **James Chambers** / **Kristijo Sherman** (Closer) or **Trameil** (Setter) remain useful references.

---

## Build steps

1. **Prefer** a frozen template from **`templates/`** (see table earlier in this skill + **`templates/README.md`**). Otherwise choose duplicate source: **Closer** → **`htsa-enrollment-james-chambers.html`** or **`htsa-enrollment-kristijo-sherman.html`**; **Setter** → **`htsa-enrollment-trameil-lee.html`**.  
2. `cp` the template → `htsa-enrollment-{slug}.html` **or** run **`scripts/htsa-instantiate-invoice.py`** — work **only** in the new file.  
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
- **No PayVa** unless CJ asked; **Splitit** only where the page includes it (**placement-01** has none); **no Splitit** on setter.  
- **Flexxbuy** spelled with two x’s.  
- Mobile layout consistent with recent invoices (Zachary / Chad patterns).  
- **New invoice file is committed and pushed** so the live URL does not 404.  
- **If the URL 404s immediately after push:** wait **1–5 minutes** (GitHub Pages rebuild), then **hard-refresh**; confirm with `sh scripts/check-enrollment-live.sh {slug}` or `curl -sI https://closewithcjclay.com/htsa-enrollment-{slug}.html`. See workflow rule **“If the live link returns 404”**.

---

## Related

`.cursor/rules/htsa-enrollment-invoice-workflow.mdc` · `htsa-mastermind-member-count.mdc` (520+ mastermind wording) · `templates/HTSA-ENROLLMENT-PLACEMENT-NOTES.md`

---

## One-line kickoff prompt (updated)

```
@htsa-enrollment-invoice NEW invoice:
Pick placement: Closer/Setter/dual × cash/financing — full name · email · phone
Use `templates/htsa-placement-0X-….html`; freeze other client HTML unless named.
After the file is correct: git add, commit, push the new HTML (else live URL 404s). Allow 1–5 min for GitHub Pages after push.
```
