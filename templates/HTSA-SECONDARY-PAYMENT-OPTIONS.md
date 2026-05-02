# HTSA secondary payment options (Whop)

**This file is not part of the main six placement shells.** Use these checkout links **only** when CJ explicitly asks for **secondary / “other” payment options**, or gives an override like *“use the $5k PIF for experience”* *instead of* the default $6k PIF.

| Layer | What to use |
|--------|-------------|
| **Primary (default)** | Frozen templates `htsa-placement-01` … `06` — standard PIF / installment Whop URLs baked into those shells. |
| **Secondary (this doc)** | Alternate Whop plans below — **never** substitute here unless CJ names the offer or says to pull from **secondary payment options**. |

**UI rule:** When adding or swapping a secondary row on an invoice, **reuse the exact same structure and classes** as the primary options in that file: same `invest-option` / `invest-row` / `invest-price-big` / `invest-btn` pattern, spacing, and typography. **Only** change visible amounts, button label text, and `href` URLs — do not invent a new visual style.

All links below are **direct-to-consumer** where applicable (`?d2c=true`). The $5k PIF plan uses the same parameter for consistency with other checkouts.

---

## Closer — secondary Whop plans

| Offer (short name) | Total | Payment structure | Notes | Whop checkout URL |
|--------------------|-------|-------------------|-------|-------------------|
| **2-Pay (Action Taker)** | **$6,000** | $3,000 down — $3,000 due in 30 days | **“Action Taker Discount.”** Intended **on the call** unless CJ states otherwise. | `https://whop.com/checkout/plan_oMi6XYvybZY4F?d2c=true` |
| **3-Pay** | **$6,600** | $2,200/mo × 3 months (due every 30 days) | | `https://whop.com/checkout/plan_YfsUaarlyP9e1?d2c=true` |
| **PIF (experience / discount)** | **$5,000** | Paid in full | Reserved for **experience** or **discount** — **not** the default $6,000 PIF. | `https://whop.com/checkout/plan_gdThsrGLXqaDF?d2c=true` |

---

## Setter — secondary Whop plan

| Offer (short name) | Total | Payment structure | Notes | Whop checkout URL |
|--------------------|-------|-------------------|-------|-------------------|
| **2-Pay** | **$3,000** | $1,500 down — $1,500 due in 30 days | Secondary to default setter shells (e.g. $3k PIF / 3-pay). | `https://whop.com/checkout/plan_nNnBopJ5NlBHU?d2c=true` |

---

## Agent checklist (secondary)

1. **Confirm CJ intent** — e.g. “replace default closer PIF with $5k experience PIF” or “add secondary payment options block.”
2. **Keep primary vs secondary visually separate** — e.g. an `<hr class="invest-zone-rule">` plus a kicker such as `Secondary payment options` or `Other payment options (Whop)` using the same class as other section kickers (`invest-section-kicker` / `invest-section-kicker--accent` as in the template).
3. **Gate** — secondary Whop buttons must live **inside** `#invest-pay-zone` with class `invest-btn` so Terms lock/unlock still applies.
4. **Do not** overwrite this file with primary-template defaults; update this file only when CJ supplies **new** secondary plan URLs or pricing.

---

## File location

Repo path: **`templates/HTSA-SECONDARY-PAYMENT-OPTIONS.md`**

Referenced by: `.cursor/rules/htsa-enrollment-invoice-workflow.mdc`, `.cursor/skills/htsa-enrollment-invoice/SKILL.md`, `templates/README.md`.
