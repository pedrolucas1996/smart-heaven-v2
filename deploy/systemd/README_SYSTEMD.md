# Configuração do Systemd para Smart Heaven v2

Este guia explica como configurar o Smart Heaven v2 para iniciar automaticamente no boot do Raspberry Pi.

## Instalação do Serviço

1. **Copie o arquivo de serviço para o systemd:**
```bash
sudo cp /home/pedro/smart-heaven-v2/deploy/systemd/smartheaven-v2.service /etc/systemd/system/
```

2. **Recarregue o systemd:**
```bash
sudo systemctl daemon-reload
```

3. **Habilite o serviço para iniciar no boot:**
```bash
sudo systemctl enable smartheaven-v2.service
```

4. **Inicie o serviço agora:**
```bash
sudo systemctl start smartheaven-v2.service
```

## Comandos Úteis

### Ver status do serviço
```bash
sudo systemctl status smartheaven-v2.service
```

### Parar o serviço
```bash
sudo systemctl stop smartheaven-v2.service
```

### Reiniciar o serviço
```bash
sudo systemctl restart smartheaven-v2.service
```

### Ver logs do serviço
```bash
sudo journalctl -u smartheaven-v2.service -f
```

### Ver logs dos containers
```bash
cd /home/pedro/smart-heaven-v2
docker-compose -f docker-compose.prod.yml logs -f
```

### Desabilitar inicialização automática
```bash
sudo systemctl disable smartheaven-v2.service
```

## Verificando se está funcionando

Após iniciar o serviço, verifique:

1. **Status do systemd:**
```bash
sudo systemctl status smartheaven-v2.service
```

2. **Containers rodando:**
```bash
docker ps
```

Você deve ver os containers:
- `smart-heaven-backend`
- `smart-heaven-frontend` (se aplicável)

3. **Teste a API:**
```bash
curl http://localhost:8000/api/v1/health
```

## Troubleshooting

### Serviço não inicia

1. Verifique os logs:
```bash
sudo journalctl -u smartheaven-v2.service -n 50
```

2. Verifique se o Docker está rodando:
```bash
sudo systemctl status docker
```

3. Teste manualmente:
```bash
cd /home/pedro/smart-heaven-v2
docker-compose -f docker-compose.prod.yml up
```

### Permissões

Certifique-se de que o usuário `pedro` tem permissão para usar Docker:
```bash
sudo usermod -aG docker pedro
# Faça logout e login novamente
```

### Porta já em uso

Se a porta 8000 já estiver em uso, edite `docker-compose.prod.yml` e mude a porta do backend.
