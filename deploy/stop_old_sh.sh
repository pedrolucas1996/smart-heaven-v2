#!/bin/bash
# Script para parar o Smart Heaven antigo (v1) no Raspberry Pi

echo "========================================"
echo "Parando Smart Heaven v1 (Antigo)"
echo "========================================"

# Para o processo servidor.py se estiver rodando
echo "1. Parando servidor.py..."
pkill -f "python.*servidor.py" || echo "   Nenhum processo servidor.py encontrado"

# Para o serviço systemd se existir
echo "2. Parando serviço systemd (se existir)..."
if systemctl list-units --type=service --all | grep -q "smartheaven.service\|smart-heaven.service"; then
    sudo systemctl stop smartheaven.service 2>/dev/null || true
    sudo systemctl stop smart-heaven.service 2>/dev/null || true
    sudo systemctl disable smartheaven.service 2>/dev/null || true
    sudo systemctl disable smart-heaven.service 2>/dev/null || true
    echo "   Serviços systemd parados e desabilitados"
else
    echo "   Nenhum serviço systemd encontrado"
fi

# Verifica se ainda há processos rodando
echo "3. Verificando processos restantes..."
if pgrep -f "servidor.py" > /dev/null; then
    echo "   AVISO: Ainda há processos servidor.py rodando!"
    echo "   Use: sudo pkill -9 -f servidor.py para forçar a parada"
else
    echo "   ✓ Nenhum processo do Smart Heaven v1 rodando"
fi

echo ""
echo "========================================"
echo "Smart Heaven v1 parado com sucesso!"
echo "========================================"
