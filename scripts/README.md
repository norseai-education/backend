# Backend Scripts

Utility scripts for managing the NorseAI backend services.

## Quick Start

```bash
# Make all scripts executable
chmod +x scripts/*.sh

# Start all services
./scripts/start.sh

# Check status
./scripts/status.sh

# View logs
./scripts/logs.sh
```

## Available Scripts

### Service Management

#### `start.sh`
Start all backend services with fresh build.

```bash
./scripts/start.sh
```

Features:
- Builds Docker images
- Starts all services
- Shows service status and URLs
- Displays useful commands

#### `stop.sh`
Stop all running services.

```bash
./scripts/stop.sh
```

#### `restart.sh`
Restart all services without losing data.

```bash
./scripts/restart.sh
```

#### `clean-restart.sh`
**⚠️ WARNING: Deletes all data!**

Complete restart with fresh volumes and data.

```bash
./scripts/clean-restart.sh
```

This will:
- Stop all services
- Remove all volumes (PostgreSQL, MongoDB, ChromaDB, Redis)
- Rebuild images
- Start services with fresh data
- Re-seed ChromaDB automatically

#### `status.sh`
Check the health of all services.

```bash
./scripts/status.sh
```

Shows:
- Docker container status
- API endpoint health checks
- Service connectivity

#### `logs.sh`
View service logs.

```bash
# All services
./scripts/logs.sh

# Specific service
./scripts/logs.sh backend
./scripts/logs.sh chromadb
./scripts/logs.sh chromadb-seed
./scripts/logs.sh ollama
```

### Data Management

#### `reseed.sh`
Re-seed ChromaDB collections with fresh data.

```bash
./scripts/reseed.sh
```

This will:
- Stop backend temporarily
- Clear ChromaDB data
- Run seed script
- Restart backend

#### `backup.sh`
Backup all databases to timestamped directory.

```bash
./scripts/backup.sh
```

Backs up:
- PostgreSQL (SQL dump)
- MongoDB (archive)
- ChromaDB (tar.gz)
- Redis (dump.rdb)

Backups saved to: `backups/YYYYMMDD_HHMMSS/`

### Development Tools

#### `rebuild.sh`
Rebuild Docker images without cache (useful after code changes).

```bash
# Rebuild backend and seed service
./scripts/rebuild.sh

# Rebuild specific services
./scripts/rebuild.sh backend
./scripts/rebuild.sh chromadb-seed
```

#### `run-seed-local.py`
Run the seed script locally (outside Docker) for development.

```bash
python3 scripts/run-seed-local.py
```

Requirements:
- ChromaDB running on localhost:8000
- Ollama running on localhost:11434
- Python dependencies installed

### Database Access

#### `db-postgres.sh`
Connect to PostgreSQL database.

```bash
./scripts/db-postgres.sh
```

Opens `psql` shell connected to `norsea_user_db`.

#### `db-mongodb.sh`
Connect to MongoDB database.

```bash
./scripts/db-mongodb.sh
```

Opens `mongosh` shell connected to `amc8_database`.

#### `db-redis.sh`
Connect to Redis CLI.

```bash
./scripts/db-redis.sh
```

Opens `redis-cli` for direct Redis access.

### Testing

#### `test-chat.sh`
Test chat endpoints end-to-end.

```bash
# Default student ID (123)
./scripts/test-chat.sh

# Custom student ID
./scripts/test-chat.sh 456
```

Tests:
1. Initialize chat session
2. Send message about fractions
3. Check chat status

#### `check-chromadb.sh`
Check ChromaDB collections and data counts.

```bash
./scripts/check-chromadb.sh
```

Shows:
- All collections
- Item counts per collection

#### `check-ollama.sh`
Check Ollama models and status.

```bash
./scripts/check-ollama.sh
```

Shows:
- Installed models
- Model details

## Common Workflows

### First Time Setup

```bash
# 1. Make scripts executable
chmod +x scripts/*.sh

# 2. Start all services
./scripts/start.sh

# 3. Wait a minute for seeding to complete

# 4. Check status
./scripts/status.sh

# 5. Test the system
./scripts/test-chat.sh
```

### After Code Changes

```bash
# 1. Rebuild changed services
./scripts/rebuild.sh backend

# 2. Restart services
./scripts/restart.sh

# 3. Check logs
./scripts/logs.sh backend
```

### Debugging Issues

```bash
# 1. Check service status
./scripts/status.sh

# 2. View logs
./scripts/logs.sh

# 3. Check ChromaDB data
./scripts/check-chromadb.sh

# 4. Check Ollama models
./scripts/check-ollama.sh

# 5. Test endpoints
./scripts/test-chat.sh
```

### Fresh Start (Clean Slate)

```bash
# ⚠️ WARNING: This deletes all data!
./scripts/clean-restart.sh
```

### Daily Development

```bash
# Start work
./scripts/start.sh

# Make code changes...

# Rebuild and test
./scripts/rebuild.sh backend
./scripts/restart.sh
./scripts/test-chat.sh

# End of day - stop services
./scripts/stop.sh
```

## Service URLs

After starting services with `./scripts/start.sh`:

- **Backend API**: http://localhost:6700
  - Docs: http://localhost:6700/docs
- **ChromaDB**: http://localhost:8000
- **PostgreSQL**: localhost:5433 (user: `postgres`)
- **MongoDB**: localhost:27019
- **Redis**: localhost:6379
- **Ollama**: http://localhost:11434

## Troubleshooting

### Scripts not executable

```bash
chmod +x scripts/*.sh
```

### Permission denied

```bash
# Run with sudo (if needed)
sudo ./scripts/start.sh
```

### Services not responding

```bash
# Check status
./scripts/status.sh

# View logs
./scripts/logs.sh

# Try clean restart
./scripts/clean-restart.sh
```

### ChromaDB not seeded

```bash
# Check seed logs
docker logs backend-chromadb-seed-1

# Re-seed manually
./scripts/reseed.sh
```

### Port already in use

```bash
# Check what's using the port
lsof -i :6700
lsof -i :8000
lsof -i :11434

# Stop the process or use different ports in docker-compose.yml
```

## File Permissions

All shell scripts should be executable:

```bash
chmod +x scripts/*.sh
```

Python scripts should be executable and have shebang:

```bash
chmod +x scripts/*.py
```

## Environment Variables

Scripts use these environment variables (with defaults):

- `OLLAMA_HOST`: Ollama API endpoint (default: `http://localhost:11434`)

Set in your shell or in `.env` file:

```bash
export OLLAMA_HOST=http://custom-host:11434
```

## Contributing

When adding new scripts:

1. Add to appropriate category in this README
2. Include usage examples
3. Document what the script does
4. Make it executable: `chmod +x scripts/your-script.sh`
5. Use consistent formatting and comments
6. Add error handling

## Notes

- All scripts assume you're in the `backend/` directory
- Docker Compose commands run against `docker-compose.yml` in current directory
- Scripts use `docker compose` (v2) not `docker-compose` (v1)
- Backup directory: `backend/backups/`
- Scripts are designed for development, not production use
