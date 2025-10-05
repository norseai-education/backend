#!/bin/bash
# Start all services with fresh build

echo "🚀 Starting NorseAI Backend Services..."
echo "========================================"

# Build images
echo "📦 Building Docker images..."
docker compose build

# Start services
echo "🔧 Starting services..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Show status
echo ""
echo "✅ Services Status:"
docker compose ps

echo ""
echo "📊 Service URLs:"
echo "  Backend API:    http://localhost:6700"
echo "  ChromaDB:       http://localhost:8000"
echo "  PostgreSQL:     localhost:5433"
echo "  MongoDB:        localhost:27019"
echo "  Redis:          localhost:6379"
echo "  Ollama:         http://localhost:11434"

echo ""
echo "📝 Useful commands:"
echo "  View logs:      docker compose logs -f"
echo "  Stop services:  docker compose down"
echo "  Restart:        docker compose restart"
