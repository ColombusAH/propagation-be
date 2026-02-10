// API configuration
// In production, VITE_API_URL should be set to the backend Railway URL
// In development, the Vite proxy handles /api requests

const getApiUrl = (): string => {
    // Check for environment variable first
    if (import.meta.env.VITE_API_URL) {
        return import.meta.env.VITE_API_URL;
    }

    // In production without VITE_API_URL, we need the backend URL
    // This will cause errors - VITE_API_URL must be set in Railway
    if (import.meta.env.PROD) {
        console.warn('VITE_API_URL is not set! API calls will fail.');
        return '';  // Will use relative URLs (won't work without proxy)
    }

    // In development, use relative URLs (Vite proxy will handle them)
    return '';
};

export const API_BASE_URL = getApiUrl();

// Helper function to construct API URLs
export const apiUrl = (path: string): string => {
    const base = API_BASE_URL;
    // If no base URL, use relative path (for Vite proxy)
    if (!base) {
        return path.startsWith('/') ? path : `/${path}`;
    }
    // Otherwise, construct full URL
    const cleanBase = base.endsWith('/') ? base.slice(0, -1) : base;
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return `${cleanBase}${cleanPath}`;
};
