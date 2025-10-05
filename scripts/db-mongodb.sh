#!/bin/bash
# Connect to MongoDB database

echo "🍃 Connecting to MongoDB..."
docker compose exec mongodb mongosh amc8_database
