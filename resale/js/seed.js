// Loads the October 11, 2026 starter collection once per browser.

import {
  applyAutoStar,
  autoPriority,
  getSetting,
  photosFor,
  putComp,
  putItem,
  putPhoto,
  setSetting,
} from "./db.js";
import { checksumOf } from "./camera.js";

const SEED_MARKER = "2026-10-11-v1";

function asNumber(value) {
  if (value === "" || value == null) return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function sourceUrls(text) {
  if (!text) return [];
  return String(text)
    .split(/[;\n]+/)
    .map((part) => part.trim())
    .filter((part) => /^https?:\/\//i.test(part));
}

function siteName(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch (err) {
    return "source";
  }
}

function compKind(url, evidence) {
  const hay = (url + " " + (evidence || "")).toLowerCase();
  if (/justanswer|appraisal/.test(hay)) return "appraisal";
  if (/hibid|proxibid|icollector|auction/.test(hay)) return "auction";
  if (/sportscardspro|numista|guide/.test(hay)) return "guide";
  if (/asking|active|listed at|poshmark|etsy|ruby lane/.test(hay)) return "ask";
  if (/sold/.test(hay)) return "sold";
  return "ask";
}

function blankToEmpty(value) {
  const text = value == null ? "" : String(value).trim();
  if (text === "Not recorded") return "";
  return text;
}

async function fileBlob(cache, filename) {
  if (!filename) return null;
  if (cache.has(filename)) return cache.get(filename);
  const response = await fetch("./seed/upload/" + filename);
  if (!response.ok) {
    cache.set(filename, null);
    return null;
  }
  const blob = await response.blob();
  cache.set(filename, blob);
  return blob;
}

export async function importSeed(onProgress) {
  const marker = await getSetting("seedImported");
  if (marker === SEED_MARKER) return { imported: false };

  const response = await fetch("./seed/CJ_Collection_Inventory.json");
  if (!response.ok) throw new Error("Starter collection could not be loaded");
  const rows = await response.json();
  const cache = new Map();

  for (let index = 0; index < rows.length; index += 1) {
    const row = rows[index];
    if (onProgress) onProgress(index + 1, rows.length);
    const low = asNumber(row["Low USD"]);
    const high = asNumber(row["High USD"]);
    const ask = asNumber(row["Suggested ask USD"]);
    const item = applyAutoStar(
      {
        id: row.ID,
        captureOrder: index + 1,
        createdAt: (row.Added || "2026-10-11") + "T12:00:00.000Z",
        name: row.Item || "",
        category: row.Category || "",
        itemDate: blankToEmpty(row["Item date"]),
        serial: blankToEmpty(row["Serial number"]),
        notes: blankToEmpty(row["User notes"]),
        storageLocation: blankToEmpty(row["Storage location"]),
        suggestedName: "",
        suggestedCategory: "",
        identityConfidence: null,
        starred: false,
        starReason: "",
        starTouched: false,
        priority: "",
        priorityTouched: false,
        tested: "",
        pricingStatus: low == null ? "needs_photo" : "priced",
        lowUsd: low,
        highUsd: high,
        askUsd: ask,
        evidence: row.Evidence || "",
        nextStep: row["Next step"] || "",
        condition: row.Condition || "",
        quantity: row.Quantity || "",
        year: row.Year || "",
        description: row.Description || "",
        saleStatus: row["Sale status"] || "Unlisted",
        errorText: "",
        dismissedDupes: [],
      },
      row["Next step"] || ""
    );
    item.priority = autoPriority(item);
    await putItem(item);

    const names = [row.Photo, row["Additional photos"]]
      .filter(Boolean)
      .flatMap((value) => String(value).split(/[;,]+/))
      .map((name) => name.trim())
      .filter(Boolean);

    const existing = await photosFor(item.id);
    let order = existing.length;
    const have = new Set(existing.map((photo) => photo.filename));
    for (const name of names) {
      if (have.has(name)) continue;
      const blob = await fileBlob(cache, name);
      if (!blob) continue;
      const checksum = await checksumOf(blob);
      await putPhoto({
        id: crypto.randomUUID(),
        itemId: item.id,
        order,
        checksum,
        createdAt: item.createdAt,
        filename: name,
        blob,
      });
      order += 1;
    }

    const seen = row["Price reviewed"] || row.Added || "2026-10-11";
    for (const url of sourceUrls(row.Sources)) {
      await putComp({
        id: crypto.randomUUID(),
        itemId: item.id,
        url,
        site: siteName(url),
        kind: compKind(url, row.Evidence),
        amount: null,
        note: row.Evidence || "",
        seenAt: seen,
        latest: true,
      });
    }
  }

  await setSetting("seedImported", SEED_MARKER);
  await setSetting("nextNumber", rows.length + 1);
  return { imported: true, count: rows.length };
}
