#!/bin/bash

# Start Ollama in the background
/bin/ollama serve &

# Wait for Ollama service to be ready
echo "Waiting for Ollama service to start..."
sleep 5

# Pull the models you need (add or remove models as needed)
echo "Pulling models..."
ollama pull qwen3:30b-a3b-instruct-2507-q4_K_M
ollama pull nomic-embed-text
# Add more models here:
# ollama pull phi3
# ollama pull gemma2
# ollama pull codellama

echo "Models pulled successfully!"
echo "Available models:"
ollama list

# Keep the container running
wait
