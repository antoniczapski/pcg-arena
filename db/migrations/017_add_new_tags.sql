-- Migration 017: Add new tags to level_stats

ALTER TABLE level_stats ADD COLUMN tag_impossible INTEGER DEFAULT 0;
ALTER TABLE level_stats ADD COLUMN tag_broken_graphics INTEGER DEFAULT 0;
