-- Migration: 005_email_verification
-- Purpose: Add email verification functionality
-- Stage: 3 (Builder Profiles - Email/Password Auth)

-- Add is_email_verified flag to users table
ALTER TABLE users ADD COLUMN is_email_verified INTEGER NOT NULL DEFAULT 0;

-- Email verification tokens table
CREATE TABLE IF NOT EXISTS email_verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    token TEXT NOT NULL UNIQUE,
    expires_at_utc TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    verified_at_utc TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Index for fast token lookup
CREATE INDEX IF NOT EXISTS idx_email_verifications_token ON email_verifications(token);

-- Index for cleanup of expired tokens
CREATE INDEX IF NOT EXISTS idx_email_verifications_expires ON email_verifications(expires_at_utc);

