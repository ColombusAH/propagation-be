// Simple service worker registration placeholder
// This can be extended with workbox or other PWA tooling

export function registerServiceWorker(): void {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker
        .register('/sw.js')
        .then((registration) => {
          console.log('[SW] SW registered: ', registration);
        })
        .catch((registrationError) => {
          console.log('[SW] SW registration failed: ', registrationError);
        });
    });
  }
}

