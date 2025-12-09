import { useState, useEffect } from 'react';
import { Thermometer, Droplets, Wind, Maximize2 } from 'lucide-react';
import { climateApi } from '../lib/api';

interface RoomSensor {
  room: string;
  temperature: number;
  humidity: number;
}

interface ClimateMonitorProps {
  compact?: boolean;
}

export function ClimateMonitor({ compact = false }: ClimateMonitorProps) {
  const [roomSensors, setRoomSensors] = useState<RoomSensor[]>([
    { room: 'Living room', temperature: 23, humidity: 55 },
    { room: 'Kitchen', temperature: 25, humidity: 60 },
    { room: 'Suite', temperature: 22, humidity: 52 },
    { room: 'Bathroom', temperature: 24, humidity: 65 },
  ]);

  const [selectedRoom, setSelectedRoom] = useState<RoomSensor>(roomSensors[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // GET: Carregar dados dos sensores ao montar o componente
  useEffect(() => {
    loadSensors();
    // Polling a cada 30 segundos
    const interval = setInterval(loadSensors, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadSensors = async () => {
    setLoading(true);
    setError(null);
    const response = await climateApi.getAll();

    if (response.success && response.data) {
      setRoomSensors(response.data as RoomSensor[]);
    } else {
      setError(response.error || 'Erro ao carregar sensores');
    }
    setLoading(false);
  };

  // Temperatura média de todos os cômodos
  const avgTemp = Math.round(
    roomSensors.reduce((acc, sensor) => acc + sensor.temperature, 0) / roomSensors.length
  );

  // Qualidade do ar baseada em umidade
  const getAirQuality = (humidity: number) => {
    if (humidity >= 40 && humidity <= 60) return { label: 'Perfect', color: 'text-green-400' };
    if (humidity >= 30 && humidity <= 70) return { label: 'Good', color: 'text-yellow-400' };
    return { label: 'Poor', color: 'text-red-400' };
  };

  const currentAirQuality = getAirQuality(selectedRoom.humidity);

  if (compact) {
    return (
      <div className="backdrop-blur-xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 rounded-3xl border border-white/10 p-6 shadow-2xl">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-white mb-1">{selectedRoom.room}</h2>
            <p className="text-slate-400 text-sm">Climate Control</p>
          </div>
          <button className="p-2 rounded-xl bg-white/5 hover:bg-white/10 transition-all">
            <Maximize2 className="w-4 h-4 text-slate-400" />
          </button>
        </div>

        {/* Temperatura Grande */}
        <div className="mb-8">
          <div className="text-6xl text-white mb-2">
            {selectedRoom.temperature}°
          </div>
          <div className="flex items-center gap-2 text-slate-400 text-sm">
            <Thermometer className="w-4 h-4" />
            <span>{avgTemp} degrees average</span>
          </div>
        </div>

        {/* Mini Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white/5 rounded-2xl p-4 border border-white/10">
            <div className="flex items-center gap-2 mb-2">
              <Droplets className="w-4 h-4 text-blue-400" />
              <span className="text-xs text-slate-400">Humidity</span>
            </div>
            <div className="text-2xl text-white">{selectedRoom.humidity}%</div>
            <p className={`text-xs ${currentAirQuality.color} mt-1`}>{currentAirQuality.label}</p>
          </div>
          
          <div className="bg-white/5 rounded-2xl p-4 border border-white/10">
            <div className="flex items-center gap-2 mb-2">
              <Wind className="w-4 h-4 text-purple-400" />
              <span className="text-xs text-slate-400">Air Flow</span>
            </div>
            <div className="text-2xl text-white">Good</div>
            <p className="text-xs text-green-400 mt-1">Optimal</p>
          </div>
        </div>

        {/* Room Selector */}
        <div className="mt-6 flex gap-2 overflow-x-auto pb-2">
          {roomSensors.map((room) => (
            <button
              key={room.room}
              onClick={() => setSelectedRoom(room)}
              className={`px-4 py-2 rounded-xl text-sm whitespace-nowrap transition-all ${
                selectedRoom.room === room.room
                  ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                  : 'bg-white/5 text-slate-400 hover:bg-white/10 border border-white/10'
              }`}
            >
              {room.room}
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="backdrop-blur-xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 rounded-3xl border border-white/10 p-8 shadow-2xl">
      <div className="flex items-start justify-between mb-8">
        <div>
          <h2 className="text-2xl text-white mb-2">Climate Monitor</h2>
          <p className="text-slate-400">Real-time temperature and humidity tracking</p>
        </div>
      </div>

      {/* Grid de todos os cômodos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {roomSensors.map((room) => {
          const quality = getAirQuality(room.humidity);
          return (
            <div
              key={room.room}
              onClick={() => setSelectedRoom(room)}
              className={`cursor-pointer p-6 rounded-2xl border transition-all ${
                selectedRoom.room === room.room
                  ? 'bg-indigo-500/20 border-indigo-500/30 shadow-lg shadow-indigo-500/20'
                  : 'bg-white/5 border-white/10 hover:bg-white/10'
              }`}
            >
              <h3 className="text-slate-300 mb-4">{room.room}</h3>
              
              <div className="text-4xl text-white mb-4">{room.temperature}°</div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-400 flex items-center gap-1">
                    <Droplets className="w-3 h-3" />
                    Humidity
                  </span>
                  <span className="text-white">{room.humidity}%</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-400">Air Quality</span>
                  <span className={quality.color}>{quality.label}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Detalhes do cômodo selecionado */}
      <div className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 rounded-2xl p-6 border border-indigo-500/20">
        <h3 className="text-white mb-4">{selectedRoom.room} - Detailed View</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Thermometer className="w-5 h-5 text-orange-400" />
              <span className="text-slate-300">Temperature</span>
            </div>
            <div className="text-3xl text-white mb-1">{selectedRoom.temperature}°C</div>
            <p className="text-sm text-slate-400">Feels comfortable</p>
          </div>
          
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Droplets className="w-5 h-5 text-blue-400" />
              <span className="text-slate-300">Humidity</span>
            </div>
            <div className="text-3xl text-white mb-1">{selectedRoom.humidity}%</div>
            <p className={`text-sm ${currentAirQuality.color}`}>{currentAirQuality.label} level</p>
          </div>
          
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Wind className="w-5 h-5 text-purple-400" />
              <span className="text-slate-300">Ventilation</span>
            </div>
            <div className="text-3xl text-white mb-1">Active</div>
            <p className="text-sm text-green-400">System running</p>
          </div>
        </div>
      </div>

      {/* Estatísticas gerais */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white/5 rounded-xl p-4 border border-white/10">
          <p className="text-xs text-slate-400 mb-1">Average Temp</p>
          <p className="text-xl text-white">{avgTemp}°C</p>
        </div>
        <div className="bg-white/5 rounded-xl p-4 border border-white/10">
          <p className="text-xs text-slate-400 mb-1">Rooms Monitored</p>
          <p className="text-xl text-white">{roomSensors.length}</p>
        </div>
        <div className="bg-white/5 rounded-xl p-4 border border-white/10">
          <p className="text-xs text-slate-400 mb-1">Energy Mode</p>
          <p className="text-xl text-green-400">Eco</p>
        </div>
        <div className="bg-white/5 rounded-xl p-4 border border-white/10">
          <p className="text-xs text-slate-400 mb-1">System Status</p>
          <p className="text-xl text-green-400">Online</p>
        </div>
      </div>
    </div>
  );
}
