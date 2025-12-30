-- Migration 010: Play Trajectories
-- Stores detailed position data for heatmap analysis and research

CREATE TABLE IF NOT EXISTS play_trajectories (
    trajectory_id TEXT PRIMARY KEY,
    vote_id TEXT NOT NULL,
    level_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    player_id TEXT,
    side TEXT NOT NULL CHECK (side IN ('left', 'right')),
    
    -- Compressed trajectory data (JSON arrays)
    trajectory_json TEXT NOT NULL,        -- Array of {tick, x, y, state}
    death_locations_json TEXT,            -- Array of {x, y, tick, cause}
    events_json TEXT,                     -- Full event stream (optional)
    
    -- Summary stats for quick queries without parsing JSON
    duration_ticks INTEGER,
    max_x_reached REAL,
    death_count INTEGER,
    completed INTEGER DEFAULT 0,          -- 1 if level was completed
    
    created_at_utc TEXT NOT NULL,
    
    FOREIGN KEY (vote_id) REFERENCES votes(vote_id),
    FOREIGN KEY (level_id) REFERENCES levels(level_id),
    FOREIGN KEY (player_id) REFERENCES player_profiles(player_id)
);

-- Index for level-based heatmap queries
CREATE INDEX IF NOT EXISTS idx_trajectories_level 
ON play_trajectories(level_id);

-- Index for player trajectory analysis
CREATE INDEX IF NOT EXISTS idx_trajectories_player 
ON play_trajectories(player_id);

-- Index for session lookups
CREATE INDEX IF NOT EXISTS idx_trajectories_session 
ON play_trajectories(session_id);

-- Index for vote linkage
CREATE INDEX IF NOT EXISTS idx_trajectories_vote 
ON play_trajectories(vote_id);

