// EcoTrack AI - High Performance Production Service Worker
const CACHE_NAME = "ecotrack-v4-cache-buster";

const STATIC_ASSETS = [
  "/styles.css?v=20",
  "/citizen.css?v=20",
  "/app.js?v=40",
  "/logo.png?v=4",
  "/manifest.json"
];

// 1. Install: Skip waiting immediately
self.addEventListener("install", event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS).catch(err => {
        console.warn("Pre-cache asset warning:", err);
      });
    })
  );
});

// 2. Activate: Wipe out ALL legacy caches (cleanconnect, old ecotrack versions)
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            console.log("[ServiceWorker] Purging legacy cache:", key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => {
      return self.clients.claim();
    })
  );
});

// 3. Fetch Strategy:
// Navigation / HTML: STRICTLY NETWORK FIRST! Never serve stale cached HTML on first visit.
self.addEventListener("fetch", event => {
  const req = event.request;

  if (req.mode === "navigate" || req.destination === "document") {
    event.respondWith(
      fetch(req)
        .then(response => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(req, clone));
          }
          return response;
        })
        .catch(() => {
          return caches.match(req).then(cached => cached || caches.match("/"));
        })
    );
    return;
  }

  // API calls or non-GET requests: Bypass cache
  if (req.method !== "GET" || req.url.includes("/api/") || req.url.includes("/reports/") || req.url.includes("/auth/")) {
    return;
  }

  // Other static assets (css, js, images): Network first, fallback to cache
  event.respondWith(
    fetch(req)
      .then(response => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(req, clone));
        }
        return response;
      })
      .catch(() => {
        return caches.match(req);
      })
  );
});
