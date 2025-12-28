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
    is_email_verified: bool = False


class DevLoginRequest(BaseModel):
    """Request for dev login (testing only)."""
    email: str = "test@example.com"
    display_name: str = "Test User"


class GoogleLoginRequest(BaseModel):
    """Request for Google OAuth login."""
    credential: str  # Google ID token


class EmailRegisterRequest(BaseModel):
    """Request for email/password registration."""
    email: str
    password: str
    display_name: str


class EmailLoginRequest(BaseModel):
    """Request for email/password login."""
    email: str
    password: str


def generate_session_token() -> str:
    """Generate a secure random session token."""
    return secrets.token_urlsafe(32)


# Password hashing configuration
MIN_PASSWORD_LENGTH = 8


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    import bcrypt
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password meets requirements.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
    return True, ""


def get_session_expiry() -> str:
    """Get the session expiry timestamp."""
    expiry = datetime.now(timezone.utc) + timedelta(days=SESSION_DURATION_DAYS)
    return expiry.isoformat()


def create_user(email: str, display_name: str, google_sub: Optional[str] = None, password_hash: Optional[str] = None) -> User:
    """
    Create a new user in the database.
    
    Args:
        email: User's email address
        display_name: User's display name
        google_sub: Google subject ID (optional, for OAuth users)
        password_hash: Hashed password (optional, for email/password users)
    
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
                INSERT INTO users (user_id, email, google_sub, display_name, password_hash, created_at_utc, last_login_utc)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, email, google_sub, display_name, password_hash, now_utc, now_utc)
            )
        
        logger.info(f"Created new user: user_id={user_id} email={email}")
        
        return User(
            user_id=user_id,
            email=email,
            display_name=display_name,
            created_at_utc=now_utc,
            last_login_utc=now_utc,
            is_email_verified=(google_sub is not None)  # Google users are auto-verified
        )
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise


def get_password_hash_by_email(email: str) -> Optional[str]:
    """Get the password hash for a user by email."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT password_hash FROM users WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()
    
    if row and row["password_hash"]:
        return row["password_hash"]
    return None


def user_has_password(email: str) -> bool:
    """Check if a user has a password set (vs OAuth-only)."""
    return get_password_hash_by_email(email) is not None


def get_user_by_email(email: str) -> Optional[User]:
    """Get a user by email address."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT user_id, email, display_name, created_at_utc, last_login_utc, is_email_verified FROM users WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()
    
    if row:
        return User(
            user_id=row["user_id"],
            email=row["email"],
            display_name=row["display_name"],
            created_at_utc=row["created_at_utc"],
            last_login_utc=row["last_login_utc"],
            is_email_verified=bool(row["is_email_verified"])
        )
    return None


def get_user_by_google_sub(google_sub: str) -> Optional[User]:
    """Get a user by Google subject ID."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT user_id, email, display_name, created_at_utc, last_login_utc, is_email_verified FROM users WHERE google_sub = ?",
        (google_sub,)
    )
    row = cursor.fetchone()
    
    if row:
        return User(
            user_id=row["user_id"],
            email=row["email"],
            display_name=row["display_name"],
            created_at_utc=row["created_at_utc"],
            last_login_utc=row["last_login_utc"],
            is_email_verified=bool(row["is_email_verified"])
        )
    return None


def get_user_by_id(user_id: str) -> Optional[User]:
    """Get a user by user ID."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT user_id, email, display_name, created_at_utc, last_login_utc, is_email_verified FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    
    if row:
        return User(
            user_id=row["user_id"],
            email=row["email"],
            display_name=row["display_name"],
            created_at_utc=row["created_at_utc"],
            last_login_utc=row["last_login_utc"],
            is_email_verified=bool(row["is_email_verified"])
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
        SELECT u.user_id, u.email, u.display_name, u.created_at_utc, u.last_login_utc, u.is_email_verified
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
            last_login_utc=row["last_login_utc"],
            is_email_verified=bool(row["is_email_verified"])
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


# Google OAuth verification
def verify_google_token(credential: str) -> Optional[dict]:
    """
    Verify a Google ID token and extract user info.
    
    Uses Google's official library to verify the JWT signature,
    check expiration, and validate the audience (client ID).
    
    Args:
        credential: The Google ID token (JWT from frontend)
    
    Returns:
        Dict with email, google_sub, and name if valid, None otherwise
    """
    if not config.google_client_id:
        logger.error("Google OAuth not configured: ARENA_GOOGLE_CLIENT_ID not set")
        return None
    
    logger.info(f"Verifying Google token with client_id: {config.google_client_id[:20]}...")
    
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        
        # Verify the token with Google's servers
        # This checks: signature, expiration, audience, and issuer
        idinfo = id_token.verify_oauth2_token(
            credential, 
            google_requests.Request(), 
            config.google_client_id
        )
        
        logger.info(f"Token verified. Audience: {idinfo.get('aud', 'unknown')[:20]}...")
        
        # Verify the token was issued by Google
        issuer = idinfo.get("iss", "")
        if issuer not in ["accounts.google.com", "https://accounts.google.com"]:
            logger.warning(f"Invalid token issuer: {issuer}")
            return None
        
        # Extract user info
        email = idinfo.get("email")
        google_sub = idinfo.get("sub")  # Unique, stable Google user ID
        name = idinfo.get("name", email.split("@")[0] if email else "User")
        
        if not email or not google_sub:
            logger.warning("Token missing required fields (email or sub)")
            return None
        
        logger.info(f"Google token verified for: {email}")
        
        return {
            "email": email,
            "google_sub": google_sub,
            "name": name
        }
        
    except ValueError as e:
        # Token is invalid (expired, wrong audience, bad signature, etc.)
        logger.warning(f"Google token verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error verifying Google token: {e}")
        return None


# ============================================================================
# Email Verification
# ============================================================================

def create_email_verification_token(user_id: str) -> str:
    """
    Create a secure verification token for email verification.
    
    Returns:
        The verification token (to be sent in email link)
    """
    token = secrets.token_urlsafe(32)
    expiry = datetime.now(timezone.utc) + timedelta(hours=24)
    
    with transaction() as cursor:
        cursor.execute(
            """
            INSERT INTO email_verifications (user_id, token, expires_at_utc, created_at_utc)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, token, expiry.isoformat(), datetime.now(timezone.utc).isoformat())
        )
    
    logger.info(f"Created email verification token for user {user_id}")
    return token


def verify_email_token(token: str) -> Optional[str]:
    """
    Verify an email verification token and mark the user's email as verified.
    
    Args:
        token: The verification token from the email link
    
    Returns:
        The user_id if verification succeeds, None otherwise
    """
    conn = get_connection()
    now = datetime.now(timezone.utc)
    
    # Find the verification record
    row = conn.execute(
        """
        SELECT user_id, expires_at_utc, verified_at_utc
        FROM email_verifications
        WHERE token = ?
        """,
        (token,)
    ).fetchone()
    
    if not row:
        logger.warning("Email verification failed: token not found")
        return None
    
    user_id = row["user_id"]
    expires_at = datetime.fromisoformat(row["expires_at_utc"])
    verified_at = row["verified_at_utc"]
    
    # Check if already verified
    if verified_at:
        logger.info(f"Email already verified for user {user_id}")
        return user_id
    
    # Check if expired
    if now > expires_at:
        logger.warning(f"Email verification failed: token expired for user {user_id}")
        return None
    
    # Mark as verified
    try:
        with transaction() as cursor:
            # Update verification record
            cursor.execute(
                """
                UPDATE email_verifications
                SET verified_at_utc = ?
                WHERE token = ?
                """,
                (now.isoformat(), token)
            )
            
            # Update user record
            cursor.execute(
                """
                UPDATE users
                SET is_email_verified = 1
                WHERE user_id = ?
                """,
                (user_id,)
            )
        
        logger.info(f"Email verified successfully for user {user_id}")
        return user_id
        
    except Exception as e:
        logger.error(f"Failed to verify email: {e}")
        return None


def send_verification_email(email: str, token: str) -> bool:
    """
    Send a verification email to the user.
    
    Args:
        email: User's email address
        token: Verification token
    
    Returns:
        True if email was sent successfully, False otherwise
    """
    if not config.sendgrid_api_key:
        logger.error("SendGrid not configured: SENDGRID_API_KEY not set")
        return False
    
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content
        
        # Build verification URL
        # Use frontend_url for the link (where the user will click)
        verification_url = f"{config.frontend_url}/verify-email?token={token}"
        
        # Create email message
        message = Mail(
            from_email=Email(config.sendgrid_from_email, config.sendgrid_from_name),
            to_emails=To(email),
            subject="Verify your PCG Arena email",
            html_content=Content(
                "text/html",
                f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1 style="color: #4CAF50;">Welcome to PCG Arena!</h1>
                        <p>Thank you for registering. Please verify your email address by clicking the button below:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{verification_url}" 
                               style="background-color: #4CAF50; color: white; padding: 14px 28px; 
                                      text-decoration: none; border-radius: 4px; display: inline-block;">
                                Verify Email
                            </a>
                        </div>
                        <p style="color: #666; font-size: 14px;">
                            Or copy and paste this link into your browser:<br>
                            <a href="{verification_url}">{verification_url}</a>
                        </p>
                        <p style="color: #666; font-size: 14px;">
                            This link will expire in 24 hours.
                        </p>
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                        <p style="color: #999; font-size: 12px;">
                            If you didn't create an account with PCG Arena, you can safely ignore this email.
                        </p>
                    </div>
                </body>
                </html>
                """
            )
        )
        
        # Send email
        sg = SendGridAPIClient(config.sendgrid_api_key)
        response = sg.send(message)
        
        if response.status_code >= 200 and response.status_code < 300:
            logger.info(f"Verification email sent successfully to {email}")
            return True
        else:
            logger.error(f"SendGrid returned status code {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        return False


# ============================================================================
# Password Reset
# ============================================================================

class ForgotPasswordRequest(BaseModel):
    """Request for password reset."""
    email: str


class ResetPasswordRequest(BaseModel):
    """Request to set new password."""
    token: str
    new_password: str


def create_password_reset_token(user_id: str) -> str:
    """
    Create a secure token for password reset.
    
    Returns:
        The reset token (to be sent in email link)
    """
    token = secrets.token_urlsafe(32)
    expiry = datetime.now(timezone.utc) + timedelta(hours=1)  # 1 hour expiry for password reset
    
    with transaction() as cursor:
        cursor.execute(
            """
            INSERT INTO password_resets (user_id, token, expires_at_utc, created_at_utc)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, token, expiry.isoformat(), datetime.now(timezone.utc).isoformat())
        )
    
    logger.info(f"Created password reset token for user {user_id}")
    return token


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token.
    
    Args:
        token: The reset token from the email link
    
    Returns:
        The user_id if valid, None otherwise
    """
    conn = get_connection()
    now = datetime.now(timezone.utc)
    
    row = conn.execute(
        """
        SELECT user_id, expires_at_utc, used_at_utc
        FROM password_resets
        WHERE token = ?
        """,
        (token,)
    ).fetchone()
    
    if not row:
        logger.warning("Password reset failed: token not found")
        return None
    
    user_id = row["user_id"]
    expires_at = datetime.fromisoformat(row["expires_at_utc"])
    used_at = row["used_at_utc"]
    
    # Check if already used
    if used_at:
        logger.warning(f"Password reset failed: token already used for user {user_id}")
        return None
    
    # Check if expired
    if now > expires_at:
        logger.warning(f"Password reset failed: token expired for user {user_id}")
        return None
    
    return user_id


def use_password_reset_token(token: str) -> bool:
    """
    Mark a password reset token as used.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with transaction() as cursor:
            cursor.execute(
                """
                UPDATE password_resets
                SET used_at_utc = ?
                WHERE token = ?
                """,
                (datetime.now(timezone.utc).isoformat(), token)
            )
        return True
    except Exception as e:
        logger.error(f"Failed to mark password reset token as used: {e}")
        return False


def update_user_password(user_id: str, new_password_hash: str) -> bool:
    """
    Update a user's password hash.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with transaction() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET password_hash = ?
                WHERE user_id = ?
                """,
                (new_password_hash, user_id)
            )
        logger.info(f"Password updated for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to update password: {e}")
        return False


def send_password_reset_email(email: str, token: str) -> bool:
    """
    Send a password reset email to the user.
    
    Args:
        email: User's email address
        token: Reset token
    
    Returns:
        True if email was sent successfully, False otherwise
    """
    if not config.sendgrid_api_key:
        logger.error("SendGrid not configured: SENDGRID_API_KEY not set")
        return False
    
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content
        
        # Build reset URL
        reset_url = f"{config.frontend_url}/reset-password?token={token}"
        
        # Create email message
        message = Mail(
            from_email=Email(config.sendgrid_from_email, config.sendgrid_from_name),
            to_emails=To(email),
            subject="Reset your PCG Arena password",
            html_content=Content(
                "text/html",
                f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1 style="color: #7c8aff;">Reset Your Password</h1>
                        <p>You requested to reset your PCG Arena password.</p>
                        <p>Click the button below to set a new password:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_url}" 
                               style="background-color: #7c8aff; color: white; padding: 14px 28px; 
                                      text-decoration: none; border-radius: 4px; display: inline-block;">
                                Reset Password
                            </a>
                        </div>
                        <p style="color: #666; font-size: 14px;">
                            Or copy and paste this link into your browser:<br>
                            <a href="{reset_url}">{reset_url}</a>
                        </p>
                        <p style="color: #666; font-size: 14px;">
                            This link will expire in <strong>1 hour</strong>.
                        </p>
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                        <p style="color: #999; font-size: 12px;">
                            If you didn't request a password reset, you can safely ignore this email.
                            Your password will remain unchanged.
                        </p>
                    </div>
                </body>
                </html>
                """
            )
        )
        
        # Send email
        sg = SendGridAPIClient(config.sendgrid_api_key)
        response = sg.send(message)
        
        if response.status_code >= 200 and response.status_code < 300:
            logger.info(f"Password reset email sent successfully to {email}")
            return True
        else:
            logger.error(f"SendGrid returned status code {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        return False

