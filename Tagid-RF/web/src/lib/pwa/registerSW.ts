// Simple service worker registration placeholder
// This can be extended with workbox or other PWA tooling

export function registerServiceWorker(): void {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      // Service worker registration can be added here if needed
      // For now, this is a placeholder for future PWA enhancements
    });
  }
}

