/* Ashmoret Selichot — offline cache.
   The point of this file: a shul basement at 1am has no signal. Everything the
   page needs is cached on first visit, so later visits work with no network. */

const VERSION = "v6";
const DATA_REV = "2";   // must equal DATA_REV in index.html
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
  "data/polin.json?r=" + DATA_REV
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

  /* The app shell changes; the texts and fonts never do. Serving the shell
     cache-first meant a fix needed two visits to appear — the stale copy on
     this load, the new one on the next. So the shell is network-first with the
     cache as its offline fallback, and everything else stays cache-first. */
  const isShell = req.mode === "navigate"
    || url.pathname.endsWith("/")
    || url.pathname.endsWith("/index.html");

  if (isShell){
    e.respondWith(
      fetch(req).then(res => {
        if (res && res.ok) caches.open(SHELL).then(c => c.put("index.html", res.clone()));
        return res;
      }).catch(() => caches.match("index.html").then(hit => hit || caches.match("./")))
    );
    return;
  }

  e.respondWith(
    caches.match(req).then(hit => {
      if (hit) return hit;
      return fetch(req).then(res => {
        if (res && (res.ok || res.type === "opaque")) {
          const copy = res.clone();
          caches.open(RUNTIME).then(c => c.put(req, copy));
        }
        return res;
      });
    })
  );
});
