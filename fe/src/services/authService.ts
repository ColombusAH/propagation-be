import type { User } from '../types/user';
import { apiClient } from './apiClient';


/**
 * Service object for handling authentication-related API calls.
 */
export const authService = {
  /**
   * Store JWT token in localStorage
   */
  setToken(token: string): void {
    localStorage.setItem('access_token', token);
  },

  /**
   * Get JWT token from localStorage
   */
  getToken(): string | null {
    return localStorage.getItem('access_token');
  },

  /**
   * Clear JWT token from localStorage
   */
  clearToken(): void {
    localStorage.removeItem('access_token');
  },
  
  /**
   * Check if user is logged in (has a token)
   */
  isLoggedIn(): boolean {
    return !!this.getToken();
  },

  /**
   * Fetches the current user's information from the backend.
   * @returns A Promise resolving to the User object or null if not authenticated or on error.
   */
  async getCurrentUser(): Promise<User | null> {
    try {
      // If no token, user is not logged in
      if (!this.isLoggedIn()) {
        console.log('authService: No token found, user not logged in');
        return null;
      }
      
      // Use apiClient which automatically adds authorization header
      return await apiClient.get<User>('/auth/me');
    } catch (error) {
      console.error('Failed to fetch user:', error);
      return null;
    }
  },

  /**
   * Placeholder login functionality using email and password.
   * @param email - User's email.
   * @param password - User's password.
   * @returns A Promise resolving to the User object or null.
   */
  async login(email: string, password: string): Promise<User | null> {
    console.log('Logging in with email:', email, 'and password:', password);
    // TODO: Implement call to the actual backend login endpoint
    return this.getCurrentUser(); // Simulates login for now
  },

  /**
   * Sends the Google ID token to the backend for verification and login.
   * @param googleIdToken - The ID token obtained from the Google Sign-In flow.
   * @returns A Promise resolving to the User object upon successful authentication, or null/throws on error.
   */
  async loginWithGoogle(googleIdToken: string): Promise<User | null> {
    console.log("authService: Sending Google token to backend");
    try {
      interface GoogleLoginResponse {
        message: string;
        user_id: string;
        role: string;
        token: string;
      }
      
      const data = await apiClient.post<GoogleLoginResponse>('/auth/google', { token: googleIdToken });
      console.log("authService: Login successful");
      
      // Store the JWT token in localStorage
      if (data.token) {
        console.log("authService: Storing token in localStorage");
        this.setToken(data.token);
        
        // Get and return current user data
        return this.getCurrentUser();
      } else {
        console.error("authService: No token received in login response");
        return null;
      }
    } catch (error) {
      console.error('authService: Failed to login with Google:', error);
      // Re-throw the error so it can be caught by the AuthContext
      throw error;
    }
  },

  /**
   * Logs user out by clearing the token.
   */
  async logout(): Promise<void> {
    console.log('User logged out');
    this.clearToken();
  }
}; 