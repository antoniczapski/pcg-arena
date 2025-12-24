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
    
    # Rating system
    initial_rating: float
    k_factor: float
    
    # Paths (inside container)
    migrations_path: str
    seed_path: str


def load_config() -> Config:
    """Load configuration from environment variables."""
    return Config(
        db_path=os.environ.get("ARENA_DB_PATH", "/data/arena.sqlite"),
        host=os.environ.get("ARENA_HOST", "0.0.0.0"),
        port=int(os.environ.get("ARENA_PORT", "8080")),
        initial_rating=float(os.environ.get("ARENA_INITIAL_RATING", "1000.0")),
        k_factor=float(os.environ.get("ARENA_K_FACTOR", "24")),
        migrations_path=os.environ.get("ARENA_MIGRATIONS_PATH", "/migrations"),
        seed_path=os.environ.get("ARENA_SEED_PATH", "/seed"),
    )

