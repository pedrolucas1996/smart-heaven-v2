import { useState, useEffect } from 'react';
import { Lightbulb, Power, Sun, Maximize2, Zap } from 'lucide-react';
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
    { id: '1', name: 'Main Light', room: 'Living room', isOn: true, brightness: 100 },
    { id: '2', name: 'Ambient', room: 'Living room', isOn: true, brightness: 60 },
    { id: '3', name: 'Corner Lamp', room: 'Living room', isOn: false, brightness: 0 },
    { id: '4', name: 'Ceiling Light', room: 'Kitchen', isOn: false, brightness: 0 },
    { id: '5', name: 'Counter Light', room: 'Kitchen', isOn: true, brightness: 85 },
  ]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      setError(response.error || 'Error loading lights');
    }
    setLoading(false);
  };

  const toggleLight = async (id: string) => {
    const light = lights.find(l => l.id === id);
    if (!light) return;

    setLights(lights.map(l =>
      l.id === id ? { ...l, isOn: !l.isOn } : l
    ));

    const response = await lightsApi.toggle(id, !light.isOn);

    if (!response.success) {
      setLights(lights.map(l =>
        l.id === id ? { ...l, isOn: light.isOn } : l
      ));
      setError(response.error || 'Error toggling light');
    }
  };

  const setBrightness = async (id: string, brightness: number) => {
    const light = lights.find(l => l.id === id);
    if (!light) return;

    setLights(lights.map(l =>
      l.id === id ? { ...l, brightness } : l
    ));

    const response = await lightsApi.setBrightness(id, brightness);

    if (!response.success) {
      setLights(lights.map(l =>
        l.id === id ? { ...l, brightness: light.brightness } : l
      ));
    }
  };

  const onLights = lights.filter(l => l.isOn).length;
  const totalBrightness = Math.round(
    lights.filter(l => l.isOn).reduce((acc, l) => acc + l.brightness, 0) / 
    (onLights || 1)
  );

  if (compact) {
    return (
      <div className="backdrop-blur-xl bg-gradient-to-br from-amber-900/40 to-slate-900/60 rounded-3xl border border-amber-500/20 p-6 shadow-2xl">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-white mb-1">Lighting</h2>
            <p className="text-slate-400 text-sm">{onLights} of {lights.length} active</p>
          </div>
          <button className="p-2 rounded-xl bg-white/5 hover:bg-white/10 transition-all">
            <Maximize2 className="w-4 h-4 text-slate-400" />
          </button>
        </div>

        {/* Brightness Gauge */}
        <div className="mb-6">
          <div className="flex items-baseline gap-2 mb-3">
            <span className="text-5xl text-white">{totalBrightness}%</span>
            <span className="text-slate-400">Average</span>
          </div>
          
          {/* Progress bar with gradient */}
          <div className="relative h-3 bg-slate-800 rounded-full overflow-hidden">
            <div 
              className="absolute h-full bg-gradient-to-r from-amber-500 via-yellow-400 to-lime-400 transition-all duration-500 rounded-full"
              style={{ width: `${totalBrightness}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>0</span>
            <span>100%</span>
          </div>
        </div>

        {/* Quick Lights */}
        <div className="space-y-2">
          {lights.slice(0, 3).map((light) => (
            <div
              key={light.id}
              className={`p-4 rounded-2xl border transition-all ${
                light.isOn
                  ? 'bg-amber-500/20 border-amber-500/30'
                  : 'bg-white/5 border-white/10'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {light.isOn ? (
                    <Lightbulb className="w-5 h-5 text-amber-400 fill-amber-400" />
                  ) : (
                    <Lightbulb className="w-5 h-5 text-slate-500" />
                  )}
                  <div>
                    <p className="text-white text-sm">{light.name}</p>
                    <p className="text-xs text-slate-400">{light.room}</p>
                  </div>
                </div>
                <button
                  onClick={() => toggleLight(light.id)}
                  className={`w-10 h-10 rounded-xl transition-all ${
                    light.isOn
                      ? 'bg-amber-500 text-white shadow-lg shadow-amber-500/30'
                      : 'bg-slate-700 text-slate-400'
                  }`}
                >
                  <Power className="w-4 h-4 mx-auto" />
                </button>
              </div>
            </div>
          ))}
        </div>

        {lights.length > 3 && (
          <div className="mt-4 text-center">
            <p className="text-sm text-slate-400">+{lights.length - 3} more lights</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="backdrop-blur-xl bg-gradient-to-br from-amber-900/40 to-slate-900/60 rounded-3xl border border-amber-500/20 p-8 shadow-2xl">
      <div className="flex items-start justify-between mb-8">
        <div>
          <h2 className="text-2xl text-white mb-2">Lighting Control</h2>
          <p className="text-slate-400">{onLights} lights on · {totalBrightness}% average brightness</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-4 py-2 rounded-xl bg-amber-500/20 border border-amber-500/30">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              <span className="text-sm text-amber-300">Energy Saving</span>
            </div>
          </div>
        </div>
      </div>

      {/* Grid de luzes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {lights.map((light) => (
          <div
            key={light.id}
            className={`p-6 rounded-2xl border transition-all ${
              light.isOn
                ? 'bg-gradient-to-br from-amber-500/20 to-yellow-500/10 border-amber-500/30 shadow-lg shadow-amber-500/10'
                : 'bg-white/5 border-white/10'
            }`}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                {light.isOn ? (
                  <div className="p-3 rounded-xl bg-amber-500/30">
                    <Lightbulb className="w-6 h-6 text-amber-400 fill-amber-400" />
                  </div>
                ) : (
                  <div className="p-3 rounded-xl bg-slate-700/50">
                    <Lightbulb className="w-6 h-6 text-slate-500" />
                  </div>
                )}
                <div>
                  <p className="text-white">{light.name}</p>
                  <p className="text-sm text-slate-400">{light.room}</p>
                </div>
              </div>
              
              <button
                onClick={() => toggleLight(light.id)}
                className={`w-12 h-12 rounded-xl transition-all ${
                  light.isOn
                    ? 'bg-gradient-to-br from-amber-500 to-yellow-500 text-white shadow-lg shadow-amber-500/40'
                    : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                }`}
              >
                <Power className="w-5 h-5 mx-auto" />
              </button>
            </div>

            {/* Brightness Slider */}
            {light.isOn && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Sun className="w-4 h-4 text-amber-400" />
                    <span className="text-sm text-slate-300">Brightness</span>
                  </div>
                  <span className="text-sm text-white">{light.brightness}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={light.brightness}
                  onChange={(e) => setBrightness(light.id, parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-700 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-amber-400 [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:shadow-lg [&::-webkit-slider-thumb]:shadow-amber-500/50"
                  style={{
                    background: `linear-gradient(to right, rgb(251, 191, 36) 0%, rgb(251, 191, 36) ${light.brightness}%, rgb(51, 65, 85) ${light.brightness}%, rgb(51, 65, 85) 100%)`
                  }}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
