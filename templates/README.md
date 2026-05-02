# HTSA enrollment invoice — frozen HTML templates

Shells in `templates/` use **`noindex`** and **`{{HTSA_*}}` placeholders only** (no client names baked in). **Never edit** a deployed `htsa-enrollment-*.html` to create a new person — copy a shell, fill placeholders, save a **new** root file.

## CJ defaults (frozen shells)

| Topic | Rule |
|--------|------|
| **Orange guarantee** | **On** in every shell **except** **1b** and **6b** (use those only when you say *no guarantee*). |
| **PayVa** | **Never** inside these shells. Add **`snippets/payva-financing-block.html`** only when you say **PayVa**. |
| **Splitit** | **On** for **every Closer** shell (under $6k PIF). **Not** on **Setter** shells (**4**, **5**). |
| **Setter** | No Splitit. |

---

## Copy → paste → fill (use with Cursor Agent)

Replace **`FULL NAME`**, **`EMAIL`**, **`+1XXXXXXXXXX`** (E.164, no spaces), and optionally pretty phone in `--phone-display` if you use the script.

| Pick… | Paste this (then fill the CAPS) |
|--------|----------------------------------|
| **1** Closer · cash + Splitit + 4-pay · guarantee | `@htsa-enrollment-invoice NEW from templates/htsa-tpl-01-closer-cash.html — FULL NAME — EMAIL — phone E.164 +1XXXXXXXXXX. Instantiate or replace {{HTSA_*}}. Grep {{HTSA. Push new HTML only. Return https://closewithcjclay.com/htsa-enrollment-{slug}.html` |
| **1b** Same as **1** · **no** orange guarantee | Same as row above but file **`templates/htsa-tpl-01b-closer-cash-no-guarantee.html`** |
| **2** *(legacy filename, same file as **1**)* | **`templates/htsa-tpl-02-closer-cash-splitit-4pay.html`** — identical to **1**; keep if an old habit |
| **3** Closer · Whop + Splitit + ClarityPay + Flexxbuy | **`templates/htsa-tpl-03-closer-whop-plus-financing-splitit.html`** + same fill-ins |
| **4** Setter · cash + financing | **`templates/htsa-tpl-04-setter-cash-financing.html`** + same fill-ins |
| **5** Setter · cash only | **`templates/htsa-tpl-05-setter-cash-only.html`** + same fill-ins |
| **6** Closer · Whop + Splitit + ClarityPay + Flexxbuy · `invest-pay-zone` layout | **`templates/htsa-tpl-06-closer-whop-financing-invest-pay-zone.html`** + same fill-ins |
| **6b** Same as **6** · **no** guarantee | **`templates/htsa-tpl-06b-closer-whop-financing-invest-pay-zone-no-guarantee.html`** |

---

## One command (optional)

From repo root — swap the template path for **1**, **3**, **4**, **5**, **6**, etc.:

```bash
python3 scripts/htsa-instantiate-invoice.py templates/htsa-tpl-01-closer-cash.html \
  --full-name "FULL NAME" \
  --email "EMAIL" \
  --phone-e164 "+1XXXXXXXXXX" \
  --phone-display "+1 (XXX) XXX-XXXX"
```

Then **`git add` / `commit` / `push`** the new `htsa-enrollment-{slug}.html` so the live URL works.

---

## Placeholders (must all be replaced before deploy)

| Token | Example |
|--------|--------|
| `{{HTSA_FULL_NAME}}` | Jane Doe |
| `{{HTSA_FIRST_NAME}}` | Jane |
| `{{HTSA_EMAIL}}` | jane@example.com |
| `{{HTSA_PHONE_E164}}` | +15551234567 (must match `data-phone` and `tel:`) |
| `{{HTSA_PHONE_DISPLAY}}` | +1 (555) 123-4567 |
| `{{HTSA_CLIENT_SLUG}}` | jane-doe |
| `{{HTSA_STORAGE_KEY}}` | `hts_terms_gate_jane_doe_v1` |

---

## PayVa add-on (only when you say PayVa)

Paste **`templates/snippets/payva-financing-block.html`** into the locked **`#invest-pay-zone`** financing grid (see live pages that include PayVa for placement). Default link: `https://app.payva.com/checkout/overview/3ELuF3gxhI`.

---

## Splitit snippet (rare)

Closer shells **already** include Splitit. Use **`templates/snippets/splitit-under-pif-closer.html`** only when patching a **non-template** closer page that is missing Splitit.

---

## Regenerating from production HTML

After a reference page changes, from repo root:

```bash
python3 scripts/build-htsa-invoice-templates.py
```

| Output | Source (read-only production file) |
|--------|--------------------------------------|
| `htsa-tpl-01-closer-cash.html` | `htsa-enrollment-matthew-hedden.html` |
| `htsa-tpl-01b-…` | Same, orange banner removed |
| `htsa-tpl-02-…` | **Duplicate of tpl-01** (legacy filename) |
| `htsa-tpl-03-…` | `htsa-enrollment-angela-verdone.html` (ClarityPay → `plan_z5iuUhSgm9seH`) |
| `htsa-tpl-04-…` | `htsa-enrollment-trameil-lee.html` |
| `htsa-tpl-05-…` | Trameil, financing section stripped |
| `htsa-tpl-06-…` | `htsa-enrollment-thomas-rulof.html` + **Splitit** injected by script |
| `htsa-tpl-06b-…` | Same as 06, orange banner removed |
