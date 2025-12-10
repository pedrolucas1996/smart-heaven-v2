import { useState, useEffect } from 'react';
import { Lightbulb, Sun, Maximize2, Zap, Loader2 } from 'lucide-react';
import { lightsApi } from '../lib/api';

interface Light {
  id: number;
  nome: string;
  apelido?: string | null;
  base_id: number;
  estado: boolean;
  invertido: boolean;
  data_de_atualizacao: string;
}

interface LightControlProps {
  compact?: boolean;
}

export function LightControlSH2({ compact = false }: LightControlProps) {
  const [lights, setLights] = useState<Light[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadLights();
    const interval = setInterval(loadLights, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const loadLights = async () => {
    if (loading) return;
    setLoading(true);
    setError(null);
    const response = await lightsApi.getAll();

    if (response.success && response.data) {
      setLights(response.data as Light[]);
    } else {
      setError(response.error || 'Erro ao carregar luzes');
    }
    setLoading(false);
  };

  const toggleLight = async (nome: string) => {
    const light = lights.find(l => l.nome === nome);
    if (!light) return;

    // Optimistic update
    setLights(lights.map(l =>
      l.nome === nome ? { ...l, estado: !l.estado } : l
    ));

    const response = await lightsApi.toggle(nome);

    if (!response.success) {
      // Revert on error
      setLights(lights.map(l =>
        l.nome === nome ? { ...l, estado: light.estado } : l
      ));
      setError(response.error || 'Erro ao alternar luz');
    }
  };

  // Get display state (handles hardware inversion)
  const getDisplayState = (light: Light) => {
    return light.invertido ? !light.estado : light.estado;
  };

  const onLights = lights.filter(l => getDisplayState(l)).length;

  if (compact) {
    return (
      <div className="backdrop-blur-xl bg-gradient-to-br from-amber-900/40 to-slate-900/60 rounded-3xl border border-amber-500/20 p-6 shadow-2xl">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-white mb-1">💡 Iluminação</h2>
            <p className="text-slate-400 text-sm">{onLights} de {lights.length} ligadas</p>
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

        {/* Quick Lights */}
        <div className="grid grid-cols-2 gap-3">
          {lights.slice(0, 4).map((light) => {
            const isOn = getDisplayState(light);
            return (
              <button
                key={light.id}
                onClick={() => toggleLight(light.nome)}
                className={`p-4 rounded-2xl transition-all ${
                  isOn
                    ? 'bg-gradient-to-br from-amber-500 to-yellow-500 text-slate-900 shadow-lg shadow-amber-500/30'
                    : 'bg-white/5 text-slate-400 hover:bg-white/10'
                }`}
              >
                <div className="flex flex-col items-center gap-2">
                  <Lightbulb className="w-6 h-6" />
                  <span className="text-xs font-medium truncate w-full text-center">{light.apelido || light.nome}</span>
                </div>
              </button>
            );
          })}
        </div>

        {lights.length > 4 && (
          <div className="mt-4 text-center">
            <p className="text-sm text-slate-400">+{lights.length - 4} mais luzes</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="backdrop-blur-xl bg-gradient-to-br from-amber-900/40 to-slate-900/60 rounded-3xl border border-amber-500/20 p-4 md:p-8 shadow-2xl">
      <div className="flex flex-col sm:flex-row items-start justify-between mb-6 gap-3">
        <div>
          <h2 className="text-xl md:text-2xl text-white mb-2">💡 Controle de Iluminação</h2>
          <p className="text-slate-400 text-sm">{onLights} de {lights.length} luzes ligadas</p>
        </div>
        {loading && <Loader2 className="w-5 h-5 md:w-6 md:h-6 text-amber-400 animate-spin" />}
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-500/20 border border-red-500/30 text-red-300 text-sm">
          {error}
        </div>
      )}

      {/* Grid de luzes - responsivo */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2 sm:gap-3 md:gap-4">
        {lights.map((light) => {
          const isOn = getDisplayState(light);
          return (
            <button
              key={light.id}
              onClick={() => toggleLight(light.nome)}
              disabled={loading}
              className={`p-2 sm:p-3 md:p-5 rounded-lg sm:rounded-xl transition-all touch-manipulation hover:scale-105 active:scale-95 ${
                isOn
                  ? 'bg-gradient-to-br from-amber-500 to-yellow-400 shadow-lg shadow-amber-500/40 hover:from-amber-400 hover:to-yellow-300'
                  : 'bg-white/5 border border-white/10 hover:bg-white/10'
              } ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="flex flex-col items-center gap-1 sm:gap-2 md:gap-3">
                <div className={`p-1.5 sm:p-2 md:p-3 rounded-full ${
                  isOn ? 'bg-white/20' : 'bg-white/5'
                }`}>
                  <Lightbulb className={`w-4 h-4 sm:w-5 sm:h-5 md:w-7 md:h-7 ${
                    isOn ? 'text-slate-900' : 'text-slate-500'
                  }`} />
                </div>

                <div className="w-full min-h-[2rem] sm:min-h-[2.5rem] flex items-center justify-center gap-1 px-1">
                  <p className={`font-medium text-[10px] sm:text-xs md:text-sm truncate leading-tight ${
                    isOn ? 'text-slate-900' : 'text-white'
                  }`} title={light.apelido || light.nome}>
                    {light.apelido || light.nome}
                  </p>
                  <span className={`text-[8px] sm:text-[9px] md:text-[10px] font-normal whitespace-nowrap ${
                    isOn ? 'text-slate-700' : 'text-slate-400'
                  }`}>
                    {isOn ? 'on' : 'off'}
                  </span>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
