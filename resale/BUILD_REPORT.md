# Build report

Claude's terminal run finished without writing the app. The permission file blocked the first save. This app was built in Cursor after that.

## What you open

On this computer, while the local preview is running:

http://127.0.0.1:8877/resale/

On your phone, after this folder is pushed:

https://closewithcjclay.com/resale/

Safari on the phone and Chrome on the computer do not share photos. The 31 starter items load in both. New photos stay in the browser that took them until you use Download backup or Share backup, then Import backup on the other one.

## Files

- `index.html`, `styles.css`, `manifest.webmanifest`, `sw.js`, `icon.png`
- `js/db.js`, `js/seed.js`, `js/camera.js`, `js/research.js`, `js/ui.js`

`memory/sites.md` is copied into `js/research.js` so the phone does not need a second download. When a real sold or auction link is saved, a short note is stored in this browser and sent with the next lookup. A static page cannot edit `memory/sites.md` on the server.

## Checks actually run

In the Cursor browser, on a local server:

1. First load: 31 items, gross **$510.25 to $1,155** across 29 priced items. CJ-004 and CJ-005 have no price.
2. The five unassigned background photos are not items.
3. CJ-016 and CJ-017 both exist and share one photo checksum.
4. A second load stayed at 31 items.
5. With no API key, Find resale prices opened Settings and showed: "Add your Anthropic key to look up prices. Your photos stay saved." No prices were written.
6. At 390px wide, type is 17px, the main buttons are about 48px tall, and the page does not scroll sideways. At 1200px wide, the camera and the list sit side by side, and the page does not scroll sideways.
7. The new work is only the `resale/` folder plus `.cursor/rules/resale-app.mdc`. Nothing was committed.

Not run on a real iPhone. This browser is not Safari on a phone, so the iPhone camera path (Take photo opening the system camera) was not tapped on a device. Desktop showed the live preview and Shutter. Take photo and Choose photos are on the page for both.

No price lookup was run against Anthropic. There is no key in the page.
