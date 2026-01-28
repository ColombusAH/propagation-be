import { useEffect, useRef, useState, useCallback } from 'react';

type SSEStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

interface UseSSEOptions {
    url: string;
    onTheftAlert?: (data: any) => void;
    onTagScan?: (data: any) => void;
    autoConnect?: boolean;
}

export function useSSE({ url, onTheftAlert, onTagScan, autoConnect = true }: UseSSEOptions) {
    const [status, setStatus] = useState<SSEStatus>('disconnected');
    const eventSourceRef = useRef<EventSource | null>(null);
    const reconnectTimeoutRef = useRef<number | undefined>(undefined);

    // Use refs for callbacks to avoid reconnecting when they change
    const onTheftAlertRef = useRef(onTheftAlert);
    const onTagScanRef = useRef(onTagScan);

    useEffect(() => {
        onTheftAlertRef.current = onTheftAlert;
        onTagScanRef.current = onTagScan;
    }, [onTheftAlert, onTagScan]);

    const connect = useCallback(() => {
        // Build full URL
        const fullUrl = url.startsWith('http')
            ? url
            : `${window.location.origin}${url}`;

        try {
            // Close existing connection
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
            }

            setStatus('connecting');
            const eventSource = new EventSource(fullUrl);

            eventSource.onopen = () => {
                setStatus('connected');
                console.log('SSE Connected');
            };

            eventSource.onerror = (error) => {
                console.error('SSE Error:', error);
                setStatus('error');
                eventSource.close();
                eventSourceRef.current = null;

                // Auto reconnect
                if (autoConnect) {
                    reconnectTimeoutRef.current = window.setTimeout(() => {
                        connect();
                    }, 3000);
                }
            };

            // Handle connected event
            eventSource.addEventListener('connected', (event) => {
                console.log('SSE Connected event:', event.data);
            });

            // Handle theft alerts
            eventSource.addEventListener('theft_alert', (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('Theft Alert received:', data);
                    onTheftAlertRef.current?.(data);

                    // Show browser notification if permitted
                    showNotification('🚨 התרעת גניבה!', {
                        body: `מוצר: ${data.product}\nמיקום: ${data.location}`,
                        icon: '/icons/icon-192x192.png',
                        tag: 'theft-alert',
                        requireInteraction: true,
                    });
                } catch (e) {
                    console.error('Failed to parse theft alert:', e);
                }
            });

            // Handle tag scans
            eventSource.addEventListener('tag_scan', (event) => {
                try {
                    const data = JSON.parse(event.data);
                    onTagScanRef.current?.(data);
                } catch (e) {
                    console.error('Failed to parse tag scan:', e);
                }
            });

            // Handle ping (keepalive)
            eventSource.addEventListener('ping', () => {
                // Keepalive - no action needed
            });

            eventSourceRef.current = eventSource;
        } catch (e) {
            console.error('SSE Connection failed:', e);
            setStatus('error');
        }
    }, [url, autoConnect]);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }
        setStatus('disconnected');
    }, []);

    useEffect(() => {
        if (autoConnect) {
            connect();
        }
        return () => disconnect();
    }, [connect, disconnect, autoConnect]);

    return { status, connect, disconnect };
}

// Helper to show browser notification
async function showNotification(title: string, options: NotificationOptions) {
    if (!('Notification' in window)) {
        console.warn('Notifications not supported');
        return;
    }

    if (Notification.permission === 'granted') {
        // Use Service Worker for better PWA support
        if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
            const registration = await navigator.serviceWorker.ready;
            await registration.showNotification(title, options);
        } else {
            new Notification(title, options);
        }
    } else if (Notification.permission !== 'denied') {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            new Notification(title, options);
        }
    }
}
