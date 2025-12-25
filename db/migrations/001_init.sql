-- PCG Arena Stage 0 - Initial Schema Migration
-- Protocol: arena/v0
-- This migration creates all core tables for the Arena system.

-- Enable foreign key enforcement (must be run per connection in SQLite)
PRAGMA foreign_keys = ON;

--------------------------------------------------------------------------------
-- schema_migrations: Track applied migrations
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at_utc TEXT NOT NULL
);

--------------------------------------------------------------------------------
-- generators: PCG algorithm/model identities
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS generators (
    generator_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    tags_json TEXT NOT NULL DEFAULT '[]',
    documentation_url TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at_utc TEXT NOT NULL,
    updated_at_utc TEXT NOT NULL,

    -- Constraints
    CHECK (is_active IN (0, 1))
);

--------------------------------------------------------------------------------
-- levels: Generated level artifacts (ASCII tilemaps)
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS levels (
    level_id TEXT PRIMARY KEY,
    generator_id TEXT NOT NULL,
    content_format TEXT NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    tilemap_text TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    seed INTEGER,
    controls_json TEXT NOT NULL DEFAULT '{}',
    created_at_utc TEXT NOT NULL,

    -- Foreign keys
    FOREIGN KEY (generator_id) REFERENCES generators(generator_id),

    -- Constraints (Stage 0: variable width up to 250, fixed height)
    CHECK (content_format = 'ASCII_TILEMAP'),
    CHECK (width >= 1 AND width <= 250),
    CHECK (height = 16)
);

--------------------------------------------------------------------------------
-- battles: Comparison instances (two levels from different generators)
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS battles (
    battle_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    issued_at_utc TEXT NOT NULL,
    expires_at_utc TEXT,
    status TEXT NOT NULL,
    left_level_id TEXT NOT NULL,
    right_level_id TEXT NOT NULL,
    left_generator_id TEXT NOT NULL,
    right_generator_id TEXT NOT NULL,
    matchmaking_policy TEXT NOT NULL DEFAULT 'uniform_v0',
    created_at_utc TEXT NOT NULL,
    updated_at_utc TEXT NOT NULL,

    -- Foreign keys
    FOREIGN KEY (left_level_id) REFERENCES levels(level_id),
    FOREIGN KEY (right_level_id) REFERENCES levels(level_id),
    FOREIGN KEY (left_generator_id) REFERENCES generators(generator_id),
    FOREIGN KEY (right_generator_id) REFERENCES generators(generator_id),

    -- Constraints
    CHECK (status IN ('ISSUED', 'COMPLETED', 'EXPIRED')),
    CHECK (left_level_id != right_level_id),
    CHECK (left_generator_id != right_generator_id)
);

--------------------------------------------------------------------------------
-- votes: User outcomes for battles
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS votes (
    vote_id TEXT PRIMARY KEY,
    battle_id TEXT NOT NULL UNIQUE,
    session_id TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    result TEXT NOT NULL,
    left_tags_json TEXT NOT NULL DEFAULT '[]',
    right_tags_json TEXT NOT NULL DEFAULT '[]',
    telemetry_json TEXT NOT NULL DEFAULT '{}',
    payload_hash TEXT NOT NULL,

    -- Foreign keys
    FOREIGN KEY (battle_id) REFERENCES battles(battle_id),

    -- Constraints
    CHECK (result IN ('LEFT', 'RIGHT', 'TIE', 'SKIP'))
);

--------------------------------------------------------------------------------
-- ratings: Current rating state per generator
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ratings (
    generator_id TEXT PRIMARY KEY,
    rating_value REAL NOT NULL,
    games_played INTEGER NOT NULL,
    wins INTEGER NOT NULL,
    losses INTEGER NOT NULL,
    ties INTEGER NOT NULL,
    skips INTEGER NOT NULL,
    updated_at_utc TEXT NOT NULL,

    -- Foreign keys
    FOREIGN KEY (generator_id) REFERENCES generators(generator_id),

    -- Constraints (non-negative counts)
    CHECK (games_played >= 0),
    CHECK (wins >= 0),
    CHECK (losses >= 0),
    CHECK (ties >= 0),
    CHECK (skips >= 0)
);

--------------------------------------------------------------------------------
-- rating_events: Audit log for rating changes (one per vote)
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS rating_events (
    event_id TEXT PRIMARY KEY,
    vote_id TEXT NOT NULL UNIQUE,
    battle_id TEXT NOT NULL,
    left_generator_id TEXT NOT NULL,
    right_generator_id TEXT NOT NULL,
    result TEXT NOT NULL,
    delta_left REAL NOT NULL,
    delta_right REAL NOT NULL,
    created_at_utc TEXT NOT NULL,

    -- Foreign keys
    FOREIGN KEY (vote_id) REFERENCES votes(vote_id),
    FOREIGN KEY (battle_id) REFERENCES battles(battle_id)
);
