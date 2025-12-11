#!/bin/bash

echo "🔧 Corrigindo Smart Heaven v2 Backend..."
echo "=========================================="
echo ""

cd ~/smart-heaven-v2

# Parar e remover container atual
echo "⏹️  Parando container..."
docker-compose -f docker-compose.prod.yml down

echo ""
echo "🗑️  Removendo imagem antiga..."
docker rmi smart-heaven-v2_backend 2>/dev/null || echo "Imagem já removida"

echo ""
echo "🔨 Reconstruindo imagem com dependências corretas..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo ""
echo "🚀 Iniciando container..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "⏳ Aguardando 10 segundos..."
sleep 10

echo ""
echo "📋 Logs do container:"
docker logs smart-heaven-backend --tail 30

echo ""
echo "=========================================="
echo "🧪 Testando endpoints..."
echo ""

# Testar backend
echo "🔌 Testando Backend (porta 8000):"
curl -s http://localhost:8000/api/v1/health || echo "❌ Backend não respondeu"

echo ""
echo ""
echo "📊 Status do container:"
docker ps | grep smart-heaven

echo ""
echo "=========================================="
echo "✅ Processo concluído!"
