// Screen controller. Camera first. Prices only after Find resale prices.

import {
  checksumOf,
  grabFrame,
  hashDistance,
  hasPreview,
  isIphone,
  perceptualHashOf,
  startPreview,
  stopPreview,
} from "./camera.js";
import {
  allItems,
  allPhotos,
  allocateItem,
  autoPriority,
  base64ToBlob,
  blankItem,
  blobToBase64,
  allComps,
  compsFor,
  deleteItem,
  deletePhoto,
  getItem,
  getJob,
  getRecoveryBackup,
  getSettings,
  grossTotals,
  importCatalogAtomic,
  mightClear,
  money,
  photosFor,
  photosWithChecksum,
  putComp,
  putItem,
  putPhoto,
  removeItemFully,
  setSetting,
} from "./db.js";
import { importSeed } from "./seed.js";
import {
  cancelResearch,
  displayAsk,
  listingBlurb,
  researchItems,
  researchOne,
  researchFailed,
  researchUnpriced,
  searchLinks,
  showsTested,
  verifyAnthropicKey,
} from "./research.js";
import { keyHint, normalizeApiKey, validateApiKeyShape } from "./keys.js";

const state = {
  items: [],
  photos: new Map(),
  mode: "next",
  currentId: null,
  sessionIds: [],
  filter: "all",
  category: "",
  query: "",
  sort: "newest",
  selectedId: null,
  detailsDirty: false,
  jobStates: {},
  urls: [],
};

const FILTERS = [
  ["all", "All"],
  ["star", "Look closer"],
  ["high", "High"],
  ["medium", "Medium"],
  ["low", "Low"],
  ["bundle", "Bundle"],
  ["photo", "Needs a better photo"],
  ["failed", "Lookup failed"],
  ["estimate", "Preliminary / unsure"],
  ["ready", "Ready to list"],
];

function $(id) {
  return document.getElementById(id);
}

function trackUrl(blob) {
  if (!blob) return "";
  const url = URL.createObjectURL(blob);
  state.urls.push(url);
  return url;
}

function clearUrls() {
  for (const url of state.urls) URL.revokeObjectURL(url);
  state.urls = [];
}

function readDetails() {
  return {
    name: $("f-name").value.trim(),
    category: $("f-category").value.trim(),
    itemDate: $("f-date").value.trim(),
    serial: $("f-serial").value.trim(),
    notes: $("f-notes").value.trim(),
    storageLocation: $("f-where").value.trim(),
  };
}

function fillDetails(item) {
  $("f-name").value = item ? item.name || "" : "";
  $("f-category").value = item ? item.category || "" : "";
  $("f-date").value = item ? item.itemDate || "" : "";
  $("f-serial").value = item ? item.serial || "" : "";
  $("f-notes").value = item ? item.notes || "" : "";
  $("f-where").value = item ? item.storageLocation || "" : "";
}

function rememberSession(id) {
  if (!state.sessionIds.includes(id)) state.sessionIds.push(id);
  sessionStorage.setItem("resale-session", JSON.stringify(state.sessionIds));
}

function chip(item) {
  if (state.jobStates[item.id] === "running") return "Identifying";
  if (item.pricingStatus === "priced") return "Priced";
  if (item.pricingStatus === "estimate") return "Preliminary estimate";
  if (item.pricingStatus === "needs_photo") return "Needs a better photo";
  if (item.pricingStatus === "failed") return "Lookup failed";
  return "Saved";
}

function lookupButtonLabel(item) {
  if (item.pricingStatus === "failed") return "Retry lookup";
  if (item.pricingStatus === "saved") return "Look up price";
  if (item.pricingStatus === "estimate") return "Refine estimate";
  return "Update price using my notes";
}

function priceText(item) {
  if (item.lowUsd == null || item.highUsd == null) {
    if (item.pricingStatus === "saved") return "Tap to price";
    if (item.pricingStatus === "failed") return "Lookup failed";
    return "No price yet";
  }
  return money(item.lowUsd) + " to " + money(item.highUsd);
}

function priceBadge(item) {
  if (item.pricingStatus === "estimate") return "<span class='badge badge-est'>Preliminary estimate</span>";
  if (item.pricingStatus === "needs_photo") return "<span class='badge badge-need'>Add a note or photo</span>";
  if (item.pricingStatus === "priced") return "<span class='badge badge-ok'>Priced</span>";
  return "";
}

function upsideLine(item) {
  if (item.potentialHigh == null) return "";
  if (item.highUsd != null && Number(item.potentialHigh) <= Number(item.highUsd)) return "";
  const cond = item.potentialCondition ? " if " + item.potentialCondition.replace(/^if\s+/i, "") : "";
  return "<p class='upside'>Could reach " + money(item.potentialHigh) + escapeHtml(cond) + "</p>";
}

function tiersHtml(item) {
  const tiers = Array.isArray(item.conditionTiers) ? item.conditionTiers : [];
  if (!tiers.length) return "";
  const body = tiers
    .map((tier) => {
      const range =
        tier.low != null && tier.high != null
          ? money(tier.low) + " to " + money(tier.high)
          : tier.high != null
          ? "up to " + money(tier.high)
          : tier.low != null
          ? money(tier.low) + "+"
          : "";
      return "<tr><th>" + escapeHtml(tier.label) + "</th><td>" + escapeHtml(range) + "</td></tr>";
    })
    .join("");
  return "<p class='tier-title'>Value by condition</p><table class='tiers'>" + body + "</table>";
}

function firstPhoto(itemId) {
  const photos = state.photos.get(itemId) || [];
  return photos[0] || null;
}

function showView(name) {
  state.view = name;
  document.body.dataset.view = name;
  for (const button of document.querySelectorAll(".nav button")) {
    button.classList.toggle("nav-on", button.dataset.view === name);
  }
  for (const view of document.querySelectorAll(".view")) {
    view.classList.toggle("on", view.id === "view-" + name);
  }
  const cameraHidden = name === "settings" || (name !== "camera" && window.innerWidth < 900);
  if (cameraHidden) turnCameraOff();
}

async function reload() {
  state.items = await allItems();
  const photos = await allPhotos();
  state.photos = new Map();
  for (const photo of photos) {
    if (!state.photos.has(photo.itemId)) state.photos.set(photo.itemId, []);
    state.photos.get(photo.itemId).push(photo);
  }
  for (const list of state.photos.values()) list.sort((a, b) => (a.order || 0) - (b.order || 0));
  const comps = await allComps();
  state.comps = new Map();
  for (const comp of comps) {
    if (!state.comps.has(comp.itemId)) state.comps.set(comp.itemId, []);
    state.comps.get(comp.itemId).push(comp);
  }
  render();
}

function render() {
  clearUrls();
  renderTray();
  renderList();
  if (state.selectedId) renderItem(state.selectedId);
}

function renderTray() {
  const tray = $("tray");
  tray.innerHTML = "";
  const items = state.sessionIds.map((id) => state.items.find((item) => item.id === id)).filter(Boolean);
  if (!items.length) {
    tray.innerHTML = "<p class='quiet'>Photos you take now show up here, in the same order.</p>";
    return;
  }
  for (const item of items) tray.appendChild(card(item));
}

function card(item) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "card";
  const photo = firstPhoto(item.id);
  const img = photo ? "<img alt='' src='" + trackUrl(photo.blob) + "'>" : "<img alt=''>";
  const count = (state.photos.get(item.id) || []).length;
  button.innerHTML =
    img +
    "<span><strong>" +
    escapeHtml(item.name || item.id) +
    "</strong><br>" +
    escapeHtml(item.id) +
    " · " +
    count +
    " photo" +
    (count === 1 ? "" : "s") +
    "<br><span class='chip'>" +
    escapeHtml(chip(item)) +
    "</span>" +
    (item.starred ? "<span class='chip star'>Starred</span>" : "") +
    "</span>";
  button.addEventListener("click", () => openItem(item.id));
  return button;
}

function paintHero() {
  const totals = grossTotals(state.items);
  const backedTotals = grossTotals(state.items.filter((item) => item.evidenceBacked));
  const preliminaryTotals = grossTotals(state.items.filter((item) => !item.evidenceBacked));
  const items = state.items.length;
  const preliminary = state.items.filter((item) => item.pricingStatus === "estimate").length;
  $("hero-range").textContent = totals.count ? money(totals.low) + " to " + money(totals.high) : "$0";
  $("hero-count").textContent = items + (items === 1 ? " item" : " items");
  $("hero-backed").textContent = backedTotals.count
    ? "Evidence-backed: " + money(backedTotals.low) + " to " + money(backedTotals.high)
    : "Evidence-backed: $0";
  $("hero-preliminary").textContent = preliminaryTotals.count
    ? "Preliminary: " + money(preliminaryTotals.low) + " to " + money(preliminaryTotals.high)
    : "Preliminary: $0";
  $("hero-note").textContent = totals.count
    ? totals.count +
      " with a range" +
      (preliminary ? ", " + preliminary + " preliminary" : "") +
      ". Gross estimate, not money in hand."
    : "No priced items yet.";
}

function renderList() {
  paintHero();
  const failedCount = state.items.filter((item) => item.pricingStatus === "failed").length;
  const retryAll = $("retry-failed");
  if (retryAll) {
    retryAll.hidden = failedCount === 0;
    retryAll.textContent = failedCount === 1 ? "Retry 1 failed" : "Retry " + failedCount + " failed";
  }

  const filters = $("filters");
  if (!filters.childElementCount) {
    for (const [id, label] of FILTERS) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = label;
      button.dataset.filter = id;
      button.addEventListener("click", () => {
        state.filter = id;
        renderList();
      });
      filters.appendChild(button);
    }
  }
  for (const button of filters.querySelectorAll("button")) {
    button.classList.toggle("on", button.dataset.filter === state.filter);
  }

  const select = $("category-filter");
  const cats = [...new Set(state.items.map((item) => item.category).filter(Boolean))].sort();
  select.innerHTML =
    '<option value="">All categories</option>' +
    cats.map((cat) => '<option value="' + escapeHtml(cat) + '">' + escapeHtml(cat) + "</option>").join("");
  select.value = state.category;

  const sortSelect = $("sort-order");
  if (sortSelect) sortSelect.value = state.sort;

  const query = state.query.trim().toLowerCase();
  const rows = $("rows");
  rows.innerHTML = "";
  const visible = [...state.items].filter((item) => matches(item, query)).sort(sortComparator);
  $("count").textContent = visible.length + " of " + state.items.length + " items";
  if (!visible.length) {
    rows.innerHTML = "<p class='quiet'>Nothing in this filter.</p>";
    return;
  }
  for (const item of visible) rows.appendChild(entry(item));
}

function entry(item) {
  const article = document.createElement("article");
  article.className = "entry";
  const photo = firstPhoto(item.id);
  const count = (state.photos.get(item.id) || []).length;
  const comps = state.comps.get(item.id) || [];
  const links = comps
    .filter((comp) => safeHttpUrl(comp.url))
    .map(
      (comp) =>
        '<a href="' +
        escapeHtml(safeHttpUrl(comp.url)) +
        '" target="_blank" rel="noopener">' +
        escapeHtml(comp.site || comp.url) +
        "</a> (" +
        escapeHtml(comp.kind) +
        ")"
    )
    .join("<br>");
  const rows = [
    ["Category", item.category],
    ["Year", item.year],
    ["Description", item.description],
    ["Quantity", item.quantity],
    ["Condition", item.condition],
    ["Evidence", item.evidence],
    ["Next step", item.nextStep],
    ["My notes", item.notes],
    ["Looked up with", item.lookupLabel],
    ["Why unsure", item.uncertainReason],
  ]
    .filter((row) => row[1])
    .map((row) => "<tr><th>" + escapeHtml(row[0]) + "</th><td>" + escapeHtml(row[1]) + "</td></tr>")
    .join("");
  const failed = item.pricingStatus === "failed";
  const lookupClass = failed || item.pricingStatus === "estimate" ? "retry-go" : "";
  const failBox = failed
    ? "<p class='fail-msg'>" + escapeHtml(item.errorText || "Lookup failed. Tap Retry on the same item.") + "</p>"
    : "";
  const hasRange = item.lowUsd != null && item.highUsd != null;
  article.innerHTML =
    (photo ? '<img alt="" src="' + trackUrl(photo.blob) + '">' : '<img alt="">') +
    "<div><small>" +
    escapeHtml(item.id) +
    " / " +
    escapeHtml(item.category || "No category yet") +
    " · " +
    count +
    " photo" +
    (count === 1 ? "" : "s") +
    (item.starred ? " · Starred" : "") +
    "</small><h2>" +
    escapeHtml(item.name || item.id) +
    "</h2>" +
    failBox +
    "<p class='price" + (hasRange ? "" : " price-empty") + "'>" +
    escapeHtml(priceText(item)) +
    "</p>" +
    priceBadge(item) +
    upsideLine(item) +
    (hasRange && item.askUsd != null ? "<p class='ask'>Suggested ask " + money(displayAsk(item)) + "</p>" : "") +
    "<p class='card-actions'><button type='button' data-open='" +
    escapeHtml(item.id) +
    "'>Open and edit</button> <button type='button' class='" +
    lookupClass +
    "' data-reprice='" +
    escapeHtml(item.id) +
    "'>" +
    escapeHtml(lookupButtonLabel(item)) +
    "</button> <button type='button' class='delete-btn' data-delete='" +
    escapeHtml(item.id) +
    "'>Delete</button></p><details><summary>Description, condition and research</summary>" +
    tiersHtml(item) +
    "<table>" +
    rows +
    (links ? "<tr><th>Sources</th><td>" + links + "</td></tr>" : "") +
    "</table></details></div>";
  article.querySelector("[data-open]").addEventListener("click", () => openItem(item.id));
  article.querySelector("[data-reprice]").addEventListener("click", () => lookupOne(item.id));
  article.querySelector("[data-delete]").addEventListener("click", () => removeItem(item));
  return article;
}

async function removeItem(item) {
  const label = item.name ? item.name + " (" + item.id + ")" : item.id;
  if (!window.confirm("Delete " + label + "? This removes the item and its photos on this device. It cannot be undone.")) {
    return;
  }
  await removeItemFully(item.id);
  state.sessionIds = state.sessionIds.filter((id) => id !== item.id);
  sessionStorage.setItem("resale-session", JSON.stringify(state.sessionIds));
  if (state.selectedId === item.id) {
    state.selectedId = null;
    showView("list");
  }
  await reload();
  $("progress").textContent = "Deleted " + item.id + ".";
}

function sortComparator(a, b) {
  if (state.sort === "newest") return (b.captureOrder || 0) - (a.captureOrder || 0);
  if (state.sort === "priceHigh") return (Number(b.highUsd) || 0) - (Number(a.highUsd) || 0);
  if (state.sort === "priceLow") return (Number(a.lowUsd) || 0) - (Number(b.lowUsd) || 0);
  return (a.captureOrder || 0) - (b.captureOrder || 0);
}

function matches(item, query) {
  if (!filterMatch(item)) return false;
  if (!query) return true;
  const hay = [item.name, item.id, item.category, item.serial, item.notes, item.suggestedName, item.description, item.condition, item.evidence]
    .join(" ")
    .toLowerCase();
  return hay.includes(query);
}

function filterMatch(item) {
  if (state.category && item.category !== state.category) return false;
  if (state.filter === "star") return item.starred;
  if (state.filter === "photo") return item.pricingStatus === "needs_photo";
  if (state.filter === "failed") return item.pricingStatus === "failed";
  if (state.filter === "estimate") return item.pricingStatus === "estimate";
  if (state.filter === "ready") {
    return item.pricingStatus === "priced" && !item.starred && (item.priority === "high" || item.priority === "medium");
  }
  if (["high", "medium", "low", "bundle"].includes(state.filter)) return item.priority === state.filter;
  return true;
}

async function openItem(id) {
  state.selectedId = id;
  showView("item");
  await renderItem(id);
}

async function renderItem(id) {
  const item = state.items.find((row) => row.id === id) || (await getItem(id));
  if (!item) return;
  const photos = state.photos.get(id) || (await photosFor(id));
  const comps = await compsFor(id);
  const settings = await getSettings();
  const body = $("item-body");
  const photoHtml = photos
    .map((photo) => "<img alt='Photo of " + escapeHtml(item.name || item.id) + "' src='" + trackUrl(photo.blob) + "'>")
    .join("");
  const ask = displayAsk(item);
  const clear = item.lowUsd != null && item.highUsd != null
    ? mightClear(item.lowUsd, item.highUsd, settings.feePercent, settings.shippingUsd)
    : null;
  const compHtml = comps
    .filter((comp) => safeHttpUrl(comp.url))
    .map((comp) => {
      const amount = comp.amount == null ? "" : " · " + money(comp.amount);
      return (
        "<p class='comps'><a href='" +
        escapeHtml(safeHttpUrl(comp.url)) +
        "' target='_blank' rel='noopener'>" +
        escapeHtml(comp.site || "Source") +
        "</a> · " +
        escapeHtml(comp.kind) +
        amount +
        (comp.note ? "<br>" + escapeHtml(comp.note) : "") +
        "</p>"
      );
    })
    .join("");
  const links = searchLinks(item)
    .map(
      (link) =>
        "<a href='" + escapeHtml(link.url) + "' target='_blank' rel='noopener'>" + escapeHtml(link.label) + "</a>"
    )
    .join(" · ");
  const dupes = await dupeCandidates(item);

  body.innerHTML =
    "<h2>" +
    escapeHtml(item.name || item.id) +
    "</h2>" +
    "<p>" +
    escapeHtml(item.id) +
    " · " +
    escapeHtml(item.category || "No category yet") +
    "</p>" +
    "<p><span class='chip'>" +
    escapeHtml(chip(item)) +
    "</span>" +
    (item.starred ? "<span class='chip star'>Starred</span>" : "") +
    (item.priority ? "<span class='chip'>" + escapeHtml(priorityLabel(item.priority)) + "</span>" : "") +
    "</p>" +
    "<div class='photos'>" +
    (photoHtml || "<p>No photo yet.</p>") +
    "</div>" +
    "<p class='price" + (item.lowUsd != null && item.highUsd != null ? "" : " price-empty") + "'>" +
    escapeHtml(priceText(item)) +
    "</p>" +
    priceBadge(item) +
    upsideLine(item) +
    tiersHtml(item) +
    (ask != null ? "<p>Suggested ask " + money(ask) + (item.tested === "untested" && showsTested(item) ? " · Untested" : "") + "</p>" : "") +
    (clear ? "<p>You might clear " + money(clear.low) + " to " + money(clear.high) + ". Guess after fees.</p>" : "") +
    (item.evidence ? "<p>" + escapeHtml(item.evidence) + "</p>" : "") +
    (item.nextStep ? "<p>" + escapeHtml(item.nextStep) + "</p>" : "") +
    (item.starReason ? "<p>Star: " + escapeHtml(item.starReason) + "</p>" : "") +
    (item.lookupLabel ? "<p>Looked up with " + escapeHtml(item.lookupLabel) + ".</p>" : "") +
    (item.uncertainReason ? "<p>Why unsure: " + escapeHtml(item.uncertainReason) + "</p>" : "") +
    (item.pricingStatus === "failed"
      ? "<p class='fail-msg'>" + escapeHtml(item.errorText || "Lookup failed.") + "</p>"
      : "") +
    "<p>" +
    links +
    "</p>" +
    "<div class='actions'>" +
    "<button type='button' id='toggle-star'>" +
    (item.starred ? "Unstar" : "Star") +
    "</button>" +
    "<button type='button' data-priority='high'>High</button>" +
    "<button type='button' data-priority='medium'>Medium</button>" +
    "<button type='button' data-priority='low'>Low</button>" +
    "<button type='button' data-priority='bundle'>Bundle</button>" +
    (showsTested(item)
      ? "<button type='button' id='mark-untested'>Untested</button><button type='button' id='mark-tested'>Tested</button>"
      : "") +
    "<button type='button' id='price-one' class='" +
    (item.pricingStatus === "failed" ? "retry-go" : "") +
    "'>" +
    escapeHtml(lookupButtonLabel(item)) +
    "</button>" +
    (item.pricingStatus === "failed"
      ? ""
      : "<button type='button' id='refresh-one'>Update price using my notes</button>") +
    "<button type='button' id='copy-blurb'>Copy listing</button>" +
    "<button type='button' id='delete-item' class='delete-btn'>Delete this item</button>" +
    "</div>" +
    "<pre id='blurb'>" +
    escapeHtml(listingBlurb(item)) +
    "</pre>" +
    compHtml +
    dupes.map((other) => dupeHtml(item, other)).join("") +
    "<div class='edit-note'>" +
    "<label>What I know about this<br><small>Add things like electric, working, in the original box, or a model number. Then re-price.</small>" +
    "<textarea id='edit-notes' placeholder='Electric and working. Lights up. In the original box. Model G-011.'>" +
    escapeHtml(item.notes || "") +
    "</textarea></label>" +
    "<div class='actions'>" +
    "<button type='button' id='save-note'>Save note</button>" +
    "<button type='button' id='save-refine' class='retry-go'>Save note and re-price</button>" +
    "</div></div>" +
    "<details class='edit-more'><summary>Edit name, category, and more</summary>" +
    "<label>Name <input id='edit-name' value='" +
    escapeHtml(item.name || "") +
    "'></label>" +
    "<label>Category <input id='edit-category' value='" +
    escapeHtml(item.category || "") +
    "'></label>" +
    "<label>Item date <input id='edit-date' value='" +
    escapeHtml(item.itemDate || "") +
    "'></label>" +
    "<label>Serial <input id='edit-serial' value='" +
    escapeHtml(item.serial || "") +
    "'></label>" +
    "<label>Where it is stored <input id='edit-where' value='" +
    escapeHtml(item.storageLocation || "") +
    "'></label>" +
    "<button type='button' id='save-details'>Save these details</button>" +
    "</details>";

  $("toggle-star").addEventListener("click", async () => {
    item.starred = !item.starred;
    item.starTouched = true;
    if (!item.starred) item.starReason = "";
    await putItem(item);
    await reload();
    await renderItem(id);
  });
  for (const button of body.querySelectorAll("[data-priority]")) {
    button.addEventListener("click", async () => {
      item.priority = button.dataset.priority;
      item.priorityTouched = true;
      await putItem(item);
      await reload();
      await renderItem(id);
    });
  }
  if ($("mark-untested")) {
    $("mark-untested").addEventListener("click", () => setTested(item, "untested"));
    $("mark-tested").addEventListener("click", () => setTested(item, "tested"));
  }
  $("price-one").addEventListener("click", () => lookupOne(item.id));
  if ($("refresh-one")) $("refresh-one").addEventListener("click", () => lookupOne(item.id));
  $("copy-blurb").addEventListener("click", async () => {
    const text = listingBlurb(item);
    try {
      await navigator.clipboard.writeText(text);
      $("progress").textContent = "Listing copied.";
    } catch (err) {
      $("progress").textContent = text;
    }
  });
  for (const button of body.querySelectorAll("[data-merge]")) {
    button.addEventListener("click", () => mergePair(button.dataset.keep, button.dataset.drop));
  }
  for (const button of body.querySelectorAll("[data-different]")) {
    button.addEventListener("click", () => markDifferent(item.id, button.dataset.different));
  }
  $("save-note").addEventListener("click", () => saveEdits(item, { refine: false }));
  $("save-refine").addEventListener("click", () => saveEdits(item, { refine: true }));
  if ($("save-details")) $("save-details").addEventListener("click", () => saveEdits(item, { refine: false }));
  $("delete-item").addEventListener("click", () => removeItem(item));
}

function dupeHtml(item, other) {
  const earlier = (item.captureOrder || 0) <= (other.captureOrder || 0) ? item.id : other.id;
  const later = earlier === item.id ? other.id : item.id;
  return (
    "<p>This photo also matches " +
    escapeHtml(other.id) +
    ".</p><div class='actions'><button type='button' data-merge='1' data-keep='" +
    earlier +
    "' data-drop='" +
    later +
    "'>Same item</button><button type='button' data-different='" +
    escapeHtml(other.id) +
    "'>Different item</button></div>"
  );
}

async function dupeCandidates(item) {
  const photos = state.photos.get(item.id) || [];
  const ids = new Set();
  for (const photo of photos) {
    const rows = await photosWithChecksum(photo.checksum);
    for (const row of rows) {
      if (row.itemId !== item.id && !(item.dismissedDupes || []).includes(row.itemId)) ids.add(row.itemId);
    }
  }
  for (const [otherId, otherPhotos] of state.photos) {
    if (otherId === item.id || (item.dismissedDupes || []).includes(otherId)) continue;
    const visuallySimilar = photos.some((photo) =>
      otherPhotos.some(
        (other) =>
          photo.perceptualHash &&
          other.perceptualHash &&
          hashDistance(photo.perceptualHash, other.perceptualHash) <= 8
      )
    );
    if (visuallySimilar) ids.add(otherId);
  }
  for (const other of state.items) {
    if (other.id === item.id || (item.dismissedDupes || []).includes(other.id)) continue;
    const sameSerial =
      item.serial &&
      other.serial &&
      normalizedIdentity(item.serial) === normalizedIdentity(other.serial);
    const sameNamedItem =
      normalizedIdentity(item.name) &&
      normalizedIdentity(item.name) === normalizedIdentity(other.name) &&
      normalizedIdentity(item.category) === normalizedIdentity(other.category);
    if (sameSerial || sameNamedItem) ids.add(other.id);
  }
  const found = [];
  for (const id of ids) {
    const other = state.items.find((row) => row.id === id) || (await getItem(id));
    if (other) found.push(other);
  }
  return found;
}

async function mergePair(keepId, dropId) {
  const keepItem = await getItem(keepId);
  const dropItem = await getItem(dropId);
  if (!keepItem || !dropItem) return;
  const merged = mergeMatchingItem(keepItem, dropItem);
  const conflicts = [];
  for (const [label, key] of [
    ["name", "name"],
    ["category", "category"],
    ["item date", "itemDate"],
    ["serial/model", "serial"],
    ["storage location", "storageLocation"],
  ]) {
    const kept = String(keepItem[key] || "").trim();
    const dropped = String(dropItem[key] || "").trim();
    if (kept && dropped && kept !== dropped) conflicts.push("Other " + label + ": " + dropped);
  }
  if (conflicts.length) merged.notes = joinDistinct(merged.notes, conflicts.join("\n"));
  merged.dismissedDupes = [
    ...new Set([...(keepItem.dismissedDupes || []), ...(dropItem.dismissedDupes || [])]),
  ].filter((id) => id !== keepId && id !== dropId);
  await putItem(merged);

  const keepPhotos = await photosFor(keepId);
  const seen = new Set(keepPhotos.map((photo) => photo.checksum));
  let order = keepPhotos.length;
  for (const photo of await photosFor(dropId)) {
    if (seen.has(photo.checksum)) {
      await deletePhoto(photo.id);
      continue;
    }
    photo.itemId = keepId;
    photo.order = order;
    order += 1;
    await putPhoto(photo);
    seen.add(photo.checksum);
  }
  for (const comp of await compsFor(dropId)) {
    comp.itemId = keepId;
    await putComp(comp);
  }
  await deleteItem(dropId);
  state.sessionIds = state.sessionIds.filter((id) => id !== dropId);
  sessionStorage.setItem("resale-session", JSON.stringify(state.sessionIds));
  state.selectedId = keepId;
  await reload();
  await renderItem(keepId);
}

async function markDifferent(id, otherId) {
  const item = await getItem(id);
  const other = await getItem(otherId);
  item.dismissedDupes = [...(item.dismissedDupes || []), otherId];
  other.dismissedDupes = [...(other.dismissedDupes || []), id];
  await putItem(item);
  await putItem(other);
  await reload();
  await renderItem(id);
}

async function saveEdits(item, opts = {}) {
  const current = await getItem(item.id);
  if ($("edit-notes")) current.notes = $("edit-notes").value.trim();
  if ($("edit-name")) current.name = $("edit-name").value.trim();
  if ($("edit-category")) current.category = $("edit-category").value.trim();
  if ($("edit-date")) current.itemDate = $("edit-date").value.trim();
  if ($("edit-serial")) current.serial = $("edit-serial").value.trim();
  if ($("edit-where")) current.storageLocation = $("edit-where").value.trim();
  await putItem(current);
  await reload();
  if (opts.refine) {
    await lookupOne(item.id);
  } else {
    $("progress").textContent = "Saved on " + item.id + ".";
  }
}

async function setTested(item, value) {
  item.tested = value;
  await putItem(item);
  await reload();
  await renderItem(item.id);
}

async function lookupOne(itemId) {
  const item = await getItem(itemId);
  if (!item) return;
  const settings = await getSettings();
  if (!settings.apiKey) {
    $("settings-note").textContent = "Add your Anthropic key to look up prices. Your photos stay saved.";
    showView("settings");
    return;
  }
  const retry = item.pricingStatus === "failed";
  $("progress").textContent = retry
    ? "Retrying " + item.id + ". Same item, not a duplicate."
    : "Pricing " + item.id + "…";
  $("cancel-lookup").hidden = false;
  try {
    const job = await researchOne(item, (states, note) => {
      state.jobStates = states;
      const lead = retry ? "Retrying " + item.id : "Pricing " + item.id;
      $("progress").textContent = lead + "." + (note ? " " + note : "");
    });
    const outcome = job && job.states ? job.states[item.id] : "";
    if (outcome === "done") $("progress").textContent = item.id + " priced.";
    else if (outcome === "failed") {
      const again = await getItem(item.id);
      $("progress").textContent = again.errorText || "Lookup failed again.";
    } else if (outcome === "discarded") $("progress").textContent = "Result discarded because the item changed or was deleted.";
    else if (outcome === "cancelled") $("progress").textContent = "Lookup cancelled. The item was kept.";
  } catch (err) {
    $("progress").textContent = err.message;
  } finally {
    $("cancel-lookup").hidden = true;
  }
  state.jobStates = {};
  await reload();
  if (state.selectedId === item.id) await renderItem(item.id);
}

function priorityLabel(priority) {
  if (priority === "high") return "High";
  if (priority === "medium") return "Medium";
  if (priority === "low") return "Low";
  if (priority === "bundle") return "Bundle";
  return priority;
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

async function attachPhoto(itemId, blob) {
  const checksum = await checksumOf(blob);
  const perceptualHash = await perceptualHashOf(blob).catch(() => "");
  const existing = await photosFor(itemId);
  if (existing.some((photo) => photo.checksum === checksum)) {
    $("save-status").textContent = "That photo is already on this item.";
    return;
  }
  await putPhoto({
    id: crypto.randomUUID(),
    itemId,
    order: existing.length,
    checksum,
    perceptualHash,
    createdAt: new Date().toISOString(),
    blob,
  });
  $("save-status").textContent = "Saved";
}

async function createFromBlob(blob) {
  const slot = await allocateItem();
  const item = blankItem(slot.id, slot.captureOrder);
  if (state.detailsDirty) Object.assign(item, readDetails());
  item.priority = autoPriority(item);
  await putItem(item);
  await attachPhoto(item.id, blob);
  state.detailsDirty = false;
  state.currentId = item.id;
  rememberSession(item.id);
  fillDetails(item);
  return item;
}

async function ingestFiles(fileList) {
  const files = [...fileList].filter((file) => file && (file.type.startsWith("image/") || file.size));
  if (!files.length) return;
  if (state.mode === "another") {
    let id = state.currentId;
    for (const file of files) {
      if (!id) {
        const item = await createFromBlob(file);
        id = item.id;
      } else {
        await attachPhoto(id, file);
      }
    }
  } else {
    for (const file of files) await createFromBlob(file);
  }
  await reload();
}

function setCameraButton() {
  const button = $("cam-toggle");
  if (isIphone()) {
    button.hidden = true;
    return;
  }
  button.hidden = false;
  button.textContent = hasPreview() ? "Turn camera off" : "Turn camera on";
}

function turnCameraOff() {
  stopPreview($("preview"));
  $("preview").hidden = true;
  $("shutter").hidden = true;
  if (!isIphone()) $("cam-note").textContent = "Camera is off.";
  setCameraButton();
}

async function turnCameraOn() {
  try {
    await startPreview($("preview"));
    $("preview").hidden = false;
    $("shutter").hidden = false;
    $("cam-note").textContent = "";
  } catch (err) {
    turnCameraOff();
    $("cam-note").textContent = "Camera permission is off. You can still add photos.";
  }
  setCameraButton();
}

function markMode() {
  $("another").classList.toggle("mode-on", state.mode === "another");
  $("next").classList.toggle("mode-on", state.mode === "next");
}

async function runBatchLookup(run) {
  const settings = await getSettings();
  if (!settings.apiKey) {
    $("settings-note").textContent = "Add your Anthropic key to look up prices. Your photos stay saved.";
    showView("settings");
    return;
  }
  $("go").disabled = true;
  if ($("retry-failed")) $("retry-failed").disabled = true;
  $("cancel-lookup").hidden = false;
  try {
    const job = await run((states, note) => {
      state.jobStates = { ...states };
      const ids = Object.keys(states);
      const finished = ids.filter((id) =>
        ["done", "failed", "discarded", "cancelled"].includes(states[id])
      ).length;
      $("progress").textContent = ids.length
        ? "Pricing " + finished + " of " + ids.length + "." + (note ? " " + note : "")
        : "Nothing new to price.";
      render();
    });
    if (!job) $("progress").textContent = "Nothing new to price.";
    else $("progress").textContent = "Lookup finished.";
  } catch (err) {
    $("progress").textContent = err.message;
  } finally {
    $("go").disabled = false;
    if ($("retry-failed")) $("retry-failed").disabled = false;
    $("cancel-lookup").hidden = true;
    state.jobStates = {};
    await reload();
  }
}

async function onFind() {
  await runBatchLookup(researchUnpriced);
}

async function onRetryFailed() {
  await runBatchLookup(researchFailed);
}

async function backupPayload() {
  const items = await allItems();
  const photos = await allPhotos();
  const settings = await getSettings();
  delete settings.apiKey;
  const encoded = [];
  for (const photo of photos) {
    encoded.push({
      id: photo.id,
      itemId: photo.itemId,
      order: photo.order,
      checksum: photo.checksum,
      createdAt: photo.createdAt,
      filename: photo.filename || "",
      blob: await blobToBase64(photo.blob),
      type: photo.blob.type || "image/jpeg",
    });
  }
  const comps = [];
  for (const item of items) comps.push(...(await compsFor(item.id)));
  return { kind: "cj-resale-backup", exportedAt: new Date().toISOString(), items, photos: encoded, comps, settings };
}

function safeHttpUrl(value) {
  try {
    const url = new URL(String(value || ""));
    return url.protocol === "http:" || url.protocol === "https:" ? url.href : "";
  } catch (error) {
    return "";
  }
}

function assertUniqueIds(rows, label) {
  const seen = new Set();
  for (const row of rows) {
    if (!row || typeof row.id !== "string" || !row.id.trim()) {
      throw new Error(label + " contains a row without an ID.");
    }
    if (seen.has(row.id)) throw new Error(label + " contains the ID " + row.id + " more than once.");
    seen.add(row.id);
  }
}

function validateBackupPayload(raw) {
  if (!raw || raw.kind !== "cj-resale-backup") throw new Error("That file is not a Resale backup.");
  if (!Array.isArray(raw.items) || !Array.isArray(raw.photos) || !Array.isArray(raw.comps)) {
    throw new Error("That backup is incomplete. Items, photos, and comps must all be present.");
  }
  assertUniqueIds(raw.items, "Items");
  assertUniqueIds(raw.photos, "Photos");
  assertUniqueIds(raw.comps, "Comps");

  const itemIds = new Set(raw.items.map((item) => item.id));
  for (const photo of raw.photos) {
    if (!itemIds.has(photo.itemId)) throw new Error("Photo " + photo.id + " points to a missing item.");
    if (typeof photo.blob !== "string" && !(photo.blob instanceof Blob)) {
      throw new Error("Photo " + photo.id + " has no usable image data.");
    }
  }
  for (const comp of raw.comps) {
    if (!itemIds.has(comp.itemId)) throw new Error("Comp " + comp.id + " points to a missing item.");
    if (!safeHttpUrl(comp.url)) throw new Error("Comp " + comp.id + " has an unsafe or invalid link.");
  }

  return {
    kind: raw.kind,
    exportedAt: raw.exportedAt || "",
    items: raw.items.map((item) => ({ ...item })),
    photos: raw.photos.map((photo) => ({
      ...photo,
      blob: typeof photo.blob === "string" ? base64ToBlob(photo.blob, photo.type) : photo.blob,
    })),
    comps: raw.comps.map((comp) => ({ ...comp, url: safeHttpUrl(comp.url) })),
    settings: raw.settings && typeof raw.settings === "object" ? { ...raw.settings } : {},
  };
}

function normalizedIdentity(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function joinDistinct(left, right) {
  const a = String(left || "").trim();
  const b = String(right || "").trim();
  if (!a) return b;
  if (!b || a === b || a.includes(b)) return a;
  if (b.includes(a)) return b;
  return a + "\n" + b;
}

function mergeMatchingItem(local, incoming) {
  const merged = { ...incoming, ...local };
  merged.name = local.name || incoming.name || "";
  merged.category = local.category || incoming.category || "";
  merged.itemDate = local.itemDate || incoming.itemDate || "";
  merged.serial = local.serial || incoming.serial || "";
  merged.storageLocation = local.storageLocation || incoming.storageLocation || "";
  merged.notes = joinDistinct(local.notes, incoming.notes);
  merged.description = joinDistinct(local.description, incoming.description);

  if (local.lowUsd == null && incoming.lowUsd != null) {
    for (const key of [
      "lowUsd",
      "highUsd",
      "askUsd",
      "potentialHigh",
      "potentialCondition",
      "conditionTiers",
      "pricingConfidence",
      "pricingStatus",
      "evidence",
      "nextStep",
      "uncertainReason",
      "lookupModel",
      "lookupLabel",
    ]) {
      merged[key] = incoming[key];
    }
  }
  return merged;
}

async function prepareMergedImport(incoming) {
  const localItems = await allItems();
  const localPhotos = await allPhotos();
  const localComps = await allComps();
  const localById = new Map(localItems.map((item) => [item.id, item]));
  const localPhotoIds = new Set(localPhotos.map((photo) => photo.id));
  const localCompIds = new Set(localComps.map((comp) => comp.id));
  const checksumsByItem = new Map();
  for (const photo of localPhotos) {
    if (!checksumsByItem.has(photo.itemId)) checksumsByItem.set(photo.itemId, new Set());
    checksumsByItem.get(photo.itemId).add(photo.checksum);
  }

  let next = Math.max(
    Number((await getSettings()).nextNumber) || 1,
    ...localItems.map((item) => Number(String(item.id).match(/\d+/)?.[0]) + 1 || 1),
    ...incoming.items.map((item) => Number(String(item.id).match(/\d+/)?.[0]) + 1 || 1)
  );
  let captureOrder = localItems.reduce((max, item) => Math.max(max, Number(item.captureOrder) || 0), 0);
  const targetByIncomingId = new Map();
  const outputItems = [];

  for (const item of incoming.items) {
    const local = localById.get(item.id);
    if (!local) {
      targetByIncomingId.set(item.id, item.id);
      outputItems.push(item);
      continue;
    }
    const incomingChecksums = new Set(
      incoming.photos.filter((photo) => photo.itemId === item.id).map((photo) => photo.checksum)
    );
    const checksumMatch = [...incomingChecksums].some((checksum) => checksumsByItem.get(item.id)?.has(checksum));
    const nameMatch =
      normalizedIdentity(local.name) &&
      normalizedIdentity(local.name) === normalizedIdentity(item.name);
    if (checksumMatch || nameMatch) {
      targetByIncomingId.set(item.id, item.id);
      outputItems.push(mergeMatchingItem(local, item));
      continue;
    }

    const newId = "CJ-" + String(next++).padStart(3, "0");
    captureOrder += 1;
    targetByIncomingId.set(item.id, newId);
    outputItems.push({
      ...item,
      id: newId,
      captureOrder,
      name: item.name ? item.name + " (imported)" : newId + " imported item",
    });
  }

  const outputPhotos = [];
  for (const photo of incoming.photos) {
    const target = targetByIncomingId.get(photo.itemId);
    const sameTargetChecksums = checksumsByItem.get(target) || new Set();
    if (sameTargetChecksums.has(photo.checksum)) continue;
    const id = localPhotoIds.has(photo.id) ? crypto.randomUUID() : photo.id;
    localPhotoIds.add(id);
    sameTargetChecksums.add(photo.checksum);
    checksumsByItem.set(target, sameTargetChecksums);
    outputPhotos.push({ ...photo, id, itemId: target });
  }

  const outputComps = incoming.comps.map((comp) => {
    const id = localCompIds.has(comp.id) ? crypto.randomUUID() : comp.id;
    localCompIds.add(id);
    return { ...comp, id, itemId: targetByIncomingId.get(comp.itemId) };
  });

  return {
    ...incoming,
    items: outputItems,
    photos: outputPhotos,
    comps: outputComps,
    settings: { ...incoming.settings, nextNumber: next },
  };
}

function bind() {
  for (const button of document.querySelectorAll(".nav button")) {
    button.addEventListener("click", () => showView(button.dataset.view));
  }
  $("go").addEventListener("click", onFind);
  $("retry-failed").addEventListener("click", onRetryFailed);
  $("cancel-lookup").addEventListener("click", () => {
    cancelResearch();
    $("progress").textContent = "Cancelling after the current response…";
  });
  $("take").addEventListener("change", (event) => {
    ingestFiles(event.target.files);
    event.target.value = "";
  });
  $("choose").addEventListener("change", (event) => {
    ingestFiles(event.target.files);
    event.target.value = "";
  });
  $("shutter").addEventListener("click", async () => {
    const blob = await grabFrame($("preview"));
    if (blob) await ingestFiles([blob]);
  });
  $("cam-toggle").addEventListener("click", () => {
    if (hasPreview()) turnCameraOff();
    else turnCameraOn();
  });
  $("another").addEventListener("click", () => {
    state.mode = "another";
    markMode();
    const current = state.items.find((item) => item.id === state.currentId);
    if (current) fillDetails(current);
  });
  $("next").addEventListener("click", () => {
    state.mode = "next";
    state.detailsDirty = false;
    fillDetails(null);
    markMode();
  });
  $("details").addEventListener("input", async () => {
    state.detailsDirty = true;
    if (state.mode === "another" && state.currentId) {
      const item = await getItem(state.currentId);
      if (!item) return;
      Object.assign(item, readDetails());
      await putItem(item);
    }
  });
  const camera = $("view-camera");
  camera.addEventListener("dragover", (event) => event.preventDefault());
  camera.addEventListener("drop", (event) => {
    event.preventDefault();
    ingestFiles(event.dataTransfer.files);
  });
  $("search").addEventListener("input", () => {
    state.query = $("search").value;
    renderList();
  });
  $("category-filter").addEventListener("change", () => {
    state.category = $("category-filter").value;
    renderList();
  });
  $("sort-order").addEventListener("change", () => {
    state.sort = $("sort-order").value;
    renderList();
  });
  $("describe-go").addEventListener("click", describeItem);
  $("back").addEventListener("click", () => {
    state.selectedId = null;
    showView("list");
  });
  $("save-settings").addEventListener("click", saveSettings);
  $("test-key").addEventListener("click", testSavedKey);
  $("export-backup").addEventListener("click", downloadBackup);
  $("share-backup").addEventListener("click", shareBackup);
  $("import-backup").addEventListener("change", importBackup);
  $("restore-import").addEventListener("click", restoreLastImport);
}

async function describeItem() {
  const text = $("describe").value.trim();
  if (text.length < 8) {
    $("progress").textContent = "Add a little more, like the year and the name.";
    return;
  }
  const settings = await getSettings();
  if (!settings.apiKey) {
    $("settings-note").textContent = "Add your Anthropic key to look up prices. Your photos stay saved.";
    showView("settings");
    return;
  }
  const slot = await allocateItem();
  const item = blankItem(slot.id, slot.captureOrder);
  item.name = text.length > 140 ? text.slice(0, 137) + "..." : text;
  item.notes = text;
  item.description = text;
  await putItem(item);
  $("describe").value = "";
  await reload();
  await openItem(item.id);
  await lookupOne(item.id);
}

async function testSavedKey() {
  const settings = await getSettings();
  if (!settings.apiKey) {
    $("settings-note").textContent = "Paste your Anthropic key, tap Save settings, and wait for Key works.";
    return;
  }
  $("settings-note").textContent = "Checking key on this browser…";
  try {
    await verifyAnthropicKey(settings);
    $("settings-note").textContent = "Key works on this browser. " + keyHint(settings.apiKey) + ".";
  } catch (err) {
    $("settings-note").textContent = err.message;
  }
}

async function saveSettings() {
  const typed = normalizeApiKey($("api-key").value);
  if (typed) {
    const shape = validateApiKeyShape(typed);
    if (shape) {
      $("settings-note").textContent = shape;
      return;
    }
    await setSetting("apiKey", typed);
  }
  await setSetting("feePercent", Number($("fee").value) || 0);
  await setSetting("shippingUsd", Number($("ship").value) || 0);
  await setSetting("haikuModel", $("haiku").value.trim() || "claude-haiku-4-5");
  await setSetting("sonnetModel", $("sonnet").value.trim() || "claude-sonnet-4-6");
  await setSetting("maxItemsPerRun", Math.max(1, Math.min(25, Number($("max-items").value) || 10)));
  $("api-key").value = "";
  const saved = (await getSettings()).apiKey;
  const hint = saved ? keyHint(saved) : "";
  $("api-key").placeholder = saved ? "Key saved on this browser" + (hint ? " · " + hint : "") : "Paste your key";
  if (saved) await testSavedKey();
  else $("settings-note").textContent = "Saved. Paste a key in the box to look up prices.";
  await reload();
}

async function downloadBackup() {
  const payload = await backupPayload();
  const blob = new Blob([JSON.stringify(payload)], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "resale-backup.json";
  link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 2000);
}

async function shareBackup() {
  const payload = await backupPayload();
  const file = new File([JSON.stringify(payload)], "resale-backup.json", { type: "application/json" });
  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    try {
      await navigator.share({ files: [file], title: "Resale backup" });
      return;
    } catch (err) {
      if (err.name === "AbortError") return;
    }
  }
  await downloadBackup();
}

async function importBackup(event) {
  const file = event.target.files && event.target.files[0];
  event.target.value = "";
  if (!file) return;
  try {
    const parsed = JSON.parse(await file.text());
    const validated = validateBackupPayload(parsed);
    const mode = $("import-mode").value === "replace" ? "replace" : "merge";
    if (
      mode === "replace" &&
      !window.confirm(
        "Replace this entire catalog with the backup? A private recovery copy will be saved so you can undo once."
      )
    ) {
      $("settings-note").textContent = "Import cancelled. Nothing changed.";
      return;
    }

    const recovery = await backupPayload();
    const payload = mode === "merge" ? await prepareMergedImport(validated) : validated;
    await importCatalogAtomic(payload, { mode, recovery });
    $("restore-import").hidden = false;
    $("settings-note").textContent =
      mode === "merge"
        ? "Backup merged safely. Existing items were kept; ID conflicts became imported copies."
        : "Backup replaced this catalog. Tap Undo last import if that was not what you wanted.";
    await reload();
  } catch (error) {
    $("settings-note").textContent = "Import stopped before changing anything: " + (error.message || "Invalid backup.");
  }
}

async function restoreLastImport() {
  const recovery = await getRecoveryBackup();
  if (!recovery || !recovery.payload) {
    $("settings-note").textContent = "There is no import to undo.";
    return;
  }
  if (!window.confirm("Undo the last import and restore the catalog from " + recovery.savedAt + "?")) return;
  try {
    const current = await backupPayload();
    const payload = validateBackupPayload(recovery.payload);
    await importCatalogAtomic(payload, { mode: "replace", recovery: current });
    $("settings-note").textContent = "The catalog from before the last import was restored.";
    await reload();
  } catch (error) {
    $("settings-note").textContent = "Restore stopped without changing the catalog: " + (error.message || "Invalid recovery.");
  }
}

async function fillSettings() {
  const settings = await getSettings();
  $("fee").value = settings.feePercent;
  $("ship").value = settings.shippingUsd;
  $("haiku").value = settings.haikuModel;
  $("sonnet").value = settings.sonnetModel;
  $("max-items").value = settings.maxItemsPerRun;
  $("api-key").value = "";
  $("api-key").placeholder = settings.apiKey ? "Key saved on this browser" : "Paste your key";
  $("restore-import").hidden = !(await getRecoveryBackup());
  if (settings.apiKey) {
    $("settings-note").textContent =
      "A key is already saved on this browser (" +
      keyHint(settings.apiKey) +
      "). Tap Test key, or paste a new key and Save settings.";
  }
}

async function start() {
  bind();
  try {
    state.sessionIds = JSON.parse(sessionStorage.getItem("resale-session") || "[]");
  } catch (err) {
    state.sessionIds = [];
  }
  try {
    await importSeed((done, total) => {
      $("boot").textContent = "Loading starter items " + done + " of " + total;
    });
    const job = await getJob();
    if (job && job.running) {
      const heartbeat = new Date(job.heartbeatAt || job.startedAt || 0).getTime();
      const recent = Date.now() - heartbeat < 10 * 60 * 1000;
      $("progress").textContent = recent
        ? "A lookup may still be running in another tab. The app will not start a second one."
        : "The previous lookup stopped. Tap Find resale prices to continue. Photos are still saved.";
    }
    await fillSettings();
    await reload();
    $("boot").hidden = true;
    turnCameraOff();
    showView("list");
    if ("serviceWorker" in navigator) navigator.serviceWorker.register("./sw.js").catch(() => {});
  } catch (err) {
    $("boot").textContent = err.message || "Could not open the catalog";
  }
}

start();
