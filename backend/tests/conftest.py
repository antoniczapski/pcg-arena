"""
Test fixtures for PCG Arena backend.

Provides:
- Temporary SQLite database
- FastAPI test client
- Seed data import
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

import pytest

# Add src to path BEFORE any imports
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))


@pytest.fixture(scope="session")
def setup_env():
    """Set up test environment variables."""
    # Create temp directory for test database
    temp_dir = tempfile.mkdtemp(prefix="pcg_arena_test_")
    
    # Get paths relative to project root
    project_root = Path(__file__).parent.parent.parent
    migrations_path = project_root / "db" / "migrations"
    seed_path = project_root / "db" / "seed"
    
    os.environ["ARENA_DB_PATH"] = str(Path(temp_dir) / "test_arena.sqlite")
    os.environ["ARENA_MIGRATIONS_PATH"] = str(migrations_path)
    os.environ["ARENA_SEED_PATH"] = str(seed_path)
    os.environ["ARENA_HOST"] = "127.0.0.1"
    os.environ["ARENA_PORT"] = "8081"
    os.environ["ARENA_DEBUG"] = "true"
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="module")
def test_db(setup_env):
    """Initialize test database with migrations and seed data."""
    temp_dir = setup_env
    
    # Import after env is set
    from db import init_connection, run_migrations, import_generators, import_levels, init_generator_ratings, close_connection, get_connection
    from config import load_config
    
    config = load_config()
    
    # Initialize fresh DB
    conn = init_connection(config.db_path)
    applied = run_migrations(config.migrations_path)
    gen_count = import_generators(config.seed_path)
    level_count = import_levels(config.seed_path)
    ratings_init = init_generator_ratings(config.initial_rating)
    
    # Get total migrations count from schema_migrations table
    cursor = conn.execute("SELECT COUNT(*) as count FROM schema_migrations")
    total_migrations = cursor.fetchone()[0]
    
    yield {
        "db_path": config.db_path,
        "migrations_applied": total_migrations,  # Total migrations in DB, not just newly applied
        "generators": gen_count,
        "levels": level_count,
        "ratings_init": ratings_init,
    }
    
    # Cleanup
    close_connection()


@pytest.fixture
def client(test_db):
    """Create test client for FastAPI app using Starlette TestClient."""
    from starlette.testclient import TestClient
    from main import app
    
    # Use TestClient for synchronous testing
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

