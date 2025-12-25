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
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import HTTPException

from config import load_config
from db import init_connection, get_connection, run_migrations, import_generators, init_generator_ratings, import_levels, log_db_status, transaction
from errors import APIError, api_error_handler, http_exception_handler, general_exception_handler, raise_api_error, ErrorCode
from middleware import RequestLoggingMiddleware
from models import (
    BattleRequest, BattleResponse, Battle, BattleSide, GeneratorInfo, LevelFormat, LevelPayload, LevelMetadata, 
    BattlePresentation, PlayOrder, LevelFormatType, Encoding, VoteRequest, VoteResponse, VoteResult,
    LeaderboardPreview, LeaderboardGeneratorPreview
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Load configuration
config = load_config()

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
    Health check endpoint.
    
    Returns server status and protocol version.
    """
    return JSONResponse({
        "protocol_version": "arena/v0",
        "status": "ok",
        "server_time_utc": datetime.now(timezone.utc).isoformat(),
        "build": {
            "backend_version": "0.1.0"
        }
    })


@app.post("/v1/battles:next", response_model=BattleResponse)
@app.post("/v1/battles%3Anext", response_model=BattleResponse)  # Handle URL-encoded version for PowerShell
async def fetch_next_battle(request: BattleRequest):
    """
    Fetch the next battle: two levels from different generators.
    
    Creates a persisted battle row and returns both levels with metadata.
    
    Note: Registered with both `:` and `%3A` to handle PowerShell Invoke-RestMethod URL encoding.
    """
    conn = get_connection()
    
    # 1. Validate session_id is present and looks like a UUID
    try:
        uuid.UUID(request.session_id)
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
    top_generator_id = selected_generators[0]
    bottom_generator_id = selected_generators[1]
    
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
    # Query random level for top generator
    cursor = conn.execute(
        """
        SELECT level_id FROM levels 
        WHERE generator_id = ? 
        ORDER BY RANDOM() 
        LIMIT 1
        """,
        (top_generator_id,)
    )
    top_level_row = cursor.fetchone()
    
    # Query random level for bottom generator
    cursor = conn.execute(
        """
        SELECT level_id FROM levels 
        WHERE generator_id = ? 
        ORDER BY RANDOM() 
        LIMIT 1
        """,
        (bottom_generator_id,)
    )
    bottom_level_row = cursor.fetchone()
    
    # Check if we have levels for both generators
    if not top_level_row or not bottom_level_row:
        # Count how many generators have levels
        cursor = conn.execute(
            """
            SELECT COUNT(DISTINCT generator_id) as count
            FROM levels
            WHERE generator_id IN (?, ?)
            """,
            (top_generator_id, bottom_generator_id)
        )
        eligible_count = cursor.fetchone()["count"]
        
        raise_api_error(
            ErrorCode.NO_BATTLE_AVAILABLE,
            f"Not enough generators with levels available (found {eligible_count} eligible generators, need 2)",
            retryable=False,
            status_code=503
        )
    
    top_level_id = top_level_row["level_id"]
    bottom_level_id = bottom_level_row["level_id"]
    
    # Ensure top and bottom levels are different (should be guaranteed by different generators, but double-check)
    if top_level_id == bottom_level_id:
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
                    top_level_id, bottom_level_id,
                    top_generator_id, bottom_generator_id,
                    matchmaking_policy, created_at_utc, updated_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    battle_id,
                    request.session_id,
                    now_utc,
                    None,  # expires_at_utc = NULL (no expiry for Stage 0)
                    "ISSUED",
                    top_level_id,
                    bottom_level_id,
                    top_generator_id,
                    bottom_generator_id,
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
    # Top side
    cursor = conn.execute(
        """
        SELECT 
            l.level_id, l.width, l.height, l.tilemap_text, l.content_hash, l.seed, l.controls_json,
            g.generator_id, g.name, g.version, g.documentation_url
        FROM levels l
        JOIN generators g ON l.generator_id = g.generator_id
        WHERE l.level_id = ?
        """,
        (top_level_id,)
    )
    top_data = cursor.fetchone()
    
    # Bottom side
    cursor = conn.execute(
        """
        SELECT 
            l.level_id, l.width, l.height, l.tilemap_text, l.content_hash, l.seed, l.controls_json,
            g.generator_id, g.name, g.version, g.documentation_url
        FROM levels l
        JOIN generators g ON l.generator_id = g.generator_id
        WHERE l.level_id = ?
        """,
        (bottom_level_id,)
    )
    bottom_data = cursor.fetchone()
    
    if not top_data or not bottom_data:
        logger.error(f"Failed to fetch level data: top={top_level_id}, bottom={bottom_level_id}")
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "Failed to fetch level data after battle creation",
            retryable=True,
            status_code=500
        )
    
    # Parse controls_json
    top_controls = json.loads(top_data["controls_json"]) if top_data["controls_json"] else {}
    bottom_controls = json.loads(bottom_data["controls_json"]) if bottom_data["controls_json"] else {}
    
    # Build response
    # Presentation config (Stage 0): hardcoded values for stable client UX
    # - play_order: TOP_THEN_BOTTOM (client presents top level first, then bottom)
    # - reveal_generator_names_after_vote: true (generator identities revealed after voting)
    # - suggested_time_limit_seconds: 300 (5 minutes total for both levels)
    battle_response = BattleResponse(
        protocol_version="arena/v0",
        battle=Battle(
            battle_id=battle_id,
            issued_at_utc=now_utc,
            expires_at_utc=None,
            presentation=BattlePresentation(
                play_order=PlayOrder.TOP_THEN_BOTTOM,
                reveal_generator_names_after_vote=True,
                suggested_time_limit_seconds=300
            ),
            top=BattleSide(
                level_id=top_data["level_id"],
                generator=GeneratorInfo(
                    generator_id=top_data["generator_id"],
                    name=top_data["name"],
                    version=top_data["version"],
                    documentation_url=top_data["documentation_url"]
                ),
                format=LevelFormat(
                    type=LevelFormatType.ASCII_TILEMAP,
                    width=top_data["width"],
                    height=top_data["height"],
                    newline="\n"
                ),
                level_payload=LevelPayload(
                    encoding=Encoding.UTF8,
                    tilemap=top_data["tilemap_text"]
                ),
                content_hash=top_data["content_hash"],
                metadata=LevelMetadata(
                    seed=top_data["seed"],
                    controls=top_controls
                )
            ),
            bottom=BattleSide(
                level_id=bottom_data["level_id"],
                generator=GeneratorInfo(
                    generator_id=bottom_data["generator_id"],
                    name=bottom_data["name"],
                    version=bottom_data["version"],
                    documentation_url=bottom_data["documentation_url"]
                ),
                format=LevelFormat(
                    type=LevelFormatType.ASCII_TILEMAP,
                    width=bottom_data["width"],
                    height=bottom_data["height"],
                    newline="\n"
                ),
                level_payload=LevelPayload(
                    encoding=Encoding.UTF8,
                    tilemap=bottom_data["tilemap_text"]
                ),
                content_hash=bottom_data["content_hash"],
                metadata=LevelMetadata(
                    seed=bottom_data["seed"],
                    controls=bottom_controls
                )
            )
        )
    )
    
    logger.info(
        f"Battle issued: battle_id={battle_id} "
        f"top_gen={top_generator_id} bottom_gen={bottom_generator_id} "
        f"top_level={top_level_id} bottom_level={bottom_level_id}"
    )
    
    return battle_response


def compute_payload_hash(battle_id: str, session_id: str, result: str, top_tags: list, bottom_tags: list, telemetry: dict) -> str:
    """
    Compute canonical payload hash for idempotency checking.
    
    Creates a deterministic hash from battle_id, session_id, result, sorted tags, and telemetry.
    This ensures that identical vote payloads produce the same hash.
    
    Args:
        battle_id: Battle identifier
        session_id: Session identifier
        result: Vote result (TOP, BOTTOM, TIE, SKIP)
        top_tags: List of tags for top level (will be sorted)
        bottom_tags: List of tags for bottom level (will be sorted)
        telemetry: Telemetry dict (will be serialized as canonical JSON)
    
    Returns:
        SHA256 hash as hex string
    """
    # Sort tags for canonical representation
    sorted_top_tags = sorted(top_tags) if top_tags else []
    sorted_bottom_tags = sorted(bottom_tags) if bottom_tags else []
    
    # Serialize telemetry as canonical JSON (sorted keys, no whitespace)
    telemetry_json = json.dumps(telemetry, sort_keys=True, separators=(',', ':')) if telemetry else '{}'
    
    # Create canonical payload string
    payload_str = json.dumps({
        "battle_id": battle_id,
        "session_id": session_id,
        "result": result,
        "top_tags": sorted_top_tags,
        "bottom_tags": sorted_bottom_tags,
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
    top_generator_id: str,
    bottom_generator_id: str,
    result: str,
    k_factor: float,
    now_utc: str,
    initial_rating: float = 1000.0
) -> tuple[float, float]:
    """
    Update generator ratings based on vote result using Elo rating system (Task D1).
    
    Implements standard Elo rating calculation:
    - Expected score: E_top = 1 / (1 + 10^((R_bottom - R_top)/400))
    - Delta: delta_top = K * (S_top - E_top), delta_bottom = -delta_top
    - Updates rating_value and counters (wins, losses, ties, games_played)
    
    SKIP semantics (Task C3):
    - Do NOT change rating_value for either generator
    - Increment skips counter for BOTH generators
    - Do NOT increment games_played (games_played is for rating-relevant matches only)
    - Return (0.0, 0.0) for deltas (no rating change)
    
    Args:
        cursor: Database cursor (within transaction)
        top_generator_id: Top generator ID
        bottom_generator_id: Bottom generator ID
        result: Vote result (TOP, BOTTOM, TIE, SKIP)
        k_factor: ELO K-factor (default 24)
        now_utc: Current UTC timestamp
        initial_rating: Initial rating if row doesn't exist (default 1000.0)
    
    Returns:
        Tuple of (delta_top, delta_bottom) rating changes
    """
    # Task D2: Ensure ratings rows exist before updating
    ensure_ratings_exist(cursor, top_generator_id, initial_rating, now_utc)
    ensure_ratings_exist(cursor, bottom_generator_id, initial_rating, now_utc)
    
    if result == VoteResult.SKIP.value or result == "SKIP":
        # SKIP semantics: increment skip counters for both generators, no rating change
        # Note: games_played is NOT incremented for SKIP (it's for rating-relevant matches only)
        cursor.execute(
            """
            UPDATE ratings 
            SET skips = skips + 1, updated_at_utc = ?
            WHERE generator_id = ?
            """,
            (now_utc, top_generator_id)
        )
        cursor.execute(
            """
            UPDATE ratings 
            SET skips = skips + 1, updated_at_utc = ?
            WHERE generator_id = ?
            """,
            (now_utc, bottom_generator_id)
        )
        logger.info(
            f"SKIP vote processed: top_gen={top_generator_id} bottom_gen={bottom_generator_id} "
            f"(skip counters incremented, no rating change)"
        )
        return (0.0, 0.0)
    
    # Task D1: Fetch current ratings
    cursor.execute(
        "SELECT rating_value FROM ratings WHERE generator_id = ?",
        (top_generator_id,)
    )
    top_row = cursor.fetchone()
    R_top = top_row["rating_value"] if top_row else initial_rating
    
    cursor.execute(
        "SELECT rating_value FROM ratings WHERE generator_id = ?",
        (bottom_generator_id,)
    )
    bottom_row = cursor.fetchone()
    R_bottom = bottom_row["rating_value"] if bottom_row else initial_rating
    
    # Calculate expected scores (Elo formula)
    # E_top = 1 / (1 + 10^((R_bottom - R_top)/400))
    rating_diff = (R_bottom - R_top) / 400.0
    E_top = 1.0 / (1.0 + math.pow(10.0, rating_diff))
    E_bottom = 1.0 - E_top
    
    # Determine outcome scores based on result
    if result == VoteResult.TOP.value or result == "TOP":
        S_top = 1.0
        S_bottom = 0.0
    elif result == VoteResult.BOTTOM.value or result == "BOTTOM":
        S_top = 0.0
        S_bottom = 1.0
    elif result == VoteResult.TIE.value or result == "TIE":
        S_top = 0.5
        S_bottom = 0.5
    else:
        # Should not happen, but handle gracefully
        logger.error(f"Unexpected vote result: {result}")
        return (0.0, 0.0)
    
    # Calculate rating deltas
    # delta_top = K * (S_top - E_top)
    # delta_bottom = -delta_top (zero-sum: ratings are conserved)
    delta_top = k_factor * (S_top - E_top)
    delta_bottom = -delta_top
    
    # Update top generator rating and counters
    new_rating_top = R_top + delta_top
    if result == VoteResult.TOP.value or result == "TOP":
        cursor.execute(
            """
            UPDATE ratings 
            SET rating_value = ?, games_played = games_played + 1,
                wins = wins + 1, updated_at_utc = ?
            WHERE generator_id = ?
            """,
            (new_rating_top, now_utc, top_generator_id)
        )
    elif result == VoteResult.BOTTOM.value or result == "BOTTOM":
        cursor.execute(
            """
            UPDATE ratings 
            SET rating_value = ?, games_played = games_played + 1,
                losses = losses + 1, updated_at_utc = ?
            WHERE generator_id = ?
            """,
            (new_rating_top, now_utc, top_generator_id)
        )
    elif result == VoteResult.TIE.value or result == "TIE":
        cursor.execute(
            """
            UPDATE ratings 
            SET rating_value = ?, games_played = games_played + 1,
                ties = ties + 1, updated_at_utc = ?
            WHERE generator_id = ?
            """,
            (new_rating_top, now_utc, top_generator_id)
        )
    
    # Update bottom generator rating and counters
    new_rating_bottom = R_bottom + delta_bottom
    if result == VoteResult.TOP.value or result == "TOP":
        cursor.execute(
            """
            UPDATE ratings 
            SET rating_value = ?, games_played = games_played + 1,
                losses = losses + 1, updated_at_utc = ?
            WHERE generator_id = ?
            """,
            (new_rating_bottom, now_utc, bottom_generator_id)
        )
    elif result == VoteResult.BOTTOM.value or result == "BOTTOM":
        cursor.execute(
            """
            UPDATE ratings 
            SET rating_value = ?, games_played = games_played + 1,
                wins = wins + 1, updated_at_utc = ?
            WHERE generator_id = ?
            """,
            (new_rating_bottom, now_utc, bottom_generator_id)
        )
    elif result == VoteResult.TIE.value or result == "TIE":
        cursor.execute(
            """
            UPDATE ratings 
            SET rating_value = ?, games_played = games_played + 1,
                ties = ties + 1, updated_at_utc = ?
            WHERE generator_id = ?
            """,
            (new_rating_bottom, now_utc, bottom_generator_id)
        )
    
    logger.info(
        f"Elo rating update: top_gen={top_generator_id} bottom_gen={bottom_generator_id} "
        f"result={result} R_top={R_top:.1f}->{new_rating_top:.1f} "
        f"R_bottom={R_bottom:.1f}->{new_rating_bottom:.1f} "
        f"delta_top={delta_top:.2f} delta_bottom={delta_bottom:.2f}"
    )
    
    return (delta_top, delta_bottom)


def insert_rating_event(
    cursor: sqlite3.Cursor,
    vote_id: str,
    battle_id: str,
    top_generator_id: str,
    bottom_generator_id: str,
    result: str,
    delta_top: float,
    delta_bottom: float,
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
        top_generator_id: Top generator ID
        bottom_generator_id: Bottom generator ID
        result: Vote result (TOP, BOTTOM, TIE, SKIP)
        delta_top: Rating change for top generator (0.0 for SKIP)
        delta_bottom: Rating change for bottom generator (0.0 for SKIP)
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
            top_generator_id, bottom_generator_id,
            result, delta_top, delta_bottom,
            created_at_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            vote_id,
            battle_id,
            top_generator_id,
            bottom_generator_id,
            result,
            delta_top,
            delta_bottom,
            now_utc,
        )
    )


@app.post("/v1/votes", response_model=VoteResponse)
async def submit_vote(request: VoteRequest):
    """
    Submit a vote for a battle.
    
    Accepts vote outcome, ensures idempotency, and atomically updates database and ratings.
    """
    conn = get_connection()
    now_utc = datetime.now(timezone.utc).isoformat()
    
    # Request validation
    # session_id and battle_id are required by Pydantic model
    # result is validated by VoteResult enum
    
    # Validate tags vocabulary for top level
    if request.top_tags:
        invalid_tags = [tag for tag in request.top_tags if tag not in ALLOWED_TAGS]
        if invalid_tags:
            raise_api_error(
                ErrorCode.INVALID_TAG,
                f"Invalid top tags: {', '.join(invalid_tags)}. Allowed tags: {', '.join(sorted(ALLOWED_TAGS))}",
                retryable=False,
                status_code=400,
                details={"invalid_tags": invalid_tags, "allowed_tags": sorted(ALLOWED_TAGS)}
            )
    
    # Validate tags vocabulary for bottom level
    if request.bottom_tags:
        invalid_tags = [tag for tag in request.bottom_tags if tag not in ALLOWED_TAGS]
        if invalid_tags:
            raise_api_error(
                ErrorCode.INVALID_TAG,
                f"Invalid bottom tags: {', '.join(invalid_tags)}. Allowed tags: {', '.join(sorted(ALLOWED_TAGS))}",
                retryable=False,
                status_code=400,
                details={"invalid_tags": invalid_tags, "allowed_tags": sorted(ALLOWED_TAGS)}
            )
    
    # Prepare telemetry JSON
    telemetry_dict = request.telemetry.model_dump() if request.telemetry else {}
    
    # Compute canonical payload hash for idempotency
    top_tags_list = request.top_tags if request.top_tags else []
    bottom_tags_list = request.bottom_tags if request.bottom_tags else []
    payload_hash = compute_payload_hash(
        request.battle_id,
        request.session_id,
        request.result.value,
        top_tags_list,
        bottom_tags_list,
        telemetry_dict
    )
    
    # Transaction: all operations must be atomic
    try:
        with transaction() as cursor:
            # 1. Load battle by battle_id
            cursor.execute(
                "SELECT * FROM battles WHERE battle_id = ?",
                (request.battle_id,)
            )
            battle_row = cursor.fetchone()
            
            if not battle_row:
                raise_api_error(
                    ErrorCode.BATTLE_NOT_FOUND,
                    f"Battle with ID '{request.battle_id}' not found",
                    retryable=False,
                    status_code=404
                )
            
            battle_status = battle_row["status"]
            battle_session_id = battle_row["session_id"]
            top_generator_id = battle_row["top_generator_id"]
            bottom_generator_id = battle_row["bottom_generator_id"]
            
            # 2. Check battle status
            if battle_status != "ISSUED":
                if battle_status == "COMPLETED":
                    # Check if vote exists (idempotency path)
                    cursor.execute(
                        "SELECT vote_id, payload_hash FROM votes WHERE battle_id = ?",
                        (request.battle_id,)
                    )
                    existing_vote = cursor.fetchone()
                    
                    if existing_vote:
                        stored_hash = existing_vote["payload_hash"]
                        if stored_hash == payload_hash:
                            # Idempotent replay: return existing vote
                            vote_id = existing_vote["vote_id"]
                            logger.info(f"Idempotent vote replay: battle_id={request.battle_id} vote_id={vote_id}")
                            
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
                                f"Vote already exists for battle '{request.battle_id}' with different payload",
                                retryable=False,
                                status_code=409,
                                details={"battle_id": request.battle_id, "existing_vote_id": existing_vote["vote_id"]}
                            )
                    else:
                        # COMPLETED but no vote? This shouldn't happen, but handle gracefully
                        raise_api_error(
                            ErrorCode.BATTLE_ALREADY_VOTED,
                            f"Battle '{request.battle_id}' is COMPLETED but no vote found (inconsistent state)",
                            retryable=False,
                            status_code=409
                        )
                else:
                    # EXPIRED or other status
                    raise_api_error(
                        ErrorCode.BATTLE_ALREADY_VOTED,
                        f"Battle '{request.battle_id}' has status '{battle_status}' and cannot be voted on",
                        retryable=False,
                        status_code=409
                    )
            
            # 3. Check session_id matches
            if battle_session_id != request.session_id:
                raise_api_error(
                    ErrorCode.INVALID_PAYLOAD,
                    f"Session ID mismatch: battle session_id='{battle_session_id}' but request session_id='{request.session_id}'",
                    retryable=False,
                    status_code=400
                )
            
            # 4. Payload hash already computed above
            
            # 5. Check if vote already exists (shouldn't for ISSUED battle, but check anyway)
            cursor.execute(
                "SELECT vote_id, payload_hash FROM votes WHERE battle_id = ?",
                (request.battle_id,)
            )
            existing_vote = cursor.fetchone()
            
            if existing_vote:
                stored_hash = existing_vote["payload_hash"]
                if stored_hash == payload_hash:
                    # Idempotent replay
                    vote_id = existing_vote["vote_id"]
                    logger.info(f"Idempotent vote replay: battle_id={request.battle_id} vote_id={vote_id}")
                else:
                    raise_api_error(
                        ErrorCode.DUPLICATE_VOTE_CONFLICT,
                        f"Vote already exists for battle '{request.battle_id}' with different payload",
                        retryable=False,
                        status_code=409
                    )
            else:
                # 6. Insert new vote
                vote_id = f"v_{uuid.uuid4()}"
                top_tags_json = json.dumps(sorted(top_tags_list)) if top_tags_list else "[]"
                bottom_tags_json = json.dumps(sorted(bottom_tags_list)) if bottom_tags_list else "[]"
                telemetry_json = json.dumps(telemetry_dict, sort_keys=True) if telemetry_dict else "{}"
                
                cursor.execute(
                    """
                    INSERT INTO votes (
                        vote_id, battle_id, session_id,
                        created_at_utc, result, top_tags_json, bottom_tags_json, telemetry_json, payload_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        vote_id,
                        request.battle_id,
                        request.session_id,
                        now_utc,
                        request.result.value,
                        top_tags_json,
                        bottom_tags_json,
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
                    (now_utc, request.battle_id)
                )
                
                # 8. Update ratings using Elo rating system
                delta_top, delta_bottom = update_ratings(
                    cursor,
                    top_generator_id,
                    bottom_generator_id,
                    request.result.value,
                    config.k_factor,
                    now_utc,
                    config.initial_rating
                )
                
                # 9. Insert rating event for auditability
                insert_rating_event(
                    cursor,
                    vote_id,
                    request.battle_id,
                    top_generator_id,
                    bottom_generator_id,
                    request.result.value,
                    delta_top,
                    delta_bottom,
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
                f"Vote accepted: vote_id={vote_id} battle_id={request.battle_id} "
                f"result={request.result.value} top_tags={top_tags_list} bottom_tags={bottom_tags_list}"
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
            "top_level_id": row["top_level_id"],
            "bottom_level_id": row["bottom_level_id"],
            "top_generator_id": row["top_generator_id"],
            "bottom_generator_id": row["bottom_generator_id"],
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
            "top_tags": json.loads(row["top_tags_json"]) if row["top_tags_json"] else [],
            "bottom_tags": json.loads(row["bottom_tags_json"]) if row["bottom_tags_json"] else [],
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

