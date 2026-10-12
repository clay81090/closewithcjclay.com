// App shell only. Catalog photos and price lookups stay out of this cache.

const CACHE = "resale-shell-8";
const SHELL = [
  "./index.html",
  "./styles.css",
  "./manifest.webmanifest",
  "./icon.png",
  "./js/db.js",
  "./js/keys.js",
  "./js/camera.js",
  "./js/seed.js",
  "./js/research.js",
  "./js/ui.js",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(SHELL).catch(() => null))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key))))
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;
  if (event.request.method !== "GET") return;
  if (url.pathname.includes("/seed/")) return;

  const shellPage =
    event.request.mode === "navigate" ||
    url.pathname.endsWith("/resale/") ||
    url.pathname.endsWith("index.html");

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE).then((cache) => cache.put(shellPage ? "./index.html" : event.request, copy));
        }
        return response;
      })
      .catch(() => caches.match(shellPage ? "./index.html" : event.request))
  );
});
