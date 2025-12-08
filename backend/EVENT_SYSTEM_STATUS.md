# Smart Heaven v2 - Event System Implementation Status

## ✅ Completado

### 1. Schemas Pydantic (src/namespaces/events/schemas.py)
- **EventPayload**: Formato moderno v1.0 para eventos de dispositivos
- **StatePayload**: Confirmação de estado por dispositivos
- **CommandPayload**: Comandos server -> device
- **GateCommandPayload**: Comando especial para portão (pulse_sequence)
- **LegacyStatePayload**: Suporte a formato antigo (ESP-01)
- **EventResponse**: Resposta de processamento de eventos
- **MappingResponse/Create/Update**: Gerenciamento de mappings
- **MetricsResponse**: Métricas do sistema

### 2. Modelo Mapping (src/models/mapping.py)
- Tabela `mappings` para device + button -> action
- Suporte a wildcards (*) para button e action
- Campo priority para ordenação de execução
- Campo parameters_json para parâmetros customizados
- Método `matches_event()` para verificar se mapping se aplica

### 3. MappingRepository (src/repositories/mapping_repo.py)
- CRUD completo para mappings
- `find_matching_mappings()` - encontra mappings aplicáveis a um evento
- Suporte a filtros (active_only, by_device, by_target)
- Soft delete via deactivate/activate

## 🔄 Próximos Passos

### 4. Legacy Adapter (criar: src/services/legacy_adapter.py)
```python
class LegacyAdapter:
    def adapt_legacy_state_to_event(payload: dict) -> EventPayload:
        # Converter { "comodo": "L_X", "state": "ON" } 
        # em EventPayload moderno
    
    def detect_format(payload: dict) -> str:
        # Detectar se é v1.0, legacy, ou inválido
```

### 5. EventService (criar: src/services/event_service.py)
- `process_event()` - pipeline completo:
  1. Validar JSON + versão
  2. Gerar event_id único
  3. Verificar idempotência (cache 3s)
  4. Salvar em logs com received_ts
  5. Buscar mappings aplicáveis
  6. Executar ações (publicar comandos MQTT)
  7. Retornar EventResponse
- `apply_mapping()` - executar ação de um mapping
- `check_idempotency()` - evitar duplicatas
- Metrics tracking (total_events, latency, etc)

### 6. MQTT Service Atualização (src/services/mqtt_service.py)
**Adicionar handlers:**
- `on_event_received(topic, payload)`:
  - Topic: `casa/evento/botao` ou `casa/evento/#`
  - Parse EventPayload
  - Chamar event_service.process_event()
  
- `on_state_received(topic, payload)`:
  - Topic: `casa/estado/lampada/{comodo}`
  - Parse StatePayload
  - Atualizar tabela luzes
  - Se origin != "server", adaptar para evento (legacy)

- `on_command_received(topic, payload)`:
  - Topic: `casa/servidor/comando_lampada`
  - **Loop prevention**: ignorar se origin == "server"
  - Se origin != "server", tratar como evento legacy

**Publicação com origin:**
```python
async def publish_command(comodo, command, trigger=None):
    payload = CommandPayload(
        comodo=comodo,
        command=command,
        origin="server",  # ← IMPORTANTE
        trigger=trigger
    )
    await self.publish("casa/servidor/comando_lampada", payload.json())
```

### 7. Events Controller (criar: src/namespaces/events/controller.py)
```python
@router.post("/api/v1/events", response_model=EventResponse)
async def receive_event(event: EventPayload, db: AsyncSession):
    # Receber evento via HTTP
    # Processar e retornar resultado

@router.get("/api/v1/mappings", response_model=List[MappingResponse])
async def list_mappings(device: Optional[str] = None):
    # Listar mappings (filtrar por device opcional)

@router.post("/api/v1/mappings", response_model=MappingResponse)
async def create_mapping(mapping: MappingCreate):
    # Criar novo mapping

@router.put("/api/v1/mappings/{id}", response_model=MappingResponse)
async def update_mapping(id: int, mapping: MappingUpdate):
    # Atualizar mapping existente

@router.delete("/api/v1/mappings/{id}")
async def delete_mapping(id: int):
    # Deletar/desativar mapping

@router.post("/api/v1/commands", response_model=MessageResponse)
async def send_command(cmd: CommandPayload):
    # Forçar comando via HTTP (útil para UI)
```

### 8. Metrics no System Controller
```python
@router.get("/api/v1/metrics", response_model=MetricsResponse)
async def get_metrics():
    # Retornar métricas do event_service
    return event_service.get_metrics()
```

## 📊 Fluxo de Dados

### Cenário 1: Botão Moderno (Base_D)
```
1. ESP publica em casa/evento/botao:
   {"v":"1.0","device":"Base_D","button":"S1","action":"press",...}

2. Backend recebe (mqtt_service.on_event_received):
   - Valida payload
   - Chama event_service.process_event()

3. EventService:
   - Gera event_id: "Base_D_S1_press_2025-12-08T11:23:00Z"
   - Verifica cache (idempotência)
   - Salva em logs com received_ts
   - Busca mappings: Base_D + S1 + press
   - Encontra: toggle L_Cozinha
   - Publica comando em casa/servidor/comando_lampada:
     {"v":"1.0","comodo":"L_Cozinha","command":"toggle","origin":"server"}

4. Base_C recebe comando:
   - Aciona relé
   - Publica estado em casa/estado/lampada/L_Cozinha:
     {"v":"1.0","comodo":"L_Cozinha","state":"ON","origin":"Base_C"}

5. Backend recebe estado:
   - Atualiza tabela luzes
```

### Cenário 2: Legacy (ESP-01)
```
1. ESP-01 aciona localmente e publica:
   {"comodo":"L_Churrasqueira","state":"ON","ts":"..."}

2. Backend (mqtt_service.on_state_received):
   - Detecta formato legacy (sem campo "v")
   - Chama legacy_adapter.adapt_legacy_state_to_event()
   - Gera EventPayload sintético
   - Processa como evento normal

3. Registra em logs como origem "legacy"
```

### Cenário 3: Loop Prevention
```
1. Base_D publica comando diretamente (firmware antigo):
   casa/servidor/comando_lampada sem "origin"

2. Backend (on_command_received):
   - Verifica origin
   - Se != "server", trata como evento (registra + alerta)
   - NÃO republica (evita loop)
```

## 🗄️ Migração de Banco

Quando banco disponível:
```bash
cd backend
alembic revision --autogenerate -m "Add mappings table"
alembic upgrade head
```

SQL esperado:
```sql
CREATE TABLE mappings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_device VARCHAR(50) NOT NULL,
    source_button VARCHAR(20) NOT NULL,
    source_action VARCHAR(20) DEFAULT 'press',
    action_type VARCHAR(50) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id VARCHAR(100) NOT NULL,
    parameters_json JSON,
    active BOOLEAN DEFAULT TRUE,
    priority INT DEFAULT 100,
    description TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    INDEX idx_device (source_device),
    INDEX idx_button (source_button),
    INDEX idx_active (active)
);
```

## 🧪 Exemplos de Mappings

```sql
-- Base_D botão S1 -> toggle L_Cozinha
INSERT INTO mappings (source_device, source_button, action_type, target_type, target_id, active)
VALUES ('Base_D', 'S1', 'toggle_light', 'light', 'L_Cozinha', TRUE);

-- Base_A botão S2 -> cena "Movie Mode"
INSERT INTO mappings (source_device, source_button, action_type, target_type, target_id, parameters_json, active)
VALUES ('Base_A', 'S2', 'activate_scene', 'scene', 'movie_mode', '{"dim_level": 20}', TRUE);

-- Base_Portao S1 -> pulso portão
INSERT INTO mappings (source_device, source_button, action_type, target_type, target_id, parameters_json, active)
VALUES ('Base_Portao', 'S1', 'pulse_gate', 'gate', 'main_gate', '{"pulses": 8, "pulse_ms": 1000}', TRUE);

-- Wildcard: qualquer botão de Base_Emergency -> alerta
INSERT INTO mappings (source_device, source_button, action_type, target_type, target_id, active)
VALUES ('Base_Emergency', '*', 'send_alert', 'notification', 'admin_telegram', TRUE);
```

## 📝 Testes Necessários

Criar em `backend/tests/test_event_system.py`:
- ✅ Parser de payloads (v1.0 e legacy)
- ✅ Matching de mappings (wildcards)
- ✅ Idempotência (mesmo evento 2x)
- ✅ Loop prevention (origin=server)
- ✅ Retry de MQTT publish
- ✅ Latency tracking

## 🔧 Configurações MQTT ACL

Restringir permissões dos ESPs:
```
# ESP devices podem apenas:
user esp_base_d
topic write casa/evento/#
topic write casa/estado/#
topic read casa/servidor/comando_lampada

# Backend pode tudo
user backend
topic readwrite #
```

## 📚 Próximas Tarefas

1. Implementar EventService (src/services/event_service.py)
2. Implementar LegacyAdapter (src/services/legacy_adapter.py)
3. Atualizar MQTTService com novos handlers
4. Criar EventsController
5. Adicionar /api/metrics endpoint
6. Criar testes unitários
7. Gerar migração quando banco disponível
8. Documentar no README.md
9. Criar migrations.md com roteiro de atualização de firmwares
