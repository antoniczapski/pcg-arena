-- PCG Arena Stage 3 - Password Authentication Migration
-- Protocol: arena/v0
-- This migration adds password-based authentication support.

--------------------------------------------------------------------------------
-- Add password_hash column to users table
-- NULL = OAuth-only user (Google login)
-- Non-NULL = user can login with email/password
--------------------------------------------------------------------------------
ALTER TABLE users ADD COLUMN password_hash TEXT;


