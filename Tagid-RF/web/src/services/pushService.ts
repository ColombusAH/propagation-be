import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Helper to convert VAPID key
function urlBase64ToUint8Array(base64String: string) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

export const pushService = {
    async getPublicKey(): Promise<string> {
        const response = await axios.get(`${API_URL}/push/vapid-public-key`);
        return response.data.publicKey;
    },

    async registerServiceWorker() {
        if ('serviceWorker' in navigator && 'PushManager' in window) {
            try {
                const registration = await navigator.serviceWorker.register('/sw.js');
                console.log('Service Worker registered:', registration);
                return registration;
            } catch (error) {
                console.error('Service Worker registration failed:', error);
                throw error;
            }
        } else {
            console.warn('Push notifications not supported');
            return null;
        }
    },

    async subscribeUser(registration: ServiceWorkerRegistration) {
        try {
            const publicKey = await this.getPublicKey();
            const convertedVapidKey = urlBase64ToUint8Array(publicKey);

            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: convertedVapidKey
            });

            console.log('User is subscribed:', subscription);

            // Send subscription to backend
            await axios.post(`${API_URL}/push/subscribe`, {
                endpoint: subscription.endpoint,
                keys: {
                    p256dh: subscription.toJSON().keys?.p256dh,
                    auth: subscription.toJSON().keys?.auth
                }
            });

            return subscription;
        } catch (error) {
            console.error('Failed to subscribe the user: ', error);
            throw error;
        }
    }
};
