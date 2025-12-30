-- Migration 012: Add player_id to votes
-- Links votes to anonymous player profiles for preference analysis

-- Add player_id column to votes table
ALTER TABLE votes ADD COLUMN player_id TEXT;

-- Index for player vote analysis
CREATE INDEX IF NOT EXISTS idx_votes_player 
ON votes(player_id);

