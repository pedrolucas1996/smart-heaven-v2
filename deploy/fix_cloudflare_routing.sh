#!/bin/bash

# Script para corrigir o roteamento do Cloudflare Tunnel
# Garante que www.smart-heaven.com aponte para Smart Heaven v2

echo "🔧 Corrigindo configuração do Cloudflare Tunnel..."

# Backup da configuração atual
echo "📦 Fazendo backup da configuração atual..."
sudo cp ~/.cloudflared/config.yml ~/.cloudflared/config.yml.backup.$(date +%Y%m%d_%H%M%S)

# Atualizar o arquivo de configuração
echo "📝 Atualizando config.yml..."
sudo tee ~/.cloudflared/config.yml > /dev/null <<EOF
tunnel: 801fa731-1562-4f0a-a9ad-a0115b185ead
credentials-file: /home/pedro/.cloudflared/801fa731-1562-4f0a-a9ad-a0115b185ead.json

ingress:
  # Frontend principal - www.smart-heaven.com
  - hostname: www.smart-heaven.com
    service: http://localhost:5173
  
  # Frontend principal - smart-heaven.com (sem www)
  - hostname: smart-heaven.com
    service: http://localhost:5173
  
  # API Backend
  - hostname: api.smart-heaven.com
    service: http://localhost:8000
  
  # Catch-all rule (obrigatório)
  - service: http_status:404
EOF

echo "✅ Configuração atualizada!"

# Verificar se o serviço cloudflared existe
if systemctl list-unit-files | grep -q cloudflared.service; then
    echo "🔄 Reiniciando serviço cloudflared..."
    sudo systemctl restart cloudflared
    
    echo "📊 Status do serviço:"
    sudo systemctl status cloudflared --no-pager
    
    echo ""
    echo "📝 Logs recentes:"
    sudo journalctl -u cloudflared -n 20 --no-pager
else
    echo "⚠️  Serviço cloudflared não encontrado!"
    echo "Você pode iniciar o tunnel manualmente com:"
    echo "cloudflared tunnel run smart-heaven-v2"
fi

echo ""
echo "✅ Configuração aplicada!"
echo ""
echo "🌐 Agora www.smart-heaven.com deve apontar para:"
echo "   Frontend (React): http://localhost:5173"
echo "   API: http://localhost:8000"
echo ""
echo "⏳ Aguarde alguns minutos para a propagação do DNS..."
echo "🔍 Teste acessando: https://www.smart-heaven.com"
