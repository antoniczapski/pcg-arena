-- Migration: Relax Battle Constraints for Practice Mode
-- Removes the CHECK constraints that prevent same level/generator on both sides
-- This allows practice battles where the same level appears on both sides

-- SQLite doesn't support ALTER TABLE to modify constraints
-- We need to recreate the table without the problematic constraints

-- Step 1: Create new table without the problematic constraints
CREATE TABLE battles_new (
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
    is_practice INTEGER NOT NULL DEFAULT 0,

    -- Foreign keys
    FOREIGN KEY (left_level_id) REFERENCES levels(level_id),
    FOREIGN KEY (right_level_id) REFERENCES levels(level_id),
    FOREIGN KEY (left_generator_id) REFERENCES generators(generator_id),
    FOREIGN KEY (right_generator_id) REFERENCES generators(generator_id),

    -- Constraints - only status validation, no level/generator uniqueness
    CHECK (status IN ('ISSUED', 'COMPLETED', 'EXPIRED')),
    CHECK (is_practice IN (0, 1)),
    -- For non-practice battles, levels must be different
    -- This is now enforced in application code instead of DB constraint
    CHECK (is_practice = 1 OR left_level_id != right_level_id),
    CHECK (is_practice = 1 OR left_generator_id != right_generator_id)
);

-- Step 2: Copy data from old table
INSERT INTO battles_new SELECT 
    battle_id, session_id, issued_at_utc, expires_at_utc, status,
    left_level_id, right_level_id, left_generator_id, right_generator_id,
    matchmaking_policy, created_at_utc, updated_at_utc, is_practice
FROM battles;

-- Step 3: Drop old table
DROP TABLE battles;

-- Step 4: Rename new table
ALTER TABLE battles_new RENAME TO battles;

-- Step 5: Recreate indexes
CREATE INDEX IF NOT EXISTS idx_battles_session_id ON battles(session_id);
CREATE INDEX IF NOT EXISTS idx_battles_status ON battles(status);
CREATE INDEX IF NOT EXISTS idx_battles_left_generator_id ON battles(left_generator_id);
CREATE INDEX IF NOT EXISTS idx_battles_right_generator_id ON battles(right_generator_id);
CREATE INDEX IF NOT EXISTS idx_battles_is_practice ON battles(is_practice);
