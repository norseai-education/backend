#!/bin/bash
# Stop all services

echo "🛑 Stopping NorseAI Backend Services..."
docker compose down

echo "✅ All services stopped"
