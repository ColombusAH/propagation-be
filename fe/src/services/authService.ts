import type { User } from '../types/user';
import { env } from '../config/env';

const API_URL = env.API_URL;

/**
 * Service object for handling authentication-related API calls.
 */
export const authService = {
  /**
   * Fetches the current user's information from the backend.
   * @returns A Promise resolving to the User object or null if not authenticated or on error.
   */
  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await fetch(`${API_URL}/auth/me`);
      
      if (response.ok) {
        // Ensure the response is not empty before parsing JSON
        const text = await response.text();
        return text ? JSON.parse(text) : null;
      }
      
      return null;
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
    console.log("authService: Sending Google token to backend:", `${API_URL}/auth/google`);
    try {
      const response = await fetch(`${API_URL}/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: googleIdToken }),
      });

      if (!response.ok) {
        // Try to parse error details from backend response
        let errorDetail = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorDetail = errorData.detail || errorDetail; 
        } catch (parseError) {
          // Ignore if response body isn't valid JSON
        }
        console.error("authService: Google login backend error:", errorDetail);
        throw new Error(errorDetail); // Throw error to be caught by AuthContext
      }

      const userData: User = await response.json();
      console.log("authService: Received user data from backend:", userData);
      return userData; // Return the user data from the backend

    } catch (error) {
      console.error('authService: Failed to login with Google:', error);
      // Re-throw the error so it can be caught by the AuthContext
      throw error;
    }
  },

  /**
   * Placeholder logout functionality.
   */
  async logout(): Promise<void> {
    // TODO: Implement call to the actual backend logout endpoint
    console.log('User logged out');
  }
}; 