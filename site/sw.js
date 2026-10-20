/* Pocket Toolbox service worker.
   Do not edit site/sw.js by hand: build.py generates it from this file and stamps a new
   VERSION (a hash of every site file) each time, so returning visitors always get updates.

   Strategy
   - Pages, manifest: network first. Always fresh when online, and the HTTP cache is bypassed,
     so a host that sets long cache times can not serve a stale page. If the network is down
     or takes longer than 4 seconds, the saved copy is used instead.
   - Fonts, images, scripts: stale while revalidate. Served instantly from the cache, then
     refreshed in the background, so they are fast, work offline and never stay stale.
   - Only good (HTTP 200, same-site) responses are saved. Errors are never cached.
   - Every new VERSION deletes the old caches. */
const VERSION = '8302a98f68';
const CACHE = 'pocket-toolbox-' + VERSION;
const PRECACHE = [
  "./",
  "index.html",
  "apple-touch-icon.png",
  "favicon-32.png",
  "favicon.ico",
  "fonts/dm-sans-latin-400-normal.woff2",
  "fonts/dm-sans-latin-500-normal.woff2",
  "fonts/dm-sans-latin-700-normal.woff2",
  "fonts/fraunces-latin-600-normal.woff2",
  "icon-192.png",
  "icon-512-maskable.png",
  "icon-512.png",
  "manifest.webmanifest",
  "qrcode.min.js"
];
const NETWORK_TIMEOUT_MS = 4000;

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE)
      .then(cache => cache.addAll(PRECACHE.map(url => new Request(url, { cache: 'reload' }))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('pocket-toolbox-') && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const req = event.request;
  const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin) return;
  const isStatic = /\.(woff2|png|ico|js)$/.test(url.pathname) && !url.pathname.endsWith('/sw.js');
  event.respondWith(isStatic ? staleWhileRevalidate(event, req) : networkFirst(req));
});

const cacheable = res => res && res.status === 200 && res.type === 'basic';

function withTimeout(promise, ms) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('timeout')), ms);
    promise.then(r => { clearTimeout(timer); resolve(r); }, e => { clearTimeout(timer); reject(e); });
  });
}

async function networkFirst(req) {
  const cache = await caches.open(CACHE);
  try {
    const res = await withTimeout(fetch(req, { cache: 'no-cache' }), NETWORK_TIMEOUT_MS);
    if (cacheable(res)) cache.put(req, res.clone());
    return res;
  } catch (err) {
    const hit = await cache.match(req, { ignoreSearch: true });
    if (hit) return hit;
    if (req.mode === 'navigate') {
      // A tool page that was never visited: the home page opens the right tool from the address.
      const home = await cache.match('./');
      if (home) return home;
    }
    return Response.error();
  }
}

async function staleWhileRevalidate(event, req) {
  const cache = await caches.open(CACHE);
  const cached = await cache.match(req);
  const refresh = fetch(req, { cache: 'no-cache' })
    .then(res => { if (cacheable(res)) cache.put(req, res.clone()); return res; })
    .catch(() => null);
  event.waitUntil(refresh);
  return cached || (await refresh) || Response.error();
}
