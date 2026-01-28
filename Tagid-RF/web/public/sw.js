/// <reference lib="webworker" />

// Service Worker for Push Notifications
// This runs in the background and can show notifications even when the app is closed

const SW_VERSION = '1.0.0';

// Install event
self.addEventListener('install', (event) => {
    console.log('[SW] Service Worker installing. Version:', SW_VERSION);
    // Skip waiting to activate immediately
    self.skipWaiting();
});

// Activate event
self.addEventListener('activate', (event) => {
    console.log('[SW] Service Worker activated. Version:', SW_VERSION);
    // Take control of all pages immediately
    event.waitUntil(self.clients.claim());
});

// Handle push notifications from server
self.addEventListener('push', (event) => {
    console.log('[SW] Push received:', event);

    let data = {
        title: 'Tagid RFID',
        body: 'יש לך התראה חדשה',
        icon: '/icons/icon-192x192.png',
        badge: '/icons/icon-72x72.png',
        tag: 'default',
    };

    if (event.data) {
        try {
            const payload = event.data.json();
            data = { ...data, ...payload };
        } catch (e) {
            data.body = event.data.text();
        }
    }

    const options = {
        body: data.body,
        icon: data.icon,
        badge: data.badge,
        tag: data.tag,
        requireInteraction: true,
        vibrate: [200, 100, 200],
        actions: [
            { action: 'view', title: 'צפה' },
            { action: 'dismiss', title: 'סגור' },
        ],
        data: data,
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
    console.log('[SW] Notification clicked:', event.action);

    event.notification.close();

    if (event.action === 'view' || !event.action) {
        // Open or focus the app
        event.waitUntil(
            self.clients.matchAll({ type: 'window', includeUncontrolled: true })
                .then((clientList) => {
                    // If app is already open, focus it
                    for (const client of clientList) {
                        if (client.url.includes('/notifications') && 'focus' in client) {
                            return client.focus();
                        }
                    }
                    // Otherwise open the notifications page
                    if (self.clients.openWindow) {
                        return self.clients.openWindow('/notifications');
                    }
                })
        );
    }
});

// Handle notification close
self.addEventListener('notificationclose', (event) => {
    console.log('[SW] Notification closed');
});
