"""
Seed data importer for PCG Arena.
Protocol: arena/v0

Imports generator metadata and level data from seed files into the database.
Uses upsert logic to safely re-run on startup without duplicating data.
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .connection import get_connection

logger = logging.getLogger(__name__)

# Level format constants (Stage 0)
MAX_LEVEL_WIDTH = 250
MIN_LEVEL_WIDTH = 1
LEVEL_HEIGHT = 16

# Allowed tile characters (Stage 0 strict alphabet from spec)
ALLOWED_TILES = set(
    "-"   # Air
    "M"   # Mario start
    "F"   # Level exit / flag
    "y"   # Spiky
    "Y"   # Winged Spiky
    "E"   # Goomba
    "g"   # Goomba (alt)
    "G"   # Winged Goomba
    "k"   # Green Koopa
    "K"   # Winged Green Koopa
    "r"   # Red Koopa
    "R"   # Winged Red Koopa
    "X"   # Solid floor block
    "#"   # Pyramid block
    "S"   # Normal solid block
    "D"   # Used block
    "%"   # Jump-through platform
    "|"   # Background for platform
    "?"   # Question block (mushroom)
    "@"   # Question block (mushroom alt)
    "Q"   # Question block (coin)
    "!"   # Question block (coin alt)
    "C"   # Coin block
    "U"   # Mushroom block
    "L"   # 1-Up block
    "1"   # Invisible 1-Up block
    "2"   # Invisible coin block
    "o"   # Free-standing coin
    "t"   # Empty pipe
    "T"   # Flower pipe
    "<"   # Pipe top left
    ">"   # Pipe top right
    "["   # Pipe body left
    "]"   # Pipe body right
    "*"   # Bullet Bill launcher body
    "B"   # Bullet Bill head
    "b"   # Bullet Bill neck/body
)


def import_generators(seed_path: str) -> int:
    """
    Import generators from generators.json into the database.
    
    Uses upsert logic: inserts new generators, updates existing ones.
    
    Args:
        seed_path: Path to the seed directory containing generators.json.
        
    Returns:
        Number of generators imported/updated.
        
    Raises:
        FileNotFoundError: If generators.json doesn't exist.
        json.JSONDecodeError: If JSON is malformed.
    """
    seed_dir = Path(seed_path)
    generators_file = seed_dir / "generators.json"
    
    if not generators_file.exists():
        logger.warning(f"generators.json not found at {generators_file}")
        return 0
    
    logger.info(f"Importing generators from {generators_file}")
    
    # Read and parse JSON
    with open(generators_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    generators = data.get("generators", [])
    if not generators:
        logger.warning("No generators found in generators.json")
        return 0
    
    logger.info(f"Found {len(generators)} generator(s) in generators.json")
    
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    
    count = 0
    for gen in generators:
        generator_id = gen.get("generator_id")
        if not generator_id:
            logger.warning(f"Skipping generator without generator_id: {gen}")
            continue
        
        # Prepare fields
        name = gen.get("name", generator_id)
        version = gen.get("version", "1.0.0")
        description = gen.get("description", "")
        documentation_url = gen.get("documentation_url")
        tags = gen.get("tags", [])
        tags_json = json.dumps(tags)
        
        # Upsert: INSERT OR UPDATE on conflict
        # SQLite supports INSERT ... ON CONFLICT since 3.24.0
        conn.execute(
            """
            INSERT INTO generators (
                generator_id, name, version, description, tags_json,
                documentation_url, is_active, created_at_utc, updated_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            ON CONFLICT(generator_id) DO UPDATE SET
                name = excluded.name,
                version = excluded.version,
                description = excluded.description,
                tags_json = excluded.tags_json,
                documentation_url = excluded.documentation_url,
                updated_at_utc = excluded.updated_at_utc
            """,
            (generator_id, name, version, description, tags_json,
             documentation_url, now, now)
        )
        
        logger.debug(f"Upserted generator: {generator_id}")
        count += 1
    
    conn.commit()
    logger.info(f"Imported {count} generator(s)")
    
    return count


def init_generator_ratings(
    initial_rating: float = 1000.0,
    initial_rd: float = 350.0,
    initial_volatility: float = 0.06
) -> int:
    """
    Initialize ratings for generators that don't have a ratings row yet.
    
    Uses Glicko-2 rating system with rating deviation (RD) and volatility.
    
    Args:
        initial_rating: The starting rating value for new generators.
        initial_rd: The starting rating deviation (uncertainty). High = uncertain.
        initial_volatility: The starting volatility (expected fluctuation).
        
    Returns:
        Number of ratings initialized.
    """
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    
    # Find generators without ratings
    cursor = conn.execute(
        """
        SELECT g.generator_id
        FROM generators g
        LEFT JOIN ratings r ON g.generator_id = r.generator_id
        WHERE r.generator_id IS NULL AND g.is_active = 1
        """
    )
    
    missing = [row["generator_id"] for row in cursor.fetchall()]
    
    if not missing:
        logger.debug("All generators already have ratings")
        return 0
    
    logger.info(f"Initializing Glicko-2 ratings for {len(missing)} generator(s)")
    
    for generator_id in missing:
        conn.execute(
            """
            INSERT INTO ratings (
                generator_id, rating_value, rd, volatility,
                games_played, wins, losses, ties, skips, updated_at_utc
            ) VALUES (?, ?, ?, ?, 0, 0, 0, 0, 0, ?)
            """,
            (generator_id, initial_rating, initial_rd, initial_volatility, now)
        )
        logger.debug(f"Initialized Glicko-2 rating for: {generator_id} (rating={initial_rating}, rd={initial_rd})")
    
    conn.commit()
    logger.info(f"Initialized {len(missing)} Glicko-2 rating(s)")
    
    return len(missing)


class LevelValidationError(Exception):
    """Raised when a level file fails validation."""
    pass


def validate_level(content: str, filename: str) -> tuple[str, int]:
    """
    Validate a level file and return the canonical tilemap with its width.
    
    Args:
        content: Raw file content (may have \\r\\n newlines).
        filename: Filename for error messages.
        
    Returns:
        Tuple of (canonical tilemap with \\n newlines, width).
        
    Raises:
        LevelValidationError: If validation fails.
    """
    # Normalize newlines: accept \r\n but convert to \n
    content = content.replace("\r\n", "\n")
    
    # Remove trailing newline if present
    if content.endswith("\n"):
        content = content[:-1]
    
    # Split into lines
    lines = content.split("\n")
    
    # Check line count
    if len(lines) != LEVEL_HEIGHT:
        raise LevelValidationError(
            f"{filename}: Expected {LEVEL_HEIGHT} lines, got {len(lines)}"
        )
    
    # Determine width from first line
    width = len(lines[0])
    
    # Check width bounds
    if width < MIN_LEVEL_WIDTH:
        raise LevelValidationError(
            f"{filename}: Width {width} is below minimum {MIN_LEVEL_WIDTH}"
        )
    if width > MAX_LEVEL_WIDTH:
        raise LevelValidationError(
            f"{filename}: Width {width} exceeds maximum {MAX_LEVEL_WIDTH}"
        )
    
    # Check each line
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Check line length matches first line (all lines must be same width)
        if len(line) != width:
            raise LevelValidationError(
                f"{filename} line {line_num}: Expected {width} chars (matching line 1), got {len(line)}"
            )
        
        # Check allowed characters
        for j, char in enumerate(line):
            if char not in ALLOWED_TILES:
                raise LevelValidationError(
                    f"{filename} line {line_num} col {j+1}: Invalid character '{char}'"
                )
    
    # Check at least one X exists (ground block)
    full_content = "\n".join(lines)

    return full_content, width


def compute_content_hash(tilemap: str) -> str:
    """
    Compute SHA-256 hash of the tilemap content.
    
    Args:
        tilemap: The canonical tilemap string.
        
    Returns:
        Hash in format "sha256:<hex>".
    """
    content_bytes = tilemap.encode("utf-8")
    hash_hex = hashlib.sha256(content_bytes).hexdigest()
    return f"sha256:{hash_hex}"


def import_levels(seed_path: str) -> int:
    """
    Import levels from the seed/levels directory structure.
    
    Directory structure: seed/levels/<generator_id>/*.txt
    Level ID format: <generator_id>::<filename>
    
    Args:
        seed_path: Path to the seed directory.
        
    Returns:
        Number of levels imported/updated.
    """
    seed_dir = Path(seed_path)
    levels_dir = seed_dir / "levels"
    
    if not levels_dir.exists():
        logger.warning(f"Levels directory not found at {levels_dir}")
        return 0
    
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    
    # Get set of valid generator IDs
    cursor = conn.execute("SELECT generator_id FROM generators")
    valid_generators = {row["generator_id"] for row in cursor.fetchall()}
    
    if not valid_generators:
        logger.warning("No generators in database - import generators first")
        return 0
    
    count = 0
    errors = 0
    
    # Iterate over generator directories
    for gen_dir in levels_dir.iterdir():
        if not gen_dir.is_dir():
            continue
        
        generator_id = gen_dir.name
        
        if generator_id not in valid_generators:
            logger.warning(f"Skipping levels for unknown generator: {generator_id}")
            continue
        
        # Find all .txt files in this generator's directory
        level_files = sorted(gen_dir.glob("*.txt"))
        
        if not level_files:
            logger.debug(f"No level files found for generator: {generator_id}")
            continue
        
        logger.info(f"Importing {len(level_files)} level(s) for generator: {generator_id}")
        
        for level_file in level_files:
            try:
                # Read file content
                raw_content = level_file.read_text(encoding="utf-8")
                
                # Validate and normalize (returns tilemap and detected width)
                tilemap, width = validate_level(raw_content, level_file.name)
                
                # Compute hash
                content_hash = compute_content_hash(tilemap)
                
                # Generate level ID: <generator_id>::<filename>
                level_id = f"{generator_id}::{level_file.name}"
                
                # Upsert level
                conn.execute(
                    """
                    INSERT INTO levels (
                        level_id, generator_id, content_format, width, height,
                        tilemap_text, content_hash, seed, controls_json, created_at_utc
                    ) VALUES (?, ?, 'ASCII_TILEMAP', ?, ?, ?, ?, NULL, '{}', ?)
                    ON CONFLICT(level_id) DO UPDATE SET
                        tilemap_text = excluded.tilemap_text,
                        content_hash = excluded.content_hash,
                        width = excluded.width
                    """,
                    (level_id, generator_id, width, LEVEL_HEIGHT,
                     tilemap, content_hash, now)
                )
                
                count += 1
                logger.debug(f"Upserted level: {level_id}")
                
            except LevelValidationError as e:
                logger.error(f"Validation error: {e}")
                errors += 1
            except Exception as e:
                logger.error(f"Failed to import {level_file}: {e}")
                errors += 1
    
    conn.commit()
    
    if errors > 0:
        logger.warning(f"Imported {count} level(s) with {errors} error(s)")
    else:
        logger.info(f"Imported {count} level(s)")
    
    return count


def get_db_status(db_path: str) -> dict:
    """
    Get database status summary for logging.
    
    Args:
        db_path: Path to the SQLite database file.
        
    Returns:
        Dictionary with counts and metadata.
    """
    import os
    
    conn = get_connection()
    
    # Get counts
    gen_count = conn.execute("SELECT COUNT(*) FROM generators").fetchone()[0]
    level_count = conn.execute("SELECT COUNT(*) FROM levels").fetchone()[0]
    rating_count = conn.execute("SELECT COUNT(*) FROM ratings").fetchone()[0]
    
    # Get applied migrations
    cursor = conn.execute(
        "SELECT version FROM schema_migrations ORDER BY version"
    )
    migrations = [row["version"] for row in cursor.fetchall()]
    
    # Get file size
    db_file = Path(db_path)
    file_size_bytes = db_file.stat().st_size if db_file.exists() else 0
    
    # Format size nicely
    if file_size_bytes < 1024:
        size_str = f"{file_size_bytes}B"
    elif file_size_bytes < 1024 * 1024:
        size_str = f"{file_size_bytes / 1024:.1f}KB"
    else:
        size_str = f"{file_size_bytes / (1024 * 1024):.1f}MB"
    
    return {
        "generators": gen_count,
        "levels": level_count,
        "ratings": rating_count,
        "migrations": migrations,
        "db_path": str(db_path),
        "db_size": size_str,
    }


def log_db_status(db_path: str) -> None:
    """
    Log a single-line DB status summary.
    
    Args:
        db_path: Path to the SQLite database file.
    """
    status = get_db_status(db_path)
    migrations_str = ",".join(status["migrations"])
    
    logger.info(
        f"DB ready: generators={status['generators']} "
        f"levels={status['levels']} ratings={status['ratings']} "
        f"migrations=[{migrations_str}] "
        f"path={status['db_path']} size={status['db_size']}"
    )

