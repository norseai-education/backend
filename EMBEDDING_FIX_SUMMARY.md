# ChromaDB Embedding Dimension Mismatch - RESOLVED ✅

## Problem Summary

After implementing the automated ChromaDB seeding system, we encountered a critical dimension mismatch error when the backend attempted to query seeded collections:

```
InvalidArgumentError' object is not subscriptable
```

**Root Cause**: The seed script was using ChromaDB's default embedding function (`all-MiniLM-L6-v2`) which produces 384-dimensional vectors, while the backend was using Ollama's `nomic-embed-text` model which produces different-dimensional vectors.

## Solution Implemented

Updated the seed script (`seed_chromadb.py`) to use Ollama embeddings matching the backend configuration.

### Key Changes

#### 1. Added Ollama Embedding Function
```python
def get_ollama_embedding_function():
    """Get Ollama embedding function for consistency with backend"""
    ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    
    # Wait for Ollama to be ready (60 retries, 2s intervals)
    # Verify nomic-embed-text model is available
    # Create OllamaEmbeddingFunction with model_name="nomic-embed-text"
```

**Features**:
- Waits up to 2 minutes for Ollama service to be ready
- Verifies `nomic-embed-text` model is available
- Gracefully falls back to default embeddings if Ollama unavailable
- Includes detailed logging for debugging

#### 2. Updated Collection Creation
```python
def create_collections(client, embedding_function=None):
    """Create required ChromaDB collections with specified embedding function"""
    # Creates collections with Ollama embedding function
    collection = client.create_collection(
        name=collection_name,
        embedding_function=embedding_function
    )
```

#### 3. Docker Compose Configuration
Added Ollama dependency to chromadb-seed service:

```yaml
chromadb-seed:
  build:
    context: ..
    dockerfile: backend/Dockerfile
  command: sh -c "cd /app/backend && python seed_chromadb.py"
  depends_on:
    - chromadb
    - ollama  # New dependency
  environment:
    - OLLAMA_HOST=http://ollama:11434  # New environment variable
  networks:
    - norsea-network
  restart: "no"
```

## Verification

### Seed Logs (Success)
```
Waiting for Ollama at http://ollama:11434...
✓ Ollama is ready!
✓ Found nomic-embed-text model in Ollama
✓ Using Ollama embeddings (nomic-embed-text)

Creating collections...
✓ Created collection 'AMC8_math'
✓ Created collection 'student_persona'
✓ Created collection 'math_related'
✓ Created collection 'AMC8_problems'
✓ Created collection 'conversation_history'
```

**Key Observations**:
- No download of `all-MiniLM-L6-v2` model (previous behavior)
- Ollama connection successful
- nomic-embed-text model verified
- Collections created with correct embeddings

### Backend Query Test (Success)
Test query: "Can you teach me about fractions?"

Backend logs show:
```
INFO:httpx:HTTP Request: POST http://ollama:11434/api/embed "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST http://chromadb:8000/api/v2/.../query "HTTP/1.1 200 OK"
INFO:backend.src.services.math_rag:Math rag result: ['Convert 0.75 to a fraction...']
```

**Key Observations**:
- ✅ Ollama embedding request successful
- ✅ ChromaDB query successful (no dimension mismatch error)
- ✅ RAG retrieved relevant seeded content
- ✅ End-to-end workflow functional

## Files Modified

1. **backend/seed_chromadb.py**
   - Added `get_ollama_embedding_function()`
   - Updated `create_collections()` to accept embedding_function parameter
   - Updated `main()` to call `get_ollama_embedding_function()`
   - Added imports: `os`, `embedding_functions` from chromadb.utils

2. **backend/docker-compose.yml**
   - Added `ollama` to chromadb-seed dependencies
   - Added `OLLAMA_HOST` environment variable

3. **backend/CHROMADB_SEEDING.md**
   - Updated troubleshooting section
   - Documented embedding alignment solution
   - Updated future improvements section

## Testing Procedure

To verify the fix works:

```bash
# 1. Clear old data and restart
cd backend
docker compose down -v

# 2. Rebuild images (important!)
docker compose build chromadb-seed backend

# 3. Start services
docker compose up -d postgres redis mongodb chromadb ollama chromadb-seed backend

# 4. Check seed logs
docker logs backend-chromadb-seed-1
# Should see: "✓ Using Ollama embeddings (nomic-embed-text)"

# 5. Test chat endpoint
curl -X POST http://localhost:6700/chat/init/123
curl -X POST http://localhost:6700/chat/s/123 \
  -H "Content-Type: application/json" \
  -d '{"message": "Can you teach me about fractions?"}'

# 6. Check backend logs for RAG success
docker logs backend-backend-1 | grep "Math rag result"
# Should see: retrieved content without errors
```

## Lessons Learned

1. **Embedding Consistency is Critical**: When seeding vector databases, always use the same embedding model that will be used at query time

2. **Service Dependencies Matter**: Seed script needs to wait for both ChromaDB AND Ollama to be ready

3. **Docker Build Cache**: After changing code, rebuild Docker images with `docker compose build` before testing

4. **Graceful Degradation**: Added fallback to default embeddings if Ollama unavailable, with clear logging

5. **Comprehensive Logging**: Detailed log messages make debugging much easier

## Impact

- ✅ RAG queries now work correctly with seeded data
- ✅ No dimension mismatch errors
- ✅ Consistent embedding model across seed and runtime
- ✅ Automated seeding system fully functional
- ✅ End-to-end chat workflow operational

## Next Steps

With the embedding alignment fixed, the system is ready for:
- Adding more realistic seed data
- Testing complex RAG queries
- Performance optimization
- Production deployment
