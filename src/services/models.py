from langchain_ollama import ChatOllama, OllamaLLM
from langchain_ollama import OllamaEmbeddings

OLLAMA_BASE_URL = "http://host.docker.internal:11434"

# === MODELS ===
LOCAL = False

if not LOCAL:
    classifier_model = OllamaLLM(model="qwen3:30b-a3b-instruct-2507-q4_K_M", base_url=OLLAMA_BASE_URL)
    teacher_model = ChatOllama(model="qwen3:30b-a3b-instruct-2507-q4_K_M", base_url=OLLAMA_BASE_URL, streaming=True)
    evaluator_model = OllamaLLM(model="qwen3:30b-a3b-instruct-2507-q4_K_M", base_url=OLLAMA_BASE_URL)
    
else:
    classifier_model = OllamaLLM(model="qwen3:4b", base_url=OLLAMA_BASE_URL)
    teacher_model = ChatOllama(model="qwen3:4b", base_url=OLLAMA_BASE_URL, streaming=True)
    evaluator_model = OllamaLLM(model="qwen3:4b", base_url=OLLAMA_BASE_URL)

embedding_model = OllamaEmbeddings(model="nomic-embed-text:latest", base_url=OLLAMA_BASE_URL)
