# Smart Heaven v2.0 🏠

Sistema de automação residencial moderno desenvolvido com FastAPI e React.

## 🚀 Stack Tecnológica

### Backend
- **FastAPI** - Framework web async de alta performance
- **SQLAlchemy 2.0** - ORM com suporte async
- **Alembic** - Migrations de banco de dados
- **Pydantic v2** - Validação de dados
- **aiomqtt** - Cliente MQTT assíncrono
- **MySQL** - Banco de dados

### Frontend
- **React 18** - Biblioteca UI
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TanStack Query** - Gerenciamento de estado servidor
- **Tailwind CSS** - Estilização
- **Lucide React** - Ícones

### Infraestrutura
- **Docker & Docker Compose** - Containerização
- **Mosquitto** - MQTT Broker
- **WebSocket** - Comunicação real-time

## 📁 Estrutura do Projeto

```
smart-heaven-v2/
├── backend/
│   ├── src/
│   │   ├── api/v1/          # Endpoints REST
│   │   ├── core/            # Configurações
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── repositories/    # Data access layer
│   │   ├── services/        # Business logic
│   │   └── main.py          # FastAPI app
│   ├── alembic/             # Database migrations
│   ├── tests/               # Testes
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes React
│   │   ├── pages/           # Páginas
│   │   ├── services/        # API calls
│   │   └── App.tsx
│   └── package.json
│
├── docker-compose.yml
└── README.md
```

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (opcional)

### Opção 1: Docker (Recomendado)

1. **Clone o repositório**
```bash
cd h:/vscode/smart-heaven-v2
```

2. **Configure as variáveis de ambiente**
```bash
cp backend/.env.example backend/.env
```

Edite `backend/.env` com suas configurações:
- Credenciais do banco de dados
- Configurações do MQTT broker
- Secret key (gere com: `openssl rand -hex 32`)

3. **Inicie os serviços**
```bash
docker-compose up -d
```

4. **Execute as migrations**
```bash
docker-compose exec backend alembic upgrade head
```

5. **Acesse a aplicação**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Opção 2: Manual

#### Backend

1. **Crie um ambiente virtual**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. **Instale as dependências**
```powershell
pip install -r requirements.txt
```

3. **Configure o .env**
```powershell
cp .env.example .env
```

4. **Execute as migrations**
```powershell
alembic upgrade head
```

5. **Inicie o servidor**
```powershell
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

1. **Instale as dependências**
```powershell
cd frontend
npm install
```

2. **Inicie o servidor de desenvolvimento**
```powershell
npm run dev
```

## 📚 API Endpoints

### Luzes (Lights)
- `GET /api/v1/lights` - Listar todas as luzes
- `GET /api/v1/lights/{lampada}` - Obter luz específica
- `POST /api/v1/lights/control` - Controlar luz
- `POST /api/v1/lights/{lampada}/on` - Ligar luz
- `POST /api/v1/lights/{lampada}/off` - Desligar luz
- `POST /api/v1/lights/{lampada}/toggle` - Alternar luz

### Interruptores (Switches)
- `GET /api/v1/switches` - Listar todos os interruptores
- `GET /api/v1/switches/{nome}` - Obter interruptor específico
- `POST /api/v1/switches/control` - Habilitar/desabilitar interruptor
- `POST /api/v1/switches/{nome}/enable` - Habilitar interruptor
- `POST /api/v1/switches/{nome}/disable` - Desabilitar interruptor

### Logs
- `GET /api/v1/logs` - Obter logs com filtros
- `GET /api/v1/logs/recent` - Logs recentes
- `GET /api/v1/logs/light/{comodo}` - Logs de uma luz específica

### Sistema
- `GET /api/v1/health` - Health check
- `GET /api/v1/` - Info da API

### WebSocket
- `WS /api/v1/ws` - Conexão WebSocket para updates em tempo real

## 🔧 Migrations

### Criar nova migration
```powershell
cd backend
alembic revision --autogenerate -m "Descrição da mudança"
```

### Aplicar migrations
```powershell
alembic upgrade head
```

### Reverter migration
```powershell
alembic downgrade -1
```

## 🧪 Testes

```powershell
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## 🔌 Integração MQTT

O sistema se comunica com dispositivos ESP32/ESP8266 via MQTT.

### Tópicos principais:
- `casa/evento/botao` - Eventos de botões físicos
- `casa/servidor/comando_lampada` - Comandos para lâmpadas
- `casa/estado/lampada/#` - Estados das lâmpadas
- `casa/servidor_web/comando_lampada` - Comandos da interface web
- `debug/esp8266` - Mensagens de debug

## 📝 Próximos Passos

- [ ] Implementar autenticação JWT
- [ ] Adicionar testes unitários e de integração
- [ ] Criar dashboard de analytics
- [ ] Implementar automações (schedules, triggers)
- [ ] Adicionar suporte a sensores
- [ ] Integração com assistentes de voz
- [ ] App mobile (React Native)
- [ ] Notificações push

## 👤 Autor

**Pedro Lucas Araujo Menardi**

## 📄 Licença

Este projeto é privado e de uso pessoal.

---

**Documentação da API:** http://localhost:8000/docs

**Versão:** 2.0.0
