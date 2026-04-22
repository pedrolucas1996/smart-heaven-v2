const API_BASE_URL = (import.meta.env.VITE_API_URL || '/api/v1').replace(//$/, '');

interface ApiResponse<T> {
success: boolean;
data?: T;
error?: string;
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
try {
const token = localStorage.getItem('token');
const headers: Record<string, string> = {
'Content-Type': 'application/json',
};
if (options?.headers && typeof options.headers === 'object') {
  const existingHeaders = options.headers as Record<string, string | string[]>;
  Object.keys(existingHeaders).forEach((key) => {
    const value = existingHeaders[key];
    headers[key] = typeof value === 'string' ? value : String(value);
  });
}

if (token) {
  headers['Authorization'] = [Bearer ${token}](http://_vscodecontentref_/5);
}

const response = await fetch([${API_BASE_URL}${endpoint}](http://_vscodecontentref_/6), {
  headers,
  ...options,
});

if (!response.ok) {
  throw new Error(`HTTP ${response.status}`);
}

const data = await response.json();
return { success: true, data };
} catch (error) {
return {
success: false,
error: error instanceof Error ? error.message : 'Erro desconhecido',
};
}
}

export const lightsApi = {
getAll: () => fetchApi('/lamps', { method: 'GET' }),
toggle: (nome: string) =>
fetchApi(/lamps/${nome}/toggle, {
method: 'POST',
body: JSON.stringify({}),
}),
};

export const switchesApi = {
getAll: () => fetchApi('/switches', { method: 'GET' }),
toggle: (nome: string, isOn: boolean) =>
isOn
? fetchApi(/switches/${nome}/enable, { method: 'POST' })
: fetchApi(/switches/${nome}/disable, { method: 'POST' }),
enable: (nome: string) => fetchApi(/switches/${nome}/enable, { method: 'POST' }),
disable: (nome: string) => fetchApi(/switches/${nome}/disable, { method: 'POST' }),
};
