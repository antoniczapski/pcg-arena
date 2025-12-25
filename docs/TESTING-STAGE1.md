# Stage 1 Testing Guide

This guide explains how to test all Stage 1 features locally before deployment.

## Prerequisites

- Docker and Docker Compose installed
- Backend running: `docker compose up -d`
- PowerShell (Windows) or Bash (Linux/Mac)

---

## Quick Test (All Features)

**Windows:**
```powershell
.\backend\scripts\test-stage1.ps1
```

This script tests all Stage 1 features automatically and provides a summary.

---

## Manual Testing

### 1. Enhanced Health Check (S1-B3)

Test the new health check metrics:

```powershell
Invoke-RestMethod http://localhost:8080/health | ConvertTo-Json
```

**Expected output:**
```json
{
    "protocol_version": "arena/v0",
    "status": "ok",
    "metrics": {
        "uptime_seconds": 123,
        "requests_total": 10,
        "battles_served": 5,
        "votes_received": 3,
        "db_size_bytes": 233472
    },
    "config": {
        "public_url": "http://localhost:8080",
        "debug_mode": false
    }
}
```

---

### 2. CORS Headers (S1-B1)

CORS is enabled via FastAPI middleware. Test with browser or:

```powershell
$response = Invoke-WebRequest http://localhost:8080/health
$response.Headers["Access-Control-Allow-Origin"]
```

**Expected:** `*` (or configured origin)

---

### 3. Environment Configuration (S1-B2)

Environment variables can be set in `compose.yml`:

```yaml
environment:
  - ARENA_PUBLIC_URL=https://arena.example.com
  - ARENA_ALLOWED_ORIGINS=https://arena.example.com
  - ARENA_LOG_LEVEL=INFO
  - ARENA_ADMIN_KEY=your_secret_key
  - ARENA_BACKUP_PATH=/backups
```

---

### 4. Request Logging (S1-B4)

Check logs for request details:

```bash
docker compose logs backend --tail=20
```

**Expected log format:**
```
Request: method=POST path=/v1/battles:next status_code=200 duration_ms=45.23 request_id=abc123
```

---

### 5. Rate Limiting (S1-B5)

Rate limits are configured:
- `/v1/battles:next`: 10 requests/minute
- `/v1/votes`: 20 requests/minute

Test by making rapid requests (should get HTTP 429 after limit).

---

### 6. Admin Endpoints (S1-A1-A4)

Admin endpoints require `Authorization: Bearer <key>` header.

#### Test without key (should fail):
```powershell
Invoke-RestMethod -Uri http://localhost:8080/admin/generators/genetic/disable -Method Post
```

**Expected:** Error "Admin endpoints are disabled"

#### Set admin key in environment:
```yaml
# In compose.yml
environment:
  - ARENA_ADMIN_KEY=my_secret_key_123
```

Restart backend: `docker compose restart backend`

#### Test with key:

**Disable generator:**
```powershell
$headers = @{ Authorization = "Bearer my_secret_key_123" }
Invoke-RestMethod -Uri http://localhost:8080/admin/generators/genetic/disable -Method Post -Headers $headers | ConvertTo-Json
```

**Enable generator:**
```powershell
$headers = @{ Authorization = "Bearer my_secret_key_123" }
Invoke-RestMethod -Uri http://localhost:8080/admin/generators/genetic/enable -Method Post -Headers $headers | ConvertTo-Json
```

**Reset season:**
```powershell
$headers = @{ Authorization = "Bearer my_secret_key_123" }
Invoke-RestMethod -Uri http://localhost:8080/admin/season/reset -Method Post -Headers $headers | ConvertTo-Json
```

**Flag session:**
```powershell
$headers = @{ Authorization = "Bearer my_secret_key_123" }
$session = "session-id-here"
Invoke-RestMethod -Uri "http://localhost:8080/admin/sessions/$session/flag?reason=spam" -Method Post -Headers $headers | ConvertTo-Json
```

**Trigger backup:**
```powershell
$headers = @{ Authorization = "Bearer my_secret_key_123" }
Invoke-RestMethod -Uri http://localhost:8080/admin/backup -Method Post -Headers $headers | ConvertTo-Json
```

---

### 7. Backup System (S1-K1-K4)

#### Manual backup:
```powershell
# Windows
.\backend\scripts\backup.ps1

# Linux/Mac
./backend/scripts/backup.sh
```

**Expected output:**
```
Creating backup: arena_20251225_211611.sqlite
Backup created successfully: arena_20251225_211611.sqlite (0.22 MB)
Backup complete. Total backups: 2
```

#### List backups:
```powershell
Get-ChildItem db\backups\arena_*.sqlite
```

#### Test restore:
```bash
# Linux/Mac
./backend/scripts/restore.sh arena_20251225_211611.sqlite

# Then restart backend
docker compose restart backend
```

#### Setup automated backups (Linux/Mac):
```bash
# Add to crontab
crontab -e

# Add line (runs daily at 3 AM UTC):
0 3 * * * /path/to/backup.sh
```

---

## Integration Tests

### Test complete battle flow:

```powershell
# 1. Create battle
$session = [guid]::NewGuid().ToString()
$body = @{ client_version="0.1.0"; session_id=$session } | ConvertTo-Json
$battle = Invoke-RestMethod -Uri http://localhost:8080/v1/battles:next -Method Post -Body $body -ContentType "application/json"

Write-Host "Battle ID: $($battle.battle.battle_id)"
Write-Host "Left: $($battle.battle.left.generator.name)"
Write-Host "Right: $($battle.battle.right.generator.name)"

# 2. Submit vote
$voteBody = @{
    battle_id = $battle.battle.battle_id
    session_id = $session
    result = "LEFT"
} | ConvertTo-Json

$voteResponse = Invoke-RestMethod -Uri http://localhost:8080/v1/votes -Method Post -Body $voteBody -ContentType "application/json"
Write-Host "Vote accepted: $($voteResponse.accepted)"

# 3. Check leaderboard
$leaderboard = Invoke-RestMethod -Uri http://localhost:8080/v1/leaderboard
$leaderboard.generators | ForEach-Object {
    Write-Host "$($_.name): $([math]::Round($_.rating, 1)) ($($_.games_played) games)"
}
```

---

## Testing with Java Client

The Java client should work without modification:

```bash
cd client-java
./gradlew run
```

All Stage 1 changes are backward compatible with the Java client.

---

## Troubleshooting

### Logs show errors:
```bash
docker compose logs backend
```

### Backend not responding:
```bash
docker compose ps
docker compose restart backend
```

### Database issues:
```bash
# Check DB status (if debug mode enabled)
curl http://localhost:8080/debug/db-status
```

### Reset everything:
```bash
docker compose down -v
docker compose up --build -d
```

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `ARENA_DB_PATH` | `/data/arena.sqlite` | Database file path |
| `ARENA_HOST` | `0.0.0.0` | Bind address |
| `ARENA_PORT` | `8080` | HTTP port |
| `ARENA_PUBLIC_URL` | `http://localhost:8080` | Public URL |
| `ARENA_INITIAL_RATING` | `1000.0` | Starting ELO |
| `ARENA_K_FACTOR` | `24` | ELO K-factor |
| `ARENA_DEBUG` | `false` | Enable debug endpoints |
| `ARENA_ADMIN_KEY` | `` | Admin API key |
| `ARENA_ALLOWED_ORIGINS` | `*` | CORS allowed origins |
| `ARENA_LOG_LEVEL` | `INFO` | Logging level |
| `ARENA_BACKUP_PATH` | `/backups` | Backup directory |

---

## Success Criteria

All tests pass when:
- ✅ Enhanced health check shows metrics
- ✅ CORS headers present in responses
- ✅ Request logging visible in docker logs
- ✅ Admin endpoints reject unauthorized requests
- ✅ Admin endpoints accept requests with valid key
- ✅ Backup script creates timestamped backups
- ✅ Backup rotation keeps last 7 days
- ✅ Battle creation works
- ✅ Vote submission works
- ✅ Leaderboard updates correctly
- ✅ Java client connects successfully

---

**Stage 1 is ready for deployment when all tests pass!** 🚀

