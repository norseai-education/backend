#!/bin/bash

# Production Environment Startup Script
# This script starts all NorseAI services in production mode

echo "🚀 Starting NorseAI in PRODUCTION mode..."
echo "📊 MongoDB: 172.16.0.177:27019 (remote server)"
echo "🔧 Environment: .env.prod"
echo ""

# Set environment variable and start services
export APP_ENV=prod

# Start all services
docker-compose up -d

echo ""
echo "✅ Production environment started!"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:6700"
echo "   API Docs: http://localhost:6700/docs"
echo "   MongoDB:  172.16.0.177:27019"
echo "   ChromaDB: localhost:8000"
echo "   Ollama:   localhost:11434"
echo ""
echo "🔍 Check status: docker-compose ps"
echo "📝 View logs: docker-compose logs -f"
echo ""
echo "⚠️  WARNING: Ensure production MongoDB server is accessible!"