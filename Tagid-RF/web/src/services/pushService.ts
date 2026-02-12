/// <reference types="vite/client" />
import axios from 'axios';

// In production, we use relative URLs via Nginx proxy
const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

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
    async getPublicKey(token?: string): Promise<string> {
        const headers: Record<string, string> = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        const response = await axios.get(`${API_URL}/push/vapid-public-key`, { headers });
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

    async subscribeUser(registration: ServiceWorkerRegistration, userId?: string) {
        try {
            const publicKey = await this.getPublicKey();
            const convertedVapidKey = urlBase64ToUint8Array(publicKey);

            // Check if subscription exists first
            let subscription = await registration.pushManager.getSubscription();

            if (subscription) {
                // Check if key changed (optional, but good practice) - or just unsubscribe and resubscribe to be safe
                // For now, we trust the existing one matches the new key if it hasn't expired.
                // But to be 100% sure we are in sync with the current VAPID key:
                // If keys differed, we would need to unsubscribe.
                // Simpler: Just try to subscribe.
            }

            // This will return the existing subscription if options match, or create new
            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: convertedVapidKey
            });

            console.log('User is subscribed:', subscription);

            // Send subscription to backend
            const headers: Record<string, string> = {};
            if (userId) { // Assuming token is handled elsewhere or we pass it
                // Note: If this service is used within a context that has the token,
                // we should pass it or use an axios interceptor.
                // For now, let's just make the URL relative.
            }

            await axios.post(`${API_URL}/push/subscribe`, {
                endpoint: subscription.endpoint,
                userId: userId,
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
    },

    async unsubscribeUser() {
        if ('serviceWorker' in navigator) {
            const registration = await navigator.serviceWorker.ready;
            const subscription = await registration.pushManager.getSubscription();
            if (subscription) {
                await subscription.unsubscribe();
            }
        }
    }
};
