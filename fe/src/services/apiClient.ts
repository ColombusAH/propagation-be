import { env } from '../config/env';

// Base API URL from environment
const API_URL = env.API_URL;

// Default request timeout in milliseconds
const DEFAULT_TIMEOUT = 10000;

/**
 * Gets the authentication token from local storage
 * @returns The JWT token or null if not found
 */
const getToken = (): string | null => {
  return localStorage.getItem('access_token');
};

/**
 * Helper function to add timeout to fetch requests
 * @param fetchPromise - The original fetch promise
 * @param timeoutMs - Timeout in milliseconds
 */
const timeoutFetch = (fetchPromise: Promise<Response>, timeoutMs: number = DEFAULT_TIMEOUT): Promise<Response> => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  
  return Promise.race([
    fetchPromise,
    new Promise<Response>((_, reject) => {
      setTimeout(() => {
        reject(new Error(`Request timed out after ${timeoutMs}ms`));
      }, timeoutMs);
    })
  ]).finally(() => clearTimeout(timeoutId)) as Promise<Response>;
};

/**
 * Centralized API client for making HTTP requests
 * Automatically adds auth token to requests when available
 */
export const apiClient = {
  /**
   * Performs a GET request to the specified endpoint
   * @param endpoint - API endpoint to call (without base URL)
   * @returns Promise resolving to the response data
   */
  async get<T>(endpoint: string): Promise<T> {
    const token = getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    
    const response = await timeoutFetch(fetch(`${API_URL}${endpoint}`, {
      method: "GET",
      headers,
    }));
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  },
  
  /**
   * Performs a POST request to the specified endpoint
   * @param endpoint - API endpoint to call (without base URL)
   * @param data - Data to send in the request body
   * @returns Promise resolving to the response data
   */
  async post<T>(endpoint: string, data: any): Promise<T> {
    const token = getToken();
    const headers: Record<string, string> = {};
    
    if (!(data instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }
    
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    
    const body = data instanceof FormData ? data : JSON.stringify(data);
    
    const response = await timeoutFetch(fetch(`${API_URL}${endpoint}`, {
      method: "POST",
      headers,
      body,
    }));
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  },
  
  /**
   * Performs a PUT request to the specified endpoint
   * @param endpoint - API endpoint to call (without base URL)
   * @param data - Data to send in the request body
   * @returns Promise resolving to the response data
   */
  async put<T>(endpoint: string, data: any): Promise<T> {
    const token = getToken();
    const headers: Record<string, string> = {};
    
    if (!(data instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }
    
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    
    const body = data instanceof FormData ? data : JSON.stringify(data);
    
    const response = await timeoutFetch(fetch(`${API_URL}${endpoint}`, {
      method: "PUT",
      headers,
      body,
    }));
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  },
  
  /**
   * Performs a DELETE request to the specified endpoint
   * @param endpoint - API endpoint to call (without base URL)
   * @returns Promise resolving to the response data
   */
  async delete<T>(endpoint: string): Promise<T> {
    const token = getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    
    const response = await timeoutFetch(fetch(`${API_URL}${endpoint}`, {
      method: "DELETE",
      headers,
    }));
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  },
}; 