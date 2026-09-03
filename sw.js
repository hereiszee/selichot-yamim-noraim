/* Ashmoret Selichot — offline cache.
   The point of this file: a shul basement at 1am has no signal. Everything the
   page needs is cached on first visit, so later visits work with no network. */

const VERSION = "v2";
const SHELL = "ashmoret-shell-" + VERSION;
const RUNTIME = "ashmoret-runtime-" + VERSION;

const PRECACHE = [
  "./",
  "index.html",
  "manifest.webmanifest",
  "icon.svg",
  "icon-180.png",
  "icon-192.png",
  "icon-512.png",
  "data/polin.json"
];

self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(SHELL)
      .then(c => Promise.allSettled(PRECACHE.map(u => c.add(u))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== SHELL && k !== RUNTIME).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

const FONT_HOSTS = ["fonts.googleapis.com", "fonts.gstatic.com"];

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  const sameOrigin = url.origin === self.location.origin;
  const isFont = FONT_HOSTS.indexOf(url.hostname) >= 0;
  if (!sameOrigin && !isFont) return;

  /* Cache first. The selichot text does not change, and being fast and offline
     matters far more here than picking up an edit the same minute it ships;
     a new VERSION above clears everything on the next visit. */
  e.respondWith(
    caches.match(req).then(hit => {
      if (hit) return hit;
      return fetch(req).then(res => {
        if (res && (res.ok || res.type === "opaque")) {
          const copy = res.clone();
          caches.open(RUNTIME).then(c => c.put(req, copy));
        }
        return res;
      }).catch(() => {
        if (req.mode === "navigate") return caches.match("index.html");
        throw new Error("offline and not cached");
      });
    })
  );
});
