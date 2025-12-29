"""
PCG Arena Backend Configuration
Protocol: arena/v0

Loads configuration from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration loaded from environment."""
    
    # Database
    db_path: str
    
    # Server
    host: str
    port: int
    public_url: str  # Public URL for external access (Stage 1)
    
    # Rating system (Glicko-2)
    initial_rating: float
    initial_rd: float  # Initial rating deviation (uncertainty)
    initial_volatility: float  # Initial volatility
    
    # Matchmaking
    matchmaking_policy: str  # "uniform_v0" or "agis_v1"
    
    # Paths (inside container)
    migrations_path: str
    seed_path: str
    backup_path: str  # Backup directory path (Stage 1)
    
    # Debug mode (enables debug endpoints)
    debug: bool
    
    # Admin API key (Stage 1)
    admin_key: str
    
    # CORS settings (Stage 1)
    allowed_origins: list[str]
    
    # Logging (Stage 1)
    log_level: str
    
    # Authentication (Stage 3)
    dev_auth: bool  # Enable dev login (testing only)
    google_client_id: str  # Google OAuth client ID
    
    # Email (Stage 3)
    sendgrid_api_key: str  # SendGrid API key for email sending
    sendgrid_from_email: str  # From email address
    sendgrid_from_name: str  # From name
    
    # Frontend URL (for email links)
    frontend_url: str  # URL of the frontend (for verification links)


def load_config() -> Config:
    """Load configuration from environment variables."""
    
    # Parse allowed origins from comma-separated string
    origins_str = os.environ.get("ARENA_ALLOWED_ORIGINS", "*")
    if origins_str == "*":
        allowed_origins = ["*"]
    else:
        allowed_origins = [origin.strip() for origin in origins_str.split(",")]
    
    # Determine public URL (defaults to localhost for local dev)
    host = os.environ.get("ARENA_HOST", "0.0.0.0")
    port = int(os.environ.get("ARENA_PORT", "8080"))
    public_url = os.environ.get("ARENA_PUBLIC_URL", f"http://localhost:{port}")
    
    return Config(
        db_path=os.environ.get("ARENA_DB_PATH", "/data/arena.sqlite"),
        host=host,
        port=port,
        public_url=public_url,
        initial_rating=float(os.environ.get("ARENA_INITIAL_RATING", "1000.0")),
        initial_rd=float(os.environ.get("ARENA_INITIAL_RD", "350.0")),
        initial_volatility=float(os.environ.get("ARENA_INITIAL_VOLATILITY", "0.06")),
        matchmaking_policy=os.environ.get("ARENA_MATCHMAKING_POLICY", "agis_v1"),
        migrations_path=os.environ.get("ARENA_MIGRATIONS_PATH", "/migrations"),
        seed_path=os.environ.get("ARENA_SEED_PATH", "/seed"),
        backup_path=os.environ.get("ARENA_BACKUP_PATH", "/backups"),
        debug=os.environ.get("ARENA_DEBUG", "false").lower() in ("true", "1", "yes"),
        admin_key=os.environ.get("ARENA_ADMIN_KEY", ""),
        allowed_origins=allowed_origins,
        log_level=os.environ.get("ARENA_LOG_LEVEL", "INFO").upper(),
        dev_auth=os.environ.get("ARENA_DEV_AUTH", "false").lower() in ("true", "1", "yes"),
        google_client_id=os.environ.get("ARENA_GOOGLE_CLIENT_ID", ""),
        sendgrid_api_key=os.environ.get("SENDGRID_API_KEY", ""),
        sendgrid_from_email=os.environ.get("SENDGRID_FROM_EMAIL", "noreply@pcg-arena.com"),
        sendgrid_from_name=os.environ.get("SENDGRID_FROM_NAME", "PCG Arena"),
        frontend_url=os.environ.get("ARENA_FRONTEND_URL", "http://localhost:3000"),
    )

