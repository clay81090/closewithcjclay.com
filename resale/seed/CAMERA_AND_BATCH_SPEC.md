# Camera capture and bulk research: confirmed requirements

## Main experience

Build a mobile app for CJ with a prominent **Camera / Add item** button. CJ can keep photographing a collection and research prices later with one bulk action. Saving, categorizing, and pricing are separate operations. No Enter key, price search, or completed form is required to retain a photo.

1. Tap Camera and take a photo. Save the image and a capture record immediately.
2. Start inexpensive background visual classification/OCR automatically. Suggest category, short name, visible maker/model/date/serial, and identification confidence. This happens without a pricing request.
3. Keep the camera flow available while classification runs. Provide **Add another photo to this item** and **Next item** actions. Back/front/packaging/marking photos can belong to one product, with one record and one valuation.
4. Show an optional, collapsed **Details** panel: name, category, item date, serial number, and notes. CJ may enter any, all, or none of these fields. Do not require a form, confirmation, or typed name to continue. Automatically record capture time separately from the optional item date.
5. Show a saved-items tray with thumbnails, photo counts, category/identification progress, and pricing status. Metadata can be edited later, photos regrouped, and items searched by category, name, serial, or note.
6. Provide **Research unpriced items** and **Research selected items**. One tap launches a persistent batch; report per-item progress and the updated priced total. CJ can keep capturing during the job or leave and return.

## Capture, categorization, and optional metadata

- Commit the original photo/blob and capture UUID to IndexedDB before showing **Saved on this device**. Do not keep images only in component state or memory. Generate a small preview separately; preserve readable markings in the original.
- Upload originals and record changes in the background. Show **Synced** only after durable server storage confirms both image and metadata. A cloud backup is not complete merely because an upload request began.
- Each photo has an immutable UUID, checksum, item/capture association, capture time, optional view label, storage path, and sync state. Each item has a stable UUID independent of editable name/category. Preserve existing CJ-001 through CJ-031 identifiers on import; never renumber existing items.
- Automatically categorize online without a pricing click. If offline, permission is denied, storage is full, or the classification service fails, retain every successfully saved image, display the reason, and queue classification for retry. Use **Uncategorized — classification pending** while identification is unavailable; never invent a category to hide an error. Allow manual category entry at any time.
- Preserve machine suggestions separately from user overrides. A later model response must not erase CJ's name, date, category, serial number, or note. Blank optional values remain null/blank, not zero or fabricated facts.
- Item date is optional and may be a purchase/acquisition/date-of-item field selected by the user. Capture time is automatic. Unknown manufacture year/era remains unconfirmed. An OCR serial is a suggestion until legible enough or user-confirmed.
- Grouping is explicit: **Add photo** retains the current item's UUID; **Next item** starts a new capture UUID. Do not assume consecutive photos always represent separate items or always represent the same item. Multi-select imports need a grouping control, with optional regrouping later.
- Handle browser refresh, app restart, camera cancellation, upload failures, and intermittent connection without losing committed captures. Add understandable retry states and storage-error feedback.

## Duplicate policy and counts

- Save captures immediately even if a potential duplicate is detected. Do not create a second confirmed inventory item solely because another photo was taken.
- Compare exact photo checksums, previous item/capture IDs, visible serial/model/marks, and image similarity. Similar appearance alone cannot prove two physical objects are the same.
- A photo added within an existing item's capture group appends to that item. An exact duplicate upload must not add a duplicate photo or item by default.
- For clear matches, attach the new view to the existing item and retain its valuations/history. Ambiguous matches stay saved in a possible-duplicate queue with **Same item / Different physical item / Decide later** actions. Do not block further camera use.
- Different physical watches, cards, colors, serial numbers, or product editions can be separate entries. Imported lots/sets remain their existing quantity/group unless CJ splits them explicitly.
- Display captured groups, confirmed inventory entries, possible duplicates, priced entries, and unpriced entries separately. Exclude possible duplicates and unpriced items from value totals. Never count multiple photos as multiple products.

## Batch pricing behavior

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

## Suggested implementation contracts

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

## Build order for Cursor

1. Import the supplied 31-item JSON snapshot, stable identifiers, all CSV fields, and grouped photo references. Verify counts and total before introducing AI.
2. Implement mobile camera capture, local persistence, optional details, multi-photo item groups, and camera/next-item loop.
3. Implement background sync and classification with real configurable service integration and visible failures. Support manual metadata when classification is unavailable.
4. Implement duplicate review and cache reuse.
5. Implement persistent batch research, price evidence, per-item errors, and gross totals.
6. Add filtering, CSV/JSON/HTML exports, backups, and history. The HTML export is a view; the app database is authoritative after import.

## Acceptance checks

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
