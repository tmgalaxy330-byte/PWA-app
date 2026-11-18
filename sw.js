/* ロジトレ Service Worker(検討中・ver未確定)
   リリースのたびに CACHE の名前を変える。変えないと端末側で更新が検知されない。 */
const CACHE = 'logitore-trial-2';
const ASSETS = [
  './',
  './index.html',
  './manual.html',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/maskable-512.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
  );
});

// アプリ側の「更新」ボタンから呼ばれる
self.addEventListener('message', (e) => {
  if (e.data === 'skip') self.skipWaiting();
});

// オフライン優先: キャッシュにあればそれを返し、なければネットワーク
self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (req.mode === 'navigate') {
    e.respondWith(
      caches.match(req, { ignoreSearch: true })
        .then((r) => r || fetch(req))
        .catch(() => caches.match('./index.html'))
    );
    return;
  }
  e.respondWith(caches.match(req, { ignoreSearch: true }).then((r) => r || fetch(req)));
});
