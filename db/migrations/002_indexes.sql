-- PCG Arena Stage 0 - Indexes Migration
-- Protocol: arena/v0
-- This migration creates all indexes for query performance.

--------------------------------------------------------------------------------
-- generators indexes
--------------------------------------------------------------------------------
-- For matchmaking: quickly find active generators
CREATE INDEX IF NOT EXISTS idx_generators_is_active ON generators(is_active);

--------------------------------------------------------------------------------
-- levels indexes
--------------------------------------------------------------------------------
-- For fetching levels by generator
CREATE INDEX IF NOT EXISTS idx_levels_generator_id ON levels(generator_id);

-- For deduplication / integrity checks (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_levels_content_hash ON levels(content_hash);

--------------------------------------------------------------------------------
-- battles indexes
--------------------------------------------------------------------------------
-- For finding battles by status (e.g., ISSUED battles awaiting votes)
CREATE INDEX IF NOT EXISTS idx_battles_status ON battles(status);

-- For session-based queries
CREATE INDEX IF NOT EXISTS idx_battles_session_id ON battles(session_id);

-- For analysis: matchup frequency between generators
CREATE INDEX IF NOT EXISTS idx_battles_generator_pair ON battles(left_generator_id, right_generator_id);

--------------------------------------------------------------------------------
-- votes indexes
--------------------------------------------------------------------------------
-- For time-based queries and ordering
CREATE INDEX IF NOT EXISTS idx_votes_created_at_utc ON votes(created_at_utc);

-- For session-based queries
CREATE INDEX IF NOT EXISTS idx_votes_session_id ON votes(session_id);
