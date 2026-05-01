# HTSA enrollment invoice — frozen HTML templates

These files are **not** served as client URLs. They live in `templates/` with `noindex` and `{{HTSA_*}}` placeholders. **Never edit** a deployed `htsa-enrollment-*.html` to spin up a new person.

## Quick “say this to Cursor” prompts

Copy one block and fill in **Full name**, **Email**, **Phone** (and overrides if needed).

**Template 1 — Closer Cash (Whop PIF + 4-pay, orange guarantee)**  
`Use templates/htsa-tpl-01-closer-cash.html — NEW invoice only: Full name, email, phone (E.164). Replace every {{HTSA_*}} OR run scripts/htsa-instantiate-invoice.py. Grep for leftover placeholders. Git add/commit/push only the new htsa-enrollment-{slug}.html. Return the live URL.`

**Template 1b — Closer Cash, NO orange guarantee**  
`Same as Template 1 but duplicate from templates/htsa-tpl-01b-closer-cash-no-guarantee.html`

**Template 2 — Closer Cash + Splitit (under PIF) + 4-pay**  
`templates/htsa-tpl-02-closer-cash-splitit-4pay.html`

**Template 3 — Closer Whop + Splitit + ClarityPay + Flexxbuy**  
`templates/htsa-tpl-03-closer-whop-plus-financing-splitit.html`

**Template 4 — Setter Cash + financing (Trameil-style)**  
`templates/htsa-tpl-04-setter-cash-financing.html`

**Template 5 — Setter Cash only (no ClarityPay / Flexxbuy)**  
`templates/htsa-tpl-05-setter-cash-only.html`

**Template 6 — Closer Whop + ClarityPay + Flexxbuy (Thomas / Akila UI, orange guarantee)**  
`templates/htsa-tpl-06-closer-whop-financing-thomas-ui.html` — same layout as `htsa-enrollment-thomas-rulof.html`; **no** Splitit.

**Template 6b — Same as 6, NO orange guarantee**  
`templates/htsa-tpl-06b-closer-whop-financing-thomas-ui-no-guarantee.html`

## Placeholders (must all be replaced before deploy)

| Token | Example |
|--------|--------|
| `{{HTSA_FULL_NAME}}` | Jane Doe |
| `{{HTSA_FIRST_NAME}}` | Jane |
| `{{HTSA_EMAIL}}` | jane@example.com |
| `{{HTSA_PHONE_E164}}` | +15551234567 (must match `data-phone` and `tel:`) |
| `{{HTSA_PHONE_DISPLAY}}` | +1 (555) 123-4567 |
| `{{HTSA_CLIENT_SLUG}}` | jane-doe (URL: `htsa-enrollment-jane-doe.html`) |
| `{{HTSA_STORAGE_KEY}}` | `hts_terms_gate_jane_doe_v1` (underscores; unique per client) |

## Fast local generate (optional)

From repo root:

```bash
python3 scripts/htsa-instantiate-invoice.py templates/htsa-tpl-01-closer-cash.html \
  --full-name "Jane Doe" \
  --email "jane@example.com" \
  --phone-e164 "+15551234567" \
  --phone-display "+1 (555) 123-4567"
```

The script prints the new file path and **`https://closewithcjclay.com/htsa-enrollment-{slug}.html`**. It **refuses to overwrite** an existing invoice. Then: spot-check, **`git add`** / **`commit`** / **`push`** that new HTML only.

Rebuild frozen copies from production (after a reference invoice changes):

```bash
python3 scripts/build-htsa-invoice-templates.py
```

## Add-on #7 — PayVa (only when CJ says PayVa)

Paste the block from **`templates/snippets/payva-financing-block.html`** into the **locked** `#invest-pay-zone`, in the third-party financing grid — typically **after** ClarityPay or Flexxbuy (match layout from `htsa-enrollment-xavier-cunningham.html`).  
Update any step copy so PayVa is mentioned when needed.

**Default URL in snippet:** `https://app.payva.com/checkout/overview/3ELuF3gxhI` — change only if CJ supplies a new PayVa link.

## Splitit — copy-ready block

- **Already included** in Template **2** and **3**.
- To add Splitit under $6k PIF on another closer layout: paste **`templates/snippets/splitit-under-pif-closer.html`** **inside** the PIF option column (after the green PIF button, before the `4-pay` option), and mirror **Splitit** mentions in step copy like Template 2. Ensure **Splitit CSS** from the template (`.invest-splitit-*`) is present.

## Regenerating templates

Sources for `scripts/build-htsa-invoice-templates.py`:

| Output file | Based on (read-only) |
|-------------|----------------------|
| `htsa-tpl-01-closer-cash.html` | `htsa-enrollment-rebecca-singh.html` |
| `htsa-tpl-01b-…` | Same, orange banner removed |
| `htsa-tpl-02-…` | `htsa-enrollment-matthew-hedden.html` |
| `htsa-tpl-03-…` | `htsa-enrollment-angela-verdone.html` (ClarityPay normalized to `plan_z5iuUhSgm9seH`) |
| `htsa-tpl-04-…` | `htsa-enrollment-trameil-lee.html` |
| `htsa-tpl-05-…` | Trameil, financing section stripped |
| `htsa-tpl-06-…` | `htsa-enrollment-thomas-rulof.html` |
| `htsa-tpl-06b-…` | Same as 06, orange banner removed |
