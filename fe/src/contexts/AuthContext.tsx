import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { User } from '../types/user';
import { authService } from '../services/authService';

/**
 * Defines the shape of the Authentication context.
 */
interface AuthContextType {
  /** The currently logged-in user, or null if not authenticated. */
  user: User | null;
  /** Indicates if an authentication operation is in progress. */
  isLoading: boolean;
  /** Stores any error message from the last authentication attempt. */
  error: string | null;
  /** Function to log in using email and password (placeholder). */
  login: (email: string, password: string) => Promise<void>;
  /** Function to log the user out. */
  logout: () => Promise<void>;
  /** Function to initiate login via Google OAuth. */
  loginWithGoogle: (googleIdToken: string) => Promise<void>;
}

/**
 * React Context for managing authentication state.
 */
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Provides authentication state and functions to its children.
 * Manages user state, loading indicators, and errors.
 * Attempts to load the current user on initial mount.
 */
export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Effect to load the current user when the component mounts
  useEffect(() => {
    const loadUser = async () => {
      setIsLoading(true);
      try {
        const userData = await authService.getCurrentUser();
        setUser(userData);
      } catch (err) {
        setError('Failed to load user');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
  }, []);

  // Placeholder login function
  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const userData = await authService.login(email, password);
      if (userData) {
        setUser(userData);
      } else {
        setError('Invalid credentials');
      }
    } catch (err) {
      setError('Login failed');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    setIsLoading(true);
    try {
      await authService.logout();
      setUser(null);
    } catch (err) {
      setError('Logout failed');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handles the Google login flow.
   * Takes the Google ID token obtained from the frontend library,
   * sends it to the backend for verification via authService,
   * and updates the user state upon success or sets an error.
   * @param googleIdToken - The ID token received from Google Sign-In.
   */
  const loginWithGoogle = async (googleIdToken: string) => {
    setIsLoading(true);
    setError(null);
    console.log("AuthContext: Attempting Google login with token..."); 
    try {
      // Call the authService to handle the backend request
      const userData = await authService.loginWithGoogle(googleIdToken);
      if (userData) {
        setUser(userData);
        console.log("AuthContext: Google login successful, user set.", userData);
      } else {
        // This case might occur if the backend returns a 200 but no user data (handle appropriately)
        setError('Google login failed: No user data received from backend.');
        console.error("AuthContext: Google login failed - no user data returned.");
      }
    } catch (err: any) { // Catch specific error types if needed
      const errorMessage = err.response?.data?.detail || err.message || 'Google login failed';
      setError(errorMessage);
      console.error("AuthContext: Google login failed", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Provide the context value to children
  return (
    <AuthContext.Provider value={{ user, isLoading, error, login, logout, loginWithGoogle }}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Custom hook to easily access the Authentication context.
 * Throws an error if used outside of an AuthProvider.
 * @returns The authentication context value.
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 