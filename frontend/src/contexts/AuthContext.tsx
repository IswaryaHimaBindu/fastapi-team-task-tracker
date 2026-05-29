import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import api from '../api/axios';

interface AuthContextValue {
  isAuthenticated: boolean;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('access_token');
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    const accessToken = response.data.access_token ?? response.data.token;
    if (!accessToken) {
      throw new Error('Authentication failed.');
    }
    localStorage.setItem('access_token', accessToken);
    setToken(accessToken);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setToken(null);
  };

  const value = useMemo(
    () => ({
      isAuthenticated: Boolean(token),
      token,
      login,
      logout,
    }),
    [token]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider');
  }
  return context;
}
