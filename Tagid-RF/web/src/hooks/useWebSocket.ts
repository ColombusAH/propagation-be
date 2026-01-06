
import { useEffect, useRef, useState, useCallback } from 'react';

type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

interface UseWebSocketOptions {
    url: string;
    onMessage?: (data: any) => void;
    autoConnect?: boolean;
}

export function useWebSocket({ url, onMessage, autoConnect = true }: UseWebSocketOptions) {
    const [status, setStatus] = useState<WebSocketStatus>('disconnected');
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<number | undefined>(undefined);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        // Handle relative URLs or full URLs
        // If running via Vite proxy, we can use relative URL, but WS protocol needs explicit host
        // or rely on browser to resolve relative to current origin if using wss://?
        // Usually standard is: 
        // const wsUrl = url.startsWith('ws') ? url : `ws://${window.location.host}${url}`;
        // But we are using Vite proxy for /api... standard WebSocket usually needs explicit port or proxy setup.
        // For local dev with proxy: ws://localhost:5173/api/ws... wait, vite proxy can proxy WS too.

        // Let's assume the URL passed is correct or relative.
        // If relative API URL is used in Vite:
        const fullUrl = url.startsWith('http') || url.startsWith('ws')
            ? url
            : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}${url}`;

        try {
            setStatus('connecting');
            const ws = new WebSocket(fullUrl);

            ws.onopen = () => {
                setStatus('connected');
                console.log('WS Connected');
            };

            ws.onclose = () => {
                setStatus('disconnected');
                console.log('WS Disconnected');
                // Auto reconnect
                reconnectTimeoutRef.current = window.setTimeout(() => {
                    connect();
                }, 3000);
            };

            ws.onerror = (error) => {
                setStatus('error');
                console.error('WS Error:', error);
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    onMessage?.(data);
                } catch (e) {
                    console.error('Failed to parse WS message:', e);
                }
            };

            wsRef.current = ws;
        } catch (e) {
            console.error('WS Connection failed:', e);
            setStatus('error');
        }
    }, [url, onMessage]);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        setStatus('disconnected');
    }, []);

    const send = useCallback((data: any) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(data));
        } else {
            console.warn('WS not connected, cannot send message');
        }
    }, []);

    useEffect(() => {
        if (autoConnect) {
            connect();
        }
        return () => disconnect();
    }, [connect, disconnect, autoConnect]);

    return { status, connect, disconnect, send };
}
