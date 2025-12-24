"""
Database connection management for PCG Arena.
Protocol: arena/v0

Provides SQLite connection with proper configuration:
- Foreign keys enabled (PRAGMA foreign_keys = ON)
- WAL mode for better concurrency
"""

import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)

# Global connection holder (Stage 0: single connection is fine)
_connection: sqlite3.Connection | None = None


def init_connection(db_path: str) -> sqlite3.Connection:
    """
    Initialize the database connection with proper SQLite settings.
    
    Args:
        db_path: Path to the SQLite database file.
        
    Returns:
        Configured SQLite connection.
        
    Note:
        Creates parent directories if they don't exist.
        Enables foreign keys (required per-connection in SQLite).
    """
    global _connection
    
    # Ensure parent directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Connecting to database: {db_path}")
    
    # Create connection
    conn = sqlite3.connect(db_path, check_same_thread=False)
    
    # Enable foreign keys (MUST be done per-connection in SQLite)
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Enable WAL mode for better concurrency
    conn.execute("PRAGMA journal_mode = WAL")
    
    # Return dict-like rows
    conn.row_factory = sqlite3.Row
    
    _connection = conn
    logger.info("Database connection initialized successfully")
    
    return conn


def get_connection() -> sqlite3.Connection:
    """
    Get the current database connection.
    
    Returns:
        The active SQLite connection.
        
    Raises:
        RuntimeError: If connection has not been initialized.
    """
    if _connection is None:
        raise RuntimeError("Database connection not initialized. Call init_connection first.")
    return _connection


@contextmanager
def transaction() -> Generator[sqlite3.Cursor, None, None]:
    """
    Context manager for database transactions.
    
    Commits on success, rolls back on exception.
    
    Yields:
        Database cursor.
        
    Example:
        with transaction() as cursor:
            cursor.execute("INSERT INTO ...")
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


def close_connection() -> None:
    """Close the database connection if open."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None
        logger.info("Database connection closed")

