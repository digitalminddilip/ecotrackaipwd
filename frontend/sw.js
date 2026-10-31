const CACHE_NAME = "ecotrack-v2";
const ASSETS = [
  "/",
  "/styles.css",
  "/citizen.css",
  "/app.js",
  "/logo.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request))
  );
});
