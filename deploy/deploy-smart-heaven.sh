#!/bin/bash
set -euo pipefail

echo "🚀 Deploy Smart Heaven v2 - GitHub Actions"
echo "==========================================="
echo ""

cd ~/smart-heaven-v2

echo "📥 Pulling latest code..."
git fetch origin
git reset --hard origin/master

echo ""
echo "🛑 Stopping containers..."
docker-compose -f docker-compose.prod.yml down

echo ""
echo "🗑️ Cleaning old images..."
docker rmi -f smart-heaven-v2_backend 2>/dev/null || true

echo ""
echo "🔨 Building new image..."
if docker-compose -f docker-compose.prod.yml build --no-cache; then
    echo "✅ Build successful"
else
    echo "❌ ERROR: Docker build failed"
    exit 1
fi

echo ""
echo "🚀 Starting containers..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "⏳ Waiting 10 seconds for startup..."
sleep 10

echo ""
echo "📋 Container logs:"
docker logs smart-heaven-backend --tail 20

echo ""
echo "🧪 Testing backend..."
if curl -f -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "✅ Backend is responding!"
else
    echo "⚠️  Backend not responding yet (may still be starting)"
fi

echo ""
echo "📊 Container status:"
docker ps | grep smart-heaven

echo ""
echo "✅ Deploy completed successfully!"
