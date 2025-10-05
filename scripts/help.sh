#!/bin/bash
# Quick reference - displays available scripts and their descriptions

cat << 'EOF'
╔══════════════════════════════════════════════════════════════════╗
║              NorseAI Backend - Script Quick Reference            ║
╚══════════════════════════════════════════════════════════════════╝

📦 SERVICE MANAGEMENT
  ./scripts/start.sh              - Start all services
  ./scripts/stop.sh               - Stop all services  
  ./scripts/restart.sh            - Restart all services
  ./scripts/clean-restart.sh      - ⚠️  Clean restart (deletes data!)
  ./scripts/status.sh             - Check service health
  ./scripts/logs.sh [service]     - View logs
  ./scripts/logs-seed.sh          - View ChromaDB seed logs

🗄️  DATA MANAGEMENT
  ./scripts/reseed.sh             - Re-seed ChromaDB
  ./scripts/backup.sh             - Backup all databases
  ./scripts/check-chromadb.sh     - Check ChromaDB collections

🔧 DEVELOPMENT
  ./scripts/rebuild.sh [service]  - Rebuild Docker images
  ./scripts/run-seed-local.py     - Run seed script locally

💾 DATABASE ACCESS
  ./scripts/db-postgres.sh        - Connect to PostgreSQL
  ./scripts/db-mongodb.sh         - Connect to MongoDB
  ./scripts/db-redis.sh           - Connect to Redis

🧪 TESTING
  ./scripts/test-chat.sh [id]     - Test chat endpoints
  ./scripts/check-ollama.sh       - Check Ollama models

📚 HELP
  cat scripts/README.md           - Full documentation
  ./scripts/help.sh               - This reference

════════════════════════════════════════════════════════════════════

Quick Start:
  1. ./scripts/start.sh           # Start all services
  2. ./scripts/status.sh          # Check everything is running
  3. ./scripts/test-chat.sh       # Test the system

Service URLs:
  • Backend:    http://localhost:6700/docs
  • ChromaDB:   http://localhost:8000
  • Ollama:     http://localhost:11434

════════════════════════════════════════════════════════════════════
EOF
