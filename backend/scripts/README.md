# PCG Arena Demo Scripts

These scripts demonstrate the complete Stage 0 battle/vote flow using curl/HTTP requests.

## Prerequisites

- Backend running (via `docker compose up` or locally)
- `curl` installed (for bash script)
- PowerShell 5.1+ (for PowerShell script)
- Optional: `jq` for better JSON parsing in bash (if not available, basic parsing is used)

## Usage

### Bash (Linux/Mac/Docker)

```bash
# From repository root
./backend/scripts/demo.sh

# Or specify custom API URL
./backend/scripts/demo.sh http://localhost:8080
```

### PowerShell (Windows)

```powershell
# From repository root
.\backend\scripts\demo.ps1

# Or specify custom API URL
.\backend\scripts\demo.ps1 -ApiUrl http://localhost:8080
```

### Running in Docker Container

```bash
# Copy script into container and run
docker compose exec backend bash -c "cd /app && bash <(cat /dev/stdin)" < backend/scripts/demo.sh

# Or mount scripts directory and run
docker compose run --rm backend bash /scripts/demo.sh
```

## What the Script Does

1. **Checks backend health** - Verifies the API is reachable
2. **Shows initial leaderboard** - Displays starting ratings
3. **Loops 10 times:**
   - Fetches a new battle (`POST /v1/battles:next`)
   - Randomly selects LEFT, RIGHT, or TIE
   - Submits vote (`POST /v1/votes`)
   - Shows updated leaderboard
   - Waits 2 seconds before next iteration
4. **Shows final leaderboard** - Displays final ratings after all votes

## Expected Output

The script will:
- Create 10 battles
- Submit 10 votes (randomly LEFT/RIGHT/TIE)
- Show leaderboard changes after each vote
- Demonstrate that ratings update correctly
- Show that data persists (instructions provided for verification)

## Verification

After running the script, verify persistence:

```bash
# Stop backend
docker compose down

# Restart backend
docker compose up

# Check leaderboard (ratings should be preserved)
curl http://localhost:8080/v1/leaderboard
```

The leaderboard should show the same ratings as the final output from the demo script, proving that data persists across container restarts.

