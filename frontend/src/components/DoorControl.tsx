import { useState, useEffect } from 'react';
import { DoorOpen, DoorClosed, Lock, Unlock, AlertCircle, Home, Warehouse, ArrowLeftRight } from 'lucide-react';
import { doorsApi } from '../lib/api';

interface Door {
  id: string;
  name: string;
  type: 'door' | 'gate';
  area: string;
  isOpen: boolean;
  isLocked: boolean;
}

interface DoorControlProps {
  compact?: boolean;
}

export function DoorControl({ compact = false }: DoorControlProps) {
  const [doors, setDoors] = useState<Door[]>([
    { id: '1', name: 'Porta Principal', type: 'door', area: 'Entrada', isOpen: false, isLocked: true },
    { id: '2', name: 'Porta Lateral', type: 'door', area: 'Entrada', isOpen: false, isLocked: true },
    { id: '3', name: 'Porta dos Fundos', type: 'door', area: 'Fundos', isOpen: false, isLocked: true },
    { id: '4', name: 'Porta da Cozinha', type: 'door', area: 'Fundos', isOpen: false, isLocked: false },
    { id: '5', name: 'Porta da Garagem', type: 'door', area: 'Garagem', isOpen: false, isLocked: false },
    { id: '6', name: 'Portão Principal', type: 'gate', area: 'Entrada', isOpen: false, isLocked: false },
    { id: '7', name: 'Portão da Garagem', type: 'gate', area: 'Garagem', isOpen: false, isLocked: false },
    { id: '8', name: 'Portão do Jardim', type: 'gate', area: 'Fundos', isOpen: false, isLocked: false },
  ]);

  const [selectedArea, setSelectedArea] = useState<string>('Todas');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const areas = [
    { name: 'Todas', icon: Home },
    { name: 'Entrada', icon: DoorOpen },
    { name: 'Garagem', icon: Warehouse },
    { name: 'Fundos', icon: ArrowLeftRight },
  ];

  // GET: Carregar dados da API ao montar o componente
  useEffect(() => {
    loadDoors();
  }, []);

  const loadDoors = async () => {
    setLoading(true);
    setError(null);
    const response = await doorsApi.getAll();
    
    if (response.success && response.data) {
      setDoors(response.data as Door[]);
    } else {
      setError(response.error || 'Erro ao carregar portas');
    }
    setLoading(false);
  };

  // POST: Abrir/fechar porta
  const toggleDoor = async (id: string) => {
    const door = doors.find(d => d.id === id);
    if (!door || door.isLocked) return;

    // Atualiza UI otimisticamente
    setDoors(doors.map(d =>
      d.id === id ? { ...d, isOpen: !d.isOpen } : d
    ));

    // Envia para API
    const response = await doorsApi.toggle(id, !door.isOpen);
    
    if (!response.success) {
      // Reverte em caso de erro
      setDoors(doors.map(d =>
        d.id === id ? { ...d, isOpen: door.isOpen } : d
      ));
      setError(response.error || 'Erro ao alterar porta');
    }
  };

  // POST: Trancar/destrancar porta
  const toggleLock = async (id: string) => {
    const door = doors.find(d => d.id === id);
    if (!door || door.isOpen) return;

    // Atualiza UI otimisticamente
    setDoors(doors.map(d =>
      d.id === id ? { ...d, isLocked: !d.isLocked } : d
    ));

    // Envia para API
    const response = await doorsApi.toggleLock(id, !door.isLocked);
    
    if (!response.success) {
      // Reverte em caso de erro
      setDoors(doors.map(d =>
        d.id === id ? { ...d, isLocked: door.isLocked } : d
      ));
      setError(response.error || 'Erro ao trancar/destrancar porta');
    }
  };

  const filteredDoors = selectedArea === 'Todas'
    ? doors
    : doors.filter(door => door.area === selectedArea);

  const openDoors = filteredDoors.filter(d => d.isOpen).length;
  const unlockedDoors = filteredDoors.filter(d => !d.isLocked).length;

  const displayDoors = compact ? doors.slice(0, 3) : filteredDoors;

  const lockAllInArea = () => {
    const areaDoors = selectedArea === 'Todas' ? doors : doors.filter(d => d.area === selectedArea);
    const allLocked = areaDoors.every(d => d.isLocked || d.isOpen);
    
    setDoors(doors.map(door => {
      if ((selectedArea === 'Todas' || door.area === selectedArea) && !door.isOpen) {
        return { ...door, isLocked: !allLocked };
      }
      return door;
    }));
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-100 p-3 rounded-lg">
            <DoorOpen className="w-6 h-6 text-indigo-600" />
          </div>
          <div>
            <h2>Portas & Portões</h2>
            <p className="text-slate-500 text-sm">{openDoors} abertas · {unlockedDoors} destrancadas</p>
          </div>
        </div>
        {(openDoors > 0 || unlockedDoors > 0) && (
          <AlertCircle className="w-5 h-5 text-amber-500" />
        )}
      </div>

      {/* Area navigation */}
      {!compact && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm text-slate-600">Áreas</h3>
            <button
              onClick={lockAllInArea}
              className="text-xs px-3 py-1.5 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
            >
              {filteredDoors.every(d => d.isLocked || d.isOpen) ? 'Destrancar Todas' : 'Trancar Todas'}
            </button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {areas.map((area) => {
              const Icon = area.icon;
              const areaDoorsCount = area.name === 'Todas'
                ? doors.length
                : doors.filter(d => d.area === area.name).length;
              const areaDoorsLocked = area.name === 'Todas'
                ? doors.filter(d => d.isLocked).length
                : doors.filter(d => d.area === area.name && d.isLocked).length;
              
              return (
                <button
                  key={area.name}
                  onClick={() => setSelectedArea(area.name)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    selectedArea === area.name
                      ? 'border-indigo-400 bg-indigo-50'
                      : 'border-slate-200 bg-white hover:border-indigo-200'
                  }`}
                >
                  <Icon className={`w-5 h-5 mx-auto mb-1 ${
                    selectedArea === area.name ? 'text-indigo-600' : 'text-slate-600'
                  }`} />
                  <p className="text-xs text-center">{area.name}</p>
                  <p className="text-xs text-center text-slate-500 mt-0.5">
                    {areaDoorsLocked}/{areaDoorsCount} trancadas
                  </p>
                </button>
              );
            })}
          </div>
        </div>
      )}

      <div className="space-y-3">
        {displayDoors.map(door => (
          <div
            key={door.id}
            className={`p-4 rounded-lg border-2 transition-all ${
              door.isOpen
                ? 'border-amber-300 bg-amber-50'
                : door.isLocked
                ? 'border-green-300 bg-green-50'
                : 'border-slate-200 bg-slate-50'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 flex-1">
                {door.isOpen ? (
                  <DoorOpen className="w-5 h-5 text-amber-600" />
                ) : (
                  <DoorClosed className="w-5 h-5 text-slate-600" />
                )}
                <div className="flex-1">
                  <h3 className="text-sm">{door.name}</h3>
                  <p className="text-xs text-slate-500">
                    {door.area} · {door.type === 'door' ? 'Porta' : 'Portão'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => toggleLock(door.id)}
                  disabled={door.isOpen}
                  className={`p-2 rounded-lg transition-all ${
                    door.isLocked
                      ? 'bg-green-500 text-white hover:bg-green-600'
                      : 'bg-amber-500 text-white hover:bg-amber-600'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                  title={door.isOpen ? 'Feche primeiro para trancar' : ''}
                >
                  {door.isLocked ? (
                    <Lock className="w-4 h-4" />
                  ) : (
                    <Unlock className="w-4 h-4" />
                  )}
                </button>
                <button
                  onClick={() => toggleDoor(door.id)}
                  disabled={door.isLocked}
                  className={`px-4 py-2 rounded-lg text-sm transition-all ${
                    door.isLocked
                      ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                      : door.isOpen
                      ? 'bg-amber-500 text-white hover:bg-amber-600'
                      : 'bg-indigo-500 text-white hover:bg-indigo-600'
                  }`}
                  title={door.isLocked ? 'Destranque primeiro para abrir' : ''}
                >
                  {door.isOpen ? 'Fechar' : 'Abrir'}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {compact && doors.length > 3 && (
        <div className="mt-4 text-center">
          <p className="text-sm text-slate-500">+{doors.length - 3} acessos adicionais</p>
        </div>
      )}
    </div>
  );
}