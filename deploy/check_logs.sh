#!/bin/bash

echo "🔍 Verificando logs completos do container..."
echo "=============================================="
echo ""

docker logs smart-heaven-backend

echo ""
echo "=============================================="
echo ""
echo "🔌 Testando conectividade:"
echo ""

# Testar backend
echo "1. Testando localhost:8000..."
curl -v http://localhost:8000/api/v1/health 2>&1 | head -20

echo ""
echo ""
echo "2. Verificando se porta está aberta..."
sudo netstat -tulpn | grep 8000

echo ""
echo ""
echo "3. Testando de dentro do container..."
docker exec smart-heaven-backend curl -s http://localhost:8000/api/v1/health || echo "❌ Falhou"

echo ""
echo "=============================================="
