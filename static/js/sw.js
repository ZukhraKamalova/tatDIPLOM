// service-worker.js
self.addEventListener('install', function(event) {
    console.log('Service Worker установлен');
});

self.addEventListener('activate', function(event) {
    console.log('Service Worker активирован');
});

self.addEventListener('fetch', function(event) {
    // Пропускаем все запросы
    event.respondWith(fetch(event.request));
});