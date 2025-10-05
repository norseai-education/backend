#!/bin/bash
# Backup all databases

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"

echo "💾 Backing up databases..."
echo "=========================="
echo "Backup location: $BACKUP_DIR"
echo ""

mkdir -p "$BACKUP_DIR"

# Backup PostgreSQL
echo "📦 Backing up PostgreSQL..."
docker compose exec -T postgres pg_dump -U postgres norsea_user_db > "$BACKUP_DIR/postgres.sql"
echo "✅ PostgreSQL backup complete"

# Backup MongoDB
echo "📦 Backing up MongoDB..."
docker compose exec -T mongodb mongodump --db=amc8_database --archive > "$BACKUP_DIR/mongodb.archive"
echo "✅ MongoDB backup complete"

# Backup ChromaDB (copy volume data)
echo "📦 Backing up ChromaDB..."
docker run --rm -v backend_chromadb_data:/data -v "$(pwd)/$BACKUP_DIR":/backup alpine tar czf /backup/chromadb.tar.gz -C /data .
echo "✅ ChromaDB backup complete"

# Backup Redis
echo "📦 Backing up Redis..."
docker compose exec -T redis redis-cli SAVE > /dev/null
docker run --rm -v backend_redis_data:/data -v "$(pwd)/$BACKUP_DIR":/backup alpine cp /data/dump.rdb /backup/redis.rdb
echo "✅ Redis backup complete"

echo ""
echo "✅ All backups complete!"
echo "📂 Location: $BACKUP_DIR"
ls -lh "$BACKUP_DIR"
