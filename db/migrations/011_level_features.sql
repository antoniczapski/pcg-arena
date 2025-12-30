-- Migration 011: Level Features
-- Stores static structural analysis of levels for research

CREATE TABLE IF NOT EXISTS level_features (
    level_id TEXT PRIMARY KEY,
    
    -- Dimensions
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    
    -- Tile counts
    ground_tiles INTEGER DEFAULT 0,
    platform_tiles INTEGER DEFAULT 0,
    pipe_tiles INTEGER DEFAULT 0,
    coin_tiles INTEGER DEFAULT 0,
    question_block_tiles INTEGER DEFAULT 0,
    brick_tiles INTEGER DEFAULT 0,
    empty_tiles INTEGER DEFAULT 0,
    
    -- Enemy counts (parsed from level tilemap)
    enemy_goomba INTEGER DEFAULT 0,
    enemy_koopa_red INTEGER DEFAULT 0,
    enemy_koopa_green INTEGER DEFAULT 0,
    enemy_spiky INTEGER DEFAULT 0,
    enemy_piranha INTEGER DEFAULT 0,
    enemy_bullet_bill INTEGER DEFAULT 0,
    enemy_total INTEGER DEFAULT 0,
    
    -- Structural metrics
    gap_count INTEGER DEFAULT 0,          -- Number of gaps (sequences of empty ground)
    max_gap_width INTEGER DEFAULT 0,      -- Widest gap in tiles
    platform_count INTEGER DEFAULT 0,     -- Distinct elevated platforms
    avg_platform_height REAL,             -- Average height of platforms (0-15)
    height_variance REAL,                 -- Variance in platform heights
    
    -- Computed complexity scores (0-1 normalized)
    enemy_density REAL,                   -- enemies / width
    coin_density REAL,                    -- coins / width
    gap_density REAL,                     -- gap_tiles / width
    structural_complexity REAL,           -- Combined metric
    
    -- Leniency score (higher = easier)
    leniency_score REAL,
    
    computed_at_utc TEXT NOT NULL,
    
    FOREIGN KEY (level_id) REFERENCES levels(level_id)
);

-- Index for generator analysis
CREATE INDEX IF NOT EXISTS idx_level_features_complexity 
ON level_features(structural_complexity);

-- Index for difficulty queries
CREATE INDEX IF NOT EXISTS idx_level_features_leniency 
ON level_features(leniency_score);

