#!/bin/bash
# Re-seed ChromaDB collections with fresh data

echo "🌱 Re-seeding ChromaDB Collections..."
echo "======================================"

# Stop backend to avoid conflicts
echo "🛑 Stopping backend..."
docker compose stop backend

# Remove ChromaDB data
echo "🧹 Clearing old ChromaDB data..."
docker compose stop chromadb
docker volume rm backend_chromadb_data 2>/dev/null || true

# Restart ChromaDB
echo "🚀 Starting ChromaDB..."
docker compose up -d chromadb

# Wait for ChromaDB to be ready
echo "⏳ Waiting for ChromaDB..."
sleep 5

# Run seed script
echo "🌱 Running seed script..."
docker compose up chromadb-seed

# Show seed logs
echo ""
echo "📋 Seed Logs:"
docker logs backend-chromadb-seed-1

# Restart backend
echo ""
echo "🚀 Starting backend..."
docker compose up -d backend

echo ""
echo "✅ Re-seeding complete!"
