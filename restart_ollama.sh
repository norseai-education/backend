#!/bin/bash

# Script to restart the Ollama service

echo "Stopping Ollama service..."
docker-compose stop ollama

echo "Starting Ollama service..."
docker-compose up -d ollama

echo "Ollama service restarted successfully!"
echo "Ollama API available at: http://localhost:11434"