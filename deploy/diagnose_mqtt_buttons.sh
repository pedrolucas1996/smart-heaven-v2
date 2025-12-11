#!/bin/bash

echo "🔍 Diagnóstico - Botões Físicos MQTT"
echo "====================================="
echo ""

# 1. Verificar se backend está rodando
echo "1️⃣ Status do Backend:"
docker ps | grep smart-heaven-backend

echo ""
echo "2️⃣ Logs do Backend (últimas 30 linhas):"
docker logs smart-heaven-backend --tail 30

echo ""
echo "3️⃣ Testando conexão MQTT do backend:"
docker logs smart-heaven-backend | grep -i mqtt | tail -10

echo ""
echo "4️⃣ Testando broker MQTT externo (192.168.31.153:1883):"
timeout 3 nc -zv 192.168.31.153 1883 2>&1 || echo "⚠️  Não conseguiu conectar ao broker MQTT"

echo ""
echo "5️⃣ Verificando tópicos MQTT configurados:"
docker exec smart-heaven-backend python -c "
from src.core.config import settings
print(f'MQTT Host: {settings.MQTT_BROKER_HOST}')
print(f'MQTT Port: {settings.MQTT_BROKER_PORT}')
print(f'Topic Button: {settings.MQTT_TOPIC_BUTTON}')
print(f'Topic Command: {settings.MQTT_TOPIC_COMMAND}')
print(f'Topic State: {settings.MQTT_TOPIC_STATE}')
" 2>&1 || echo "❌ Erro ao ler configuração"

echo ""
echo "6️⃣ Testando se o broker MQTT está recebendo mensagens:"
echo "   (Aperte um botão físico agora e veja se aparece mensagem)"
echo ""
timeout 10 mosquitto_sub -h 192.168.31.153 -t "casa/evento/botao" -v 2>&1 || echo "⚠️  mosquitto_sub não disponível ou sem mensagens"

echo ""
echo "====================================="
echo "✅ Diagnóstico completo!"
echo ""
echo "💡 Próximos passos:"
echo "   - Se backend está rodando mas MQTT não conecta: verificar firewall"
echo "   - Se tópicos estão errados: atualizar config.py"
echo "   - Se broker não responde: verificar Mosquitto no servidor"
