# PCG Arena — Backend Spec

**Location:** `./backend/spec.md`  
**Protocol:** `arena/v0`  
**Status:** ✅ Stage 0/1/2/3/4 Complete — Stable API with advanced matchmaking  
**Next:** Stage 5 — Research Analytics (see `docs/stage5-spec.md`)

This document describes the **backend implementation** for PCG Arena. The backend is a Python/FastAPI application serving the Arena API.

**Current deployment:** GCP Compute Engine (e2-micro) with Docker  
**Clients:** Java validation client (Stage 0/1), Browser frontend (Stage 2/3/4)  
**Key features:** 
- Core battle/voting API (Stage 0-2)
- Authentication system with Google OAuth and email/password (Stage 3)
- Builder profile for generator submissions (Stage 3)
- Glicko-2 rating system and AGIS matchmaking (Stage 4a)
- Admin dashboard and confusion matrix (Stage 4b)
- *(Stage 5 planned)* Enhanced telemetry, per-level stats, research data export

---

## 1) Overview

The backend is a **Python FastAPI application** that:
- Runs inside a Docker container
- Connects to a SQLite database (mounted volume)
- Applies database migrations on startup
- Imports seed data (generators and levels) on startup
- Serves HTTP API endpoints for health, leaderboard, and (future) battles/votes
- Provides an HTML leaderboard view

---

## 2) Directory structure

### Current tree (Stage 0 implementation)

```
backend/
├── spec.md                     # This file - backend specification
├── Dockerfile                  # Container build instructions
├── requirements.txt            # Python dependencies
├── config/
│   └── settings.env            # Environment variable defaults
├── src/                        # Python source code
│   ├── __init__.py             # Package marker with version info
│   ├── config.py               # Configuration loading from environment
│   ├── main.py                 # FastAPI application entry point
│   └── db/                     # Database module
│       ├── __init__.py         # Module exports
│       ├── connection.py       # SQLite connection management
│       ├── migrations.py       # Migration runner
│       └── seed.py             # Seed data importer + DB status
├── openapi/                    # (Placeholder) OpenAPI spec files
├── scripts/                    # (Placeholder) Dev/admin scripts
└── tests/                      # (Placeholder) Test suite
```

---

## 3) File descriptions

### Root files

| File | Purpose |
|------|---------|
| `Dockerfile` | Builds the container image: Python 3.12-slim, installs deps, copies source, runs `main.py` |
| `requirements.txt` | Python dependencies: FastAPI, Uvicorn, Pydantic |
| `spec.md` | This documentation file |

### `config/`

| File | Purpose |
|------|---------|
| `settings.env` | Default environment variables loaded by Docker Compose |

**Environment variables:**
- `ARENA_DB_PATH` — Path to SQLite database (default: `/data/arena.sqlite`)
- `ARENA_HOST` — Server bind address (default: `0.0.0.0`)
- `ARENA_PORT` — Server port (default: `8080`)
- `ARENA_INITIAL_RATING` — Starting Glicko-2 rating (default: `1000.0`)
- `ARENA_INITIAL_RD` — Initial rating deviation (default: `350.0`)
- `ARENA_INITIAL_VOLATILITY` — Initial volatility (default: `0.06`)
- `ARENA_MATCHMAKING_POLICY` — Matchmaking algorithm: `uniform_v0` or `agis_v1` (default: `agis_v1`)
- `ARENA_AGIS_MIN_GAMES` — Games before generator is "converged" (default: `30`)
- `ARENA_AGIS_TARGET_BATTLES_PER_PAIR` — Minimum battles per pair (default: `10`)
- `ARENA_AGIS_RATING_SIGMA` — Rating similarity standard deviation (default: `150.0`)
- `ARENA_AGIS_QUALITY_BIAS` — Quality bias strength (default: `0.2`)
- `ARENA_ADMIN_EMAILS` — Comma-separated admin emails (default: `antoni.krzysztof.czapski@gmail.com`)
- `ARENA_MIGRATIONS_PATH` — Path to migrations directory (default: `/migrations`)
- `ARENA_SEED_PATH` — Path to seed directory (default: `/seed`)

### `src/`

#### `src/__init__.py`
Package marker. Defines:
- `__version__ = "0.1.0"`
- `__protocol__ = "arena/v0"`

#### `src/config.py`
Configuration loader. Exports:
- `Config` dataclass — Holds all configuration values
- `load_config()` — Reads environment variables with defaults

#### `src/main.py`
FastAPI application entry point. Contains:

**Startup flow:**
1. `init_connection()` — Opens SQLite, enables foreign keys
2. `run_migrations()` — Applies pending SQL migrations
3. `import_generators()` — Upserts generators from JSON
4. `import_levels()` — Validates and upserts level files
5. `init_generator_ratings()` — Creates ratings rows for new generators
6. `log_db_status()` — Logs summary of DB state

**Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check, returns protocol version and server time |
| GET | `/v1/leaderboard` | JSON leaderboard: generators sorted by rating (Glicko-2) |
| GET | `/v1/generators/{generator_id}` | Get detailed generator info with all levels |
| GET | `/v1/stats/confusion-matrix` | Confusion matrix of generator pairwise comparisons (Stage 4b) |
| GET | `/v1/auth/me/admin` | Check if current user has admin privileges (Stage 4b) |
| GET | `/v1/admin/stats` | Admin statistics (requires OAuth admin auth, Stage 4b) |
| GET | `/` | HTML leaderboard page for humans |
| POST | `/v1/battles:next` | Issue a new battle using AGIS matchmaking (Stage 4a) |
| POST | `/v1/votes` | Submit vote for a battle, update Glicko-2 ratings (Stage 4a) |
| GET | `/debug/db-status` | Database status (requires `ARENA_DEBUG=true`) |
| GET | `/debug/battles` | List battles (requires `ARENA_DEBUG=true`) |
| GET | `/debug/votes` | List votes (requires `ARENA_DEBUG=true`) |
| GET | `/debug/matchmaking` | AGIS matchmaking stats (requires `ARENA_DEBUG=true`, Stage 4a) |
| GET | `/debug/pair-stats` | Generator pair statistics (requires `ARENA_DEBUG=true`, Stage 4a) |

### `src/db/`

Database module. All database operations are centralized here.

#### `src/db/__init__.py`
Module exports:
- `get_connection`, `init_connection` — Connection management
- `run_migrations` — Migration runner
- `import_generators`, `init_generator_ratings`, `import_levels` — Seed importers
- `log_db_status` — Status logging

#### `src/db/connection.py`
SQLite connection management. Provides:
- `init_connection(db_path)` — Opens connection, enables `PRAGMA foreign_keys = ON`, enables WAL mode
- `get_connection()` — Returns current connection
- `transaction()` — Context manager for atomic operations
- `close_connection()` — Cleanup

**Key behaviors:**
- Creates parent directories if needed
- Uses `sqlite3.Row` for dict-like row access
- Single global connection (sufficient for Stage 0)

#### `src/db/migrations.py`
Migration runner. Provides:
- `run_migrations(migrations_path)` — Applies all pending `.sql` files in order

**Key behaviors:**
- Sorts migrations lexicographically by filename
- Tracks applied migrations in `schema_migrations` table
- Special handling for first run (applies `001_init.sql` first to create `schema_migrations`)
- Each migration runs in a transaction
- Fails fast with clear error on any failure

#### `src/db/seed.py`
Seed data importer. Provides:

**Constants:**
- `MAX_LEVEL_WIDTH = 250` — Maximum level width
- `LEVEL_HEIGHT = 16` — Fixed level height
- `ALLOWED_TILES` — Set of valid tile characters

**Functions:**
- `import_generators(seed_path)` — Reads `generators.json`, upserts to `generators` table
- `init_generator_ratings(initial_rating)` — Creates `ratings` rows for generators without one
- `validate_level(content, filename)` — Validates tilemap, returns `(canonical_content, width)`
- `compute_content_hash(tilemap)` — Returns `sha256:<hex>` hash
- `import_levels(seed_path)` — Scans `levels/<gen_id>/*.txt`, validates, upserts to `levels` table
- `get_db_status(db_path)` — Returns dict with counts and metadata
- `log_db_status(db_path)` — Logs single-line summary

**Validation rules for levels:**
- Exactly 16 lines
- All lines same width (1-250 characters)
- Only allowed tile characters
- At least one `X` (ground block)
- Newlines normalized to `\n`

---

## 4) Docker configuration

### Dockerfile summary

```dockerfile
FROM python:3.12-slim
WORKDIR /app
# Install curl for healthcheck, Python deps
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./
ENV ARENA_DB_PATH=/data/arena.sqlite
ENV ARENA_MIGRATIONS_PATH=/migrations
ENV ARENA_SEED_PATH=/seed
EXPOSE 8080
CMD ["python", "main.py"]
```

### Volume mounts (from docker-compose.yml)

| Host path | Container path | Mode | Purpose |
|-----------|----------------|------|---------|
| `./db/local` | `/data` | rw | SQLite database persistence |
| `./db/migrations` | `/migrations` | ro | SQL migration scripts |
| `./db/seed` | `/seed` | ro | Seed data (generators.json, levels) |

---

## 5) Current system state

### Stage 0 Features (Complete)

| Feature | Status | Location |
|---------|--------|----------|
| Database migrations | ✅ Complete | `db/migrations.py` |
| Generator import | ✅ Complete | `db/seed.py` |
| Level import + validation | ✅ Complete | `db/seed.py` |
| Rating initialization | ✅ Complete | `db/seed.py` |
| Health endpoint | ✅ Complete | `main.py` |
| JSON leaderboard | ✅ Complete | `main.py` |
| HTML leaderboard | ✅ Complete | `main.py` |
| DB status logging | ✅ Complete | `db/seed.py` |
| Battle creation | ✅ Complete | `main.py` |
| Vote submission | ✅ Complete | `main.py` |
| ELO rating calculation | ✅ Complete | `main.py` |
| Debug endpoints | ✅ Complete | `main.py` |
| Foreign key enforcement | ✅ Complete | `db/connection.py` |

### Stage 1 Features (Complete)

| Feature | Status | Location |
|---------|--------|----------|
| CORS middleware | ✅ Complete | `main.py` |
| Environment configuration | ✅ Complete | `config.py` |
| Enhanced health check | ✅ Complete | `main.py` |
| Request logging | ✅ Complete | `middleware.py` |
| Rate limiting | ✅ Complete | `main.py` |
| Admin endpoints (5) | ✅ Complete | `main.py` |
| Bearer token auth | ✅ Complete | `main.py` |
| GCP deployment | ✅ Complete | Operational on e2-micro |
| Backup scripts | ✅ Complete | `scripts/backup.sh`, `scripts/backup.ps1` |
| Remote validation | ✅ Complete | Java client tested |

### Stage 4 Features (Complete)

| Feature | Status | Location |
|---------|--------|----------|
| Glicko-2 rating system | ✅ Complete | `glicko2.py`, `main.py` |
| AGIS matchmaking | ✅ Complete | `matchmaking.py`, `main.py` |
| Generator pair statistics | ✅ Complete | `main.py`, `db/migrations/007_glicko_matchmaking.sql` |
| Confusion matrix endpoint | ✅ Complete | `main.py` |
| Admin dashboard endpoints | ✅ Complete | `main.py` |
| Configurable AGIS parameters | ✅ Complete | `config.py` |
| Admin email configuration | ✅ Complete | `config.py` |

### Future Tasks

| Feature | Stage | Notes |
|---------|-------|-------|
| Browser frontend | Stage 2 | JavaScript/Canvas Mario game |
| Advanced matchmaking | Stage 3 | Uncertainty-aware pairing |
| Battle expiration | Stage 3 | Mark old battles as EXPIRED |
| OpenAPI spec | Stage 3 | Formal API documentation |
| Generator versioning | Stage 3 | Season archives, A/B testing |
| User accounts | Stage 4 | Authentication and profiles |

---

## 6) Testing

### Running tests locally

```powershell
cd backend
pip install pytest httpx
$env:PYTHONPATH = "src"
pytest tests -v
```

### Running tests in Docker

```bash
docker compose run --rm backend pytest tests -v
```

### Demo script

A scripted demo is available to test the complete battle/vote flow:

```bash
# Bash (Linux/Mac/Docker)
./backend/scripts/demo.sh

# PowerShell (Windows)
.\backend\scripts\demo.ps1
```

The demo script:
- Creates a session
- Fetches 10 battles (`POST /v1/battles:next`)
- Submits votes for each battle (`POST /v1/votes`)
- Shows leaderboard changes after each vote
- Waits 2 seconds between each iteration
- Demonstrates data persistence

See `backend/scripts/README.md` for details.

### Test coverage (Stage 0)

The test suite covers:

1. **Migrations and seed import** — Verify DB is populated correctly
2. **Battle creation** — Verify `/v1/battles:next` returns valid battles
3. **Rating updates** — Verify votes update ELO ratings correctly
4. **Idempotency** — Verify repeated identical votes don't double-update
5. **Conflict detection** — Verify different votes for same battle are rejected

---

## 6) API contract summary

### `GET /health`

Returns server status.

```json
{
  "protocol_version": "arena/v0",
  "status": "ok",
  "server_time_utc": "2025-12-24T12:00:00Z",
  "build": { "backend_version": "0.1.0" }
}
```

### `GET /v1/leaderboard`

Returns generator rankings.

```json
{
  "protocol_version": "arena/v0",
  "updated_at_utc": "2025-12-24T12:00:00Z",
  "rating_system": {
    "name": "Glicko-2",
    "initial_rating": 1000.0,
    "initial_rd": 350.0
  },
  "matchmaking_policy": "agis_v1",
  "generators": [
    {
      "rank": 1,
      "generator_id": "hopper",
      "name": "Hopper level generator",
      "version": "1.0.0",
      "documentation_url": "...",
      "rating": 1000.0,
      "games_played": 0,
      "wins": 0,
      "losses": 0,
      "ties": 0,
      "skips": 0
    }
  ]
}
```

### `GET /v1/generators/{generator_id}`

Returns detailed information about a specific generator including all its levels.

**Response 200:**
```json
{
  "protocol_version": "arena/v0",
  "generator_id": "hopper",
  "name": "Hopper Level Generator",
  "version": "1.0.0",
  "description": "Constructive left-to-right generator...",
  "tags": ["constructive", "probabilistic"],
  "documentation_url": "https://...",
  "is_active": true,
  "level_count": 100,
      "rating": 1024.5,
      "rd": 125.3,
      "games_played": 42,
      "wins": 20,
      "losses": 18,
      "ties": 4,
      "skips": 0,
  "created_at_utc": "2025-12-24T12:00:00Z",
  "updated_at_utc": "2025-12-28T15:30:00Z",
  "levels": [
    {
      "level_id": "hopper::lvl-1.txt",
      "content_format": "ASCII_TILEMAP",
      "width": 200,
      "height": 16,
      "tilemap_text": "--------------------...",
      "content_hash": "sha256:abc123...",
      "created_at_utc": "2025-12-24T12:00:00Z"
    }
  ]
}
```

**Response 404:** Generator not found

### `GET /`

Returns HTML page with styled leaderboard table.

### `POST /v1/battles:next`

Issues a new battle with two random levels from different generators.

**Request body:**
```json
{
  "client_version": "0.1.0",
  "session_id": "a3b5c2f0-2c39-4a2a-9fd3-6a8f6dd90e2b",
  "player_id": null,
  "preferences": { "mode": "standard" }
}
```

**Response 200:**
```json
{
  "protocol_version": "arena/v0",
  "battle": {
    "battle_id": "btl_...",
    "issued_at_utc": "2025-12-24T12:00:00Z",
    "expires_at_utc": null,
    "presentation": {
      "play_order": "LEFT_THEN_RIGHT",
      "reveal_generator_names_after_vote": true,
      "suggested_time_limit_seconds": 300
    },
    "left": { "level_id": "...", "generator": {...}, "format": {...}, "level_payload": {...} },
    "right": { "level_id": "...", "generator": {...}, "format": {...}, "level_payload": {...} }
  }
}
```

**Errors:** `NO_BATTLE_AVAILABLE`, `INVALID_PAYLOAD`, `INTERNAL_ERROR`

### `POST /v1/votes`

Submit a vote for a battle. Idempotent with atomic rating update.

**Request body:**
```json
{
  "client_version": "0.1.0",
  "session_id": "...",
  "battle_id": "btl_...",
  "result": "LEFT",
  "left_tags": ["fun", "good_flow"],
  "right_tags": ["too_hard"],
  "telemetry": { "left": {...}, "right": {...} }
}
```

**Response 200:**
```json
{
  "protocol_version": "arena/v0",
  "accepted": true,
  "vote_id": "v_...",
  "leaderboard_preview": {
    "updated_at_utc": "...",
    "generators": [...]
  }
}
```

**Errors:** `BATTLE_NOT_FOUND`, `BATTLE_ALREADY_VOTED`, `DUPLICATE_VOTE_CONFLICT`, `INVALID_TAG`, `INVALID_PAYLOAD`, `INTERNAL_ERROR`

Note: Vote result values are `LEFT`, `RIGHT`, `TIE`, or `SKIP`.

### `GET /v1/stats/confusion-matrix`

Returns confusion matrix of generator pairwise comparisons.

**Response 200:**
```json
{
  "protocol_version": "arena/v0",
  "generators": [
    {"id": "genetic", "name": "Grammatical Evolution Generator"},
    {"id": "hopper", "name": "Hopper Level Generator"}
  ],
  "matrix": [
    [null, {"battles": 15, "wins": 8, "losses": 5, "ties": 2, "win_rate": 0.533}],
    [{"battles": 15, "wins": 5, "losses": 8, "ties": 2, "win_rate": 0.333}, null]
  ],
  "coverage": {
    "total_pairs": 45,
    "pairs_with_data": 38,
    "pairs_at_target": 22,
    "target_battles_per_pair": 10,
    "coverage_percent": 84.4,
    "target_coverage_percent": 48.9
  }
}
```

### `GET /v1/auth/me/admin`

Check if current user has admin privileges.

**Response 200:**
```json
{
  "authenticated": true,
  "is_admin": true,
  "email": "admin@example.com"
}
```

### `GET /v1/admin/stats`

Get admin statistics for matchmaking and coverage. Requires OAuth authentication with admin email.

**Response 200:**
```json
{
  "protocol_version": "arena/v0",
  "user": {"email": "admin@example.com", "is_admin": true},
  "config": {
    "matchmaking_policy": "agis_v1",
    "initial_rating": 1000.0,
    "initial_rd": 350.0,
    "min_games_for_significance": 30,
    "target_battles_per_pair": 10,
    "rating_similarity_sigma": 150.0,
    "quality_bias_strength": 0.2
  },
  "matchmaking": { ... },
  "generators": [ ... ],
  "coverage_gaps": { ... }
}
```

**Response 401:** Not authenticated
**Response 403:** Not an admin user

### Debug Endpoints

These require `ARENA_DEBUG=true` environment variable.

- `GET /debug/db-status` — Table counts, last migration, DB file size
- `GET /debug/battles?status=ISSUED&limit=10` — List battles
- `GET /debug/votes?limit=10` — List votes

---

## 7) Development workflow

### Running locally (Docker)

```bash
docker compose up --build
```

### Running locally (Python, no Docker)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

$env:ARENA_DB_PATH = "..\db\local\arena.sqlite"
$env:ARENA_MIGRATIONS_PATH = "..\db\migrations"
$env:ARENA_SEED_PATH = "..\db\seed"

cd src
python main.py
```

### Resetting the database

Delete the SQLite file and restart:

```powershell
Remove-Item db\local\arena.sqlite
docker compose up --build
```

---

## 8) Architecture notes

### Design principles

1. **Single responsibility** — Each module has one clear purpose
2. **Fail fast** — Startup fails immediately on migration/validation errors
3. **Idempotency** — All seed operations are safe to repeat
4. **Explicit configuration** — All settings via environment variables
5. **Clean boundaries** — Database logic isolated in `db/` module

### Key invariants

1. **Foreign keys enforced** — `PRAGMA foreign_keys = ON` per connection
2. **One vote per battle** — Enforced by UNIQUE constraint on `votes.battle_id`
3. **Atomic updates** — Vote + rating update in single transaction
4. **Consistent widths** — All lines in a level must have same width

### Future considerations

- **Connection pooling** — Current single connection is fine for Stage 0
- **Async DB** — SQLite operations are sync; could use `aiosqlite` if needed
- **Caching** — Leaderboard could be cached for performance
- **Rate limiting** — Not needed for local-only Stage 0

