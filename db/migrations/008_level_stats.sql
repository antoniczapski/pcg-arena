-- Migration 008: Level Statistics Table
-- Tracks aggregate performance metrics per level for research analysis

CREATE TABLE IF NOT EXISTS level_stats (
    level_id TEXT PRIMARY KEY,
    generator_id TEXT NOT NULL,
    
    -- Battle outcomes
    times_shown INTEGER DEFAULT 0,
    times_won INTEGER DEFAULT 0,
    times_lost INTEGER DEFAULT 0,
    times_tied INTEGER DEFAULT 0,
    times_skipped INTEGER DEFAULT 0,
    
    -- Gameplay metrics
    times_completed INTEGER DEFAULT 0,
    total_deaths INTEGER DEFAULT 0,
    total_play_time_seconds REAL DEFAULT 0,
    
    -- Computed averages (updated on each vote)
    win_rate REAL,                    -- wins / (wins + losses), NULL if no decisive votes
    completion_rate REAL,             -- completed / shown
    avg_deaths REAL,                  -- total_deaths / shown
    avg_duration_seconds REAL,        -- total_play_time / shown
    
    -- Tag counts
    tag_fun INTEGER DEFAULT 0,
    tag_boring INTEGER DEFAULT 0,
    tag_too_hard INTEGER DEFAULT 0,
    tag_too_easy INTEGER DEFAULT 0,
    tag_creative INTEGER DEFAULT 0,
    tag_good_flow INTEGER DEFAULT 0,
    tag_unfair INTEGER DEFAULT 0,
    tag_confusing INTEGER DEFAULT 0,
    tag_not_mario_like INTEGER DEFAULT 0,
    
    -- Difficulty classification (computed from deaths/completion)
    difficulty_score REAL,            -- Normalized 0-1 based on deaths/completion
    
    updated_at_utc TEXT NOT NULL,
    
    FOREIGN KEY (level_id) REFERENCES levels(level_id),
    FOREIGN KEY (generator_id) REFERENCES generators(generator_id)
);

-- Index for efficient generator-based queries
CREATE INDEX IF NOT EXISTS idx_level_stats_generator 
ON level_stats(generator_id);

-- Index for leaderboard-style queries
CREATE INDEX IF NOT EXISTS idx_level_stats_win_rate 
ON level_stats(win_rate DESC);

-- Index for difficulty analysis
CREATE INDEX IF NOT EXISTS idx_level_stats_difficulty 
ON level_stats(difficulty_score);

