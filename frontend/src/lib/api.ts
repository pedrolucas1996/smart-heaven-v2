// Configuração base da API - Smart Heaven v2 Backend
const API_BASE_URL = (import.meta.env.VITE_API_URL || '/api/v1').replace(/\/$/, '');

declare global {
  interface Window {
    __SH_TOKEN__?: string;
  }
}

const getAuthToken = () => {
  return (
    localStorage.getItem('token') ||
    localStorage.getItem('access_token') ||
    window.__SH_TOKEN__ ||
    null
  );
};

// Tipos de resposta
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Helper genérico para fazer requisições
async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  // Merge with existing headers if provided
  if (options?.headers && typeof options.headers === 'object') {
    const existingHeaders = options.headers as Record<string, string | string[]>;
    Object.keys(existingHeaders).forEach((key) => {
      const value = existingHeaders[key];
      headers[key] = typeof value === 'string' ? value : String(value);
    });
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const urls = [`${API_BASE_URL}${endpoint}`];
  if (API_BASE_URL.startsWith('http') && !endpoint.startsWith('/api/')) {
    urls.push(`/api/v1${endpoint}`);
  }

  let lastError = 'Erro desconhecido';

  for (const url of urls) {
    try {
      const response = await fetch(url, {
        headers,
        ...options,
      });

      const bodyText = await response.text();
      const contentType = response.headers.get('content-type') || '';

      if (!response.ok) {
        let detail = `HTTP ${response.status}`;
        try {
          const parsedError = bodyText ? JSON.parse(bodyText) : null;
          detail =
            parsedError?.detail ||
            parsedError?.error ||
            parsedError?.message ||
            detail;
        } catch {
          // Keep default HTTP detail
        }
        lastError = detail;
        continue;
      }

      if (!bodyText) {
        return { success: true, data: undefined as T };
      }

      let parsed: any;
      try {
        parsed = JSON.parse(bodyText);
      } catch {
        // 200 but HTML/plain text (common when route is wrong): try next candidate URL
        if (contentType.includes('text/html') || bodyText.startsWith('<!DOCTYPE') || bodyText.startsWith('<html')) {
          lastError = 'Resposta HTML inesperada da API';
          continue;
        }
        lastError = 'Resposta inválida da API';
        continue;
      }

      // Support wrapped payloads: { success, data } / { data } / { items }
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
        if (parsed.success === false) {
          return {
            success: false,
            error: parsed.error || parsed.detail || parsed.message || 'Erro da API',
          };
        }

        if ('data' in parsed) {
          return { success: true, data: parsed.data as T };
        }

        if ('items' in parsed) {
          return { success: true, data: parsed.items as T };
        }
      }

      return { success: true, data: parsed as T };
    } catch (error) {
      lastError = error instanceof Error ? error.message : 'Erro desconhecido';
    }
  }

  console.error('API Error:', endpoint, lastError);
  return {
    success: false,
    error: lastError,
  };
}

// API de Iluminação - Adaptado para SH2 backend
export const lightsApi = {
  // GET: Buscar todas as lâmpadas
  getAll: async () => {
    const response = await fetchApi<any[]>('/lights', { method: 'GET' });

    if (!response.success || !response.data) {
      // Backward-compatible fallback
      const fallback = await fetchApi<any[]>('/lamps', { method: 'GET' });
      if (!fallback.success || !fallback.data) {
        return fallback;
      }

      const normalizedFallback = fallback.data.map((item) => ({
        ...item,
        nome: item.nome ?? item.lampada,
        apelido: item.apelido ?? null,
        invertido: typeof item.invertido === 'boolean' ? item.invertido : false,
      }));

      const dedupFallbackMap = new Map<string, any>();
      normalizedFallback.forEach((lamp: any) => {
        const key = String(lamp.nome ?? lamp.lampada ?? lamp.id);
        const prev = dedupFallbackMap.get(key);
        if (!prev || (lamp.id ?? 0) > (prev.id ?? 0)) {
          dedupFallbackMap.set(key, lamp);
        }
      });

      return { success: true, data: Array.from(dedupFallbackMap.values()) };
    }

    const normalized = response.data.map((item) => ({
      ...item,
      nome: item.nome ?? item.lampada,
      apelido: item.apelido ?? null,
      invertido: typeof item.invertido === 'boolean' ? item.invertido : false,
    }));

    // Remove duplicates by lamp name, keeping latest ID
    const dedupMap = new Map<string, any>();
    normalized.forEach((lamp: any) => {
      const key = String(lamp.nome ?? lamp.lampada ?? lamp.id);
      const prev = dedupMap.get(key);
      if (!prev || (lamp.id ?? 0) > (prev.id ?? 0)) {
        dedupMap.set(key, lamp);
      }
    });

    return { success: true, data: Array.from(dedupMap.values()) };
  },

  // POST: Ligar/desligar lâmpada - SH2 usa toggle endpoint
  toggle: async (lampada: string, isOn?: boolean) => {
    const primary = await fetchApi(`/lights/${lampada}/toggle`, {
      method: 'POST',
      body: JSON.stringify({}),
    });

    if (primary.success) {
      return primary;
    }

    return fetchApi(`/lamps/${lampada}/toggle`, {
      method: 'POST',
      body: JSON.stringify({}),
    });
  },

  // POST: Ajustar brilho (não implementado no SH2 ainda)
  setBrightness: (id: string, brightness: number) =>
    fetchApi(`/lamps/${id}/brightness`, {
      method: 'POST',
      body: JSON.stringify({ brightness }),
    }),

  // POST: Ligar/desligar todas de um cômodo (usando control endpoint do SH2)
  toggleRoom: async (room: string, isOn: boolean) => {
    const payload = {
      comodo: room,
      acao: isOn ? 'ligar' : 'desligar',
      origem: 'frontend',
    };

    const primary = await fetchApi(`/lights/control`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    if (primary.success) {
      return primary;
    }

    return fetchApi(`/lamps/control`, {
      method: 'POST',
      body: JSON.stringify({ nome: room, acao: payload.acao, origem: payload.origem }),
    });
  },
};

// API de Interruptores - Adaptado para SH2 backend
export const switchesApi = {
  // GET: Buscar todos os interruptores
  getAll: async () => {
    const response = await fetchApi<any[]>('/switches', { method: 'GET' });

    if (!response.success || !response.data) {
      return response;
    }

    const normalized = response.data.map((item) => ({
      ...item,
      nome: item.nome ?? item.botao,
      base: item.base ?? (item.base_id != null ? `Base ${item.base_id}` : 'Base'),
    }));

    const dedupMap = new Map<string, any>();
    normalized.forEach((sw: any) => {
      const key = String(sw.nome ?? sw.id);
      const prev = dedupMap.get(key);
      if (!prev || (sw.id ?? 0) > (prev.id ?? 0)) {
        dedupMap.set(key, sw);
      }
    });

    return { success: true, data: Array.from(dedupMap.values()) };
  },

  // POST: Habilitar interruptor (ativo = true)
  toggle: (nome: string, isOn: boolean) =>
    isOn 
      ? fetchApi(`/switches/${nome}/enable`, { method: 'POST' })
      : fetchApi(`/switches/${nome}/disable`, { method: 'POST' }),

  // POST: Ativar/desativar interruptor (modo manutenção)
  toggleMaintenance: (nome: string, isActive: boolean) =>
    isActive
      ? fetchApi(`/switches/${nome}/enable`, { method: 'POST' })
      : fetchApi(`/switches/${nome}/disable`, { method: 'POST' }),

  // GET: Buscar interruptores vinculados a uma lâmpada (não implementado no SH2)
  getByLight: (lightId: string) =>
    fetchApi(`/switches/light/${lightId}`, { method: 'GET' }),
};

// API de Portas e Portões
export const doorsApi = {
  // GET: Buscar todas as portas
  getAll: () => fetchApi('/doors', { method: 'GET' }),

  // POST: Abrir/fechar porta
  toggle: (id: string, isOpen: boolean) =>
    fetchApi(`/doors/${id}/toggle`, {
      method: 'POST',
      body: JSON.stringify({ isOpen }),
    }),

  // POST: Trancar/destrancar porta
  toggleLock: (id: string, isLocked: boolean) =>
    fetchApi(`/doors/${id}/lock`, {
      method: 'POST',
      body: JSON.stringify({ isLocked }),
    }),

  // POST: Trancar todas de uma área
  lockArea: (area: string, isLocked: boolean) =>
    fetchApi(`/doors/area/${area}/lock`, {
      method: 'POST',
      body: JSON.stringify({ isLocked }),
    }),
};

// API de Clima
export const climateApi = {
  // GET: Buscar dados atuais de todos os sensores
  getAll: () => fetchApi('/climate/sensors', { method: 'GET' }),

  // GET: Buscar histórico de um cômodo
  getHistory: (room: string, hours: number = 24) =>
    fetchApi(`/climate/history/${room}?hours=${hours}`, { method: 'GET' }),

  // GET: Buscar dados de um sensor específico
  getRoom: (room: string) => fetchApi(`/climate/sensors/${room}`, { method: 'GET' }),
};

// API de Câmeras
export const camerasApi = {
  // GET: Buscar todas as câmeras
  getAll: () => fetchApi('/cameras', { method: 'GET' }),

  // GET: Buscar imagem atualizada de uma câmera
  getSnapshot: (id: string) => fetchApi(`/cameras/${id}/snapshot`, { method: 'GET' }),

  // POST: Iniciar/parar gravação
  toggleRecording: (id: string, recording: boolean) =>
    fetchApi(`/cameras/${id}/recording`, {
      method: 'POST',
      body: JSON.stringify({ recording }),
    }),

  // POST: Capturar imagem
  capture: (id: string) =>
    fetchApi(`/cameras/${id}/capture`, {
      method: 'POST',
    }),
};

// API de Carro
export const carApi = {
  // GET: Buscar status do carro
  getStatus: () => fetchApi('/car/status', { method: 'GET' }),

  // POST: Trancar/destrancar carro
  toggleLock: (isLocked: boolean) =>
    fetchApi('/car/lock', {
      method: 'POST',
      body: JSON.stringify({ isLocked }),
    }),

  // POST: Ligar/desligar motor
  toggleEngine: (engineRunning: boolean) =>
    fetchApi('/car/engine', {
      method: 'POST',
      body: JSON.stringify({ engineRunning }),
    }),

  // GET: Buscar localização atualizada
  getLocation: () => fetchApi('/car/location', { method: 'GET' }),
};

export { API_BASE_URL };