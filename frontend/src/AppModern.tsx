import { useState } from 'react';
import { LightControlSH2 } from './components/LightControlSH2';
import { SwitchControlSH2 } from './components/SwitchControlSH2';
import { Home, Lightbulb, ToggleRight, Sparkles, Bell, User, Wifi, WifiOff } from 'lucide-react';
import { useWebSocket } from './services/websocket';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const { isConnected } = useWebSocket();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header com glassmorphism */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-slate-900/50 border-b border-white/10">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-2.5 rounded-xl shadow-lg shadow-indigo-500/20">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl text-white">Smart Heaven v2</h1>
                <p className="text-sm text-slate-400">Sistema de Automação Residencial</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/5 border border-white/10">
                {isConnected ? (
                  <>
                    <Wifi className="w-4 h-4 text-green-400" />
                    <span className="text-sm text-green-400">Conectado</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="w-4 h-4 text-red-400" />
                    <span className="text-sm text-red-400">Desconectado</span>
                  </>
                )}
              </div>
              <button className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-all">
                <Bell className="w-5 h-5 text-slate-300" />
              </button>
              <button className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-all">
                <User className="w-5 h-5 text-slate-300" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Pills */}
      <nav className="sticky top-[73px] z-40 backdrop-blur-xl bg-slate-900/30 border-b border-white/5">
        <div className="max-w-[1600px] mx-auto px-6 py-3">
          <div className="flex gap-2 overflow-x-auto">
            {[
              { id: 'overview', label: 'Dashboard', icon: Home },
              { id: 'lights', label: 'Luzes', icon: Lightbulb },
              { id: 'switches', label: 'Interruptores', icon: ToggleRight },
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-5 py-2.5 rounded-xl whitespace-nowrap transition-all ${
                    activeTab === tab.id
                      ? 'bg-white/10 text-white shadow-lg shadow-indigo-500/20 border border-white/20'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-sm">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-[1600px] mx-auto px-6 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <LightControlSH2 compact />
              <SwitchControlSH2 compact />
            </div>
          </div>
        )}
        {activeTab === 'lights' && <LightControlSH2 />}
        {activeTab === 'switches' && <SwitchControlSH2 />}
      </main>
    </div>
  );
}
