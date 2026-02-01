
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
    const isExplicitlyDisconnected = useRef(false);

    // Use ref for onMessage to avoid reconnecting when callback identity changes
    const onMessageRef = useRef(onMessage);
    useEffect(() => {
        onMessageRef.current = onMessage;
    }, [onMessage]);

    const disconnect = useCallback(() => {
        isExplicitlyDisconnected.current = true;
        if (reconnectTimeoutRef.current) {
            window.clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = undefined;
        }
        if (wsRef.current) {
            wsRef.current.onopen = null;
            wsRef.current.onclose = null;
            wsRef.current.onmessage = null;
            wsRef.current.onerror = null;
            wsRef.current.close();
            wsRef.current = null;
        }
        setStatus('disconnected');
    }, []);

    const connect = useCallback(() => {
        // Prepare URL
        const fullUrl = url.startsWith('http') || url.startsWith('ws')
            ? url
            : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}${url}`;

        try {
            // Prevent multiple connections
            if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) {
                console.debug('WS already connecting or open, skipping');
                return;
            }

            // Before connecting, ensure any previous state is cleaned up
            if (reconnectTimeoutRef.current) {
                window.clearTimeout(reconnectTimeoutRef.current);
                reconnectTimeoutRef.current = undefined;
            }

            isExplicitlyDisconnected.current = false;
            setStatus('connecting');
            console.log(`Connecting to WS: ${fullUrl}`);
            const ws = new WebSocket(fullUrl);

            ws.onopen = () => {
                if (isExplicitlyDisconnected.current) {
                    ws.close();
                    return;
                }
                setStatus('connected');
                console.log('WS Connected');
            };

            ws.onclose = (event) => {
                wsRef.current = null;
                if (isExplicitlyDisconnected.current) {
                    setStatus('disconnected');
                    console.log('WS Disconnected (explicit)');
                    return;
                }

                setStatus('disconnected');
                console.log(`WS Closed: ${event.code} ${event.reason}`);

                // Auto reconnect
                if (autoConnect) {
                    console.log('WS will attempt to reconnect in 3s...');
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
    }, [url, autoConnect]);

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
        return () => {
            console.log('useWebSocket unmounting, disconnecting...');
            disconnect();
        };
    }, [connect, disconnect, autoConnect]);

    return { status, connect, disconnect, send };
}
