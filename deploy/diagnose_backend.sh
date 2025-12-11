#!/bin/bash

echo "🔍 Diagnóstico do Smart Heaven v2 Backend"
echo "=========================================="
echo ""

# Verificar logs do container
echo "📋 Logs do container (últimas 50 linhas):"
docker logs smart-heaven-backend --tail 50

echo ""
echo "=========================================="
echo ""

# Verificar se o .env existe
echo "📄 Verificando arquivo .env:"
if [ -f ~/smart-heaven-v2/backend/.env ]; then
    echo "✅ Arquivo .env existe"
    echo ""
    echo "Conteúdo (sem senhas):"
    grep -v "PASSWORD\|SECRET\|APIKEY" ~/smart-heaven-v2/backend/.env | head -20
else
    echo "❌ Arquivo .env NÃO encontrado!"
fi

echo ""
echo "=========================================="
echo ""

# Verificar conectividade com banco de dados
echo "🗄️  Testando conexão com MySQL:"
mysql -h 192.168.31.153 -u pedro -p smartheaven -e "SELECT 'Conexão OK!' as status;" 2>&1 | head -5

echo ""
echo "=========================================="
echo ""

# Verificar portas em uso
echo "🔌 Portas 8000 e 5173 em uso:"
sudo netstat -tulpn | grep -E ":(8000|5173)" || echo "Nenhuma porta em uso"

echo ""
echo "=========================================="
echo ""

# Verificar docker-compose
echo "🐳 Configuração do Docker:"
cat ~/smart-heaven-v2/docker-compose.prod.yml

echo ""
echo "=========================================="
echo ""
echo "✅ Diagnóstico completo!"
