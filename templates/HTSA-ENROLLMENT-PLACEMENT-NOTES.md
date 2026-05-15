# HTSA enrollment — placement shells (CJ reference)

Authoritative for **which frozen file** to use. Full agent procedure: `.cursor/skills/htsa-enrollment-invoice/SKILL.md` and `.cursor/rules/htsa-enrollment-invoice-workflow.mdc`.

## Six placement rows

| You say | Template file |
| --- | --- |
| Closer – Cash only | `templates/htsa-placement-01-closer-cash-only.html` |
| Closer – Cash + Financing | `templates/htsa-placement-02-closer-cash-financing.html` |
| Setter – Cash only | `templates/htsa-placement-03-setter-cash-only.html` |
| Setter – Cash + Financing | `templates/htsa-placement-04-setter-cash-financing.html` |
| Closer & Setter – Cash only | `templates/htsa-placement-05-closer-setter-cash-only.html` |
| Closer & Setter – Cash + Financing | `templates/htsa-placement-06-closer-setter-cash-financing.html` |

## Shell notes

- **01** — Source: `htsa-enrollment-val-tappan.html` — $6k PIF + 4-pay only (**no Splitit**); Terms + Apps Script + orange banner; `{{HTSA_*}}`.
- **02** — Source: `htsa-enrollment-thomas-rulof.html` + Splitit under PIF + **Closer** ClarityPay **$7,200** `https://whop.com/checkout/1ba2LjGOo3B1Wpp4jf-eF61-w5X4-yCzD-25zhqI3VcVLf/` + Flexxbuy. **Never** Setter `plan_z5iuUhSgm9seH` on Closer. No PayVa.
- **03 / 04** — Source: `htsa-enrollment-trameil-lee.html`; **03** has financing stripped; Terms/hint = payment-only (not “financing”).
- **05 / 06** — Jocelyn header + combined curriculum on Val shell; one Terms gate + one `#invest-pay-zone`; Closer invest-box then Setter invest-box; footer card title **Closer & Setter**; no PayVa.
- **Guarantee** — Orange block in all six; omit only if CJ says **no guarantee**.

## Rebuild frozen templates

From repo root:

```bash
python3 scripts/build-htsa-invoice-templates.py
```

Writes `htsa-placement-01`…`06`; removes legacy `htsa-tpl-*.html` if present. **Read-only** pull of Member voice strip + footer row from `htsa-enrollment-wayne-wintermute.html` (Wayne’s **live** file is not modified). Normalizes Mastermind copy to **520+** and Trustpilot line to **4.9 stars out of 5** on write.

## ClarityPay (never swap)

- **Closer:** $7,200 — `https://whop.com/checkout/1ba2LjGOo3B1Wpp4jf-eF61-w5X4-yCzD-25zhqI3VcVLf/`
- **Setter:** $3,600 — `https://whop.com/checkout/plan_z5iuUhSgm9seH?d2c=true`

## Secondary Whop plans

**File:** `templates/HTSA-SECONDARY-PAYMENT-OPTIONS.md` — use **only** when CJ asks for secondary / other payment options. Do **not** swap into the main six silently.

### Closer (secondary)

| Offer | Total | Structure | URL |
| --- | --- | --- | --- |
| 2-Pay Action Taker | $6,000 | $3k down / $3k @ 30d | `https://whop.com/checkout/plan_oMi6XYvybZY4F?d2c=true` |
| 3-Pay | $6,600 | $2,200×3 | `https://whop.com/checkout/plan_YfsUaarlyP9e1?d2c=true` |
| PIF (experience / discount) | $5,000 | PIF | `https://whop.com/checkout/plan_gdThsrGLXqaDF?d2c=true` |

### Setter (secondary)

| Offer | Total | Structure | URL |
| --- | --- | --- | --- |
| 2-Pay | $3,000 | $1.5k down / $1.5k @ 30d | `https://whop.com/checkout/plan_nNnBopJ5NlBHU?d2c=true` |

## Secondary block UI

Inside `#invest-pay-zone`: `<hr class="invest-zone-rule">` + kicker (*Secondary payment options* / *Other payment options*). Duplicate primary `invest-option` / `invest-row` / `invest-price-big` / `invest-btn` markup; change only amounts, labels, and `href`.

## New invoice (minimal CJ input)

**Provide:** full name, email, phone (E.164 + display optional), **one row** from the table above.

**Instantiate** (from repo root; replace `0X` and placeholders):

```bash
python3 scripts/htsa-instantiate-invoice.py templates/htsa-placement-0X-….html \
  --full-name "FULL NAME" \
  --email "EMAIL" \
  --phone-e164 "+1XXXXXXXXXX" \
  --phone-display "+1 (XXX) XXX-XXXX"
```

Then **commit and push** the new `htsa-enrollment-{slug}.html` so GitHub Pages serves it.

**Live URL:** `https://closewithcjclay.com/htsa-enrollment-{slug}.html` (must be `htsa-enrollment-`, not `hts-enrollment-`).

## Cursor

- `@templates/HTSA-ENROLLMENT-PLACEMENT-NOTES.md` — this file + placement table.
- `@templates/HTSA-SECONDARY-PAYMENT-OPTIONS.md` — alternate Whop links only when CJ asks.
