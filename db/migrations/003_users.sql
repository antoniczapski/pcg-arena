-- PCG Arena Stage 3 - Users and Builder Profile Migration
-- Protocol: arena/v0
-- This migration adds user authentication and generator ownership.

--------------------------------------------------------------------------------
-- users: Authenticated users (researchers/builders)
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    google_sub TEXT UNIQUE,              -- Google's unique subject ID (null for dev auth)
    display_name TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    last_login_utc TEXT NOT NULL
);

--------------------------------------------------------------------------------
-- Add owner_user_id to generators table
-- NULL = system-seeded generator (from generators.json)
-- Non-NULL = user-submitted generator (from builder profile)
--------------------------------------------------------------------------------
ALTER TABLE generators ADD COLUMN owner_user_id TEXT REFERENCES users(user_id);

--------------------------------------------------------------------------------
-- user_sessions: Track active sessions (for session management)
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_sessions (
    session_token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    expires_at_utc TEXT NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

--------------------------------------------------------------------------------
-- Indexes for users and sessions
--------------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_google_sub ON users(google_sub);
CREATE INDEX IF NOT EXISTS idx_generators_owner_user_id ON generators(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at_utc);

