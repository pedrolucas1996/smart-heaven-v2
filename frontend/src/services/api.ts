import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',  // Usa proxy do Vite
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export interface Light {
  id: number;
  lampada: string;
  estado: boolean;
  data_de_atualizacao: string;
}

export interface Switch {
  id: number;
  nome: string;
  base: string;
  estado: boolean;
  ativo: boolean;
  data_de_atualizacao: string;
}

export interface Log {
  id: number;
  comodo: string;
  estado: boolean;
  origem: string;
  timestamp: string;
  detalhes?: string;
}

export interface LightCommand {
  comodo: string;
  acao: 'ligar' | 'desligar';
  origem?: string;
}

export interface SwitchCommand {
  botao: string;
  acao: 'habilitar' | 'desabilitar';
}

// Lights API
export const lightsApi = {
  getAll: () => api.get<Light[]>('/lights'),
  getOne: (lampada: string) => api.get<Light>(`/lights/${lampada}`),
  control: (command: LightCommand) => api.post('/lights/control', command),
  turnOn: (lampada: string) => api.post(`/lights/${lampada}/on`),
  turnOff: (lampada: string) => api.post(`/lights/${lampada}/off`),
  toggle: (lampada: string) => api.post(`/lights/${lampada}/toggle`),
};

// Switches API
export const switchesApi = {
  getAll: () => api.get<Switch[]>('/switches'),
  getOne: (nome: string) => api.get<Switch>(`/switches/${nome}`),
  control: (command: SwitchCommand) => api.post('/switches/control', command),
  enable: (nome: string) => api.post(`/switches/${nome}/enable`),
  disable: (nome: string) => api.post(`/switches/${nome}/disable`),
};

// Logs API
export const logsApi = {
  getRecent: (limit = 50) => api.get<Log[]>(`/logs/recent?limit=${limit}`),
  getByLight: (comodo: string, limit = 100) => 
    api.get<Log[]>(`/logs/light/${comodo}?limit=${limit}`),
  getAll: (params?: {
    comodo?: string;
    origem?: string;
    limit?: number;
    offset?: number;
  }) => api.get<Log[]>('/logs', { params }),
};

// Health API
export const healthApi = {
  check: () => api.get('/health'),
};

export default api;
