import type { User } from '../types/user';
import { env } from '../config/env';

const API_URL = env.API_URL;

export const authService = {
  /**
   * Get current user information
   * @returns User data or null if not authenticated
   */
  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await fetch(`${API_URL}/auth/me`);
      
      if (response.ok) {
        return await response.json();
      }
      
      return null;
    } catch (error) {
      console.error('Failed to fetch user:', error);
      return null;
    }
  },

  /**
   * Login functionality - placeholder for actual implementation
   */
  async login(email: string, password: string): Promise<User | null> {
    // This would be implemented to call the actual login endpoint
    // For now, we'll just fetch the current user to simulate login
    return this.getCurrentUser();
  },

  /**
   * Logout functionality - placeholder
   */
  async logout(): Promise<void> {
    // This would call the logout endpoint when implemented
    console.log('User logged out');
  }
}; 