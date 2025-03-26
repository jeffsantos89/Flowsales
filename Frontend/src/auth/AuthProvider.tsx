import { createContext, useContext, useEffect, useState, ReactNode, useCallback, useMemo } from 'react';
import jwtDecode from 'jwt-decode';

// Constants
const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const TOKEN_REFRESH_THRESHOLD = 5 * 60 * 1000; // 5 minutes

// Types
interface User {
  id: string;
  email: string;
  roles: string[];
  [key: string]: any;
}

interface DecodedToken {
  exp: number;
  user: User;
  [key: string]: any;
}

interface AuthContextType {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, refreshToken?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  hasRole: (role: string) => boolean;
}

interface AuthError extends Error {
  code?: string;
}

// Create Context with a default value
const AuthContext = createContext<AuthContextType>({} as AuthContextType);

// Custom hook for using auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshTokenValue, setRefreshTokenValue] = useState<string | null>(null);

  // Token validation
  const decodeAndValidateToken = useCallback((token: string): DecodedToken | null => {
    try {
      const decoded = jwtDecode<DecodedToken>(token);
      const currentTime = Date.now();
      const expirationTime = decoded.exp * 1000;

      if (expirationTime <= currentTime) {
        throw new Error('Token expired');
      }

      return decoded;
    } catch (error) {
      console.error('Token validation error:', error);
      return null;
    }
  }, []);

  // Check if token needs refresh
  const shouldRefreshToken = useCallback((decodedToken: DecodedToken): boolean => {
    const currentTime = Date.now();
    const expirationTime = decodedToken.exp * 1000;
    return (expirationTime - currentTime) < TOKEN_REFRESH_THRESHOLD;
  }, []);

  // Token refresh logic
  const refreshToken = useCallback(async () => {
    if (!refreshTokenValue) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refreshToken: refreshTokenValue }),
      });

      if (!response.ok) {
        throw new Error('Failed to refresh token');
      }

      const { accessToken, refreshToken: newRefreshToken } = await response.json();
      
      await login(accessToken, newRefreshToken);
    } catch (error) {
      await logout();
      throw error;
    }
  }, [refreshTokenValue]);

  // Login function
  const login = useCallback(async (newToken: string, newRefreshToken?: string) => {
    try {
      const decoded = decodeAndValidateToken(newToken);
      if (!decoded) {
        throw new Error('Invalid token');
      }

      sessionStorage.setItem(TOKEN_KEY, newToken);
      if (newRefreshToken) {
        sessionStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken);
        setRefreshTokenValue(newRefreshToken);
      }

      setToken(newToken);
      setUser(decoded.user);
    } catch (error) {
      await logout();
      throw error;
    }
  }, [decodeAndValidateToken]);

  // Logout function
  const logout = useCallback(async () => {
    try {
      // Optional: Call logout endpoint
      if (token) {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      sessionStorage.removeItem(TOKEN_KEY);
      sessionStorage.removeItem(REFRESH_TOKEN_KEY);
      setToken(null);
      setUser(null);
      setRefreshTokenValue(null);
    }
  }, [token]);

  // Role checking
  const hasRole = useCallback((role: string): boolean => {
    return user?.roles?.includes(role) ?? false;
  }, [user]);

  // Initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedToken = sessionStorage.getItem(TOKEN_KEY);
        const storedRefreshToken = sessionStorage.getItem(REFRESH_TOKEN_KEY);

        if (storedToken) {
          const decoded = decodeAndValidateToken(storedToken);
          
          if (decoded) {
            if (shouldRefreshToken(decoded) && storedRefreshToken) {
              setRefreshTokenValue(storedRefreshToken);
              await refreshToken();
            } else {
              await login(storedToken, storedRefreshToken || undefined);
            }
          } else {
            await logout();
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        await logout();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Memoized context value
  const contextValue = useMemo(() => ({
    token,
    user,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    logout,
    refreshToken,
    hasRole,
  }), [token, user, isLoading, login, logout, refreshToken, hasRole]);

  if (isLoading) {
    return <div>Loading...</div>; // Consider using a proper loading component
  }

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export { AuthContext };
