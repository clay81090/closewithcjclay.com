---
name: htsa-enrollment-invoice
description: >-
  Builds a new live HTSA enrollment invoice HTML by copying a vetted
  "gold" template in the closewithcjclay.com repo, then personalizing
  name, email, and phone. Use when the user asks for an
  htsa-enrollment page, HTSA invoice, personalized enrollment link, or
  pastes name/email/phone with Closer, Setter, financing, or guarantee
  options.
---

# HTSA enrollment invoice (new client page)

## Goal

Ship a new **`htsa-enrollment-firstname-lastname.html`** in the **repo root** that matches an existing, proven page—**only** the new client’s details change. **Live pages stay untouched:** never overwrite another person’s file.

## Safety rules (non-negotiable)

1. **Do not** open an old client’s file and "Save" over it, and **do not** search-replace across the whole project.
2. **Do** start from a **gold template** file (read it if needed, then work only on a **new** path).
3. **Do** use a **new filename** for every new person: all lowercase, hyphens, e.g. `htsa-enrollment-daler-achilov.html`.
4. **Do not** add "3 one-on-one sessions with Chad" unless the user **explicitly** asks in this chat.

## What to ask the user (or use if they already pasted it)

- Full name, email, phone (from HubSpot is fine)
- **Program:** `Closer only` / `Setter only` / `Closer & Setter`
- **Financing:** `Yes` (include Pre-Qualify / external financing options as in the gold file) or `No` (cash / in-house Whop options only—see template)
- **Orange performance-guarantee block:** `Yes` or `No` (if Yes, the gold file must already include the orange banner; or copy the banner block from a page that has it)
- **Slug:** `firstname-lastname` from their name (lowercase, ASCII-ish; same style as your other `htsa-enrollment-*.html` files)

## Pick the gold template (read this file, then copy—never edit the original)

| User wants | Copy from (source of truth) |
|------------|-----------------------------|
| **Closer & Setter** (dual program / pricing) | `htsa-enrollment-jocelyn-navarro.html` |
| **Closer, cash / in-house only** (PIF, 4-pay, Splitit; **no** ClarityPay/PayVa/Flexxbuy lines). Orange guarantee optional; Timi’s file **includes** the orange box | `htsa-enrollment-timi-bonner-mccourt.html` |
| **Closer, curriculum wording check** (should match your standard closer copy) | `htsa-enrollment-amy-grochala.html` |
| **Setter, curriculum + setter investment stack** | `htsa-enrollment-kaitlyn-hall.html` |
| Orange guarantee **wording/position** reference | `htsa-enrollment-erick-brower.html` (or use Timi if the whole closer+cash+guarantee package is the goal) |

**Setter vs Closer vs both:** the curriculum and investment sections **must** match the product they bought—use the right gold file so you do not mix setter and closer pricing.

## How to create the file (implementation)

**Preferred (safest, reproducible):** duplicate on disk, then edit **only** the new file.

```bash
cd /path/to/closewithcjclay.com
cp htsa-enrollment-GOLD-PICKED.html htsa-enrollment-firstname-lastname.html
```

Then search/replace **only** inside `htsa-enrollment-firstname-lastname.html`.

**In Cursor without terminal:** the assistant may **read** the whole gold template and **write** a new file to the new path with the same content, then apply edits. That is still safe for the old file (original stays unchanged) but uses more context—terminal `cp` is leaner if available.

## Fields to change in the new file (only these patterns)

- `<title>HTSA Invoice — {Full Name}</title>`
- Hero paragraph: `"{FirstName}, I really enjoyed…"`
- `billing-name` + `mailto:` + visible email + `tel:` (digits in `href`, human format on screen)
- Any step that says the first name (e.g. "pick $6,000…")
- "Welcome to the HTSA Family, {FirstName}."
- Run a quick check: `grep` the **old** example name in the new file and confirm **zero** hits (except false positives in long base64 strings)

## After the file exists

- **Default:** do **not** `git add` / `commit` / `push` **unless the user explicitly asks** to publish.
- **Public URL (when the file is on `main` and hosting serves the root):**  
  `https://closewithcjclay.com/htsa-enrollment-firstname-lastname.html`

## Related project rule

- Facebook Mastermind line: use **490+ members** (see `htsa-mastermind-member-count.mdc` in `.cursor/rules/` if present).

## Agent mode vs regular chat (for CJ)

- **Agent mode (Composer / Agent with tools):** best when you want the model to run **`cp`**, edit the **new** file, run **`grep`** to verify, and (if you say so) **git push**—one thread, few mistakes, fast. **This is the recommended way** when you are on a live sales call.
- **Regular ask/chat without tools:** the model can still **tell you the exact `cp` command** and the **exact** find/replace list, or output a full file—but you or Agent mode must apply it. If something must not touch the gold files, say: *"Create only `htsa-enrollment-…` — do not modify Timi or Jocelyn."*

## One-line trigger you can paste in chat

```text
@htsa-enrollment-invoice  New HTSA invoice:
Name:
Email:
Phone:
Program: Closer | Setter | Closer & Setter
Financing: Yes | No
Orange guarantee: Yes | No
Push to GitHub: Yes | No
```

(Adjust `@` mention if your Cursor build lists this skill under a different name in the @ menu.)
