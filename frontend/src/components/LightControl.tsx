import { useState, useEffect } from 'react';
import { Lightbulb, Zap, Home, UtensilsCrossed, Bath, Bed, Trees, Warehouse, Loader2 } from 'lucide-react';
import { lightsApi } from '../lib/api';

interface Light {
  id: string;
  name: string;
  room: string;
  isOn: boolean;
  brightness: number;
}

interface LightControlProps {
  compact?: boolean;
}

export function LightControl({ compact = false }: LightControlProps) {
  const [lights, setLights] = useState<Light[]>([
    { id: '1', name: 'Luz Principal', room: 'Sala', isOn: true, brightness: 80 },
    { id: '2', name: 'Luz Ambiente', room: 'Sala', isOn: true, brightness: 40 },
    { id: '3', name: 'Luz de Leitura', room: 'Sala', isOn: false, brightness: 60 },
    { id: '4', name: 'Luz Principal', room: 'Cozinha', isOn: false, brightness: 100 },
    { id: '5', name: 'Luz da Bancada', room: 'Cozinha', isOn: true, brightness: 90 },
    { id: '6', name: 'Luz da Pia', room: 'Cozinha', isOn: false, brightness: 80 },
    { id: '7', name: 'Luz Principal', room: 'Suite', isOn: true, brightness: 60 },
    { id: '8', name: 'Abajur Esquerdo', room: 'Suite', isOn: false, brightness: 30 },
    { id: '9', name: 'Abajur Direito', room: 'Suite', isOn: true, brightness: 35 },
    { id: '10', name: 'Luz do Closet', room: 'Suite', isOn: false, brightness: 100 },
    { id: '11', name: 'Luz do Espelho', room: 'Banheiro', isOn: false, brightness: 100 },
    { id: '12', name: 'Luz Principal', room: 'Banheiro', isOn: false, brightness: 90 },
    { id: '13', name: 'Luz Externa', room: 'Jardim', isOn: true, brightness: 100 },
    { id: '14', name: 'Luz do Caminho', room: 'Jardim', isOn: true, brightness: 70 },
    { id: '15', name: 'Luz da Garagem', room: 'Garagem', isOn: false, brightness: 100 },
  ]);

  const [selectedRoom, setSelectedRoom] = useState<string>('Todos');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const rooms = [
    { name: 'Todos', icon: Home },
    { name: 'Sala', icon: Home },
    { name: 'Cozinha', icon: UtensilsCrossed },
    { name: 'Suite', icon: Bed },
    { name: 'Banheiro', icon: Bath },
    { name: 'Jardim', icon: Trees },
    { name: 'Garagem', icon: Warehouse },
  ];

  // GET: Carregar dados da API ao montar o componente
  useEffect(() => {
    loadLights();
  }, []);

  const loadLights = async () => {
    setLoading(true);
    setError(null);
    const response = await lightsApi.getAll();
    
    if (response.success && response.data) {
      setLights(response.data as Light[]);
    } else {
      setError(response.error || 'Erro ao carregar lâmpadas');
      // Continua usando dados mock em caso de erro
    }
    setLoading(false);
  };

  // POST: Ligar/desligar lâmpada
  const toggleLight = async (id: string) => {
    const light = lights.find(l => l.id === id);
    if (!light) return;

    // Atualiza UI otimisticamente
    setLights(lights.map(l =>
      l.id === id ? { ...l, isOn: !l.isOn } : l
    ));

    // Envia para API
    const response = await lightsApi.toggle(id, !light.isOn);
    
    if (!response.success) {
      // Reverte em caso de erro
      setLights(lights.map(l =>
        l.id === id ? { ...l, isOn: light.isOn } : l
      ));
      setError(response.error || 'Erro ao alterar lâmpada');
    }
  };

  // POST: Ajustar brilho
  const setBrightness = async (id: string, brightness: number) => {
    const light = lights.find(l => l.id === id);
    if (!light) return;

    // Atualiza UI
    setLights(lights.map(l =>
      l.id === id ? { ...l, brightness } : l
    ));

    // Envia para API (com debounce seria melhor para sliders)
    const response = await lightsApi.setBrightness(id, brightness);
    
    if (!response.success) {
      setError(response.error || 'Erro ao ajustar brilho');
    }
  };

  const filteredLights = selectedRoom === 'Todos' 
    ? lights 
    : lights.filter(light => light.room === selectedRoom);

  const totalLights = filteredLights.length;
  const lightsOn = filteredLights.filter(l => l.isOn).length;
  const averageBrightness = Math.round(
    filteredLights.filter(l => l.isOn).reduce((sum, l) => sum + l.brightness, 0) / lightsOn || 0
  );

  const displayLights = compact ? lights.slice(0, 4) : filteredLights;

  // POST: Ligar/desligar todas as luzes de um cômodo
  const toggleAllInRoom = async () => {
    const roomLights = selectedRoom === 'Todos' ? lights : lights.filter(l => l.room === selectedRoom);
    const allOn = roomLights.every(l => l.isOn);
    
    // Atualiza UI otimisticamente
    setLights(lights.map(light => {
      if (selectedRoom === 'Todos' || light.room === selectedRoom) {
        return { ...light, isOn: !allOn };
      }
      return light;
    }));

    // Envia para API
    const response = await lightsApi.toggleRoom(selectedRoom, !allOn);
    
    if (!response.success) {
      // Reverte em caso de erro
      loadLights();
      setError(response.error || 'Erro ao alterar luzes do cômodo');
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-yellow-100 p-3 rounded-lg">
            <Lightbulb className="w-6 h-6 text-yellow-600" />
          </div>
          <div>
            <h2>Controle de Iluminação</h2>
            <p className="text-slate-500 text-sm">{lightsOn} de {totalLights} acesas</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-yellow-600">
          <Zap className="w-5 h-5" />
          <span>{averageBrightness}%</span>
        </div>
      </div>

      {/* Room navigation */}
      {!compact && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm text-slate-600">Cômodos</h3>
            <button
              onClick={toggleAllInRoom}
              className="text-xs px-3 py-1.5 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors"
            >
              {filteredLights.every(l => l.isOn) ? 'Desligar Todas' : 'Ligar Todas'}
            </button>
          </div>
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-7 gap-2">
            {rooms.map((room) => {
              const Icon = room.icon;
              const roomLightCount = room.name === 'Todos' 
                ? lights.length 
                : lights.filter(l => l.room === room.name).length;
              const roomLightsOn = room.name === 'Todos'
                ? lights.filter(l => l.isOn).length
                : lights.filter(l => l.room === room.name && l.isOn).length;
              
              return (
                <button
                  key={room.name}
                  onClick={() => setSelectedRoom(room.name)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    selectedRoom === room.name
                      ? 'border-yellow-400 bg-yellow-50'
                      : 'border-slate-200 bg-white hover:border-yellow-200'
                  }`}
                >
                  <Icon className={`w-5 h-5 mx-auto mb-1 ${
                    selectedRoom === room.name ? 'text-yellow-600' : 'text-slate-600'
                  }`} />
                  <p className="text-xs text-center">{room.name}</p>
                  <p className="text-xs text-center text-slate-500 mt-0.5">
                    {roomLightsOn}/{roomLightCount}
                  </p>
                </button>
              );
            })}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {displayLights.map(light => (
          <div
            key={light.id}
            className={`p-4 rounded-lg border-2 transition-all ${
              light.isOn
                ? 'border-yellow-300 bg-yellow-50'
                : 'border-slate-200 bg-slate-50'
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex-1">
                <h3 className="text-sm">{light.name}</h3>
                <p className="text-xs text-slate-500">{light.room}</p>
              </div>
              <button
                onClick={() => toggleLight(light.id)}
                className={`p-2 rounded-lg transition-all ${
                  light.isOn
                    ? 'bg-yellow-500 text-white hover:bg-yellow-600'
                    : 'bg-slate-200 text-slate-400 hover:bg-slate-300'
                }`}
              >
                <Lightbulb className="w-5 h-5" />
              </button>
            </div>
            
            {light.isOn && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-600">Brilho</span>
                  <span>{light.brightness}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={light.brightness}
                  onChange={(e) => setBrightness(light.id, parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-yellow-500"
                />
              </div>
            )}
          </div>
        ))}
      </div>

      {compact && lights.length > 4 && (
        <div className="mt-4 text-center">
          <p className="text-sm text-slate-500">+{lights.length - 4} lâmpadas adicionais</p>
        </div>
      )}
    </div>
  );
}