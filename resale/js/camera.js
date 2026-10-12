// Camera helpers. iPhone uses the system camera. Desktop Chrome uses a live preview.

let stream = null;

export function isIphone() {
  return /iPhone|iPad|iPod/i.test(navigator.userAgent || "");
}

export async function checksumOf(blob) {
  const bytes = await blob.arrayBuffer();
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((part) => part.toString(16).padStart(2, "0")).join("");
}

// A small visual fingerprint catches resized or recompressed copies that have
// different file bytes. It is only a duplicate hint; CJ still confirms merges.
export async function perceptualHashOf(blob) {
  const bitmap = await createImageBitmap(blob);
  const canvas = document.createElement("canvas");
  canvas.width = 9;
  canvas.height = 8;
  const context = canvas.getContext("2d", { willReadFrequently: true });
  context.drawImage(bitmap, 0, 0, 9, 8);
  bitmap.close();
  const pixels = context.getImageData(0, 0, 9, 8).data;
  let bits = "";
  for (let y = 0; y < 8; y += 1) {
    for (let x = 0; x < 8; x += 1) {
      const offset = (y * 9 + x) * 4;
      const next = offset + 4;
      const gray = pixels[offset] * 0.299 + pixels[offset + 1] * 0.587 + pixels[offset + 2] * 0.114;
      const nextGray = pixels[next] * 0.299 + pixels[next + 1] * 0.587 + pixels[next + 2] * 0.114;
      bits += gray > nextGray ? "1" : "0";
    }
  }
  return bits.match(/.{1,4}/g).map((part) => parseInt(part, 2).toString(16)).join("");
}

export function hashDistance(left, right) {
  if (!left || !right || left.length !== right.length) return Infinity;
  let distance = 0;
  for (let index = 0; index < left.length; index += 1) {
    let value = parseInt(left[index], 16) ^ parseInt(right[index], 16);
    while (value) {
      distance += value & 1;
      value >>= 1;
    }
  }
  return distance;
}

export async function startPreview(video) {
  stopPreview(video);
  stream = await navigator.mediaDevices.getUserMedia({
    audio: false,
    video: { facingMode: { ideal: "environment" } },
  });
  video.srcObject = stream;
  await video.play();
  return stream;
}

export function stopPreview(video) {
  if (stream) {
    for (const track of stream.getTracks()) track.stop();
    stream = null;
  }
  if (video) video.srcObject = null;
}

export function hasPreview() {
  return Boolean(stream);
}

// Saves the current live frame. The original file from Take photo is stored separately.
export function grabFrame(video) {
  const width = video.videoWidth || 1280;
  const height = video.videoHeight || 720;
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  canvas.getContext("2d").drawImage(video, 0, 0, width, height);
  return new Promise((resolve) => canvas.toBlob((blob) => resolve(blob), "image/jpeg", 0.92));
}
