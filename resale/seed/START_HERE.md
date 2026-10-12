# Start here: CJ's camera inventory app

## Give this folder to Cursor

1. Unzip CJ_Cursor_Package.zip.
2. Open the CJ_Cursor_Package folder in Cursor.
3. Paste the contents of CURSOR_BUILD_PROMPT.md into Cursor's agent chat.

## What is included

| File | Purpose |
|---|---|
| CURSOR_HANDOFF.md | Complete handoff: current inventory, research sites/process, latest camera/bulk requirements, and exact HTML source |
| CAMERA_AND_BATCH_SPEC.md | Detailed capture, automatic category, optional metadata, multiple-photo groups, batch pricing, caching, failure handling, and acceptance checks |
| CURSOR_BUILD_PROMPT.md | Ready-to-paste build instruction |
| CJ_Collection_Inventory.json | All current seed records, easiest to import into the new app database |
| CJ_Collection_Inventory.csv | All records and the union of all 25 fields, including additional photos, sources, and optional metadata |
| CJ_Collection_Inventory.html | Current standalone searchable report; open it to view the collection |
| build_inventory.py | Portable snapshot/export generator; uses upload/ beside the script |
| upload/ | All available original uploaded photos, including extra views |
| photo_manifest.json | Photo-to-item associations, checksums, and unassigned originals that must not become automatic extra items |

## Verified snapshot

31 inventory entries; 29 priced; 2 pending valuation. Gross estimated resale range: **$510.25–$1,155**. Prices and research are carried forward from the October 11, 2026 review; packaging this folder did not reappraise the collection. Lots/sets count as one inventory entry. Multiple angles do not add extra entries.

Imported records preserve their CJ identifiers. Category, name, optional item date, serial, notes, sources, quantity, price confidence/evidence, and photo groups must survive import. The HTML/CSV/JSON are exports of one seed snapshot; after import, the app database becomes authoritative. Do not maintain independent edited versions that can diverge.

## Rebuild the existing exports

From this folder, run `python3 build_inventory.py`. It writes the HTML, JSON, and CSV using only Python's standard library and nearby upload/ photos. CURSOR_HANDOFF.md already contains the delivered HTML snapshot; if rebuilding after record changes, refresh that embedded reference or rely on the separate HTML file.

## Most important workflow

**Snap -> saved immediately -> automatic category -> next item -> bulk research later.** Optional fields never block capture. Add photo retains the same product group. Next item starts another group. Unpriced items stay saved indefinitely. Use the full specification for offline behavior, duplicate decisions, and cost/cache control.
