import { useState, useEffect } from 'react';
import { Camera, Video, RefreshCw, Maximize2, Circle, Home, Trees, ShieldAlert } from 'lucide-react';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { camerasApi } from '../lib/api';

interface CameraFeed {
  id: string;
  name: string;
  location: string;
  area: string;
  imageUrl: string;
  status: 'active' | 'inactive';
  recording: boolean;
}

interface CameraViewerProps {
  compact?: boolean;
}

export function CameraViewer({ compact = false }: CameraViewerProps) {
  const [cameras, setCameras] = useState<CameraFeed[]>([
    {
      id: '1',
      name: 'Entrada Principal',
      location: 'Porta da Frente',
      area: 'Interna',
      imageUrl: 'https://images.unsplash.com/photo-1635438843495-674a5899fd4c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxmcm9udCUyMGRvb3IlMjBjYW1lcmF8ZW58MXx8fHwxNzY0OTc2NDIzfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      status: 'active',
      recording: true,
    },
    {
      id: '2',
      name: 'Garagem',
      location: 'Área de Veículos',
      area: 'Interna',
      imageUrl: 'https://images.unsplash.com/photo-1549047608-55b2fd4b8427?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxnYXJhZ2UlMjBjYW1lcmElMjB2aWV3fGVufDF8fHx8MTc2NDk3NjQyMnww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      status: 'active',
      recording: true,
    },
    {
      id: '3',
      name: 'Sala de Estar',
      location: 'Área Social',
      area: 'Interna',
      imageUrl: 'https://images.unsplash.com/photo-1670278458296-00ff8a63141e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzZWN1cml0eSUyMGNhbWVyYSUyMGhvbWV8ZW58MXx8fHwxNzY0OTc2NDIyfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      status: 'active',
      recording: false,
    },
    {
      id: '4',
      name: 'Jardim',
      location: 'Área dos Fundos',
      area: 'Externa',
      imageUrl: 'https://images.unsplash.com/photo-1610843108778-b60ad4e73747?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxiYWNreWFyZCUyMGNhbWVyYXxlbnwxfHx8fDE3NjQ5NzY0MjN8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      status: 'active',
      recording: true,
    },
    {
      id: '5',
      name: 'Portão Frontal',
      location: 'Entrada Principal',
      area: 'Externa',
      imageUrl: 'https://images.unsplash.com/photo-1635438843495-674a5899fd4c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxmcm9udCUyMGRvb3IlMjBjYW1lcmF8ZW58MXx8fHwxNzY0OTc2NDIzfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      status: 'active',
      recording: true,
    },
    {
      id: '6',
      name: 'Perímetro Lateral',
      location: 'Lateral Direita',
      area: 'Perímetro',
      imageUrl: 'https://images.unsplash.com/photo-1670278458296-00ff8a63141e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzZWN1cml0eSUyMGNhbWVyYSUyMGhvbWV8ZW58MXx8fHwxNzY0OTc2NDIyfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      status: 'active',
      recording: true,
    },
  ]);

  const [selectedCamera, setSelectedCamera] = useState<string | null>(null);
  const [selectedArea, setSelectedArea] = useState<string>('Todas');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const areas = [
    { name: 'Todas', icon: Camera },
    { name: 'Interna', icon: Home },
    { name: 'Externa', icon: Trees },
    { name: 'Perímetro', icon: ShieldAlert },
  ];

  // GET: Carregar dados das câmeras ao montar o componente
  useEffect(() => {
    loadCameras();
  }, []);

  const loadCameras = async () => {
    setLoading(true);
    setError(null);
    const response = await camerasApi.getAll();
    
    if (response.success && response.data) {
      setCameras(response.data as CameraFeed[]);
    } else {
      setError(response.error || 'Erro ao carregar câmeras');
    }
    setLoading(false);
  };

  // POST: Iniciar/parar gravação
  const toggleRecording = async (id: string) => {
    const camera = cameras.find(c => c.id === id);
    if (!camera) return;

    // Atualiza UI otimisticamente
    setCameras(cameras.map(c =>
      c.id === id ? { ...c, recording: !c.recording } : c
    ));

    // Envia para API
    const response = await camerasApi.toggleRecording(id, !camera.recording);
    
    if (!response.success) {
      // Reverte em caso de erro
      setCameras(cameras.map(c =>
        c.id === id ? { ...c, recording: camera.recording } : c
      ));
      setError(response.error || 'Erro ao alterar gravação');
    }
  };

  // POST: Capturar snapshot
  const captureSnapshot = async (id: string) => {
    const response = await camerasApi.capture(id);
    
    if (response.success) {
      // Pode mostrar notificação de sucesso
      console.log('Snapshot capturado com sucesso');
    } else {
      setError(response.error || 'Erro ao capturar imagem');
    }
  };

  const filteredCameras = selectedArea === 'Todas'
    ? cameras
    : cameras.filter(camera => camera.area === selectedArea);

  const activeCameras = filteredCameras.filter(c => c.status === 'active').length;
  const recordingCameras = filteredCameras.filter(c => c.recording).length;

  const displayCameras = compact ? cameras.slice(0, 2) : filteredCameras;

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-purple-100 p-3 rounded-lg">
            <Camera className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h2>Câmeras de Segurança</h2>
            <p className="text-slate-500 text-sm">
              {activeCameras} ativas · {recordingCameras} gravando
            </p>
          </div>
        </div>
        <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
          <RefreshCw className="w-5 h-5 text-slate-600" />
        </button>
      </div>

      {/* Area navigation */}
      {!compact && (
        <div className="mb-6">
          <h3 className="text-sm text-slate-600 mb-3">Áreas</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {areas.map((area) => {
              const Icon = area.icon;
              const areaCamerasCount = area.name === 'Todas'
                ? cameras.length
                : cameras.filter(c => c.area === area.name).length;
              const areaCamerasActive = area.name === 'Todas'
                ? cameras.filter(c => c.status === 'active').length
                : cameras.filter(c => c.area === area.name && c.status === 'active').length;
              
              return (
                <button
                  key={area.name}
                  onClick={() => setSelectedArea(area.name)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    selectedArea === area.name
                      ? 'border-purple-400 bg-purple-50'
                      : 'border-slate-200 bg-white hover:border-purple-200'
                  }`}
                >
                  <Icon className={`w-5 h-5 mx-auto mb-1 ${
                    selectedArea === area.name ? 'text-purple-600' : 'text-slate-600'
                  }`} />
                  <p className="text-xs text-center">{area.name}</p>
                  <p className="text-xs text-center text-slate-500 mt-0.5">
                    {areaCamerasActive}/{areaCamerasCount} ativas
                  </p>
                </button>
              );
            })}
          </div>
        </div>
      )}

      <div className={`grid gap-4 ${compact ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-2'}`}>
        {displayCameras.map(camera => (
          <div
            key={camera.id}
            className="relative group rounded-lg overflow-hidden border-2 border-slate-200 hover:border-purple-300 transition-all cursor-pointer bg-slate-900"
            onClick={() => setSelectedCamera(selectedCamera === camera.id ? null : camera.id)}
          >
            <div className="aspect-video relative overflow-hidden">
              <ImageWithFallback
                src={camera.imageUrl}
                alt={camera.name}
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
              
              {/* Status indicators */}
              <div className="absolute top-3 left-3 flex items-center gap-2">
                <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full text-xs ${
                  camera.status === 'active'
                    ? 'bg-green-500/90 text-white'
                    : 'bg-red-500/90 text-white'
                }`}>
                  <Circle className="w-2 h-2 fill-current" />
                  <span>{camera.status === 'active' ? 'AO VIVO' : 'OFFLINE'}</span>
                </div>
                {camera.recording && (
                  <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-red-600/90 text-white text-xs">
                    <Video className="w-3 h-3" />
                    <span>REC</span>
                  </div>
                )}
              </div>

              {/* Camera info */}
              <div className="absolute bottom-3 left-3 right-3 flex items-end justify-between">
                <div className="text-white">
                  <h3 className="text-sm">{camera.name}</h3>
                  <p className="text-xs opacity-90">{camera.location} · {camera.area}</p>
                </div>
                <button className="p-2 bg-white/20 hover:bg-white/30 rounded-lg backdrop-blur-sm transition-all">
                  <Maximize2 className="w-4 h-4 text-white" />
                </button>
              </div>
            </div>

            {/* Expanded controls */}
            {selectedCamera === camera.id && !compact && (
              <div className="p-3 bg-slate-50 border-t">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">Última atualização: agora</span>
                  <div className="flex gap-2">
                    <button
                      className="px-3 py-1.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-xs"
                      onClick={() => captureSnapshot(camera.id)}
                    >
                      Capturar
                    </button>
                    <button
                      className="px-3 py-1.5 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors text-xs"
                      onClick={() => toggleRecording(camera.id)}
                    >
                      Configurar
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {compact && cameras.length > 2 && (
        <div className="mt-4 text-center">
          <p className="text-sm text-slate-500">+{cameras.length - 2} câmeras adicionais</p>
        </div>
      )}
    </div>
  );
}