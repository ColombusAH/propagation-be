import { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Toast } from './Toast';
import { Toast as ToastType } from './types';
import { subscribeToToasts } from '../../hooks/useToast';

const Container = styled.div`
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 10000;
  display: flex;
  flex-direction: column;
  pointer-events: none;
  
  > * {
    pointer-events: auto;
  }
  
  @media (max-width: 640px) {
    left: 1rem;
    right: 1rem;
  }
`;

/**
 * ToastContainer - Container for all toast notifications
 * 
 * Manages the display and lifecycle of toast notifications.
 * Should be placed once at the app root level.
 * 
 * @example
 * ```tsx
 * // In App.tsx
 * <ToastContainer />
 * ```
 */
export function ToastContainer() {
    const [toasts, setToasts] = useState<ToastType[]>([]);

    useEffect(() => {
        const unsubscribe = subscribeToToasts((toast) => {
            setToasts(prev => [...prev, toast]);
        });

        return unsubscribe;
    }, []);

    const removeToast = (id: string) => {
        setToasts(prev => prev.filter(t => t.id !== id));
    };

    if (toasts.length === 0) {
        return null;
    }

    return (
        <Container>
            {toasts.map(toast => (
                <Toast
                    key={toast.id}
                    toast={toast}
                    onClose={() => removeToast(toast.id)}
                />
            ))}
        </Container>
    );
}
