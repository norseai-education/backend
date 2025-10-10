from langchain_ollama import OllamaLLM
from langchain_ollama import OllamaEmbeddings

# === MODELS ===
LOCAL = False

if not LOCAL:
    classifier_model = OllamaLLM(model="qwen3:30b-a3b-instruct-2507-q4_K_M"，base_url="http://host.docker.internal:11434")
    teacher_model = OllamaLLM(model="qwen3:30b-a3b-instruct-2507-q4_K_M"，base_url="http://host.docker.internal:11434")
    evaluator_model = OllamaLLM(model="qwen3:30b-a3b-instruct-2507-q4_K_M"，base_url="http://host.docker.internal:11434")
    
else:
    classifier_model = OllamaLLM(model="qwen3:4b")
    teacher_model = OllamaLLM(model="qwen3:4b")
    evaluator_model = OllamaLLM(model="qwen3:4b")

embedding_model = OllamaEmbeddings(model="nomic-embed-text:latest"，base_url="http://host.docker.internal:11434")

