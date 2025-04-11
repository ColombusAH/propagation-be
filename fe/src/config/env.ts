// Environment variables configuration

// Use import.meta.env for Vite environment variables
const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const env = {
  API_URL,
}; 