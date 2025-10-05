#!/bin/bash
# Clean restart - removes all volumes and data

echo "🧹 Clean Restart - This will DELETE all data!"
echo "=============================================="
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Cancelled"
    exit 0
fi

echo "🛑 Stopping all services..."
docker compose down -v

echo "📦 Rebuilding images..."
docker compose build

echo "🚀 Starting services with fresh data..."
docker compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "✅ Clean restart complete!"
echo ""
echo "📝 Check seed logs: docker logs backend-chromadb-seed-1"
echo "📝 Check backend logs: docker logs backend-backend-1"
