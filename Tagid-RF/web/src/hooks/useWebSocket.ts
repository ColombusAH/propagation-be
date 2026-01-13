
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

    // Use ref for onMessage to avoid reconnecting when callback identity changes
    const onMessageRef = useRef(onMessage);
    useEffect(() => {
        onMessageRef.current = onMessage;
    }, [onMessage]);

    const connect = useCallback(() => {
        // Prepare URL
        const fullUrl = url.startsWith('http') || url.startsWith('ws')
            ? url
            : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}${url}`;

        try {
            // Prevent multiple connections
            if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) {
                return;
            }

            setStatus('connecting');
            const ws = new WebSocket(fullUrl);

            ws.onopen = () => {
                setStatus('connected');
                console.log('WS Connected');
            };

            ws.onclose = () => {
                setStatus('disconnected');
                console.log('WS Disconnected');
                wsRef.current = null;
                // Auto reconnect
                if (autoConnect) {
                    reconnectTimeoutRef.current = window.setTimeout(() => {
                        connect();
                    }, 3000);
                }
            };

            ws.onerror = (error) => {
                console.error('WS Error:', error);
                setStatus('error');
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    onMessageRef.current?.(data);
                } catch (e) {
                    console.error('Failed to parse WS message:', e);
                }
            };

            wsRef.current = ws;
        } catch (e) {
            console.error('WS Connection failed:', e);
            setStatus('error');
        }
    }, [url, autoConnect]); // Removed onMessage from dependencies

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
