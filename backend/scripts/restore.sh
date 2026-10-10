#!/bin/bash
# PCG Arena - Database Restore Script (S1-K4)
# This script restores the database from a backup

set -e

# Configuration
BACKUP_DIR="${ARENA_BACKUP_PATH:-/backups}"
DB_PATH="${ARENA_DB_PATH:-/data/arena.sqlite}"

# Check if backup file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_filename>"
    echo ""
    echo "Available backups:"
    ls -lh "$BACKUP_DIR"/arena_*.sqlite 2>/dev/null || echo "  No backups found"
    exit 1
fi

BACKUP_FILE=$1
BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILE"

# Check if backup exists
if [ ! -f "$BACKUP_PATH" ]; then
    echo "ERROR: Backup file not found: $BACKUP_PATH"
    echo ""
    echo "Available backups:"
    ls -lh "$BACKUP_DIR"/arena_*.sqlite 2>/dev/null || echo "  No backups found"
    exit 1
fi

# Create a safety backup of current database
if [ -f "$DB_PATH" ]; then
    SAFETY_BACKUP="${DB_PATH}.pre-restore.$(date +%Y%m%d_%H%M%S)"
    echo "Creating safety backup of current database: $SAFETY_BACKUP"
    cp "$DB_PATH" "$SAFETY_BACKUP"
fi

# Restore database
echo "Restoring database from: $BACKUP_FILE"
cp "$BACKUP_PATH" "$DB_PATH"

# Verify restore
if [ -f "$DB_PATH" ]; then
    SIZE=$(du -h "$DB_PATH" | cut -f1)
    echo "Restore complete: $DB_PATH ($SIZE)"
    echo ""
    echo "IMPORTANT: Restart the backend to use the restored database:"
    echo "  docker compose restart backend"
else
    echo "ERROR: Restore failed"
    exit 1
fi

