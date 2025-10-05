#!/bin/bash
# Connect to Redis CLI

echo "📦 Connecting to Redis..."
docker compose exec redis redis-cli
