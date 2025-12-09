import { useState, useEffect } from 'react';
import { ToggleLeft, ToggleRight, Power, Wrench, Home, UtensilsCrossed, Bath, Bed, Trees, Warehouse, AlertCircle, Clock } from 'lucide-react';
import { switchesApi } from '../lib/api';

interface Switch {
  id: string;
  name: string;
  room: string;
  isActive: boolean; // Se está ativo (não em manutenção)
  isOn: boolean; // Estado atual do interruptor
  linkedLights: string[]; // IDs das lâmpadas vinculadas
  lastPressed?: string; // ISO timestamp da última vez que foi pressionado
}

interface SwitchControlProps {
  compact?: boolean;
}

export function SwitchControl({ compact = false }: SwitchControlProps) {
  const [switches, setSwitches] = useState<Switch[]>([
    { id: 's1', name: 'Interruptor Principal', room: 'Sala', isActive: true, isOn: true, linkedLights: ['1'], lastPressed: '2025-12-08T10:30:00Z' },
    { id: 's2', name: 'Interruptor da Porta', room: 'Sala', isActive: true, isOn: true, linkedLights: ['1', '2'], lastPressed: '2025-12-08T09:15:00Z' },
    { id: 's3', name: 'Interruptor Three-Way 1', room: 'Sala', isActive: true, isOn: false, linkedLights: ['3'], lastPressed: '2025-12-08T08:45:00Z' },
    { id: 's4', name: 'Interruptor Three-Way 2', room: 'Sala', isActive: true, isOn: false, linkedLights: ['3'], lastPressed: '2025-12-07T22:30:00Z' },
    { id: 's5', name: 'Interruptor Bancada', room: 'Cozinha', isActive: true, isOn: true, linkedLights: ['5'], lastPressed: '2025-12-08T07:00:00Z' },
    { id: 's6', name: 'Interruptor Geral', room: 'Cozinha', isActive: true, isOn: false, linkedLights: ['4', '5', '6'], lastPressed: '2025-12-07T23:00:00Z' },
    { id: 's7', name: 'Interruptor Cabeceira Esq', room: 'Suite', isActive: true, isOn: false, linkedLights: ['8'], lastPressed: '2025-12-08T06:00:00Z' },
    { id: 's8', name: 'Interruptor Cabeceira Dir', room: 'Suite', isActive: true, isOn: true, linkedLights: ['9'], lastPressed: '2025-12-08T06:15:00Z' },
    { id: 's9', name: 'Interruptor Porta Suite', room: 'Suite', isActive: true, isOn: true, linkedLights: ['7'], lastPressed: '2025-12-08T09:00:00Z' },
    { id: 's10', name: 'Interruptor Principal', room: 'Banheiro', isActive: false, isOn: false, linkedLights: ['11', '12'], lastPressed: '2025-12-06T18:00:00Z' },
    { id: 's11', name: 'Interruptor Jardim', room: 'Jardim', isActive: true, isOn: true, linkedLights: ['13', '14'], lastPressed: '2025-12-07T18:30:00Z' },
    { id: 's12', name: 'Interruptor Garagem', room: 'Garagem', isActive: true, isOn: false, linkedLights: ['15'], lastPressed: '2025-12-08T08:00:00Z' },
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

  // Formata data/hora de forma amigável
  const formatLastPressed = (timestamp?: string): string => {
    if (!timestamp) return 'Nunca acionado';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    // Tempo relativo
    if (diffMins < 1) return 'Agora mesmo';
    if (diffMins < 60) return `Há ${diffMins} min`;
    if (diffHours < 24) return `Há ${diffHours}h`;
    if (diffDays === 1) return 'Ontem';
    if (diffDays < 7) return `Há ${diffDays} dias`;

    // Data formatada
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // GET: Carregar dados da API ao montar o componente
  useEffect(() => {
    loadSwitches();
  }, []);

  const loadSwitches = async () => {
    setLoading(true);
    setError(null);
    const response = await switchesApi.getAll();
    
    if (response.success && response.data) {
      setSwitches(response.data as Switch[]);
    } else {
      setError(response.error || 'Erro ao carregar interruptores');
    }
    setLoading(false);
  };

  // POST: Acionar interruptor (só funciona se estiver ativo)
  const toggleSwitch = async (id: string) => {
    const switchItem = switches.find(s => s.id === id);
    if (!switchItem || !switchItem.isActive) return; // Não aciona se estiver em manutenção

    // Atualiza UI otimisticamente
    setSwitches(switches.map(s =>
      s.id === id ? { ...s, isOn: !s.isOn } : s
    ));

    // Envia para API
    const response = await switchesApi.toggle(id, !switchItem.isOn);
    
    if (!response.success) {
      // Reverte em caso de erro
      setSwitches(switches.map(s =>
        s.id === id ? { ...s, isOn: switchItem.isOn } : s
      ));
      setError(response.error || 'Erro ao acionar interruptor');
    }
  };

  // POST: Ativar/desativar interruptor (modo manutenção)
  const toggleMaintenance = async (id: string) => {
    const switchItem = switches.find(s => s.id === id);
    if (!switchItem) return;

    // Atualiza UI otimisticamente
    setSwitches(switches.map(s =>
      s.id === id ? { ...s, isActive: !s.isActive } : s
    ));

    // Envia para API
    const response = await switchesApi.toggleMaintenance(id, !switchItem.isActive);
    
    if (!response.success) {
      // Reverte em caso de erro
      setSwitches(switches.map(s =>
        s.id === id ? { ...s, isActive: switchItem.isActive } : s
      ));
      setError(response.error || 'Erro ao alterar modo manutenção');
    }
  };

  const filteredSwitches = selectedRoom === 'Todos'
    ? switches
    : switches.filter(s => s.room === selectedRoom);

  const activeSwitches = filteredSwitches.filter(s => s.isActive).length;
  const inactiveSwitches = filteredSwitches.filter(s => !s.isActive).length;
  const onSwitches = filteredSwitches.filter(s => s.isOn && s.isActive).length;

  const displaySwitches = compact ? switches.slice(0, 3) : filteredSwitches;

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-blue-100 p-3 rounded-lg">
            <ToggleRight className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2>Interruptores Inteligentes</h2>
            <p className="text-slate-500 text-sm">
              {activeSwitches} ativos · {onSwitches} acionados
              {inactiveSwitches > 0 && ` · ${inactiveSwitches} em manutenção`}
            </p>
          </div>
        </div>
        {inactiveSwitches > 0 && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-100 text-amber-700 rounded-full">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">Manutenção</span>
          </div>
        )}
      </div>

      {/* Room navigation */}
      {!compact && (
        <div className="mb-6">
          <h3 className="text-sm text-slate-600 mb-3">Cômodos</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2">
            {rooms.map((room) => {
              const Icon = room.icon;
              const roomSwitchesCount = room.name === 'Todos'
                ? switches.length
                : switches.filter(s => s.room === room.name).length;
              const roomSwitchesActive = room.name === 'Todos'
                ? switches.filter(s => s.isActive).length
                : switches.filter(s => s.room === room.name && s.isActive).length;
              
              return (
                <button
                  key={room.name}
                  onClick={() => setSelectedRoom(room.name)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    selectedRoom === room.name
                      ? 'border-blue-400 bg-blue-50'
                      : 'border-slate-200 bg-white hover:border-blue-200'
                  }`}
                >
                  <Icon className={`w-5 h-5 mx-auto mb-1 ${
                    selectedRoom === room.name ? 'text-blue-600' : 'text-slate-600'
                  }`} />
                  <p className="text-xs text-center">{room.name}</p>
                  <p className="text-xs text-center text-slate-500 mt-0.5">
                    {roomSwitchesActive}/{roomSwitchesCount}
                  </p>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Switches Grid */}
      <div className="space-y-3">
        {displaySwitches.map(switchItem => (
          <div
            key={switchItem.id}
            className={`p-4 rounded-lg border-2 transition-all ${
              !switchItem.isActive
                ? 'border-amber-300 bg-amber-50'
                : switchItem.isOn
                ? 'border-blue-300 bg-blue-50'
                : 'border-slate-200 bg-white'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 flex-1">
                {switchItem.isOn && switchItem.isActive ? (
                  <ToggleRight className="w-6 h-6 text-blue-600" />
                ) : (
                  <ToggleLeft className="w-6 h-6 text-slate-400" />
                )}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm">{switchItem.name}</h3>
                    {!switchItem.isActive && (
                      <span className="px-2 py-0.5 bg-amber-200 text-amber-800 text-xs rounded-full flex items-center gap-1">
                        <Wrench className="w-3 h-3" />
                        Manutenção
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-500">
                    {switchItem.room} · {switchItem.linkedLights.length} lâmpada{switchItem.linkedLights.length !== 1 ? 's' : ''} vinculada{switchItem.linkedLights.length !== 1 ? 's' : ''}
                  </p>
                  {!compact && (
                    <p className="text-xs text-slate-400 mt-1">
                      IDs: {switchItem.linkedLights.join(', ')}
                    </p>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2">
                {/* Botão de manutenção */}
                <button
                  onClick={() => toggleMaintenance(switchItem.id)}
                  className={`p-2 rounded-lg transition-all ${
                    switchItem.isActive
                      ? 'bg-slate-200 text-slate-600 hover:bg-slate-300'
                      : 'bg-amber-500 text-white hover:bg-amber-600'
                  }`}
                  title={switchItem.isActive ? 'Colocar em manutenção' : 'Ativar interruptor'}
                >
                  {switchItem.isActive ? (
                    <Wrench className="w-4 h-4" />
                  ) : (
                    <Power className="w-4 h-4" />
                  )}
                </button>

                {/* Botão de acionar */}
                <button
                  onClick={() => toggleSwitch(switchItem.id)}
                  disabled={!switchItem.isActive}
                  className={`px-4 py-2 rounded-lg transition-all ${
                    !switchItem.isActive
                      ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                      : switchItem.isOn
                      ? 'bg-blue-500 text-white hover:bg-blue-600'
                      : 'bg-slate-300 text-slate-700 hover:bg-slate-400'
                  }`}
                  title={!switchItem.isActive ? 'Interruptor em manutenção' : ''}
                >
                  {switchItem.isOn ? 'Ligado' : 'Desligado'}
                </button>
              </div>
            </div>
            {!compact && (
              <div className="mt-2 text-xs text-slate-500">
                Última ação: {formatLastPressed(switchItem.lastPressed)}
              </div>
            )}
          </div>
        ))}
      </div>

      {compact && switches.length > 3 && (
        <div className="mt-4 text-center">
          <p className="text-sm text-slate-500">+{switches.length - 3} interruptores adicionais</p>
        </div>
      )}

      {/* Legend */}
      {!compact && (
        <div className="mt-6 pt-6 border-t">
          <h3 className="text-sm mb-3">Como funciona</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-slate-600">
            <div className="flex items-start gap-2">
              <ToggleRight className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <p><span className="font-medium">Interruptor Ligado:</span> Lâmpadas vinculadas estão acesas</p>
            </div>
            <div className="flex items-start gap-2">
              <ToggleLeft className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
              <p><span className="font-medium">Interruptor Desligado:</span> Lâmpadas vinculadas estão apagadas</p>
            </div>
            <div className="flex items-start gap-2">
              <Wrench className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
              <p><span className="font-medium">Modo Manutenção:</span> Interruptor desativado, não responde a comandos</p>
            </div>
            <div className="flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <p><span className="font-medium">Múltiplos Interruptores:</span> Uma lâmpada pode ter vários interruptores</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}