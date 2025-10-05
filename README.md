# NorseAI - AI Teacher Platform

A comprehensive AI-powered education platform featuring interactive learning, chat functionality, and advanced analytics. Built with modern web technologies and containerized for easy deployment.

## 🏗️ Architecture

This platform consists of multiple services running in Docker containers:

- **Frontend**: React application with Material-UI
- **Backend**: FastAPI server with Python
- **Database**: MongoDB for data persistence
- **Vector Database**: ChromaDB for embeddings and similarity search
- **AI Engine**: Ollama for local LLM inference

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### 1. Clone and Setup

```bash
# Clone the backend repository (contains docker-compose and all services)
git clone https://github.com/norseai-education/backend.git
cd backend

# Clone frontend repository as sibling
git clone https://github.com/norseai-education/frontend.git ../frontend
```

### 2. Environment Setup

```bash
# Copy environment files
cp .env.dev .env.dev.local
cp .env.prod .env.prod.local

# Edit with your database credentials (optional - defaults will work for local development)
nano .env.dev.local  # For development
nano .env.prod.local # For production (if deploying)
```

### 3. Start All Services

```bash
# Start all services (backend, frontend, MongoDB, ChromaDB, Ollama)
docker-compose up -d

# Or start specific services
docker-compose up -d backend frontend mongodb chromadb ollama
```

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:6700
- **API Documentation**: http://localhost:6700/docs
- **MongoDB**: localhost:27019
- **ChromaDB**: localhost:8000
- **Ollama API**: localhost:11434

## 🌍 Environment Configuration

The application supports both development and production environments with different database configurations.

### Development Environment (Default)

**Use Case**: Local development, testing, and debugging
- **MongoDB**: Local Docker instance (`mongodb://localhost:27019/amc8_database`)
- **Environment File**: `.env.dev`

```bash
# Quick start - use the convenience script
./dev-start.sh

# Or manually set environment and start
APP_ENV=dev docker-compose up -d

# Or start specific services
APP_ENV=dev docker-compose up -d backend frontend mongodb chromadb ollama
```

### Production Environment

**Use Case**: Live deployment with production database
- **MongoDB**: Remote server (`mongodb://172.16.0.177:27019`)
- **Environment File**: `.env.prod`

```bash
# Quick start - use the convenience script
./prod-start.sh

# Or manually set environment and start
APP_ENV=prod docker-compose up -d

# Or start specific services
APP_ENV=prod docker-compose up -d backend frontend mongodb chromadb ollama
```

### Environment Variables

Create the following `.env` files in the backend directory:

**Development (.env.dev)**:
```env
# Environment mode
APP_ENV=dev

# MongoDB connection for development (local Docker instance)
DEV_MONGODB_URL=mongodb://localhost:27019/amc8_database

# Database password (optional - used for PostgreSQL if configured)
DEV_DB_PASSWORD=my-dev-secure-password
```

**Production (.env.prod)**:
```env
# Environment mode
APP_ENV=prod

# MongoDB connection for production (remote server)
PROD_MONGODB_URL=mongodb://172.16.0.177:27019

# Database password (should be loaded from secure vault in production)
PROD_DB_PASSWORD=my-prod-very-secure-password-from-vault

# PostgreSQL host (if using PostgreSQL alongside MongoDB)
PROD_DB_HOST=prod-postgres-db.internal-network
```

### Creating Environment Files

```bash
# Copy the template files
cp .env.dev .env.dev.local    # For development overrides
cp .env.prod .env.prod.local  # For production overrides

# Edit with your specific values
nano .env.dev.local
nano .env.prod.local
```

**Security Note**: The `.env.dev.local` and `.env.prod.local` files are gitignored to prevent committing sensitive credentials. The template files (`.env.dev`, `.env.prod`) are tracked and contain example values.

**Note**: The application automatically loads `.env.dev` for development and `.env.prod` for production based on the `APP_ENV` variable.

#### Environment Variable Reference

- **`APP_ENV`**: Controls which environment file to load (`dev` or `prod`)
- **`DEV_MONGODB_URL`**: MongoDB connection string for development environment
- **`PROD_MONGODB_URL`**: MongoDB connection string for production environment  
- **`DEV_DB_PASSWORD` / `PROD_DB_PASSWORD`**: Database passwords (currently used for PostgreSQL if configured)
#### Service Configuration

The application uses the following default service connections (configured in Docker network):

- **ChromaDB**: `http://chromadb:8000` (vector database for embeddings)
- **Ollama**: `http://ollama:11434` (local LLM inference)
- **MongoDB**: Environment-specific URL from `.env.dev` or `.env.prod`
- **PostgreSQL**: `postgresql://user:password@host:5432/database` (if configured)

### Checking Current Environment

```bash
# Check which environment is running
docker-compose exec backend env | grep APP_ENV

# View MongoDB connection in logs
docker-compose logs backend | grep -i mongodb
```

**Note**: If `APP_ENV` is not set, the application defaults to development mode.

## 🤖 Ollama Setup

Ollama provides local LLM inference capabilities for your AI teacher platform.

### Running Ollama

```bash
# Start Ollama service
docker-compose up -d ollama

# Check Ollama status
docker-compose ps ollama

# View Ollama logs
docker-compose logs -f ollama
```

### Managing Models

```bash
# Pull a model (run inside Ollama container)
docker-compose exec ollama ollama pull qwen2:0.5b
docker-compose exec ollama ollama pull llama3.2:3b
docker-compose exec ollama ollama pull mistral:7b

# List available models
curl http://localhost:11434/api/tags

# Remove a model
docker-compose exec ollama ollama rm <model-name>
```

### Testing Ollama

```bash
# Test inference
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen2:0.5b", "prompt": "Hello, what is AI?", "stream": false}'

# Check running models
curl http://localhost:11434/api/ps
```

### Ollama in Backend Code

Your FastAPI backend can interact with Ollama using the service name:

```python
import requests

def query_ollama(prompt: str, model: str = "qwen2:0.5b"):
    response = requests.post("http://ollama:11434/api/generate",
                           json={"model": model, "prompt": prompt, "stream": false})
    return response.json()["response"]
```

## 🛠️ Development

### Local Development Setup

```bash
# Backend development
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 6700

# Frontend development
cd ../frontend
npm install
npm run dev
```

### Docker Commands

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
docker-compose restart ollama

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f ollama

# Clean up
docker-compose down -v  # Remove volumes too
docker system prune -a  # Remove unused images
```

### Service Management Scripts

Convenient scripts are provided in the backend directory:

```bash
# Environment-specific startup
./dev-start.sh      # Start in development mode
./prod-start.sh     # Start in production mode

# General management
./start.sh          # Start all services (uses default env)
./stop.sh           # Stop all services

# Service-specific restart
./restart_ollama.sh # Restart Ollama service
```

## 📊 Services Overview

### Backend (FastAPI)
- **Port**: 6700
- **Framework**: FastAPI with Python 3.11
- **Features**: REST API, WebSocket support, AI integration
- **Database**: MongoDB with Motor driver

### Frontend (React)
- **Port**: 5173 (maps to container port 80)
- **Framework**: React 18 with Vite
- **UI**: Material-UI with custom theming
- **Features**: Responsive design, real-time chat, admin dashboard

### Database Services
- **MongoDB**: Document database for user data and application state
- **ChromaDB**: Vector database for embeddings and semantic search

### AI Services
- **Ollama**: Local LLM inference with support for multiple models
- **Models**: Qwen2, Llama, Mistral, and other open-source models

## 🔧 Configuration

### Environment Variables

Create `.env` files in the backend directory:

**Backend (.env.dev/.env.prod)**:
```env
MONGODB_URL=mongodb://mongodb:27017/amc8_database
OLLAMA_URL=http://ollama:11434
CHROMADB_URL=http://chromadb:8000
```

### Docker Compose Configuration

The `docker-compose.yml` includes:
- Service networking with custom bridge network
- Volume persistence for databases and models
- Port mappings for local development
- Dependency management between services

## 📈 Monitoring & Debugging

```bash
# Health check
curl http://localhost:6700/health

# Backend logs
docker-compose logs -f backend

# Database status
docker-compose exec mongodb mongo --eval "db.stats()"

# Ollama status
curl http://localhost:11434/api/tags
```

## 🆘 Troubleshooting

### Common Issues

**Port conflicts**: Ensure ports 5173, 6700, 27019, 8000, 11434 are available

**Ollama model not found**: Pull the model first with `docker-compose exec ollama ollama pull <model>`

**Database connection issues**: Check MongoDB logs with `docker-compose logs mongodb`

**Build failures**: Clear Docker cache with `docker system prune -a`

### Getting Help

- Check service logs: `docker-compose logs <service-name>`
- Verify container status: `docker-compose ps`
- Test individual APIs: Use curl commands above
