# Configuração do Cloudflare Tunnel para Smart Heaven v2

Este guia explica como configurar o Cloudflare Tunnel para expor o Smart Heaven v2 na internet através do domínio `smart-heaven.com`.

## 📋 Pré-requisitos

- Domínio configurado no Cloudflare (`smart-heaven.com`)
- Smart Heaven v2 rodando no Raspberry Pi
- Acesso ao dashboard do Cloudflare

## 🚀 Opção 1: Cloudflare Tunnel (Zero Trust) - RECOMENDADO

### Passo 1: Instalar cloudflared no Raspberry Pi

```bash
# Baixar o cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb

# Instalar
sudo dpkg -i cloudflared-linux-arm64.deb

# Verificar instalação
cloudflared --version
```

### Passo 2: Autenticar com Cloudflare

```bash
cloudflared tunnel login
```

Isso abrirá uma página no navegador. Faça login e autorize o domínio `smart-heaven.com`.

### Passo 3: Criar um Tunnel

```bash
# Criar tunnel
cloudflared tunnel create smart-heaven-v2

# Isso criará um arquivo de credenciais em ~/.cloudflared/
```

**Anote o Tunnel ID** que aparecerá (algo como: `abcd1234-5678-90ef-ghij-klmnopqrstuv`)

### Passo 4: Criar arquivo de configuração

```bash
sudo nano ~/.cloudflared/config.yml
```

Adicione o seguinte conteúdo:

```yaml
tunnel: <SEU_TUNNEL_ID>
credentials-file: /home/pedro/.cloudflared/<SEU_TUNNEL_ID>.json

ingress:
  # Frontend
  - hostname: smart-heaven.com
    service: http://localhost:5173
  
  # API Backend
  - hostname: api.smart-heaven.com
    service: http://localhost:8000
  
  # WebSocket MQTT (se necessário)
  - hostname: mqtt.smart-heaven.com
    service: ws://localhost:9001
  
  # Catch-all rule (obrigatório)
  - service: http_status:404
```

**Ajuste o Tunnel ID** e o caminho do arquivo de credenciais!

### Passo 5: Configurar DNS no Cloudflare

```bash
# Criar registro DNS para o frontend
cloudflared tunnel route dns smart-heaven-v2 smart-heaven.com

# Criar registro DNS para a API
cloudflared tunnel route dns smart-heaven-v2 api.smart-heaven.com

# Criar registro DNS para MQTT (opcional)
cloudflared tunnel route dns smart-heaven-v2 mqtt.smart-heaven.com
```

### Passo 6: Iniciar o tunnel como serviço

```bash
# Instalar como serviço systemd
sudo cloudflared service install

# Iniciar o serviço
sudo systemctl start cloudflared

# Habilitar para iniciar no boot
sudo systemctl enable cloudflared

# Verificar status
sudo systemctl status cloudflared
```

### Passo 7: Verificar no Dashboard do Cloudflare

1. Acesse: https://one.dash.cloudflare.com/
2. Vá em **Access** > **Tunnels**
3. Verifique se o tunnel `smart-heaven-v2` está **Active**

## 🌐 Opção 2: Cloudflare com Port Forwarding (Menos Seguro)

Se você preferir não usar Tunnel:

### 1. Configure Port Forwarding no Roteador

- Porta externa: 80 → Porta interna: 5173 (Frontend)
- Porta externa: 443 → Porta interna: 8000 (Backend)

### 2. Configure DNS no Cloudflare

1. Acesse o dashboard do Cloudflare
2. Vá em **DNS** > **Records**
3. Adicione os registros:

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | @ | SEU_IP_PUBLICO | ✓ Proxied |
| CNAME | api | smart-heaven.com | ✓ Proxied |
| CNAME | www | smart-heaven.com | ✓ Proxied |

### 3. Configure SSL/TLS

1. Vá em **SSL/TLS** > **Overview**
2. Selecione: **Full** ou **Full (strict)**
3. Gere um certificado Origin no Cloudflare se necessário

## 🔧 Atualizar Frontend para usar API do domínio

Edite o arquivo `frontend/src/services/api.ts` (ou similar):

```typescript
// Antes (desenvolvimento local)
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Depois (produção com Cloudflare)
const API_BASE_URL = import.meta.env.PROD 
  ? 'https://api.smart-heaven.com/api/v1'  // Produção
  : 'http://localhost:8000/api/v1';         // Desenvolvimento
```

Ou use variáveis de ambiente no Vite:

**frontend/.env.production:**
```env
VITE_API_URL=https://api.smart-heaven.com/api/v1
```

**frontend/.env.development:**
```env
VITE_API_URL=http://localhost:8000/api/v1
```

## 📊 Verificando o funcionamento

### Testar o Tunnel

```bash
# Ver logs do cloudflared
sudo journalctl -u cloudflared -f

# Testar conectividade
curl https://api.smart-heaven.com/api/v1/health
```

### Testar o Frontend

Acesse no navegador:
- https://smart-heaven.com (Frontend)
- https://api.smart-heaven.com/docs (Swagger API)

## 🔒 Segurança Adicional (Recomendado)

### 1. Habilitar Cloudflare Access

Proteja o acesso com autenticação:

1. No dashboard Cloudflare, vá em **Access** > **Applications**
2. Clique em **Add an application**
3. Selecione **Self-hosted**
4. Configure:
   - **Application name:** Smart Heaven v2
   - **Subdomain:** smart-heaven
   - **Domain:** smart-heaven.com
5. Adicione regras de acesso (emails permitidos, etc.)

### 2. Firewall Rules

No Cloudflare Dashboard:
1. Vá em **Security** > **WAF**
2. Crie regras para proteger contra bots e ataques

### 3. Rate Limiting

1. Vá em **Security** > **Rate Limiting**
2. Crie regras para limitar requisições por IP

## 🔄 Migração do Smart Heaven v1 para v2

### Parar o antigo e iniciar o novo:

```bash
# 1. Para o Smart Heaven v1
bash /home/pedro/smart-heaven-v2/deploy/stop_old_sh.sh

# 2. Inicia o Smart Heaven v2
cd /home/pedro/smart-heaven-v2
docker-compose -f docker-compose.prod.yml up -d

# 3. O Cloudflare Tunnel automaticamente roteará para o novo serviço
# (porque o tunnel aponta para localhost:5173 e localhost:8000)
```

**Importante:** Não é necessário mudar configuração do Cloudflare se você mantiver as mesmas portas!

## 🆘 Troubleshooting

### Tunnel não conecta

```bash
# Ver logs
sudo journalctl -u cloudflared -f

# Reiniciar
sudo systemctl restart cloudflared

# Testar manualmente
cloudflared tunnel run smart-heaven-v2
```

### Erro 502 Bad Gateway

- Verifique se o Smart Heaven v2 está rodando: `docker ps`
- Verifique se as portas estão corretas no `config.yml`
- Teste localmente: `curl http://localhost:8000/api/v1/health`

### Tunnel desconecta frequentemente

Adicione ao `config.yml`:

```yaml
tunnel: <SEU_TUNNEL_ID>
credentials-file: /home/pedro/.cloudflared/<SEU_TUNNEL_ID>.json

# Configurações de reconnect
grace-period: 30s
retries: 5

ingress:
  # ... suas rotas ...
```

## 📚 Referências

- [Cloudflare Tunnel Docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [cloudflared GitHub](https://github.com/cloudflare/cloudflared)
- [Cloudflare Zero Trust](https://developers.cloudflare.com/cloudflare-one/)
