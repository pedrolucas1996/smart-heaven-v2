import { useState, useEffect } from 'react';
import { ToggleLeft, ToggleRight, Power, Wrench, Maximize2, Clock, Zap, Loader2 } from 'lucide-react';
import { switchesApi } from '../lib/api';

interface Switch {
  id: number;
  nome: string;
  base: string;
  estado: boolean;
  ativo: boolean;
  data_de_atualizacao: string;
}

interface SwitchControlProps {
  compact?: boolean;
}

export function SwitchControlSH2({ compact = false }: SwitchControlProps) {
  const [switches, setSwitches] = useState<Switch[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const formatLastPressed = (timestamp?: string): string => {
    if (!timestamp) return 'Nunca usado';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Agora';
    if (diffMins < 60) return `Há ${diffMins}m`;
    if (diffHours < 24) return `Há ${diffHours}h`;
    if (diffDays === 1) return 'Ontem';
    if (diffDays < 7) return `Há ${diffDays} dias`;

    return date.toLocaleDateString('pt-BR', {
      month: 'short',
      day: 'numeric'
    });
  };

  useEffect(() => {
    loadSwitches();
    const interval = setInterval(loadSwitches, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const loadSwitches = async () => {
    if (loading) return;
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

  const toggleMaintenance = async (nome: string) => {
    const switchItem = switches.find(s => s.nome === nome);
    if (!switchItem) return;

    // Optimistic update
    setSwitches(switches.map(s =>
      s.nome === nome ? { ...s, ativo: !s.ativo } : s
    ));

    const response = await switchesApi.toggleMaintenance(nome, !switchItem.ativo);
    
    if (!response.success) {
      // Revert on error
      setSwitches(switches.map(s =>
        s.nome === nome ? { ...s, ativo: switchItem.ativo } : s
      ));
      setError(response.error || 'Erro ao alterar modo manutenção');
    }
  };

  const activeSwitches = switches.filter(s => s.ativo).length;
  const inMaintenance = switches.filter(s => !s.ativo).length;

  if (compact) {
    return (
      <div className="backdrop-blur-xl bg-gradient-to-br from-blue-900/40 to-slate-900/60 rounded-3xl border border-blue-500/20 p-6 shadow-2xl">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-white mb-1">🔘 Interruptores</h2>
            <p className="text-slate-400 text-sm">{activeSwitches} ativos · {inMaintenance} em manutenção</p>
          </div>
          <button className="p-2 rounded-xl bg-white/5 hover:bg-white/10 transition-all">
            {loading && <Loader2 className="w-4 h-4 text-slate-400 animate-spin" />}
            {!loading && <Maximize2 className="w-4 h-4 text-slate-400" />}
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-red-500/20 border border-red-500/30 text-red-300 text-sm">
            {error}
          </div>
        )}

        {/* Quick Switches */}
        <div className="space-y-3">
          {switches.slice(0, 3).map((sw) => (
            <div
              key={sw.id}
              className={`p-4 rounded-2xl border transition-all ${
                !sw.ativo
                  ? 'bg-amber-500/10 border-amber-500/30'
                  : sw.estado
                  ? 'bg-blue-500/20 border-blue-500/30'
                  : 'bg-white/5 border-white/10'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  {sw.estado && sw.ativo ? (
                    <ToggleRight className="w-5 h-5 text-blue-400" />
                  ) : (
                    <ToggleLeft className="w-5 h-5 text-slate-500" />
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm truncate">{sw.nome}</p>
                    <p className="text-xs text-slate-400">{sw.base}</p>
                  </div>
                </div>
                
                <button
                  onClick={() => toggleMaintenance(sw.nome)}
                  className={`w-10 h-10 rounded-xl transition-all flex-shrink-0 ${
                    !sw.ativo
                      ? 'bg-amber-500 text-white'
                      : sw.estado
                      ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/30'
                      : 'bg-slate-700 text-slate-400'
                  }`}
                >
                  {!sw.ativo ? (
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
            <p className="text-sm text-slate-400">+{switches.length - 3} mais interruptores</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="backdrop-blur-xl bg-gradient-to-br from-blue-900/40 to-slate-900/60 rounded-3xl border border-blue-500/20 p-8 shadow-2xl">
      <div className="flex items-start justify-between mb-8">
        <div>
          <h2 className="text-2xl text-white mb-2">🔘 Interruptores Inteligentes</h2>
          <p className="text-slate-400">{activeSwitches} ativos{inMaintenance > 0 && ` · ${inMaintenance} em manutenção`}</p>
        </div>
        {inMaintenance > 0 && (
          <div className="px-4 py-2 rounded-xl bg-amber-500/20 border border-amber-500/30">
            <div className="flex items-center gap-2">
              <Wrench className="w-4 h-4 text-amber-400" />
              <span className="text-sm text-amber-300">Modo Manutenção</span>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-500/20 border border-red-500/30 text-red-300">
          {error}
        </div>
      )}

      {/* Grid de interruptores */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {switches.map((sw) => (
          <div
            key={sw.id}
            className={`p-6 rounded-2xl border transition-all ${
              !sw.ativo
                ? 'bg-gradient-to-br from-amber-500/20 to-orange-500/10 border-amber-500/30'
                : sw.estado
                ? 'bg-gradient-to-br from-blue-500/20 to-indigo-500/10 border-blue-500/30 shadow-lg shadow-blue-500/10'
                : 'bg-white/5 border-white/10'
            }`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3 flex-1">
                {sw.estado && sw.ativo ? (
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
                    <p className="text-white">{sw.nome}</p>
                    {!sw.ativo && (
                      <span className="px-2 py-0.5 bg-amber-500/30 text-amber-300 text-xs rounded-full">
                        Manutenção
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-slate-400">{sw.base}</p>
                </div>
              </div>
            </div>

            {/* Last Updated */}
            <div className="flex items-center gap-2 mb-4 text-xs text-slate-400">
              <Clock className="w-3 h-3" />
              <span>Atualizado: {formatLastPressed(sw.data_de_atualizacao)}</span>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => toggleMaintenance(sw.nome)}
                className={`flex-1 px-4 py-2.5 rounded-xl text-sm transition-all ${
                  sw.ativo
                    ? 'bg-slate-700/50 text-slate-300 hover:bg-slate-700 border border-slate-600'
                    : 'bg-amber-500/30 text-amber-300 hover:bg-amber-500/40 border border-amber-500/40'
                }`}
              >
                {sw.ativo ? 'Manutenção' : 'Reativar'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
