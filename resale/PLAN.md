# Resale plan (decided)

Build the phone website in this folder. Do not add pages, accounts, or a backend.

Public path after publish: `https://closewithcjclay.com/resale/`

CJ uses **Safari on his iPhone** and **Chrome on his computer**. Both must work. They do not share storage. Say that on the page.

## Files you may create or replace

- `resale/index.html` (replace the placeholder)
- `resale/styles.css`
- `resale/manifest.webmanifest`
- `resale/sw.js`
- `resale/icon.png` (a simple 180×180 PNG is enough)
- `resale/js/db.js`
- `resale/js/seed.js`
- `resale/js/camera.js`
- `resale/js/research.js`
- `resale/js/ui.js`
- `resale/BUILD_REPORT.md`

No other files. No npm. No framework. Plain HTML, CSS, and ES modules. Relative URLs so the folder works on GitHub Pages.

## What the page is

A camera-first catalog. He shoots items, they save immediately in that order, and later one button fills in prices for the ones that do not have prices yet.

Two browsers, one rule: the database is IndexedDB in **this** browser. Safari on the phone and Chrome on the computer each get their own copy. The original 31 items load in both from `seed/`. Photos he takes afterward stay on that browser until he uses **Export backup** and **Import backup**.

Show a small line on the camera screen: `Saved on this browser`.

## First launch

Import `seed/CJ_Collection_Inventory.json` once. Marker key: `seedImported = 2026-10-11-v1`. If that marker exists, do not import again.

- Keep IDs `CJ-001` through `CJ-031`. Never renumber them.
- 31 items. 29 have a low price. 2 are pending: `CJ-004` and `CJ-005`. Pending stays blank, not zero.
- Gross total of the 29 priced items is **$510.25–$1,155**. Label it `October 11, 2026 estimate`. Leave pending items out of the total.
- Load each `Photo` and `Additional photos` file from `seed/upload/`.
- `seed/photo_manifest.json` is the photo map. One photo may belong to two items. `CJ-016` and `CJ-017` share `IMG_90CE19D3-F5DD-4536-AD43-2BE5619D4949.jpeg`. Keep both items.
- The five `unassigned_originals` are not inventory items. Do not show them in the catalog or the total.
- Copy prices, sources, evidence, condition, quantity, category, and next step onto the item. Those imported prices are already done. The research button must skip them unless he taps **Refresh price** on that item.

## Save shape (IndexedDB)

Database name: `cj-resale`.

`items`

- `id` string, stable (`CJ-001`, then `CJ-032` upward)
- `captureOrder` number. Sort by this. Research never reorders.
- `createdAt` ISO time
- User fields, blank allowed: `name`, `category`, `itemDate`, `serial`, `notes`, `storageLocation`
- Machine fields, separate: `suggestedName`, `suggestedCategory`, `identityConfidence`
- A later machine result must not overwrite a user field that is non-empty.
- `starred` boolean, `starReason` string
- `priority` one of `high`, `medium`, `low`, `bundle`, or empty for auto
- `priorityTouched` boolean. If true, do not auto-change priority.
- `tested` one of `untested`, `tested`, or empty
- `pricingStatus` one of `saved`, `priced`, `needs_photo`, `failed`
- `lowUsd`, `highUsd`, `askUsd` numbers or null
- `evidence`, `nextStep`, `condition`, `quantity`, `year`, `description`
- `saleStatus` default `Unlisted`

`photos`

- `id`, `itemId`, `order`, `checksum`, `createdAt`, `blob`

`comps`

- `id`, `itemId`, `url`, `site`, `kind` (`sold`, `auction`, `ask`, `guide`, `appraisal`), `amount`, `note`, `seenAt`

`settings`

- `apiKey` (never written to a file)
- `feePercent` default `13`
- `shippingUsd` default `5`
- `haikuModel` default `claude-haiku-4-5`
- `sonnetModel` default `claude-sonnet-4-6`
- `seedImported`
- `nextNumber` (32 after a fresh import)

`jobs`

- one active batch: item ids, started time, per-item state

## Camera

No form before the next photo. Optional details stay behind a closed **Details** control: name, category, item date, serial, note, where it is stored.

### iPhone Safari

The main control is a big **Take photo** button. It opens `<input type="file" accept="image/*" capture="environment">`, which opens the iPhone camera. This is the path that must work. A live in-page camera is optional and only if `getUserMedia` succeeds on that phone. If it fails, hide it and keep **Take photo**.

After a shot, two big buttons:

- **Another photo of this** — next picture attaches to the same item
- **Next item** — next picture starts a new ID

Remember which one he tapped. Do not pop the keyboard.

### Desktop Chrome

Show a live webcam preview with `getUserMedia` and a shutter that saves the frame. Also show **Choose photos**. That picker allows many files. Dropping photos on the page works the same way.

Chosen files become items in the order selected, one item each, unless **Another photo of this** is the active mode. Then they all attach to the current item, in order.

If the webcam is blocked, the page still works through **Choose photos**. Say `Camera permission is off. You can still add photos.`

### Both

- Write the blob and the item row to IndexedDB before showing `Saved`.
- A reload keeps them, same order, still unpriced.
- Same checksum on the same item does not add a second photo.
- Same checksum as another item does not delete anything. Leave both. He can merge later from the item screen: **Same item** moves photos onto the earlier item and keeps the earlier ID. **Different item** leaves them. Do not block the camera for this.
- New IDs continue at `CJ-032` using `nextNumber`.
- Status text until research: `Saved, price not looked up yet`.

Show a tray of this session's new items in capture order: thumbnail, photo count, status.

## Find resale prices

One button: **Find resale prices**. It prices items whose `pricingStatus` is `saved` or `failed`, in `captureOrder`. It does not price `priced` items and it does not price imported items that already have a low or a pending-identification status from the seed (`CJ-004`, `CJ-005` stay pending until **Refresh price**).

Second tap while a job is running does not start another job. It shows the same progress.

**Price this item** and **Refresh price** exist on the item screen. Refresh is the only rerun for an item that already has a result.

If there is no API key, the button opens Settings and says `Add your Anthropic key to look up prices. Your photos stay saved.`

### API call

From the browser:

```
POST https://api.anthropic.com/v1/messages
x-api-key: (the key from IndexedDB)
anthropic-version: 2023-06-01
anthropic-dangerous-direct-browser-access: true
content-type: application/json
```

Never put the key in source, HTML, or the service worker.

Identification and ordinary pricing use `settings.haikuModel`. If the item is starred or identity confidence is under 0.5, use `settings.sonnetModel` for that item only.

Downscale each sent image to 1024 px on the long side with a canvas. Keep the original blob.

Send at most 8 items per request. All photos of one item go in that item's group. Label each image with the item id.

Include the matching section of `memory/sites.md` in the prompt (bundle the file text into `js/sites.js` as a string copied at build time, so the phone is not blocked by a missing fetch). Tell the model to check those sites first.

Ask for JSON only:

```json
{
  "items": [
    {
      "id": "CJ-032",
      "name": "",
      "category": "",
      "confidence": 0,
      "needsPhoto": "",
      "star": false,
      "starReason": "",
      "low": null,
      "high": null,
      "ask": null,
      "comps": [
        { "url": "", "site": "", "kind": "sold", "amount": 0, "note": "" }
      ],
      "evidence": "",
      "nextStep": ""
    }
  ]
}
```

Rules for accepting that JSON:

- If `needsPhoto` is non-empty, set `pricingStatus` to `needs_photo`, leave prices null, and show that sentence on the item.
- If there is no comp with a real `http` URL, leave prices null. Do not fill a number the model merely guessed.
- `kind` must stay `sold`, `auction`, `ask`, `guide`, or `appraisal`. An ask, guide, or appraisal cannot be the only support for a tight range. Show it, and label it with those words.
- Store every accepted comp. Do not delete older comps on refresh. Mark the newest run.
- One item's error does not stop the rest. That item becomes `failed` with the error text.
- If the API says the model id is unknown, show the error on the row. Do not loop forever. He can change the model id in Settings.
- Also request the server web search tool (`web_search_20250305`, name `web_search`). If that tool is rejected, continue without it and build **Open search** links instead (below). Still do not invent prices.

Comparison rules from the seed, keep them in the prompt:

- Souvenir medal is not precious-metal or flown metal.
- Untested loose watch is not a sealed working boxed watch.
- Base card is not a rare parallel.
- Box only is not the complete product.
- Gold plate is not solid gold.

### Open search links

When a price is still empty, show buttons built from the category in `memory/sites.md`. At minimum, for every item, an eBay sold search URL using the item name:

`https://www.ebay.com/sch/i.html?_nkw=ENCODED&LH_Sold=1&LH_Complete=1`

Plus the category's first site if a search URL is obvious (Numista, SportsCardsPro). These links open in a new tab. They are not prices.

## Star

Auto-star, and still let him tap the star, when any of these are true:

- category is jewelry and no metal mark is mentioned
- notes or model text suggest a key-date coin, a better-grade note, a diamond, or precious metal
- a sealed or boxed collectible whose high is more than twice the low and the high is over 75
- `needsPhoto` mentions a mark, caseback, mint mark, or whether the bottle is inside

Star does not remove the item. Filter name: **Look closer**.

## Sell priority

Auto, unless `priorityTouched` is true:

- `bundle` when `highUsd` is under 8
- `high` when `askUsd` is 40 or more
- `medium` when `askUsd` is 15 or more
- `low` otherwise
- leave priority empty when there is no price yet

He can set High, Medium, Low, or Bundle with one tap. That sets `priorityTouched`.

Show **You might clear** as `(low - shipping)` and `(high - shipping)` after subtracting `feePercent`, floored at 0. Label it `Guess after fees`.

On a watch, lighter, or item whose category contains `Watch` or `lighter`, show **Untested / Tested**. Untested lowers the displayed ask by 20 percent for the label only, and says `Untested`. Do not change the stored comp amounts.

## Item screen

All photos, range, ask, each comp with its kind and link, evidence, next step, star, priority, tested, details fields, listing blurb, **Refresh price**.

Listing blurb: a one-line title plus three short condition lines he can copy. Mention untested, opened, or box-only when the record says that. No hype.

## List screen

Search box matches name, id, category, serial, notes.

Filters: All, Look closer, High, Medium, Low, Bundle, Needs a better photo, Ready to list.

Ready to list means priced, not starred, and priority is high or medium.

Totals on the list: gross low–high of items that have both prices. Text: `Gross estimate, not money in hand.`

## Settings

- API key field, saved only in IndexedDB. Password-style input.
- Fee percent and shipping.
- Haiku model id and Sonnet model id.
- **Export backup** downloads one JSON file: items, comps, and photos as base64, plus the settings except the API key. Also use `navigator.share` when Safari has it, so he can AirDrop it to the computer.
- **Import backup** reads that JSON, replaces this browser's items and photos, and does not import an API key.
- Explain in one sentence: `Chrome on your computer and Safari on your phone keep separate catalogs. Export on one, import on the other.`

## Look and controls

- Phone: camera fills the screen. Tray sits under the buttons. Type at least 16px. Tap targets at least 44px. No sideways scroll at 320px wide.
- Computer: camera column and list column side by side once the window is 900px or wider.
- White list, black text, one green **Find resale prices** button. The camera area can be black.
- This is not an HTSA enrollment page. Do not copy those layouts, logos, or sales sentences.
- Add to Home Screen: manifest name `Resale`, `apple-touch-icon` pointing at `icon.png`.
- Service worker caches only the app shell files (html, css, js, icon, manifest). Do not cache API calls. Do not cache `seed/` photos forever. Network first for `index.html`.

## Acceptance checks you must run

Use Chrome if it is available, or a local static server from the repo root (`python3 -m http.server`) and say you could not open Safari on a phone.

1. Reload logic: after import, 31 items, pending CJ-004 and CJ-005, priced gross `$510.25–$1,155`.
2. The five unassigned originals are not items.
3. CJ-016 and CJ-017 both exist and can share the one photo.
4. A second page load does not duplicate the 31.
5. With no key, **Find resale prices** asks for the key and does not write prices.
6. Buttons and type fit at 390px wide and at 1200px wide. No horizontal scroll.
7. `git status` shows changes only under `resale/`, and you did not change the guardrail files or `seed/`.

Write what you actually did in `resale/BUILD_REPORT.md`.
