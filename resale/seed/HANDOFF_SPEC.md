# CJ Collection Inventory: Cursor Handoff

## Goal

Build a phone-first inventory app for CJ's collectibles and antiques. The primary action should be **take a photo, identify the object, check the existing collection for a duplicate, research likely resale value, and save a new item only when it is genuinely distinct**. The app must preserve its database across sessions and avoid redoing identification/research for previously cataloged items. It should be straightforward enough to use one-handed while sorting a collection.

This document is the handoff from the existing ChatGPT workflow. It includes the current inventory snapshot, source/evaluation method, product requirements, and the complete existing static HTML export at the end. Treat the inventory records below as the current source-of-truth snapshot; the embedded HTML is a generated/exported view, not a database backend.

## Latest confirmed camera and batch requirements

### Main experience

Build a mobile app for CJ with a prominent **Camera / Add item** button. CJ can keep photographing a collection and research prices later with one bulk action. Saving, categorizing, and pricing are separate operations. No Enter key, price search, or completed form is required to retain a photo.

1. Tap Camera and take a photo. Save the image and a capture record immediately.
2. Start inexpensive background visual classification/OCR automatically. Suggest category, short name, visible maker/model/date/serial, and identification confidence. This happens without a pricing request.
3. Keep the camera flow available while classification runs. Provide **Add another photo to this item** and **Next item** actions. Back/front/packaging/marking photos can belong to one product, with one record and one valuation.
4. Show an optional, collapsed **Details** panel: name, category, item date, serial number, and notes. CJ may enter any, all, or none of these fields. Do not require a form, confirmation, or typed name to continue. Automatically record capture time separately from the optional item date.
5. Show a saved-items tray with thumbnails, photo counts, category/identification progress, and pricing status. Metadata can be edited later, photos regrouped, and items searched by category, name, serial, or note.
6. Provide **Research unpriced items** and **Research selected items**. One tap launches a persistent batch; report per-item progress and the updated priced total. CJ can keep capturing during the job or leave and return.

### Capture, categorization, and optional metadata

- Commit the original photo/blob and capture UUID to IndexedDB before showing **Saved on this device**. Do not keep images only in component state or memory. Generate a small preview separately; preserve readable markings in the original.
- Upload originals and record changes in the background. Show **Synced** only after durable server storage confirms both image and metadata. A cloud backup is not complete merely because an upload request began.
- Each photo has an immutable UUID, checksum, item/capture association, capture time, optional view label, storage path, and sync state. Each item has a stable UUID independent of editable name/category. Preserve existing CJ-001 through CJ-031 identifiers on import; never renumber existing items.
- Automatically categorize online without a pricing click. If offline, permission is denied, storage is full, or the classification service fails, retain every successfully saved image, display the reason, and queue classification for retry. Use **Uncategorized — classification pending** while identification is unavailable; never invent a category to hide an error. Allow manual category entry at any time.
- Preserve machine suggestions separately from user overrides. A later model response must not erase CJ's name, date, category, serial number, or note. Blank optional values remain null/blank, not zero or fabricated facts.
- Item date is optional and may be a purchase/acquisition/date-of-item field selected by the user. Capture time is automatic. Unknown manufacture year/era remains unconfirmed. An OCR serial is a suggestion until legible enough or user-confirmed.
- Grouping is explicit: **Add photo** retains the current item's UUID; **Next item** starts a new capture UUID. Do not assume consecutive photos always represent separate items or always represent the same item. Multi-select imports need a grouping control, with optional regrouping later.
- Handle browser refresh, app restart, camera cancellation, upload failures, and intermittent connection without losing committed captures. Add understandable retry states and storage-error feedback.

### Duplicate policy and counts

- Save captures immediately even if a potential duplicate is detected. Do not create a second confirmed inventory item solely because another photo was taken.
- Compare exact photo checksums, previous item/capture IDs, visible serial/model/marks, and image similarity. Similar appearance alone cannot prove two physical objects are the same.
- A photo added within an existing item's capture group appends to that item. An exact duplicate upload must not add a duplicate photo or item by default.
- For clear matches, attach the new view to the existing item and retain its valuations/history. Ambiguous matches stay saved in a possible-duplicate queue with **Same item / Different physical item / Decide later** actions. Do not block further camera use.
- Different physical watches, cards, colors, serial numbers, or product editions can be separate entries. Imported lots/sets remain their existing quantity/group unless CJ splits them explicitly.
- Display captured groups, confirmed inventory entries, possible duplicates, priced entries, and unpriced entries separately. Exclude possible duplicates and unpriced items from value totals. Never count multiple photos as multiple products.

### Batch pricing behavior

- Research only on an explicit **Research unpriced items**, **Research selected items**, or **Refresh price** action. Automatic classification must not automatically launch paid marketplace searches.
- A batch records selected stable item IDs, the relevant photo/identity revision, requested time, progress, and each item's result/error. Jobs run server-side and persist across navigation/restarts; the UI polls or subscribes to status.
- Before pricing, use existing classification/metadata and duplicate decisions. If identification is insufficient, mark that item **Needs identification** and continue with other items. Show the specific missing mark/photo needed.
- Use the already recorded comps and research for imported records unless CJ requests refresh or new evidence materially changes the item. Cached results are tied to item/identity revision and review time. Never replay this whole chat to value one item.
- Use a configurable small vision model for OCR/classification, batch independent items when practical, and reserve more expensive analysis for ambiguous or potentially valuable pieces. Preserve per-item image grouping in all calls. Keep cost/request/token records available in settings without cluttering the capture flow.
- Enqueue with idempotency keys. Repeated taps must reuse the same active job; retries resume incomplete work and cannot duplicate inventory rows, valuations, or charges for already-completed steps when avoidable.
- Limit concurrency, cap per-batch spending, and make cancel/resume explicit. Canceling research preserves captured items/photos. A failing source/item must not cancel or silently disappear from the rest of the batch.
- Store category confidence, identity confidence, and pricing confidence separately. A confidently identified common card can have thin price evidence.
- Separate estimated likely resale range, suggested listing ask, and actual sale proceeds. Record source URL, source type (sold/auction/active ask/guide), observed amount, sale/review date when visible, condition match, and any hidden Best Offer amount. Pending values are excluded from totals. Keep price history rather than overwriting it.
- Use the existing handoff's category-specific comparison rules. Do not compare souvenir medals with flown precious-metal medals, a loose untested watch with a sealed working boxed watch, a base card with a rare parallel, or a box-only item with a complete product.

### Suggested implementation contracts

These are internal app contracts to implement, not claims that an external marketplace already supplies these endpoints.

- `POST /captures`: durable capture/group record with client UUID and idempotency key; blank optional fields accepted.
- `POST /captures/:id/photos`: add another view to the same group; signed upload workflow if needed.
- `PATCH /items/:id`: apply explicit user edits and preserve suggestion/valuation history.
- `POST /classify`: automatic queued classification/OCR for new or meaningfully changed photos, independent of pricing.
- `POST /research-batches`: selected item UUIDs, `only_unpriced` or explicit `force_refresh`, idempotency key, spending limit.
- `GET /research-batches/:id`: persistent per-item progress/errors/results.
- `POST /duplicate-decisions`: merge/attach or keep separate, with an auditable decision and transaction.
- Keep API keys/server credentials on the server. Use working, permitted search/APIs and clearly disclose unavailable sources; do not fake web research or sold data.

Suggested tables: `items`, `capture_groups`, `photos`, `classification_results`, `user_overrides`, `research_batches`, `research_jobs`, `valuations`, `comps`, `possible_duplicates`, and `transactions`. Statuses should be independent: capture sync state, classification state, duplicate state, and pricing state. A synced, categorized item can remain unpriced indefinitely.

### Build order for Cursor

1. Import the supplied 31-item JSON snapshot, stable identifiers, all CSV fields, and grouped photo references. Verify counts and total before introducing AI.
2. Implement mobile camera capture, local persistence, optional details, multi-photo item groups, and camera/next-item loop.
3. Implement background sync and classification with real configurable service integration and visible failures. Support manual metadata when classification is unavailable.
4. Implement duplicate review and cache reuse.
5. Implement persistent batch research, price evidence, per-item errors, and gross totals.
6. Add filtering, CSV/JSON/HTML exports, backups, and history. The HTML export is a view; the app database is authoritative after import.

### Acceptance checks

- Take 10 photos for 10 different items without typing or pressing Enter: every photo survives refresh, becomes a saved capture, and categorization starts automatically online. None has pricing research launched yet.
- Capture one watch's back, front, and box with **Add photo**: one product, three photos, one valuation. **Next item** starts a separate group.
- Leave name/date/category/serial/notes blank: capture, sync, and later batch pricing still work. Entering one optional field never makes others required.
- Edit the category/note while classification is running: background results must not overwrite the edit.
- Capture offline, close/reopen the app, then reconnect: images/groups remain and resume classification/sync; pending category is visibly honest.
- Fail one upload/classification/source: keep the capture and report its issue; other captures/jobs continue. Do not show Synced or Priced for a failed operation.
- Research all unpriced items with one click and navigate away: the server job continues and results/progress are available later. Repeated taps do not launch duplicate jobs.
- Run the same completed batch again without refresh: reuse current results rather than repeat equivalent paid work.
- A suspected duplicate stays saved for review and does not increase the confirmed value total. Different physical variants can be kept separately.
- Import all 31 entries with 29 priced and 2 pending; priced gross total is $510.25–$1,155. This is a historical estimate snapshot, not a guaranteed return or a fresh market appraisal.
- CSV export includes the union of every field across records, including additional photo references, and preserves empty values, commas, quotes, Unicode, and line breaks.

## Product Requirements

### Mobile capture flow

1. Camera capture saves each photo/group immediately without Enter, pricing, or required manual fields.
2. Automatic inexpensive classification/OCR starts independently of pricing. Save offline captures and categorize when the service is available; show pending status honestly.
3. Optional name, category, item date, serial number, and note fields can stay blank. Preserve user overrides.
4. **Add photo to this item** groups views; **Next item** starts another group. Keep capturing while prior classifications run.
5. Check duplicate evidence in the background. Keep ambiguous captures saved for review without adding a duplicate confirmed item or value.
6. One **Research unpriced items** or **Research selected items** action starts persistent batch pricing. Reuse existing research until an explicit refresh or material identity change.
7. Save data/photos locally and sync to durable server storage with distinct Saved/Synced indicators.
8. Follow the full confirmed specification above, including independent states, idempotency, optional metadata, retry, and acceptance checks.

### Inventory/search views

- Search/filter by category, item, ID, maker/model, year, material, status, and price range.
- Item detail: all photos, description, condition, purchase cost if known, price range, suggested ask, actual sale, fees/shipping, net proceeds if known, date added/reviewed, source links, confidence, notes, storage location, and next steps.
- Duplicate review queue and items needing better photos/identification/pricing.
- Export CSV and a printable/shareable HTML report. Keep portable backups (CSV + JSON with photo references or archive).
- Display totals as **gross estimates** and exclude pending items; do not imply that asking prices are sale proceeds.
- Support offline capture drafts and sync/retry when connection returns.

### Cost-conscious AI/research design

- Use a small/low-cost vision model for initial labeling and OCR; ask for only structured fields and visible evidence. Use deterministic duplicate checks before calling a model or search provider.
- Batch independent items in a single request when practical, but keep multiple photos of one item grouped together. Do not make a separate expensive call for each angle. Use a stronger model only for ambiguous/high-value candidates or a user-requested second opinion.
- Cache results by item/photo fingerprint and query; do not repeat identical searches unless the user requests a refresh or the last review is stale. Store search date and sources.
- Separate image understanding from live-market research. Research only after initial identification and duplicate review. Avoid sending personal information in photos; crop to the object where possible.
- Do not claim that the app can search all marketplaces unless it has a permitted, working data source/API. Use official APIs or compliant search interfaces; otherwise open cited search links for human review. Do not scrape sites against their terms.

## Current Data Snapshot

As of October 11, 2026: 31 inventory entries, 29 with price ranges and 2 pending valuation. Priced gross resale estimate: **$510.25–$1,155**, before shipping, fees, taxes, repair costs, or buyer offers. This is not a guaranteed sale total. Elvis decanter prices vary widely by exact series, original case, bottle seal/fill, and working music box; appraisals and auction results differ substantially.

| ID | Item | Current estimate | Status / duplicate note |
|---|---|---:|---|
| CJ-001 | Hygrade Baseball's All-Time Greats, 50-card set | $15–$25 | Count and condition need confirmation |
| CJ-002 | 1991 Score Larry Sheets #176 | $0.50–$2 | Low-value single; consider bundling |
| CJ-003 | RAG-branded boxed pen and round accessory | $10–$30 | Accessory function/maker unknown |
| CJ-004 | "All the Children of the World" medallion / possible trinket-box lid | Pending | Need base, dimensions, edge marks, material |
| CJ-005 | Three-flower pendant necklace | Pending | Need back/clasp/hallmarks/material |
| CJ-006 | Ronald McDonald analog child's watch, red band, loose/display case | $10–$25 | Separate physical watch from carded digital watches below |
| CJ-007 | Oleg Cassini quartz watch, diamond accent, box/tag | $25–$50 | Running status/model number unknown |
| CJ-008 | Kaywoodie V.I.P. piezo butane lighter, boxed | $20–$40 | Untested; exact model sold comp not confirmed |
| CJ-009 | Waltham boxed ladies watch/bracelet-watch set | $10–$25 | Object type and running status unclear |
| CJ-010 | Shriners scimitar/crescent metal case or plaque, boxed | $15–$30 | Function, maker, metal unknown |
| CJ-011 | Monticello "Button" Jewelry / Jefferson-tradition necklace, 24K gold plate on brass | $15–$30 | **This is the Jefferson necklace already added.** Do not add another for the same necklace. |
| CJ-012 | 1987 U.S. Constitution Bicentennial commemorative diamond knife | $20–$30 | Box says layered in 24K gold; not solid gold |
| CJ-013 | U.S. 3-cent Washington stamp booklet, stated 24 stamps | $15–$35 | Verify Scott number, completeness, gum/condition |
| CJ-014 | U.S. coin folder lot: Liberty/Jefferson/Buffalo nickels, Mercury dimes, partial cents, book | $20–$80 | **Best upside candidate; inspect every date/mintmark before selling as a lot** |
| CJ-015 | Laino's boxed pen and pencil set | $10–$25 | Test and inspect maker/material marks |
| CJ-016 | Official Ronald McDonald Watch, black band, carded package | $15–$30 | Carded digital promo watch; untested |
| CJ-017 | Official Ronald McDonald Watch, red band, carded package | $15–$30 | **Distinct from CJ-016 by band/color; keep separate.** |
| CJ-018 | Elvis Silver Anniversary musical decanter with matching presentation case | $70–$175 | Higher-value vintage collectible; verify music-box function and factory seal |
| CJ-019 | McCormick Elvis full-figure bourbon decanter in blue/white box | $60–$100 | A close matching full-figure/blue-box example sold for $65 with working music box |
| CJ-020 | McCormick Elvis 1977 bust bourbon decanter, limited edition | $35–$70 | Comparable empty boxed example sold for $34.95; condition/fill affect value |
| CJ-021 | Three-magazine lot: 1945 Life, 1976 Saturday Evening Post, D-Day 60th anniversary Life | $8–$20 | Low-confidence lot estimate; inspect completeness and condition |
| CJ-022 | McCormick Elvis “A Second in a Series” red/white package | $45–$95 | Estimate assumes the decanter is inside; box-only value about $10–$20 |
| CJ-023 | 1981 Kennedy Space Center Columbia STS-1 bronze medallion, carded | $8–$15 | Exact design sold for $11.99; souvenir medal, not flown silver |
| CJ-024 | 1928A $2 U.S. Legal Tender note, red seal | $10–$30 | One note shown front/back; circulated; verify series and grade |
| CJ-025 | 1969 Bahamas 25 cents, hibiscus reverse | $0.50–$2 | World coin; not a U.S. quarter or presumed silver |
| CJ-026 | 1996 Press Pass #16 Chris Darkins football card | $0.25–$1 | One card shown front/back; base single, likely bundle item |
| CJ-027 | WWII War Ration Book Four with stamps and registrar certificate | $10–$25 | Count books and inspect completeness; family history item |
| CJ-028 | Campbell Soup Company 1982 Original Edition Swiss mechanical watch | $15–$35 | Back/front pair; worn strap, movement untested |
| CJ-029 | Lionel Collectible Train Watch | $8–$20 | Back/front pair; no tin shown; untested |
| CJ-030 | Seiko Mickey Mouse quartz watch, 5Y22-8039 | $15–$50 | Back/front pair; exact case-reference comp sold for $50; function unknown |
| CJ-031 | Lorus Disney Mickey Mouse quartz watch | $10–$30 | Back/front pair; model partly obscured; untested |

Important duplicate interpretation: CJ-016 and CJ-017 are two separate physical watches with different band colors, so both belong in the inventory. CJ-006 is a third, visibly different analog watch. The Jefferson-tradition necklace maps to CJ-011. The three-flower pendant CJ-005 is a different necklace and stays separate.

The currently generated HTML embeds image data as base64. That makes it portable but large; the app should instead store image files/object-storage references and keep records in a durable database. The existing HTML is a read-only-style searchable/exportable snapshot: its CSV button exports rows but editing the HTML does not update the Python source/database.

## Research Sites and What They Were Used For

These URLs were referenced in the existing records/research. Marketplace availability and prices change. Re-open and verify a comp at the time of valuation; distinguish sold/closed results from active asking prices. Some source pages were search/category pages, and some accepted offers do not disclose final price.

| Source | Use / caveat | Example links already recorded |
|---|---|---|
| eBay item pages/search results | Main marketplace comps. Prefer completed/sold transactions, same model/condition/completeness. Active listings only show what sellers hope to get. Best Offer may hide final price. | [Hygrade used set](https://www.ebay.com/itm/358662800278), [Hygrade sealed set](https://www.ebay.com/itm/236782439988), [Ronald McDonald watch](https://www.ebay.com/itm/377262752141), [1984 packaged watch](https://www.ebay.com/itm/168394455836), [Oleg Cassini](https://www.ebay.com/itm/257509344212), [Oleg Cassini](https://www.ebay.com/itm/226610082660), [Oleg Cassini](https://www.ebay.com/itm/285135452601), [Kaywoodie lighter](https://www.ebay.com/itm/117442554000), [Waltham](https://www.ebay.com/itm/137296073783), [Shriners](https://www.ebay.com/itm/267581221710), [Shriners](https://www.ebay.com/itm/124467490989), [Monticello necklace](https://www.ebay.com/itm/167355284357), [Monticello necklace](https://www.ebay.com/itm/188006321361), [stamp booklet](https://www.ebay.com/itm/366320996823), [coin folders](https://www.ebay.com/itm/336401721315), [coin folders](https://www.ebay.com/itm/257511746379), [coin folder](https://www.ebay.com/itm/236838538208), [McCormick full-figure Elvis sold for $65](https://www.ebay.com/itm/115710305800), [red-box Second Series current listing](https://www.ebay.com/itm/406678192462) |
| HiBid | Realized auction amounts for Elvis/McCormick editions; confirm lot descriptions and condition because auction prices can be low and local pickup/fees affect comparability. | [1977 sealed Elvis decanter realized $80](https://hibid.com/lot/158537658/1977-mccormick-whiskey-elvis-decanter-sealed), [Elvis collection auction, Silver Anniversary lot realized $70](https://hibid.com/catalog/611370?apage=2) |
| Proxibid | Realized prices for sealed/full decanters with boxes. Silver Anniversary lot realized $25; other editions in the same sale often realized $21–$22. Treat as auction evidence, not retail replacement value. | [Vintage Elvis sealed decanter auction](https://www.proxibid.com/The-Auction-Mill/Vintage-Elvis-Sealed-Decanters-Memorabilia-Omaha/event-catalog/175674) |
| JustAnswer appraiser Q&A | Individual appraisal opinions, not transaction data. These give higher value scenarios when the original package is present and the music box works; keep separate from realized sold comps. | [Silver Anniversary working/music-box value $150–$175](https://www.justanswer.com/antiques/qc9b0-silver-anniversary-elvis-decanter-sealed.html), [sealed decanters with original boxes appraisal](https://www.justanswer.com/antiques/foa7m-elvis-presley-bourbon-music-decanters-unopened.html) |
| Elvis CollectionHero price references | Archived eBay completed listings with described condition; verify dates/model match and remember older prices may not equal current market. | [1977 empty boxed bust sold for $34.95](https://elvis.collectionhero.com/view_item.php?id=67723), [Second Series, empty with working music box, sold for $45](https://elvis.collectionhero.com/view_item.php?id=23447) |
| SportsCardsPro | Card identification, price guide, and recorded sales history for common sports cards. Check card number/set/year/parallel and condition; thin sales history means low confidence. | [1991 Score Larry Sheets #176](https://www.sportscardspro.com/game/baseball-cards-1991-score/larry-sheets-176) |
| Ruby Lane | Antique/vintage specialty dealer listings can aid identification; an asking price is not evidence of a completed sale. | [Kaywoodie V.I.P. lighter result](https://www.rubylane.com/item/210948-4703/Vintage-Kaywoodie-VIP-Electric-Lighter-Original) |
| Poshmark | Secondary source for niche decor/collectibles; brand page/listing ask used only as a weak lead, not a sold comp. | [Ms. Dee brand page](https://poshmark.com/brand/ms%20dee) |
| Etsy | Useful for artisan/design context and active asking prices, not proof of completed resale value. | [Cassini jewelry search](https://www.etsy.com/market/cassini_jewelry?page=2) |
| Swisher Bros. auction archive | Auction results for comparable commemorative knife; auction result is more useful than a current ask, but verify exact model/lot. | [Holt Estate auction](https://swisherbros.com/auction/297-the-holt-estate/) |
| PicClick | Aggregates marketplace listings; use as a lead and confirm underlying/current/sold details on the marketplace. | [1987 Constitution knife](https://picclick.com/1987-We-The-People-200th-Anniversary-US-Constitution-184549546595.html) |
| General eBay category/search pages | Broad market context only; many results are unrelated or unsold. | [Washington 3-cent stamp category](https://www.ebay.com/b/george-washington-3-cent-stamp/bn_7024933439) |
| iCollector | Realized auction results for collectibles, medals, and banknotes; compare condition and premium separately. | [1928A $2 red seal sold for $30](https://www.icollector.com/1928A-U-S-Red-Seal-Two-Dollars-Note_i59949866), [STS-1 medal group sale](https://www.icollector.com/January-31st-Estate-Token-Sale-Bank-Tokens-Trade-Dollars-Medallions-and-more_as39095_p6?mobile=0&ps=100&vm=0) |
| Numista | Coin identification and indicative collector values; community estimates are not guaranteed realized sale prices. | [1969 Bahamas 25 cents](https://en.numista.com/3161), [1981 STS-1 Columbia medal identification](https://en.numista.com/336234) |
| Trading Card Database / SportsCardsPro / Beckett | Card identity and low-dollar price context; submitted prices and current asks are not equivalent to a confirmed sale. | [1996 Press Pass #16 Chris Darkins](https://www.tcdb.com/Price.cfm/sid/8396/cid/899786/1996-Press-Pass-16-Chris-Darkins), [SportsCardsPro 1996 Press Pass values](https://www.sportscardspro.com/console/football-cards-1996-press-pass), [Beckett marketplace](https://marketplace.beckett.com/search_new/?manufacturer=223640) |
| eBay sold listings (new batch) | Completed sales for exact or near-exact watches and WWII ration books. Active asks and Best Offer prices are clearly distinguished from confirmed prices. | [Campbell Soup 1982 watch sale indicator](https://www.ebay.com/itm/296540139153), [Lionel watch sold $20](https://www.ebay.com/itm/317888944867), [Seiko 5Y22-8039 sold $50](https://www.ebay.com/itm/236409919979), [Lorus Mickey sold $30](https://www.ebay.com/itm/335290027384), [Ration Book 3 sold $9.31](https://www.ebay.com/itm/257438164035), [Ration Books 1–4 sold $59.99](https://www.ebay.com/itm/205762548182) |
| HiBid / regional auction records | Auction realizations for Lionel and Lorus watches; sale amounts depend on lot, box, operation, fees, and pickup. | [Lionel with tin sold $16](https://hibid.com/lot/307238694/lionel-collectible-train-watch-with-tin), [Lorus Disney watch auction description and sale](https://palmersauctionco.com/auction/277-september-watch-clock/lot-106-lorus-disney/) |
| Poshmark | Active asking prices for the Campbell Soup watch; asks are not realized prices. | [Campbell Soup Company 1982 Original Edition watch](https://poshmark.com/listing/Campbell-Soup-Company-1982-Original-Edition-Mechanical-Watch-693ab5f8006e433b7297d0b0) |
| WatchCharts Marketplace | Aggregated sold comparable information and model identification for Seiko 5Y22-8039; verify the underlying sale and condition before relying on it. | [Seiko Mickey Mouse 5Y22-8039](https://marketplace.watchcharts.com/listing/25867637-seiko-mickey-mouse-watch-vintage-rare-dial-date-leather-band-5y22-8039) |

Additional recorded observations: a Hygrade used set sold for $16.99 and sealed set for $44.99 in different conditions; Larry Sheets pricing came from SportsCardsPro ($1.26 estimate and two recorded low-dollar sales); Kaywoodie boxed lighter accepted offer was reported as $35 from a $39.99 listing (accepted amount may not be fully verifiable); a similar boxed knife auction result was $20–$25; coin folders have a broad range because contents are unseen. The Oleg Cassini comps in the record were active asking prices, not confirmed sales. For the possible medallion lid and the Jefferson necklace, research did not verify an exact completed sale. Do not present catalog values or active asks as realized sale prices.

Latest batch on October 11, 2026: CJ-027 records the pictured family WWII ration ephemera group (War Ration Book Four, visible stamps/coupon sheet and registrar certificate) as one lot until the full count is known; comparable Book 3 sold for $9.31, while a fuller Books 1–4 set sold for $59.99. CJ-028 through CJ-031 are four separate watches, each with a front/back photo pair: Campbell Soup 1982 wind-up character watch, Lionel train watch, Seiko Mickey Mouse 5Y22-8039, and Lorus Disney Mickey Mouse watch with model partly obscured. The watches are not duplicates of the existing Ronald McDonald watches; their brands/models differ. Movement operation is unverified, which is reflected in the estimates. These five new records raised the gross priced total to $510.25–$1,155; two earlier items remain pending valuation.

New additions on October 11, 2026: CJ-023 is a carded souvenir medallion for Columbia STS-1; an exact-design medal sold for $11.99. CJ-024 is one 1928A red-seal $2 U.S. Legal Tender note pictured on both sides, with visible wear; $30 is an auction comparable but grade can materially change value. CJ-025 is a common 1969 Bahamas 25-cent coin with hibiscus design, estimated modestly. CJ-026 is a 1996 Press Pass Chris Darkins base football card; pair of photos are front/back of the same card. No duplicate was found among existing records. Current total includes these four entries.

Elvis valuation correction added October 11, 2026: CJ-018 is the 1980 Silver Anniversary model, with liquor and matching case per CJ. Better-matched sold evidence is $70 for a Silver Anniversary lot on HiBid and $25 for a Proxibid lot described as sealed/full with box; individual appraisers estimate about $150–$175 or $175–$225 for boxed examples when the music box works and the seal/package condition is strong. Those appraisal figures are not realized sales, so the current $70–$175 range is deliberately broad. The blue-box full-figure McCormick example has a close sold eBay match at $65 with a working music box. A 1977 empty bust with box/booklet sold for $34.95. A full-size “A Second in a Series” example with an empty container and working music box sold for $45; a current opened-bottle listing asks $93.75. Confirm the decanter, factory seal, liquor level, serial/certificate, and music-box function before tightening estimates. No estimate assigns independent value to the whiskey itself.

## Repeatable Per-Photo Workflow

1. **Capture first.** Commit original photo and its capture/group UUID immediately, with optional metadata blank if CJ chooses.
2. **Categorize automatically.** Queue low-cost OCR/visual identification without launching market research. Preserve original text, confidence, machine suggestions, and user overrides separately.
3. **Group views.** Back/front/packaging photos of one product append to its group. Next item is an explicit action; allow regrouping later.
4. **Check duplicates.** Compare hashes, prior associations, serials, model/marks, and images. Save possible duplicates for review without inflating confirmed counts/totals. Distinct physical variants remain separate.
5. **Research when requested.** A bulk action queues selected/unpriced item UUIDs. Use cached identification/comps for previously researched items; do not repeat this entire conversation or identical queries.
6. **Compare carefully.** Prefer sold/auction results for matching model, condition, unit/lot, completeness, and tested function. Distinguish active asks, guides, hidden offers, and appraisals from verified realized prices.
7. **Save history and failures.** Record low/high estimated USD, listing ask, evidence/URLs/confidence, reviewed date, revisions, and per-item errors. A research failure never deletes an item or its photos.
8. **Report the batch.** Show each item’s added/duplicate/review status and price evidence, then the priced gross subtotal and unpriced/review counts. Extra angles are not extra products.

### Duplicate policy examples from this collection

- A different photo/angle of the same watch is an update to the same ID.
- The black-band and red-band carded Ronald McDonald digital watches are two separate units (CJ-016/CJ-017), not duplicates.
- CJ-006 is an analog Ronald McDonald child's watch, separate from the carded digital watches.
- "Jefferson necklace" refers to the existing Monticello "Button" Jewelry necklace CJ-011. Ask if a new photo is that same necklace; do not add a duplicate.
- The silver-colored three-flower necklace CJ-005 is separately identified and should not be merged with CJ-011.

## Data Model Recommendation

Use SQLite for a single-user MVP or Postgres/Supabase if cloud sync/multiple devices are needed. Suggested tables:

- `items`: stable ID, normalized identity fields, category, title, description, year/era, quantity, condition, material, maker, model, sale status, storage location, created/updated timestamps.
- `photos`: item ID, storage URI, original filename, capture/upload date, view label (front/back/mark/packaging), perceptual hash, OCR text.
- `valuations`: item ID, low/high estimate, suggested ask, currency, reviewed date, confidence, methodology, notes; retain history instead of overwriting.
- `comps`: valuation ID, source/site, URL, sold/active/auction status, observed price, date, condition match notes, access date.
- `transactions`: item ID, sold date, gross price, shipping charged/paid, platform fees, taxes/other costs, net proceeds.
- `possible_duplicates`: candidate item IDs, similarity evidence, user decision, decision date.

Use server-side secrets for model/search services. Never put API keys in mobile client code or static HTML. Provide delete/export controls and backup/restore. Use a transaction when assigning IDs/saving to prevent collisions.

## Existing Implementation and How to Run

- `build_inventory.py` contains the 31 structured snapshot records and generates portable HTML, JSON, and CSV exports from the same rows. Its paths are relative to the script, so it runs after the folder is moved.
- `CJ_Collection_Inventory.html` is a standalone searchable/category-filtered inventory export with a Download CSV action. The separate CSV and JSON include all row fields, including additional photo references. Original photos are provided under `upload/`; `photo_manifest.json` records associations and unassigned originals.
- The current generated page is static. It cannot ingest a new photo or persist edits; the proposed app must replace that limitation with a database, camera upload, deduplication, and reviewed valuation flow.
- To regenerate the existing HTML snapshot in the current workspace: `python3 build_inventory.py` (expects local photos under `upload/`).

## Acceptance Checks

- Add a multi-angle photo set of an already cataloged item: app proposes matching ID, adds images only after user confirms, and leaves item count unchanged.
- Upload the same image twice: no duplicate record; second upload resolves to the existing item or is held for review.
- Upload the red-band McDonald watch after the black-band watch: app asks/recognizes it is a separate physical variant and saves a new item.
- Upload another photo of the existing Jefferson necklace: match CJ-011; do not add another necklace.
- Upload the distinct three-flower necklace: keep it separate from CJ-011 and flag material as unknown until hallmarks are visible.
- Show comps with direct URLs and label each as sold/auction/active ask; do not describe an active asking price as sale price.
- Estimate totals exclude pending records and visibly say gross estimate, not guaranteed proceeds.
- Mobile camera flow is usable on a narrow screen, handles permission denial, offline draft, slow upload, retry, and empty database.
- CSV export includes every record field and correctly escapes commas, quotes, and line breaks.

