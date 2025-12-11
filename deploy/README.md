# 📁 Scripts de Deploy - Smart Heaven v2

Esta pasta contém todos os scripts e configurações necessários para fazer o deploy do Smart Heaven v2 no Raspberry Pi e substituir a versão antiga.

## 📄 Arquivos

### Scripts de Shell

- **`stop_old_sh.sh`** - Para o Smart Heaven v1 (antigo)
- **`install_smartheaven_v2.sh`** - Instalação inicial completa do Smart Heaven v2
- **`deploy_to_raspberry.sh`** - Deploy/atualização rápida (git pull + rebuild)

### Configuração Systemd

- **`systemd/smartheaven-v2.service`** - Serviço systemd para inicialização automática
- **`systemd/README_SYSTEMD.md`** - Documentação do systemd

### Documentação

- **`MIGRATION_GUIDE.md`** - 📘 **COMECE AQUI!** Guia completo passo a passo
- **`CLOUDFLARE_SETUP.md`** - Configuração detalhada do Cloudflare Tunnel

## 🚀 Quick Start

### 1️⃣ Primeira Instalação (do zero)

Siga o guia completo: **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)**

### 2️⃣ Apenas Deploy/Atualização (se já está instalado)

```bash
# No Raspberry Pi
cd /home/pedro/smart-heaven-v2
bash deploy/deploy_to_raspberry.sh
```

## 📋 Ordem de Execução

Para uma migração completa do Smart Heaven v1 para v2:

1. **Parar v1**: Execute `stop_old_sh.sh`
2. **Instalar v2**: Execute `install_smartheaven_v2.sh`
3. **Configurar Systemd**: Siga `systemd/README_SYSTEMD.md`
4. **Configurar Cloudflare**: Siga `CLOUDFLARE_SETUP.md`

## 🔧 Como Usar os Scripts

### No Windows (PowerShell)

```powershell
# Transferir scripts para o Raspberry Pi
cd H:\vscode\smart-heaven-v2

# Transferir todos os scripts
scp -r deploy pedro@192.168.31.153:/home/pedro/smart-heaven-v2/
```

### No Raspberry Pi

```bash
# Tornar scripts executáveis
chmod +x /home/pedro/smart-heaven-v2/deploy/*.sh

# Executar script desejado
bash /home/pedro/smart-heaven-v2/deploy/install_smartheaven_v2.sh
```

## 📚 Documentação Detalhada

### Para Primeira Instalação

Leia: **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)**

Este guia contém:
- ✅ Pré-requisitos
- ✅ Passo a passo completo
- ✅ Comandos de teste
- ✅ Troubleshooting
- ✅ Próximos passos

### Para Cloudflare

Leia: **[CLOUDFLARE_SETUP.md](CLOUDFLARE_SETUP.md)**

Este guia contém:
- ✅ Instalação do cloudflared
- ✅ Configuração do Tunnel
- ✅ DNS setup
- ✅ Segurança adicional
- ✅ Troubleshooting

### Para Systemd

Leia: **[systemd/README_SYSTEMD.md](systemd/README_SYSTEMD.md)**

Este guia contém:
- ✅ Instalação do serviço
- ✅ Comandos úteis
- ✅ Logs e monitoramento
- ✅ Troubleshooting

## 🆘 Ajuda Rápida

### Verificar se Smart Heaven v2 está rodando

```bash
# Ver containers Docker
docker ps

# Ver status do serviço
sudo systemctl status smartheaven-v2

# Testar API
curl http://localhost:8000/api/v1/health
```

### Ver logs

```bash
# Logs do backend
cd /home/pedro/smart-heaven-v2
docker-compose -f docker-compose.prod.yml logs -f backend

# Logs do systemd
sudo journalctl -u smartheaven-v2 -f

# Logs do Cloudflare Tunnel
sudo journalctl -u cloudflared -f
```

### Reiniciar tudo

```bash
sudo systemctl restart smartheaven-v2
sudo systemctl restart cloudflared
```

## ⚠️ Notas Importantes

1. **Backup**: Sempre faça backup do banco de dados antes de migrations
2. **Portas**: O v2 usa as mesmas portas do MySQL (3306) e MQTT (1883) do v1
3. **Credenciais**: Verifique o arquivo `.env` no backend
4. **Cloudflare**: Mantenha o tunnel rodando como serviço systemd

## 🔗 Estrutura de Portas

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| Backend API | 8000 | FastAPI |
| Frontend | 5173 | Vite Dev Server |
| MySQL | 3306 | Banco de dados (externo) |
| MQTT | 1883 | Mosquitto (externo) |
| MQTT WebSocket | 9001 | WebSocket MQTT (externo) |

## 📞 Contato

Se encontrar problemas, verifique:
1. Logs dos containers
2. Logs do systemd
3. Conectividade com MySQL e MQTT
4. Status do Cloudflare Tunnel

---

**Boa sorte com o deploy! 🚀**
