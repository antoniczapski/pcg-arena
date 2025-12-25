#!/bin/bash
# PCG Arena - Database Backup Script (S1-K1)
# This script creates a timestamped backup of the SQLite database

set -e

# Configuration
BACKUP_DIR="${ARENA_BACKUP_PATH:-/backups}"
DB_PATH="${ARENA_DB_PATH:-/data/arena.sqlite}"
KEEP_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="arena_${TIMESTAMP}.sqlite"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILE"

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo "ERROR: Database file not found: $DB_PATH"
    exit 1
fi

# Create backup
echo "Creating backup: $BACKUP_FILE"
cp "$DB_PATH" "$BACKUP_PATH"

# Verify backup
if [ -f "$BACKUP_PATH" ]; then
    SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
    echo "Backup created successfully: $BACKUP_FILE ($SIZE)"
else
    echo "ERROR: Backup failed"
    exit 1
fi

# S1-K3: Rotate backups - keep only last N days
echo "Rotating backups (keeping last $KEEP_DAYS days)..."
find "$BACKUP_DIR" -name "arena_*.sqlite" -type f -mtime +$KEEP_DAYS -delete

# Count remaining backups
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "arena_*.sqlite" -type f | wc -l)
echo "Backup complete. Total backups: $BACKUP_COUNT"

