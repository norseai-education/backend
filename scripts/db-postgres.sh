#!/bin/bash
# Connect to PostgreSQL database

echo "🐘 Connecting to PostgreSQL..."
docker compose exec postgres psql -U postgres -d norsea_user_db
