import { useState, useEffect } from 'react';
import { Car, MapPin, Fuel, Gauge, Battery, Lock, Unlock, Navigation, Maximize2, Zap, AlertTriangle } from 'lucide-react';
import { carApi } from '../lib/api';

interface CarStatus {
  location: string;
  latitude: number;
  longitude: number;
  speed: number;
  fuel: number;
  battery: number;
  isLocked: boolean;
  engineRunning: boolean;
  odometer: number;
}

interface CarTrackerProps {
  compact?: boolean;
}

export function CarTracker({ compact = false }: CarTrackerProps) {
  const [carStatus, setCarStatus] = useState<CarStatus>({
    location: 'Rua das Flores, 123 - Centro',
    latitude: -23.550520,
    longitude: -46.633308,
    speed: 0,
    fuel: 75,
    battery: 95,
    isLocked: true,
    engineRunning: false,
    odometer: 45678,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCarStatus();
  }, []);

  const loadCarStatus = async () => {
    setLoading(true);
    setError(null);
    const response = await carApi.getStatus();
    
    if (response.success && response.data) {
      setCarStatus(response.data as CarStatus);
    } else {
      setError(response.error || 'Erro ao carregar status do carro');
    }
    setLoading(false);
  };

  const toggleLock = async () => {
    if (carStatus.engineRunning) return;

    const newLockState = !carStatus.isLocked;
    setCarStatus({ ...carStatus, isLocked: newLockState });

    const response = await carApi.toggleLock(newLockState);
    
    if (!response.success) {
      setCarStatus({ ...carStatus, isLocked: !newLockState });
      setError(response.error || 'Erro ao trancar/destrancar carro');
    }
  };

  const toggleEngine = async () => {
    if (carStatus.isLocked) return;

    const newEngineState = !carStatus.engineRunning;
    setCarStatus({
      ...carStatus,
      engineRunning: newEngineState,
      speed: newEngineState ? carStatus.speed : 0
    });

    const response = await carApi.toggleEngine(newEngineState);
    
    if (!response.success) {
      setCarStatus({
        ...carStatus,
        engineRunning: !newEngineState
      });
      setError(response.error || 'Erro ao ligar/desligar motor');
    }
  };

  useEffect(() => {
    const interval = setInterval(async () => {
      const response = await carApi.getLocation();
      
      if (response.success && response.data) {
        const locationData = response.data as Partial<CarStatus>;
        setCarStatus(prev => ({
          ...prev,
          ...locationData
        }));
      }
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const getFuelStatus = (fuel: number) => {
    if (fuel < 20) return { label: 'Low', color: 'text-red-400', bgColor: 'bg-red-500/20' };
    if (fuel < 50) return { label: 'Medium', color: 'text-amber-400', bgColor: 'bg-amber-500/20' };
    return { label: 'Full', color: 'text-green-400', bgColor: 'bg-green-500/20' };
  };

  const fuelStatus = getFuelStatus(carStatus.fuel);

  if (compact) {
    return (
      <div className="backdrop-blur-xl bg-gradient-to-br from-cyan-900/40 to-slate-900/60 rounded-3xl border border-cyan-500/20 p-6 shadow-2xl">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-white mb-1">My Car</h2>
            <p className="text-slate-400 text-sm">{carStatus.engineRunning ? 'Engine On' : 'Parked'}</p>
          </div>
          <div className={`p-2 rounded-xl ${
            carStatus.isLocked ? 'bg-green-500/20' : 'bg-amber-500/20'
          }`}>
            {carStatus.isLocked ? (
              <Lock className="w-4 h-4 text-green-400" />
            ) : (
              <Unlock className="w-4 h-4 text-amber-400" />
            )}
          </div>
        </div>

        {/* Location */}
        <div className="mb-6 p-4 bg-white/5 rounded-2xl border border-white/10">
          <div className="flex items-start gap-3">
            <MapPin className="w-5 h-5 text-cyan-400 mt-0.5" />
            <div className="flex-1 min-w-0">
              <p className="text-sm text-white mb-1">Current Location</p>
              <p className="text-xs text-slate-400 truncate">{carStatus.location}</p>
            </div>
          </div>
        </div>

        {/* Mini Stats */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white/5 rounded-2xl p-4 border border-white/10">
            <div className="flex items-center gap-2 mb-2">
              <Fuel className="w-4 h-4 text-orange-400" />
              <span className="text-xs text-slate-400">Fuel</span>
            </div>
            <div className="text-2xl text-white">{Math.round(carStatus.fuel)}%</div>
            <p className={`text-xs ${fuelStatus.color} mt-1`}>{fuelStatus.label}</p>
          </div>
          
          <div className="bg-white/5 rounded-2xl p-4 border border-white/10">
            <div className="flex items-center gap-2 mb-2">
              <Battery className="w-4 h-4 text-green-400" />
              <span className="text-xs text-slate-400">Battery</span>
            </div>
            <div className="text-2xl text-white">{carStatus.battery}%</div>
            <p className="text-xs text-green-400 mt-1">Good</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="backdrop-blur-xl bg-gradient-to-br from-cyan-900/40 to-slate-900/60 rounded-3xl border border-cyan-500/20 p-8 shadow-2xl">
      <div className="flex items-start justify-between mb-8">
        <div>
          <h2 className="text-2xl text-white mb-2">Vehicle Control</h2>
          <p className="text-slate-400">{carStatus.engineRunning ? 'Engine running' : 'Parked'} · {carStatus.odometer.toLocaleString()} km</p>
        </div>
        <div className="flex items-center gap-3">
          <div className={`px-4 py-2 rounded-xl border flex items-center gap-2 ${
            carStatus.isLocked
              ? 'bg-green-500/20 border-green-500/30'
              : 'bg-amber-500/20 border-amber-500/30'
          }`}>
            {carStatus.isLocked ? (
              <>
                <Lock className="w-4 h-4 text-green-400" />
                <span className="text-sm text-green-300">Locked</span>
              </>
            ) : (
              <>
                <Unlock className="w-4 h-4 text-amber-400" />
                <span className="text-sm text-amber-300">Unlocked</span>
              </>
            )}
          </div>
          {carStatus.engineRunning && (
            <div className="px-4 py-2 rounded-xl bg-red-500/20 border border-red-500/30 flex items-center gap-2">
              <Zap className="w-4 h-4 text-red-400" />
              <span className="text-sm text-red-300">Engine On</span>
            </div>
          )}
        </div>
      </div>

      {/* Location Card */}
      <div className="mb-8 p-6 bg-gradient-to-br from-cyan-500/10 to-blue-500/10 rounded-2xl border border-cyan-500/20">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-xl bg-cyan-500/20">
            <MapPin className="w-6 h-6 text-cyan-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-white mb-2">Current Location</h3>
            <p className="text-slate-300 mb-2">{carStatus.location}</p>
            <p className="text-sm text-slate-400">
              {carStatus.latitude.toFixed(6)}, {carStatus.longitude.toFixed(6)}
            </p>
          </div>
          <button className="p-3 rounded-xl bg-white/10 hover:bg-white/20 transition-all">
            <Navigation className="w-5 h-5 text-cyan-400" />
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className={`p-6 rounded-2xl border transition-all ${
          carStatus.speed > 0 
            ? 'bg-gradient-to-br from-blue-500/20 to-cyan-500/10 border-blue-500/30 shadow-lg shadow-blue-500/10'
            : 'bg-white/5 border-white/10'
        }`}>
          <div className="flex items-center gap-2 mb-3">
            <Gauge className="w-5 h-5 text-blue-400" />
            <span className="text-sm text-slate-300">Speed</span>
          </div>
          <div className="text-3xl text-white mb-1">{carStatus.speed}</div>
          <p className="text-xs text-slate-400">km/h</p>
        </div>

        <div className={`p-6 rounded-2xl border ${
          carStatus.fuel < 20
            ? 'bg-gradient-to-br from-red-500/20 to-orange-500/10 border-red-500/30 shadow-lg shadow-red-500/10'
            : 'bg-gradient-to-br from-orange-500/20 to-yellow-500/10 border-orange-500/30'
        }`}>
          <div className="flex items-center gap-2 mb-3">
            <Fuel className="w-5 h-5 text-orange-400" />
            <span className="text-sm text-slate-300">Fuel</span>
          </div>
          <div className="text-3xl text-white mb-1">{Math.round(carStatus.fuel)}%</div>
          <p className={`text-xs ${fuelStatus.color}`}>{fuelStatus.label}</p>
          {carStatus.fuel < 20 && (
            <div className="flex items-center gap-1 mt-2">
              <AlertTriangle className="w-3 h-3 text-red-400" />
              <span className="text-xs text-red-400">Refuel soon</span>
            </div>
          )}
        </div>

        <div className="p-6 rounded-2xl bg-gradient-to-br from-green-500/20 to-emerald-500/10 border border-green-500/30">
          <div className="flex items-center gap-2 mb-3">
            <Battery className="w-5 h-5 text-green-400" />
            <span className="text-sm text-slate-300">Battery</span>
          </div>
          <div className="text-3xl text-white mb-1">{carStatus.battery}%</div>
          <p className="text-xs text-green-400">Good</p>
        </div>

        <div className="p-6 rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-500/10 border border-purple-500/30">
          <div className="flex items-center gap-2 mb-3">
            <Car className="w-5 h-5 text-purple-400" />
            <span className="text-sm text-slate-300">Odometer</span>
          </div>
          <div className="text-2xl text-white mb-1">{carStatus.odometer.toLocaleString()}</div>
          <p className="text-xs text-slate-400">km total</p>
        </div>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={toggleLock}
          disabled={carStatus.engineRunning}
          className={`py-4 px-6 rounded-2xl transition-all flex items-center justify-center gap-3 ${
            carStatus.isLocked
              ? 'bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white shadow-lg shadow-amber-500/30'
              : 'bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white shadow-lg shadow-green-500/30'
          } disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none`}
        >
          {carStatus.isLocked ? (
            <>
              <Unlock className="w-5 h-5" />
              <span>Unlock Vehicle</span>
            </>
          ) : (
            <>
              <Lock className="w-5 h-5" />
              <span>Lock Vehicle</span>
            </>
          )}
        </button>

        <button
          onClick={toggleEngine}
          disabled={carStatus.isLocked}
          className={`py-4 px-6 rounded-2xl transition-all flex items-center justify-center gap-3 ${
            carStatus.engineRunning
              ? 'bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600 text-white shadow-lg shadow-red-500/30'
              : 'bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white shadow-lg shadow-cyan-500/30'
          } disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none`}
        >
          <Car className="w-5 h-5" />
          <span>{carStatus.engineRunning ? 'Stop Engine' : 'Start Engine'}</span>
        </button>
      </div>

      {/* Info Banner */}
      {carStatus.isLocked && (
        <div className="mt-4 p-3 bg-slate-800/50 rounded-xl border border-slate-700/50">
          <p className="text-xs text-slate-400 text-center">
            Vehicle is locked. Unlock to start the engine.
          </p>
        </div>
      )}
      {!carStatus.isLocked && !carStatus.engineRunning && (
        <div className="mt-4 p-3 bg-amber-500/10 rounded-xl border border-amber-500/20">
          <p className="text-xs text-amber-400 text-center flex items-center justify-center gap-2">
            <AlertTriangle className="w-3 h-3" />
            Vehicle is unlocked. Lock it for security.
          </p>
        </div>
      )}
    </div>
  );
}
