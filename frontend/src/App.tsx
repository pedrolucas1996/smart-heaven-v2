import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { Lightbulb, LightbulbOff, Power, Wifi, WifiOff } from 'lucide-react';
import { lightsApi, switchesApi, logsApi, healthApi } from './services/api';
import { useWebSocket } from './services/websocket';

function App() {
  const queryClient = useQueryClient();
  const { isConnected, subscribe } = useWebSocket();

  // Fetch lights
  const { data: lights = [], isLoading: lightsLoading } = useQuery({
    queryKey: ['lights'],
    queryFn: async () => {
      const response = await lightsApi.getAll();
      return response.data;
    },
    refetchInterval: 5000,
  });

  // Fetch switches
  const { data: switches = [] } = useQuery({
    queryKey: ['switches'],
    queryFn: async () => {
      const response = await switchesApi.getAll();
      return response.data;
    },
  });

  // Fetch recent logs
  const { data: logs = [] } = useQuery({
    queryKey: ['logs'],
    queryFn: async () => {
      const response = await logsApi.getRecent(20);
      return response.data;
    },
    refetchInterval: 10000,
  });

  // Health check
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await healthApi.check();
      return response.data;
    },
    refetchInterval: 30000,
  });

  // Toggle light mutation
  const toggleLight = useMutation({
    mutationFn: (lampada: string) => lightsApi.toggle(lampada),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lights'] });
      queryClient.invalidateQueries({ queryKey: ['logs'] });
    },
  });

  // Toggle switch mutation
  const toggleSwitch = useMutation({
    mutationFn: ({ nome, ativo }: { nome: string; ativo: boolean }) =>
      ativo ? switchesApi.disable(nome) : switchesApi.enable(nome),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['switches'] });
    },
  });

  // Subscribe to WebSocket updates
  useEffect(() => {
    const unsubLight = subscribe('light_update', () => {
      queryClient.invalidateQueries({ queryKey: ['lights'] });
      queryClient.invalidateQueries({ queryKey: ['logs'] });
    });

    const unsubSwitch = subscribe('switch_update', () => {
      queryClient.invalidateQueries({ queryKey: ['switches'] });
    });

    return () => {
      unsubLight();
      unsubSwitch();
    };
  }, [subscribe, queryClient]);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">🏠 Smart Heaven v2.0</h1>
          <div className="flex gap-4 items-center">
            <div className="flex items-center gap-2">
              {isConnected ? (
                <>
                  <Wifi className="w-5 h-5 text-green-500" />
                  <span className="text-sm text-green-500">Conectado</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-5 h-5 text-red-500" />
                  <span className="text-sm text-red-500">Desconectado</span>
                </>
              )}
            </div>
            {health && (
              <div className="text-sm">
                <span className={health.mqtt_connected ? 'text-green-500' : 'text-red-500'}>
                  MQTT: {health.mqtt_connected ? '✓' : '✗'}
                </span>
                {' | '}
                <span className={health.database_connected ? 'text-green-500' : 'text-red-500'}>
                  DB: {health.database_connected ? '✓' : '✗'}
                </span>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="container mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Lights Section */}
          <div className="lg:col-span-2">
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">💡 Luzes</h2>
              {lightsLoading ? (
                <p>Carregando...</p>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {lights.map((light) => (
                    <button
                      key={light.id}
                      onClick={() => toggleLight.mutate(light.lampada)}
                      disabled={toggleLight.isPending}
                      className={`p-4 rounded-lg border-2 transition-all ${
                        light.estado
                          ? 'bg-yellow-500 border-yellow-400 text-gray-900'
                          : 'bg-gray-700 border-gray-600 text-gray-300'
                      } hover:scale-105 active:scale-95`}
                    >
                      <div className="flex flex-col items-center gap-2">
                        {light.estado ? (
                          <Lightbulb className="w-8 h-8" />
                        ) : (
                          <LightbulbOff className="w-8 h-8" />
                        )}
                        <span className="text-sm font-medium">{light.lampada}</span>
                        <span className="text-xs">
                          {light.estado ? ' on' : ' off'}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Switches Section */}
            <div className="bg-gray-800 rounded-lg p-6 mt-6">
              <h2 className="text-xl font-semibold mb-4">🔘 Interruptores</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {switches.map((sw) => (
                  <button
                    key={sw.id}
                    onClick={() => toggleSwitch.mutate({ nome: sw.nome, ativo: sw.ativo })}
                    disabled={toggleSwitch.isPending}
                    className={`p-3 rounded-lg border transition-all ${
                      sw.ativo
                        ? 'bg-green-600 border-green-500'
                        : 'bg-gray-700 border-gray-600'
                    } hover:scale-105`}
                  >
                    <div className="flex flex-col items-center gap-1">
                      <Power className="w-5 h-5" />
                      <span className="text-xs font-medium">{sw.nome}</span>
                      <span className="text-xs opacity-75">
                        {sw.ativo ? 'Ativo' : 'Inativo'}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Logs Section */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800 rounded-lg p-6 h-full">
              <h2 className="text-xl font-semibold mb-4">📋 Eventos Recentes</h2>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {logs.map((log) => (
                  <div
                    key={log.id}
                    className="bg-gray-700 rounded p-3 text-sm"
                  >
                    <div className="flex justify-between items-start">
                      <span className="font-medium">{log.comodo}</span>
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          log.estado
                            ? 'bg-green-600 text-white'
                            : 'bg-red-600 text-white'
                        }`}
                      >
                        {log.estado ? 'ON' : 'OFF'}
                      </span>
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      <span>{log.origem}</span>
                      {' • '}
                      <span>{new Date(log.timestamp).toLocaleTimeString('pt-BR')}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
