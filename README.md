# WEB UI for norseai

**Setup to run locally on Ubuntu:**  
1. On terminal, set up a virtual environment: **python3 -m venv env_name**
2. Activate environment: **source env_name/bin/activate**  
3. Run **git clone https://github.com/Andrew-exe/norseai_code.git** to clone the repository  
4. Run **pip install -r requirements.txt** to install required dependencies  
5. Install Ollama: **curl -fsSL https://ollama.com/install.sh | sh** or download through windows: https://ollama.com/download/windows
6. Pull the required models from Ollama (using recommended smaller models for local, or model of your choice): **ollama pull qwen3:4b**  
7. Go to models.py (vim models.py in terminal) and change *LOCAL* to *True*  
8. Run python3 main.py (If port is taken, go to *main.py* and at the bottom change the port to your available port number)  
9. Go to LOCALHOST:port (default is 127.0.0.1:8001) to access the UI  

**Note**: Change *DEBUG_LEVEL* in utils.py to handle logging info
