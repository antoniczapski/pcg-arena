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
    
    # Rating system
    initial_rating: float
    k_factor: float
    
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
        k_factor=float(os.environ.get("ARENA_K_FACTOR", "24")),
        migrations_path=os.environ.get("ARENA_MIGRATIONS_PATH", "/migrations"),
        seed_path=os.environ.get("ARENA_SEED_PATH", "/seed"),
        backup_path=os.environ.get("ARENA_BACKUP_PATH", "/backups"),
        debug=os.environ.get("ARENA_DEBUG", "false").lower() in ("true", "1", "yes"),
        admin_key=os.environ.get("ARENA_ADMIN_KEY", ""),
        allowed_origins=allowed_origins,
        log_level=os.environ.get("ARENA_LOG_LEVEL", "INFO").upper(),
    )

