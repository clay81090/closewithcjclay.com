# Claude Code handoff: CJ closer homebase + prescribed checkout

**Repo:** `/Users/charlesclay/closewithcjclay.com`  
**Live site:** https://closewithcjclay.com  
**Date:** 29 Sept 2026  
**Owner:** CJ Clay only. Do not send homebase URLs to prospects.

Paste this whole file into Claude Code. Build what is listed under **Build next**. Do not redesign what already works.

---

## Prompt for Claude Code (copy this first)

```text
You are working in the closewithcjclay.com GitHub Pages repo.

DO NOT change these live paths or their current UI:
- https://closewithcjclay.com/send-packs/  (four email/text copy cards + on-call checkout tiles)
- https://closewithcjclay.com/before-our-call/
- https://closewithcjclay.com/access/  (generic enroll portal; may still show payment cards until /agreement exists)
- Any existing htsa-enrollment-*.html client page unless CJ names that file
- r/_TEMPLATE-precall.html and live r/<slug>/ pages
- The four-card send pack copy, spacing, and Copy buttons

READ FIRST:
- .cursor/rules/htsa-page-map.mdc
- .cursor/rules/htsa-close-page.mdc
- docs/CLOSER-HOMEBASE-CLAUDE-CODE-HANDOFF.md (this file)
- templates/HTSA-SECONDARY-PAYMENT-OPTIONS.md
- scripts/htsa_close_copy.py
- scripts/htsa_precall_copy.py

BUILD:
1. New prospect walkthrough page at /agreement/ with NO payment grid (value, 30-day plan, guarantee, terms). Clone look from access/index.html but strip plans. Keep Miranda-style footer and in-page TOS like Sean/Natalia.
2. Optional: /access/?plan=pif|plan|clarity hides other cards and shows one prescribed option. Default /access/ can still show all options if they ask.
3. Keep /send-packs/ as the closer homebase. You may add features below the existing four cards. Do not restyle the four cards.
4. Never put Setter ClarityPay $300 (plan_z5iuUhSgm9seH) on a Closer page. Never put Closer ClarityPay $600 (1ba2LjGOo3B1Wpp4jf...) on a Setter page.

Voice: commas and periods. No dash-splattered copy. No "reactivation" in prospect-facing text.
```

---

## Yes, NotebookLM’s 3-step flow is possible

It matches how HTSA already thinks: prescribe one path, do not hand a menu.

| Step | What CJ does | What they see |
|------|----------------|---------------|
| 1 | Share screen or drop walkthrough URL | Value, game plan, guarantee, terms. **No price grid.** |
| 2 | Verbally prescribe one option | They hear one number, not four boxes |
| 3 | On **https://closewithcjclay.com/send-packs/** tap Closer or Setter, tap the plan, **Copy Zoom link**, paste in Zoom chat | One Whop checkout |

Colleague pattern: https://htsa.co/member-agreement (rep picks program, member gets one agreement). CJ’s version lives on closewithcjclay.com so he does not leave his site.

**Already live today (do not rip out):**

- Send packs: https://closewithcjclay.com/send-packs/
- Pre-call: https://closewithcjclay.com/before-our-call
- Enroll portal (still has payment cards): https://closewithcjclay.com/access
- 30-day plan: https://closewithcjclay.com/30-day-roadmap.html

**Not built yet (your job):** `/agreement/` no-price walkthrough. Optional `?plan=` on `/access/`.

---

## Do not touch

- Filenames and URLs of `/send-packs/`, `/access/`, `/before-our-call/`
- The four send-pack tiles (pre-call email, pre-call text, post-call email, post-call text) and their locked copy
- Existing client `htsa-enrollment-*.html` unless CJ names the person
- `templates/_TEMPLATE-close.html` layout/CSS beyond adding `?plan=` hiding if you implement it carefully
- Calendar URLs, TOS PDF, Apps Script endpoint, termsVersion

---

## Locked fail-safe copy (zero names)

Canonical code: `scripts/htsa_precall_copy.py`, `scripts/htsa_close_copy.py`.

### Pre-call email

Subject: `Before our call / HTSA pre-call page`  
Link: https://closewithcjclay.com/before-our-call  
Opens: `Hi,` then **Click Here to Review the Pre-Call Page**.

### Pre-call text

Opens: `Hey, looking forward to connecting on our call!`  
Same URL on its own line.

### Post-call email

Subject: `Your HTSA enrollment page is ready`  
Link: https://closewithcjclay.com/access  
Includes enrollment bonuses through **Thursday, October 1st at 8pm EST**. Remove bonus sentences after Oct 1 when CJ says so.  
After You Pay: Self-Enroll + 5 minute call with CJ.  
Closer line: moments of decision / step into position.

### Post-call text

Opens: `Hey, really enjoyed our call...`  
URL: https://closewithcjclay.com/access  
Bonuses line through Oct 1. Execute / halfway / moments of decision.

Do not put first names in these packs. Do not use real prospect names in examples. Use Test Person / test@example.com / +15555550100.

---

## Pricing truth (never mix Closer and Setter)

Source: `templates/_TEMPLATE-close.html`, placement shells, `templates/HTSA-SECONDARY-PAYMENT-OPTIONS.md`.

### Closer primary

| Label | Amount | Checkout |
|-------|--------|----------|
| PIF | $6,000 | https://whop.com/checkout/plan_hDgy1h7nsgiim?d2c=true |
| 4-pay | $1,750 today · $7,000 total | https://whop.com/checkout/plan_m6yk0QLbxWaak?d2c=true |
| ClarityPay | **$600/mo · $7,200 total · 0% APR · 620+** | https://whop.com/checkout/1ba2LjGOo3B1Wpp4jf-eF61-w5X4-yCzD-25zhqI3VcVLf/ |

### Setter primary

| Label | Amount | Checkout |
|-------|--------|----------|
| PIF | $3,000 | https://whop.com/checkout/plan_qzvfCCb1rIO0L?d2c=true |
| 3-pay | $1,050 today · $3,150 total | https://whop.com/checkout/plan_oK3AajTKp0mXK?d2c=true |
| ClarityPay | **$300/mo · $3,600 total** | https://whop.com/checkout/plan_z5iuUhSgm9seH?d2c=true |

**$300 / month ClarityPay is Setter only.** Never print it next to Closer $600.

### Closer, only if CJ named it

| Label | Checkout |
|-------|----------|
| Splitit $600/mo · $7,200 · 0% | https://whop.com/checkout/plan_LiZXezzaPMzUF |
| 2-pay Action Taker $6,000 | https://whop.com/checkout/plan_oMi6XYvybZY4F?d2c=true |
| 3-pay $2,200 · $6,600 | https://whop.com/checkout/plan_YfsUaarlyP9e1?d2c=true |
| PIF $5,000 promo | https://whop.com/checkout/plan_gdThsrGLXqaDF?d2c=true |
| Promo 3-pay $1,750 · $5,250 | https://whop.com/checkout/plan_YrqGOXMxGbOVa?d2c=true |
| Promo ClarityPay $500/mo · $6,000 | https://whop.com/checkout/plan_VUSDju20gTBCg/ |
| PIF remainder $4,250 | https://whop.com/checkout/6HGikz2DEePqj5xzLH-E8gN-27Xu-MqoH-038LDTsjAgF9/ |

### Setter extra

| Label | Checkout |
|-------|----------|
| 2-pay $1,500 + $1,500 | https://whop.com/checkout/plan_nNnBopJ5NlBHU?d2c=true |
| Flexxbuy | https://app.flexxbuy.com/high-ticket-sales-academy-llc/apply/ (request $3,500 on the app) |

**Do not invent a $500 deposit Whop URL.** There is no canonical deposit plan in this repo. If CJ wants one, he supplies the checkout first.

---

## Build next (in order)

### 1. `/agreement/` (new)

Folder: `agreement/index.html`  
Live: https://closewithcjclay.com/agreement/

Clone visual language from `access/index.html` (navy/green, 820px, CJ headshot, guarantee, After You Pay collapsed, in-page TOS, 30-day plan modal, Miranda footer).

**Remove:** all payment cards, Whop buttons, ClarityPay tiles, Splitit.

**Keep / add:** what they are getting, guarantee, curriculum modal, 30-day plan, terms, one line such as “CJ will send your prescribed checkout in Zoom chat.”

`noindex`. Not for ads. For Zoom screen share.

Do not delete `/access/`.

### 2. Optional `?plan=` on `/access/` only

If `?plan=pif` show only PIF. `plan` = 4-pay. `clarity` = Closer $600 checkout. Ignore unknown params (show all).

Setter `?plan=` only if you later add a setter generic portal. Default `/access/` is **Closer**.

### 3. Homebase stays `/send-packs/`

Already has:

- Four copy packs
- Closer / Setter toggle
- Copy Zoom link + Copy chat line + link
- Copy screen-share page → `/access/` until `/agreement/` exists

When `/agreement/` ships, change the screen-share copy target to `https://closewithcjclay.com/agreement/` in `send-packs/index.html` only. Keep `/access/` as the all-options enroll URL in the **post-call email/text**.

Suggested Zoom chat line (already in send-packs JS):

```text
I just dropped your direct checkout in the Zoom chat. Open that. It is [plan name]. I will stay right here with you.

[checkout URL]
```

### 4. After Oct 1

When CJ says so: remove bonus sentences from `htsa_close_copy.py`, send-packs post-call copy, `/access/` bonus section, and this doc.

---

## Terms (if you add agreement page)

- PDF: https://closewithcjclay.com/HTSA-Terms-of-Service.pdf
- `termsVersion`: `HTSA-TOS-PDF-closewithcjclay-2026-04`
- Apps Script: see `.cursor/rules/htsa-close-page.mdc` (recordTermsAgreement on checkout confirm, not a locked pay wall on the new walkthrough)

Walkthrough page: they can read TOS. Payment consent still happens on Whop / existing close-page confirm sheet.

---

## On-call script (for CJ, not for the page)

1. Bookmark https://closewithcjclay.com/send-packs/
2. Screen share `/agreement/` (or `/access/` until agreement exists)
3. Walk guarantee and 30-day plan
4. Prescribe: “We are doing Closer paid in full” / “Setter ClarityPay at $300 a month”
5. On send-packs: Closer or Setter → that tile → Copy Zoom link → paste in chat
6. Stay on the phone. Narrate Whop. Do not go quiet.
7. After they pay: send post-call email then text from the four cards (generic `/access` is still fine)

---

## Git / Pages

New files must be committed and pushed to `origin/main` or GitHub Pages 404s. Wait for HTTP 200 before telling CJ a URL is live.

---

## Files to open in Cursor

| File | Why |
|------|-----|
| `send-packs/index.html` | Homebase |
| `access/index.html` | Generic enroll |
| `templates/_TEMPLATE-close.html` | Close template |
| `scripts/htsa_close_copy.py` | Post-call copy |
| `scripts/htsa_precall_copy.py` | Pre-call copy |
| `templates/HTSA-SECONDARY-PAYMENT-OPTIONS.md` | Extra Whop plans |
| `.cursor/rules/htsa-page-map.mdc` | Four page types |
