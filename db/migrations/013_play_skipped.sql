-- Migration 013: Add times_play_skipped column
-- Tracks how many times players skipped playing a level (before finishing)
-- Different from times_skipped which tracks vote result SKIP

ALTER TABLE level_stats ADD COLUMN times_play_skipped INTEGER DEFAULT 0;
