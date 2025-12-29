-- PCG Arena Stage 4a - Glicko-2 Matchmaking Migration
-- Protocol: arena/v0
-- Adds rating deviation (RD) and volatility for Glicko-2, plus pair statistics table

--------------------------------------------------------------------------------
-- ratings table: Add Glicko-2 columns
--------------------------------------------------------------------------------
-- Rating deviation (RD): Confidence in rating. High = uncertain, Low = confident
-- Range: ~50 (very certain) to 350 (new/uncertain)
-- Default: 350 (new generator)
ALTER TABLE ratings ADD COLUMN rd REAL NOT NULL DEFAULT 350.0;

-- Volatility: Expected fluctuation in player performance
-- Range: typically 0.03 to 0.1
-- Default: 0.06 (recommended starting value)
ALTER TABLE ratings ADD COLUMN volatility REAL NOT NULL DEFAULT 0.06;

--------------------------------------------------------------------------------
-- generator_pair_stats: Track battles between each pair of generators
--------------------------------------------------------------------------------
-- Used for confusion matrix and coverage-aware matchmaking
CREATE TABLE IF NOT EXISTS generator_pair_stats (
    -- Use lexicographically ordered pair (gen1_id < gen2_id) for consistency
    gen1_id TEXT NOT NULL,
    gen2_id TEXT NOT NULL,
    
    -- Battle counts
    battle_count INTEGER NOT NULL DEFAULT 0,
    gen1_wins INTEGER NOT NULL DEFAULT 0,
    gen2_wins INTEGER NOT NULL DEFAULT 0,
    ties INTEGER NOT NULL DEFAULT 0,
    skips INTEGER NOT NULL DEFAULT 0,
    
    -- Timestamps
    last_battle_utc TEXT,
    
    -- Primary key is the pair
    PRIMARY KEY (gen1_id, gen2_id),
    
    -- Foreign keys
    FOREIGN KEY (gen1_id) REFERENCES generators(generator_id),
    FOREIGN KEY (gen2_id) REFERENCES generators(generator_id),
    
    -- Ensure gen1_id < gen2_id lexicographically (enforced by application)
    CHECK (gen1_id < gen2_id)
);

--------------------------------------------------------------------------------
-- rating_events: Add RD deltas for auditability
--------------------------------------------------------------------------------
-- Add columns for RD changes (nullable for backward compatibility with existing events)
ALTER TABLE rating_events ADD COLUMN rd_left_before REAL;
ALTER TABLE rating_events ADD COLUMN rd_left_after REAL;
ALTER TABLE rating_events ADD COLUMN rd_right_before REAL;
ALTER TABLE rating_events ADD COLUMN rd_right_after REAL;

--------------------------------------------------------------------------------
-- Indexes for new tables/columns
--------------------------------------------------------------------------------
-- For finding under-sampled pairs (low battle count)
CREATE INDEX IF NOT EXISTS idx_pair_stats_battle_count 
    ON generator_pair_stats(battle_count);

-- For time-based queries on pair stats
CREATE INDEX IF NOT EXISTS idx_pair_stats_last_battle 
    ON generator_pair_stats(last_battle_utc);

-- For efficient lookup by RD (high uncertainty generators)
CREATE INDEX IF NOT EXISTS idx_ratings_rd ON ratings(rd);

