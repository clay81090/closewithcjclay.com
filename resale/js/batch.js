// Smart batch import. Photos are reviewed before one atomic catalog save.

import { allPhotos, getSettings, itemQuantity, saveNewItemBatch } from "./db.js";
import { checksumOf, perceptualHashOf } from "./camera.js";
import { explainApiFailure, normalizeApiKey } from "./keys.js";

const PHOTOS_PER_REQUEST = 40;

function $(id) {
  return document.getElementById(id);
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

async function smallImage(blob) {
  const bitmap = await createImageBitmap(blob);
  const scale = Math.min(1, 640 / Math.max(bitmap.width, bitmap.height));
  const canvas = document.createElement("canvas");
  canvas.width = Math.max(1, Math.round(bitmap.width * scale));
  canvas.height = Math.max(1, Math.round(bitmap.height * scale));
  canvas.getContext("2d").drawImage(bitmap, 0, 0, canvas.width, canvas.height);
  bitmap.close();
  return new Promise((resolve) => canvas.toBlob((result) => resolve(result || blob), "image/jpeg", 0.72));
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

function parseJsonResponse(data) {
  const text = (data.content || [])
    .filter((block) => block.type === "text" && block.text)
    .map((block) => block.text)
    .join("\n");
  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");
  if (start < 0 || end < start) throw new Error("The photo sorter did not return usable groups.");
  try {
    return JSON.parse(text.slice(start, end + 1));
  } catch (error) {
    throw new Error("The photo sorter returned malformed groups. No catalog items were changed.");
  }
}

async function groupChunk(settings, photos) {
  const content = [
    {
      type: "text",
      text:
        "Sort these resale photos into physical items. Return JSON only, no markdown.\n" +
        "Group front, back, label, box, and detail views of the SAME physical item together. " +
        "Keep different products, printed names, characters, editions, models, boxes, dolls, cards, or serial numbers separate even when they share a category. " +
        "A single photo can belong to only one group. Use every photo number exactly once. " +
        "Give each group a useful visible name and category. Quantity is normally 1. Use quantity above 1 only when a photo clearly shows a multi-piece lot; the owner can change it during review.\n" +
        'JSON shape: {"groups":[{"photos":[1,2],"name":"","category":"","quantity":1,"reason":""}]}',
    },
  ];

  for (const photo of photos) {
    content.push({ type: "text", text: "PHOTO " + photo.number + " · " + photo.file.name });
    const smaller = await smallImage(photo.file);
    content.push({
      type: "image",
      source: { type: "base64", media_type: "image/jpeg", data: await toBase64(smaller) },
    });
  }

  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": normalizeApiKey(settings.apiKey),
      "anthropic-version": "2023-06-01",
      "anthropic-dangerous-direct-browser-access": "true",
    },
    body: JSON.stringify({
      model: settings.haikuModel || "claude-haiku-4-5",
      max_tokens: 4096,
      messages: [{ role: "user", content }],
    }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data.error && data.error.message ? data.error.message : "Photo sorting failed";
    throw new Error(explainApiFailure(response.status, message));
  }
  return parseJsonResponse(data);
}

function normalizeGroups(rawGroups, photos) {
  const byNumber = new Map(photos.map((photo) => [photo.number, photo]));
  const used = new Set();
  const groups = [];
  for (const raw of Array.isArray(rawGroups) ? rawGroups : []) {
    const grouped = [];
    for (const value of Array.isArray(raw.photos) ? raw.photos : []) {
      const number = Number(value);
      if (!byNumber.has(number) || used.has(number)) continue;
      used.add(number);
      grouped.push(byNumber.get(number));
    }
    if (!grouped.length) continue;
    groups.push({
      id: crypto.randomUUID(),
      photos: grouped,
      name: String(raw.name || "").trim(),
      category: String(raw.category || "").trim(),
      quantity: Math.max(1, Math.min(9999, Number(raw.quantity) || 1)),
      reason: String(raw.reason || "").trim(),
    });
  }
  for (const photo of photos) {
    if (used.has(photo.number)) continue;
    groups.push({
      id: crypto.randomUUID(),
      photos: [photo],
      name: "",
      category: "",
      quantity: 1,
      reason: "Kept separate because the sorter did not confidently match it.",
    });
  }
  return groups;
}

export function initSmartBatch({ onSaved, onNeedsKey }) {
  let photos = [];
  let groups = [];
  let running = false;

  const releasePhotos = () => {
    for (const photo of photos) URL.revokeObjectURL(photo.url);
    photos = [];
  };

  const syncReviewEdits = () => {
    for (const card of $("smart-batch-review").querySelectorAll("[data-group]")) {
      const group = groups.find((row) => row.id === card.dataset.group);
      if (!group) continue;
      group.name = card.querySelector("[data-name]").value.trim();
      group.category = card.querySelector("[data-category]").value.trim();
      group.quantity = itemQuantity({ unitCount: card.querySelector("[data-quantity]").value });
    }
  };

  const renderReview = () => {
    const review = $("smart-batch-review");
    review.innerHTML = "";
    review.hidden = !groups.length;
    groups.forEach((group, index) => {
      const card = document.createElement("article");
      card.className = "batch-group";
      card.dataset.group = group.id;
      card.innerHTML =
        "<h3>Item " + (index + 1) + " · " + group.photos.length + (group.photos.length === 1 ? " photo" : " photos") + "</h3>" +
        "<div class='batch-photos'>" +
        group.photos
          .map(
            (photo) =>
              "<figure><img src='" + photo.url + "' alt='Selected photo " + photo.number + "'><figcaption>Photo " +
              photo.number + "</figcaption></figure>"
          )
          .join("") +
        "</div>" +
        "<label>Name <input data-name value='" + escapeHtml(group.name) + "'></label>" +
        "<label>Category <input data-category value='" + escapeHtml(group.category) + "'></label>" +
        "<label>Quantity <input data-quantity type='number' min='1' max='9999' value='" + group.quantity + "'></label>" +
        (group.reason ? "<p class='quiet'>" + escapeHtml(group.reason) + "</p>" : "") +
        "<div class='actions'>" +
        (group.photos.length > 1 ? "<button type='button' data-split='" + group.id + "'>Split these photos</button>" : "") +
        (index ? "<button type='button' data-merge='" + group.id + "'>Merge with item " + index + "</button>" : "") +
        "</div>";
      review.appendChild(card);
    });
    const finish = document.createElement("div");
    finish.className = "batch-finish";
    finish.innerHTML =
      "<p><strong>" + groups.length + (groups.length === 1 ? " item" : " items") + " ready.</strong> Fix any name or quantity, then save.</p>" +
      "<button type='button' id='save-smart-batch' class='go'>Save all " + groups.length + " items</button>";
    review.appendChild(finish);

    for (const button of review.querySelectorAll("[data-split]")) {
      button.addEventListener("click", () => {
        syncReviewEdits();
        const index = groups.findIndex((group) => group.id === button.dataset.split);
        const original = groups[index];
        const singles = original.photos.map((photo, photoIndex) => ({
          ...original,
          id: crypto.randomUUID(),
          photos: [photo],
          name: photoIndex ? "" : original.name,
          quantity: 1,
          reason: "",
        }));
        groups.splice(index, 1, ...singles);
        renderReview();
      });
    }
    for (const button of review.querySelectorAll("[data-merge]")) {
      button.addEventListener("click", () => {
        syncReviewEdits();
        const index = groups.findIndex((group) => group.id === button.dataset.merge);
        if (index < 1) return;
        groups[index - 1].photos.push(...groups[index].photos);
        if (!groups[index - 1].name) groups[index - 1].name = groups[index].name;
        groups.splice(index, 1);
        renderReview();
      });
    }
    $("save-smart-batch").addEventListener("click", saveBatch);
  };

  const analyze = async () => {
    if (running || !photos.length) return;
    const settings = await getSettings();
    if (!settings.apiKey) {
      $("smart-batch-status").textContent = "Add your Anthropic key in Settings before using Smart Batch.";
      if (onNeedsKey) onNeedsKey();
      return;
    }
    running = true;
    $("smart-batch-retry").hidden = true;
    groups = [];
    try {
      const chunks = [];
      for (let index = 0; index < photos.length; index += PHOTOS_PER_REQUEST) {
        chunks.push(photos.slice(index, index + PHOTOS_PER_REQUEST));
      }
      for (let index = 0; index < chunks.length; index += 1) {
        $("smart-batch-status").textContent =
          "Sorting photos " + (index + 1) + " of " + chunks.length + " with the fast model, " +
          (settings.haikuModel || "claude-haiku-4-5") + "…";
        const result = await groupChunk(settings, chunks[index]);
        groups.push(...normalizeGroups(result.groups, chunks[index]));
      }
      $("smart-batch-status").textContent =
        "Grouped with " + (settings.haikuModel || "claude-haiku-4-5") +
        ". Review below. Different names or boxes should stay separate.";
      renderReview();
    } catch (error) {
      $("smart-batch-status").textContent = error.message || "Smart Batch failed. Nothing was saved.";
      $("smart-batch-retry").hidden = false;
    } finally {
      running = false;
    }
  };

  async function saveBatch() {
    if (running || !groups.length) return;
    syncReviewEdits();
    running = true;
    const existingChecksums = new Set((await allPhotos()).map((photo) => photo.checksum));
    let skipped = 0;
    const prepared = [];
    try {
      for (let groupIndex = 0; groupIndex < groups.length; groupIndex += 1) {
        const group = groups[groupIndex];
        $("smart-batch-status").textContent =
          "Preparing item " + (groupIndex + 1) + " of " + groups.length + "…";
        const savedPhotos = [];
        for (const photo of group.photos) {
          const checksum = await checksumOf(photo.file);
          if (existingChecksums.has(checksum)) {
            skipped += 1;
            continue;
          }
          existingChecksums.add(checksum);
          savedPhotos.push({
            checksum,
            perceptualHash: await perceptualHashOf(photo.file).catch(() => ""),
            createdAt: new Date().toISOString(),
            filename: photo.file.name || "",
            blob: photo.file,
          });
        }
        if (!savedPhotos.length) continue;
        prepared.push({
          item: {
            name: group.name,
            category: group.category,
            unitCount: itemQuantity({ unitCount: group.quantity }),
            identityConfidence: 0.6,
          },
          photos: savedPhotos,
        });
      }
      if (!prepared.length) throw new Error("Every selected photo was already saved. No duplicates were added.");
      const created = await saveNewItemBatch(prepared);
      const session = JSON.parse(sessionStorage.getItem("resale-session") || "[]");
      sessionStorage.setItem("resale-session", JSON.stringify([...new Set([...session, ...created.map((item) => item.id)])]));
      $("smart-batch-status").textContent =
        created.length + (created.length === 1 ? " item saved" : " items saved") +
        (skipped ? ". " + skipped + " duplicate photo" + (skipped === 1 ? " was" : "s were") + " skipped." : ".") +
        " Tap Find resale prices when you are ready.";
      groups = [];
      $("smart-batch-review").hidden = true;
      $("smart-batch-review").innerHTML = "";
      releasePhotos();
      $("smart-batch-input").value = "";
      if (onSaved) await onSaved(created);
    } catch (error) {
      $("smart-batch-status").textContent = error.message || "The batch was not saved.";
    } finally {
      running = false;
    }
  }

  $("smart-batch-input").addEventListener("change", async (event) => {
    if (running) return;
    releasePhotos();
    groups = [];
    $("smart-batch-review").hidden = true;
    const files = [...event.target.files].filter((file) => file.type.startsWith("image/"));
    photos = files.map((file, index) => ({
      number: index + 1,
      file,
      url: URL.createObjectURL(file),
    }));
    $("smart-batch-status").textContent = photos.length
      ? photos.length + " photos selected. Sorting related views into items…"
      : "Choose photos to begin.";
    if (photos.length) await analyze();
  });
  $("smart-batch-retry").addEventListener("click", analyze);
}
