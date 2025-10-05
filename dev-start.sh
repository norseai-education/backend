#!/bin/bash

# Development Environment Startup Script
# This script starts all NorseAI services in development mode

echo "🚀 Starting NorseAI in DEVELOPMENT mode..."
echo "📊 MongoDB: localhost:27019 (local Docker)"
echo "🔧 Environment: .env.dev"
echo ""

# Set environment variable and start services
export APP_ENV=dev

# Start all services
docker-compose up -d

echo ""
echo "✅ Development environment started!"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:6700"
echo "   API Docs: http://localhost:6700/docs"
echo "   MongoDB:  localhost:27019"
echo "   ChromaDB: localhost:8000"
echo "   Ollama:   localhost:11434"
echo ""
echo "🔍 Check status: docker-compose ps"
echo "📝 View logs: docker-compose logs -f"