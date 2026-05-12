# HTSA enrollment invoice — frozen HTML templates

Shells in `templates/` use **`noindex`** and **`{{HTSA_*}}` placeholders only** (no client names baked in). **Never edit** a deployed `htsa-enrollment-*.html` to create a new person — copy a shell, fill placeholders, save a **new** root file.

## Secondary Whop plans (not in the six shells)

Alternate checkouts (2-pay / 3-pay / $5k PIF closer, setter 2-pay) live in **`HTSA-SECONDARY-PAYMENT-OPTIONS.md`**. Use that file **only** when CJ asks for **secondary / other** payment options or a named override (e.g. **$5k PIF for experience**). Do **not** mix those URLs into the main six templates unless CJ instructs you to ship them on a specific invoice.

---

## CJ command → template file

| Column 1 (what CJ types) | Column 2 (frozen shell) |
|--------------------------|-------------------------|
| **Closer – Cash only** | `templates/htsa-placement-01-closer-cash-only.html` |
| **Closer – Cash + Financing** | `templates/htsa-placement-02-closer-cash-financing.html` |
| **Setter – Cash only** | `templates/htsa-placement-03-setter-cash-only.html` |
| **Setter – Cash + Financing** | `templates/htsa-placement-04-setter-cash-financing.html` |
| **Closer & Setter – Cash only** | `templates/htsa-placement-05-closer-setter-cash-only.html` |
| **Closer & Setter – Cash + Financing** | `templates/htsa-placement-06-closer-setter-cash-financing.html` |

## Defaults

| Topic | Rule |
|--------|------|
| **Orange guarantee** | **On** in every shell. Remove it **only** if CJ says *no guarantee*. |
| **PayVa** | **Never** in shells. Add **`snippets/payva-financing-block.html`** only when CJ says **PayVa**. |
| **Splitit** | **On** under **Closer** $6k PIF (including dual pages). **Not** on **Setter**. |
| **Layout** | Built from read-only **`htsa-enrollment-val-tappan.html`**, **`htsa-enrollment-thomas-rulof.html`**, **`htsa-enrollment-trameil-lee.html`**, and dual header/curriculum from **`htsa-enrollment-jocelyn-navarro.html`** (do not edit client files when regenerating). |

---

## Copy → paste → fill (Cursor Agent)

Replace **`FULL NAME`**, **`EMAIL`**, **`+1XXXXXXXXXX`** (E.164), and optional `--phone-display`.

**Example prompt:**  
`@htsa-enrollment-invoice NEW from templates/htsa-placement-01-closer-cash-only.html — FULL NAME — EMAIL — phone E.164 +1XXXXXXXXXX. Instantiate or replace {{HTSA_*}}. Grep for stray names. Push new HTML only. Return https://closewithcjclay.com/htsa-enrollment-{slug}.html`

---

## Instantiate (optional)

From repo root — swap the template path for the row you need:

```bash
python3 scripts/htsa-instantiate-invoice.py templates/htsa-placement-01-closer-cash-only.html \
  --full-name "FULL NAME" \
  --email "EMAIL" \
  --phone-e164 "+1XXXXXXXXXX" \
  --phone-display "+1 (XXX) XXX-XXXX"
```

Then **`git add` / `commit` / `push`** the new `htsa-enrollment-{slug}.html`.

---

## Placeholders (replace all before deploy)

| Token | Example |
|--------|--------|
| `{{HTSA_FULL_NAME}}` | Jane Doe |
| `{{HTSA_FIRST_NAME}}` | Jane |
| `{{HTSA_EMAIL}}` | jane@example.com |
| `{{HTSA_PHONE_E164}}` | +15551234567 (match `data-phone` and `tel:`) |
| `{{HTSA_PHONE_DISPLAY}}` | +1 (555) 123-4567 |
| `{{HTSA_CLIENT_SLUG}}` | jane-doe |
| `{{HTSA_STORAGE_KEY}}` | `hts_terms_gate_jane_doe_v1` |

---

## Live URL 404 after you “shipped”?

| Cause | What to do |
|-------|------------|
| File never **pushed** to **`origin/main`** | `git push origin main` — the site only serves what’s in the repo. |
| **Too soon** after push | Wait **1–5 minutes** for GitHub Pages, then try again. |
| Cached 404 in browser | **Hard-refresh** (⌘⇧R / Ctrl+Shift+R). |
| Wrong path | Must be **`htsa-enrollment-`…** (with **`a`** in **htsa**). |

Check from terminal (prints HTTP status code, want **200**):

```bash
sh scripts/check-enrollment-live.sh your-client-slug
```

---

## Regenerating from production HTML

From repo root:

```bash
python3 scripts/build-htsa-invoice-templates.py
```

| Output | Sources (read-only) |
|--------|---------------------|
| `htsa-placement-01-closer-cash-only.html` | `htsa-enrollment-val-tappan.html` |
| `htsa-placement-02-closer-cash-financing.html` | `htsa-enrollment-thomas-rulof.html` + **Splitit** under PIF; **Closer ClarityPay** → `$7,200` checkout `1ba2LjGOo3B1Wpp4jf-eF61-w5X4-yCzD-25zhqI3VcVLf` (**not** setter `plan_z5iuUhSgm9seH`) |
| `htsa-placement-03-setter-cash-only.html` | `htsa-enrollment-trameil-lee.html` (financing stripped) |
| `htsa-placement-04-setter-cash-financing.html` | `htsa-enrollment-trameil-lee.html` |
| `htsa-placement-05-closer-setter-cash-only.html` | Val + Trameil (cash) invest stacks; **Jocelyn** header/curriculum chunk |
| `htsa-placement-06-closer-setter-cash-financing.html` | Thomas+Splitit + Trameil (full); **Jocelyn** chunk; **no PayVa** |

Legacy `htsa-tpl-*.html` filenames are **removed** when you run the build script; use **`htsa-placement-*`** only.
