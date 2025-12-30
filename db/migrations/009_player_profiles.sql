-- Migration 009: Player Profiles and Sessions
-- Tracks anonymous player identities for preference analysis and clustering

CREATE TABLE IF NOT EXISTS player_profiles (
    player_id TEXT PRIMARY KEY,           -- 'anon_uuid' for anonymous, 'u_uuid' for linked accounts
    
    -- Activity tracking
    first_seen_utc TEXT NOT NULL,
    last_seen_utc TEXT NOT NULL,
    total_battles INTEGER DEFAULT 0,
    total_votes INTEGER DEFAULT 0,
    
    -- Session aggregates
    total_sessions INTEGER DEFAULT 1,
    avg_battles_per_session REAL,
    
    -- Skill estimation (optional Glicko-2 for players)
    skill_rating REAL DEFAULT 1000.0,
    skill_rd REAL DEFAULT 350.0,
    
    -- Preference patterns (for clustering analysis)
    prefers_harder_count INTEGER DEFAULT 0,   -- Voted for level with more deaths
    prefers_easier_count INTEGER DEFAULT 0,   -- Voted for level with fewer deaths
    prefers_longer_count INTEGER DEFAULT 0,   -- Voted for longer levels
    prefers_shorter_count INTEGER DEFAULT 0,  -- Voted for shorter levels
    
    -- Account linking (NULL for anonymous players)
    linked_user_id TEXT,
    
    FOREIGN KEY (linked_user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS player_sessions (
    session_id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    started_at_utc TEXT NOT NULL,
    last_activity_utc TEXT NOT NULL,
    battles_completed INTEGER DEFAULT 0,
    user_agent TEXT,
    ip_hash TEXT,                             -- SHA256 of IP for rate limiting only
    
    FOREIGN KEY (player_id) REFERENCES player_profiles(player_id)
);

-- Index for player session lookups
CREATE INDEX IF NOT EXISTS idx_player_sessions_player 
ON player_sessions(player_id);

-- Index for activity-based queries
CREATE INDEX IF NOT EXISTS idx_player_profiles_activity 
ON player_profiles(last_seen_utc DESC);

-- Index for linked accounts
CREATE INDEX IF NOT EXISTS idx_player_profiles_linked 
ON player_profiles(linked_user_id);

