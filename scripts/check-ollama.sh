#!/bin/bash
# Check Ollama models and status

echo "🤖 Ollama Status"
echo "================"
echo ""

echo "📋 Installed Models:"
curl -s http://localhost:11434/api/tags | python3 -m json.tool

echo ""
echo "💾 Model Details:"
echo "  qwen2:0.5b - Language Model"
echo "  nomic-embed-text - Embedding Model"

echo ""
