import { useState, useEffect } from 'react';
import { DoorOpen, DoorClosed, Lock, Unlock, AlertCircle, Home, Warehouse, ArrowLeftRight, Shield, Maximize2 } from 'lucide-react';
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

  const toggleDoor = async (id: string) => {
    const door = doors.find(d => d.id === id);
    if (!door || door.isLocked) return;

    setDoors(doors.map(d =>
      d.id === id ? { ...d, isOpen: !d.isOpen } : d
    ));

    const response = await doorsApi.toggle(id, !door.isOpen);
    
    if (!response.success) {
      setDoors(doors.map(d =>
        d.id === id ? { ...d, isOpen: door.isOpen } : d
      ));
      setError(response.error || 'Erro ao alterar porta');
    }
  };

  const toggleLock = async (id: string) => {
    const door = doors.find(d => d.id === id);
    if (!door || door.isOpen) return;

    setDoors(doors.map(d =>
      d.id === id ? { ...d, isLocked: !d.isLocked } : d
    ));

    const response = await doorsApi.toggleLock(id, !door.isLocked);
    
    if (!response.success) {
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
  const lockedDoors = filteredDoors.filter(d => d.isLocked).length;
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

  if (compact) {
    return (
      <div className="backdrop-blur-xl bg-gradient-to-br from-emerald-900/40 to-slate-900/60 rounded-3xl border border-emerald-500/20 p-6 shadow-2xl">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-white mb-1">Security</h2>
            <p className="text-slate-400 text-sm">{openDoors} open · {lockedDoors} locked</p>
          </div>
          <button className="p-2 rounded-xl bg-white/5 hover:bg-white/10 transition-all">
            <Maximize2 className="w-4 h-4 text-slate-400" />
          </button>
        </div>

        {/* Security Status */}
        <div className="mb-6">
          <div className="flex items-center gap-4 mb-4">
            <div className={`p-4 rounded-2xl ${lockedDoors === doors.length ? 'bg-green-500/20' : 'bg-amber-500/20'}`}>
              <Shield className={`w-8 h-8 ${lockedDoors === doors.length ? 'text-green-400' : 'text-amber-400'}`} />
            </div>
            <div>
              <div className="text-3xl text-white">{lockedDoors}/{doors.length}</div>
              <p className="text-sm text-slate-400">Secured</p>
            </div>
          </div>
          
          {/* Progress bar */}
          <div className="relative h-2 bg-slate-800 rounded-full overflow-hidden">
            <div 
              className={`absolute h-full transition-all duration-500 rounded-full ${
                lockedDoors === doors.length ? 'bg-gradient-to-r from-green-500 to-emerald-400' : 'bg-gradient-to-r from-amber-500 to-yellow-400'
              }`}
              style={{ width: `${(lockedDoors / doors.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Quick Access */}
        <div className="space-y-2">
          {displayDoors.map((door) => (
            <div
              key={door.id}
              className={`p-4 rounded-2xl border transition-all ${
                door.isOpen
                  ? 'bg-amber-500/20 border-amber-500/30'
                  : door.isLocked
                  ? 'bg-green-500/20 border-green-500/30'
                  : 'bg-white/5 border-white/10'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {door.isOpen ? (
                    <DoorOpen className="w-5 h-5 text-amber-400" />
                  ) : (
                    <DoorClosed className="w-5 h-5 text-slate-400" />
                  )}
                  <div>
                    <p className="text-white text-sm">{door.name}</p>
                    <p className="text-xs text-slate-400">{door.area}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {door.isLocked ? (
                    <Lock className="w-4 h-4 text-green-400" />
                  ) : (
                    <Unlock className="w-4 h-4 text-amber-400" />
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {doors.length > 3 && (
          <div className="mt-4 text-center">
            <p className="text-sm text-slate-400">+{doors.length - 3} more access points</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="backdrop-blur-xl bg-gradient-to-br from-emerald-900/40 to-slate-900/60 rounded-3xl border border-emerald-500/20 p-8 shadow-2xl">
      <div className="flex items-start justify-between mb-8">
        <div>
          <h2 className="text-2xl text-white mb-2">Doors & Gates</h2>
          <p className="text-slate-400">{openDoors} open · {lockedDoors} locked · {unlockedDoors} unlocked</p>
        </div>
        <div className="flex items-center gap-3">
          {(openDoors > 0 || unlockedDoors > 0) && (
            <div className="px-4 py-2 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-amber-400" />
              <span className="text-sm text-amber-300">Attention Required</span>
            </div>
          )}
          {openDoors === 0 && unlockedDoors === 0 && (
            <div className="px-4 py-2 rounded-xl bg-green-500/20 border border-green-500/30 flex items-center gap-2">
              <Shield className="w-4 h-4 text-green-400" />
              <span className="text-sm text-green-300">All Secured</span>
            </div>
          )}
        </div>
      </div>

      {/* Area Navigation */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-slate-300">Areas</h3>
          <button
            onClick={lockAllInArea}
            className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all text-sm shadow-lg shadow-green-500/20"
          >
            {filteredDoors.every(d => d.isLocked || d.isOpen) ? 'Unlock All' : 'Lock All'}
          </button>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
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
                className={`p-4 rounded-2xl border transition-all ${
                  selectedArea === area.name
                    ? 'bg-emerald-500/20 border-emerald-500/30 shadow-lg shadow-emerald-500/10'
                    : 'bg-white/5 border-white/10 hover:bg-white/10'
                }`}
              >
                <Icon className={`w-6 h-6 mx-auto mb-2 ${
                  selectedArea === area.name ? 'text-emerald-400' : 'text-slate-400'
                }`} />
                <p className="text-sm text-white text-center">{area.name}</p>
                <p className="text-xs text-slate-400 text-center mt-1">
                  {areaDoorsLocked}/{areaDoorsCount} locked
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Doors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {displayDoors.map(door => (
          <div
            key={door.id}
            className={`p-6 rounded-2xl border transition-all ${
              door.isOpen
                ? 'bg-gradient-to-br from-amber-500/20 to-orange-500/10 border-amber-500/30 shadow-lg shadow-amber-500/10'
                : door.isLocked
                ? 'bg-gradient-to-br from-green-500/20 to-emerald-500/10 border-green-500/30 shadow-lg shadow-green-500/10'
                : 'bg-white/5 border-white/10'
            }`}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                {door.isOpen ? (
                  <div className="p-3 rounded-xl bg-amber-500/30">
                    <DoorOpen className="w-6 h-6 text-amber-400" />
                  </div>
                ) : (
                  <div className={`p-3 rounded-xl ${door.isLocked ? 'bg-green-500/30' : 'bg-slate-700/50'}`}>
                    <DoorClosed className={`w-6 h-6 ${door.isLocked ? 'text-green-400' : 'text-slate-400'}`} />
                  </div>
                )}
                <div>
                  <p className="text-white">{door.name}</p>
                  <p className="text-sm text-slate-400">{door.area} · {door.type === 'door' ? 'Door' : 'Gate'}</p>
                </div>
              </div>
            </div>

            {/* Status & Controls */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => toggleLock(door.id)}
                disabled={door.isOpen}
                className={`flex-1 py-3 rounded-xl transition-all flex items-center justify-center gap-2 ${
                  door.isLocked
                    ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg shadow-green-500/30 hover:from-green-600 hover:to-emerald-600'
                    : 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg shadow-amber-500/30 hover:from-amber-600 hover:to-orange-600'
                } disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none`}
                title={door.isOpen ? 'Close first to lock' : ''}
              >
                {door.isLocked ? (
                  <>
                    <Unlock className="w-4 h-4" />
                    <span className="text-sm">Unlock</span>
                  </>
                ) : (
                  <>
                    <Lock className="w-4 h-4" />
                    <span className="text-sm">Lock</span>
                  </>
                )}
              </button>
              <button
                onClick={() => toggleDoor(door.id)}
                disabled={door.isLocked}
                className={`flex-1 py-3 rounded-xl transition-all text-sm ${
                  door.isLocked
                    ? 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
                    : door.isOpen
                    ? 'bg-white/10 text-white hover:bg-white/20 border border-white/20'
                    : 'bg-white/10 text-white hover:bg-white/20 border border-white/20'
                }`}
                title={door.isLocked ? 'Unlock first to open' : ''}
              >
                {door.isOpen ? 'Close' : 'Open'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
