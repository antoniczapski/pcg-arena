import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';

// In development, use relative paths to go through Vite's proxy
// In production, use the configured API base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// Google OAuth configuration
export const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';
export const DEV_AUTH_ENABLED = import.meta.env.VITE_DEV_AUTH === 'true';

// Declare Google Identity Services types
declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (response: { credential: string }) => void;
            auto_select?: boolean;
          }) => void;
          prompt: () => void;
          renderButton: (element: HTMLElement, config: {
            theme?: 'outline' | 'filled_blue' | 'filled_black';
            size?: 'large' | 'medium' | 'small';
            type?: 'standard' | 'icon';
            text?: 'signin_with' | 'signup_with' | 'continue_with' | 'signin';
            shape?: 'rectangular' | 'pill' | 'circle' | 'square';
            width?: number;
          }) => void;
          disableAutoSelect: () => void;
        };
      };
    };
  }
}

export interface User {
  user_id: string;
  email: string;
  display_name: string;
  created_at_utc: string;
  last_login_utc: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  isGoogleReady: boolean;
  loginWithEmail: (email: string, password: string) => Promise<void>;
  registerWithEmail: (email: string, password: string, displayName: string) => Promise<void>;
  loginWithGoogle: (credential: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  renderGoogleButton: (element: HTMLElement) => void;
  resendVerificationEmail: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGoogleReady, setIsGoogleReady] = useState(false);
  const googleInitialized = useRef(false);

  const refreshUser = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/auth/me`, {
        credentials: 'include', // Include cookies
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Failed to fetch user:', error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Google login handler
  const loginWithGoogle = useCallback(async (credential: string) => {
    console.log('Google OAuth: Received credential, sending to backend...');
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/v1/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ credential }),
      });

      if (!response.ok) {
        const error = await response.json();
        console.error('Google OAuth: Backend returned error:', error);
        // Show alert so user sees the error
        alert(`Google Sign-In failed: ${error.error?.message || 'Unknown error'}`);
        throw new Error(error.error?.message || 'Google login failed');
      }

      const data = await response.json();
      setUser(data.user);
      console.log('Google OAuth: Login successful!', data.user.email);
    } catch (error) {
      console.error('Google OAuth: Failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initialize Google Identity Services
  useEffect(() => {
    if (!GOOGLE_CLIENT_ID || googleInitialized.current) {
      return;
    }

    // Load Google Identity Services script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    
    script.onload = () => {
      if (window.google) {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: (response) => {
            if (response.credential) {
              loginWithGoogle(response.credential);
            }
          },
        });
        googleInitialized.current = true;
        setIsGoogleReady(true);
        console.log('Google Identity Services initialized');
      }
    };

    script.onerror = () => {
      console.error('Failed to load Google Identity Services');
    };

    document.body.appendChild(script);

    return () => {
      // Cleanup on unmount
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }
    };
  }, [loginWithGoogle]);

  // Check authentication on mount
  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  // Render Google Sign-In button in a specified element
  const renderGoogleButton = useCallback((element: HTMLElement) => {
    if (window.google && isGoogleReady) {
      window.google.accounts.id.renderButton(element, {
        theme: 'filled_blue',
        size: 'large',
        type: 'standard',
        text: 'signin_with',
        shape: 'rectangular',
      });
    }
  }, [isGoogleReady]);

  // Email/password login
  const loginWithEmail = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || 'Login failed');
      }

      const data = await response.json();
      setUser(data.user);
      console.log('Email login successful:', data.user.email);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Email/password registration
  const registerWithEmail = async (email: string, password: string, displayName: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email, password, display_name: displayName }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || 'Registration failed');
      }

      const data = await response.json();
      setUser(data.user);
      console.log('Registration successful:', data.user.email);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await fetch(`${API_BASE_URL}/v1/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
      setUser(null);
      
      // Also sign out from Google to prevent auto-select on next visit
      if (window.google) {
        window.google.accounts.id.disableAutoSelect();
      }
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const resendVerificationEmail = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/auth/resend-verification`, {
        method: 'POST',
        credentials: 'include',
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || 'Failed to send verification email');
      }

      const data = await response.json();
      alert(data.message || 'Verification email sent! Please check your inbox.');
    } catch (error) {
      console.error('Failed to resend verification email:', error);
      alert(`Failed to send verification email: ${(error as Error).message}`);
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    isGoogleReady,
    loginWithEmail,
    registerWithEmail,
    loginWithGoogle,
    logout,
    refreshUser,
    renderGoogleButton,
    resendVerificationEmail,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

