#!/bin/bash
# View logs for specific service or all services

SERVICE=${1:-""}

if [ -z "$SERVICE" ]; then
    echo "📋 Viewing all service logs (press Ctrl+C to exit)..."
    docker compose logs -f
else
    echo "📋 Viewing logs for: $SERVICE (press Ctrl+C to exit)..."
    docker compose logs -f $SERVICE
fi
