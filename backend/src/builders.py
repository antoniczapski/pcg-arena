"""
PCG Arena - Builder Profile Module
Protocol: arena/v0

Handles generator submission and management for authenticated users:
- List user's generators
- Create new generator with levels (ZIP upload)
- Update generator version (replace levels, keep rating)
- Delete generator
"""

import uuid
import json
import zipfile
import io
import logging
import re
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import UploadFile, HTTPException
from pydantic import BaseModel, Field

from config import load_config
from db import get_connection, transaction
from db.seed import validate_level, compute_content_hash, LevelValidationError

logger = logging.getLogger(__name__)
config = load_config()

# Builder constraints
MAX_GENERATORS_PER_USER = 3
MIN_LEVELS_PER_GENERATOR = 50
MAX_LEVELS_PER_GENERATOR = 200
MAX_ZIP_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# Generator ID validation pattern (alphanumeric, hyphens, underscores)
GENERATOR_ID_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]{2,31}$')


class GeneratorMetadata(BaseModel):
    """Metadata for a new generator submission."""
    generator_id: str = Field(..., min_length=3, max_length=32)
    name: str = Field(..., min_length=3, max_length=100)
    version: str = Field(default="1.0.0", max_length=20)
    description: str = Field(default="", max_length=1000)
    tags: List[str] = Field(default_factory=list, max_length=10)
    documentation_url: Optional[str] = Field(default=None, max_length=500)


class GeneratorInfo(BaseModel):
    """Generator info for API responses."""
    generator_id: str
    name: str
    version: str
    description: str
    tags: List[str]
    documentation_url: Optional[str]
    is_active: bool
    level_count: int
    rating: float
    games_played: int
    wins: int
    losses: int
    ties: int
    created_at_utc: str
    updated_at_utc: str


class BuilderError(Exception):
    """Custom exception for builder-related errors."""
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def validate_generator_id(generator_id: str) -> None:
    """Validate generator ID format."""
    if not GENERATOR_ID_PATTERN.match(generator_id):
        raise BuilderError(
            "INVALID_GENERATOR_ID",
            f"Generator ID must be 3-32 characters, start with a letter, and contain only alphanumeric characters, hyphens, and underscores",
            400
        )


def get_user_generators(user_id: str) -> List[GeneratorInfo]:
    """
    Get all generators owned by a user.
    
    Args:
        user_id: The user's ID
    
    Returns:
        List of GeneratorInfo objects
    """
    conn = get_connection()
    
    cursor = conn.execute(
        """
        SELECT 
            g.generator_id, g.name, g.version, g.description, g.tags_json,
            g.documentation_url, g.is_active, g.created_at_utc, g.updated_at_utc,
            COUNT(l.level_id) as level_count,
            COALESCE(r.rating_value, 1000.0) as rating,
            COALESCE(r.games_played, 0) as games_played,
            COALESCE(r.wins, 0) as wins,
            COALESCE(r.losses, 0) as losses,
            COALESCE(r.ties, 0) as ties
        FROM generators g
        LEFT JOIN levels l ON g.generator_id = l.generator_id
        LEFT JOIN ratings r ON g.generator_id = r.generator_id
        WHERE g.owner_user_id = ?
        GROUP BY g.generator_id
        ORDER BY g.created_at_utc DESC
        """,
        (user_id,)
    )
    
    generators = []
    for row in cursor.fetchall():
        tags = json.loads(row["tags_json"]) if row["tags_json"] else []
        generators.append(GeneratorInfo(
            generator_id=row["generator_id"],
            name=row["name"],
            version=row["version"],
            description=row["description"],
            tags=tags,
            documentation_url=row["documentation_url"],
            is_active=bool(row["is_active"]),
            level_count=row["level_count"],
            rating=row["rating"],
            games_played=row["games_played"],
            wins=row["wins"],
            losses=row["losses"],
            ties=row["ties"],
            created_at_utc=row["created_at_utc"],
            updated_at_utc=row["updated_at_utc"]
        ))
    
    return generators


def get_user_generator_count(user_id: str) -> int:
    """Get the number of generators owned by a user."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT COUNT(*) as count FROM generators WHERE owner_user_id = ?",
        (user_id,)
    )
    return cursor.fetchone()["count"]


def generator_id_exists(generator_id: str) -> bool:
    """Check if a generator ID already exists."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT 1 FROM generators WHERE generator_id = ?",
        (generator_id,)
    )
    return cursor.fetchone() is not None


def is_generator_owner(generator_id: str, user_id: str) -> bool:
    """Check if a user owns a specific generator."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT 1 FROM generators WHERE generator_id = ? AND owner_user_id = ?",
        (generator_id, user_id)
    )
    return cursor.fetchone() is not None


async def process_levels_zip(zip_file: UploadFile) -> List[tuple]:
    """
    Process a ZIP file containing level files.
    
    Args:
        zip_file: The uploaded ZIP file
    
    Returns:
        List of tuples (filename, tilemap, width, content_hash)
    
    Raises:
        BuilderError: If ZIP is invalid or levels fail validation
    """
    # Read ZIP file content
    content = await zip_file.read()
    
    if len(content) > MAX_ZIP_SIZE_BYTES:
        raise BuilderError(
            "ZIP_TOO_LARGE",
            f"ZIP file exceeds maximum size of {MAX_ZIP_SIZE_BYTES // (1024 * 1024)} MB",
            400
        )
    
    levels = []
    errors = []
    
    try:
        with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
            # Get all .txt files
            txt_files = [f for f in zf.namelist() if f.endswith('.txt') and not f.startswith('__MACOSX')]
            
            if len(txt_files) < MIN_LEVELS_PER_GENERATOR:
                raise BuilderError(
                    "NOT_ENOUGH_LEVELS",
                    f"ZIP must contain at least {MIN_LEVELS_PER_GENERATOR} level files, found {len(txt_files)}",
                    400
                )
            
            if len(txt_files) > MAX_LEVELS_PER_GENERATOR:
                raise BuilderError(
                    "TOO_MANY_LEVELS",
                    f"ZIP contains {len(txt_files)} levels, maximum is {MAX_LEVELS_PER_GENERATOR}",
                    400
                )
            
            for filename in txt_files:
                try:
                    # Read file content
                    raw_content = zf.read(filename).decode('utf-8')
                    
                    # Get just the filename without path
                    base_filename = filename.split('/')[-1]
                    
                    # Validate level (returns tilemap, width, height)
                    tilemap, width, height = validate_level(raw_content, base_filename)
                    content_hash = compute_content_hash(tilemap)
                    
                    levels.append((base_filename, tilemap, width, height, content_hash))
                    
                except LevelValidationError as e:
                    errors.append(str(e))
                except UnicodeDecodeError:
                    errors.append(f"{filename}: Not a valid UTF-8 text file")
    
    except zipfile.BadZipFile:
        raise BuilderError(
            "INVALID_ZIP",
            "The uploaded file is not a valid ZIP archive",
            400
        )
    
    if errors:
        # If more than 5 errors, truncate
        error_summary = errors[:5]
        if len(errors) > 5:
            error_summary.append(f"... and {len(errors) - 5} more errors")
        
        raise BuilderError(
            "LEVEL_VALIDATION_FAILED",
            f"Level validation failed:\n" + "\n".join(error_summary),
            400
        )
    
    return levels


async def create_generator(
    user_id: str,
    metadata: GeneratorMetadata,
    zip_file: UploadFile
) -> GeneratorInfo:
    """
    Create a new generator with levels.
    
    Args:
        user_id: The owner's user ID
        metadata: Generator metadata
        zip_file: ZIP file containing level files
    
    Returns:
        The created GeneratorInfo
    
    Raises:
        BuilderError: If validation fails or limits exceeded
    """
    # Validate generator ID format
    validate_generator_id(metadata.generator_id)
    
    # Check user hasn't exceeded limit
    current_count = get_user_generator_count(user_id)
    if current_count >= MAX_GENERATORS_PER_USER:
        raise BuilderError(
            "MAX_GENERATORS_EXCEEDED",
            f"You can only have {MAX_GENERATORS_PER_USER} generators. Delete one to add a new one.",
            400
        )
    
    # Check generator ID doesn't already exist
    if generator_id_exists(metadata.generator_id):
        raise BuilderError(
            "GENERATOR_ID_EXISTS",
            f"Generator ID '{metadata.generator_id}' is already taken",
            409
        )
    
    # Process ZIP file
    levels = await process_levels_zip(zip_file)
    
    conn = get_connection()
    now_utc = datetime.now(timezone.utc).isoformat()
    
    try:
        with transaction() as cursor:
            # Insert generator
            tags_json = json.dumps(metadata.tags)
            cursor.execute(
                """
                INSERT INTO generators (
                    generator_id, name, version, description, tags_json,
                    documentation_url, is_active, owner_user_id,
                    created_at_utc, updated_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
                """,
                (
                    metadata.generator_id,
                    metadata.name,
                    metadata.version,
                    metadata.description,
                    tags_json,
                    metadata.documentation_url,
                    user_id,
                    now_utc,
                    now_utc
                )
            )
            
            # Insert levels
            for filename, tilemap, width, height, content_hash in levels:
                level_id = f"{metadata.generator_id}::{filename}"
                cursor.execute(
                    """
                    INSERT INTO levels (
                        level_id, generator_id, content_format, width, height,
                        tilemap_text, content_hash, seed, controls_json, created_at_utc
                    ) VALUES (?, ?, 'ASCII_TILEMAP', ?, ?, ?, ?, NULL, '{}', ?)
                    """,
                    (level_id, metadata.generator_id, width, height, tilemap, content_hash, now_utc)
                )
            
            # Initialize Glicko-2 rating
            cursor.execute(
                """
                INSERT INTO ratings (
                    generator_id, rating_value, rd, volatility,
                    games_played, wins, losses, ties, skips, updated_at_utc
                ) VALUES (?, ?, ?, ?, 0, 0, 0, 0, 0, ?)
                """,
                (metadata.generator_id, config.initial_rating, config.initial_rd, 
                 config.initial_volatility, now_utc)
            )
        
        logger.info(f"Created generator: generator_id={metadata.generator_id} owner={user_id} levels={len(levels)}")
        
        return GeneratorInfo(
            generator_id=metadata.generator_id,
            name=metadata.name,
            version=metadata.version,
            description=metadata.description,
            tags=metadata.tags,
            documentation_url=metadata.documentation_url,
            is_active=True,
            level_count=len(levels),
            rating=config.initial_rating,
            games_played=0,
            wins=0,
            losses=0,
            ties=0,
            created_at_utc=now_utc,
            updated_at_utc=now_utc
        )
    
    except Exception as e:
        logger.error(f"Failed to create generator: {e}")
        raise BuilderError(
            "CREATE_FAILED",
            f"Failed to create generator: {str(e)}",
            500
        )


async def update_generator(
    user_id: str,
    generator_id: str,
    metadata: GeneratorMetadata,
    zip_file: UploadFile
) -> GeneratorInfo:
    """
    Update a generator with new levels (new version).
    
    Keeps rating and games_played, replaces all levels.
    
    Args:
        user_id: The owner's user ID
        generator_id: The generator to update
        metadata: Updated generator metadata
        zip_file: ZIP file containing new level files
    
    Returns:
        The updated GeneratorInfo
    
    Raises:
        BuilderError: If validation fails or user doesn't own generator
    """
    # Check ownership
    if not is_generator_owner(generator_id, user_id):
        raise BuilderError(
            "NOT_OWNER",
            "You don't have permission to update this generator",
            403
        )
    
    # Process ZIP file
    levels = await process_levels_zip(zip_file)
    
    conn = get_connection()
    now_utc = datetime.now(timezone.utc).isoformat()
    
    try:
        with transaction() as cursor:
            # Delete old levels that are NOT referenced by battles
            # This preserves historical battle data while allowing updates
            cursor.execute(
                """
                DELETE FROM levels 
                WHERE generator_id = ? 
                AND level_id NOT IN (
                    SELECT left_level_id FROM battles WHERE left_generator_id = ?
                    UNION
                    SELECT right_level_id FROM battles WHERE right_generator_id = ?
                )
                """,
                (generator_id, generator_id, generator_id)
            )
            
            # Update generator metadata
            tags_json = json.dumps(metadata.tags)
            cursor.execute(
                """
                UPDATE generators SET
                    name = ?,
                    version = ?,
                    description = ?,
                    tags_json = ?,
                    documentation_url = ?,
                    updated_at_utc = ?
                WHERE generator_id = ?
                """,
                (
                    metadata.name,
                    metadata.version,
                    metadata.description,
                    tags_json,
                    metadata.documentation_url,
                    now_utc,
                    generator_id
                )
            )
            
            # Insert or replace new levels
            # Using INSERT OR REPLACE to handle levels that might already exist
            # (e.g., if same filename as a level referenced by battles)
            for filename, tilemap, width, height, content_hash in levels:
                level_id = f"{generator_id}::{filename}"
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO levels (
                        level_id, generator_id, content_format, width, height,
                        tilemap_text, content_hash, seed, controls_json, created_at_utc
                    ) VALUES (?, ?, 'ASCII_TILEMAP', ?, ?, ?, ?, NULL, '{}', ?)
                    """,
                    (level_id, generator_id, width, height, tilemap, content_hash, now_utc)
                )
        
        logger.info(f"Updated generator: generator_id={generator_id} owner={user_id} new_levels={len(levels)}")
        
        # Get current rating info and actual level count
        rating_cursor = conn.execute(
            """
            SELECT rating_value, games_played, wins, losses, ties
            FROM ratings WHERE generator_id = ?
            """,
            (generator_id,)
        )
        rating_row = rating_cursor.fetchone()
        
        # Get actual level count (may include some historical levels)
        level_count_row = conn.execute(
            "SELECT COUNT(*) as count FROM levels WHERE generator_id = ?",
            (generator_id,)
        ).fetchone()
        actual_level_count = level_count_row["count"] if level_count_row else len(levels)
        
        return GeneratorInfo(
            generator_id=generator_id,
            name=metadata.name,
            version=metadata.version,
            description=metadata.description,
            tags=metadata.tags,
            documentation_url=metadata.documentation_url,
            is_active=True,
            level_count=actual_level_count,
            rating=rating_row["rating_value"] if rating_row else config.initial_rating,
            games_played=rating_row["games_played"] if rating_row else 0,
            wins=rating_row["wins"] if rating_row else 0,
            losses=rating_row["losses"] if rating_row else 0,
            ties=rating_row["ties"] if rating_row else 0,
            created_at_utc=now_utc,  # Will be overwritten by actual value
            updated_at_utc=now_utc
        )
    
    except BuilderError:
        raise
    except Exception as e:
        logger.error(f"Failed to update generator: {e}")
        raise BuilderError(
            "UPDATE_FAILED",
            f"Failed to update generator: {str(e)}",
            500
        )


def delete_generator(user_id: str, generator_id: str) -> None:
    """
    Delete a generator and all its levels.
    
    If the generator has battles (historical data), it will be "soft deleted"
    by marking it as inactive and removing user ownership, rather than 
    actually deleting it (to preserve battle history).
    
    Args:
        user_id: The owner's user ID
        generator_id: The generator to delete
    
    Raises:
        BuilderError: If user doesn't own generator
    """
    # Check ownership
    if not is_generator_owner(generator_id, user_id):
        raise BuilderError(
            "NOT_OWNER",
            "You don't have permission to delete this generator",
            403
        )
    
    conn = get_connection()
    
    # Check if generator has battles
    has_battles = conn.execute(
        """
        SELECT COUNT(*) as count FROM battles 
        WHERE left_generator_id = ? OR right_generator_id = ?
        """,
        (generator_id, generator_id)
    ).fetchone()["count"] > 0
    
    try:
        with transaction() as cursor:
            if has_battles:
                # Soft delete: mark as inactive and remove owner
                # This preserves battle history while hiding from user
                cursor.execute(
                    """
                    UPDATE generators 
                    SET is_active = 0, 
                        owner_user_id = NULL,
                        name = name || ' [deleted]',
                        updated_at_utc = ?
                    WHERE generator_id = ?
                    """,
                    (datetime.now(timezone.utc).isoformat(), generator_id)
                )
                logger.info(f"Soft-deleted generator (has battles): generator_id={generator_id} owner={user_id}")
            else:
                # Hard delete: no battles, safe to remove everything
                # Delete levels first (foreign key)
                cursor.execute(
                    "DELETE FROM levels WHERE generator_id = ?",
                    (generator_id,)
                )
                
                # Delete rating
                cursor.execute(
                    "DELETE FROM ratings WHERE generator_id = ?",
                    (generator_id,)
                )
                
                # Delete generator
                cursor.execute(
                    "DELETE FROM generators WHERE generator_id = ?",
                    (generator_id,)
                )
                logger.info(f"Hard-deleted generator: generator_id={generator_id} owner={user_id}")
    
    except Exception as e:
        logger.error(f"Failed to delete generator: {e}")
        raise BuilderError(
            "DELETE_FAILED",
            f"Failed to delete generator: {str(e)}",
            500
        )

