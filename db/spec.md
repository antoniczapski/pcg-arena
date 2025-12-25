# PCG Arena — Database Spec (Stage 0)
**Location:** `./db/spec.md`  
**Protocol:** `arena/v0`  
**Scope:** Stage 0 (local-only): Dockerized backend + local persistent database + Java client.

This document defines the **database responsibilities** and the exact **data model** required to support Stage 0. It is written so the DB layer can be implemented independently from backend/client decisions, as long as the backend respects these storage contracts.

---

## 1) Purpose and non-negotiable requirements

### Primary purpose
Persist everything needed for the Arena loop:
1) Serve battles (two levels from two generators)
2) Accept a vote outcome (LEFT / RIGHT / TIE / SKIP)
3) Update and persist generator ratings
4) Survive backend container restarts and image rebuilds without losing state

### Non-negotiable requirements
- **Durability outside container:** the database file/data must be stored on a host-mounted volume or bind mount. Container rebuilds must not wipe data.
- **Atomicity:** vote insertion and rating update must be committed atomically (single transaction). No partial updates.
- **Idempotency support:** repeated submissions for the same battle must not double-count ratings.
- **Auditability:** the system must preserve enough history to reproduce the leaderboard and explain where it came from (at minimum, persist battles + votes).
- **Schema migrations:** database schema must be versioned and migratable using files in `./db/migrations`.

---

## 2) Database technology choice

### Stage 0 DB engine
**SQLite** is the recommended database for Stage 0.

Reasons:
- single-file persistence (easy volume mounting, easy backup)
- supports transactions and constraints needed for correctness
- low operational overhead (no separate DB process needed)

### Where the DB file lives
In Stage 0, we assume the backend container mounts a host directory (for example `./db/local/`) and stores the SQLite DB file there.

**Important:** `./db/local/` should be gitignored. Only schema + seed data belong in git.

---

## 3) Directory structure and file responsibilities

### Current tree (Stage 0 implementation)

```
db/
├── spec.md                     # This file - database specification
├── local/                      # Runtime database storage (gitignored)
│   └── arena.sqlite            # SQLite database file
├── migrations/                 # Ordered SQL migration scripts
│   ├── 001_init.sql            # Core tables: generators, levels, battles, votes, ratings, rating_events
│   └── 002_indexes.sql         # Performance indexes for all tables
└── seed/                       # Initial data for fresh database
    ├── generators.json         # Generator metadata (id, name, version, description, tags, url)
    └── levels/                 # Level files organized by generator
        ├── genetic/            # Levels for "genetic" generator
        │   ├── lvl-1.txt       # ASCII tilemap file (variable width x 16 lines)
        │   ├── lvl-2.txt
        │   └── ...
        ├── hopper/             # Levels for "hopper" generator
        │   └── ...
        └── notch/              # Levels for "notch" generator
            └── ...
```

### File descriptions

| Path | Purpose | Managed by |
|------|---------|------------|
| `spec.md` | Database schema specification and requirements | Human/docs |
| `local/` | Runtime SQLite storage, persists across container restarts | Backend (write), Docker volume mount |
| `local/arena.sqlite` | SQLite database file with all tables | Backend runtime |
| `migrations/` | SQL scripts applied in lexicographic order on startup | Backend migration runner |
| `migrations/001_init.sql` | Creates all 7 core tables with constraints | Backend migration runner |
| `migrations/002_indexes.sql` | Creates performance indexes | Backend migration runner |
| `seed/generators.json` | JSON array of generator metadata for upsert on startup | Backend seed importer |
| `seed/levels/<gen_id>/*.txt` | ASCII tilemap files, one level per file | Backend seed importer |

### `./db/migrations/`

Contains ordered, versioned migration scripts.

**Current migrations:**
- `001_init.sql` — Creates tables: `schema_migrations`, `generators`, `levels`, `battles`, `votes`, `ratings`, `rating_events`
- `002_indexes.sql` — Creates indexes for: `generators.is_active`, `levels.generator_id`, `levels.content_hash`, `battles.status`, `battles.session_id`, `battles.generator_pair`, `votes.created_at_utc`, `votes.session_id`

**Functional requirements:**
- Migrations run from scratch on empty DB
- Migrations run incrementally on existing DB
- Each migration is idempotent (uses `CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`)
- Backend tracks applied migrations in `schema_migrations` table

**Naming convention:** `NNN_description.sql` where NNN is a 3-digit sequence number.

### `./db/seed/`

Contains initial data (not code) to populate a fresh DB.

**Current structure:**
- `generators.json` — Defines 3 generators (hopper, genetic, notch)
- `levels/<generator_id>/lvl-N.txt` — 10 levels per generator (30 total)

**Functional requirements:**
- Seed import uses upsert logic (safe to run repeatedly)
- Generators must be imported before levels (foreign key constraint)
- Level files must pass validation (16 lines, width ≤ 250, valid tile alphabet)

### `./db/local/`

Runtime storage for the SQLite database file.

**Important:** This directory is gitignored. Only the `.gitkeep` placeholder is tracked.

**Docker mount:** `./db/local` → `/data` (read-write)

---

## 4) Entities and relationships (conceptual model)

Stage 0 requires these logical entities:

1) **Generator** — a PCG algorithm / model identity  
2) **Level** — a generated level artifact, attributed to a generator  
3) **Battle** — a single comparison instance: exactly one top level and one bottom level  
4) **Vote** — the user outcome for a battle (top/bottom/tie/skip) + optional tags/telemetry  
5) **Rating state** — current rating per generator (+ optional history)

Relationships:
- A generator has many levels.
- A battle references two levels (top and bottom).
- A vote references exactly one battle.
- Ratings are per generator and updated based on votes.

---

## 5) Schema requirements (tables, columns, constraints)

This section defines the **minimum schema**. You may add columns, but you must not remove required fields without updating the Stage 0 API spec.

### 5.1 Table: `generators`
Stores generator identities and metadata.

Required columns:
- `generator_id` (TEXT, PK)  
  Stable identifier (e.g., `markov_v1`, `ga_v1`).
- `name` (TEXT, NOT NULL)  
  Display name.
- `version` (TEXT, NOT NULL)  
  Human readable version string.
- `description` (TEXT, NOT NULL DEFAULT '')  
- `tags_json` (TEXT, NOT NULL DEFAULT '[]')  
  JSON array of strings. (SQLite has no strict JSON type; store as text.)
- `documentation_url` (TEXT, NULL)  
- `is_active` (INTEGER, NOT NULL DEFAULT 1)  
  1 = eligible for matchmaking, 0 = excluded.
- `created_at_utc` (TEXT, NOT NULL)  
  ISO timestamp.
- `updated_at_utc` (TEXT, NOT NULL)  
  ISO timestamp.

Constraints:
- `generator_id` unique and stable.
- `is_active` is 0/1.

Indexes:
- index on `is_active` for matchmaking.

---

### 5.2 Table: `levels`
Stores the level artifacts (Stage 0: ASCII tilemap).

Required columns:
- `level_id` (TEXT, PK)  
  Stable identifier (recommend deterministic naming, e.g., `lvl_<generator>_<nnnn>`).
- `generator_id` (TEXT, NOT NULL, FK -> generators.generator_id)
- `content_format` (TEXT, NOT NULL)  
  Must be `'ASCII_TILEMAP'` in Stage 0.
- `width` (INTEGER, NOT NULL)  
  Variable width, up to 250.
- `height` (INTEGER, NOT NULL)  
  Must be 16.
- `tilemap_text` (TEXT, NOT NULL)  
  The full 16-line ASCII tilemap payload.
- `content_hash` (TEXT, NOT NULL)  
  e.g., `sha256:<hex>` for dedup / integrity.
- `seed` (INTEGER, NULL)  
  Optional.
- `controls_json` (TEXT, NOT NULL DEFAULT '{}')  
  JSON object (future-friendly).
- `created_at_utc` (TEXT, NOT NULL)

Constraints:
- FK `generator_id` must exist.
- `width` must be between 1 and 250, `height` must be 16.
- `content_format` must be `ASCII_TILEMAP`.
- `content_hash` should be unique *per generator* (recommended) or globally unique (optional stricter).

Indexes:
- index on `generator_id`
- optional index on `content_hash`

---

### 5.3 Table: `battles`
Represents a served battle. A battle can be `ISSUED`, `COMPLETED`, or `EXPIRED`.

Required columns:
- `battle_id` (TEXT, PK)  
  Unique ID assigned by backend.
- `session_id` (TEXT, NOT NULL)  
  Client-provided UUID (anonymous session).
- `issued_at_utc` (TEXT, NOT NULL)
- `expires_at_utc` (TEXT, NULL)  
  Stage 0 can set null to mean “no expiry”.
- `status` (TEXT, NOT NULL)  
  Enum: `ISSUED`, `COMPLETED`, `EXPIRED`.
- `left_level_id` (TEXT, NOT NULL, FK -> levels.level_id)
- `right_level_id` (TEXT, NOT NULL, FK -> levels.level_id)
- `left_generator_id` (TEXT, NOT NULL, FK -> generators.generator_id)
- `right_generator_id` (TEXT, NOT NULL, FK -> generators.generator_id)
- `matchmaking_policy` (TEXT, NOT NULL DEFAULT 'uniform_v0')  
  For reproducibility / debugging.
- `created_at_utc` (TEXT, NOT NULL)
- `updated_at_utc` (TEXT, NOT NULL)

Constraints:
- `left_level_id != right_level_id`
- `left_generator_id != right_generator_id`
- `left_generator_id` must match the generator of `left_level_id`
- `right_generator_id` must match the generator of `right_level_id`

Note: SQLite cannot easily enforce “generator matches level” via FK alone; backend must enforce it, but you can add triggers if desired.

Indexes:
- index on `status`
- index on `session_id`
- index on `(left_generator_id, right_generator_id)` for analysis

---

### 5.4 Table: `votes`
Stores one vote per battle.

Required columns:
- `vote_id` (TEXT, PK)  
  Unique vote ID assigned by backend.
- `battle_id` (TEXT, NOT NULL, UNIQUE, FK -> battles.battle_id)  
  Enforces one vote per battle.
- `session_id` (TEXT, NOT NULL)  
  Must match battles.session_id (backend-enforced).
- `created_at_utc` (TEXT, NOT NULL)
- `result` (TEXT, NOT NULL)  
  Enum: `LEFT`, `RIGHT`, `TIE`, `SKIP`.
- `tags_json` (TEXT, NOT NULL DEFAULT '[]')  
  JSON array of allowed tags.
- `telemetry_json` (TEXT, NOT NULL DEFAULT '{}')  
  JSON object (client summary).

Constraints:
- Only one row per `battle_id`.
- `result` must be one of the 4 enums.

Idempotency requirement:
- Backend must treat `(session_id, battle_id)` as idempotency key:
  - if same payload repeats, return same vote_id
  - if different payload repeats, reject as conflict
DB support for this:
- `battle_id` UNIQUE ensures no double counting.
- backend may also add a `payload_hash` column to detect conflicting retries.

Recommended additional column:
- `payload_hash` (TEXT, NOT NULL)  
  Hash of canonical vote payload (battle_id+result+tags+telemetry) to detect conflicts.

Indexes:
- index on `created_at_utc`
- index on `session_id`

---

### 5.5 Table: `ratings`
Stores current rating state per generator.

Required columns:
- `generator_id` (TEXT, PK, FK -> generators.generator_id)
- `rating_value` (REAL, NOT NULL)
- `games_played` (INTEGER, NOT NULL)
- `wins` (INTEGER, NOT NULL)
- `losses` (INTEGER, NOT NULL)
- `ties` (INTEGER, NOT NULL)
- `skips` (INTEGER, NOT NULL)
- `updated_at_utc` (TEXT, NOT NULL)

Stage 0 defaults:
- initial rating = 1000.0
- `games_played/wins/...` start at 0

Constraints:
- counts must be non-negative.

---

### 5.6 Table: `rating_events` (recommended for auditability)
This is strongly recommended because it gives you a clear audit log and makes debugging dramatically easier.

Required columns:
- `event_id` (TEXT, PK)
- `vote_id` (TEXT, NOT NULL, UNIQUE, FK -> votes.vote_id)
- `battle_id` (TEXT, NOT NULL, FK -> battles.battle_id)
- `left_generator_id` (TEXT, NOT NULL)
- `right_generator_id` (TEXT, NOT NULL)
- `result` (TEXT, NOT NULL)
- `delta_left` (REAL, NOT NULL)
- `delta_right` (REAL, NOT NULL)
- `created_at_utc` (TEXT, NOT NULL)

Rules:
- exactly one rating_event per vote (UNIQUE on vote_id)
- used to reconstruct rating history if needed

If you want to keep Stage 0 minimal, you can omit `rating_events`, but then you lose most of your explainability.

---

## 6) Functional requirements for DB operations (what backend must be able to do)

### 6.1 Startup / ingestion
Backend must be able to:
- initialize schema (apply migrations)
- ingest seed data:
  - upsert generators
  - upsert levels (validate dimensions and allowed alphabet at ingestion time)
- initialize ratings:
  - ensure every active generator has a ratings row

### 6.2 Matchmaking queries
Backend must be able to:
- list active generators
- pick a random level for a generator efficiently
- create a battle row with status `ISSUED`

### 6.3 Vote submission transaction (critical path)
On vote submission, backend must execute a single transaction:
1) validate battle exists and is `ISSUED`
2) insert vote (enforcing one per battle)
3) update battle status to `COMPLETED`
4) update ratings and counters
5) insert rating_events (if enabled)

If any step fails, transaction rolls back.

### 6.4 Leaderboard query
Backend must be able to:
- return generators ordered by rating_value DESC, including counters and metadata
- do this quickly enough for “refresh on each vote”

### 6.5 Maintenance / debugging
Backend should be able to:
- mark generator inactive
- inspect battle/vote counts
- export votes and rating_events for analysis

---

## 7) Allowed tag vocabulary (enforced at DB boundary)

To keep your data clean, Stage 0 should enforce a fixed tag set.

Allowed tags:
- fun
- boring
- good_flow
- creative
- unfair
- confusing
- too_hard
- too_easy
- not_mario_like

DB expectation:
- votes.tags_json contains only tags from this set
- backend rejects invalid tags before insert

---

## 8) Schema versioning and migration plan

### Migration format
Stage 0 can use plain SQL migrations in `./db/migrations`.

Functional requirements:
- Each migration file must be applied once in order.
- Backend must track applied migrations in a table.

Required internal table:
- `schema_migrations(version TEXT PRIMARY KEY, applied_at_utc TEXT NOT NULL)`

Example workflow:
- On startup, backend checks `schema_migrations` and applies any missing migration files.

### Suggested migration sequence
- `001_init.sql` — create tables
- `002_indexes.sql` — create indexes
- `003_rating_events.sql` — optional audit table
- `004_constraints_triggers.sql` — optional triggers for stricter enforcement

---

## 9) Backups and restore (Stage 0)

Because this is a single local DB file:
- Backup is: copy the SQLite file while backend is stopped (or use SQLite backup API).
- Restore is: replace the file.

Stage 0 requirement:
- provide a simple documented way to make a backup before major changes.

---

## 10) Acceptance criteria (DB-specific)

The DB setup is “correct” when:

1) **Fresh start works**
- empty DB → apply migrations → import seed → backend can serve battles.

2) **Persistence works**
- stop backend container → restart → ratings/votes remain.

3) **Atomic vote update works**
- crash during vote submission must not leave DB in half-updated state.

4) **One vote per battle**
- attempting to insert second vote for same battle fails and does not change ratings.

5) **Referential integrity**
- battles cannot reference nonexistent levels
- levels cannot reference nonexistent generators


## 11) Implementation checklist for `./db`

To implement the DB layer in Stage 0, you need:

- [ ] Create `001_init.sql` defining tables:
  - generators, levels, battles, votes, ratings, schema_migrations
  - (recommended) rating_events
- [ ] Create `002_indexes.sql` with indexes listed above
- [ ] Define `seed/generators.json` and at least one generator + a few levels
- [ ] Add `seed/levels/<generator_id>/` with ASCII tilemap files
- [ ] Decide DB file location convention (e.g., `db/local/arena.sqlite`)
- [ ] Document how backend applies migrations and seed import
- [ ] Add a DB-level constraint or backend enforcement for:
  - one vote per battle
  - valid result enum
  - valid tag vocabulary

When these are done, the DB is ready for backend/client development.
