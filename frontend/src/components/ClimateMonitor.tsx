import { useState, useEffect } from 'react';
import { Thermometer, Droplets, Wind, Home, UtensilsCrossed, Bed, Bath } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { climateApi } from '../lib/api';

interface ClimateData {
  time: string;
  temperature: number;
  humidity: number;
}

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
    { room: 'Sala', temperature: 23, humidity: 55 },
    { room: 'Cozinha', temperature: 25, humidity: 60 },
    { room: 'Suite', temperature: 22, humidity: 52 },
    { room: 'Banheiro', temperature: 24, humidity: 65 },
  ]);

  const [selectedRoom, setSelectedRoom] = useState<string>('Sala');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const rooms = [
    { name: 'Sala', icon: Home },
    { name: 'Cozinha', icon: UtensilsCrossed },
    { name: 'Suite', icon: Bed },
    { name: 'Banheiro', icon: Bath },
  ];

  const [historicalData, setHistoricalData] = useState<ClimateData[]>([
    { time: '00:00', temperature: 21, humidity: 60 },
    { time: '04:00', temperature: 20, humidity: 62 },
    { time: '08:00', temperature: 22, humidity: 58 },
    { time: '12:00', temperature: 25, humidity: 52 },
    { time: '16:00', temperature: 24, humidity: 54 },
    { time: '20:00', temperature: 23, humidity: 55 },
  ]);

  // GET: Carregar dados dos sensores ao montar o componente
  useEffect(() => {
    loadSensors();
  }, []);

  // GET: Carregar histórico quando trocar de cômodo
  useEffect(() => {
    loadHistory(selectedRoom);
  }, [selectedRoom]);

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

  const loadHistory = async (room: string) => {
    const response = await climateApi.getHistory(room, 24);
    
    if (response.success && response.data) {
      setHistoricalData(response.data as ClimateData[]);
    }
  };

  // Simulate real-time updates (pode ser substituído por WebSocket ou polling)
  useEffect(() => {
    const interval = setInterval(() => {
      loadSensors(); // Atualiza dados dos sensores periodicamente
    }, 30000); // A cada 30 segundos

    return () => clearInterval(interval);
  }, []);

  const getTempStatus = (temp: number) => {
    if (temp < 18) return { label: 'Frio', color: 'text-blue-600' };
    if (temp > 26) return { label: 'Quente', color: 'text-red-600' };
    return { label: 'Confortável', color: 'text-green-600' };
  };

  const getHumidityStatus = (humidity: number) => {
    if (humidity < 40) return { label: 'Baixa', color: 'text-orange-600' };
    if (humidity > 60) return { label: 'Alta', color: 'text-blue-600' };
    return { label: 'Ideal', color: 'text-green-600' };
  };

  const currentSensor = roomSensors.find(s => s.room === selectedRoom) || roomSensors[0];
  const tempStatus = getTempStatus(currentSensor.temperature);
  const humidityStatus = getHumidityStatus(currentSensor.humidity);

  const avgTemp = Math.round(roomSensors.reduce((sum, s) => sum + s.temperature, 0) / roomSensors.length * 10) / 10;
  const avgHumidity = Math.round(roomSensors.reduce((sum, s) => sum + s.humidity, 0) / roomSensors.length);

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-cyan-100 p-3 rounded-lg">
          <Wind className="w-6 h-6 text-cyan-600" />
        </div>
        <div>
          <h2>Monitoramento de Clima</h2>
          <p className="text-slate-500 text-sm">Média: {avgTemp}°C · {avgHumidity}% umidade</p>
        </div>
      </div>

      {/* Room navigation */}
      {!compact && (
        <div className="mb-6">
          <h3 className="text-sm text-slate-600 mb-3">Cômodos</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {rooms.map((room) => {
              const Icon = room.icon;
              const sensor = roomSensors.find(s => s.room === room.name);
              
              return (
                <button
                  key={room.name}
                  onClick={() => setSelectedRoom(room.name)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    selectedRoom === room.name
                      ? 'border-cyan-400 bg-cyan-50'
                      : 'border-slate-200 bg-white hover:border-cyan-200'
                  }`}
                >
                  <Icon className={`w-5 h-5 mx-auto mb-1 ${
                    selectedRoom === room.name ? 'text-cyan-600' : 'text-slate-600'
                  }`} />
                  <p className="text-xs text-center">{room.name}</p>
                  {sensor && (
                    <p className="text-xs text-center text-slate-500 mt-0.5">
                      {sensor.temperature}°C · {sensor.humidity}%
                    </p>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Current readings */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gradient-to-br from-orange-50 to-red-50 p-4 rounded-lg border border-orange-200">
          <div className="flex items-center gap-2 mb-2">
            <Thermometer className="w-5 h-5 text-orange-600" />
            <span className="text-sm text-slate-600">Temperatura</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl">{currentSensor.temperature}°C</span>
          </div>
          <p className={`text-sm mt-1 ${tempStatus.color}`}>{tempStatus.label}</p>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-4 rounded-lg border border-blue-200">
          <div className="flex items-center gap-2 mb-2">
            <Droplets className="w-5 h-5 text-blue-600" />
            <span className="text-sm text-slate-600">Umidade</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl">{currentSensor.humidity}%</span>
          </div>
          <p className={`text-sm mt-1 ${humidityStatus.color}`}>{humidityStatus.label}</p>
        </div>
      </div>

      {/* Chart */}
      {!compact && (
        <div className="mt-6">
          <h3 className="text-sm mb-4">Histórico de {selectedRoom} - Últimas 24h</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={historicalData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="time" stroke="#64748b" fontSize={12} />
              <YAxis yAxisId="left" stroke="#f97316" fontSize={12} />
              <YAxis yAxisId="right" orientation="right" stroke="#3b82f6" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="temperature"
                stroke="#f97316"
                strokeWidth={2}
                name="Temperatura (°C)"
                dot={{ fill: '#f97316', r: 4 }}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="humidity"
                stroke="#3b82f6"
                strokeWidth={2}
                name="Umidade (%)"
                dot={{ fill: '#3b82f6', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}