-- Migration: Make vote_id nullable in play_trajectories
-- Allows storing trajectories from practice battles without associated votes

-- SQLite doesn't support ALTER COLUMN, so we need to recreate the table

-- Step 1: Create new table with nullable vote_id and no foreign key constraints on optional fields
CREATE TABLE play_trajectories_new (
    trajectory_id TEXT PRIMARY KEY,
    vote_id TEXT,  -- Now nullable, no foreign key constraint
    level_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    player_id TEXT,  -- No foreign key - player may not exist in profiles yet
    side TEXT NOT NULL CHECK (side IN ('left', 'right')),
    
    -- Compressed trajectory data (JSON arrays)
    trajectory_json TEXT NOT NULL,
    death_locations_json TEXT,
    events_json TEXT,
    
    -- Summary stats
    duration_ticks INTEGER,
    max_x_reached REAL,
    death_count INTEGER,
    completed INTEGER DEFAULT 0,
    
    created_at_utc TEXT NOT NULL,
    
    -- Only keep level foreign key - level must exist
    FOREIGN KEY (level_id) REFERENCES levels(level_id)
);

-- Step 2: Copy all existing data
INSERT INTO play_trajectories_new 
SELECT * FROM play_trajectories;

-- Step 3: Drop old table
DROP TABLE play_trajectories;

-- Step 4: Rename new table
ALTER TABLE play_trajectories_new RENAME TO play_trajectories;

-- Step 5: Recreate indexes
CREATE INDEX IF NOT EXISTS idx_trajectories_level 
ON play_trajectories(level_id);

CREATE INDEX IF NOT EXISTS idx_trajectories_player 
ON play_trajectories(player_id);

CREATE INDEX IF NOT EXISTS idx_trajectories_session 
ON play_trajectories(session_id);

CREATE INDEX IF NOT EXISTS idx_trajectories_vote 
ON play_trajectories(vote_id);
