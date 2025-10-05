#!/bin/bash
# Restart all services

echo "🔄 Restarting NorseAI Backend Services..."

# Restart all services
docker compose restart

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Show status
echo ""
echo "✅ Services Status:"
docker compose ps

echo ""
echo "📝 View logs: docker compose logs -f"
