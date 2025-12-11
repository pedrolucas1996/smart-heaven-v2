#!/bin/bash
# Script de deploy do Smart Heaven v2 para Raspberry Pi

set -e  # Para em caso de erro

echo "========================================"
echo "Deploy Smart Heaven v2 para Raspberry Pi"
echo "========================================"

# Configurações
REPO_DIR="/home/pedro/smart-heaven-v2"
DEPLOY_USER="pedro"

echo "1. Atualizando código do repositório..."
cd "$REPO_DIR"
git fetch origin
git pull origin master

echo ""
echo "2. Parando containers antigos (se existirem)..."
docker-compose -f docker-compose.prod.yml down || true

echo ""
echo "3. Reconstruindo imagens Docker..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo ""
echo "4. Iniciando novos containers..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "5. Aguardando containers inicializarem..."
sleep 10

echo ""
echo "6. Executando migrations do banco de dados..."
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

echo ""
echo "7. Verificando status dos containers..."
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "8. Verificando logs recentes..."
docker-compose -f docker-compose.prod.yml logs --tail=20

echo ""
echo "========================================"
echo "✓ Deploy concluído com sucesso!"
echo "========================================"
echo ""
echo "Serviços disponíveis:"
echo "  - Backend API: http://192.168.31.153:8000"
echo "  - Frontend: http://192.168.31.153:5173"
echo "  - API Docs: http://192.168.31.153:8000/docs"
echo ""
echo "Para ver logs em tempo real:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
