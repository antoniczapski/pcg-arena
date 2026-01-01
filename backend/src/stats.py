"""
Stage 5: Statistics computation module for PCG Arena

Handles:
- Per-level statistics updates
- Player profile management
- Trajectory storage
- Aggregate statistics computation
"""

import json
import sqlite3
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Optional

from db import get_connection


def ensure_level_stats_exist(cursor: sqlite3.Cursor, level_id: str, generator_id: str, now_utc: str) -> None:
    """Ensure level_stats row exists for a level."""
    cursor.execute(
        """
        INSERT OR IGNORE INTO level_stats (level_id, generator_id, updated_at_utc)
        VALUES (?, ?, ?)
        """,
        (level_id, generator_id, now_utc)
    )


def update_level_stats_for_vote(
    cursor: sqlite3.Cursor,
    left_level_id: str,
    right_level_id: str,
    left_generator_id: str,
    right_generator_id: str,
    result: str,
    left_telemetry: dict,
    right_telemetry: dict,
    left_tags: list,
    right_tags: list,
    now_utc: str
) -> None:
    """
    Update level_stats for both levels after a vote.
    
    Args:
        cursor: Database cursor
        left_level_id: Left level ID
        right_level_id: Right level ID  
        left_generator_id: Left generator ID
        right_generator_id: Right generator ID
        result: Vote result (LEFT, RIGHT, TIE, SKIP)
        left_telemetry: Telemetry for left level
        right_telemetry: Telemetry for right level
        left_tags: Tags for left level
        right_tags: Tags for right level
        now_utc: Current UTC timestamp
    """
    # Ensure stats rows exist
    ensure_level_stats_exist(cursor, left_level_id, left_generator_id, now_utc)
    ensure_level_stats_exist(cursor, right_level_id, right_generator_id, now_utc)
    
    # Determine outcomes for each level
    left_won = result == "LEFT"
    right_won = result == "RIGHT"
    is_tie = result == "TIE"
    is_skip = result == "SKIP"
    
    # Update left level stats
    _update_single_level_stats(
        cursor, left_level_id, 
        won=left_won, lost=right_won, tied=is_tie, skipped=is_skip,
        telemetry=left_telemetry, tags=left_tags, now_utc=now_utc
    )
    
    # Update right level stats
    _update_single_level_stats(
        cursor, right_level_id,
        won=right_won, lost=left_won, tied=is_tie, skipped=is_skip,
        telemetry=right_telemetry, tags=right_tags, now_utc=now_utc
    )


def _update_single_level_stats(
    cursor: sqlite3.Cursor,
    level_id: str,
    won: bool,
    lost: bool,
    tied: bool,
    skipped: bool,
    telemetry: dict,
    tags: list,
    now_utc: str
) -> None:
    """Update stats for a single level."""
    # Extract telemetry values
    completed = telemetry.get("completed", False)
    deaths = telemetry.get("deaths", 0)
    duration = telemetry.get("duration_seconds", 0)
    play_skipped = telemetry.get("skipped", False)  # Player skipped playing this level
    
    # Build tag updates
    tag_updates = []
    tag_values = []
    for tag in tags:
        column = f"tag_{tag.replace('-', '_')}"
        # Only update if column exists (ignore invalid tags)
        if tag in ["fun", "boring", "too_hard", "too_easy", "creative", "good_flow", "unfair", "confusing", "not_mario_like"]:
            tag_updates.append(f"{column} = {column} + 1")
    
    # Build SQL update (times_play_skipped may not exist in older DBs, handle gracefully)
    try:
        cursor.execute(
            f"""
            UPDATE level_stats SET
                times_shown = times_shown + 1,
                times_won = times_won + ?,
                times_lost = times_lost + ?,
                times_tied = times_tied + ?,
                times_skipped = times_skipped + ?,
                times_play_skipped = times_play_skipped + ?,
                times_completed = times_completed + ?,
                total_deaths = total_deaths + ?,
                total_play_time_seconds = total_play_time_seconds + ?,
                {', '.join(tag_updates) + ',' if tag_updates else ''}
                updated_at_utc = ?
            WHERE level_id = ?
            """,
            (
                1 if won else 0,
                1 if lost else 0,
                1 if tied else 0,
                1 if skipped else 0,
                1 if play_skipped else 0,
                1 if completed else 0,
                deaths,
                duration,
                now_utc,
                level_id
            )
        )
    except sqlite3.OperationalError:
        # Fallback for DBs without times_play_skipped column
        cursor.execute(
            f"""
            UPDATE level_stats SET
                times_shown = times_shown + 1,
                times_won = times_won + ?,
                times_lost = times_lost + ?,
                times_tied = times_tied + ?,
                times_skipped = times_skipped + ?,
                times_completed = times_completed + ?,
                total_deaths = total_deaths + ?,
                total_play_time_seconds = total_play_time_seconds + ?,
                {', '.join(tag_updates) + ',' if tag_updates else ''}
                updated_at_utc = ?
            WHERE level_id = ?
            """,
            (
                1 if won else 0,
                1 if lost else 0,
                1 if tied else 0,
                1 if skipped else 0,
                1 if completed else 0,
                deaths,
                duration,
                now_utc,
                level_id
            )
        )
    
    # Recompute derived metrics
    cursor.execute(
        """
        UPDATE level_stats SET
            win_rate = CASE 
                WHEN times_won + times_lost > 0 
                THEN CAST(times_won AS REAL) / (times_won + times_lost)
                ELSE NULL 
            END,
            completion_rate = CASE 
                WHEN times_shown > 0 
                THEN CAST(times_completed AS REAL) / times_shown
                ELSE NULL 
            END,
            avg_deaths = CASE 
                WHEN times_shown > 0 
                THEN CAST(total_deaths AS REAL) / times_shown
                ELSE NULL 
            END,
            avg_duration_seconds = CASE 
                WHEN times_shown > 0 
                THEN total_play_time_seconds / times_shown
                ELSE NULL 
            END,
            difficulty_score = CASE 
                WHEN times_shown > 0 
                THEN 1.0 - (CAST(times_completed AS REAL) / times_shown)
                ELSE NULL 
            END
        WHERE level_id = ?
        """,
        (level_id,)
    )


def ensure_player_profile_exists(
    cursor: sqlite3.Cursor,
    player_id: str,
    now_utc: str
) -> None:
    """Ensure player_profiles row exists."""
    if not player_id:
        return
        
    cursor.execute(
        """
        INSERT OR IGNORE INTO player_profiles (
            player_id, first_seen_utc, last_seen_utc
        ) VALUES (?, ?, ?)
        """,
        (player_id, now_utc, now_utc)
    )


def update_player_profile_for_vote(
    cursor: sqlite3.Cursor,
    player_id: str,
    now_utc: str
) -> None:
    """Update player profile after a vote."""
    if not player_id:
        return
    
    ensure_player_profile_exists(cursor, player_id, now_utc)
    
    cursor.execute(
        """
        UPDATE player_profiles SET
            last_seen_utc = ?,
            total_votes = total_votes + 1
        WHERE player_id = ?
        """,
        (now_utc, player_id)
    )


def update_player_session(
    cursor: sqlite3.Cursor,
    session_id: str,
    player_id: str,
    now_utc: str,
    user_agent: Optional[str] = None,
    ip_hash: Optional[str] = None
) -> None:
    """Update or create player session record."""
    if not player_id:
        return
    
    # Try to update existing session
    cursor.execute(
        """
        UPDATE player_sessions SET
            last_activity_utc = ?,
            battles_completed = battles_completed + 1
        WHERE session_id = ?
        """,
        (now_utc, session_id)
    )
    
    if cursor.rowcount == 0:
        # Create new session
        cursor.execute(
            """
            INSERT INTO player_sessions (
                session_id, player_id, started_at_utc, last_activity_utc,
                battles_completed, user_agent, ip_hash
            ) VALUES (?, ?, ?, ?, 1, ?, ?)
            """,
            (session_id, player_id, now_utc, now_utc, user_agent, ip_hash)
        )


def store_trajectory(
    cursor: sqlite3.Cursor,
    vote_id: str,
    level_id: str,
    session_id: str,
    player_id: Optional[str],
    side: str,
    telemetry: dict,
    now_utc: str
) -> None:
    """Store trajectory data from telemetry."""
    trajectory = telemetry.get("trajectory", [])
    death_locations = telemetry.get("death_locations", [])
    events = telemetry.get("events", [])
    
    # Skip if no trajectory data
    if not trajectory:
        return
    
    trajectory_id = f"traj_{uuid.uuid4()}"
    
    # Compute summary stats
    duration_ticks = trajectory[-1].get("tick", 0) if trajectory else 0
    max_x = max(p.get("x", 0) for p in trajectory) if trajectory else 0
    death_count = len(death_locations)
    completed = 1 if telemetry.get("completed", False) else 0
    
    cursor.execute(
        """
        INSERT INTO play_trajectories (
            trajectory_id, vote_id, level_id, session_id, player_id, side,
            trajectory_json, death_locations_json, events_json,
            duration_ticks, max_x_reached, death_count, completed,
            created_at_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            trajectory_id,
            vote_id,
            level_id,
            session_id,
            player_id,
            side,
            json.dumps(trajectory),
            json.dumps(death_locations) if death_locations else None,
            json.dumps(events) if events else None,
            duration_ticks,
            max_x,
            death_count,
            completed,
            now_utc
        )
    )


def get_platform_stats() -> dict:
    """Get platform-wide aggregate statistics."""
    conn = get_connection()
    
    # Total counts
    cursor = conn.execute("SELECT COUNT(*) FROM votes")
    total_votes = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(*) FROM battles WHERE status = 'COMPLETED'")
    total_battles = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(DISTINCT session_id) FROM votes")
    unique_sessions = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(DISTINCT player_id) FROM player_profiles")
    unique_players = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(*) FROM generators WHERE is_active = 1")
    active_generators = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(*) FROM levels")
    total_levels = cursor.fetchone()[0]
    
    # Vote distribution
    cursor = conn.execute(
        """
        SELECT 
            result,
            COUNT(*) as count,
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM votes), 1) as percent
        FROM votes
        GROUP BY result
        """
    )
    vote_dist = {row["result"]: {"count": row["count"], "percent": row["percent"]} for row in cursor.fetchall()}
    
    # Engagement metrics from level_stats
    cursor = conn.execute(
        """
        SELECT 
            AVG(completion_rate) as avg_completion,
            AVG(avg_deaths) as avg_deaths,
            AVG(avg_duration_seconds) as avg_duration
        FROM level_stats
        WHERE times_shown > 0
        """
    )
    row = cursor.fetchone()
    
    return {
        "totals": {
            "battles_completed": total_battles,
            "votes_cast": total_votes,
            "unique_sessions": unique_sessions,
            "unique_players": unique_players,
            "active_generators": active_generators,
            "total_levels": total_levels
        },
        "vote_distribution": {
            "left_percent": vote_dist.get("LEFT", {}).get("percent", 0),
            "right_percent": vote_dist.get("RIGHT", {}).get("percent", 0),
            "tie_percent": vote_dist.get("TIE", {}).get("percent", 0),
            "skip_percent": vote_dist.get("SKIP", {}).get("percent", 0)
        },
        "engagement": {
            "completion_rate_percent": round((row["avg_completion"] or 0) * 100, 1),
            "avg_deaths_per_level": round(row["avg_deaths"] or 0, 1),
            "avg_duration_seconds": round(row["avg_duration"] or 0, 1)
        }
    }


def get_level_stats(level_id: str) -> Optional[dict]:
    """Get statistics for a specific level."""
    conn = get_connection()
    
    cursor = conn.execute(
        """
        SELECT * FROM level_stats WHERE level_id = ?
        """,
        (level_id,)
    )
    row = cursor.fetchone()
    
    if not row:
        return None
    
    return {
        "level_id": row["level_id"],
        "generator_id": row["generator_id"],
        "performance": {
            "times_shown": row["times_shown"],
            "win_rate": row["win_rate"],
            "completion_rate": row["completion_rate"],
            "avg_deaths": row["avg_deaths"],
            "avg_duration_seconds": row["avg_duration_seconds"]
        },
        "outcomes": {
            "wins": row["times_won"],
            "losses": row["times_lost"],
            "ties": row["times_tied"],
            "skips": row["times_skipped"],
            "play_skipped": row["times_play_skipped"] if "times_play_skipped" in row.keys() else 0
        },
        "tags": {
            "fun": row["tag_fun"],
            "boring": row["tag_boring"],
            "too_hard": row["tag_too_hard"],
            "too_easy": row["tag_too_easy"],
            "creative": row["tag_creative"],
            "good_flow": row["tag_good_flow"],
            "unfair": row["tag_unfair"],
            "confusing": row["tag_confusing"],
            "not_mario_like": row["tag_not_mario_like"]
        },
        "difficulty": {
            "score": row["difficulty_score"],
            "classification": _classify_difficulty(row["difficulty_score"])
        }
    }


def _classify_difficulty(score: Optional[float]) -> str:
    """Classify difficulty score into category."""
    if score is None:
        return "unknown"
    if score < 0.2:
        return "very_easy"
    if score < 0.4:
        return "easy"
    if score < 0.6:
        return "medium"
    if score < 0.8:
        return "hard"
    return "very_hard"


def get_level_heatmap(level_id: str) -> dict:
    """Get aggregate death and position data for heatmap visualization."""
    conn = get_connection()
    
    # Get all death locations for this level
    cursor = conn.execute(
        """
        SELECT death_locations_json FROM play_trajectories
        WHERE level_id = ? AND death_locations_json IS NOT NULL
        """,
        (level_id,)
    )
    
    death_counts = {}
    total_deaths = 0
    
    for row in cursor.fetchall():
        try:
            deaths = json.loads(row["death_locations_json"])
            for death in deaths:
                tile_x = int(death.get("x", 0) / 16)
                death_counts[tile_x] = death_counts.get(tile_x, 0) + 1
                total_deaths += 1
        except (json.JSONDecodeError, TypeError):
            continue
    
    # Get sample count
    cursor = conn.execute(
        """
        SELECT COUNT(*) FROM play_trajectories WHERE level_id = ?
        """,
        (level_id,)
    )
    sample_count = cursor.fetchone()[0]
    
    return {
        "level_id": level_id,
        "sample_count": sample_count,
        "death_heatmap": {
            "tile_size": 16,
            "data": [{"tile_x": x, "count": c} for x, c in sorted(death_counts.items())],
            "max_count": max(death_counts.values()) if death_counts else 0,
            "total_deaths": total_deaths
        }
    }


def init_level_stats_for_all_levels():
    """Initialize level_stats rows for all existing levels."""
    conn = get_connection()
    now_utc = datetime.now(timezone.utc).isoformat()
    
    cursor = conn.execute(
        """
        INSERT OR IGNORE INTO level_stats (level_id, generator_id, updated_at_utc)
        SELECT level_id, generator_id, ?
        FROM levels
        """,
        (now_utc,)
    )
    
    conn.commit()
    return cursor.rowcount

