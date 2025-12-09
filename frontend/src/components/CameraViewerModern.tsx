import { useState, useEffect } from 'react';
import { Camera, Video, RefreshCw, Maximize2, Circle, Home, Trees, ShieldAlert, Play, Pause, Download } from 'lucide-react';
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

  const toggleRecording = async (id: string) => {
    const camera = cameras.find(c => c.id === id);
    if (!camera) return;

    setCameras(cameras.map(c =>
      c.id === id ? { ...c, recording: !c.recording } : c
    ));

    const response = await camerasApi.toggleRecording(id, !camera.recording);
    
    if (!response.success) {
      setCameras(cameras.map(c =>
        c.id === id ? { ...c, recording: camera.recording } : c
      ));
      setError(response.error || 'Erro ao alterar gravação');
    }
  };

  const captureSnapshot = async (id: string) => {
    const response = await camerasApi.capture(id);
    
    if (response.success) {
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

  if (compact) {
    return (
      <div className="backdrop-blur-xl bg-gradient-to-br from-purple-900/40 to-slate-900/60 rounded-3xl border border-purple-500/20 p-6 shadow-2xl">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-white mb-1">Cameras</h2>
            <p className="text-slate-400 text-sm">{activeCameras} active · {recordingCameras} recording</p>
          </div>
          <button 
            onClick={loadCameras}
            className="p-2 rounded-xl bg-white/5 hover:bg-white/10 transition-all"
          >
            <RefreshCw className="w-4 h-4 text-slate-400" />
          </button>
        </div>

        {/* Cameras Grid */}
        <div className="grid grid-cols-1 gap-3">
          {displayCameras.map(camera => (
            <div
              key={camera.id}
              className="relative group rounded-2xl overflow-hidden border border-white/10 hover:border-purple-500/30 transition-all cursor-pointer bg-slate-900"
            >
              <div className="aspect-video relative overflow-hidden">
                <ImageWithFallback
                  src={camera.imageUrl}
                  alt={camera.name}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
                
                {/* Status indicators */}
                <div className="absolute top-2 left-2 flex items-center gap-2">
                  <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs backdrop-blur-md ${
                    camera.status === 'active'
                      ? 'bg-green-500/90 text-white'
                      : 'bg-red-500/90 text-white'
                  }`}>
                    <Circle className="w-2 h-2 fill-current animate-pulse" />
                    <span>LIVE</span>
                  </div>
                  {camera.recording && (
                    <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-red-600/90 text-white text-xs backdrop-blur-md">
                      <Video className="w-3 h-3" />
                      <span>REC</span>
                    </div>
                  )}
                </div>

                {/* Camera info */}
                <div className="absolute bottom-2 left-2 right-2 text-white">
                  <p className="text-sm">{camera.name}</p>
                  <p className="text-xs text-slate-300">{camera.location}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {cameras.length > 2 && (
          <div className="mt-4 text-center">
            <p className="text-sm text-slate-400">+{cameras.length - 2} more cameras</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="backdrop-blur-xl bg-gradient-to-br from-purple-900/40 to-slate-900/60 rounded-3xl border border-purple-500/20 p-8 shadow-2xl">
      <div className="flex items-start justify-between mb-8">
        <div>
          <h2 className="text-2xl text-white mb-2">Security Cameras</h2>
          <p className="text-slate-400">{activeCameras} active · {recordingCameras} recording</p>
        </div>
        <button 
          onClick={loadCameras}
          className="p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-all"
        >
          <RefreshCw className="w-5 h-5 text-slate-400" />
        </button>
      </div>

      {/* Area Navigation */}
      <div className="mb-6">
        <h3 className="text-slate-300 mb-4">Areas</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
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
                className={`p-4 rounded-2xl border transition-all ${
                  selectedArea === area.name
                    ? 'bg-purple-500/20 border-purple-500/30 shadow-lg shadow-purple-500/10'
                    : 'bg-white/5 border-white/10 hover:bg-white/10'
                }`}
              >
                <Icon className={`w-6 h-6 mx-auto mb-2 ${
                  selectedArea === area.name ? 'text-purple-400' : 'text-slate-400'
                }`} />
                <p className="text-sm text-white text-center">{area.name}</p>
                <p className="text-xs text-slate-400 text-center mt-1">
                  {areaCamerasActive}/{areaCamerasCount} active
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Cameras Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {displayCameras.map(camera => (
          <div
            key={camera.id}
            className="relative group rounded-2xl overflow-hidden border border-white/10 hover:border-purple-500/30 transition-all cursor-pointer bg-slate-900"
            onClick={() => setSelectedCamera(selectedCamera === camera.id ? null : camera.id)}
          >
            <div className="aspect-video relative overflow-hidden">
              <ImageWithFallback
                src={camera.imageUrl}
                alt={camera.name}
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
              
              {/* Status indicators */}
              <div className="absolute top-3 left-3 flex items-center gap-2">
                <div className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-full text-xs backdrop-blur-md ${
                  camera.status === 'active'
                    ? 'bg-green-500/90 text-white'
                    : 'bg-red-500/90 text-white'
                }`}>
                  <Circle className="w-2 h-2 fill-current animate-pulse" />
                  <span>LIVE</span>
                </div>
                {camera.recording && (
                  <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-red-600/90 text-white text-xs backdrop-blur-md">
                    <Video className="w-3 h-3" />
                    <span>REC</span>
                  </div>
                )}
              </div>

              {/* Camera info */}
              <div className="absolute bottom-3 left-3 right-3 flex items-end justify-between">
                <div className="text-white">
                  <p className="text-sm">{camera.name}</p>
                  <p className="text-xs text-slate-300">{camera.location} · {camera.area}</p>
                </div>
                <button className="p-2 bg-white/10 hover:bg-white/20 rounded-lg backdrop-blur-md transition-all">
                  <Maximize2 className="w-4 h-4 text-white" />
                </button>
              </div>
            </div>

            {/* Expanded controls */}
            {selectedCamera === camera.id && (
              <div className="p-4 bg-gradient-to-br from-purple-500/10 to-slate-900/50 border-t border-white/10">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs text-slate-400">Last update: now</span>
                  <div className={`px-2 py-1 rounded-lg text-xs ${
                    camera.recording ? 'bg-red-500/20 text-red-300' : 'bg-slate-700/50 text-slate-400'
                  }`}>
                    {camera.recording ? 'Recording' : 'Idle'}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    className="flex-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl transition-colors text-xs flex items-center justify-center gap-2"
                    onClick={(e) => {
                      e.stopPropagation();
                      captureSnapshot(camera.id);
                    }}
                  >
                    <Download className="w-3 h-3" />
                    Snapshot
                  </button>
                  <button
                    className={`flex-1 px-3 py-2 rounded-xl transition-colors text-xs flex items-center justify-center gap-2 ${
                      camera.recording
                        ? 'bg-red-600 hover:bg-red-700 text-white'
                        : 'bg-slate-700 hover:bg-slate-600 text-white'
                    }`}
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleRecording(camera.id);
                    }}
                  >
                    {camera.recording ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
                    {camera.recording ? 'Stop' : 'Record'}
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
