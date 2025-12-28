-- Migration: 006_password_reset
-- Purpose: Add password reset token storage
-- Stage: 3 (Builder Profiles - Password Reset)

-- Password reset tokens table
CREATE TABLE IF NOT EXISTS password_resets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    token TEXT NOT NULL UNIQUE,
    expires_at_utc TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    used_at_utc TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Index for fast token lookup
CREATE INDEX IF NOT EXISTS idx_password_resets_token ON password_resets(token);

-- Index for cleanup of expired tokens
CREATE INDEX IF NOT EXISTS idx_password_resets_expires ON password_resets(expires_at_utc);

