#!/bin/bash

echo "🔧 Rebuild COMPLETO do Smart Heaven v2 Backend"
echo "=============================================="
echo ""

cd ~/smart-heaven-v2

# Parar tudo
echo "⏹️  Parando containers..."
docker-compose -f docker-compose.prod.yml down -v

# Limpar completamente
echo "🗑️  Removendo imagens, volumes e cache..."
docker rmi -f smart-heaven-v2_backend 2>/dev/null || true
docker system prune -f

# Git pull para garantir código atualizado
echo "📥 Atualizando código do repositório..."
git pull origin master || echo "⚠️  Não foi possível atualizar via git"

# Rebuild SEM CACHE e SEM VOLUMES
echo ""
echo "🔨 Reconstruindo imagem (sem cache)..."
docker-compose -f docker-compose.prod.yml build --no-cache --pull

echo ""
echo "🚀 Iniciando container..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "⏳ Aguardando 15 segundos para startup..."
sleep 15

echo ""
echo "📋 Logs do container (últimas 50 linhas):"
docker logs smart-heaven-backend --tail 50

echo ""
echo "=========================================="
echo ""
echo "🧪 Testando Backend:"
curl -s http://localhost:8000/api/v1/health && echo "✅ Backend respondendo!" || echo "❌ Backend não respondeu"

echo ""
echo "=========================================="
echo "📊 Status final:"
docker ps | grep smart-heaven

echo ""
echo "✅ Processo concluído!"
echo ""
echo "💡 Se ainda não funcionar, execute:"
echo "   docker logs smart-heaven-backend"
