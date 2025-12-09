import { useState, useEffect } from 'react';
import { Car, MapPin, Fuel, Gauge, Battery, Lock, Unlock, Navigation } from 'lucide-react';
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

  // GET: Carregar dados do carro ao montar o componente
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

  // POST: Trancar/destrancar carro
  const toggleLock = async () => {
    if (carStatus.engineRunning) return;

    const newLockState = !carStatus.isLocked;

    // Atualiza UI otimisticamente
    setCarStatus({ ...carStatus, isLocked: newLockState });

    // Envia para API
    const response = await carApi.toggleLock(newLockState);
    
    if (!response.success) {
      // Reverte em caso de erro
      setCarStatus({ ...carStatus, isLocked: !newLockState });
      setError(response.error || 'Erro ao trancar/destrancar carro');
    }
  };

  // POST: Ligar/desligar motor
  const toggleEngine = async () => {
    if (carStatus.isLocked) return;

    const newEngineState = !carStatus.engineRunning;

    // Atualiza UI otimisticamente
    setCarStatus({
      ...carStatus,
      engineRunning: newEngineState,
      speed: newEngineState ? carStatus.speed : 0
    });

    // Envia para API
    const response = await carApi.toggleEngine(newEngineState);
    
    if (!response.success) {
      // Reverte em caso de erro
      setCarStatus({
        ...carStatus,
        engineRunning: !newEngineState
      });
      setError(response.error || 'Erro ao ligar/desligar motor');
    }
  };

  // Atualiza localização periodicamente
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
    }, 10000); // A cada 10 segundos

    return () => clearInterval(interval);
  }, []);

  const getFuelStatus = (fuel: number) => {
    if (fuel < 20) return { label: 'Baixo', color: 'text-red-600' };
    if (fuel < 50) return { label: 'Médio', color: 'text-amber-600' };
    return { label: 'Cheio', color: 'text-green-600' };
  };

  const fuelStatus = getFuelStatus(carStatus.fuel);

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-emerald-100 p-3 rounded-lg">
            <Car className="w-6 h-6 text-emerald-600" />
          </div>
          <div>
            <h2>Meu Carro</h2>
            <p className="text-slate-500 text-sm">
              {carStatus.engineRunning ? 'Motor ligado' : 'Estacionado'}
            </p>
          </div>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${
          carStatus.isLocked
            ? 'bg-green-100 text-green-700'
            : 'bg-amber-100 text-amber-700'
        }`}>
          {carStatus.isLocked ? (
            <Lock className="w-4 h-4" />
          ) : (
            <Unlock className="w-4 h-4" />
          )}
          <span className="text-sm">
            {carStatus.isLocked ? 'Trancado' : 'Destrancado'}
          </span>
        </div>
      </div>

      {/* Location */}
      <div className="mb-6 p-4 bg-slate-50 rounded-lg">
        <div className="flex items-start gap-3">
          <MapPin className="w-5 h-5 text-emerald-600 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-sm mb-1">Localização Atual</h3>
            <p className="text-slate-600 text-sm mb-2">{carStatus.location}</p>
            <p className="text-xs text-slate-500">
              {carStatus.latitude.toFixed(6)}, {carStatus.longitude.toFixed(6)}
            </p>
          </div>
          <button className="p-2 hover:bg-slate-200 rounded-lg transition-colors">
            <Navigation className="w-5 h-5 text-slate-600" />
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="p-3 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg border border-blue-200">
          <div className="flex items-center gap-2 mb-2">
            <Gauge className="w-4 h-4 text-blue-600" />
            <span className="text-xs text-slate-600">Velocidade</span>
          </div>
          <p className="text-xl">{carStatus.speed}</p>
          <p className="text-xs text-slate-500">km/h</p>
        </div>

        <div className="p-3 bg-gradient-to-br from-orange-50 to-red-50 rounded-lg border border-orange-200">
          <div className="flex items-center gap-2 mb-2">
            <Fuel className="w-4 h-4 text-orange-600" />
            <span className="text-xs text-slate-600">Combustível</span>
          </div>
          <p className="text-xl">{Math.round(carStatus.fuel)}%</p>
          <p className={`text-xs ${fuelStatus.color}`}>{fuelStatus.label}</p>
        </div>

        <div className="p-3 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border border-green-200">
          <div className="flex items-center gap-2 mb-2">
            <Battery className="w-4 h-4 text-green-600" />
            <span className="text-xs text-slate-600">Bateria</span>
          </div>
          <p className="text-xl">{carStatus.battery}%</p>
          <p className="text-xs text-slate-500">Boa</p>
        </div>

        <div className="p-3 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg border border-purple-200">
          <div className="flex items-center gap-2 mb-2">
            <Car className="w-4 h-4 text-purple-600" />
            <span className="text-xs text-slate-600">Odômetro</span>
          </div>
          <p className="text-xl">{carStatus.odometer.toLocaleString()}</p>
          <p className="text-xs text-slate-500">km</p>
        </div>
      </div>

      {/* Controls */}
      {!compact && (
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={toggleLock}
            disabled={carStatus.engineRunning}
            className={`py-3 px-4 rounded-lg transition-all flex items-center justify-center gap-2 ${
              carStatus.isLocked
                ? 'bg-amber-500 hover:bg-amber-600 text-white'
                : 'bg-green-500 hover:bg-green-600 text-white'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {carStatus.isLocked ? (
              <>
                <Unlock className="w-5 h-5" />
                <span>Destrancar</span>
              </>
            ) : (
              <>
                <Lock className="w-5 h-5" />
                <span>Trancar</span>
              </>
            )}
          </button>

          <button
            onClick={toggleEngine}
            disabled={carStatus.isLocked}
            className={`py-3 px-4 rounded-lg transition-all flex items-center justify-center gap-2 ${
              carStatus.engineRunning
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-emerald-500 hover:bg-emerald-600 text-white'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            <Car className="w-5 h-5" />
            <span>{carStatus.engineRunning ? 'Desligar Motor' : 'Ligar Motor'}</span>
          </button>
        </div>
      )}
    </div>
  );
}