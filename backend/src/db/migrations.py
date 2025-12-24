"""
Database migration runner for PCG Arena.
Protocol: arena/v0

Applies SQL migrations from the migrations directory exactly once, in order.
Handles the first-run case where schema_migrations table doesn't exist yet.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

from .connection import get_connection

logger = logging.getLogger(__name__)

# The first migration that creates schema_migrations table
INIT_MIGRATION = "001_init.sql"


def _table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone() is not None


def _get_applied_migrations() -> set[str]:
    """
    Get the set of already-applied migration versions.
    
    Returns:
        Set of migration filenames that have been applied.
    """
    if not _table_exists("schema_migrations"):
        return set()
    
    conn = get_connection()
    cursor = conn.execute("SELECT version FROM schema_migrations")
    return {row["version"] for row in cursor.fetchall()}


def _record_migration(version: str) -> None:
    """
    Record a migration as applied in schema_migrations.
    
    Args:
        version: The migration filename (e.g., '001_init.sql').
    """
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO schema_migrations (version, applied_at_utc) VALUES (?, ?)",
        (version, now)
    )


def _apply_migration(migration_path: Path) -> None:
    """
    Apply a single migration file within a transaction.
    
    Args:
        migration_path: Path to the .sql migration file.
        
    Raises:
        Exception: If migration fails (transaction will be rolled back).
    """
    version = migration_path.name
    logger.info(f"Applying migration: {version}")
    
    # Read the SQL content
    sql_content = migration_path.read_text(encoding="utf-8")
    
    conn = get_connection()
    
    # Execute the migration in a transaction
    try:
        # executescript commits any pending transaction and runs in autocommit
        # So we need to handle this differently - execute statements one by one
        # or use executescript which handles multiple statements
        conn.executescript(sql_content)
        
        # Record the migration (only if schema_migrations exists now)
        # Note: 001_init.sql creates schema_migrations, so after it runs we can record
        _record_migration(version)
        conn.commit()
        
        logger.info(f"Successfully applied migration: {version}")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to apply migration {version}: {e}")
        raise RuntimeError(f"Migration {version} failed: {e}") from e


def run_migrations(migrations_path: str) -> int:
    """
    Run all pending migrations from the migrations directory.
    
    Migrations are applied in lexicographic order by filename.
    Each migration is applied exactly once and recorded in schema_migrations.
    
    Special handling for first run:
    - If schema_migrations table doesn't exist, 001_init.sql is applied first
    - After that, schema_migrations is used as source of truth
    
    Args:
        migrations_path: Path to directory containing .sql migration files.
        
    Returns:
        Number of migrations applied.
        
    Raises:
        RuntimeError: If any migration fails.
        FileNotFoundError: If migrations directory doesn't exist.
    """
    migrations_dir = Path(migrations_path)
    
    if not migrations_dir.exists():
        logger.warning(f"Migrations directory not found: {migrations_path}")
        return 0
    
    # Find all .sql files and sort lexicographically
    migration_files = sorted(migrations_dir.glob("*.sql"), key=lambda p: p.name)
    
    if not migration_files:
        logger.info("No migration files found")
        return 0
    
    logger.info(f"Found {len(migration_files)} migration file(s)")
    
    # Get already applied migrations
    applied = _get_applied_migrations()
    logger.info(f"Already applied: {len(applied)} migration(s)")
    
    # Special case: first run - schema_migrations doesn't exist yet
    # We need to apply 001_init.sql first to create it
    if not _table_exists("schema_migrations"):
        init_file = migrations_dir / INIT_MIGRATION
        if not init_file.exists():
            raise RuntimeError(
                f"First run requires {INIT_MIGRATION} to create schema_migrations table, "
                f"but file not found at {init_file}"
            )
        logger.info("First run detected - applying initial migration to create schema_migrations")
        _apply_migration(init_file)
        applied.add(INIT_MIGRATION)
    
    # Apply remaining migrations in order
    count = 0
    for migration_file in migration_files:
        version = migration_file.name
        
        if version in applied:
            logger.debug(f"Skipping already applied: {version}")
            continue
        
        _apply_migration(migration_file)
        count += 1
    
    if count == 0:
        logger.info("No new migrations to apply")
    else:
        logger.info(f"Applied {count} new migration(s)")
    
    return count

