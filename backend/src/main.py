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
from fastapi import FastAPI, Request, Response, Header, Depends, UploadFile, Form, File
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
from auth import (
    User, DevLoginRequest, GoogleLoginRequest, EmailRegisterRequest, EmailLoginRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
    get_current_user, create_user, get_user_by_email, get_user_by_google_sub,
    create_session, delete_session, set_session_cookie, clear_session_cookie,
    update_last_login, cleanup_expired_sessions, verify_google_token, SESSION_COOKIE_NAME,
    hash_password, verify_password, validate_password, get_password_hash_by_email,
    create_email_verification_token, verify_email_token, send_verification_email,
    create_password_reset_token, verify_password_reset_token, use_password_reset_token,
    update_user_password, send_password_reset_email, mark_email_verified
)
from builders import (
    GeneratorMetadata, GeneratorInfo as BuilderGeneratorInfo, BuilderError,
    get_user_generators, create_generator, update_generator, delete_generator,
    MAX_GENERATORS_PER_USER, MIN_LEVELS_PER_GENERATOR, MAX_LEVELS_PER_GENERATOR
)
from matchmaking import (
    select_generators_agis, select_random_level, update_pair_stats, get_matchmaking_stats
)
from glicko2 import (
    update_ratings_glicko2, GlickoRating, DEFAULT_RD, DEFAULT_VOLATILITY
)
from stats import (
    update_level_stats_for_vote, update_player_profile_for_vote,
    update_player_session, store_trajectory, get_platform_stats,
    get_level_stats, get_level_heatmap
)
from level_features import (
    extract_features_from_tilemap, store_level_features,
    extract_and_store_all_level_features, get_level_features
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
        
        # Initialize Glicko-2 ratings for new generators
        ratings_init = init_generator_ratings(
            config.initial_rating, 
            config.initial_rd,
            config.initial_volatility
        )
        if ratings_init > 0:
            logger.info(f"Initialized Glicko-2 ratings for {ratings_init} new generator(s)")
        
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
    
    # 2. Select generators using matchmaking policy
    # AGIS (Adaptive Glicko-Informed Selection) considers:
    # - Generator uncertainty (RD): prioritize uncertain generators
    # - Rating similarity: prefer similar skill levels
    # - Coverage: ensure all pairs get enough battles
    # - Quality bias: slight preference for better generators after convergence
    
    matchmaking_policy = config.matchmaking_policy
    
    try:
        if matchmaking_policy == "agis_v1":
            # Use AGIS algorithm for smart matchmaking
            left_generator_id, right_generator_id = select_generators_agis(conn)
        else:
            # Fallback to uniform random selection
            cursor = conn.execute(
                "SELECT generator_id FROM generators WHERE is_active = 1"
            )
            active_generators = [row["generator_id"] for row in cursor.fetchall()]
            
            if len(active_generators) < 2:
                raise ValueError(f"Need at least 2 active generators, found {len(active_generators)}")
            
            selected_generators = random.sample(active_generators, 2)
            left_generator_id = selected_generators[0]
            right_generator_id = selected_generators[1]
            matchmaking_policy = "uniform_v0"
            
    except ValueError as e:
        raise_api_error(
            ErrorCode.NO_BATTLE_AVAILABLE,
            str(e),
            retryable=False,
            status_code=503
        )
    
    # 3. Select random levels from each generator
    left_level_id = select_random_level(conn, left_generator_id)
    right_level_id = select_random_level(conn, right_generator_id)
    
    if not left_level_id or not right_level_id:
        raise_api_error(
            ErrorCode.NO_BATTLE_AVAILABLE,
            f"Selected generators have no levels",
            retryable=False,
            status_code=503
        )
    
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
                    matchmaking_policy,
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
    initial_rd: float,
    initial_volatility: float,
    now_utc: str
) -> None:
    """
    Ensure a Glicko-2 ratings row exists for a generator.
    
    If the ratings row doesn't exist, creates it with initial values.
    This is defensive programming to handle edge cases where a generator
    might be added without a ratings row.
    
    Args:
        cursor: Database cursor (within transaction)
        generator_id: Generator ID to check/create
        initial_rating: Initial rating value (default 1000.0)
        initial_rd: Initial rating deviation (default 350.0)
        initial_volatility: Initial volatility (default 0.06)
        now_utc: Current UTC timestamp
    """
    cursor.execute(
        "SELECT generator_id FROM ratings WHERE generator_id = ?",
        (generator_id,)
    )
    if cursor.fetchone() is None:
        logger.warning(f"Ratings row missing for generator {generator_id}, creating with Glicko-2 defaults")
        cursor.execute(
            """
            INSERT INTO ratings (
                generator_id, rating_value, rd, volatility,
                games_played, wins, losses, ties, skips, updated_at_utc
            ) VALUES (?, ?, ?, ?, 0, 0, 0, 0, 0, ?)
            """,
            (generator_id, initial_rating, initial_rd, initial_volatility, now_utc)
        )


def update_ratings(
    cursor: sqlite3.Cursor,
    left_generator_id: str,
    right_generator_id: str,
    result: str,
    now_utc: str,
    initial_rating: float = 1000.0,
    initial_rd: float = 350.0,
    initial_volatility: float = 0.06
) -> tuple[float, float, dict]:
    """
    Update generator ratings based on vote result using Glicko-2 rating system.
    
    Glicko-2 features:
    - Rating (μ): Skill estimate
    - Rating Deviation (RD/φ): Uncertainty in rating (decreases with more games)
    - Volatility (σ): Expected fluctuation in performance
    
    SKIP semantics:
    - Do NOT change rating_value, RD, or volatility for either generator
    - Increment skips counter for BOTH generators
    - Do NOT increment games_played
    - Return (0.0, 0.0, {}) for deltas
    
    Args:
        cursor: Database cursor (within transaction)
        left_generator_id: Left generator ID
        right_generator_id: Right generator ID
        result: Vote result (LEFT, RIGHT, TIE, SKIP)
        now_utc: Current UTC timestamp
        initial_rating: Initial rating if row doesn't exist (default 1000.0)
        initial_rd: Initial rating deviation (default 350.0)
        initial_volatility: Initial volatility (default 0.06)
    
    Returns:
        Tuple of (delta_left, delta_right, rd_info) where rd_info contains RD before/after
    """
    # Ensure ratings rows exist before updating
    ensure_ratings_exist(cursor, left_generator_id, initial_rating, initial_rd, initial_volatility, now_utc)
    ensure_ratings_exist(cursor, right_generator_id, initial_rating, initial_rd, initial_volatility, now_utc)
    
    if result == VoteResult.SKIP.value or result == "SKIP":
        # SKIP semantics: increment skip counters, no rating change
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
        return (0.0, 0.0, {})
    
    # Fetch current Glicko-2 ratings
    cursor.execute(
        "SELECT rating_value, rd, volatility FROM ratings WHERE generator_id = ?",
        (left_generator_id,)
    )
    left_row = cursor.fetchone()
    left_rating = left_row["rating_value"] if left_row else initial_rating
    left_rd = left_row["rd"] if left_row and left_row["rd"] else initial_rd
    left_volatility = left_row["volatility"] if left_row and left_row["volatility"] else initial_volatility
    
    cursor.execute(
        "SELECT rating_value, rd, volatility FROM ratings WHERE generator_id = ?",
        (right_generator_id,)
    )
    right_row = cursor.fetchone()
    right_rating = right_row["rating_value"] if right_row else initial_rating
    right_rd = right_row["rd"] if right_row and right_row["rd"] else initial_rd
    right_volatility = right_row["volatility"] if right_row and right_row["volatility"] else initial_volatility
    
    # Update ratings using Glicko-2
    new_left, new_right = update_ratings_glicko2(
        left_rating, left_rd, left_volatility,
        right_rating, right_rd, right_volatility,
        result
    )
    
    # Calculate deltas for audit trail
    delta_left = new_left.rating - left_rating
    delta_right = new_right.rating - right_rating
    
    # RD info for audit trail
    rd_info = {
        "rd_left_before": left_rd,
        "rd_left_after": new_left.rd,
        "rd_right_before": right_rd,
        "rd_right_after": new_right.rd
    }
    
    # Update left generator
    if result == VoteResult.LEFT.value or result == "LEFT":
        counter_update = "wins = wins + 1"
    elif result == VoteResult.RIGHT.value or result == "RIGHT":
        counter_update = "losses = losses + 1"
    else:  # TIE
        counter_update = "ties = ties + 1"
    
    cursor.execute(
        f"""
        UPDATE ratings 
        SET rating_value = ?, rd = ?, volatility = ?,
            games_played = games_played + 1, {counter_update},
            updated_at_utc = ?
        WHERE generator_id = ?
        """,
        (new_left.rating, new_left.rd, new_left.volatility, now_utc, left_generator_id)
    )
    
    # Update right generator (opposite outcome)
    if result == VoteResult.LEFT.value or result == "LEFT":
        counter_update = "losses = losses + 1"
    elif result == VoteResult.RIGHT.value or result == "RIGHT":
        counter_update = "wins = wins + 1"
    else:  # TIE
        counter_update = "ties = ties + 1"
    
    cursor.execute(
        f"""
        UPDATE ratings 
        SET rating_value = ?, rd = ?, volatility = ?,
            games_played = games_played + 1, {counter_update},
            updated_at_utc = ?
        WHERE generator_id = ?
        """,
        (new_right.rating, new_right.rd, new_right.volatility, now_utc, right_generator_id)
    )
    
    logger.info(
        f"Glicko-2 rating update: left_gen={left_generator_id} right_gen={right_generator_id} "
        f"result={result} "
        f"left={left_rating:.1f}±{left_rd:.0f} -> {new_left.rating:.1f}±{new_left.rd:.0f} "
        f"right={right_rating:.1f}±{right_rd:.0f} -> {new_right.rating:.1f}±{new_right.rd:.0f}"
    )
    
    return (delta_left, delta_right, rd_info)


def insert_rating_event(
    cursor: sqlite3.Cursor,
    vote_id: str,
    battle_id: str,
    left_generator_id: str,
    right_generator_id: str,
    result: str,
    delta_left: float,
    delta_right: float,
    now_utc: str,
    rd_info: dict = None
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
        rd_info: Optional dict with RD before/after values for Glicko-2
    
    Note:
        This function is called within the vote submission transaction, ensuring
        that rating events are created atomically with votes. For idempotent
        vote replays, this function is not called (the event already exists).
    """
    event_id = f"evt_{uuid.uuid4()}"
    
    # Extract RD info if provided
    rd_left_before = rd_info.get("rd_left_before") if rd_info else None
    rd_left_after = rd_info.get("rd_left_after") if rd_info else None
    rd_right_before = rd_info.get("rd_right_before") if rd_info else None
    rd_right_after = rd_info.get("rd_right_after") if rd_info else None
    
    cursor.execute(
        """
        INSERT INTO rating_events (
            event_id, vote_id, battle_id,
            left_generator_id, right_generator_id,
            result, delta_left, delta_right,
            rd_left_before, rd_left_after, rd_right_before, rd_right_after,
            created_at_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            rd_left_before,
            rd_left_after,
            rd_right_before,
            rd_right_after,
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
                        vote_id, battle_id, session_id, player_id,
                        created_at_utc, result, left_tags_json, right_tags_json, telemetry_json, payload_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        vote_id,
                        vote_request.battle_id,
                        vote_request.session_id,
                        vote_request.player_id,  # Stage 5: Include player_id
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
                
                # 8. Update ratings using Glicko-2 rating system
                delta_left, delta_right, rd_info = update_ratings(
                    cursor,
                    left_generator_id,
                    right_generator_id,
                    vote_request.result.value,
                    now_utc,
                    config.initial_rating,
                    config.initial_rd,
                    config.initial_volatility
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
                    now_utc,
                    rd_info
                )
                
                # 10. Update generator pair statistics
                update_pair_stats(
                    cursor,
                    left_generator_id,
                    right_generator_id,
                    vote_request.result.value,
                    now_utc
                )
                
                # Stage 5: Get level IDs for stats tracking
                cursor.execute(
                    "SELECT left_level_id, right_level_id FROM battles WHERE battle_id = ?",
                    (vote_request.battle_id,)
                )
                level_row = cursor.fetchone()
                left_level_id = level_row["left_level_id"] if level_row else None
                right_level_id = level_row["right_level_id"] if level_row else None
                
                if left_level_id and right_level_id:
                    # 11. Stage 5: Update per-level statistics
                    left_telemetry_data = telemetry_dict.get("left", {}) if telemetry_dict else {}
                    right_telemetry_data = telemetry_dict.get("right", {}) if telemetry_dict else {}
                    
                    update_level_stats_for_vote(
                        cursor,
                        left_level_id,
                        right_level_id,
                        left_generator_id,
                        right_generator_id,
                        vote_request.result.value,
                        left_telemetry_data,
                        right_telemetry_data,
                        left_tags_list,
                        right_tags_list,
                        now_utc
                    )
                    
                    # 12. Stage 5: Update player profile
                    update_player_profile_for_vote(
                        cursor,
                        vote_request.player_id,
                        now_utc
                    )
                    
                    # 13. Stage 5: Update player session
                    update_player_session(
                        cursor,
                        vote_request.session_id,
                        vote_request.player_id,
                        now_utc
                    )
                    
                    # 14. Stage 5: Store trajectories if available
                    if left_telemetry_data.get("trajectory"):
                        store_trajectory(
                            cursor, vote_id, left_level_id,
                            vote_request.session_id, vote_request.player_id,
                            "left", left_telemetry_data, now_utc
                        )
                    if right_telemetry_data.get("trajectory"):
                        store_trajectory(
                            cursor, vote_id, right_level_id,
                            vote_request.session_id, vote_request.player_id,
                            "right", right_telemetry_data, now_utc
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


# =============================================================================
# Stage 5: Public Statistics API Endpoints
# =============================================================================

@app.get("/v1/stats/platform")
async def get_platform_statistics():
    """
    Get platform-wide aggregate statistics.
    
    Returns totals, vote distribution, and engagement metrics.
    Public endpoint - no authentication required.
    """
    try:
        stats = get_platform_stats()
        return {
            "protocol_version": "arena/v0",
            "stats": stats
        }
    except Exception as e:
        logger.exception(f"Error fetching platform stats: {e}")
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "Failed to fetch platform statistics",
            retryable=True,
            status_code=500
        )


@app.get("/v1/stats/generators/{generator_id}")
async def get_generator_statistics(generator_id: str):
    """
    Get aggregate statistics for a specific generator.
    
    Returns win rates, level performance, and difficulty distribution.
    Public endpoint - no authentication required.
    """
    conn = get_connection()
    
    # Check generator exists
    cursor = conn.execute(
        "SELECT * FROM generators WHERE generator_id = ?",
        (generator_id,)
    )
    gen_row = cursor.fetchone()
    
    if not gen_row:
        raise_api_error(
            ErrorCode.GENERATOR_NOT_FOUND,
            f"Generator '{generator_id}' not found",
            retryable=False,
            status_code=404
        )
    
    # Get level stats for this generator
    cursor = conn.execute(
        """
        SELECT 
            COUNT(*) as level_count,
            SUM(times_shown) as total_shown,
            AVG(win_rate) as avg_win_rate,
            AVG(completion_rate) as avg_completion_rate,
            AVG(avg_deaths) as avg_deaths,
            AVG(avg_duration_seconds) as avg_duration,
            AVG(difficulty_score) as avg_difficulty
        FROM level_stats
        WHERE generator_id = ?
        """,
        (generator_id,)
    )
    stats_row = cursor.fetchone()
    
    # Get individual level stats
    cursor = conn.execute(
        """
        SELECT 
            level_id, times_shown, win_rate, completion_rate,
            avg_deaths, avg_duration_seconds, difficulty_score,
            tag_fun, tag_boring, tag_too_hard, tag_too_easy
        FROM level_stats
        WHERE generator_id = ?
        ORDER BY times_shown DESC
        """,
        (generator_id,)
    )
    level_rows = cursor.fetchall()
    
    # Get tag totals
    cursor = conn.execute(
        """
        SELECT 
            SUM(tag_fun) as fun,
            SUM(tag_boring) as boring,
            SUM(tag_too_hard) as too_hard,
            SUM(tag_too_easy) as too_easy,
            SUM(tag_creative) as creative,
            SUM(tag_good_flow) as good_flow,
            SUM(tag_unfair) as unfair,
            SUM(tag_confusing) as confusing,
            SUM(tag_not_mario_like) as not_mario_like
        FROM level_stats
        WHERE generator_id = ?
        """,
        (generator_id,)
    )
    tag_row = cursor.fetchone()
    
    return {
        "protocol_version": "arena/v0",
        "generator_id": generator_id,
        "name": gen_row["name"],
        "aggregate": {
            "level_count": stats_row["level_count"] or 0,
            "total_battles": stats_row["total_shown"] or 0,
            "avg_win_rate": round(stats_row["avg_win_rate"] or 0, 3),
            "avg_completion_rate": round(stats_row["avg_completion_rate"] or 0, 3),
            "avg_deaths_per_play": round(stats_row["avg_deaths"] or 0, 1),
            "avg_duration_seconds": round(stats_row["avg_duration"] or 0, 1),
            "avg_difficulty_score": round(stats_row["avg_difficulty"] or 0, 3)
        },
        "tags": {
            "fun": tag_row["fun"] or 0,
            "boring": tag_row["boring"] or 0,
            "too_hard": tag_row["too_hard"] or 0,
            "too_easy": tag_row["too_easy"] or 0,
            "creative": tag_row["creative"] or 0,
            "good_flow": tag_row["good_flow"] or 0,
            "unfair": tag_row["unfair"] or 0,
            "confusing": tag_row["confusing"] or 0,
            "not_mario_like": tag_row["not_mario_like"] or 0
        },
        "levels": [
            {
                "level_id": row["level_id"],
                "times_shown": row["times_shown"],
                "win_rate": round(row["win_rate"] or 0, 3),
                "completion_rate": round(row["completion_rate"] or 0, 3),
                "avg_deaths": round(row["avg_deaths"] or 0, 1),
                "difficulty_score": round(row["difficulty_score"] or 0, 3)
            }
            for row in level_rows
        ]
    }


@app.get("/v1/stats/levels/{level_id}")
async def get_level_statistics(level_id: str):
    """
    Get detailed statistics for a specific level.
    
    Returns performance metrics, tag counts, and structural features.
    Public endpoint - no authentication required.
    """
    # Get level stats
    stats = get_level_stats(level_id)
    
    if not stats:
        # Check if level exists at all
        conn = get_connection()
        cursor = conn.execute(
            "SELECT level_id FROM levels WHERE level_id = ?",
            (level_id,)
        )
        if not cursor.fetchone():
            raise_api_error(
                ErrorCode.LEVEL_NOT_FOUND,
                f"Level '{level_id}' not found",
                retryable=False,
                status_code=404
            )
        # Level exists but no stats yet
        stats = {
            "level_id": level_id,
            "performance": {"times_shown": 0},
            "outcomes": {},
            "tags": {},
            "difficulty": {}
        }
    
    # Get level features
    features = get_level_features(level_id)
    
    return {
        "protocol_version": "arena/v0",
        "level_id": level_id,
        "stats": stats,
        "features": features
    }


@app.get("/v1/stats/levels/{level_id}/heatmap")
async def get_level_heatmap_data(level_id: str):
    """
    Get death heatmap data for a specific level.
    
    Returns aggregate death locations for visualization.
    Public endpoint - no authentication required.
    """
    # Check if level exists
    conn = get_connection()
    cursor = conn.execute(
        "SELECT level_id FROM levels WHERE level_id = ?",
        (level_id,)
    )
    if not cursor.fetchone():
        raise_api_error(
            ErrorCode.LEVEL_NOT_FOUND,
            f"Level '{level_id}' not found",
            retryable=False,
            status_code=404
        )
    
    heatmap = get_level_heatmap(level_id)
    
    return {
        "protocol_version": "arena/v0",
        **heatmap
    }


# =============================================================================
# Stage 5: Admin Data Export API Endpoints (Requires Authentication)
# =============================================================================

@app.get("/v1/admin/export/votes")
async def export_votes(
    current_user: User = Depends(get_current_user),
    limit: int = 1000,
    offset: int = 0
):
    """
    Export vote data with full telemetry.
    
    Admin-only endpoint for research data export.
    Returns paginated vote records with all telemetry.
    """
    # Check if user is admin (you would add proper admin check)
    if not current_user:
        raise_api_error(
            ErrorCode.UNAUTHORIZED,
            "Authentication required for data export",
            retryable=False,
            status_code=401
        )
    
    conn = get_connection()
    
    cursor = conn.execute(
        """
        SELECT 
            v.vote_id, v.battle_id, v.session_id, v.player_id,
            v.created_at_utc, v.result, 
            v.left_tags_json, v.right_tags_json, v.telemetry_json,
            b.left_generator_id, b.right_generator_id,
            b.left_level_id, b.right_level_id
        FROM votes v
        JOIN battles b ON v.battle_id = b.battle_id
        ORDER BY v.created_at_utc DESC
        LIMIT ? OFFSET ?
        """,
        (limit, offset)
    )
    
    votes = []
    for row in cursor.fetchall():
        votes.append({
            "vote_id": row["vote_id"],
            "battle_id": row["battle_id"],
            "session_id": row["session_id"],
            "player_id": row["player_id"],
            "created_at_utc": row["created_at_utc"],
            "result": row["result"],
            "left_generator_id": row["left_generator_id"],
            "right_generator_id": row["right_generator_id"],
            "left_level_id": row["left_level_id"],
            "right_level_id": row["right_level_id"],
            "left_tags": json.loads(row["left_tags_json"]) if row["left_tags_json"] else [],
            "right_tags": json.loads(row["right_tags_json"]) if row["right_tags_json"] else [],
            "telemetry": json.loads(row["telemetry_json"]) if row["telemetry_json"] else {}
        })
    
    # Get total count
    cursor = conn.execute("SELECT COUNT(*) FROM votes")
    total = cursor.fetchone()[0]
    
    return {
        "protocol_version": "arena/v0",
        "export_type": "votes",
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": votes
    }


@app.get("/v1/admin/export/trajectories")
async def export_trajectories(
    current_user: User = Depends(get_current_user),
    level_id: str = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Export trajectory data for heatmap and path analysis.
    
    Admin-only endpoint for research data export.
    Returns paginated trajectory records.
    """
    if not current_user:
        raise_api_error(
            ErrorCode.UNAUTHORIZED,
            "Authentication required for data export",
            retryable=False,
            status_code=401
        )
    
    conn = get_connection()
    
    query = """
        SELECT 
            trajectory_id, vote_id, level_id, session_id, player_id, side,
            trajectory_json, death_locations_json, events_json,
            duration_ticks, max_x_reached, death_count, completed,
            created_at_utc
        FROM play_trajectories
    """
    params = []
    
    if level_id:
        query += " WHERE level_id = ?"
        params.append(level_id)
    
    query += " ORDER BY created_at_utc DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor = conn.execute(query, params)
    
    trajectories = []
    for row in cursor.fetchall():
        trajectories.append({
            "trajectory_id": row["trajectory_id"],
            "vote_id": row["vote_id"],
            "level_id": row["level_id"],
            "session_id": row["session_id"],
            "player_id": row["player_id"],
            "side": row["side"],
            "trajectory": json.loads(row["trajectory_json"]) if row["trajectory_json"] else [],
            "death_locations": json.loads(row["death_locations_json"]) if row["death_locations_json"] else [],
            "events": json.loads(row["events_json"]) if row["events_json"] else [],
            "summary": {
                "duration_ticks": row["duration_ticks"],
                "max_x_reached": row["max_x_reached"],
                "death_count": row["death_count"],
                "completed": bool(row["completed"])
            },
            "created_at_utc": row["created_at_utc"]
        })
    
    # Get total count
    count_query = "SELECT COUNT(*) FROM play_trajectories"
    count_params = []
    if level_id:
        count_query += " WHERE level_id = ?"
        count_params.append(level_id)
    cursor = conn.execute(count_query, count_params)
    total = cursor.fetchone()[0]
    
    return {
        "protocol_version": "arena/v0",
        "export_type": "trajectories",
        "total": total,
        "limit": limit,
        "offset": offset,
        "filter": {"level_id": level_id} if level_id else None,
        "data": trajectories
    }


@app.get("/v1/admin/export/level-stats")
async def export_level_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Export all level statistics.
    
    Admin-only endpoint for research data export.
    Returns all level stats for analysis.
    """
    if not current_user:
        raise_api_error(
            ErrorCode.UNAUTHORIZED,
            "Authentication required for data export",
            retryable=False,
            status_code=401
        )
    
    conn = get_connection()
    
    cursor = conn.execute(
        """
        SELECT ls.*, lf.*
        FROM level_stats ls
        LEFT JOIN level_features lf ON ls.level_id = lf.level_id
        ORDER BY ls.times_shown DESC
        """
    )
    
    stats = []
    for row in cursor.fetchall():
        stats.append(dict(row))
    
    return {
        "protocol_version": "arena/v0",
        "export_type": "level_stats",
        "total": len(stats),
        "data": stats
    }


@app.get("/v1/admin/export/player-profiles")
async def export_player_profiles(
    current_user: User = Depends(get_current_user),
    limit: int = 500,
    offset: int = 0
):
    """
    Export player profile data for clustering analysis.
    
    Admin-only endpoint for research data export.
    Returns player profiles with preference patterns.
    """
    if not current_user:
        raise_api_error(
            ErrorCode.UNAUTHORIZED,
            "Authentication required for data export",
            retryable=False,
            status_code=401
        )
    
    conn = get_connection()
    
    cursor = conn.execute(
        """
        SELECT *
        FROM player_profiles
        ORDER BY total_votes DESC
        LIMIT ? OFFSET ?
        """,
        (limit, offset)
    )
    
    profiles = []
    for row in cursor.fetchall():
        profiles.append(dict(row))
    
    # Get total count
    cursor = conn.execute("SELECT COUNT(*) FROM player_profiles")
    total = cursor.fetchone()[0]
    
    return {
        "protocol_version": "arena/v0",
        "export_type": "player_profiles",
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": profiles
    }


@app.post("/v1/admin/extract-features")
async def trigger_feature_extraction(
    current_user: User = Depends(get_current_user)
):
    """
    Trigger extraction of static features for all levels.
    
    Admin-only endpoint to compute level features.
    """
    if not current_user:
        raise_api_error(
            ErrorCode.UNAUTHORIZED,
            "Authentication required",
            retryable=False,
            status_code=401
        )
    
    count = extract_and_store_all_level_features()
    
    return {
        "protocol_version": "arena/v0",
        "message": f"Extracted features for {count} levels"
    }


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
            r.rd,
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
            "rd": row["rd"] if row["rd"] else config.initial_rd,  # Rating deviation
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
            "name": "Glicko-2",
            "initial_rating": config.initial_rating,
            "initial_rd": config.initial_rd,
        },
        "matchmaking_policy": config.matchmaking_policy,
        "generators": generators,
    })


@app.get("/v1/stats/confusion-matrix")
async def get_confusion_matrix():
    """
    Get the confusion matrix of generator pairwise comparisons.
    
    Returns win rates and battle counts between all generator pairs.
    This is useful for analyzing matchup balance and coverage.
    """
    conn = get_connection()
    
    # Get all active generators
    cursor = conn.execute(
        """
        SELECT generator_id, name 
        FROM generators 
        WHERE is_active = 1
        ORDER BY generator_id
        """
    )
    generators = [{"id": row["generator_id"], "name": row["name"]} for row in cursor.fetchall()]
    generator_ids = [g["id"] for g in generators]
    
    # Get all pair stats
    cursor = conn.execute(
        """
        SELECT 
            gen1_id, gen2_id, battle_count, 
            gen1_wins, gen2_wins, ties, skips
        FROM generator_pair_stats
        """
    )
    
    # Build matrix data
    # matrix[gen1_id][gen2_id] = {battles, gen1_wins, gen2_wins, ...}
    pair_data = {}
    for row in cursor.fetchall():
        key = (row["gen1_id"], row["gen2_id"])
        pair_data[key] = {
            "battle_count": row["battle_count"],
            "gen1_wins": row["gen1_wins"],
            "gen2_wins": row["gen2_wins"],
            "ties": row["ties"],
            "skips": row["skips"],
        }
    
    # Build the matrix
    matrix = []
    for gen1_id in generator_ids:
        row_data = []
        for gen2_id in generator_ids:
            if gen1_id == gen2_id:
                row_data.append(None)  # Diagonal
            else:
                # Normalize key (gen1 < gen2)
                if gen1_id < gen2_id:
                    key = (gen1_id, gen2_id)
                    data = pair_data.get(key, {})
                    row_data.append({
                        "battles": data.get("battle_count", 0),
                        "wins": data.get("gen1_wins", 0),
                        "losses": data.get("gen2_wins", 0),
                        "ties": data.get("ties", 0),
                        "win_rate": data.get("gen1_wins", 0) / data.get("battle_count", 1) if data.get("battle_count", 0) > 0 else None,
                    })
                else:
                    key = (gen2_id, gen1_id)
                    data = pair_data.get(key, {})
                    row_data.append({
                        "battles": data.get("battle_count", 0),
                        "wins": data.get("gen2_wins", 0),  # Flipped
                        "losses": data.get("gen1_wins", 0),  # Flipped
                        "ties": data.get("ties", 0),
                        "win_rate": data.get("gen2_wins", 0) / data.get("battle_count", 1) if data.get("battle_count", 0) > 0 else None,
                    })
        matrix.append(row_data)
    
    # Calculate coverage statistics
    total_pairs = len(generator_ids) * (len(generator_ids) - 1) // 2
    pairs_with_data = len([k for k, v in pair_data.items() if v["battle_count"] > 0])
    target_battles = config.agis_target_battles_per_pair
    pairs_at_target = len([k for k, v in pair_data.items() if v["battle_count"] >= target_battles])
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "generators": generators,
        "matrix": matrix,
        "coverage": {
            "total_pairs": total_pairs,
            "pairs_with_data": pairs_with_data,
            "pairs_at_target": pairs_at_target,
            "target_battles_per_pair": target_battles,
            "coverage_percent": (pairs_with_data / total_pairs * 100) if total_pairs > 0 else 0,
            "target_coverage_percent": (pairs_at_target / total_pairs * 100) if total_pairs > 0 else 0,
        }
    })


def is_admin_user(user: User) -> bool:
    """Check if a user has admin privileges based on their email."""
    if not user:
        return False
    return user.email.lower() in config.admin_emails


@app.get("/v1/admin/stats")
async def get_admin_stats(request: Request):
    """
    Get admin statistics for matchmaking and coverage.
    
    Requires admin authentication (OAuth login with admin email).
    """
    user = get_current_user(request)
    
    if not user:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            "Authentication required. Please log in with Google OAuth.",
            retryable=False,
            status_code=401
        )
    
    if not is_admin_user(user):
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            "Admin access required. Your email is not in the admin list.",
            retryable=False,
            status_code=403
        )
    
    conn = get_connection()
    
    # Get matchmaking stats
    matchmaking_stats = get_matchmaking_stats(conn)
    
    # Get generator stats
    cursor = conn.execute(
        """
        SELECT 
            g.generator_id, g.name,
            r.rating_value, r.rd, r.games_played,
            r.wins, r.losses, r.ties, r.skips
        FROM generators g
        LEFT JOIN ratings r ON g.generator_id = r.generator_id
        WHERE g.is_active = 1
        ORDER BY r.rating_value DESC
        """
    )
    
    generators = []
    for row in cursor.fetchall():
        generators.append({
            "generator_id": row["generator_id"],
            "name": row["name"],
            "rating": row["rating_value"] or config.initial_rating,
            "rd": row["rd"] or config.initial_rd,
            "games_played": row["games_played"] or 0,
            "wins": row["wins"] or 0,
            "losses": row["losses"] or 0,
            "ties": row["ties"] or 0,
            "skips": row["skips"] or 0,
            "needs_more_games": (row["games_played"] or 0) < config.agis_min_games_for_significance,
        })
    
    # Get under-covered pairs (pairs needing more battles)
    cursor = conn.execute(
        """
        SELECT gen1_id, gen2_id, battle_count
        FROM generator_pair_stats
        WHERE battle_count < ?
        ORDER BY battle_count ASC
        LIMIT 20
        """,
        (config.agis_target_battles_per_pair,)
    )
    under_covered_pairs = [
        {"gen1": row["gen1_id"], "gen2": row["gen2_id"], "battles": row["battle_count"]}
        for row in cursor.fetchall()
    ]
    
    # Get missing pairs (no battles at all)
    cursor = conn.execute("SELECT generator_id FROM generators WHERE is_active = 1")
    active_gen_ids = sorted([row["generator_id"] for row in cursor.fetchall()])
    
    cursor = conn.execute("SELECT gen1_id, gen2_id FROM generator_pair_stats")
    existing_pairs = set((row["gen1_id"], row["gen2_id"]) for row in cursor.fetchall())
    
    missing_pairs = []
    for i, g1 in enumerate(active_gen_ids):
        for g2 in active_gen_ids[i+1:]:
            if (g1, g2) not in existing_pairs:
                missing_pairs.append({"gen1": g1, "gen2": g2})
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "user": {
            "email": user.email,
            "is_admin": True,
        },
        "config": {
            "matchmaking_policy": config.matchmaking_policy,
            "initial_rating": config.initial_rating,
            "initial_rd": config.initial_rd,
            "min_games_for_significance": config.agis_min_games_for_significance,
            "target_battles_per_pair": config.agis_target_battles_per_pair,
            "rating_similarity_sigma": config.agis_rating_similarity_sigma,
            "quality_bias_strength": config.agis_quality_bias_strength,
        },
        "matchmaking": matchmaking_stats,
        "generators": generators,
        "coverage_gaps": {
            "under_covered_pairs": under_covered_pairs,
            "missing_pairs": missing_pairs[:20],  # Limit to 20
            "total_missing": len(missing_pairs),
        }
    })


@app.get("/v1/auth/me/admin")
async def check_admin_status(request: Request):
    """
    Check if the current user has admin privileges.
    
    Returns admin status for the frontend to show/hide admin features.
    """
    user = get_current_user(request)
    
    if not user:
        return JSONResponse({
            "authenticated": False,
            "is_admin": False,
        })
    
    return JSONResponse({
        "authenticated": True,
        "is_admin": is_admin_user(user),
        "email": user.email,
    })


@app.get("/v1/generators/{generator_id}")
async def get_generator_details(generator_id: str):
    """
    Get detailed information about a generator, including all its levels.
    
    This endpoint is public (no authentication required) and returns:
    - Generator metadata (name, version, description, tags, etc.)
    - Rating statistics (rating, games_played, wins, losses, ties)
    - All levels with their tilemaps for preview rendering
    
    Used by:
    - Generator detail page (accessible from leaderboard)
    - Builder profile (viewing own generators)
    """
    from datetime import datetime, timezone
    
    conn = get_connection()
    
    # Get generator info with rating
    cursor = conn.execute(
        """
        SELECT 
            g.generator_id,
            g.name,
            g.version,
            g.description,
            g.tags_json,
            g.documentation_url,
            g.is_active,
            g.owner_user_id,
            g.created_at_utc,
            g.updated_at_utc,
            COALESCE(r.rating_value, 1000.0) as rating,
            COALESCE(r.games_played, 0) as games_played,
            COALESCE(r.wins, 0) as wins,
            COALESCE(r.losses, 0) as losses,
            COALESCE(r.ties, 0) as ties,
            COALESCE(r.skips, 0) as skips
        FROM generators g
        LEFT JOIN ratings r ON g.generator_id = r.generator_id
        WHERE g.generator_id = ?
        """,
        (generator_id,)
    )
    
    row = cursor.fetchone()
    
    if not row:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            f"Generator '{generator_id}' not found",
            retryable=False,
            status_code=404
        )
    
    # Parse tags
    import json
    tags = json.loads(row["tags_json"]) if row["tags_json"] else []
    
    # Get all levels for this generator
    cursor = conn.execute(
        """
        SELECT 
            level_id,
            content_format,
            width,
            height,
            tilemap_text,
            content_hash,
            created_at_utc
        FROM levels
        WHERE generator_id = ?
        ORDER BY level_id ASC
        """,
        (generator_id,)
    )
    
    levels = []
    for level_row in cursor.fetchall():
        levels.append({
            "level_id": level_row["level_id"],
            "format": {
                "type": level_row["content_format"],
                "width": level_row["width"],
                "height": level_row["height"],
            },
            "tilemap": level_row["tilemap_text"],
            "content_hash": level_row["content_hash"],
            "created_at_utc": level_row["created_at_utc"],
        })
    
    # Compute rank (optional, for display)
    cursor = conn.execute(
        """
        SELECT COUNT(*) + 1 as rank
        FROM ratings r
        JOIN generators g ON r.generator_id = g.generator_id
        WHERE r.rating_value > ? AND g.is_active = 1
        """,
        (row["rating"],)
    )
    rank_row = cursor.fetchone()
    rank = rank_row["rank"] if rank_row else None
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "generator": {
            "generator_id": row["generator_id"],
            "name": row["name"],
            "version": row["version"],
            "description": row["description"] or "",
            "tags": tags,
            "documentation_url": row["documentation_url"],
            "is_active": bool(row["is_active"]),
            "created_at_utc": row["created_at_utc"],
            "updated_at_utc": row["updated_at_utc"],
            "rank": rank,
            "rating": row["rating"],
            "games_played": row["games_played"],
            "wins": row["wins"],
            "losses": row["losses"],
            "ties": row["ties"],
            "skips": row["skips"],
            "level_count": len(levels),
        },
        "levels": levels,
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


@app.get("/debug/matchmaking")
async def debug_matchmaking():
    """
    Get matchmaking statistics for debugging.
    
    Returns information about:
    - Total generators and pairs
    - Coverage statistics (pairs with battles, pairs at target)
    - Average rating deviation
    - New generators needing more games
    
    Only available when ARENA_DEBUG=true.
    """
    if not config.debug:
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "Debug endpoints are disabled. Set ARENA_DEBUG=true to enable.",
            retryable=False,
            status_code=403
        )
    
    conn = get_connection()
    stats = get_matchmaking_stats(conn)
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "matchmaking_policy": config.matchmaking_policy,
        "stats": stats,
    })


@app.get("/debug/pair-stats")
async def debug_pair_stats(limit: int = 50):
    """
    Get generator pair battle statistics for confusion matrix.
    
    Returns battle counts and win rates between generator pairs.
    
    Only available when ARENA_DEBUG=true.
    """
    if not config.debug:
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "Debug endpoints are disabled. Set ARENA_DEBUG=true to enable.",
            retryable=False,
            status_code=403
        )
    
    conn = get_connection()
    cursor = conn.execute(
        """
        SELECT 
            gen1_id, gen2_id, battle_count, 
            gen1_wins, gen2_wins, ties, skips,
            last_battle_utc
        FROM generator_pair_stats
        ORDER BY battle_count DESC
        LIMIT ?
        """,
        (min(limit, 500),)
    )
    
    pairs = []
    for row in cursor.fetchall():
        pairs.append({
            "gen1_id": row["gen1_id"],
            "gen2_id": row["gen2_id"],
            "battle_count": row["battle_count"],
            "gen1_wins": row["gen1_wins"],
            "gen2_wins": row["gen2_wins"],
            "ties": row["ties"],
            "skips": row["skips"],
            "last_battle_utc": row["last_battle_utc"],
        })
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "pairs": pairs,
        "count": len(pairs),
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


# ============================================================================
# Authentication Endpoints (Stage 3)
# ============================================================================

@app.get("/v1/auth/me")
async def get_current_user_endpoint(request: Request):
    """
    Get the currently authenticated user.
    
    Returns user info if authenticated, 401 if not.
    """
    user = get_current_user(request)
    
    if not user:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            "Not authenticated",
            retryable=False,
            status_code=401
        )
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "display_name": user.display_name,
            "created_at_utc": user.created_at_utc,
            "last_login_utc": user.last_login_utc,
            "is_email_verified": user.is_email_verified
        }
    })


@app.post("/v1/auth/dev-login")
async def dev_login(request: Request, response: Response, body: DevLoginRequest):
    """
    Dev login endpoint for local testing.
    
    Only available when ARENA_DEV_AUTH=true.
    Creates or logs in a test user without OAuth.
    """
    if not config.dev_auth:
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "Dev auth is disabled. Set ARENA_DEV_AUTH=true to enable.",
            retryable=False,
            status_code=403
        )
    
    # Check if user exists
    user = get_user_by_email(body.email)
    
    if not user:
        # Create new user
        user = create_user(
            email=body.email,
            display_name=body.display_name,
            google_sub=None
        )
    else:
        # Update last login
        update_last_login(user.user_id)
    
    # Create session
    session_token = create_session(user.user_id)
    
    logger.info(f"Dev login: user_id={user.user_id} email={user.email}")
    
    json_response = JSONResponse({
        "protocol_version": "arena/v0",
        "message": "Login successful",
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "display_name": user.display_name,
            "created_at_utc": user.created_at_utc,
            "last_login_utc": user.last_login_utc,
            "is_email_verified": user.is_email_verified
        }
    })
    
    # Set cookie on the actual response object being returned
    set_session_cookie(json_response, session_token)
    return json_response


@app.post("/v1/auth/google")
async def google_login(request: Request, response: Response, body: GoogleLoginRequest):
    """
    Google OAuth login endpoint.
    
    Exchanges a Google ID token for a session.
    """
    if not config.google_client_id:
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "Google OAuth is not configured. Set ARENA_GOOGLE_CLIENT_ID.",
            retryable=False,
            status_code=503
        )
    
    # Verify Google token
    token_info = verify_google_token(body.credential)
    
    if not token_info:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            "Invalid or expired Google token",
            retryable=False,
            status_code=401
        )
    
    # Check if user exists by Google sub
    user = get_user_by_google_sub(token_info["google_sub"])
    
    if not user:
        # Check if user exists by email
        user = get_user_by_email(token_info["email"])
        
        if not user:
            # Create new user (auto-verified since using Google OAuth)
            user = create_user(
                email=token_info["email"],
                display_name=token_info["name"],
                google_sub=token_info["google_sub"]
            )
        else:
            # Link Google account to existing user
            # Mark as verified since they're logging in via Google
            update_last_login(user.user_id)
            mark_email_verified(user.user_id)
    else:
        update_last_login(user.user_id)
        # Ensure they're marked as verified (Google users are always verified)
        if not user.is_email_verified:
            mark_email_verified(user.user_id)
    
    # Create session
    session_token = create_session(user.user_id)
    
    logger.info(f"Google login: user_id={user.user_id} email={user.email}")
    
    # Google OAuth users are always verified
    json_response = JSONResponse({
        "protocol_version": "arena/v0",
        "message": "Login successful",
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "display_name": user.display_name,
            "created_at_utc": user.created_at_utc,
            "last_login_utc": user.last_login_utc,
            "is_email_verified": True  # Google OAuth users are always verified
        }
    })
    
    # Set cookie on the actual response object being returned
    set_session_cookie(json_response, session_token)
    return json_response


@app.post("/v1/auth/register")
async def email_register(request: Request, response: Response, body: EmailRegisterRequest):
    """
    Register a new user with email and password.
    
    Creates a new account and logs the user in.
    """
    # Validate password
    is_valid, error_msg = validate_password(body.password)
    if not is_valid:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            error_msg,
            retryable=False,
            status_code=400
        )
    
    # Validate email format (basic check)
    if not body.email or '@' not in body.email or len(body.email) < 5:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            "Invalid email address",
            retryable=False,
            status_code=400
        )
    
    # Check if email already exists
    existing_user = get_user_by_email(body.email.lower())
    if existing_user:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            "An account with this email already exists",
            retryable=False,
            status_code=409
        )
    
    # Create user with hashed password
    password_hash = hash_password(body.password)
    user = create_user(
        email=body.email.lower(),
        display_name=body.display_name or body.email.split('@')[0],
        password_hash=password_hash
    )
    
    # Send verification email
    verification_token = create_email_verification_token(user.user_id)
    email_sent = send_verification_email(body.email.lower(), verification_token)
    
    if not email_sent:
        logger.warning(f"Failed to send verification email for user {user.user_id}")
    
    # Create session
    session_token = create_session(user.user_id)
    
    logger.info(f"Email registration: user_id={user.user_id} email={user.email}")
    
    json_response = JSONResponse({
        "protocol_version": "arena/v0",
        "message": "Registration successful. Please check your email to verify your account.",
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "display_name": user.display_name,
            "created_at_utc": user.created_at_utc,
            "last_login_utc": user.last_login_utc,
            "is_email_verified": user.is_email_verified,
            "is_email_verified": user.is_email_verified
        }
    })
    
    set_session_cookie(json_response, session_token)
    return json_response


@app.post("/v1/auth/login")
async def email_login(request: Request, response: Response, body: EmailLoginRequest):
    """
    Login with email and password.
    
    Authenticates the user and creates a new session.
    """
    # Get user by email
    user = get_user_by_email(body.email.lower())
    
    if not user:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            "Invalid email or password",
            retryable=False,
            status_code=401
        )
    
    # Get password hash
    password_hash = get_password_hash_by_email(body.email.lower())
    
    if not password_hash:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            "This account uses Google Sign-In. Please login with Google.",
            retryable=False,
            status_code=401
        )
    
    # Verify password
    if not verify_password(body.password, password_hash):
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            "Invalid email or password",
            retryable=False,
            status_code=401
        )
    
    # Update last login
    update_last_login(user.user_id)
    
    # Create session
    session_token = create_session(user.user_id)
    
    logger.info(f"Email login: user_id={user.user_id} email={user.email}")
    
    json_response = JSONResponse({
        "protocol_version": "arena/v0",
        "message": "Login successful",
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "display_name": user.display_name,
            "created_at_utc": user.created_at_utc,
            "last_login_utc": user.last_login_utc,
            "is_email_verified": user.is_email_verified
        }
    })
    
    set_session_cookie(json_response, session_token)
    return json_response


@app.post("/v1/auth/logout")
async def logout(request: Request, response: Response):
    """
    Logout the current user.
    
    Clears the session cookie and deletes the session.
    """
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    
    if session_token:
        delete_session(session_token)
    
    json_response = JSONResponse({
        "protocol_version": "arena/v0",
        "message": "Logged out successfully"
    })
    
    # Clear cookie on the actual response object being returned
    clear_session_cookie(json_response)
    return json_response


@app.post("/v1/auth/verify-email")
async def verify_email(token: str):
    """
    Verify a user's email address using the token from the verification email.
    
    Query params:
        token: The verification token from the email link
    """
    user_id = verify_email_token(token)
    
    if not user_id:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            "Invalid or expired verification token",
            retryable=False,
            status_code=400
        )
    
    logger.info(f"Email verified for user {user_id}")
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "message": "Email verified successfully"
    })


@app.post("/v1/auth/resend-verification")
async def resend_verification(request: Request):
    """
    Resend verification email to the current user.
    
    Requires authentication.
    """
    user = require_auth(request)
    
    if user.is_email_verified:
        return JSONResponse({
            "protocol_version": "arena/v0",
            "message": "Email already verified"
        })
    
    # Create new verification token
    verification_token = create_email_verification_token(user.user_id)
    email_sent = send_verification_email(user.email, verification_token)
    
    if not email_sent:
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "Failed to send verification email. Please try again later.",
            retryable=True,
            status_code=500
        )
    
    logger.info(f"Verification email resent for user {user.user_id}")
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "message": "Verification email sent"
    })


@app.post("/v1/auth/forgot-password")
async def forgot_password(body: ForgotPasswordRequest):
    """
    Request a password reset email.
    
    Sends a password reset link to the user's email if the account exists.
    Always returns success to prevent email enumeration.
    """
    email = body.email.lower()
    user = get_user_by_email(email)
    
    if user:
        # Check if user has a password (not Google-only)
        if get_password_hash_by_email(email):
            # Create reset token and send email
            reset_token = create_password_reset_token(user.user_id)
            send_password_reset_email(email, reset_token)
            logger.info(f"Password reset requested for: {email}")
        else:
            # Google-only account, don't send reset email
            logger.info(f"Password reset requested for Google-only account: {email}")
    else:
        # Don't reveal whether the email exists
        logger.info(f"Password reset requested for unknown email: {email}")
    
    # Always return success to prevent email enumeration
    return JSONResponse({
        "protocol_version": "arena/v0",
        "message": "If an account exists with this email, you will receive a password reset link."
    })


@app.post("/v1/auth/reset-password")
async def reset_password(body: ResetPasswordRequest):
    """
    Reset password using a reset token.
    
    Sets a new password for the user if the token is valid.
    """
    # Validate new password
    is_valid, error_msg = validate_password(body.new_password)
    if not is_valid:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            error_msg,
            retryable=False,
            status_code=400
        )
    
    # Verify token
    user_id = verify_password_reset_token(body.token)
    if not user_id:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            "Invalid or expired reset link. Please request a new one.",
            retryable=False,
            status_code=400
        )
    
    # Update password
    new_hash = hash_password(body.new_password)
    if not update_user_password(user_id, new_hash):
        raise_api_error(
            ErrorCode.INTERNAL_ERROR,
            "Failed to update password. Please try again.",
            retryable=True,
            status_code=500
        )
    
    # Mark token as used
    use_password_reset_token(body.token)
    
    logger.info(f"Password reset successful for user {user_id}")
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "message": "Password updated successfully. You can now sign in with your new password."
    })


# ============================================================================
# Builder Profile Endpoints (Stage 3)
# ============================================================================

def require_auth(request: Request) -> User:
    """Helper to require authentication for an endpoint."""
    user = get_current_user(request)
    if not user:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            "Authentication required",
            retryable=False,
            status_code=401
        )
    
    # Check email verification (but allow unverified users to access certain endpoints)
    # Google users are auto-verified, so this mainly applies to email/password users
    if not user.is_email_verified:
        # For now, we allow unverified users to access the builder profile
        # but they will see a verification notice
        # In the future, you might want to restrict certain actions
        logger.debug(f"Unverified user accessing endpoint: {user.user_id}")
    
    return user


@app.get("/v1/builders/me/generators")
async def list_my_generators(request: Request):
    """
    List generators owned by the current user.
    
    Returns up to MAX_GENERATORS_PER_USER generators with their metadata and stats.
    """
    user = require_auth(request)
    
    generators = get_user_generators(user.user_id)
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "user_id": user.user_id,
        "max_generators": MAX_GENERATORS_PER_USER,
        "min_levels_required": MIN_LEVELS_PER_GENERATOR,
        "max_levels_allowed": MAX_LEVELS_PER_GENERATOR,
        "generators": [
            {
                "generator_id": g.generator_id,
                "name": g.name,
                "version": g.version,
                "description": g.description,
                "tags": g.tags,
                "documentation_url": g.documentation_url,
                "is_active": g.is_active,
                "level_count": g.level_count,
                "rating": g.rating,
                "games_played": g.games_played,
                "wins": g.wins,
                "losses": g.losses,
                "ties": g.ties,
                "created_at_utc": g.created_at_utc,
                "updated_at_utc": g.updated_at_utc
            }
            for g in generators
        ]
    })


@app.post("/v1/builders/generators")
@limiter.limit("5/hour")
async def create_generator_endpoint(
    request: Request,
    generator_id: str = None,
    name: str = None,
    version: str = "1.0.0",
    description: str = "",
    tags: str = "",
    documentation_url: str = None,
    levels_zip: UploadFile = None
):
    """
    Create a new generator with levels.
    
    Accepts multipart form data with generator metadata and a ZIP file of levels.
    """
    from fastapi import Form, File
    user = require_auth(request)
    
    # For multipart forms, we need to handle this differently
    # This is a simplified version - real implementation would use Form() and File()
    raise_api_error(
        ErrorCode.INTERNAL_ERROR,
        "Use the multipart endpoint at /v1/builders/generators/upload",
        retryable=False,
        status_code=400
    )


@app.post("/v1/builders/generators/upload")
@limiter.limit("5/hour")
async def upload_generator(
    request: Request,
    generator_id: str = Form(...),
    name: str = Form(...),
    version: str = Form(default="1.0.0"),
    description: str = Form(default=""),
    tags: str = Form(default=""),
    documentation_url: str = Form(default=None),
    levels_zip: UploadFile = File(...)
):
    """
    Create a new generator with levels (multipart upload).
    
    Form fields:
    - generator_id: Unique ID for the generator (3-32 chars, alphanumeric/hyphens)
    - name: Display name (3-100 chars)
    - version: Version string (default: "1.0.0")
    - description: Description (max 1000 chars)
    - tags: Comma-separated tags (max 10)
    - documentation_url: Optional URL to documentation
    - levels_zip: ZIP file containing at least 50 level .txt files
    """
    user = require_auth(request)
    
    # Parse tags
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    
    metadata = GeneratorMetadata(
        generator_id=generator_id,
        name=name,
        version=version,
        description=description,
        tags=tag_list[:10],  # Limit to 10 tags
        documentation_url=documentation_url if documentation_url else None
    )
    
    try:
        generator = await create_generator(user.user_id, metadata, levels_zip)
        
        return JSONResponse({
            "protocol_version": "arena/v0",
            "message": f"Generator '{generator.generator_id}' created successfully with {generator.level_count} levels",
            "generator": {
                "generator_id": generator.generator_id,
                "name": generator.name,
                "version": generator.version,
                "description": generator.description,
                "tags": generator.tags,
                "documentation_url": generator.documentation_url,
                "is_active": generator.is_active,
                "level_count": generator.level_count,
                "rating": generator.rating,
                "games_played": generator.games_played
            }
        }, status_code=201)
    
    except BuilderError as e:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            e.message,
            retryable=False,
            status_code=e.status_code,
            details={"code": e.code}
        )


@app.put("/v1/builders/generators/{generator_id}/upload")
@limiter.limit("5/hour")
async def update_generator_endpoint(
    request: Request,
    generator_id: str,
    name: str = Form(...),
    version: str = Form(...),
    description: str = Form(default=""),
    tags: str = Form(default=""),
    documentation_url: str = Form(default=None),
    levels_zip: UploadFile = File(...)
):
    """
    Update a generator with new levels (new version).
    
    Keeps rating and games_played, replaces all levels.
    """
    user = require_auth(request)
    
    # Parse tags
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    
    metadata = GeneratorMetadata(
        generator_id=generator_id,
        name=name,
        version=version,
        description=description,
        tags=tag_list[:10],
        documentation_url=documentation_url if documentation_url else None
    )
    
    try:
        generator = await update_generator(user.user_id, generator_id, metadata, levels_zip)
        
        return JSONResponse({
            "protocol_version": "arena/v0",
            "message": f"Generator '{generator_id}' updated to version {version} with {generator.level_count} levels",
            "generator": {
                "generator_id": generator.generator_id,
                "name": generator.name,
                "version": generator.version,
                "description": generator.description,
                "tags": generator.tags,
                "documentation_url": generator.documentation_url,
                "is_active": generator.is_active,
                "level_count": generator.level_count,
                "rating": generator.rating,
                "games_played": generator.games_played
            }
        })
    
    except BuilderError as e:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            e.message,
            retryable=False,
            status_code=e.status_code,
            details={"code": e.code}
        )


@app.delete("/v1/builders/generators/{generator_id}")
async def delete_generator_endpoint(request: Request, generator_id: str):
    """
    Delete a generator and all its levels.
    
    This action cannot be undone. Rating history is preserved in rating_events.
    """
    user = require_auth(request)
    
    try:
        delete_generator(user.user_id, generator_id)
        
        return JSONResponse({
            "protocol_version": "arena/v0",
            "message": f"Generator '{generator_id}' deleted successfully"
        })
    
    except BuilderError as e:
        raise_api_error(
            ErrorCode.INVALID_PAYLOAD,
            e.message,
            retryable=False,
            status_code=e.status_code,
            details={"code": e.code}
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
