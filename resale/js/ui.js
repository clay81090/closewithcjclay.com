// Screen controller. Camera first. Prices only after Find resale prices.

import { checksumOf, grabFrame, hasPreview, isIphone, startPreview, stopPreview } from "./camera.js";
import {
  allItems,
  allPhotos,
  allocateItem,
  autoPriority,
  base64ToBlob,
  blankItem,
  blobToBase64,
  compsFor,
  deleteItem,
  deletePhoto,
  getItem,
  getJob,
  getSettings,
  grossTotals,
  mightClear,
  money,
  photosFor,
  photosWithChecksum,
  putComp,
  putItem,
  putPhoto,
  replaceCatalog,
  saveJob,
  setSetting,
} from "./db.js";
import { importSeed } from "./seed.js";
import {
  displayAsk,
  listingBlurb,
  researchItems,
  researchOne,
  researchUnpriced,
  searchLinks,
  showsTested,
} from "./research.js";

const state = {
  items: [],
  photos: new Map(),
  mode: "next",
  currentId: null,
  sessionIds: [],
  filter: "all",
  query: "",
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
  if (item.pricingStatus === "needs_photo") return "Needs a better photo";
  if (item.pricingStatus === "failed") return "Lookup failed";
  return "Saved";
}

function priceText(item) {
  if (item.lowUsd == null || item.highUsd == null) {
    if (item.pricingStatus === "saved") return "Saved, price not looked up yet";
    if (item.pricingStatus === "failed") return item.errorText || "Lookup failed";
    return "No sold price yet";
  }
  return money(item.lowUsd) + " to " + money(item.highUsd);
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

function renderList() {
  $("count").textContent = state.items.length + " items";
  const totals = grossTotals(state.items);
  $("totals").textContent =
    (totals.count
      ? money(totals.low) + " to " + money(totals.high) + " across " + totals.count + " priced items. "
      : "No priced items yet. ") +
    "October 11, 2026 starter prices are included. Gross estimate, not money in hand.";

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

  const query = state.query.trim().toLowerCase();
  const rows = $("rows");
  rows.innerHTML = "";
  const visible = [...state.items].reverse().filter((item) => matches(item, query));
  if (!visible.length) {
    rows.innerHTML = "<p class='quiet'>Nothing in this filter.</p>";
    return;
  }
  for (const item of visible) rows.appendChild(card(item));
}

function matches(item, query) {
  if (!filterMatch(item)) return false;
  if (!query) return true;
  const hay = [item.name, item.id, item.category, item.serial, item.notes, item.suggestedName]
    .join(" ")
    .toLowerCase();
  return hay.includes(query);
}

function filterMatch(item) {
  if (state.filter === "star") return item.starred;
  if (state.filter === "photo") return item.pricingStatus === "needs_photo";
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
    .map((comp) => {
      const amount = comp.amount == null ? "" : " · " + money(comp.amount);
      return (
        "<p class='comps'><a href='" +
        escapeHtml(comp.url) +
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
    "<p><strong>" +
    escapeHtml(priceText(item)) +
    "</strong></p>" +
    (ask != null ? "<p>Suggested ask " + money(ask) + (item.tested === "untested" && showsTested(item) ? " · Untested" : "") + "</p>" : "") +
    (clear ? "<p>You might clear " + money(clear.low) + " to " + money(clear.high) + ". Guess after fees.</p>" : "") +
    (item.evidence ? "<p>" + escapeHtml(item.evidence) + "</p>" : "") +
    (item.nextStep ? "<p>" + escapeHtml(item.nextStep) + "</p>" : "") +
    (item.starReason ? "<p>Star: " + escapeHtml(item.starReason) + "</p>" : "") +
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
    "<button type='button' id='price-one'>Price this item</button>" +
    "<button type='button' id='refresh-one'>Refresh price</button>" +
    "<button type='button' id='copy-blurb'>Copy listing</button>" +
    "</div>" +
    "<pre id='blurb'>" +
    escapeHtml(listingBlurb(item)) +
    "</pre>" +
    compHtml +
    dupes.map((other) => dupeHtml(item, other)).join("") +
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
    "<label>Note <input id='edit-notes' value='" +
    escapeHtml(item.notes || "") +
    "'></label>" +
    "<label>Where it is stored <input id='edit-where' value='" +
    escapeHtml(item.storageLocation || "") +
    "'></label>";

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
  $("price-one").addEventListener("click", () => lookupOne(item));
  $("refresh-one").addEventListener("click", () => lookupOne(item));
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
  for (const input of ["edit-name", "edit-category", "edit-date", "edit-serial", "edit-notes", "edit-where"]) {
    $(input).addEventListener("change", () => saveEdits(item));
  }
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
  const found = [];
  for (const id of ids) {
    const other = state.items.find((row) => row.id === id) || (await getItem(id));
    if (other) found.push(other);
  }
  return found;
}

async function mergePair(keepId, dropId) {
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

async function saveEdits(item) {
  item.name = $("edit-name").value.trim();
  item.category = $("edit-category").value.trim();
  item.itemDate = $("edit-date").value.trim();
  item.serial = $("edit-serial").value.trim();
  item.notes = $("edit-notes").value.trim();
  item.storageLocation = $("edit-where").value.trim();
  await putItem(item);
  await reload();
}

async function setTested(item, value) {
  item.tested = value;
  await putItem(item);
  await reload();
  await renderItem(item.id);
}

async function lookupOne(item) {
  const settings = await getSettings();
  if (!settings.apiKey) {
    $("settings-note").textContent = "Add your Anthropic key to look up prices. Your photos stay saved.";
    showView("settings");
    return;
  }
  $("progress").textContent = "Pricing " + item.id + "…";
  try {
    await researchOne(item, (states) => {
      state.jobStates = states;
      $("progress").textContent = "Pricing " + item.id + "…";
    });
  } catch (err) {
    $("progress").textContent = err.message;
  }
  await reload();
  await renderItem(item.id);
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
    .replace(/"/g, "&quot;");
}

async function attachPhoto(itemId, blob) {
  const checksum = await checksumOf(blob);
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

async function onFind() {
  const settings = await getSettings();
  if (!settings.apiKey) {
    $("settings-note").textContent = "Add your Anthropic key to look up prices. Your photos stay saved.";
    showView("settings");
    return;
  }
  const running = await getJob();
  if (running && running.running) {
    state.jobStates = running.states || {};
    $("progress").textContent = "A lookup is already running.";
    render();
    return;
  }
  $("go").disabled = true;
  try {
    const job = await researchUnpriced((states) => {
      state.jobStates = { ...states };
      const ids = Object.keys(states);
      const finished = ids.filter((id) => states[id] === "done" || states[id] === "failed").length;
      $("progress").textContent = ids.length ? "Pricing " + finished + " of " + ids.length : "Nothing new to price.";
      render();
    });
    if (!job) $("progress").textContent = "Nothing new to price.";
    else $("progress").textContent = "Lookup finished.";
  } catch (err) {
    $("progress").textContent = err.message;
  } finally {
    $("go").disabled = false;
    state.jobStates = {};
    await reload();
  }
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

function bind() {
  for (const button of document.querySelectorAll(".nav button")) {
    button.addEventListener("click", () => showView(button.dataset.view));
  }
  $("go").addEventListener("click", onFind);
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
  $("back").addEventListener("click", () => {
    state.selectedId = null;
    showView("list");
  });
  $("save-settings").addEventListener("click", saveSettings);
  $("export-backup").addEventListener("click", downloadBackup);
  $("share-backup").addEventListener("click", shareBackup);
  $("import-backup").addEventListener("change", importBackup);
}

async function saveSettings() {
  await setSetting("apiKey", $("api-key").value.trim());
  await setSetting("feePercent", Number($("fee").value) || 0);
  await setSetting("shippingUsd", Number($("ship").value) || 0);
  await setSetting("haikuModel", $("haiku").value.trim() || "claude-haiku-4-5");
  await setSetting("sonnetModel", $("sonnet").value.trim() || "claude-sonnet-4-6");
  $("settings-note").textContent = "Saved on this browser.";
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
  const payload = JSON.parse(await file.text());
  if (!payload || payload.kind !== "cj-resale-backup" || !Array.isArray(payload.items)) {
    $("settings-note").textContent = "That file is not a Resale backup.";
    return;
  }
  payload.photos = (payload.photos || []).map((photo) => ({
    ...photo,
    blob: typeof photo.blob === "string" ? base64ToBlob(photo.blob, photo.type) : photo.blob,
  }));
  await replaceCatalog(payload);
  $("settings-note").textContent = "Backup imported on this browser. Your key was left as it was.";
  await reload();
}

async function fillSettings() {
  const settings = await getSettings();
  $("fee").value = settings.feePercent;
  $("ship").value = settings.shippingUsd;
  $("haiku").value = settings.haikuModel;
  $("sonnet").value = settings.sonnetModel;
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
      job.running = false;
      await saveJob(job);
      $("progress").textContent = "The last lookup stopped. Tap Find resale prices to continue. Photos are still saved.";
    }
    await fillSettings();
    await reload();
    $("boot").hidden = true;
    turnCameraOff();
    if ("serviceWorker" in navigator) navigator.serviceWorker.register("./sw.js").catch(() => {});
  } catch (err) {
    $("boot").textContent = err.message || "Could not open the catalog";
  }
}

start();
