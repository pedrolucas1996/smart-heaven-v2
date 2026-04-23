import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

const API_BASE_URL = (import.meta.env.VITE_API_URL || '/api/v1').replace(/\/$/, '');

const getStoredToken = () => {
  const token = localStorage.getItem('token');
  const accessToken = localStorage.getItem('access_token');
  const candidate = token || accessToken;
  if (!candidate || candidate === 'undefined' || candidate === 'null') {
    return null;
  }
  return candidate;
};

interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load token from localStorage on mount
  useEffect(() => {
    const storedToken = getStoredToken();
    if (storedToken) {
      // Keep both keys synced for backward compatibility
      localStorage.setItem('token', storedToken);
      localStorage.setItem('access_token', storedToken);
      setToken(storedToken);
      fetchCurrentUser(storedToken);
    } else {
      localStorage.removeItem('token');
      localStorage.removeItem('access_token');
      setIsLoading(false);
    }
  }, []);

  // Configure axios defaults when token changes
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  const fetchCurrentUser = async (authToken: string) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${authToken}` },
      });
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch current user:', error);
      localStorage.removeItem('token');
      localStorage.removeItem('access_token');
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await axios.post(
      `${API_BASE_URL}/auth/login`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    const tokenFromResponse = response?.data?.access_token || response?.data?.token;

    if (!tokenFromResponse || typeof tokenFromResponse !== 'string') {
      console.error('Login response without token:', response?.data);
      throw new Error('Login retornou sem token. Verifique a resposta do backend (/auth/login).');
    }

    setToken(tokenFromResponse);
    localStorage.setItem('token', tokenFromResponse);
    localStorage.setItem('access_token', tokenFromResponse);
    await fetchCurrentUser(tokenFromResponse);
  };

  const register = async (username: string, email: string, password: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/register`, {
        username,
        email,
        password,
      });

      // Não faz auto-login porque usuário precisa ser aprovado primeiro
      return response.data;
    } catch (error: any) {
      console.error('Register error:', error);
      throw error;
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('access_token');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
