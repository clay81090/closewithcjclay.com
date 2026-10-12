// Price lookup. Runs only when CJ taps the button. Never invents a sold price.

import {
  allItems,
  applyAutoStar,
  autoPriority,
  commitResearchResult,
  getItem,
  getSettings,
  photoSignature,
  photosFor,
  researchInputFingerprint,
  saveJob,
  setSetting,
  getSetting,
} from "./db.js";
import { explainApiFailure, normalizeApiKey } from "./keys.js";

// Copy of memory/sites.md so the phone does not depend on a second fetch.
const SITE_MEMORY = `
# Site memory
Check the matching category first. A weak site is not a sold price.

## Baseball cards
- First: SportsCardsPro, then Trading Card Database. eBay sold for the same year, set, number, and parallel.
- Weak: Beckett asks, generic eBay browse.
- A set is one item. A base card is not a rare parallel.

## Football cards
- First: Trading Card Database and SportsCardsPro. eBay sold for that year, set, and number.

## Watches
- First: caseback brand and movement, then eBay sold. WatchCharts for known Seiko movements.
- An untested loose watch is not a sealed working boxed watch.

## Jewelry
- If the metal mark is missing, give a broad preliminary costume or unknown-metal range. Never assume precious metal. Star it for follow-up.

## Coins and currency
- First: Numista. If date or mint mark is missing, give a broad preliminary range and say what would tighten it.
- A folder is one lot until a key date is split out.

## Stamps
- If Scott number or condition is missing, give a broad preliminary range and say what would tighten it.

## Elvis decanters and whiskey memorabilia
- HiBid and Proxibid realized prices, then eBay sold.
- Keep empty, sealed, boxed, and working music box separate.
- JustAnswer is an opinion, not a sale. A box alone is not the full decanter.

## Space medals and souvenir metal
- A souvenir medal is not a flown precious-metal medal.

## Everything else
- eBay sold for the same completeness and tested or untested state.
- Ruby Lane, Etsy, and Poshmark are asks, not sales.
`;

const KINDS = new Set(["sold", "auction", "ask", "guide", "appraisal"]);
const LOCK_NAME = "cj-resale-price-research";
const FALLBACK_LOCK_KEY = "cj-resale-price-lock";
const LOCK_TTL_MS = 10 * 60 * 1000;
let activeController = null;

function numberOrNull(value) {
  if (value == null || value === "") return null;
  const number = Number(value);
  return Number.isFinite(number) && number >= 0 ? number : null;
}

function normalizedRange(lowValue, highValue) {
  const low = numberOrNull(lowValue);
  const high = numberOrNull(highValue);
  if (low == null || high == null) return { low, high };
  return low <= high ? { low, high } : { low: high, high: low };
}

async function downscale(blob) {
  const bitmap = await createImageBitmap(blob);
  const scale = Math.min(1, 1024 / Math.max(bitmap.width, bitmap.height));
  const canvas = document.createElement("canvas");
  canvas.width = Math.max(1, Math.round(bitmap.width * scale));
  canvas.height = Math.max(1, Math.round(bitmap.height * scale));
  canvas.getContext("2d").drawImage(bitmap, 0, 0, canvas.width, canvas.height);
  bitmap.close();
  const smaller = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.82));
  return smaller || blob;
}

async function toBase64(blob) {
  const dataUrl = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(blob);
  });
  return dataUrl.split(",")[1] || "";
}

function fastModel(settings) {
  return settings.haikuModel || "claude-haiku-4-5";
}

function closerModel(settings) {
  return settings.sonnetModel || "claude-sonnet-4-6";
}

function modelFor(item, settings) {
  const lowConfidence = typeof item.identityConfidence === "number" && item.identityConfidence < 0.5;
  if (item.starred || lowConfidence) return closerModel(settings);
  return fastModel(settings);
}

function modelPhrase(model, settings, unsure) {
  const kind = model === closerModel(settings) ? "the closer look" : "the fast model";
  const lead = unsure ? "The fast model was unsure. Now using " : "Using ";
  return lead + kind + ", " + model + ".";
}

function chunk(list, size) {
  const groups = [];
  for (let i = 0; i < list.length; i += size) groups.push(list.slice(i, i + size));
  return groups;
}

async function buildContent(items) {
  const notes = (await getSetting("siteNotes")) || [];
  const learned = notes.length ? "\n\nNotes saved from earlier lookups in this browser:\n" + notes.join("\n") : "";
  const blocks = [
    {
      type: "text",
      text:
        "You price resale items for one person. Return JSON only, no markdown.\n\n" +
        SITE_MEMORY +
        learned +
        "\n\nYou are a sharp, helpful resale appraiser. Behave like an expert who gives a useful number first and refines later. Never refuse to estimate.\n\n" +
        "Core rule: ALWAYS return your best low and high in US dollars. A photo is not required. A written description alone is enough. If you found real sold or auction listings, base the range on them. If you could not find a listing right now, still give a reasoned market range from what you know about this kind of item, and lower priceConfidence to show it is a knowledge estimate. Only leave low and high null if the description is too vague to even guess what the item is (for example 'old toy').\n\n" +
        "Rules:\n" +
        "- Identify the item from the photos and the owner's words together. You do not need a model number to give a range.\n" +
        "- Prefer sold and auction comps for the numbers. Asking prices and guides are weaker but fine for a preliminary range.\n" +
        "- Put a real http URL on any comp you actually found. Never invent a URL or a fake sold price. Having no URL is NOT a reason to skip low and high.\n" +
        "- confidence is how sure you are what the item is (0 to 1). priceConfidence is how sure you are about the dollars (0 to 1). A knowledge estimate with no live comp should have priceConfidence around 0.3 to 0.5, not null prices.\n" +
        "- conditionTiers: 3 to 5 rows showing how the value changes with condition, newest first in value. Example rows: used with wear; good, no box; excellent with original outfit; with original box and paperwork; rare variant. Each row is {label, low, high}. Use the owner's stated condition to pick which tier the main low and high come from.\n" +
        "- low and high reflect the owner's actual condition from OWNER FACTS. If they say in box, pristine, sealed, or collector edition, price the matching higher tier, do not price it like a loose used one.\n" +
        "- potentialHigh is the top price if the best case is confirmed (sealed, boxed, working, rare variant, desirable model). potentialCondition names what unlocks it. Set potentialHigh null only if there is no upside.\n" +
        "- uncertainReason: one short sentence on what would tighten the number, for example exact edition or back tag not confirmed. This never blocks the range.\n" +
        "- needsPhoto: only a short note of what photo would help later. Never a reason to return null prices when you can name the item.\n" +
        "- Honor the facts: sealed or in-box is not an opened example. Box only is not the complete product. Gold plate is not solid gold. Untested is not confirmed working. Base card is not a rare parallel.\n" +
        "- kind is one of sold, auction, ask, guide, appraisal.\n\n" +
        'JSON shape: {"items":[{"id":"","name":"","category":"","confidence":0,"priceConfidence":0,"uncertainReason":"","needsPhoto":"","star":false,"starReason":"","low":null,"high":null,"potentialHigh":null,"potentialCondition":"","conditionTiers":[{"label":"","low":0,"high":0}],"ask":null,"comps":[{"url":"","site":"","kind":"sold","amount":0,"note":""}],"evidence":"","nextStep":""}]}\n\n' +
        "Items in this batch:\n" +
        items
          .map((item) => {
            return (
              item.id +
              ": name=" +
              (item.name || "unknown") +
              "; category=" +
              (item.category || "unknown") +
              "; item date=" +
              (item.itemDate || item.year || "unknown") +
              "; serial/model=" +
              (item.serial || "unknown") +
              "; condition=" +
              (item.condition || "") +
              "; tested status=" +
              (item.tested || "not stated") +
              "; quantity=" +
              (item.quantity || "not stated") +
              "; OWNER NOTES=" +
              (item.notes || "none") +
              "; DESCRIPTION=" +
              (item.description || "none")
            );
          })
          .join("\n"),
    },
  ];

  for (const item of items) {
    const photos = await photosFor(item.id);
    const chosen =
      photos.length <= 6
        ? photos
        : [...photos.slice(0, 2), ...photos.slice(-4)];
    blocks.push({
      type: "text",
      text:
        "Photos for " +
        item.id +
        " (" +
        chosen.length +
        " of " +
        photos.length +
        "). First views plus newest detail photos are included.",
    });
    for (const photo of chosen) {
      try {
        const small = await downscale(photo.blob);
        blocks.push({
          type: "image",
          source: { type: "base64", media_type: "image/jpeg", data: await toBase64(small) },
        });
      } catch (err) {
        blocks.push({ type: "text", text: "One photo for " + item.id + " could not be read." });
      }
    }
  }
  return blocks;
}

export async function verifyAnthropicKey(settings) {
  const apiKey = normalizeApiKey(settings.apiKey);
  if (!apiKey) throw new Error("No key saved yet.");
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
      "anthropic-dangerous-direct-browser-access": "true",
    },
    body: JSON.stringify({
      model: settings.haikuModel || "claude-haiku-4-5",
      max_tokens: 8,
      messages: [{ role: "user", content: "Reply with the word OK." }],
    }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data.error && data.error.message ? data.error.message : "Key check failed";
    throw new Error(explainApiFailure(response.status, message));
  }
  return true;
}

async function callModel(settings, model, items, allowSearch) {
  const apiKey = normalizeApiKey(settings.apiKey);
  const body = {
    model,
    max_tokens: 4096,
    messages: [{ role: "user", content: await buildContent(items) }],
  };
  if (allowSearch) {
    body.tools = [{ type: "web_search_20250305", name: "web_search", max_uses: 8 }];
  }
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
      "anthropic-dangerous-direct-browser-access": "true",
    },
    body: JSON.stringify(body),
    signal: activeController?.signal,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data.error && data.error.message ? data.error.message : "Lookup failed";
    const error = new Error(explainApiFailure(response.status, message));
    error.status = response.status;
    error.code = "HTTP";
    throw error;
  }
  const text = (data.content || [])
    .filter((block) => block.type === "text" && block.text)
    .map((block) => block.text)
    .join("\n");
  if (!text.trim()) {
    const error = new Error("The lookup returned no price text");
    error.code = "EMPTY_RESPONSE";
    throw error;
  }
  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");
  if (start < 0 || end < start) {
    const error = new Error("The lookup did not return structured price data");
    error.code = "PARSE_RESPONSE";
    throw error;
  }
  try {
    return JSON.parse(text.slice(start, end + 1));
  } catch (cause) {
    const error = new Error("The lookup returned malformed price data. No second paid attempt was made.");
    error.code = "PARSE_RESPONSE";
    throw error;
  }
}

function isAuthOrBillingError(err) {
  const status = err && err.status;
  if (status === 401 || status === 403) return true;
  const message = String((err && err.message) || "").toLowerCase();
  return message.includes("rejected this key") || message.includes("balance is too low");
}

async function lookupGroup(settings, model, items) {
  try {
    return await callModel(settings, model, items, true);
  } catch (err) {
    if (isAuthOrBillingError(err) || err.name === "AbortError") throw err;
    const message = String(err.message || "");
    const toolRejected =
      err.code === "HTTP" &&
      (err.status === 400 || err.status === 422) &&
      /tool|web_search|search/i.test(message);
    if (!toolRejected) throw err;
    return callModel(settings, model, items, false);
  }
}

async function rememberComp(item, comp) {
  if (comp.kind !== "sold" && comp.kind !== "auction") return;
  const notes = (await getSetting("siteNotes")) || [];
  const line =
    (item.category || "Other") +
    ": " +
    (comp.site || "source") +
    " supported a " +
    comp.kind +
    " comp on " +
    new Date().toISOString().slice(0, 10);
  if (!notes.includes(line)) {
    notes.push(line);
    await setSetting("siteNotes", notes.slice(-40));
  }
}

function rangeFromCompAmounts(comps) {
  const amounts = comps
    .map((comp) => numberOrNull(comp.amount))
    .filter((amount) => amount != null && amount > 0);
  if (!amounts.length) return { low: null, high: null };
  return { low: Math.min(...amounts), high: Math.max(...amounts) };
}

function isDocumentedSaleComp(comp) {
  if (comp.kind !== "sold" && comp.kind !== "auction") return false;
  if (comp.amount == null || comp.amount <= 0 || !comp.note) return false;
  try {
    const url = new URL(comp.url);
    return (url.protocol === "http:" || url.protocol === "https:") && url.pathname !== "/";
  } catch (error) {
    return false;
  }
}

const RESEARCH_FIELDS = [
  "name",
  "category",
  "suggestedName",
  "suggestedCategory",
  "identityConfidence",
  "pricingConfidence",
  "uncertainReason",
  "potentialHigh",
  "potentialCondition",
  "conditionTiers",
  "errorText",
  "evidence",
  "nextStep",
  "lowUsd",
  "highUsd",
  "askUsd",
  "pricingStatus",
  "evidenceBacked",
  "verifiedSaleCount",
  "starred",
  "starReason",
  "priority",
  "lookupModel",
  "lookupLabel",
];

function researchPatch(item) {
  return Object.fromEntries(RESEARCH_FIELDS.map((key) => [key, item[key]]));
}

export async function applyLookup(item, result, meta = {}) {
  const current = await getItem(item.id);
  if (!current) return { status: "deleted", item: null };
  const expectedFingerprint = item.__researchFingerprint || researchInputFingerprint(item);
  const expectedPhotoSignature = item.__photoSignature || photoSignature(await photosFor(item.id));
  if (researchInputFingerprint(current) !== expectedFingerprint) {
    return { status: "changed", item: current };
  }

  const next = { ...current };
  if (!next.name && result.name) next.name = result.name;
  if (!next.category && result.category) next.category = result.category;
  if (result.name) next.suggestedName = result.name;
  if (result.category) next.suggestedCategory = result.category;
  if (typeof result.confidence === "number") next.identityConfidence = result.confidence;
  if (typeof result.priceConfidence === "number") next.pricingConfidence = result.priceConfidence;
  else if (typeof result.confidence === "number") next.pricingConfidence = result.confidence;
  if (result.uncertainReason) next.uncertainReason = String(result.uncertainReason).trim();
  next.potentialHigh = numberOrNull(result.potentialHigh);
  next.potentialCondition = result.potentialCondition ? String(result.potentialCondition).trim() : "";
  next.conditionTiers = Array.isArray(result.conditionTiers)
    ? result.conditionTiers
        .map((tier) => {
          const range = normalizedRange(tier && tier.low, tier && tier.high);
          return {
            label: tier && tier.label ? String(tier.label).trim() : "",
            low: range.low,
            high: range.high,
          };
        })
        .filter((tier) => tier.label && (tier.low != null || tier.high != null))
        .slice(0, 5)
    : [];

  const comps = (Array.isArray(result.comps) ? result.comps : [])
    .filter((comp) => comp && typeof comp.url === "string" && /^https?:\/\//i.test(comp.url.trim()))
    .map((comp) => ({
      url: comp.url.trim(),
      site: comp.site || "",
      kind: KINDS.has(comp.kind) ? comp.kind : "ask",
      amount: numberOrNull(comp.amount),
      note: comp.note || "",
    }));
  const documentedSales = comps.filter(isDocumentedSaleComp);
  const hasSale = documentedSales.length > 0;
  const needsPhoto = String(result.needsPhoto || "").trim();

  const seenAt = new Date().toISOString();
  const compRows = comps.map((comp) => ({
      id: crypto.randomUUID(),
      itemId: item.id,
      url: comp.url,
      site: comp.site,
      kind: comp.kind,
      amount: comp.amount,
      note: comp.note,
      seenAt,
      latest: true,
  }));

  next.errorText = "";
  let { low, high } = normalizedRange(result.low, result.high);
  if (low == null || high == null) {
    const derived = rangeFromCompAmounts(comps);
    if (low == null) low = derived.low;
    if (high == null) high = derived.high;
  }
  next.evidence = result.evidence || "";
  next.nextStep = result.nextStep || "";
  const followUp = [needsPhoto, next.uncertainReason].filter(Boolean).join(" · ");
  if (followUp && !next.nextStep.includes(needsPhoto)) {
    next.nextStep = followUp + (next.nextStep ? " · " + next.nextStep : "");
  }

  const hasAsk = comps.some((comp) => comp.kind === "ask" || comp.kind === "guide" || comp.kind === "appraisal");
  const priceSure =
    documentedSales.length > 0 &&
    (next.pricingConfidence == null || next.pricingConfidence >= 0.55) &&
    !needsPhoto &&
    !next.uncertainReason;
  next.evidenceBacked = priceSure;
  next.verifiedSaleCount = documentedSales.length;

  if (low != null && high != null) {
    next.lowUsd = low;
    next.highUsd = high;
    if (next.potentialHigh != null && next.potentialHigh < high) next.potentialHigh = null;
    next.askUsd = numberOrNull(result.ask);
    next.pricingStatus = priceSure ? "priced" : "estimate";
    if (next.pricingStatus === "estimate" && next.evidence && !/preliminary/i.test(next.evidence)) {
      next.evidence = next.evidence + " Preliminary estimate from photo match and comps, not an authenticated appraisal.";
    } else if (next.pricingStatus === "estimate" && !next.evidence) {
      next.evidence = "Preliminary estimate from photo match and comps, not an authenticated appraisal.";
    }
  } else if (comps.length || result.name || result.evidence) {
    next.pricingStatus = "needs_photo";
    next.lowUsd = null;
    next.highUsd = null;
    next.askUsd = null;
    next.nextStep =
      next.nextStep ||
      (comps.length && !hasSale && hasAsk
        ? "Similar listings found, but no dollar range yet. Add a note or back photo, then retry."
        : "Could not build a range yet. Add a back photo or a short note, then retry.");
  } else {
    next.pricingStatus = "needs_photo";
    next.lowUsd = null;
    next.highUsd = null;
    next.askUsd = null;
    next.nextStep = next.nextStep || "No match yet. Add another angle or a note about maker and condition.";
  }

  if (result.star && !next.starTouched) {
    next.starred = true;
    next.starReason = result.starReason || next.starReason || "Flagged during lookup";
  }
  applyAutoStar(next, needsPhoto);
  next.priority = autoPriority(next);
  next.lookupModel = meta.model || "";
  next.lookupLabel = meta.label || "";

  const outcome = await commitResearchResult({
    id: item.id,
    expectedFingerprint,
    expectedPhotoSignature,
    patch: researchPatch(next),
    comps: compRows,
  });
  if (outcome.status === "saved") {
    for (const comp of comps) await rememberComp(outcome.item, comp);
  }
  return outcome;
}

async function failItem(item, message) {
  return commitResearchResult({
    id: item.id,
    expectedFingerprint: item.__researchFingerprint || researchInputFingerprint(item),
    expectedPhotoSignature: item.__photoSignature || photoSignature(await photosFor(item.id)),
    patch: { pricingStatus: "failed", errorText: message, nextStep: message },
    comps: [],
    replaceComps: false,
  });
}

async function priceGroup(settings, model, group, onProgress, states, unsure) {
  for (const item of group) states[item.id] = "running";
  const phrase = modelPhrase(model, settings, unsure);
  if (onProgress) onProgress(states, phrase);
  const retry = [];
  try {
    const parsed = await lookupGroup(settings, model, group);
    const byId = new Map((parsed.items || []).map((row) => [row.id, row]));
    for (const item of group) {
      const row = byId.get(item.id);
      if (!row) {
        const failure = await failItem(item, "This item was missing from the lookup result.");
        states[item.id] = failure.status === "saved" ? "failed" : "discarded";
        continue;
      }
      try {
        const label = modelPhrase(model, settings, false).replace(/^Using /, "").replace(/\.$/, "");
        const outcome = await applyLookup(item, row, { model, label });
        if (outcome.status === "deleted" || outcome.status === "changed") {
          states[item.id] = "discarded";
          continue;
        }
        const saved = outcome.item;
        states[item.id] = "done";
        const lowConfidence = typeof saved.identityConfidence === "number" && saved.identityConfidence < 0.5;
        const newlyStarred = saved.starred && !item.starred;
        if (!unsure && model !== closerModel(settings) && (lowConfidence || newlyStarred)) retry.push(saved);
      } catch (err) {
        const failure = await failItem(item, err.message || "Could not save this result");
        states[item.id] = failure.status === "saved" ? "failed" : "discarded";
      }
    }
  } catch (err) {
    if (err.name === "AbortError") {
      for (const item of group) states[item.id] = "cancelled";
      if (onProgress) onProgress(states, "Lookup cancelled. Saved items were kept.");
      return retry;
    }
    for (const item of group) {
      const failure = await failItem(item, err.message || "Lookup failed");
      states[item.id] = failure.status === "saved" ? "failed" : "discarded";
    }
  }
  if (onProgress) onProgress(states, phrase);
  return retry;
}

async function runItems(settings, items, onProgress, states, heartbeat) {
  const groups = new Map();
  for (const item of items) {
    const photos = await photosFor(item.id);
    const written = (item.notes || item.name || item.description || "").trim();
    if (!photos.length && written.length < 8) {
      states[item.id] = "failed";
      await failItem(item, "Add a photo or describe the item.");
      if (onProgress) onProgress(states, "");
      continue;
    }
    // No photo means the model has to reason from words alone, so use the
    // stronger model for those from the start instead of the fast one.
    const model = photos.length ? modelFor(item, settings) : closerModel(settings);
    if (!groups.has(model)) groups.set(model, []);
    groups.get(model).push({
      ...item,
      __researchFingerprint: researchInputFingerprint(item),
      __photoSignature: photoSignature(photos),
    });
  }

  const retry = [];
  for (const [model, groupItems] of groups) {
    for (const group of chunk(groupItems, 8)) {
      if (heartbeat) await heartbeat();
      retry.push(...(await priceGroup(settings, model, group, onProgress, states, false)));
      if (heartbeat) await heartbeat();
    }
  }
  for (const group of chunk(retry, 8)) {
    if (heartbeat) await heartbeat();
    await priceGroup(settings, closerModel(settings), group, onProgress, states, true);
    if (heartbeat) await heartbeat();
  }
}

function busyError() {
  const error = new Error("A lookup is already running in this or another tab.");
  error.code = "BUSY";
  return error;
}

async function withFallbackLock(task) {
  const owner = crypto.randomUUID();
  const now = Date.now();
  let lease;
  try {
    lease = JSON.parse(localStorage.getItem(FALLBACK_LOCK_KEY) || "null");
  } catch (error) {
    lease = null;
  }
  if (lease && lease.expiresAt > now) throw busyError();
  localStorage.setItem(FALLBACK_LOCK_KEY, JSON.stringify({ owner, expiresAt: now + LOCK_TTL_MS }));
  const renew = setInterval(() => {
    localStorage.setItem(
      FALLBACK_LOCK_KEY,
      JSON.stringify({ owner, expiresAt: Date.now() + LOCK_TTL_MS })
    );
  }, 15000);
  try {
    return await task();
  } finally {
    clearInterval(renew);
    try {
      const current = JSON.parse(localStorage.getItem(FALLBACK_LOCK_KEY) || "null");
      if (current?.owner === owner) localStorage.removeItem(FALLBACK_LOCK_KEY);
    } catch (error) {
      localStorage.removeItem(FALLBACK_LOCK_KEY);
    }
  }
}

async function withResearchLock(task) {
  if (!navigator.locks?.request) return withFallbackLock(task);
  let result;
  let acquired = false;
  await navigator.locks.request(LOCK_NAME, { ifAvailable: true }, async (lock) => {
    if (!lock) return;
    acquired = true;
    result = await task();
  });
  if (!acquired) throw busyError();
  return result;
}

async function researchItemsLocked(items, onProgress) {
  const settings = await getSettings();
  if (!settings.apiKey) {
    const error = new Error("Add your Anthropic key to look up prices. Your photos stay saved.");
    error.code = "NO_KEY";
    throw error;
  }
  const states = {};
  for (const item of items) states[item.id] = "pending";
  const job = {
    itemIds: items.map((item) => item.id),
    startedAt: new Date().toISOString(),
    heartbeatAt: new Date().toISOString(),
    running: true,
    states,
  };
  await saveJob(job);
  if (onProgress) onProgress(states);
  activeController = new AbortController();
  const heartbeat = async () => {
    job.heartbeatAt = new Date().toISOString();
    job.states = { ...states };
    await saveJob(job);
  };
  try {
    await runItems(settings, items, onProgress, states, heartbeat);
  } finally {
    job.running = false;
    job.states = states;
    job.finishedAt = new Date().toISOString();
    await saveJob(job);
    activeController = null;
  }
  return job;
}

export async function researchItems(items, onProgress) {
  return withResearchLock(() => researchItemsLocked(items, onProgress));
}

export function cancelResearch() {
  if (activeController) activeController.abort();
}

export async function researchUnpriced(onProgress) {
  const settings = await getSettings();
  const limit = Math.max(1, Math.min(25, Number(settings.maxItemsPerRun) || 10));
  const items = (await allItems()).filter(
    (item) => item.pricingStatus === "saved" || item.pricingStatus === "failed"
  ).slice(0, limit);
  if (!items.length) return null;
  return researchItems(items, onProgress);
}

export async function researchFailed(onProgress) {
  const settings = await getSettings();
  const limit = Math.max(1, Math.min(25, Number(settings.maxItemsPerRun) || 10));
  const items = (await allItems()).filter((item) => item.pricingStatus === "failed").slice(0, limit);
  if (!items.length) return null;
  return researchItems(items, onProgress);
}

export async function researchOne(item, onProgress) {
  return researchItems([item], onProgress);
}

export function searchLinks(item) {
  const query = encodeURIComponent(item.name || item.suggestedName || item.category || "collectible");
  const links = [
    {
      label: "eBay sold",
      url: "https://www.ebay.com/sch/i.html?_nkw=" + query + "&LH_Sold=1&LH_Complete=1",
    },
  ];
  const category = (item.category || "").toLowerCase();
  if (/coin|currency|note|stamp/.test(category)) {
    links.push({
      label: "Numista",
      url: "https://en.numista.com/catalogue/index.php?q=" + query,
    });
  }
  if (/card/.test(category)) {
    links.push({
      label: "SportsCardsPro",
      url: "https://www.sportscardspro.com/",
    });
  }
  return links;
}

export function listingBlurb(item) {
  const title = item.name || item.id;
  const lines = [];
  const condition = item.condition || "";
  if (item.tested === "untested" || /untested/i.test(condition)) lines.push("Untested.");
  if (/opened/i.test(condition)) lines.push("Opened.");
  if (/box only|box-only|no decanter/i.test(condition + " " + (item.description || ""))) {
    lines.push("Box only. The piece inside is not confirmed.");
  }
  if (item.quantity && lines.length < 3) lines.push(item.quantity);
  if (condition && lines.length < 3 && !lines.includes(condition)) lines.push(condition);
  if (item.nextStep && lines.length < 3) lines.push(item.nextStep);
  while (lines.length < 3) lines.push("See the photos for condition.");
  return [title, ...lines.slice(0, 3)].join("\n");
}

export function showsTested(item) {
  return /watch|lighter/i.test((item.category || "") + " " + (item.name || ""));
}

export function displayAsk(item) {
  if (item.askUsd == null) return null;
  if (item.tested === "untested" && showsTested(item)) return Number(item.askUsd) * 0.8;
  return Number(item.askUsd);
}
