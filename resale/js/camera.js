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
