---
name: htsa-enrollment-invoice
description: >-
  Builds a new HTSA enrollment invoice by duplicating Margarita’s Terms-gate template,
  wiring payment/financing lock, Apps Script payload with phone, and CJ’s program or
  financing choices. Use for new client links, orange-guarantee questions, or pasted
  name/email/phone. Never edits legacy invoices unless CJ names a file.
---

# HTSA enrollment invoice (agent skill)

**Authoritative rules live in** `.cursor/rules/htsa-enrollment-invoice-workflow.mdc`. This skill adds implementation detail for Cursor agents.

---

## Legacy freeze

- Do **not** retrofit, mass-update, or reorder old or already-sent invoices.
- Touch a historical `htsa-enrollment-*.html` **only** when CJ specifies that **exact** filepath.

---

## Reference files

| Purpose | Repo file |
|---------|-----------|
| First production Terms-gate invoice | `htsa-enrollment-margarita-de-la-rosa.html` (Margarita De La Rosa) |
| Sandbox (simulated payment rehearsal) | `htsa-enrollment-cj-clay-practice.html` — never ship trial simulator UI on production pages |
| Pinned GitHub snapshot | [`5f55f399` Margarita blob](https://github.com/clay81090/closewithcjclay.com/blob/5f55f39971069805d08a4e78653c7790a66e7acb/htsa-enrollment-margarita-de-la-rosa.html) |

---

## Mandatory page flow (Margarita parity)

1. Program / curriculum overview  
2. Program Investment heading  
3. Terms gate (`#hts-terms-agreement-panel`): PDF → clarifications → checkbox → Record button  
4. Locked `#invest-pay-zone` wrapping **all** money/financing actions (Whop PIF · 4-pay · Splitit path · ClarityPay · PayVa if CJ names it · Flexxbuy · future checkout links)  
5. Next Steps After Payment  
6. Welcome to HTSA Family  
7. Reviews / testimonials / footer (no duplicate Terms block below Welcome)

---

## Core rule — everything monetized stays locked until Terms record

Prospects pursuing **only financing** still must complete the Terms gate first. Locked zone uses classes `invest-wrap invest-pay-zone invest-pay-zone--locked`; JS intercepts `a.invest-btn` (including `invest-btn secondary`). Session unlock persists via `sessionStorage` (`hts_terms_gate_*` key).

Orange `.enrollment-guarantee-banner` is optional and **separate** from the Terms gate.

---

## Terms gate checklist (mirror Margarita)

- PDF: `https://closewithcjclay.com/HTSA-Terms-of-Service.pdf`  
- Lifetime access + 1-on-1 coaching + AI platform clarifications (same substantive structure as Margarita)  
- Checkbox: *I have read and agree to the Terms of Service linked above.*  
- Button: *Record agreement & unlock payments* (production wording)  

**Panel attributes (unique per invoice):**

- `data-full-name` · `data-email` · **`data-phone`** (E.g. match `tel:` digits) · `data-client-slug`

**Payload `recordTermsAgreement` must include:** `action`, `fullName`, `email`, **`phone`**, `enrollmentPageUrl`, `clientSlug`, `termsUrl`, `termsVersion`, `userAgent`.

**Constants:**

- Endpoint:  
  `https://script.google.com/macros/s/AKfycbxeyf0Q_wiM-d6pq5DnBNKUDVTvMvzFwD60DPpjMEm60LnIQ2tjSkGmy5u1Gt5sQa4Jng/exec`

- Terms version ID: **`HTSA-TOS-PDF-closewithcjclay-2026-04`**

`hts-enrollment-webapp-google-apps-script-sample.gs` already persists `payload.phone`.

---

## CJ inputs (every new invoice)

- Full name, email, phone  
- Program: Closer / Setter / both  
- **Orange performance guarantee:** yes/no (**orange banner only** — not Terms)  
- **Payment setup:**  
  - in-house cash **only** (Whop tiers + Splitit instructions per CJ — **no** external pre-qual), **or**  
  - in-house **plus financing** — include **only vendors CJ names** (ClarityPay, PayVa, Flexxbuy, etc.). **Never invent** providers.

---

## Build steps

```bash
cd /path/to/closewithcjclay.com
cp htsa-enrollment-margarita-de-la-rosa.html htsa-enrollment-firstname-lastname.html
```

Edit **only** the new file: title, hero, billing, Steps, Welcome, Terms `data-*`, unique `sessionStorage` key string, JS slug fallback if any, investment blocks per CJ, optional orange snippet **copied read-only** from Timi/Erick templates (do not alter those repo files).

**Before commit:** `grep` stray template names/emails/phones/slugs.

---

## QA before commit/push

- Only intended **new** `.html` (plus rule/skill if updated in **same task**).  
- No accidental `git add` of `Untitled`, HTSA-Terms review artifacts, or unrelated legacy invoices.  
- Terms data attributes match buyer; **`phone`** in POST body.  
- Pay zone locks until record; unlocks after successful post.  
- Orange banner matches CJ guarantee yes/no.  
- Financing list matches CJ’s named providers only.

**Ship link:** `https://closewithcjclay.com/htsa-enrollment-{slug}.html` — **no** `?v=` unless CJ asks.

---

## Step 2 — Welcome Email card (standard copy)

Match structure from **`htsa-enrollment-amanda-perez.html`**: Zoom links, star/email, Tues + Wed recurring coaching times.

---

## One-line kickoff prompt

```
@htsa-enrollment-invoice NEW invoice:
Name · Email · Phone · Program · Orange banner YES/NO · Payment tiers (exact vendor names OR in-house-only) · Special CJ notes
Duplicate Margarita ONLY — freeze all other invoices.
Clean link output only; cache-bust only if CJ requests.
```

---

## Related

`.cursor/rules/htsa-enrollment-invoice-workflow.mdc` · `htsa-mastermind-member-count.mdc`
