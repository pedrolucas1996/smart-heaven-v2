#!/bin/bash
# Script de instalação inicial do Smart Heaven v2 no Raspberry Pi

set -e  # Para em caso de erro

echo "========================================"
echo "Instalação Smart Heaven v2 no Raspberry Pi"
echo "========================================"

# Configurações
REPO_URL="https://github.com/seu-usuario/smart-heaven-v2.git"  # AJUSTE AQUI
INSTALL_DIR="/home/pedro/smart-heaven-v2"
MYSQL_HOST="192.168.31.153"
MYSQL_USER="pedro"
MYSQL_PASS="395967"
MYSQL_DB="smartheaven"
MQTT_HOST="192.168.31.153"

echo "1. Verificando dependências..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "   Docker não encontrado. Instalando..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "   Docker instalado. IMPORTANTE: Faça logout e login novamente!"
else
    echo "   ✓ Docker já instalado"
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "   Docker Compose não encontrado. Instalando..."
    sudo apt-get update
    sudo apt-get install -y docker-compose
else
    echo "   ✓ Docker Compose já instalado"
fi

# Verificar Git
if ! command -v git &> /dev/null; then
    echo "   Git não encontrado. Instalando..."
    sudo apt-get update
    sudo apt-get install -y git
else
    echo "   ✓ Git já instalado"
fi

echo ""
echo "2. Clonando repositório..."
if [ -d "$INSTALL_DIR" ]; then
    echo "   Diretório já existe. Atualizando..."
    cd "$INSTALL_DIR"
    git pull
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo ""
echo "3. Criando arquivo .env para o backend..."
cat > backend/.env << EOF
# Database Configuration
DATABASE_URL=mysql+aiomysql://${MYSQL_USER}:${MYSQL_PASS}@${MYSQL_HOST}:3306/${MYSQL_DB}

# MQTT Configuration


# Application Settings
APP_NAME=Smart Heaven v2
APP_VERSION=2.0.0
ENVIRONMENT=production
LOG_LEVEL=INFO

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:5173","http://192.168.31.153:5173","http://smart-heaven.com","https://smart-heaven.com"]

# CallMeBot (WhatsApp Notifications)
CALLMEBOT_PHONE=+5515996895395
CALLMEBOT_APIKEY=8548044
EOF

echo "   ✓ Arquivo .env criado"

echo ""
echo "4. Verificando conectividade com MySQL..."
if mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASS" -e "USE $MYSQL_DB;" 2>/dev/null; then
    echo "   ✓ Conexão com MySQL OK"
else
    echo "   ⚠ Erro ao conectar com MySQL. Verifique as credenciais!"
    echo "   Continuando mesmo assim..."
fi

echo ""
echo "5. Construindo imagens Docker..."
docker-compose -f docker-compose.prod.yml build

echo ""
echo "6. Iniciando containers..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "7. Aguardando containers inicializarem..."
sleep 15

echo ""
echo "8. Executando migrations do banco de dados..."
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

echo ""
echo "9. Verificando status..."
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "========================================"
echo "✓ Instalação concluída com sucesso!"
echo "========================================"
echo ""
echo "Próximos passos:"
echo "1. Acesse http://${MYSQL_HOST}:8000/docs para ver a API"
echo "2. Acesse http://${MYSQL_HOST}:5173 para o frontend"
echo "3. Configure o Cloudflare Tunnel (veja CLOUDFLARE_SETUP.md)"
echo ""
echo "Comandos úteis:"
echo "  - Ver logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  - Parar: docker-compose -f docker-compose.prod.yml down"
echo "  - Reiniciar: docker-compose -f docker-compose.prod.yml restart"
