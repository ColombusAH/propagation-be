// Environment variables configuration

// Get current environment
const isDevelopment = import.meta.env.DEV || false;

// In development, use the full URL with port from the environment variable
// In production, use relative URLs that will be handled by nginx proxy
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Get Google Client ID - This MUST be set in your .env file
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

if (!GOOGLE_CLIENT_ID) {
  console.error("Error: VITE_GOOGLE_CLIENT_ID environment variable is not set.");
  // Optionally, throw an error to prevent the app from starting without it
  // throw new Error("VITE_GOOGLE_CLIENT_ID environment variable is not set.");
}

console.log(`Environment: ${isDevelopment ? 'Development' : 'Production'}`);
console.log(`API URL: ${API_URL}`);
if (GOOGLE_CLIENT_ID) { // Log only if it exists to avoid logging undefined
  console.log(`Google Client ID is configured.`); 
}

export const env = {
  API_URL,
  isDevelopment,
  GOOGLE_CLIENT_ID: GOOGLE_CLIENT_ID || '', // Provide a default empty string or handle the missing case
}; 