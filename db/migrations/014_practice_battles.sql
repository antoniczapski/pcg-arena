-- Migration: Practice Battles
-- Adds support for practice/replay mode where players can play a specific level
-- without affecting ratings or voting stats

-- Add is_practice flag to battles table
-- Practice battles allow same level on both sides and don't affect ratings
ALTER TABLE battles ADD COLUMN is_practice INTEGER NOT NULL DEFAULT 0;

-- Create index for filtering practice vs regular battles
CREATE INDEX IF NOT EXISTS idx_battles_is_practice ON battles(is_practice);
