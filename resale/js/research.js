// Price lookup. Runs only when CJ taps the button. Never invents a sold price.

import {
  allItems,
  applyAutoStar,
  autoPriority,
  compsFor,
  getJob,
  getSettings,
  photosFor,
  putComp,
  putItem,
  saveJob,
  setSetting,
  getSetting,
} from "./db.js";

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
- Do not price until a metal mark is visible. Star it when the mark is missing.

## Coins and currency
- First: Numista. eBay sold only after the date and mint mark are visible.
- A folder is one lot until a key date is split out.

## Stamps
- Scott number and condition before a price.

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

function numberOrNull(value) {
  if (value == null || value === "") return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
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

function modelFor(item, settings) {
  const lowConfidence = typeof item.identityConfidence === "number" && item.identityConfidence < 0.5;
  if (item.starred || lowConfidence) return settings.sonnetModel || "claude-sonnet-4-6";
  return settings.haikuModel || "claude-haiku-4-5";
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
        "\n\nRules:\n" +
        "- Prefer sold and auction comps. An asking price, guide, or appraisal is not a sold price.\n" +
        "- Every comp needs a real http URL you actually found. If you cannot find one, use an empty comps list and null prices.\n" +
        "- Do not invent a URL or a sold price.\n" +
        "- Souvenir medal is not precious-metal or flown metal.\n" +
        "- Untested loose watch is not a sealed working boxed watch.\n" +
        "- Base card is not a rare parallel.\n" +
        "- Box only is not the complete product.\n" +
        "- Gold plate is not solid gold.\n" +
        "- The owner's notes are facts about the item in hand. A sealed, unopened, or undamaged box is not the same as an opened, empty, or damaged example. Say that difference in the evidence and do not copy the opened price onto a sealed item.\n" +
        "- A written description with no photo is enough to search. Do not put needsPhoto on a specific named item such as a doll, card, or bottle when the owner already described the year, name, and whether it is sealed.\n" +
        "- If a hallmark, caseback, card back, mint mark, or whether the bottle is inside is missing from both the photos and the notes, put that in needsPhoto and use null prices.\n" +
        "- kind is one of sold, auction, ask, guide, appraisal.\n\n" +
        'JSON shape: {"items":[{"id":"","name":"","category":"","confidence":0,"needsPhoto":"","star":false,"starReason":"","low":null,"high":null,"ask":null,"comps":[{"url":"","site":"","kind":"sold","amount":0,"note":""}],"evidence":"","nextStep":""}]}\n\n' +
        "Items in this batch:\n" +
        items
          .map((item) => {
            return (
              item.id +
              ": name=" +
              (item.name || "unknown") +
              "; category=" +
              (item.category || "unknown") +
              "; condition=" +
              (item.condition || "") +
              "; OWNER FACTS=" +
              (item.notes || item.description || "none")
            );
          })
          .join("\n"),
    },
  ];

  for (const item of items) {
    const photos = await photosFor(item.id);
    const chosen = photos.slice(0, 4);
    blocks.push({
      type: "text",
      text: "Photos for " + item.id + " (" + chosen.length + " of " + photos.length + ").",
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

async function callModel(settings, model, items, allowSearch) {
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
      "x-api-key": settings.apiKey,
      "anthropic-version": "2023-06-01",
      "anthropic-dangerous-direct-browser-access": "true",
    },
    body: JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data.error && data.error.message ? data.error.message : "Lookup failed";
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  const text = (data.content || [])
    .filter((block) => block.type === "text" && block.text)
    .map((block) => block.text)
    .join("\n");
  if (!text.trim()) throw new Error("The lookup returned no price text");
  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");
  if (start < 0 || end < start) throw new Error("The lookup did not return JSON");
  return JSON.parse(text.slice(start, end + 1));
}

async function lookupGroup(settings, model, items) {
  try {
    return await callModel(settings, model, items, true);
  } catch (err) {
    const message = String(err.message || "");
    if (/tool|web_search|search/i.test(message)) {
      return callModel(settings, model, items, false);
    }
    throw err;
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

export async function applyLookup(item, result) {
  const next = { ...item };
  if (!next.name && result.name) next.name = result.name;
  if (!next.category && result.category) next.category = result.category;
  if (result.name) next.suggestedName = result.name;
  if (result.category) next.suggestedCategory = result.category;
  if (typeof result.confidence === "number") next.identityConfidence = result.confidence;

  const comps = (Array.isArray(result.comps) ? result.comps : [])
    .filter((comp) => comp && typeof comp.url === "string" && /^https?:\/\//i.test(comp.url.trim()))
    .map((comp) => ({
      url: comp.url.trim(),
      site: comp.site || "",
      kind: KINDS.has(comp.kind) ? comp.kind : "ask",
      amount: numberOrNull(comp.amount),
      note: comp.note || "",
    }));
  const hasSale = comps.some((comp) => comp.kind === "sold" || comp.kind === "auction");
  const needsPhoto = String(result.needsPhoto || "").trim();

  const previous = await compsFor(item.id);
  for (const comp of previous) {
    if (comp.latest) await putComp({ ...comp, latest: false });
  }
  const seenAt = new Date().toISOString();
  for (const comp of comps) {
    await putComp({
      id: crypto.randomUUID(),
      itemId: item.id,
      url: comp.url,
      site: comp.site,
      kind: comp.kind,
      amount: comp.amount,
      note: comp.note,
      seenAt,
      latest: true,
    });
    await rememberComp(next, comp);
  }

  next.errorText = "";
  const written = (item.notes || item.description || "").trim().length > 12;
  const low = numberOrNull(result.low);
  const high = numberOrNull(result.high);
  if (needsPhoto && !(written && hasSale && low != null && high != null)) {
    next.pricingStatus = "needs_photo";
    next.lowUsd = null;
    next.highUsd = null;
    next.askUsd = null;
    next.nextStep = needsPhoto;
    next.evidence = result.evidence || next.evidence || "";
  } else if (!hasSale) {
    next.pricingStatus = "needs_photo";
    next.lowUsd = null;
    next.highUsd = null;
    next.askUsd = null;
    next.evidence = result.evidence || "";
    next.nextStep = comps.length
      ? "Only asking prices or guides came back. No sold range was saved."
      : "No source link came back, so no price was saved.";
  } else {
    next.lowUsd = numberOrNull(result.low);
    next.highUsd = numberOrNull(result.high);
    next.askUsd = numberOrNull(result.ask);
    next.evidence = result.evidence || "";
    next.nextStep = result.nextStep || "";
    if (next.lowUsd == null || next.highUsd == null) {
      next.pricingStatus = "needs_photo";
      next.askUsd = null;
      next.nextStep = next.nextStep || "A sold link came back without a usable range.";
    } else {
      next.pricingStatus = "priced";
      if (needsPhoto) next.nextStep = needsPhoto + (next.nextStep ? " " + next.nextStep : "");
    }
  }

  if (result.star && !next.starTouched) {
    next.starred = true;
    next.starReason = result.starReason || next.starReason || "Flagged during lookup";
  }
  applyAutoStar(next, needsPhoto);
  next.priority = autoPriority(next);
  await putItem(next);
  return next;
}

async function failItem(item, message) {
  const next = {
    ...item,
    pricingStatus: "failed",
    errorText: message,
    nextStep: message,
  };
  await putItem(next);
  return next;
}

async function runItems(settings, items, onProgress, states) {
  const groups = new Map();
  for (const item of items) {
    const photos = await photosFor(item.id);
    const written = (item.notes || item.name || item.description || "").trim();
    if (!photos.length && written.length < 8) {
      states[item.id] = "failed";
      await failItem(item, "Add a photo or describe the item.");
      if (onProgress) onProgress(states);
      continue;
    }
    const model = modelFor(item, settings);
    if (!groups.has(model)) groups.set(model, []);
    groups.get(model).push(item);
  }

  for (const [model, groupItems] of groups) {
    for (const group of chunk(groupItems, 8)) {
      for (const item of group) states[item.id] = "running";
      if (onProgress) onProgress(states);
      try {
        const parsed = await lookupGroup(settings, model, group);
        const byId = new Map((parsed.items || []).map((row) => [row.id, row]));
        for (const item of group) {
          const row = byId.get(item.id);
          if (!row) {
            states[item.id] = "failed";
            await failItem(item, "This item was missing from the lookup result.");
            continue;
          }
          try {
            await applyLookup(item, row);
            states[item.id] = "done";
          } catch (err) {
            states[item.id] = "failed";
            await failItem(item, err.message || "Could not save this result");
          }
        }
      } catch (err) {
        for (const item of group) {
          states[item.id] = "failed";
          await failItem(item, err.message || "Lookup failed");
        }
      }
      if (onProgress) onProgress(states);
    }
  }
}

export async function researchItems(items, onProgress) {
  const existing = await getJob();
  if (existing && existing.running) return existing;
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
    running: true,
    states,
  };
  await saveJob(job);
  if (onProgress) onProgress(states);
  try {
    await runItems(settings, items, onProgress, states);
  } finally {
    job.running = false;
    job.states = states;
    await saveJob(job);
  }
  return job;
}

export async function researchUnpriced(onProgress) {
  const existing = await getJob();
  if (existing && existing.running) return existing;
  const items = (await allItems()).filter(
    (item) => item.pricingStatus === "saved" || item.pricingStatus === "failed"
  );
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
