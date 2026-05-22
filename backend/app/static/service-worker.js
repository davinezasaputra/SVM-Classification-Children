const CACHE_NAME = 'sim-gizi-v8'; // Versi ke-8 (Pamungkas)

// 1. DAFTAR FILE WAJIB (Aset inti yang di-download di awal)
const urlsToCache = [
  '/login',
  '/static/manifest.json',
  '/static/style.css' // <-- File CSS lokal hasil Tailwind v4 kita
];

// 2. PROSES INSTALASI
self.addEventListener('install', event => {
  self.skipWaiting(); // Paksa aktif tanpa antri
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
  console.log('Service Worker V8: Siap bertugas!');
});

// 3. JURUS RUNTIME CACHING (Sambil Menyelam Minum Air)
self.addEventListener('fetch', event => {
  // PWA hanya menangkap aksi Buka Halaman (GET), abaikan aksi Simpan Data (POST)
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Jika ONLINE: Ambil dari internet, lalu diam-diam fotokopi ke memori HP
        if (response && response.status === 200) {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
        }
        return response;
      })
      .catch(() => {
        // Jika OFFLINE: Cari fotokopian di memori HP
        return caches.match(event.request).then(cachedResponse => {
          
          // Jika ketemu di memori, tampilkan!
          if (cachedResponse) {
            return cachedResponse; 
          }
          
          // JIKA TIDAK KETEMU (Mencegah Error 'Failed to convert to Response')
          // Buatkan halaman darurat secara instan di dalam HP
          return new Response(
            '<html lang="id"><body style="font-family:sans-serif; text-align:center; padding:3rem; background-color:#f8fafc;">' +
            '<h2 style="color:#0f172a;">Sinyal Terputus</h2>' +
            '<p style="color:#64748b;">Halaman ini belum tersimpan di memori perangkat karena belum pernah dibuka sebelumnya.</p>' +
            '<a href="/" style="display:inline-block; margin-top:20px; padding:10px 20px; background-color:#0d9488; color:white; text-decoration:none; border-radius:8px; font-weight:bold;">Kembali ke Dashboard</a>' +
            '</body></html>',
            {
              status: 503,
              statusText: 'Service Unavailable',
              headers: new Headers({ 'Content-Type': 'text/html' })
            }
          );
        });
      })
  );
});

// 4. PETUGAS KEBERSIHAN (Menghapus memori PWA versi lama)
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Menghapus Cache Lama:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim(); // Ambil alih kontrol browser seketika
});