from langchain_ollama import OllamaLLM
from langchain_ollama import OllamaEmbeddings
import os

# === OLLAMA CONFIGURATION ===
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://ollama:11434')

# === MODELS ===
LOCAL = True  # Set to True to use smaller local models

if not LOCAL:
    classifier_model = OllamaLLM(model="qwen3:30b-a3b-instruct-2507-q4_K_M", base_url=OLLAMA_BASE_URL)
    teacher_model = OllamaLLM(model="qwen3:30b-a3b-instruct-2507-q4_K_M", base_url=OLLAMA_BASE_URL)
    evaluator_model = OllamaLLM(model="qwen3:30b-a3b-instruct-2507-q4_K_M", base_url=OLLAMA_BASE_URL)
    
else:
    # Use available local models
    classifier_model = OllamaLLM(model="qwen2:0.5b", base_url=OLLAMA_BASE_URL)
    teacher_model = OllamaLLM(model="qwen2:0.5b", base_url=OLLAMA_BASE_URL)
    evaluator_model = OllamaLLM(model="qwen2:0.5b", base_url=OLLAMA_BASE_URL)

embedding_model = OllamaEmbeddings(model="nomic-embed-text:latest", base_url=OLLAMA_BASE_URL)