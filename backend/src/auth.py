"""
PCG Arena - Authentication Module
Protocol: arena/v0

Handles user authentication with:
- Dev login (for local testing)
- Google OAuth (for production)
- Session management via secure cookies
"""

import uuid
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import Request, Response, HTTPException
from pydantic import BaseModel, EmailStr

from config import load_config
from db import get_connection, transaction

logger = logging.getLogger(__name__)
config = load_config()

# Session configuration
SESSION_COOKIE_NAME = "arena_session"
SESSION_DURATION_DAYS = 30


class User(BaseModel):
    """User model for API responses."""
    user_id: str
    email: str
    display_name: str
    created_at_utc: str
    last_login_utc: str


class DevLoginRequest(BaseModel):
    """Request for dev login (testing only)."""
    email: str = "test@example.com"
    display_name: str = "Test User"


class GoogleLoginRequest(BaseModel):
    """Request for Google OAuth login."""
    credential: str  # Google ID token


def generate_session_token() -> str:
    """Generate a secure random session token."""
    return secrets.token_urlsafe(32)


def get_session_expiry() -> str:
    """Get the session expiry timestamp."""
    expiry = datetime.now(timezone.utc) + timedelta(days=SESSION_DURATION_DAYS)
    return expiry.isoformat()


def create_user(email: str, display_name: str, google_sub: Optional[str] = None) -> User:
    """
    Create a new user in the database.
    
    Args:
        email: User's email address
        display_name: User's display name
        google_sub: Google subject ID (optional, for OAuth users)
    
    Returns:
        The created User object
    """
    conn = get_connection()
    now_utc = datetime.now(timezone.utc).isoformat()
    user_id = f"u_{uuid.uuid4().hex[:16]}"
    
    try:
        with transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO users (user_id, email, google_sub, display_name, created_at_utc, last_login_utc)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, email, google_sub, display_name, now_utc, now_utc)
            )
        
        logger.info(f"Created new user: user_id={user_id} email={email}")
        
        return User(
            user_id=user_id,
            email=email,
            display_name=display_name,
            created_at_utc=now_utc,
            last_login_utc=now_utc
        )
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise


def get_user_by_email(email: str) -> Optional[User]:
    """Get a user by email address."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT user_id, email, display_name, created_at_utc, last_login_utc FROM users WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()
    
    if row:
        return User(
            user_id=row["user_id"],
            email=row["email"],
            display_name=row["display_name"],
            created_at_utc=row["created_at_utc"],
            last_login_utc=row["last_login_utc"]
        )
    return None


def get_user_by_google_sub(google_sub: str) -> Optional[User]:
    """Get a user by Google subject ID."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT user_id, email, display_name, created_at_utc, last_login_utc FROM users WHERE google_sub = ?",
        (google_sub,)
    )
    row = cursor.fetchone()
    
    if row:
        return User(
            user_id=row["user_id"],
            email=row["email"],
            display_name=row["display_name"],
            created_at_utc=row["created_at_utc"],
            last_login_utc=row["last_login_utc"]
        )
    return None


def get_user_by_id(user_id: str) -> Optional[User]:
    """Get a user by user ID."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT user_id, email, display_name, created_at_utc, last_login_utc FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    
    if row:
        return User(
            user_id=row["user_id"],
            email=row["email"],
            display_name=row["display_name"],
            created_at_utc=row["created_at_utc"],
            last_login_utc=row["last_login_utc"]
        )
    return None


def update_last_login(user_id: str) -> None:
    """Update the user's last login timestamp."""
    conn = get_connection()
    now_utc = datetime.now(timezone.utc).isoformat()
    
    with transaction() as cursor:
        cursor.execute(
            "UPDATE users SET last_login_utc = ? WHERE user_id = ?",
            (now_utc, user_id)
        )


def create_session(user_id: str) -> str:
    """
    Create a new session for a user.
    
    Args:
        user_id: The user's ID
    
    Returns:
        The session token
    """
    conn = get_connection()
    now_utc = datetime.now(timezone.utc).isoformat()
    expires_at = get_session_expiry()
    session_token = generate_session_token()
    
    with transaction() as cursor:
        cursor.execute(
            """
            INSERT INTO user_sessions (session_token, user_id, created_at_utc, expires_at_utc)
            VALUES (?, ?, ?, ?)
            """,
            (session_token, user_id, now_utc, expires_at)
        )
    
    logger.debug(f"Created session for user {user_id}")
    return session_token


def get_user_from_session(session_token: str) -> Optional[User]:
    """
    Get the user associated with a session token.
    
    Args:
        session_token: The session token from cookie
    
    Returns:
        User if session is valid and not expired, None otherwise
    """
    if not session_token:
        return None
    
    conn = get_connection()
    now_utc = datetime.now(timezone.utc).isoformat()
    
    cursor = conn.execute(
        """
        SELECT u.user_id, u.email, u.display_name, u.created_at_utc, u.last_login_utc
        FROM user_sessions s
        JOIN users u ON s.user_id = u.user_id
        WHERE s.session_token = ? AND s.expires_at_utc > ?
        """,
        (session_token, now_utc)
    )
    row = cursor.fetchone()
    
    if row:
        return User(
            user_id=row["user_id"],
            email=row["email"],
            display_name=row["display_name"],
            created_at_utc=row["created_at_utc"],
            last_login_utc=row["last_login_utc"]
        )
    return None


def delete_session(session_token: str) -> None:
    """Delete a session (logout)."""
    conn = get_connection()
    
    with transaction() as cursor:
        cursor.execute(
            "DELETE FROM user_sessions WHERE session_token = ?",
            (session_token,)
        )


def cleanup_expired_sessions() -> int:
    """Delete all expired sessions. Returns count of deleted sessions."""
    conn = get_connection()
    now_utc = datetime.now(timezone.utc).isoformat()
    
    with transaction() as cursor:
        cursor.execute(
            "DELETE FROM user_sessions WHERE expires_at_utc <= ?",
            (now_utc,)
        )
        count = cursor.rowcount
    
    if count > 0:
        logger.info(f"Cleaned up {count} expired session(s)")
    
    return count


def get_current_user(request: Request) -> Optional[User]:
    """
    Get the current user from the request cookies.
    
    Args:
        request: FastAPI request object
    
    Returns:
        User if authenticated, None otherwise
    """
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_token:
        return None
    
    return get_user_from_session(session_token)


def set_session_cookie(response: Response, session_token: str) -> None:
    """Set the session cookie on the response."""
    is_https = config.public_url.startswith("https://")
    
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        max_age=SESSION_DURATION_DAYS * 24 * 60 * 60,
        path="/",  # Explicitly set path to root
        httponly=True,
        samesite="lax",
        secure=is_https
    )


def clear_session_cookie(response: Response) -> None:
    """Clear the session cookie on the response."""
    response.delete_cookie(key=SESSION_COOKIE_NAME)


# Google OAuth verification (placeholder - will be implemented in Phase 2)
def verify_google_token(credential: str) -> Optional[dict]:
    """
    Verify a Google ID token and extract user info.
    
    Args:
        credential: The Google ID token
    
    Returns:
        Dict with email, google_sub, and name if valid, None otherwise
    
    Note: This is a placeholder for Phase 2 implementation.
    """
    # Phase 2 will implement actual Google token verification
    # For now, return None to indicate not implemented
    logger.warning("Google OAuth not yet implemented (Phase 2)")
    return None

