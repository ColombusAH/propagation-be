// Environment variables configuration

// Get current environment
const isDevelopment = import.meta.env.DEV || false;

// In development, use the full URL with port from the environment variable
// In production, use relative URLs that will be handled by nginx proxy
const API_URL =  import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

console.log(`Environment: ${isDevelopment ? 'Development' : 'Production'}`);
console.log(`API URL: ${API_URL}`);

export const env = {
  API_URL,
  isDevelopment,
}; 