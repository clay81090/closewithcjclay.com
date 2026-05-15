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
- **03 / 04** — Source: `htsa-enrollment-trameil-lee.html`; **03** has financing stripped; Terms/hint = payment-only (not “financing”). **03** header `Payment:` and Prepared For `Payment:` use the **short Wayne line** (*Select payment option below*); no `Pricing:` row in billing. Whop/USD amounts stay **only** under Program Investment (`setter_cash_only` in `scripts/build-htsa-invoice-templates.py`).
- **05 / 06** — Jocelyn header + combined curriculum on Val shell; one Terms gate + one `#invest-pay-zone`; Closer invest-box then Setter invest-box; footer card title **Closer & Setter**; no PayVa.
- **Guarantee** — Orange block in all six; omit only if CJ says **no guarantee**.

## Live reference pages (visual / copy)

- **`htsa-enrollment-luz-gonzales.html`** — Production **Closer**, **cash + financing** stack done right: Whop PIF / 4-pay, **Splitit** under PIF, ClarityPay ($7,200) + Flexxbuy. Use when checking “full” closer financing UX (placement **02** is the frozen rebuild target).
- **`htsa-enrollment-wayne-wintermute.html`** — Canonical **header, hero, billing, member strip, footer** pull for template rebuilds. **No Splitit** on this live page (cash-only pay zone); for closer **without** Splitit use placement **01**.

## Six live demos (frozen layout, Jordan Example / fake contact)

After rebuilding shells, run `python3 scripts/rebuild-htsa-demo-enrollment-pages.py` and push. **`noindex`** — for previews and internal links, not SEO.

| # | URL |
|---|-----|
| 01 | `https://closewithcjclay.com/htsa-enrollment-demo-01-closer-cash-only.html` |
| 02 | `https://closewithcjclay.com/htsa-enrollment-demo-02-closer-cash-financing.html` |
| 03 | `https://closewithcjclay.com/htsa-enrollment-demo-03-setter-cash-only.html` |
| 04 | `https://closewithcjclay.com/htsa-enrollment-demo-04-setter-cash-financing.html` |
| 05 | `https://closewithcjclay.com/htsa-enrollment-demo-05-closer-setter-cash-only.html` |
| 06 | `https://closewithcjclay.com/htsa-enrollment-demo-06-closer-setter-cash-financing.html` |

**Real clients** keep their own `htsa-enrollment-{client}.html` URLs (e.g. Jocelyn). Demos are separate canonical-layout bookmarks.

## Rebuild frozen templates

From repo root:

```bash
python3 scripts/build-htsa-invoice-templates.py
```

Writes `htsa-placement-01`…`06`; removes legacy `htsa-tpl-*.html` if present. **Read-only** pull of Member voice strip + footer row from `htsa-enrollment-wayne-wintermute.html` (Wayne’s **live** file is not modified). Normalizes Mastermind copy to **520+** and Trustpilot line to **4.9 stars out of 5** on write. Then run **`python3 scripts/rebuild-htsa-demo-enrollment-pages.py`** to refresh the six **`htsa-enrollment-demo-*`** preview pages.

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
