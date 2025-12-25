"""
PCG Arena Backend - Main Entry Point
Protocol: arena/v0

This module initializes the application:
1. Loads configuration
2. Initializes database connection
3. Runs pending migrations
4. Starts the API server
"""

import logging
import sys
import uuid
import random
import json
import sqlite3
import hashlib
import math
import time
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI, Request, Header, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import load_config
from db import init_connection, get_connection, run_migrations, import_generators, init_generator_ratings, import_levels, log_db_status, transaction
from errors import APIError, api_error_handler, http_exception_handler, general_exception_handler, raise_api_error, ErrorCode
from middleware import RequestLoggingMiddleware
from models import (
    BattleRequest, BattleResponse, Battle, BattleSide, GeneratorInfo, LevelFormat, LevelPayload, LevelMetadata, 
    BattlePresentation, PlayOrder, LevelFormatType, Encoding, VoteRequest, VoteResponse, VoteResult,
    LeaderboardPreview, LeaderboardGeneratorPreview
)

# Load configuration first
config = load_config()

# Configure logging based on config
logging.basicConfig(
    level=getattr(logging, config.log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Allowed tags vocabulary (Stage 0)
ALLOWED_TAGS = {
    "fun", "boring", "good_flow", "creative", "unfair", "confusing",
    "too_hard", "too_easy", "not_mario_like"
}

# Create FastAPI app
app = FastAPI(
    title="PCG Arena",
    description="Pairwise rating platform for Mario PCG generators",
    version="0.1.0",
)

# S1-B1: Add CORS middleware for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# S1-B5: Set up rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Track server startup time for uptime
startup_time = time.time()

# Track request counts for monitoring
request_counts = {
    "total": 0,
    "battles": 0,
    "votes": 0,
}

# Register exception handlers for consistent error responses
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Register request logging middleware
app.add_middleware(RequestLoggingMiddleware)


@app.on_event("startup")
async def startup_event():
    """Initialize database and run migrations on startup."""
    logger.info("Starting PCG Arena backend...")
    logger.info(f"Protocol: arena/v0")
    
    try:
        # Initialize database connection
        init_connection(config.db_path)
        
        # Run migrations
        applied = run_migrations(config.migrations_path)
        logger.info(f"Database ready (applied {applied} new migrations)")
        
        # Import seed data: generators
        gen_count = import_generators(config.seed_path)
        logger.info(f"Generators ready ({gen_count} imported/updated)")
        
        # Import seed data: levels
        level_count = import_levels(config.seed_path)
        logger.info(f"Levels ready ({level_count} imported/updated)")
        
        # Initialize ratings for new generators
        ratings_init = init_generator_ratings(config.initial_rating)
        if ratings_init > 0:
            logger.info(f"Initialized ratings for {ratings_init} new generator(s)")
        
        # Log DB status summary
        log_db_status(config.db_path)
        
        # Task E1: Expired battles cleanup
        # Stage 0 uses expires_at_utc=NULL (no expiry), so this is skipped.
        # If needed in future: mark battles with expires_at_utc < now_utc and status=ISSUED as EXPIRED
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)


@app.get("/health")
async def health_check():
    """
    Health check endpoint (S1-B3: Enhanced for Stage 1).
    
    Returns server status, protocol version, and monitoring metrics.
    """
    conn = get_connection()
    
    # Calculate uptime
    uptime_seconds = int(time.time() - startup_time)
    
    # Get battle and vote counts
    cursor = conn.execute("SELECT COUNT(*) as count FROM battles")
    battles_served = cursor.fetchone()["count"]
    
    cursor = conn.execute("SELECT COUNT(*) as count FROM votes")
    votes_received = cursor.fetchone()["count"]
    
    # Get database size
    import os
    from pathlib import Path
    db_path = Path(config.db_path)
    db_size_bytes = db_path.stat().st_size if db_path.exists() else 0
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "status": "ok",
        "server_time_utc": datetime.now(timezone.utc).isoformat(),
        "build": {
            "backend_version": "0.1.0"
        },
        "metrics": {
            "uptime_seconds": uptime_seconds,
            "requests_total": request_counts["total"],
            "battles_served": battles_served,
            "votes_received": votes_received,
            "db_size_bytes": db_size_bytes,
        },
        "config": {
            "public_url": config.public_url,
            "debug_mode": config.debug,
        }
    })


@app.post("/v1/battles:next", response_model=BattleResponse)
@app.post("/v1/battles%3Anext", response_model=BattleResponse)  # Handle URL-encoded version for PowerShell
@limiter.limit("10/minute")  # S1-B5: Rate limiting
async def fetch_next_battle(battle_request: BattleRequest, request: Request):
    """
    Fetch the next battle: two levels from different generators.
    
    Creates a persisted battle row and returns both levels with metadata.
    
    Note: Registered with both `:` and `%3A` to handle PowerShell Invoke-RestMethod URL encoding.
    """
    request_counts["total"] += 1
    request_counts["battles"] += 1
    
    conn = get_connection()
    
    # 1. Validate session_id is present and looks like a UUID
    try:
        uuid.UUID(battle_request.session_id)
    except (ValueError, AttributeError):
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            f"Invalid session_id format: must be a valid UUID",
            retryable=False,
            status_code=400
        )
    
    # 2. Query active generators (is_active = 1)
    cursor = conn.execute(
        "SELECT generator_id FROM generators WHERE is_active = 1"
    )
    active_generators = [row["generator_id"] for row in cursor.fetchall()]
    
    if len(active_generators) < 2:
        raise_api_error(
            ErrorCode.NO_BATTLE_AVAILABLE,
            f"Not enough active generators available (found {len(active_generators)}, need at least 2)",
            retryable=False,
            status_code=503
        )
    
    # 3. Sample two distinct generator_ids uniformly
    selected_generators = random.sample(active_generators, 2)
    left_generator_id = selected_generators[0]
    right_generator_id = selected_generators[1]
    
    # 4. For each generator, select 1 random level
    # 
    # Random level selection strategy (Stage 0):
    # We use SQLite's RANDOM() function with ORDER BY RANDOM() LIMIT 1.
    # This approach:
    # - Works well for Stage 0 scale (typically <100 levels per generator)
    # - Provides uniform distribution over repeated requests
    # - Is simple and requires no additional state or precomputation
    # 
    # Performance note:
    # ORDER BY RANDOM() requires sorting all matching rows, which is O(n log n).
    # For Stage 0 with small datasets (dozens of levels per generator), this is
    # perfectly acceptable. If we scale to thousands of levels per generator,
    # we should consider:
    # - Pre-computing random offsets (SELECT COUNT(*), then random offset)
    # - Using a more sophisticated sampling algorithm
    # - Caching level pools per generator
    # 
    # Query random level for left generator
    cursor = conn.execute(
        """
        SELECT level_id FROM levels 
        WHERE generator_id = ? 
        ORDER BY RANDOM() 
        LIMIT 1
        """,
        (left_generator_id,)
    )
    left_level_row = cursor.fetchone()
    
    # Query random level for right generator
    cursor = conn.execute(
        """
        SELECT level_id FROM levels 
        WHERE generator_id = ? 
        ORDER BY RANDOM() 
        LIMIT 1
        """,
        (right_generator_id,)
    )
    right_level_row = cursor.fetchone()
    
    # Check if we have levels for both generators
    if not left_level_row or not right_level_row:
        # Count how many generators have levels
        cursor = conn.execute(
            """
            SELECT COUNT(DISTINCT generator_id) as count
            FROM levels
            WHERE generator_id IN (?, ?)
            """,
            (left_generator_id, right_generator_id)
        )
        eligible_count = cursor.fetchone()["count"]
        
        raise_api_error(
            ErrorCode.NO_BATTLE_AVAILABLE,
            f"Not enough generators with levels available (found {eligible_count} eligible generators, need 2)",
            retryable=False,
            status_code=503
        )
    
    left_level_id = left_level_row["level_id"]
    right_level_id = right_level_row["level_id"]
    
    # Ensure left and right levels are different (should be guaranteed by different generators, but double-check)
    if left_level_id == right_level_id:
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "Selected duplicate level for battle (this should not happen)",
            retryable=True,
            status_code=500
        )
    
    # 5. Create battle_id (UUID string prefixed with 'btl_')
    battle_id = f"btl_{uuid.uuid4()}"
    
    # 6. Insert into battles table (within a transaction)
    now_utc = datetime.now(timezone.utc).isoformat()
    
    try:
        with transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO battles (
                    battle_id, session_id, issued_at_utc, expires_at_utc, status,
                    left_level_id, right_level_id,
                    left_generator_id, right_generator_id,
                    matchmaking_policy, created_at_utc, updated_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    battle_id,
                    battle_request.session_id,
                    now_utc,
                    None,  # expires_at_utc = NULL (no expiry for Stage 0)
                    "ISSUED",
                    left_level_id,
                    right_level_id,
                    left_generator_id,
                    right_generator_id,
                    "uniform_v0",
                    now_utc,
                    now_utc,
                )
            )
    except sqlite3.IntegrityError as e:
        logger.error(f"Failed to create battle: {e}")
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "Failed to create battle due to database constraint violation",
            retryable=True,
            status_code=500
        )
    
    # 7. Fetch full level and generator data for response
    # Left side
    cursor = conn.execute(
        """
        SELECT 
            l.level_id, l.width, l.height, l.tilemap_text, l.content_hash, l.seed, l.controls_json,
            g.generator_id, g.name, g.version, g.documentation_url
        FROM levels l
        JOIN generators g ON l.generator_id = g.generator_id
        WHERE l.level_id = ?
        """,
        (left_level_id,)
    )
    left_data = cursor.fetchone()
    
    # Right side
    cursor = conn.execute(
        """
        SELECT 
            l.level_id, l.width, l.height, l.tilemap_text, l.content_hash, l.seed, l.controls_json,
            g.generator_id, g.name, g.version, g.documentation_url
        FROM levels l
        JOIN generators g ON l.generator_id = g.generator_id
        WHERE l.level_id = ?
        """,
        (right_level_id,)
    )
    right_data = cursor.fetchone()
    
    if not left_data or not right_data:
        logger.error(f"Failed to fetch level data: left={left_level_id}, right={right_level_id}")
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "Failed to fetch level data after battle creation",
            retryable=True,
            status_code=500
        )
    
    # Parse controls_json
    left_controls = json.loads(left_data["controls_json"]) if left_data["controls_json"] else {}
    right_controls = json.loads(right_data["controls_json"]) if right_data["controls_json"] else {}
    
    # Build response
    # Presentation config (Stage 0): hardcoded values for stable client UX
    # - play_order: LEFT_THEN_RIGHT (client presents left level first, then right)
    # - reveal_generator_names_after_vote: true (generator identities revealed after voting)
    # - suggested_time_limit_seconds: 300 (5 minutes total for both levels)
    battle_response = BattleResponse(
        protocol_version="arena/v0",
        battle=Battle(
            battle_id=battle_id,
            issued_at_utc=now_utc,
            expires_at_utc=None,
            presentation=BattlePresentation(
                play_order=PlayOrder.LEFT_THEN_RIGHT,
                reveal_generator_names_after_vote=True,
                suggested_time_limit_seconds=300
            ),
            left=BattleSide(
                level_id=left_data["level_id"],
                generator=GeneratorInfo(
                    generator_id=left_data["generator_id"],
                    name=left_data["name"],
                    version=left_data["version"],
                    documentation_url=left_data["documentation_url"]
                ),
                format=LevelFormat(
                    type=LevelFormatType.ASCII_TILEMAP,
                    width=left_data["width"],
                    height=left_data["height"],
                    newline="\n"
                ),
                level_payload=LevelPayload(
                    encoding=Encoding.UTF8,
                    tilemap=left_data["tilemap_text"]
                ),
                content_hash=left_data["content_hash"],
                metadata=LevelMetadata(
                    seed=left_data["seed"],
                    controls=left_controls
                )
            ),
            right=BattleSide(
                level_id=right_data["level_id"],
                generator=GeneratorInfo(
                    generator_id=right_data["generator_id"],
                    name=right_data["name"],
                    version=right_data["version"],
                    documentation_url=right_data["documentation_url"]
                ),
                format=LevelFormat(
                    type=LevelFormatType.ASCII_TILEMAP,
                    width=right_data["width"],
                    height=right_data["height"],
                    newline="\n"
                ),
                level_payload=LevelPayload(
                    encoding=Encoding.UTF8,
                    tilemap=right_data["tilemap_text"]
                ),
                content_hash=right_data["content_hash"],
                metadata=LevelMetadata(
                    seed=right_data["seed"],
                    controls=right_controls
                )
            )
        )
    )
    
    logger.info(
        f"Battle issued: battle_id={battle_id} "
        f"left_gen={left_generator_id} right_gen={right_generator_id} "
        f"left_level={left_level_id} right_level={right_level_id}"
    )
    
    return battle_response


def compute_payload_hash(battle_id: str, session_id: str, result: str, left_tags: list, right_tags: list, telemetry: dict) -> str:
    """
    Compute canonical payload hash for idempotency checking.
    
    Creates a deterministic hash from battle_id, session_id, result, sorted tags, and telemetry.
    This ensures that identical vote payloads produce the same hash.
    
    Args:
        battle_id: Battle identifier
        session_id: Session identifier
        result: Vote result (LEFT, RIGHT, TIE, SKIP)
        left_tags: List of tags for left level (will be sorted)
        right_tags: List of tags for right level (will be sorted)
        telemetry: Telemetry dict (will be serialized as canonical JSON)
    
    Returns:
        SHA256 hash as hex string
    """
    # Sort tags for canonical representation
    sorted_left_tags = sorted(left_tags) if left_tags else []
    sorted_right_tags = sorted(right_tags) if right_tags else []
    
    # Serialize telemetry as canonical JSON (sorted keys, no whitespace)
    telemetry_json = json.dumps(telemetry, sort_keys=True, separators=(',', ':')) if telemetry else '{}'
    
    # Create canonical payload string
    payload_str = json.dumps({
        "battle_id": battle_id,
        "session_id": session_id,
        "result": result,
        "left_tags": sorted_left_tags,
        "right_tags": sorted_right_tags,
        "telemetry": json.loads(telemetry_json)  # Parse and re-serialize for consistency
    }, sort_keys=True, separators=(',', ':'))
    
    # Compute SHA256 hash
    hash_obj = hashlib.sha256(payload_str.encode('utf-8'))
    return hash_obj.hexdigest()


def ensure_ratings_exist(
    cursor: sqlite3.Cursor,
    generator_id: str,
    initial_rating: float,
    now_utc: str
) -> None:
    """
    Ensure a ratings row exists for a generator (Task D2).
    
    If the ratings row doesn't exist, creates it with initial values.
    This is defensive programming to handle edge cases where a generator
    might be added without a ratings row.
    
    Args:
        cursor: Database cursor (within transaction)
        generator_id: Generator ID to check/create
        initial_rating: Initial rating value (default 1000.0)
        now_utc: Current UTC timestamp
    """
    cursor.execute(
        "SELECT generator_id FROM ratings WHERE generator_id = ?",
        (generator_id,)
    )
    if cursor.fetchone() is None:
        logger.warning(f"Ratings row missing for generator {generator_id}, creating with initial rating {initial_rating}")
        cursor.execute(
            """
            INSERT INTO ratings (
                generator_id, rating_value, games_played,
                wins, losses, ties, skips, updated_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (generator_id, initial_rating, 0, 0, 0, 0, 0, now_utc)
        )


def update_ratings(
    cursor: sqlite3.Cursor,
    left_generator_id: str,
    right_generator_id: str,
    result: str,
    k_factor: float,
    now_utc: str,
    initial_rating: float = 1000.0
) -> tuple[float, float]:
    """
    Update generator ratings based on vote result using Elo rating system (Task D1).
    
    Implements standard Elo rating calculation:
    - Expected score: E_left = 1 / (1 + 10^((R_right - R_left)/400))
    - Delta: delta_left = K * (S_left - E_left), delta_right = -delta_left
    - Updates rating_value and counters (wins, losses, ties, games_played)
    
    SKIP semantics (Task C3):
    - Do NOT change rating_value for either generator
    - Increment skips counter for BOTH generators
    - Do NOT increment games_played (games_played is for rating-relevant matches only)
    - Return (0.0, 0.0) for deltas (no rating change)
    
    Args:
        cursor: Database cursor (within transaction)
        left_generator_id: Left generator ID
        right_generator_id: Right generator ID
        result: Vote result (LEFT, RIGHT, TIE, SKIP)
        k_factor: ELO K-factor (default 24)
        now_utc: Current UTC timestamp
        initial_rating: Initial rating if row doesn't exist (default 1000.0)
    
    Returns:
        Tuple of (delta_left, delta_right) rating changes
    """
    # Task D2: Ensure ratings rows exist before updating
    ensure_ratings_exist(cursor, left_generator_id, initial_rating, now_utc)
    ensure_ratings_exist(cursor, right_generator_id, initial_rating, now_utc)
    
    if result == VoteResult.SKIP.value or result == "SKIP":
        # SKIP semantics: increment skip counters for both generators, no rating change
        # Note: games_played is NOT incremented for SKIP (it's for rating-relevant matches only)
        cursor.execute(
            """
            UPDATE ratings 
            SET skips = skips + 1, updated_at_utc = ?
            WHERE generator_id = ?
            """,
            (now_utc, left_generator_id)
        )
        cursor.execute(
            """
            UPDATE ratings 
            SET skips = skips + 1, updated_at_utc = ?
            WHERE generator_id = ?
            """,
            (now_utc, right_generator_id)
        )
        logger.info(
            f"SKIP vote processed: left_gen={left_generator_id} right_gen={right_generator_id} "
            f"(skip counters incremented, no rating change)"
        )
        return (0.0, 0.0)
    
    # Task D1: Fetch current ratings
    cursor.execute(
        "SELECT rating_value FROM ratings WHERE generator_id = ?",
        (left_generator_id,)
    )
    left_row = cursor.fetchone()
    R_left = left_row["rating_value"] if left_row else initial_rating
    
    cursor.execute(
        "SELECT rating_value FROM ratings WHERE generator_id = ?",
        (right_generator_id,)
    )
    right_row = cursor.fetchone()
    R_right = right_row["rating_value"] if right_row else initial_rating
    
    # Calculate expected scores (Elo formula)
    # E_left = 1 / (1 + 10^((R_right - R_left)/400))
    rating_diff = (R_right - R_left) / 400.0
    E_left = 1.0 / (1.0 + math.pow(10.0, rating_diff))
    E_right = 1.0 - E_left
    
    # Determine outcome scores based on result
    if result == VoteResult.LEFT.value or result == "LEFT":
        S_left = 1.0
        S_right = 0.0
    elif result == VoteResult.RIGHT.value or result == "RIGHT":
        S_left = 0.0
        S_right = 1.0
    elif result == VoteResult.TIE.value or result == "TIE":
        S_left = 0.5
        S_right = 0.5
    else:
        # Should not happen, but handle gracefully
        logger.error(f"Unexpected vote result: {result}")
        return (0.0, 0.0)
    
    # Calculate rating deltas
    # delta_left = K * (S_left - E_left)
    # delta_right = -delta_left (zero-sum: ratings are conserved)
    delta_left = k_factor * (S_left - E_left)
    delta_right = -delta_left
    
    # Update left generator rating and counters
    new_rating_left = R_left + delta_left
    if result == VoteResult.LEFT.value or result == "LEFT":
        cursor.execute(
            """
            UPDATE ratings 
            SET rating_value = ?, games_played = games_played + 1,
                wins = wins + 1, updated_at_utc = ?
            WHERE generator_id = ?
            """,
            (new_rating_left, now_utc, left_generator_id)
        )
    elif result == VoteResult.RIGHT.value or result == "RIGHT":
        cursor.execute(
            """
            UPDATE ratings 
            SET rating_value = ?, games_played = games_played + 1,
                losses = losses + 1, updated_at_utc = ?
            WHERE generator_id = ?
            """,
            (new_rating_left, now_utc, left_generator_id)
        )
    elif result == VoteResult.TIE.value or result == "TIE":
        cursor.execute(
            """
            UPDATE ratings 
            SET rating_value = ?, games_played = games_played + 1,
                ties = ties + 1, updated_at_utc = ?
            WHERE generator_id = ?
            """,
            (new_rating_left, now_utc, left_generator_id)
        )
    
    # Update right generator rating and counters
    new_rating_right = R_right + delta_right
    if result == VoteResult.LEFT.value or result == "LEFT":
        cursor.execute(
            """
            UPDATE ratings 
            SET rating_value = ?, games_played = games_played + 1,
                losses = losses + 1, updated_at_utc = ?
            WHERE generator_id = ?
            """,
            (new_rating_right, now_utc, right_generator_id)
        )
    elif result == VoteResult.RIGHT.value or result == "RIGHT":
        cursor.execute(
            """
            UPDATE ratings 
            SET rating_value = ?, games_played = games_played + 1,
                wins = wins + 1, updated_at_utc = ?
            WHERE generator_id = ?
            """,
            (new_rating_right, now_utc, right_generator_id)
        )
    elif result == VoteResult.TIE.value or result == "TIE":
        cursor.execute(
            """
            UPDATE ratings 
            SET rating_value = ?, games_played = games_played + 1,
                ties = ties + 1, updated_at_utc = ?
            WHERE generator_id = ?
            """,
            (new_rating_right, now_utc, right_generator_id)
        )
    
    logger.info(
        f"Elo rating update: left_gen={left_generator_id} right_gen={right_generator_id} "
        f"result={result} R_left={R_left:.1f}->{new_rating_left:.1f} "
        f"R_right={R_right:.1f}->{new_rating_right:.1f} "
        f"delta_left={delta_left:.2f} delta_right={delta_right:.2f}"
    )
    
    return (delta_left, delta_right)


def insert_rating_event(
    cursor: sqlite3.Cursor,
    vote_id: str,
    battle_id: str,
    left_generator_id: str,
    right_generator_id: str,
    result: str,
    delta_left: float,
    delta_right: float,
    now_utc: str
) -> None:
    """
    Insert rating event for auditability and debugging.
    
    Creates an audit log entry for every vote that affects ratings (or is skipped).
    This enables reconstructing rating history and debugging rating calculations.
    
    Args:
        cursor: Database cursor (within transaction)
        vote_id: Vote identifier (must be unique - one event per vote)
        battle_id: Battle identifier
        left_generator_id: Left generator ID
        right_generator_id: Right generator ID
        result: Vote result (LEFT, RIGHT, TIE, SKIP)
        delta_left: Rating change for left generator (0.0 for SKIP)
        delta_right: Rating change for right generator (0.0 for SKIP)
        now_utc: Current UTC timestamp
    
    Note:
        This function is called within the vote submission transaction, ensuring
        that rating events are created atomically with votes. For idempotent
        vote replays, this function is not called (the event already exists).
    """
    event_id = f"evt_{uuid.uuid4()}"
    
    cursor.execute(
        """
        INSERT INTO rating_events (
            event_id, vote_id, battle_id,
            left_generator_id, right_generator_id,
            result, delta_left, delta_right,
            created_at_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            vote_id,
            battle_id,
            left_generator_id,
            right_generator_id,
            result,
            delta_left,
            delta_right,
            now_utc,
        )
    )


@app.post("/v1/votes", response_model=VoteResponse)
@limiter.limit("20/minute")  # S1-B5: Rate limiting (higher limit for votes)
async def submit_vote(vote_request: VoteRequest, request: Request):
    """
    Submit a vote for a battle.
    
    Accepts vote outcome, ensures idempotency, and atomically updates database and ratings.
    """
    request_counts["total"] += 1
    request_counts["votes"] += 1
    
    conn = get_connection()
    now_utc = datetime.now(timezone.utc).isoformat()
    
    # Request validation
    # session_id and battle_id are required by Pydantic model
    # result is validated by VoteResult enum
    
    # Validate tags vocabulary for left level
    if vote_request.left_tags:
        invalid_tags = [tag for tag in vote_request.left_tags if tag not in ALLOWED_TAGS]
        if invalid_tags:
            raise_api_error(
                ErrorCode.INVALID_TAG,
                f"Invalid left tags: {', '.join(invalid_tags)}. Allowed tags: {', '.join(sorted(ALLOWED_TAGS))}",
                retryable=False,
                status_code=400,
                details={"invalid_tags": invalid_tags, "allowed_tags": sorted(ALLOWED_TAGS)}
            )
    
    # Validate tags vocabulary for right level
    if vote_request.right_tags:
        invalid_tags = [tag for tag in vote_request.right_tags if tag not in ALLOWED_TAGS]
        if invalid_tags:
            raise_api_error(
                ErrorCode.INVALID_TAG,
                f"Invalid right tags: {', '.join(invalid_tags)}. Allowed tags: {', '.join(sorted(ALLOWED_TAGS))}",
                retryable=False,
                status_code=400,
                details={"invalid_tags": invalid_tags, "allowed_tags": sorted(ALLOWED_TAGS)}
            )
    
    # Prepare telemetry JSON
    telemetry_dict = vote_request.telemetry.model_dump() if vote_request.telemetry else {}
    
    # Compute canonical payload hash for idempotency
    left_tags_list = vote_request.left_tags if vote_request.left_tags else []
    right_tags_list = vote_request.right_tags if vote_request.right_tags else []
    payload_hash = compute_payload_hash(
        vote_request.battle_id,
        vote_request.session_id,
        vote_request.result.value,
        left_tags_list,
        right_tags_list,
        telemetry_dict
    )
    
    # Transaction: all operations must be atomic
    try:
        with transaction() as cursor:
            # 1. Load battle by battle_id
            cursor.execute(
                "SELECT * FROM battles WHERE battle_id = ?",
                (vote_request.battle_id,)
            )
            battle_row = cursor.fetchone()
            
            if not battle_row:
                raise_api_error(
                    ErrorCode.BATTLE_NOT_FOUND,
                    f"Battle with ID '{vote_request.battle_id}' not found",
                    retryable=False,
                    status_code=404
                )
            
            battle_status = battle_row["status"]
            battle_session_id = battle_row["session_id"]
            left_generator_id = battle_row["left_generator_id"]
            right_generator_id = battle_row["right_generator_id"]
            
            # 2. Check battle status
            if battle_status != "ISSUED":
                if battle_status == "COMPLETED":
                    # Check if vote exists (idempotency path)
                    cursor.execute(
                        "SELECT vote_id, payload_hash FROM votes WHERE battle_id = ?",
                        (vote_request.battle_id,)
                    )
                    existing_vote = cursor.fetchone()
                    
                    if existing_vote:
                        stored_hash = existing_vote["payload_hash"]
                        if stored_hash == payload_hash:
                            # Idempotent replay: return existing vote
                            vote_id = existing_vote["vote_id"]
                            logger.info(f"Idempotent vote replay: battle_id={vote_request.battle_id} vote_id={vote_id}")
                            
                            # Fetch leaderboard for response
                            cursor.execute(
                                """
                                SELECT 
                                    g.generator_id, g.name,
                                    r.rating_value, r.games_played
                                FROM generators g
                                JOIN ratings r ON g.generator_id = r.generator_id
                                WHERE g.is_active = 1
                                ORDER BY r.rating_value DESC, g.generator_id ASC
                                """
                            )
                            generators_data = cursor.fetchall()
                            
                            leaderboard_generators = [
                                LeaderboardGeneratorPreview(
                                    generator_id=row["generator_id"],
                                    name=row["name"],
                                    rating=row["rating_value"],
                                    games_played=row["games_played"]
                                )
                                for row in generators_data
                            ]
                            
                            cursor.execute("SELECT MAX(updated_at_utc) as last_update FROM ratings")
                            last_update_row = cursor.fetchone()
                            last_update = last_update_row["last_update"] if last_update_row["last_update"] else now_utc
                            
                            return VoteResponse(
                                protocol_version="arena/v0",
                                accepted=True,
                                vote_id=vote_id,
                                leaderboard_preview=LeaderboardPreview(
                                    updated_at_utc=last_update,
                                    generators=leaderboard_generators
                                )
                            )
                        else:
                            # Different payload for same battle
                            raise_api_error(
                                ErrorCode.DUPLICATE_VOTE_CONFLICT,
                                f"Vote already exists for battle '{vote_request.battle_id}' with different payload",
                                retryable=False,
                                status_code=409,
                                details={"battle_id": vote_request.battle_id, "existing_vote_id": existing_vote["vote_id"]}
                            )
                    else:
                        # COMPLETED but no vote? This shouldn't happen, but handle gracefully
                        raise_api_error(
                            ErrorCode.BATTLE_ALREADY_VOTED,
                            f"Battle '{vote_request.battle_id}' is COMPLETED but no vote found (inconsistent state)",
                            retryable=False,
                            status_code=409
                        )
                else:
                    # EXPIRED or other status
                    raise_api_error(
                        ErrorCode.BATTLE_ALREADY_VOTED,
                        f"Battle '{vote_request.battle_id}' has status '{battle_status}' and cannot be voted on",
                        retryable=False,
                        status_code=409
                    )
            
            # 3. Check session_id matches
            if battle_session_id != vote_request.session_id:
                raise_api_error(
                    ErrorCode.INVALID_PAYLOAD,
                    f"Session ID mismatch: battle session_id='{battle_session_id}' but request session_id='{vote_request.session_id}'",
                    retryable=False,
                    status_code=400
                )
            
            # 4. Payload hash already computed above
            
            # 5. Check if vote already exists (shouldn't for ISSUED battle, but check anyway)
            cursor.execute(
                "SELECT vote_id, payload_hash FROM votes WHERE battle_id = ?",
                (vote_request.battle_id,)
            )
            existing_vote = cursor.fetchone()
            
            if existing_vote:
                stored_hash = existing_vote["payload_hash"]
                if stored_hash == payload_hash:
                    # Idempotent replay
                    vote_id = existing_vote["vote_id"]
                    logger.info(f"Idempotent vote replay: battle_id={vote_request.battle_id} vote_id={vote_id}")
                else:
                    raise_api_error(
                        ErrorCode.DUPLICATE_VOTE_CONFLICT,
                        f"Vote already exists for battle '{vote_request.battle_id}' with different payload",
                        retryable=False,
                        status_code=409
                    )
            else:
                # 6. Insert new vote
                vote_id = f"v_{uuid.uuid4()}"
                left_tags_json = json.dumps(sorted(left_tags_list)) if left_tags_list else "[]"
                right_tags_json = json.dumps(sorted(right_tags_list)) if right_tags_list else "[]"
                telemetry_json = json.dumps(telemetry_dict, sort_keys=True) if telemetry_dict else "{}"
                
                cursor.execute(
                    """
                    INSERT INTO votes (
                        vote_id, battle_id, session_id,
                        created_at_utc, result, left_tags_json, right_tags_json, telemetry_json, payload_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        vote_id,
                        vote_request.battle_id,
                        vote_request.session_id,
                        now_utc,
                        vote_request.result.value,
                        left_tags_json,
                        right_tags_json,
                        telemetry_json,
                        payload_hash,
                    )
                )
                
                # 7. Update battle status to COMPLETED
                cursor.execute(
                    """
                    UPDATE battles 
                    SET status = 'COMPLETED', updated_at_utc = ?
                    WHERE battle_id = ?
                    """,
                    (now_utc, vote_request.battle_id)
                )
                
                # 8. Update ratings using Elo rating system
                delta_left, delta_right = update_ratings(
                    cursor,
                    left_generator_id,
                    right_generator_id,
                    vote_request.result.value,
                    config.k_factor,
                    now_utc,
                    config.initial_rating
                )
                
                # 9. Insert rating event for auditability
                insert_rating_event(
                    cursor,
                    vote_id,
                    vote_request.battle_id,
                    left_generator_id,
                    right_generator_id,
                    vote_request.result.value,
                    delta_left,
                    delta_right,
                    now_utc
                )
            
            # Fetch leaderboard for response
            cursor.execute(
                """
                SELECT 
                    g.generator_id, g.name,
                    r.rating_value, r.games_played
                FROM generators g
                JOIN ratings r ON g.generator_id = r.generator_id
                WHERE g.is_active = 1
                ORDER BY r.rating_value DESC, g.generator_id ASC
                """
            )
            generators_data = cursor.fetchall()
            
            leaderboard_generators = [
                LeaderboardGeneratorPreview(
                    generator_id=row["generator_id"],
                    name=row["name"],
                    rating=row["rating_value"],
                    games_played=row["games_played"]
                )
                for row in generators_data
            ]
            
            cursor.execute("SELECT MAX(updated_at_utc) as last_update FROM ratings")
            last_update_row = cursor.fetchone()
            last_update = last_update_row["last_update"] if last_update_row["last_update"] else now_utc
            
            logger.info(
                f"Vote accepted: vote_id={vote_id} battle_id={vote_request.battle_id} "
                f"result={vote_request.result.value} left_tags={left_tags_list} right_tags={right_tags_list}"
            )
            
            return VoteResponse(
                protocol_version="arena/v0",
                accepted=True,
                vote_id=vote_id,
                leaderboard_preview=LeaderboardPreview(
                    updated_at_utc=last_update,
                    generators=leaderboard_generators
                )
            )
            
    except APIError:
        # Re-raise API errors
        raise
    except sqlite3.IntegrityError as e:
        logger.error(f"Database integrity error during vote submission: {e}")
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "Failed to submit vote due to database constraint violation",
            retryable=True,
            status_code=500
        )
    except Exception as e:
        logger.exception(f"Unexpected error during vote submission: {e}")
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "An internal error occurred while processing vote",
            retryable=True,
            status_code=500
        )


@app.get("/test/error/{error_code}")
async def test_error(error_code: str):
    """
    Test endpoint to demonstrate error handling.
    
    This endpoint allows testing different error codes and responses.
    Not part of the production API - for development/testing only.
    """
    from errors import raise_api_error, ErrorCode
    
    # Map error codes to test scenarios
    error_tests = {
        "NO_BATTLE_AVAILABLE": {
            "code": ErrorCode.NO_BATTLE_AVAILABLE,
            "message": "No battle available - not enough generators or levels loaded",
            "retryable": True,
            "status_code": 503
        },
        "INVALID_PAYLOAD": {
            "code": ErrorCode.INVALID_PAYLOAD,
            "message": "Invalid request payload",
            "retryable": False,
            "status_code": 400
        },
        "INVALID_TAG": {
            "code": ErrorCode.INVALID_TAG,
            "message": "Invalid tag 'invalid_tag' - not in allowed vocabulary",
            "retryable": False,
            "status_code": 400,
            "details": {"invalid_tag": "invalid_tag", "allowed_tags": ["fun", "boring", "good_flow"]}
        },
        "BATTLE_NOT_FOUND": {
            "code": ErrorCode.BATTLE_NOT_FOUND,
            "message": "Battle with ID 'btl_123' not found",
            "retryable": False,
            "status_code": 404
        },
        "BATTLE_ALREADY_VOTED": {
            "code": ErrorCode.BATTLE_ALREADY_VOTED,
            "message": "Battle 'btl_123' has already been voted on",
            "retryable": False,
            "status_code": 409
        },
        "DUPLICATE_VOTE_CONFLICT": {
            "code": ErrorCode.DUPLICATE_VOTE_CONFLICT,
            "message": "Duplicate vote with conflicting payload",
            "retryable": False,
            "status_code": 409
        },
        "INTERNAL_ERROR": {
            "code": ErrorCode.INTERNAL_ERROR,
            "message": "An internal server error occurred",
            "retryable": True,
            "status_code": 500
        },
        "UNSUPPORTED_CLIENT_VERSION": {
            "code": ErrorCode.UNSUPPORTED_CLIENT_VERSION,
            "message": "Client version '0.0.0' is not supported",
            "retryable": False,
            "status_code": 400
        }
    }
    
    if error_code not in error_tests:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            f"Unknown test error code: {error_code}",
            retryable=False,
            status_code=400,
            details={"available_codes": list(error_tests.keys())}
        )
    
    test_config = error_tests[error_code]
    raise_api_error(
        code=test_config["code"],
        message=test_config["message"],
        retryable=test_config["retryable"],
        status_code=test_config["status_code"],
        details=test_config.get("details")
    )


@app.get("/v1/leaderboard")
async def get_leaderboard():
    """
    Get the current generator leaderboard.
    
    Returns generators sorted by rating (descending), with stats.
    """
    from datetime import datetime, timezone
    
    conn = get_connection()
    
    # Join generators and ratings, sort by rating DESC, then generator_id
    cursor = conn.execute(
        """
        SELECT 
            g.generator_id,
            g.name,
            g.version,
            g.documentation_url,
            r.rating_value,
            r.games_played,
            r.wins,
            r.losses,
            r.ties,
            r.skips,
            r.updated_at_utc
        FROM generators g
        JOIN ratings r ON g.generator_id = r.generator_id
        WHERE g.is_active = 1
        ORDER BY r.rating_value DESC, g.generator_id ASC
        """
    )
    
    generators = []
    for rank, row in enumerate(cursor.fetchall(), start=1):
        generators.append({
            "rank": rank,
            "generator_id": row["generator_id"],
            "name": row["name"],
            "version": row["version"],
            "documentation_url": row["documentation_url"],
            "rating": row["rating_value"],
            "games_played": row["games_played"],
            "wins": row["wins"],
            "losses": row["losses"],
            "ties": row["ties"],
            "skips": row["skips"],
        })
    
    # Get the most recent update time
    if generators:
        cursor = conn.execute(
            "SELECT MAX(updated_at_utc) as last_update FROM ratings"
        )
        last_update = cursor.fetchone()["last_update"]
    else:
        last_update = datetime.now(timezone.utc).isoformat()
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "updated_at_utc": last_update,
        "rating_system": {
            "name": "ELO",
            "initial_rating": config.initial_rating,
            "k_factor": config.k_factor,
        },
        "generators": generators,
    })


@app.get("/", response_class=HTMLResponse)
async def leaderboard_page():
    """
    Render a simple HTML leaderboard page.
    
    Provides a human-readable view of generator rankings.
    """
    from datetime import datetime, timezone
    
    conn = get_connection()
    
    # Get leaderboard data
    cursor = conn.execute(
        """
        SELECT 
            g.generator_id,
            g.name,
            g.version,
            g.documentation_url,
            r.rating_value,
            r.games_played,
            r.wins,
            r.losses,
            r.ties,
            r.skips
        FROM generators g
        JOIN ratings r ON g.generator_id = r.generator_id
        WHERE g.is_active = 1
        ORDER BY r.rating_value DESC, g.generator_id ASC
        """
    )
    rows = cursor.fetchall()
    
    # Build table rows
    table_rows = ""
    for rank, row in enumerate(rows, start=1):
        doc_link = f'<a href="{row["documentation_url"]}">{row["name"]}</a>' if row["documentation_url"] else row["name"]
        table_rows += f"""
        <tr>
            <td>{rank}</td>
            <td>{doc_link}</td>
            <td><code>{row["generator_id"]}</code></td>
            <td>{row["version"]}</td>
            <td><strong>{row["rating_value"]:.1f}</strong></td>
            <td>{row["games_played"]}</td>
            <td>{row["wins"]}</td>
            <td>{row["losses"]}</td>
            <td>{row["ties"]}</td>
            <td>{row["skips"]}</td>
        </tr>
        """
    
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PCG Arena - Leaderboard</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                max-width: 1000px;
                margin: 0 auto;
                padding: 2rem;
                background: #0d1117;
                color: #c9d1d9;
            }}
            h1 {{
                color: #58a6ff;
                border-bottom: 1px solid #30363d;
                padding-bottom: 0.5rem;
            }}
            .meta {{
                color: #8b949e;
                font-size: 0.9rem;
                margin-bottom: 1.5rem;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: #161b22;
                border-radius: 6px;
                overflow: hidden;
            }}
            th, td {{
                padding: 0.75rem 1rem;
                text-align: left;
                border-bottom: 1px solid #30363d;
            }}
            th {{
                background: #21262d;
                color: #58a6ff;
                font-weight: 600;
            }}
            tr:hover {{
                background: #1f2428;
            }}
            code {{
                background: #30363d;
                padding: 0.2rem 0.4rem;
                border-radius: 3px;
                font-size: 0.85rem;
            }}
            a {{
                color: #58a6ff;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .rating {{
                font-weight: bold;
                color: #3fb950;
            }}
            .footer {{
                margin-top: 2rem;
                color: #8b949e;
                font-size: 0.8rem;
            }}
        </style>
    </head>
    <body>
        <h1>🎮 PCG Arena Leaderboard</h1>
        <div class="meta">
            Protocol: arena/v0 | Rating: ELO (K={config.k_factor}) | Updated: {now}
        </div>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Generator</th>
                    <th>ID</th>
                    <th>Version</th>
                    <th>Rating</th>
                    <th>Games</th>
                    <th>W</th>
                    <th>L</th>
                    <th>T</th>
                    <th>Skip</th>
                </tr>
            </thead>
            <tbody>
                {table_rows if table_rows else '<tr><td colspan="10" style="text-align:center;color:#8b949e;">No generators yet</td></tr>'}
            </tbody>
        </table>
        <div class="footer">
            <a href="/v1/leaderboard">JSON API</a> | 
            <a href="/health">Health Check</a> |
            <a href="/docs">API Docs</a>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)


# Task E3: Debug endpoints (only available when ARENA_DEBUG=true)
# These endpoints help inspect database state without opening SQLite directly.
# For Stage 0 local-only, no auth needed. For hosted stages, guard behind ARENA_DEBUG.

@app.get("/debug/db-status")
async def debug_db_status():
    """
    Get database status and metadata (Task E3).
    
    Returns counts of tables, last migration applied, and database file size.
    Only available when ARENA_DEBUG=true.
    """
    if not config.debug:
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "Debug endpoints are disabled. Set ARENA_DEBUG=true to enable.",
            retryable=False,
            status_code=403
        )
    
    import os
    from pathlib import Path
    
    conn = get_connection()
    
    # Get table counts (using whitelist for safety)
    table_names = [
        "generators", "levels", "battles", "votes", 
        "ratings", "rating_events", "schema_migrations"
    ]
    tables = {}
    
    for table_name in table_names:
        # Safe: table_name is from whitelist, not user input
        cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        tables[table_name] = cursor.fetchone()["count"]
    
    # Get last migration
    cursor = conn.execute(
        "SELECT version, applied_at_utc FROM schema_migrations ORDER BY version DESC LIMIT 1"
    )
    last_migration_row = cursor.fetchone()
    last_migration = {
        "version": last_migration_row["version"] if last_migration_row else None,
        "applied_at_utc": last_migration_row["applied_at_utc"] if last_migration_row else None,
    }
    
    # Get database file size
    db_path = Path(config.db_path)
    db_size_bytes = db_path.stat().st_size if db_path.exists() else 0
    db_size_mb = db_size_bytes / (1024 * 1024)
    
    # Get foreign keys status
    cursor = conn.execute("PRAGMA foreign_keys")
    foreign_keys_enabled = bool(cursor.fetchone()[0])
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "database": {
            "path": config.db_path,
            "size_bytes": db_size_bytes,
            "size_mb": round(db_size_mb, 2),
            "foreign_keys_enabled": foreign_keys_enabled,
        },
        "table_counts": tables,
        "last_migration": last_migration,
    })


@app.get("/debug/battles")
async def debug_battles(status: str = None, limit: int = 10):
    """
    Get battle records for debugging (Task E3).
    
    Query parameters:
    - status: Filter by status (ISSUED, COMPLETED, EXPIRED). If not provided, returns all.
    - limit: Maximum number of records to return (default: 10, max: 100)
    
    Only available when ARENA_DEBUG=true.
    """
    if not config.debug:
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "Debug endpoints are disabled. Set ARENA_DEBUG=true to enable.",
            retryable=False,
            status_code=403
        )
    
    if limit > 100:
        limit = 100
    
    conn = get_connection()
    
    if status:
        # Validate status
        if status not in ("ISSUED", "COMPLETED", "EXPIRED"):
            raise_api_error(
                ErrorCode.INVALID_PAYLOAD,
                f"Invalid status: {status}. Must be one of: ISSUED, COMPLETED, EXPIRED",
                retryable=False,
                status_code=400
            )
        cursor = conn.execute(
            """
            SELECT * FROM battles 
            WHERE status = ?
            ORDER BY created_at_utc DESC
            LIMIT ?
            """,
            (status, limit)
        )
    else:
        cursor = conn.execute(
            """
            SELECT * FROM battles 
            ORDER BY created_at_utc DESC
            LIMIT ?
            """,
            (limit,)
        )
    
    battles = []
    for row in cursor.fetchall():
        battles.append({
            "battle_id": row["battle_id"],
            "session_id": row["session_id"],
            "status": row["status"],
            "issued_at_utc": row["issued_at_utc"],
            "expires_at_utc": row["expires_at_utc"],
            "left_level_id": row["left_level_id"],
            "right_level_id": row["right_level_id"],
            "left_generator_id": row["left_generator_id"],
            "right_generator_id": row["right_generator_id"],
            "matchmaking_policy": row["matchmaking_policy"],
            "created_at_utc": row["created_at_utc"],
            "updated_at_utc": row["updated_at_utc"],
        })
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "battles": battles,
        "count": len(battles),
        "status_filter": status,
        "limit": limit,
    })


@app.get("/debug/votes")
async def debug_votes(limit: int = 10):
    """
    Get vote records for debugging (Task E3).
    
    Query parameters:
    - limit: Maximum number of records to return (default: 10, max: 100)
    
    Only available when ARENA_DEBUG=true.
    """
    if not config.debug:
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "Debug endpoints are disabled. Set ARENA_DEBUG=true to enable.",
            retryable=False,
            status_code=403
        )
    
    if limit > 100:
        limit = 100
    
    conn = get_connection()
    
    cursor = conn.execute(
        """
        SELECT * FROM votes 
        ORDER BY created_at_utc DESC
        LIMIT ?
        """,
        (limit,)
    )
    
    votes = []
    for row in cursor.fetchall():
        votes.append({
            "vote_id": row["vote_id"],
            "battle_id": row["battle_id"],
            "session_id": row["session_id"],
            "result": row["result"],
            "left_tags": json.loads(row["left_tags_json"]) if row["left_tags_json"] else [],
            "right_tags": json.loads(row["right_tags_json"]) if row["right_tags_json"] else [],
            "telemetry": json.loads(row["telemetry_json"]) if row["telemetry_json"] else {},
            "payload_hash": row["payload_hash"],
            "created_at_utc": row["created_at_utc"],
        })
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "votes": votes,
        "count": len(votes),
        "limit": limit,
    })


# S1-A: Admin API endpoints (protected by admin key)

def verify_admin_key(authorization: str = Header(None)) -> bool:
    """
    Verify admin API key from Authorization header.
    
    Args:
        authorization: Authorization header value (format: "Bearer <key>")
    
    Returns:
        True if key is valid
    
    Raises:
        APIError if key is missing or invalid
    """
    if not config.admin_key:
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "Admin endpoints are disabled. Set ARENA_ADMIN_KEY to enable.",
            retryable=False,
            status_code=403
        )
    
    if not authorization:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            "Missing Authorization header. Use: Authorization: Bearer <admin_key>",
            retryable=False,
            status_code=401
        )
    
    # Parse "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            "Invalid Authorization header format. Use: Authorization: Bearer <admin_key>",
            retryable=False,
            status_code=401
        )
    
    provided_key = parts[1]
    if provided_key != config.admin_key:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            "Invalid admin key",
            retryable=False,
            status_code=403
        )
    
    return True


@app.post("/admin/generators/{generator_id}/disable")
async def admin_disable_generator(generator_id: str, is_admin: bool = Depends(verify_admin_key)):
    """
    S1-A1: Disable a generator from matchmaking.
    
    Sets is_active = 0 for the specified generator, removing it from battle selection.
    """
    conn = get_connection()
    now_utc = datetime.now(timezone.utc).isoformat()
    
    # Check if generator exists
    cursor = conn.execute(
        "SELECT generator_id, name, is_active FROM generators WHERE generator_id = ?",
        (generator_id,)
    )
    gen = cursor.fetchone()
    
    if not gen:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            f"Generator '{generator_id}' not found",
            retryable=False,
            status_code=404
        )
    
    if gen["is_active"] == 0:
        return JSONResponse({
            "protocol_version": "arena/v0",
            "message": f"Generator '{generator_id}' is already disabled",
            "generator_id": generator_id,
            "name": gen["name"],
            "is_active": False
        })
    
    # Disable generator
    try:
        with transaction() as cursor:
            cursor.execute(
                "UPDATE generators SET is_active = 0, updated_at_utc = ? WHERE generator_id = ?",
                (now_utc, generator_id)
            )
        
        logger.info(f"Admin: Disabled generator '{generator_id}'")
        
        return JSONResponse({
            "protocol_version": "arena/v0",
            "message": f"Generator '{generator_id}' has been disabled",
            "generator_id": generator_id,
            "name": gen["name"],
            "is_active": False
        })
    except Exception as e:
        logger.error(f"Failed to disable generator '{generator_id}': {e}")
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            f"Failed to disable generator: {str(e)}",
            retryable=True,
            status_code=500
        )


@app.post("/admin/generators/{generator_id}/enable")
async def admin_enable_generator(generator_id: str, is_admin: bool = Depends(verify_admin_key)):
    """
    S1-A1: Enable a generator for matchmaking.
    
    Sets is_active = 1 for the specified generator, including it in battle selection.
    """
    conn = get_connection()
    now_utc = datetime.now(timezone.utc).isoformat()
    
    # Check if generator exists
    cursor = conn.execute(
        "SELECT generator_id, name, is_active FROM generators WHERE generator_id = ?",
        (generator_id,)
    )
    gen = cursor.fetchone()
    
    if not gen:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            f"Generator '{generator_id}' not found",
            retryable=False,
            status_code=404
        )
    
    if gen["is_active"] == 1:
        return JSONResponse({
            "protocol_version": "arena/v0",
            "message": f"Generator '{generator_id}' is already enabled",
            "generator_id": generator_id,
            "name": gen["name"],
            "is_active": True
        })
    
    # Enable generator
    try:
        with transaction() as cursor:
            cursor.execute(
                "UPDATE generators SET is_active = 1, updated_at_utc = ? WHERE generator_id = ?",
                (now_utc, generator_id)
            )
        
        logger.info(f"Admin: Enabled generator '{generator_id}'")
        
        return JSONResponse({
            "protocol_version": "arena/v0",
            "message": f"Generator '{generator_id}' has been enabled",
            "generator_id": generator_id,
            "name": gen["name"],
            "is_active": True
        })
    except Exception as e:
        logger.error(f"Failed to enable generator '{generator_id}': {e}")
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            f"Failed to enable generator: {str(e)}",
            retryable=True,
            status_code=500
        )


@app.post("/admin/season/reset")
async def admin_reset_season(is_admin: bool = Depends(verify_admin_key)):
    """
    S1-A2: Reset the season (ratings and battle history).
    
    WARNING: This operation:
    - Resets all generator ratings to initial rating
    - Clears wins/losses/ties/skips counters
    - DOES NOT delete battles or votes (for audit trail)
    
    Returns count of generators reset.
    """
    conn = get_connection()
    now_utc = datetime.now(timezone.utc).isoformat()
    
    try:
        with transaction() as cursor:
            # Reset all ratings
            cursor.execute(
                """
                UPDATE ratings 
                SET rating_value = ?,
                    games_played = 0,
                    wins = 0,
                    losses = 0,
                    ties = 0,
                    skips = 0,
                    updated_at_utc = ?
                """,
                (config.initial_rating, now_utc)
            )
            
            count = cursor.rowcount
        
        logger.warning(f"Admin: Season reset - {count} generators reset to {config.initial_rating}")
        
        return JSONResponse({
            "protocol_version": "arena/v0",
            "message": f"Season reset complete. {count} generators reset to rating {config.initial_rating}",
            "generators_reset": count,
            "initial_rating": config.initial_rating,
            "note": "Battle and vote history preserved for audit purposes"
        })
    except Exception as e:
        logger.error(f"Failed to reset season: {e}")
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            f"Failed to reset season: {str(e)}",
            retryable=True,
            status_code=500
        )


@app.post("/admin/sessions/{session_id}/flag")
async def admin_flag_session(session_id: str, reason: str = None, is_admin: bool = Depends(verify_admin_key)):
    """
    S1-A3: Flag a session for suspicious activity.
    
    Query parameters:
    - reason: Optional reason for flagging
    
    Returns count of battles and votes associated with session.
    Note: Stage 0 does not have a session flags table, so this just returns info for manual review.
    """
    conn = get_connection()
    
    # Check if session exists
    cursor = conn.execute(
        "SELECT COUNT(*) as count FROM battles WHERE session_id = ?",
        (session_id,)
    )
    battle_count = cursor.fetchone()["count"]
    
    cursor = conn.execute(
        "SELECT COUNT(*) as count FROM votes WHERE session_id = ?",
        (session_id,)
    )
    vote_count = cursor.fetchone()["count"]
    
    if battle_count == 0 and vote_count == 0:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            f"Session '{session_id}' not found",
            retryable=False,
            status_code=404
        )
    
    logger.warning(f"Admin: Flagged session '{session_id}' - Reason: {reason or 'Not specified'} - Battles: {battle_count}, Votes: {vote_count}")
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "message": f"Session '{session_id}' flagged for review",
        "session_id": session_id,
        "reason": reason,
        "battle_count": battle_count,
        "vote_count": vote_count,
        "note": "Manual review required - session flagging table not implemented in Stage 0"
    })


@app.post("/admin/backup")
async def admin_trigger_backup(is_admin: bool = Depends(verify_admin_key)):
    """
    S1-A4: Trigger a manual database backup.
    
    Copies the SQLite database file to the backup directory.
    """
    import shutil
    from pathlib import Path
    
    try:
        db_path = Path(config.db_path)
        backup_dir = Path(config.backup_path)
        
        if not db_path.exists():
            raise_api_error(
                ErrorCode.INTERNAL_ERROR,
                f"Database file not found: {config.db_path}",
                retryable=False,
                status_code=500
            )
        
        # Create backup directory if it doesn't exist
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_filename = f"arena_manual_{timestamp}.sqlite"
        backup_path = backup_dir / backup_filename
        
        # Copy database file
        shutil.copy2(db_path, backup_path)
        
        backup_size_bytes = backup_path.stat().st_size
        backup_size_mb = backup_size_bytes / (1024 * 1024)
        
        logger.info(f"Admin: Manual backup created - {backup_filename} ({backup_size_mb:.2f} MB)")
        
        return JSONResponse({
            "protocol_version": "arena/v0",
            "message": "Backup created successfully",
            "backup_filename": backup_filename,
            "backup_path": str(backup_path),
            "backup_size_bytes": backup_size_bytes,
            "backup_size_mb": round(backup_size_mb, 2),
            "timestamp": timestamp
        })
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            f"Failed to create backup: {str(e)}",
            retryable=True,
            status_code=500
        )


def main():
    """Run the server."""
    logger.info(f"Starting server on {config.host}:{config.port}")
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
