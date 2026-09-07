# Special offer self-enroll — Claude sandbox build (v7 → v19)

**Paste into Notion** (also folded into `docs/PROSPECT-PAGE-VERSION-INDEX.md`).

**Sandbox root:** `/Users/charlesclay/Documents/SPECIAL-OFFER-CLAUDE-SANDBOX/WORK/`  
**Live target (when shipped):** `special-offer.html` on closewithcjclay.com  
**Baseline:** live Cursor collapsible-Parts build (`1788483600` / V6 era).  
**Rule:** each request = its own new version; prior never overwritten. **Nothing here is live** until you copy it into the repo. **Current preferred: v19.**

Hub: https://closewithcjclay.com/special-offer-history.html

| Ver | File (sandbox WORK/) | Preview | What changed |
|---|---|---|---|
| V7 | `special-offer-v7.html` | [Open](https://closewithcjclay.com/special-offer-claude-v7-preview.html) | Deleted Janaye. Part 2 90-day value stack + Part 3 return. Pricing before start. Option B rewrite. Date → Sept 6. |
| V8 | `special-offer-v8.html` | [Open](https://closewithcjclay.com/special-offer-claude-v8-preview.html) | Footer quote = pipe/plumber + 40/70 message. |
| V9 | `special-offer-v9.html` | [Open](https://closewithcjclay.com/special-offer-claude-v9-preview.html) | Dark buttons + footer → guarantee-box blue. Accordion: one Part open at a time. |
| V10 | `special-offer-v10.html` | [Open](https://closewithcjclay.com/special-offer-claude-v10-preview.html) | Each of 6 Part headers = blue band with white content beneath. |
| V11 | `special-offer-v11.html` | [Open](https://closewithcjclay.com/special-offer-claude-v11-preview.html) | Terms = in-place scrollable modal. Removed standalone Terms Part. Ends on Part 5 + referral. |
| V12 | `special-offer-v12.html` | [Open](https://closewithcjclay.com/special-offer-claude-v12-preview.html) | Part 5 = two green tabs (call CJ vs self-enroll). Self-enroll 4 steps, Amy style. |
| V13 | `special-offer-v13.html` | [Open](https://closewithcjclay.com/special-offer-claude-v13-preview.html) | Frictionless checkout to Whop. Guarantee/terms popup (Myli wording). Empty PDF iframe removed. |
| V14 | `special-offer-v14.html` | [Open](https://closewithcjclay.com/special-offer-claude-v14-preview.html) | Compact referral: your name + 3 name rows with Send. No big preview/thumbnail. |
| V15 | `special-offer-v15.html` | [Open](https://closewithcjclay.com/special-offer-claude-v15-preview.html) | Referral = blue Part 6 ($250–$500). CJ quote flipped to green. |
| V16 | `special-offer-v16.html` | [Open](https://closewithcjclay.com/special-offer-claude-v16-preview.html) | Closing quote = white editorial card, gold hairline, navy serif, centered. |
| V17 | `special-offer-v17.html` | [Open](https://closewithcjclay.com/special-offer-claude-v17-preview.html) | Closing kicker shortened to "One honest thought." |
| V18 | `special-offer-v18.html` | [Open](https://closewithcjclay.com/special-offer-claude-v18-preview.html) | Red 48h per-browser countdown. On expiry swap to standard pricing. Sept 6 copy → timer. |
| V19 **preferred** | `special-offer-v19.html` | [Open](https://closewithcjclay.com/special-offer-claude-v19-preview.html) | Intro: number at bottom, text or call immediately. PREFERRED Claude sandbox build. |

## Ship v19 (only when you ask)

```bash
cp "/Users/charlesclay/Documents/SPECIAL-OFFER-CLAUDE-SANDBOX/WORK/special-offer-v19.html" \
   "/Users/charlesclay/Desktop/closewithcjclay.com/closewithcjclay.com/special-offer.html"
```

Then: `git add special-offer.html && git commit && git push`.

## Notes

- Pricing in these builds = reactivation set ($5,000 PIF · 3×$1,750 · ClarityPay $500/mo). Countdown expiry swaps to standard ($6,000 · 4×$1,750 · $600/mo).
- 48h countdown is client-side (localStorage). Test expired: `localStorage.setItem('htsa_special_deadline_v1', Date.now()-1000)` then refresh, or `?offer=standard`.
