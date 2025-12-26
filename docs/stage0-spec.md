# Stage 0 Spec — PCG Arena Local Protocol (v0)

**Status:** ✅ COMPLETE (2025-12-24)

This document is the **technical specification** for Stage 0 implementation. It defines:
- the exact **API contract** (endpoints + request/response payloads),
- the **level format** (ASCII tilemap) with examples and validation rules,
- database technology choice and **persistence expectations**,
- invariants and failure modes so the backend, DB, and Java client can be developed independently.

**Protocol version:** `arena/v0`  
**Scope:** Local-only validation (Docker backend + persistent local DB + Java client)  
**Implementation:** ✅ All components complete and validated

**Note:** This spec remains the authoritative reference for protocol `arena/v0`, which is stable across all stages (0, 1, 2).

---

## 1. Stage 0 architecture and trust boundaries

Stage 0 comprises three components:

1) **Backend** (Docker container)  
- exposes HTTP API on localhost
- owns matchmaking, rating updates, storage writes, and validation

2) **Database** (persisted outside container)  
- durable store for levels, battles, votes, ratings
- must survive container restarts/rebuilds

3) **Java Client** (local executable)  
- requests battles and receives two levels
- renders levels, runs gameplay, collects vote/tags/telemetry
- submits votes and optionally shows leaderboard

### Trust model (Stage 0)
- Client is not trusted. Backend validates payloads and enforces invariants.
- Stage 0 assumes local execution, but still prevents obvious corruption:
  - battle IDs cannot be voted twice
  - vote submission is idempotent
  - backend rejects malformed levels/unknown generator IDs

### Implementation status

**All Stage 0 components:** ✅ COMPLETE (2025-12-24)

| Feature | Status | Location |
|---------|--------|----------|
| **Database schema** | ✅ Complete | `db/migrations/001_init.sql` |
| **Database indexes** | ✅ Complete | `db/migrations/002_indexes.sql` |
| **Migration runner** | ✅ Complete | `backend/src/db/migrations.py` |
| **SQLite persistence** | ✅ Complete | `db/local/arena.sqlite` |
| **Generator import** | ✅ Complete | `backend/src/db/seed.py` |
| **Level validation + import** | ✅ Complete | `backend/src/db/seed.py` |
| **Rating initialization** | ✅ Complete | `backend/src/db/seed.py` |
| **Health endpoint** | ✅ Complete | `backend/src/main.py` |
| **Leaderboard endpoint** | ✅ Complete | `backend/src/main.py` |
| **HTML leaderboard** | ✅ Complete | `backend/src/main.py` |
| **Battle creation** | ✅ Complete | `backend/src/main.py` |
| **Vote submission** | ✅ Complete | `backend/src/main.py` |
| **ELO rating update** | ✅ Complete | `backend/src/main.py` |
| **Debug endpoints** | ✅ Complete | `backend/src/main.py` |
| **Java client (Phases 1 & 2)** | ✅ Complete | `client-java/` |

**Stage 1 additions:** Backend deployed to GCP with CORS, rate limiting, admin endpoints, and backups (see `docs/stage1-spec.md`).

**Next stage:** Stage 2 — Browser frontend implementation (see `docs/stage2-spec.md`).

---

## 2. Database choice (Stage 0): SQLite

### Decision
**Use SQLite (single file DB) for Stage 0.**

### Rationale
Stage 0 has:
- low concurrency (single-digit users, often just you)
- small data volume (a few generators × ~100 levels each, plus votes)
- local-only deployment with minimal ops

SQLite gives:
- a single durable file that can be bind-mounted as a Docker volume
- ACID transactions (critical for atomic “vote + rating update”)
- simplicity (no extra service to run, no ports, no credentials)
- easy backups (copy the file)

### Constraints and future compatibility
- SQLite supports the invariants we need now.
- If later you move to Postgres for hosted stages, the data model and API can remain unchanged; only persistence changes.
- Stage 0 code should be written as if the DB is replaceable (clean persistence layer).

### Persistence requirement
The SQLite file **must live outside the container filesystem**:
- either a Docker named volume mounted into the container,
- or a bind-mounted host directory.

---

## 3. HTTP API (final contract)

### Base URL
Backend listens on:
- `http://localhost:8080` (default; configurable via env)

### Content type
- Requests and responses use `application/json; charset=utf-8`

### Protocol versioning
All responses MUST include:
- `protocol_version: "arena/v0"`

The client MUST refuse to proceed if:
- `protocol_version` is missing or not `"arena/v0"`.

### Error format (standard)
All non-2xx responses return JSON in this shape:

```json
{
  "protocol_version": "arena/v0",
  "error": {
    "code": "STRING_ENUM",
    "message": "Human readable message",
    "retryable": false,
    "details": { "optional": "object" }
  }
}
````

---

## 4. Endpoint: Health

### GET `/health`

**Purpose:** allow the client to confirm backend is reachable and protocol-compatible.

**Response 200**

```json
{
  "protocol_version": "arena/v0",
  "status": "ok",
  "server_time_utc": "2025-12-24T12:00:00Z",
  "build": {
    "git_sha": "optional",
    "backend_version": "0.1.0"
  }
}
```

---

## 5. Endpoint: Fetch next battle

### POST `/v1/battles:next`

**Purpose:** request the next comparison: two levels labeled `left` and `right`.

#### Request body

```json
{
  "client_version": "0.1.0",
  "session_id": "a3b5c2f0-2c39-4a2a-9fd3-6a8f6dd90e2b",
  "player_id": null,
  "preferences": {
    "mode": "standard"
  }
}
```

Field notes:

* `session_id` MUST be a UUID generated by client at startup.
* `player_id` is reserved for future. Stage 0 should send `null` or omit.
* `preferences.mode` is reserved; backend can ignore.

#### Response 200 (battle envelope)

```json
{
  "protocol_version": "arena/v0",
  "battle": {
    "battle_id": "btl_20251224_000001",
    "issued_at_utc": "2025-12-24T12:00:10Z",
    "expires_at_utc": null,
    "presentation": {
      "play_order": "LEFT_THEN_RIGHT",
      "reveal_generator_names_after_vote": true,
      "suggested_time_limit_seconds": 300
    },
    "left": {
      "level_id": "lvl_markov_v1_0007",
      "generator": {
        "generator_id": "markov_v1",
        "name": "Markov v1",
        "version": "1.0.0",
        "documentation_url": "https://example.com/markov"
      },
      "format": {
        "type": "ASCII_TILEMAP",
        "width": 150,
        "height": 16,
        "newline": "\n"
      },
      "level_payload": {
        "encoding": "utf-8",
        "tilemap": "....(see level format section; full 16 lines here)..."
      },
      "content_hash": "sha256:7f3f...ab",
      "metadata": {
        "seed": 7,
        "controls": {}
      }
    },
    "right": {
      "level_id": "lvl_ga_v1_0042",
      "generator": {
        "generator_id": "ga_v1",
        "name": "GA v1",
        "version": "1.0.0",
        "documentation_url": "https://example.com/ga"
      },
      "format": {
        "type": "ASCII_TILEMAP",
        "width": 150,
        "height": 16,
        "newline": "\n"
      },
      "level_payload": {
        "encoding": "utf-8",
        "tilemap": "....(16 lines)..."
      },
      "content_hash": "sha256:9a1c...d2",
      "metadata": {
        "seed": 42,
        "controls": {}
      }
    }
  }
}
```

#### Backend invariants for battle creation

* `left.generator.generator_id != right.generator.generator_id` (must be different generators)
* `left.level_id != right.level_id`
* The returned `tilemap` MUST validate according to the Level Format section.
* `battle_id` MUST be unique.
* Battle MUST be persisted as "ISSUED" before returning the response (so resubmission works).

#### Client expectations

* Client MUST present both levels in the specified `play_order`, unless the user chooses `SKIP`.
* Client MUST cache `battle_id` locally until it submits a vote.
* Client MUST treat `level_payload.tilemap` as authoritative, and not rewrite it.

#### Possible errors

* `NO_BATTLE_AVAILABLE` (retryable): not enough generators or levels loaded
* `INTERNAL_ERROR` (retryable): unexpected failure
* `UNSUPPORTED_CLIENT_VERSION` (non-retryable): incompatible client

---

## 6. Endpoint: Submit vote

### POST `/v1/votes`

**Purpose:** submit a single outcome for a previously issued battle.

#### Request body

```json
{
  "client_version": "0.1.0",
  "session_id": "a3b5c2f0-2c39-4a2a-9fd3-6a8f6dd90e2b",
  "battle_id": "btl_20251224_000001",
  "result": "LEFT",
  "left_tags": ["fun", "good_flow"],
  "right_tags": ["too_hard"],
  "telemetry": {
    "left": {
      "played": true,
      "duration_seconds": 63,
      "completed": false,
      "coins_collected": 3
    },
    "right": {
      "played": true,
      "duration_seconds": 70,
      "completed": true,
      "coins_collected": 5
    }
  }
}
```

#### `result` enum

* `LEFT`
* `RIGHT`
* `TIE`
* `SKIP`

Rules:

* `SKIP` is allowed even if the player didn't fully play both levels.
* If `result` is `LEFT/RIGHT/TIE`, the client SHOULD set `played=true` for both sides unless the user quit early; backend does not enforce but logs.

#### `tags` vocabulary (Stage 0)

Stage 0 supports a small fixed vocabulary. Unknown tags MUST be rejected (to keep data clean), returning `INVALID_TAG`.

**Note:** Tags are per-level. Each level (left and right) can have its own set of tags.

Allowed tags (initial):

* `fun`
* `boring`
* `good_flow`
* `creative`
* `unfair`
* `confusing`
* `too_hard`
* `too_easy`
* `not_mario_like`

You can evolve this list, but do so deliberately and version it in `docs/decisions.md`.

#### Response 200 (accepted)

```json
{
  "protocol_version": "arena/v0",
  "accepted": true,
  "vote_id": "v_20251224_000001",
  "leaderboard_preview": {
    "updated_at_utc": "2025-12-24T12:02:00Z",
    "generators": [
      {
        "generator_id": "markov_v1",
        "name": "Markov v1",
        "rating": 1012.4,
        "games_played": 5
      },
      {
        "generator_id": "ga_v1",
        "name": "GA v1",
        "rating": 987.6,
        "games_played": 5
      }
    ]
  }
}
```

#### Idempotency requirement

Votes MUST be idempotent with respect to `(session_id, battle_id)`:

* If the client retries submission due to a network error, backend MUST NOT double-count.
* If the same `(session_id, battle_id)` with identical payload arrives again, backend returns the same `vote_id` and `accepted=true`.
* If the same `(session_id, battle_id)` arrives with a different payload, backend returns `DUPLICATE_VOTE_CONFLICT`.

#### Backend atomicity requirement

Backend MUST perform these writes atomically in one transaction:

1. mark battle as `COMPLETED`
2. insert vote
3. update ratings (or enqueue and persist an event that deterministically updates ratings)

If the transaction fails, none of the changes apply.

#### Possible errors

* `BATTLE_NOT_FOUND` (non-retryable)
* `BATTLE_ALREADY_VOTED` (non-retryable)
* `DUPLICATE_VOTE_CONFLICT` (non-retryable)
* `INVALID_TAG` (non-retryable)
* `INVALID_PAYLOAD` (non-retryable)
* `INTERNAL_ERROR` (retryable)

---

## 7. Endpoint: Leaderboard

### GET `/v1/leaderboard`

**Purpose:** allow client and humans to inspect current generator ladder.

#### Response 200

```json
{
  "protocol_version": "arena/v0",
  "updated_at_utc": "2025-12-24T12:02:00Z",
  "rating_system": {
    "name": "ELO",
    "initial_rating": 1000,
    "k_factor": 24
  },
  "generators": [
    {
      "rank": 1,
      "generator_id": "markov_v1",
      "name": "Markov v1",
      "documentation-url": "https://example.com/markov",      
      "version": "1.0.0",
      "rating": 1012.4,
      "games_played": 5,
      "wins": 3,
      "losses": 2,
      "ties": 0,
      "skips": 0
    }
  ]
}
```

#### “Displayed on localhost by the backend”

Stage 0 additionally requires a simple human-readable view:

* Backend SHOULD serve a minimal page at `/` that renders the leaderboard.
* This is not required for client integration; it’s for convenience and debugging.

---

## 8. Level format: ASCII tilemap (final definition)

### Overview

Each level is a rectangle:

* `WIDTH`: variable, up to 250 characters (all lines must have the same width)
* `HEIGHT = 16`
* Exactly 16 lines separated by `\n`
* Each line has the same number of characters (1 to 250)
* No trailing spaces
* Final newline at end is optional but recommended

### Allowed tile characters (Stage 0)

Stage 0 defines a strict alphabet:

* `M` — Mario start position
* `F` — Level exit / flag position
* `y` — Spiky
* `Y` — Winged Spiky
* `E`, `g` — Goomba
* `G` — Winged Goomba
* `k` — Green Koopa
* `K` — Winged Green Koopa
* `r` — Red Koopa
* `R` — Winged Red Koopa
* `X` — Solid floor block
* `#` — Pyramid block
* `S` — Normal solid block
* `D` — Used block
* `%` — Jump-through platform
* `|` — Background for jump-through platform
* `?`, `@` — Question block (mushroom)
* `Q`, `!` — Question block (coin)
* `C` — Coin block
* `U` — Mushroom block
* `L` — 1-Up block
* `1` — Invisible 1-Up block
* `2` — Invisible coin block
* `o` — Free-standing coin
* `t` — Empty pipe (auto-detects shape)
* `T` — Flower pipe (may spawn enemy flower)
* `<` — Pipe top left
* `>` — Pipe top right
* `[` — Pipe body left
* `]` — Pipe body right
* `*` — Bullet Bill launcher body
* `B` — Bullet Bill head
* `b` — Bullet Bill neck/body

Rules:

* Any character outside this set is invalid.
* If `S` or `F` appear, they must appear at most once each.
* If absent, client uses default spawn and goal policy (defined in client implementation).

### Minimal semantic rules (Stage 0)

Stage 0 does not enforce full playability constraints, but the backend MUST enforce basic sanity:

* Valid dimensions and alphabet

### Example level (tiny excerpt for readability)

Below is an illustrative excerpt showing the **shape**. Seed levels are 200 characters wide; the schema allows any width from 1-250.

Line 1 (top row, mostly air):
`--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------`

A mid row with blocks and coins:
`------------------------------|%%%%%%%--------gg-----g----||||||||||%%%%%%%%%%%%|||||||||||------g----------------------------------%%%%%%%%%%%-----------------r---------k--%%%%%%%%-------------------`

Bottom row with ground:
`XXXXXX|||||XXXXXXXXXXXXXX----XXXXXXXXXXXX----XXXXXXXXXXXXX|||||||||||||||||||||||||||||||||-----XXXXXXXXXXX-----XXX----||||||||||||||||||||||||XXXXXXXXXXX---XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXFXX`

Full example:
```
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------CC2SSCC--------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------kgggkgkggkg------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------r------------------------------------------------------------------------------------------------------------------------------------
------------------------------%%%%------------------------%%%%%%%%%%------------%%%%%%%%%%%------------------------------------------------------USSSCC-------------------------------------------------
------------------------------||||------------------------||||||||||------------|||||||||||-------------------------------------------------------------------------------------------------------------
------------------------------|%%%%%%%--------gg-----g----||||||||||%%%%%%%%%%%%|||||||||||------g----------------------------------%%%%%%%%%%%-----------------r---------k--%%%%%%%%-------------------
------%%%%%-------------------||||||||--------------------|||||||||||||||||||||||||||||||||----------------------------%%%%%%%%%%%%%|||||||||||------------------------------||||||||-------------------
XXXXXX|||||XXXXXXXXXXXXXX----XXXXXXXXXXXX----XXXXXXXXXXXXX|||||||||||||||||||||||||||||||||-----XXXXXXXXXXX-----XXX----||||||||||||||||||||||||XXXXXXXXXXX---XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXFXX

```

## 9. Matchmaking (Stage 0 final behavior)

### Default (must implement)

* Uniformly sample two distinct generators from active set.
* Uniformly sample one level from each generator's pool.
* First sampled generator = left, second = right.
* Persist the battle before returning it.

### Optional enhancements (allowed but not required)

* Avoid repeating exact same (generatorA, generatorB, levelA, levelB) within a short window.
* Prefer near-rating opponents for more informative battles.

Stage 0 MUST remain deterministic enough for debugging:

* backend should log battle selection decisions (battle_id → chosen generators/levels).

---

## 10. Storage layout and ingestion (Stage 0)

### Generator metadata

Generators are defined in a seed file, e.g.:

* `db/seed/generators.json`

Each generator entry contains:

* `generator_id` (stable)
* `name`
* `version`
* `description`
* `tags` (list)
* `documentation_url`

### Level bundles

Levels are stored per generator, e.g.:

* `db/seed/levels/<generator_id>/`

Each level have to be:

* a `.txt` file containing the ASCII tilemap, or

Backend ingestion (Stage 0):

* on startup, backend reads generator metadata and level files
* validates each level against the Level Format rules
* inserts/upserts into SQLite

If any level is invalid, backend should fail fast with a clear error so the dataset is clean.

---

## 11. Rating system parameters (Stage 0)

Stage 0 uses Elo for simplicity.

Defaults:

* `initial_rating = 1000`
* `k_factor = 24`
* ties: count as 0.5–0.5 outcome
* skips: do not update ratings, but increment skip counters

These parameters must be included in `/v1/leaderboard` so clients and humans know what the numbers mean.

---

## 12. Observability and debugging (Stage 0)

Backend must log:

* every issued battle (battle_id, generator ids, level ids)
* every accepted vote (vote_id, battle_id, result, tags)
* any rejection reason with error code

Database should allow simple queries to answer:

* how many battles issued vs completed
* per-generator win/loss/tie/skip
* vote distribution (left/right bias detection)

---

## 13. Stage 0 acceptance tests (must-pass scenarios)

1. **Happy path** ✅ *Implemented*

* client fetches battle
* plays both
* submits vote
* leaderboard changes (for non-skip)

2. **Idempotency** ✅ *Implemented*

* submit the same vote twice due to simulated timeout
* backend returns accepted and does not double-update rating

3. **Duplicate conflict** ✅ *Implemented*

* submit a different vote for same battle_id
* backend rejects with `DUPLICATE_VOTE_CONFLICT`

4. **Persistence** ✅ *Implemented*

* Import seed data, restart backend container
* Leaderboard and generator counts remain unchanged

5. **Invalid level ingestion** ✅ *Implemented*

* Put an invalid character in a level file
* Backend fails startup with clear validation error message