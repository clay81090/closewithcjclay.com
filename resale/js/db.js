// Phone database. Everything CJ saves stays in this browser until he exports it.

const DB_NAME = "cj-resale";
const DB_VERSION = 1;

let dbPromise = null;

function openDb() {
  if (dbPromise) return dbPromise;
  dbPromise = new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onerror = () => reject(req.error);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains("items")) {
        db.createObjectStore("items", { keyPath: "id" });
      }
      if (!db.objectStoreNames.contains("photos")) {
        const photos = db.createObjectStore("photos", { keyPath: "id" });
        photos.createIndex("itemId", "itemId", { unique: false });
        photos.createIndex("checksum", "checksum", { unique: false });
      }
      if (!db.objectStoreNames.contains("comps")) {
        const comps = db.createObjectStore("comps", { keyPath: "id" });
        comps.createIndex("itemId", "itemId", { unique: false });
      }
      if (!db.objectStoreNames.contains("settings")) {
        db.createObjectStore("settings", { keyPath: "key" });
      }
      if (!db.objectStoreNames.contains("jobs")) {
        db.createObjectStore("jobs", { keyPath: "id" });
      }
    };
    req.onsuccess = () => resolve(req.result);
  });
  return dbPromise;
}

function tx(storeNames, mode, fn) {
  return openDb().then(
    (db) =>
      new Promise((resolve, reject) => {
        const t = db.transaction(storeNames, mode);
        const result = fn(t);
        t.oncomplete = () => resolve(result);
        t.onerror = () => reject(t.error);
        t.onabort = () => reject(t.error || new Error("Save was cancelled"));
      })
  );
}

function requestToPromise(req) {
  return new Promise((resolve, reject) => {
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

export const DEFAULT_SETTINGS = {
  apiKey: "",
  feePercent: 13,
  shippingUsd: 5,
  haikuModel: "claude-haiku-4-5",
  sonnetModel: "claude-sonnet-4-6",
  seedImported: "",
  nextNumber: 1,
};

export async function getSetting(key) {
  const row = await tx(["settings"], "readonly", (t) => requestToPromise(t.objectStore("settings").get(key)));
  if (!row) return DEFAULT_SETTINGS[key];
  return row.value;
}

export async function setSetting(key, value) {
  await tx(["settings"], "readwrite", (t) => {
    t.objectStore("settings").put({ key, value });
  });
}

export async function getSettings() {
  const keys = Object.keys(DEFAULT_SETTINGS);
  const settings = { ...DEFAULT_SETTINGS };
  for (const key of keys) {
    const value = await getSetting(key);
    if (value !== undefined) settings[key] = value;
  }
  return settings;
}

export async function allItems() {
  const rows = await tx(["items"], "readonly", (t) => requestToPromise(t.objectStore("items").getAll()));
  return rows.sort((a, b) => (a.captureOrder || 0) - (b.captureOrder || 0));
}

export async function getItem(id) {
  return tx(["items"], "readonly", (t) => requestToPromise(t.objectStore("items").get(id)));
}

export async function putItem(item) {
  await tx(["items"], "readwrite", (t) => {
    t.objectStore("items").put(item);
  });
  return item;
}

export async function deleteItem(id) {
  await tx(["items"], "readwrite", (t) => {
    t.objectStore("items").delete(id);
  });
}

export async function photosFor(itemId) {
  const rows = await tx(["photos"], "readonly", (t) =>
    requestToPromise(t.objectStore("photos").index("itemId").getAll(itemId))
  );
  return rows.sort((a, b) => (a.order || 0) - (b.order || 0));
}

export async function allPhotos() {
  return tx(["photos"], "readonly", (t) => requestToPromise(t.objectStore("photos").getAll()));
}

export async function putPhoto(photo) {
  await tx(["photos"], "readwrite", (t) => {
    t.objectStore("photos").put(photo);
  });
  return photo;
}

export async function deletePhoto(id) {
  await tx(["photos"], "readwrite", (t) => {
    t.objectStore("photos").delete(id);
  });
}

export async function photosWithChecksum(checksum) {
  return tx(["photos"], "readonly", (t) =>
    requestToPromise(t.objectStore("photos").index("checksum").getAll(checksum))
  );
}

export async function compsFor(itemId) {
  const rows = await tx(["comps"], "readonly", (t) =>
    requestToPromise(t.objectStore("comps").index("itemId").getAll(itemId))
  );
  return rows.sort((a, b) => String(b.seenAt || "").localeCompare(String(a.seenAt || "")));
}

export async function allComps() {
  return tx(["comps"], "readonly", (t) => requestToPromise(t.objectStore("comps").getAll()));
}

export async function putComp(comp) {
  await tx(["comps"], "readwrite", (t) => {
    t.objectStore("comps").put(comp);
  });
}

export async function getJob() {
  return tx(["jobs"], "readonly", (t) => requestToPromise(t.objectStore("jobs").get("active")));
}

export async function saveJob(job) {
  job.id = "active";
  await tx(["jobs"], "readwrite", (t) => {
    t.objectStore("jobs").put(job);
  });
  return job;
}

async function clearStore(name) {
  await tx([name], "readwrite", (t) => {
    t.objectStore(name).clear();
  });
}

// Next new item. Existing CJ-001 through CJ-031 are never reused.
export async function allocateItem() {
  const items = await allItems();
  const settings = await getSettings();
  const number = Number(settings.nextNumber) || items.length + 1;
  const captureOrder = items.reduce((max, item) => Math.max(max, item.captureOrder || 0), 0) + 1;
  await setSetting("nextNumber", number + 1);
  return {
    id: "CJ-" + String(number).padStart(3, "0"),
    captureOrder,
  };
}

export function blankItem(id, captureOrder) {
  return {
    id,
    captureOrder,
    createdAt: new Date().toISOString(),
    name: "",
    category: "",
    itemDate: "",
    serial: "",
    notes: "",
    storageLocation: "",
    suggestedName: "",
    suggestedCategory: "",
    identityConfidence: null,
    starred: false,
    starReason: "",
    starTouched: false,
    priority: "",
    priorityTouched: false,
    tested: "",
    pricingStatus: "saved",
    lowUsd: null,
    highUsd: null,
    askUsd: null,
    evidence: "",
    nextStep: "",
    condition: "",
    quantity: "",
    year: "",
    description: "",
    saleStatus: "Unlisted",
    errorText: "",
    dismissedDupes: [],
  };
}

export function money(value) {
  if (value == null || value === "" || !Number.isFinite(Number(value))) return "";
  const amount = Math.round(Number(value) * 100) / 100;
  const whole = Math.abs(amount - Math.round(amount)) < 0.001;
  return amount.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: whole ? 0 : 2,
    maximumFractionDigits: whole ? 0 : 2,
  });
}

export function grossTotals(items) {
  let low = 0;
  let high = 0;
  let count = 0;
  for (const item of items) {
    if (item.lowUsd == null || item.highUsd == null) continue;
    low += Number(item.lowUsd);
    high += Number(item.highUsd);
    count += 1;
  }
  return { low, high, count };
}

// Guess after fees. Fee comes off the price first, then shipping.
export function mightClear(low, high, feePercent, shippingUsd) {
  const fee = Number(feePercent) / 100;
  const shipping = Number(shippingUsd) || 0;
  const net = (amount) => Math.max(0, Number(amount) * (1 - fee) - shipping);
  return { low: net(low), high: net(high) };
}

export function autoPriority(item) {
  if (item.priorityTouched) return item.priority || "";
  if (item.highUsd == null || item.lowUsd == null) return "";
  if (Number(item.highUsd) < 8) return "bundle";
  const ask = item.askUsd == null ? Number(item.highUsd) : Number(item.askUsd);
  if (ask >= 40) return "high";
  if (ask >= 15) return "medium";
  return "low";
}

// "Silver-colored" and "gold-tone" are colors, not hallmarks.
function hasMetalMark(text) {
  if (/925|sterling|\b14k\b|\b10k\b|\b18k\b|\b24k\b|gold plate|gold-plate|pewter|\bbrass\b/i.test(text)) {
    return true;
  }
  const stripped = text.replace(/silver-colored|gold-colored|gold-tone|gold tone|silver tone|silver-tone/gi, "");
  return /\bsilver\b|\bgold\b/i.test(stripped);
}

export function starReasons(item, needsPhoto) {
  const text = [item.name, item.category, item.notes, item.description, item.year].filter(Boolean).join(" ");
  const reasons = [];
  const jewelry =
    /jewel|necklace|pendant/i.test(item.category || "") ||
    (/\b(ring|bracelet)\b/i.test(item.name || "") && !/watch/i.test(item.category || ""));
  if (jewelry && !hasMetalMark(text)) reasons.push("Metal mark is not visible");
  if (/key date|mint marks?|diamond|platinum|solid gold|precious metal/i.test(text)) {
    reasons.push("May be worth a closer look before you sell it");
  }
  if (
    item.highUsd != null &&
    item.lowUsd != null &&
    Number(item.highUsd) > 75 &&
    Number(item.highUsd) > Number(item.lowUsd) * 2 &&
    /sealed|boxed|original box|presentation case/i.test(text)
  ) {
    reasons.push("Boxed piece with a wide price range");
  }
  if (needsPhoto && /caseback|mint\s*marks?|hallmark|bottle|inside the box/i.test(needsPhoto)) {
    reasons.push(needsPhoto);
  }
  return reasons;
}

export function applyAutoStar(item, needsPhoto) {
  if (item.starTouched) return item;
  const reasons = starReasons(item, needsPhoto || "");
  if (reasons.length) {
    item.starred = true;
    item.starReason = reasons[0];
  }
  return item;
}

export async function replaceCatalog(payload) {
  const apiKey = await getSetting("apiKey");
  await clearStore("items");
  await clearStore("photos");
  await clearStore("comps");
  for (const item of payload.items || []) await putItem(item);
  for (const photo of payload.photos || []) await putPhoto(photo);
  for (const comp of payload.comps || []) await putComp(comp);
  const incoming = payload.settings || {};
  for (const key of Object.keys(DEFAULT_SETTINGS)) {
    if (key === "apiKey") continue;
    if (incoming[key] !== undefined) await setSetting(key, incoming[key]);
  }
  await setSetting("apiKey", apiKey || "");
  await setSetting("seedImported", incoming.seedImported || "backup");
}

export async function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(",")[1] || "");
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(blob);
  });
}

export function base64ToBlob(data, type) {
  const binary = atob(data);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
  return new Blob([bytes], { type: type || "image/jpeg" });
}
