# PCG Arena Backend Scripts

This directory contains utility scripts for backup, restore, and testing.

## Backup Scripts

### `backup.sh` / `backup.ps1`

Creates a timestamped backup of the SQLite database and automatically rotates old backups.

**Linux/Mac:**
```bash
# Inside Docker container
./backend/scripts/backup.sh

# From host (via docker exec)
docker compose exec backend /app/scripts/backup.sh
```

**Windows:**
```powershell
# From host
.\backend\scripts\backup.ps1
```

**Configuration (Environment Variables):**
- `ARENA_BACKUP_PATH`: Backup directory (default: `/backups`)
- `ARENA_DB_PATH`: Database file path (default: `/data/arena.sqlite`)

**Features:**
- Creates timestamped backup: `arena_20251225_143022.sqlite`
- Keeps last 7 days of backups (configurable)
- Verifies backup was created successfully

---

### `restore.sh`

Restores the database from a backup file.

**Usage:**
```bash
# List available backups
./backend/scripts/restore.sh

# Restore from specific backup
./backend/scripts/restore.sh arena_20251225_143022.sqlite
```

**Safety:**
- Creates a safety backup of current database before restoring
- Requires backend restart after restore

---

## Automated Backups (Stage 1)

### Setup daily backups with cron

**On VM/server:**

1. Make script executable:
```bash
chmod +x /path/to/backup.sh
```

2. Add cron job (runs daily at 3 AM UTC):
```bash
crontab -e
# Add line:
0 3 * * * /path/to/backup.sh
```

3. Verify cron job:
```bash
crontab -l
```

### Setup daily backups on Windows

Use Windows Task Scheduler:

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 3:00 AM
4. Action: Start a program
   - Program: `powershell.exe`
   - Arguments: `-File C:\path\to\backup.ps1`
5. Save and test

---

## Demo Script

### `demo.ps1` / `demo.sh`

Runs 10 automated battles with random votes to test the complete flow.

**Usage:**
```powershell
# Windows
.\backend\scripts\demo.ps1

# With custom URL
.\backend\scripts\demo.ps1 -ApiUrl http://your-server:8080
```

```bash
# Linux/Mac
./backend/scripts/demo.sh

# With custom URL
./backend/scripts/demo.sh http://your-server:8080
```

---

## Testing

All scripts include error handling and verification:
- Exit with code 1 on failure
- Print clear success/error messages
- Verify operations completed successfully
