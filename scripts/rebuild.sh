#!/bin/bash
# Rebuild Docker images without cache

echo "🔨 Rebuilding Docker Images (no cache)..."
echo "=========================================="

SERVICES=${1:-"backend chromadb-seed"}

echo "Rebuilding: $SERVICES"
echo ""

docker compose build --no-cache $SERVICES

echo ""
echo "✅ Rebuild complete!"
echo ""
echo "💡 Next steps:"
echo "  - Restart services: ./scripts/restart.sh"
echo "  - Clean restart: ./scripts/clean-restart.sh"
