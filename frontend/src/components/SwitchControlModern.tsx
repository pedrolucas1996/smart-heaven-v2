import { useState, useEffect } from 'react';
import { ToggleLeft, ToggleRight, Power, Wrench, Maximize2, Clock, Zap } from 'lucide-react';
import { switchesApi } from '../lib/api';

interface Switch {
  id: string;
  name: string;
  room: string;
  isActive: boolean;
  isOn: boolean;
  linkedLights: string[];
  lastPressed?: string;
}

interface SwitchControlProps {
  compact?: boolean;
}

export function SwitchControl({ compact = false }: SwitchControlProps) {
  const [switches, setSwitches] = useState<Switch[]>([
    { id: 's1', name: 'Main Switch', room: 'Living room', isActive: true, isOn: true, linkedLights: ['1'], lastPressed: '2025-12-08T10:30:00Z' },
    { id: 's2', name: 'Door Switch', room: 'Living room', isActive: true, isOn: true, linkedLights: ['1', '2'], lastPressed: '2025-12-08T09:15:00Z' },
    { id: 's3', name: 'Three-Way 1', room: 'Living room', isActive: true, isOn: false, linkedLights: ['3'], lastPressed: '2025-12-08T08:45:00Z' },
    { id: 's5', name: 'Counter Switch', room: 'Kitchen', isActive: true, isOn: true, linkedLights: ['5'], lastPressed: '2025-12-08T07:00:00Z' },
    { id: 's6', name: 'Main Kitchen', room: 'Kitchen', isActive: true, isOn: false, linkedLights: ['4', '5', '6'], lastPressed: '2025-12-07T23:00:00Z' },
    { id: 's9', name: 'Suite Door', room: 'Suite', isActive: true, isOn: true, linkedLights: ['7'], lastPressed: '2025-12-08T09:00:00Z' },
    { id: 's10', name: 'Main Switch', room: 'Bathroom', isActive: false, isOn: false, linkedLights: ['11', '12'], lastPressed: '2025-12-06T18:00:00Z' },
  ]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const formatLastPressed = (timestamp?: string): string => {
    if (!timestamp) return 'Never used';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

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
      setError(response.error || 'Error loading switches');
    }
    setLoading(false);
  };

  const toggleSwitch = async (id: string) => {
    const switchItem = switches.find(s => s.id === id);
    if (!switchItem || !switchItem.isActive) return;

    setSwitches(switches.map(s =>
      s.id === id ? { ...s, isOn: !s.isOn } : s
    ));

    const response = await switchesApi.toggle(id, !switchItem.isOn);
    
    if (!response.success) {
      setSwitches(switches.map(s =>
        s.id === id ? { ...s, isOn: switchItem.isOn } : s
      ));
      setError(response.error || 'Error toggling switch');
    }
  };

  const toggleMaintenance = async (id: string) => {
    const switchItem = switches.find(s => s.id === id);
    if (!switchItem) return;

    setSwitches(switches.map(s =>
      s.id === id ? { ...s, isActive: !s.isActive } : s
    ));

    const response = await switchesApi.toggleMaintenance(id, !switchItem.isActive);
    
    if (!response.success) {
      setSwitches(switches.map(s =>
        s.id === id ? { ...s, isActive: switchItem.isActive } : s
      ));
      setError(response.error || 'Error changing maintenance mode');
    }
  };

  const activeSwitches = switches.filter(s => s.isActive).length;
  const onSwitches = switches.filter(s => s.isOn && s.isActive).length;
  const inMaintenance = switches.filter(s => !s.isActive).length;

  if (compact) {
    return (
      <div className="backdrop-blur-xl bg-gradient-to-br from-blue-900/40 to-slate-900/60 rounded-3xl border border-blue-500/20 p-6 shadow-2xl">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-white mb-1">Switches</h2>
            <p className="text-slate-400 text-sm">{onSwitches} active · {activeSwitches} online</p>
          </div>
          <button className="p-2 rounded-xl bg-white/5 hover:bg-white/10 transition-all">
            <Maximize2 className="w-4 h-4 text-slate-400" />
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 mb-6">
          <div className="bg-white/5 rounded-xl p-3 border border-white/10">
            <p className="text-xs text-slate-400 mb-1">Active</p>
            <p className="text-2xl text-white">{onSwitches}</p>
          </div>
          <div className="bg-white/5 rounded-xl p-3 border border-white/10">
            <p className="text-xs text-slate-400 mb-1">Online</p>
            <p className="text-2xl text-green-400">{activeSwitches}</p>
          </div>
          {inMaintenance > 0 && (
            <div className="bg-amber-500/10 rounded-xl p-3 border border-amber-500/30">
              <p className="text-xs text-amber-300 mb-1">Maintenance</p>
              <p className="text-2xl text-amber-400">{inMaintenance}</p>
            </div>
          )}
        </div>

        {/* Quick Switches */}
        <div className="space-y-3">
          {switches.slice(0, 3).map((sw) => (
            <div
              key={sw.id}
              className={`p-4 rounded-2xl border transition-all ${
                !sw.isActive
                  ? 'bg-amber-500/10 border-amber-500/30'
                  : sw.isOn
                  ? 'bg-blue-500/20 border-blue-500/30'
                  : 'bg-white/5 border-white/10'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  {sw.isOn && sw.isActive ? (
                    <ToggleRight className="w-5 h-5 text-blue-400" />
                  ) : (
                    <ToggleLeft className="w-5 h-5 text-slate-500" />
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm truncate">{sw.name}</p>
                    <p className="text-xs text-slate-400">{sw.room}</p>
                  </div>
                </div>
                
                <button
                  onClick={() => sw.isActive ? toggleSwitch(sw.id) : toggleMaintenance(sw.id)}
                  disabled={!sw.isActive}
                  className={`w-10 h-10 rounded-xl transition-all flex-shrink-0 ${
                    !sw.isActive
                      ? 'bg-amber-500 text-white'
                      : sw.isOn
                      ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/30'
                      : 'bg-slate-700 text-slate-400'
                  }`}
                >
                  {!sw.isActive ? (
                    <Wrench className="w-4 h-4 mx-auto" />
                  ) : (
                    <Power className="w-4 h-4 mx-auto" />
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>

        {switches.length > 3 && (
          <div className="mt-4 text-center">
            <p className="text-sm text-slate-400">+{switches.length - 3} more switches</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="backdrop-blur-xl bg-gradient-to-br from-blue-900/40 to-slate-900/60 rounded-3xl border border-blue-500/20 p-8 shadow-2xl">
      <div className="flex items-start justify-between mb-8">
        <div>
          <h2 className="text-2xl text-white mb-2">Smart Switches</h2>
          <p className="text-slate-400">{onSwitches} active · {activeSwitches} online{inMaintenance > 0 && ` · ${inMaintenance} in maintenance`}</p>
        </div>
        {inMaintenance > 0 && (
          <div className="px-4 py-2 rounded-xl bg-amber-500/20 border border-amber-500/30">
            <div className="flex items-center gap-2">
              <Wrench className="w-4 h-4 text-amber-400" />
              <span className="text-sm text-amber-300">Maintenance Mode</span>
            </div>
          </div>
        )}
      </div>

      {/* Grid de interruptores */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {switches.map((sw) => (
          <div
            key={sw.id}
            className={`p-6 rounded-2xl border transition-all ${
              !sw.isActive
                ? 'bg-gradient-to-br from-amber-500/20 to-orange-500/10 border-amber-500/30'
                : sw.isOn
                ? 'bg-gradient-to-br from-blue-500/20 to-indigo-500/10 border-blue-500/30 shadow-lg shadow-blue-500/10'
                : 'bg-white/5 border-white/10'
            }`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3 flex-1">
                {sw.isOn && sw.isActive ? (
                  <div className="p-3 rounded-xl bg-blue-500/30">
                    <ToggleRight className="w-6 h-6 text-blue-400" />
                  </div>
                ) : (
                  <div className="p-3 rounded-xl bg-slate-700/50">
                    <ToggleLeft className="w-6 h-6 text-slate-500" />
                  </div>
                )}
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="text-white">{sw.name}</p>
                    {!sw.isActive && (
                      <span className="px-2 py-0.5 bg-amber-500/30 text-amber-300 text-xs rounded-full">
                        Maintenance
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-slate-400">{sw.room} · {sw.linkedLights.length} light{sw.linkedLights.length !== 1 ? 's' : ''}</p>
                </div>
              </div>
            </div>

            {/* Last Pressed */}
            <div className="flex items-center gap-2 mb-4 text-xs text-slate-400">
              <Clock className="w-3 h-3" />
              <span>Last used: {formatLastPressed(sw.lastPressed)}</span>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => toggleMaintenance(sw.id)}
                className={`flex-1 px-4 py-2.5 rounded-xl text-sm transition-all ${
                  sw.isActive
                    ? 'bg-slate-700/50 text-slate-300 hover:bg-slate-700 border border-slate-600'
                    : 'bg-amber-500/30 text-amber-300 hover:bg-amber-500/40 border border-amber-500/40'
                }`}
              >
                {sw.isActive ? 'Maintenance' : 'Reactivate'}
              </button>
              
              <button
                onClick={() => toggleSwitch(sw.id)}
                disabled={!sw.isActive}
                className={`flex-1 px-4 py-2.5 rounded-xl text-sm transition-all ${
                  !sw.isActive
                    ? 'bg-slate-700/30 text-slate-500 cursor-not-allowed'
                    : sw.isOn
                    ? 'bg-gradient-to-br from-blue-500 to-indigo-500 text-white shadow-lg shadow-blue-500/40'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                {sw.isOn ? 'Turn Off' : 'Turn On'}
              </button>
            </div>

            {/* Linked Lights Info */}
            {sw.linkedLights.length > 0 && (
              <div className="mt-4 pt-4 border-t border-white/10">
                <div className="flex items-center gap-2">
                  <Zap className="w-3 h-3 text-indigo-400" />
                  <span className="text-xs text-slate-400">
                    Controls: Lights {sw.linkedLights.join(', ')}
                  </span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
