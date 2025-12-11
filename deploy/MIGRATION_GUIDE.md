# 🚀 Guia Completo: Migração do Smart Heaven v1 para v2 no Raspberry Pi

Este guia fornece um passo a passo completo para substituir o Smart Heaven antigo (v1) pelo novo Smart Heaven v2, incluindo configuração no Cloudflare.

## 📋 Pré-requisitos

- Raspberry Pi com SSH habilitado
- Acesso root/sudo
- Internet funcionando
- MySQL e Mosquitto MQTT já rodando (nas mesmas portas do v1)
- Domínio `smart-heaven.com` no Cloudflare

## 🎯 Visão Geral do Processo

1. **Parar** o Smart Heaven v1
2. **Instalar** dependências (Docker, etc)
3. **Clonar** e configurar Smart Heaven v2
4. **Iniciar** Smart Heaven v2
5. **Configurar** Cloudflare Tunnel
6. **Configurar** inicialização automática

---

## 🛠️ Passo 1: Conectar no Raspberry Pi

```bash
# Do seu computador Windows, conecte via SSH
ssh pedro@192.168.31.153
```

---

## ⛔ Passo 2: Parar o Smart Heaven v1

### 2.1. Transferir script de parada

**No Windows (PowerShell):**

```powershell
# Vá para o diretório do projeto
cd H:\vscode\smart-heaven-v2

# Transfira o script de parada
scp deploy/stop_old_sh.sh pedro@192.168.31.153:/home/pedro/
```

### 2.2. Executar no Raspberry Pi

**No Raspberry Pi:**

```bash
# Tornar executável
chmod +x /home/pedro/stop_old_sh.sh

# Executar
bash /home/pedro/stop_old_sh.sh
```

**Saída esperada:**
```
========================================
Parando Smart Heaven v1 (Antigo)
========================================
1. Parando servidor.py...
2. Parando serviço systemd (se existir)...
3. Verificando processos restantes...
   ✓ Nenhum processo do Smart Heaven v1 rodando
========================================
Smart Heaven v1 parado com sucesso!
========================================
```

---

## 📦 Passo 3: Instalar Dependências

### 3.1. Transferir script de instalação

**No Windows (PowerShell):**

```powershell
# Transferir script de instalação
scp deploy/install_smartheaven_v2.sh pedro@192.168.31.153:/home/pedro/
```

### 3.2. Editar configurações do script

**No Raspberry Pi:**

```bash
# Editar o script para ajustar a URL do repositório
nano /home/pedro/install_smartheaven_v2.sh
```

**Mude esta linha:**
```bash
REPO_URL="https://github.com/seu-usuario/smart-heaven-v2.git"  # AJUSTE AQUI
```

**Para:**
```bash
REPO_URL="/home/pedro/compartilhada/smart-heaven-v2"  # Caminho local
```

Ou se você tiver o repositório no GitHub:
```bash
REPO_URL="https://github.com/pedromenardi/smart-heaven-v2.git"
```

Salve com `Ctrl+X`, depois `Y`, depois `Enter`.

### 3.3. Executar instalação

```bash
# Tornar executável
chmod +x /home/pedro/install_smartheaven_v2.sh

# Executar
bash /home/pedro/install_smartheaven_v2.sh
```

Este script irá:
- ✅ Instalar Docker e Docker Compose
- ✅ Clonar/atualizar o repositório
- ✅ Criar arquivo `.env` com configurações
- ✅ Construir imagens Docker
- ✅ Iniciar containers
- ✅ Executar migrations do banco

**⏱️ Isso pode levar 5-10 minutos...**

---

## 🧪 Passo 4: Verificar Funcionamento

### 4.1. Verificar containers

```bash
cd /home/pedro/smart-heaven-v2
docker-compose -f docker-compose.prod.yml ps
```

**Você deve ver:**
```
NAME                      STATUS
smart-heaven-backend      Up
```

### 4.2. Testar a API

```bash
curl http://localhost:8000/api/v1/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "mqtt_connected": true,
  "database_connected": true
}
```

### 4.3. Ver logs

```bash
docker-compose -f docker-compose.prod.yml logs -f backend
```

Pressione `Ctrl+C` para sair.

---

## 🌐 Passo 5: Configurar Cloudflare Tunnel

### 5.1. Instalar cloudflared

```bash
# Baixar
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb

# Instalar
sudo dpkg -i cloudflared-linux-arm64.deb

# Verificar
cloudflared --version
```

### 5.2. Autenticar

```bash
cloudflared tunnel login
```

Copie a URL que aparecer e abra no navegador do seu computador. Faça login no Cloudflare e autorize.

### 5.3. Criar tunnel

```bash
cloudflared tunnel create smart-heaven-v2
```

**Anote o Tunnel ID** que aparecer!

### 5.4. Criar configuração

```bash
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

**Cole o seguinte** (substitua `<SEU_TUNNEL_ID>` pelo ID que você anotou):

```yaml
tunnel: <SEU_TUNNEL_ID>
credentials-file: /home/pedro/.cloudflared/<SEU_TUNNEL_ID>.json

ingress:
  # API Backend
  - hostname: api.smart-heaven.com
    service: http://localhost:8000
  
  # Frontend (se você adicionar depois)
  - hostname: smart-heaven.com
    service: http://localhost:5173
  
  # Catch-all
  - service: http_status:404
```

Salve com `Ctrl+X`, `Y`, `Enter`.

### 5.5. Configurar DNS

```bash
# API
cloudflared tunnel route dns smart-heaven-v2 api.smart-heaven.com

# Frontend principal
cloudflared tunnel route dns smart-heaven-v2 smart-heaven.com
```

### 5.6. Iniciar tunnel como serviço

```bash
# Instalar como serviço
sudo cloudflared service install

# Iniciar
sudo systemctl start cloudflared

# Habilitar no boot
sudo systemctl enable cloudflared

# Verificar status
sudo systemctl status cloudflared
```

---

## 🔄 Passo 6: Configurar Inicialização Automática do Smart Heaven v2

### 6.1. Transferir arquivo systemd

**No Windows (PowerShell):**

```powershell
scp deploy/systemd/smartheaven-v2.service pedro@192.168.31.153:/home/pedro/
```

### 6.2. Instalar serviço

**No Raspberry Pi:**

```bash
# Copiar para systemd
sudo cp /home/pedro/smartheaven-v2.service /etc/systemd/system/

# Recarregar
sudo systemctl daemon-reload

# Habilitar
sudo systemctl enable smartheaven-v2.service

# Iniciar
sudo systemctl start smartheaven-v2.service

# Verificar
sudo systemctl status smartheaven-v2.service
```

---

## ✅ Passo 7: Testar do Exterior

### 7.1. Testar API

**Do seu computador ou celular (fora da rede local):**

Abra no navegador:
```
https://api.smart-heaven.com/docs
```

Você deve ver a documentação Swagger da API!

### 7.2. Testar endpoint

```bash
curl https://api.smart-heaven.com/api/v1/health
```

---

## 🎉 Pronto!

Seu Smart Heaven v2 está rodando e acessível pela internet!

## 📝 Comandos Úteis

### Ver logs do backend

```bash
cd /home/pedro/smart-heaven-v2
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Reiniciar Smart Heaven v2

```bash
sudo systemctl restart smartheaven-v2.service
```

### Parar Smart Heaven v2

```bash
sudo systemctl stop smartheaven-v2.service
```

### Ver logs do Cloudflare Tunnel

```bash
sudo journalctl -u cloudflared -f
```

### Atualizar código (quando fizer mudanças)

```bash
cd /home/pedro/smart-heaven-v2
bash deploy/deploy_to_raspberry.sh
```

---

## 🆘 Troubleshooting

### Backend não inicia

```bash
# Ver logs detalhados
docker-compose -f docker-compose.prod.yml logs backend

# Verificar .env
cat backend/.env

# Testar conexão MySQL
mysql -h 192.168.31.153 -u pedro -p395967 -e "USE smartheaven; SHOW TABLES;"
```

### Cloudflare Tunnel não conecta

```bash
# Ver logs
sudo journalctl -u cloudflared -n 50

# Verificar config
cat ~/.cloudflared/config.yml

# Testar manualmente
cloudflared tunnel run smart-heaven-v2
```

### Erro 502 ao acessar

1. Verifique se o backend está rodando: `docker ps`
2. Teste localmente: `curl http://localhost:8000/api/v1/health`
3. Verifique logs do cloudflared: `sudo journalctl -u cloudflared -f`

---

## 📚 Próximos Passos

1. ✅ Configurar frontend (React)
2. ✅ Migrar dados do banco antigo (se necessário)
3. ✅ Testar automações com os ESPs
4. ✅ Configurar backups automáticos
5. ✅ Monitorar logs e métricas

---

## 🔗 Links Úteis

- Documentação do projeto: `H:\vscode\smart-heaven-v2\README.md`
- Systemd: `H:\vscode\smart-heaven-v2\deploy\systemd\README_SYSTEMD.md`
- Cloudflare: `H:\vscode\smart-heaven-v2\deploy\CLOUDFLARE_SETUP.md`
