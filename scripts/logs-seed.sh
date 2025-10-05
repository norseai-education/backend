#!/bin/bash
# View ChromaDB seed logs (useful for debugging seeding issues)

echo "🌱 ChromaDB Seed Logs"
echo "====================="
echo ""

if docker ps -a | grep -q "chromadb-seed"; then
    docker logs backend-chromadb-seed-1
else
    echo "⚠️  chromadb-seed container not found"
    echo ""
    echo "Try running:"
    echo "  ./scripts/reseed.sh     # To run seeding"
    echo "  ./scripts/start.sh      # To start all services"
fi
