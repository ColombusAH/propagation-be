import { useCallback } from 'react';
import { Toast, ToastType, ToastOptions } from '../components/Toast/types';

// Global toast state (simple implementation without external library)
let toastListeners: Array<(toast: Toast) => void> = [];
let toastIdCounter = 0;

/**
 * useToast - Hook for showing toast notifications
 * 
 * Provides methods to show different types of toast notifications.
 * 
 * @example
 * ```tsx
 * const toast = useToast();
 * 
 * // Success toast
 * toast.success('נשמר בהצלחה!');
 * 
 * // Error toast
 * toast.error('שגיאה בשמירה');
 * 
 * // Info toast
 * toast.info('מידע חשוב');
 * 
 * // Warning toast
 * toast.warning('אזהרה!');
 * 
 * // Custom duration
 * toast.success('הודעה', { duration: 5000 });
 * ```
 */
export function useToast() {
    const showToast = useCallback((type: ToastType, message: string, options?: ToastOptions) => {
        const toast: Toast = {
            id: `toast-${++toastIdCounter}`,
            type,
            message,
            duration: options?.duration ?? 3000,
        };

        toastListeners.forEach(listener => listener(toast));
    }, []);

    return {
        success: useCallback((message: string, options?: ToastOptions) => {
            showToast('success', message, options);
        }, [showToast]),

        error: useCallback((message: string, options?: ToastOptions) => {
            showToast('error', message, options);
        }, [showToast]),

        info: useCallback((message: string, options?: ToastOptions) => {
            showToast('info', message, options);
        }, [showToast]),

        warning: useCallback((message: string, options?: ToastOptions) => {
            showToast('warning', message, options);
        }, [showToast]),
    };
}

/**
 * Subscribe to toast events
 * @internal
 */
export function subscribeToToasts(listener: (toast: Toast) => void) {
    toastListeners.push(listener);
    return () => {
        toastListeners = toastListeners.filter(l => l !== listener);
    };
}
