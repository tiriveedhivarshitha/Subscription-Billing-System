const CACHE_NAME = 'billing-cache-v1';
const SAFE_ASSETS = [
    './',
    './index.html',
    './signup.html',
    './dashboard.html',
    './style.css',
    './script.js',
    './dashboard.js',
    './pwa.js',
    './manifest.json',
    './icon.svg',
    './offline.html'
];

self.addEventListener('install', (event) => {
    // Force immediate activation
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[Service Worker] Caching safe static assets');
            return cache.addAll(SAFE_ASSETS);
        })
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[Service Worker] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // SECURITY RESTRICTION: 
    // Do NOT cache or intercept any API requests (FastAPI backend).
    // This ensures billing calculations, invoices, and authenticated data are always fresh.
    if (url.hostname === '127.0.0.1' && url.port === '8000') {
        return; // Let the browser handle it directly (bypasses SW)
    }
    if (url.pathname.includes('/api/') || url.pathname.includes('/admin') || url.pathname.includes('invoice')) {
        return; 
    }

    // Only intercept GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    event.respondWith(
        fetch(event.request).catch(() => {
            // If network fails, try the cache
            return caches.match(event.request).then((cachedResponse) => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                // If it's a navigation request and not in cache, show offline page
                if (event.request.mode === 'navigate') {
                    return caches.match('./offline.html');
                }
            });
        })
    );
});
