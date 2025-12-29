"""
PCG Arena - AGIS Matchmaking Algorithm
Protocol: arena/v0

Implements Adaptive Glicko-Informed Selection (AGIS) for battle matchmaking.

Goals:
1. Fast convergence: Select generators with high uncertainty (RD) more often
2. Similar ratings: Prefer matchups between generators of similar skill
3. Coverage: Ensure all generator pairs get enough battles for confusion matrix
4. Quality bias: Slightly prefer better generators after they've converged

Algorithm:
1. Compute selection weights for each generator based on uncertainty and games
2. Sample first generator using weighted selection
3. Compute pair weights for second generator based on rating similarity and coverage
4. Sample second generator using pair weights
5. Select random levels from each generator
"""

import math
import random
import logging
import sqlite3
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

from glicko2 import information_gain, match_quality, DEFAULT_RD, MIN_RD, MAX_RD
from config import load_config

logger = logging.getLogger(__name__)

# Load configurable AGIS parameters
_config = load_config()
MIN_GAMES_FOR_SIGNIFICANCE = _config.agis_min_games_for_significance
RATING_SIMILARITY_SIGMA = _config.agis_rating_similarity_sigma
TARGET_BATTLES_PER_PAIR = _config.agis_target_battles_per_pair
QUALITY_BIAS_STRENGTH = _config.agis_quality_bias_strength

# Weights for combining pair selection factors
ALPHA = 0.5  # Rating similarity weight
BETA = 0.3   # Uncertainty weight
GAMMA = 0.2  # Coverage weight


@dataclass
class GeneratorStats:
    """Generator statistics for matchmaking."""
    generator_id: str
    rating: float
    rd: float  # Rating deviation
    volatility: float
    games_played: int
    is_active: bool


@dataclass  
class PairStats:
    """Statistics for a generator pair."""
    gen1_id: str
    gen2_id: str
    battle_count: int
    gen1_wins: int
    gen2_wins: int
    ties: int


def get_active_generators_with_stats(conn: sqlite3.Connection) -> List[GeneratorStats]:
    """
    Get all active generators with their rating statistics.
    
    Only includes generators that have at least one level.
    """
    cursor = conn.execute(
        """
        SELECT 
            g.generator_id,
            COALESCE(r.rating_value, 1000.0) as rating,
            COALESCE(r.rd, 350.0) as rd,
            COALESCE(r.volatility, 0.06) as volatility,
            COALESCE(r.games_played, 0) as games_played,
            g.is_active
        FROM generators g
        LEFT JOIN ratings r ON g.generator_id = r.generator_id
        WHERE g.is_active = 1
        AND EXISTS (SELECT 1 FROM levels l WHERE l.generator_id = g.generator_id)
        """
    )
    
    generators = []
    for row in cursor.fetchall():
        generators.append(GeneratorStats(
            generator_id=row["generator_id"],
            rating=row["rating"],
            rd=row["rd"],
            volatility=row["volatility"],
            games_played=row["games_played"],
            is_active=bool(row["is_active"])
        ))
    
    return generators


def get_pair_counts(conn: sqlite3.Connection) -> Dict[Tuple[str, str], int]:
    """
    Get battle counts for all generator pairs.
    
    Returns dict with (gen1_id, gen2_id) -> battle_count
    where gen1_id < gen2_id lexicographically.
    """
    cursor = conn.execute(
        "SELECT gen1_id, gen2_id, battle_count FROM generator_pair_stats"
    )
    
    pair_counts = {}
    for row in cursor.fetchall():
        pair_key = (row["gen1_id"], row["gen2_id"])
        pair_counts[pair_key] = row["battle_count"]
    
    return pair_counts


def normalize_pair_key(id1: str, id2: str) -> Tuple[str, str]:
    """Ensure pair key is in canonical order (gen1 < gen2)."""
    if id1 < id2:
        return (id1, id2)
    return (id2, id1)


def compute_generator_weight(gen: GeneratorStats, n_generators: int) -> float:
    """
    Compute selection weight for a generator as first pick.
    
    High weight = more likely to be selected.
    
    Factors:
    - High RD (uncertain) → higher weight
    - Few games played → higher weight (boost for new generators)
    - After convergence, slight quality bias toward better ratings
    """
    # Base weight from uncertainty (RD)
    # RD ranges from ~30 (very certain) to 350 (new/uncertain)
    rd_normalized = (gen.rd - MIN_RD) / (MAX_RD - MIN_RD)
    uncertainty_weight = (1.0 + rd_normalized) ** 2  # Quadratic boost for uncertain
    
    # Games played factor
    games = gen.games_played
    
    if games < MIN_GAMES_FOR_SIGNIFICANCE:
        # Strong boost for new generators (want to reach significance quickly)
        convergence_ratio = games / MIN_GAMES_FOR_SIGNIFICANCE
        games_weight = 3.0 * (1.0 - convergence_ratio) + 1.0  # 4x to 1x
    else:
        # After significance, mild quality bias
        # Normalize rating to [0.8, 1.2] range (assuming 600-1400 typical range)
        quality_factor = 0.8 + QUALITY_BIAS_STRENGTH * max(0, min(1, (gen.rating - 600) / 800))
        games_weight = quality_factor
    
    total_weight = uncertainty_weight * games_weight
    
    # Ensure positive weight
    return max(0.01, total_weight)


def compute_pair_weight(
    gen1: GeneratorStats,
    gen2: GeneratorStats,
    pair_counts: Dict[Tuple[str, str], int]
) -> float:
    """
    Compute weight for selecting gen2 given gen1 is already selected.
    
    Factors:
    - Rating similarity: Prefer similar ratings (informative matches)
    - Uncertainty: Prefer opponents with high RD
    - Coverage: Boost under-represented pairs
    """
    # Rating similarity (Gaussian kernel)
    rating_diff = abs(gen1.rating - gen2.rating)
    similarity_weight = math.exp(-(rating_diff ** 2) / (2 * RATING_SIMILARITY_SIGMA ** 2))
    
    # Uncertainty of second generator
    rd_normalized = (gen2.rd - MIN_RD) / (MAX_RD - MIN_RD)
    uncertainty_weight = 1.0 + rd_normalized
    
    # Coverage bonus
    pair_key = normalize_pair_key(gen1.generator_id, gen2.generator_id)
    count = pair_counts.get(pair_key, 0)
    
    if count < TARGET_BATTLES_PER_PAIR:
        # Exponential decay bonus as we approach target
        coverage_bonus = 2.0 * math.exp(-count / 3.0)
    else:
        # Minimal bonus after target reached
        coverage_bonus = 0.1
    
    # Information gain from match
    info_gain = information_gain(gen1.rd, gen2.rd)
    
    # Match quality (prefer balanced matches)
    quality = match_quality(gen1.rating, gen1.rd, gen2.rating, gen2.rd)
    
    # Combine factors
    base_weight = (
        ALPHA * similarity_weight +
        BETA * uncertainty_weight +
        GAMMA * (info_gain + quality)
    )
    
    # Add coverage bonus
    total_weight = base_weight + coverage_bonus
    
    return max(0.01, total_weight)


def select_generators_agis(conn: sqlite3.Connection) -> Tuple[str, str]:
    """
    Select two generators for a battle using AGIS algorithm.
    
    Args:
        conn: Database connection
    
    Returns:
        Tuple of (left_generator_id, right_generator_id)
    
    Raises:
        ValueError: If fewer than 2 active generators with levels
    """
    # Get all active generators with stats
    generators = get_active_generators_with_stats(conn)
    
    if len(generators) < 2:
        raise ValueError(f"Need at least 2 active generators, found {len(generators)}")
    
    n = len(generators)
    
    # Get pair battle counts
    pair_counts = get_pair_counts(conn)
    
    # Step 1: Compute selection weights for each generator
    weights = [compute_generator_weight(g, n) for g in generators]
    
    # Step 2: Sample first generator
    total_weight = sum(weights)
    probs = [w / total_weight for w in weights]
    gen1 = random.choices(generators, weights=probs, k=1)[0]
    
    # Step 3: Compute pair weights for second generator
    pair_weights = []
    for gen in generators:
        if gen.generator_id == gen1.generator_id:
            pair_weights.append(0)  # Can't pick same generator
        else:
            pw = compute_pair_weight(gen1, gen, pair_counts)
            pair_weights.append(pw)
    
    # Step 4: Sample second generator
    total_pw = sum(pair_weights)
    if total_pw == 0:
        # Fallback: uniform selection among non-gen1
        eligible = [g for g in generators if g.generator_id != gen1.generator_id]
        gen2 = random.choice(eligible)
    else:
        pair_probs = [pw / total_pw for pw in pair_weights]
        gen2 = random.choices(generators, weights=pair_probs, k=1)[0]
    
    logger.debug(
        f"AGIS selected: gen1={gen1.generator_id} (rating={gen1.rating:.0f}, rd={gen1.rd:.0f}, games={gen1.games_played}) "
        f"gen2={gen2.generator_id} (rating={gen2.rating:.0f}, rd={gen2.rd:.0f}, games={gen2.games_played})"
    )
    
    return gen1.generator_id, gen2.generator_id


def select_random_level(conn: sqlite3.Connection, generator_id: str) -> Optional[str]:
    """
    Select a random level from a generator.
    
    Uses uniform random selection (simple but effective for small pools).
    
    Args:
        conn: Database connection
        generator_id: Generator to select from
    
    Returns:
        level_id or None if no levels
    """
    cursor = conn.execute(
        """
        SELECT level_id FROM levels 
        WHERE generator_id = ? 
        ORDER BY RANDOM() 
        LIMIT 1
        """,
        (generator_id,)
    )
    row = cursor.fetchone()
    return row["level_id"] if row else None


def update_pair_stats(
    cursor: sqlite3.Cursor,
    gen1_id: str,
    gen2_id: str,
    result: str,
    now_utc: str
) -> None:
    """
    Update generator pair statistics after a battle.
    
    Args:
        cursor: Database cursor (within transaction)
        gen1_id: First generator ID (from battle, could be left or right)
        gen2_id: Second generator ID
        result: Vote result ("LEFT", "RIGHT", "TIE", "SKIP")
        now_utc: Current UTC timestamp
    
    Note: LEFT/RIGHT in result refers to battle positions, not gen1/gen2.
          This function handles the mapping based on which generator was on which side.
    """
    # Normalize to canonical order
    if gen1_id < gen2_id:
        canonical_gen1, canonical_gen2 = gen1_id, gen2_id
        # gen1 was on left in battle context
        left_is_gen1 = True
    else:
        canonical_gen1, canonical_gen2 = gen2_id, gen1_id
        # gen2 was on left in battle context
        left_is_gen1 = False
    
    # Determine winner in terms of gen1/gen2
    gen1_win_delta = 0
    gen2_win_delta = 0
    tie_delta = 0
    skip_delta = 0
    
    if result == "LEFT":
        if left_is_gen1:
            gen1_win_delta = 1
        else:
            gen2_win_delta = 1
    elif result == "RIGHT":
        if left_is_gen1:
            gen2_win_delta = 1
        else:
            gen1_win_delta = 1
    elif result == "TIE":
        tie_delta = 1
    elif result == "SKIP":
        skip_delta = 1
    
    # Upsert pair stats
    cursor.execute(
        """
        INSERT INTO generator_pair_stats (
            gen1_id, gen2_id, battle_count, gen1_wins, gen2_wins, ties, skips, last_battle_utc
        ) VALUES (?, ?, 1, ?, ?, ?, ?, ?)
        ON CONFLICT(gen1_id, gen2_id) DO UPDATE SET
            battle_count = battle_count + 1,
            gen1_wins = gen1_wins + ?,
            gen2_wins = gen2_wins + ?,
            ties = ties + ?,
            skips = skips + ?,
            last_battle_utc = ?
        """,
        (
            canonical_gen1, canonical_gen2,
            gen1_win_delta, gen2_win_delta, tie_delta, skip_delta, now_utc,
            gen1_win_delta, gen2_win_delta, tie_delta, skip_delta, now_utc
        )
    )


def get_matchmaking_stats(conn: sqlite3.Connection) -> dict:
    """
    Get statistics about the current matchmaking state.
    
    Useful for debugging and monitoring.
    """
    generators = get_active_generators_with_stats(conn)
    pair_counts = get_pair_counts(conn)
    
    # Calculate coverage
    n = len(generators)
    total_pairs = n * (n - 1) // 2 if n >= 2 else 0
    covered_pairs = sum(1 for count in pair_counts.values() if count > 0)
    target_covered = sum(1 for count in pair_counts.values() if count >= TARGET_BATTLES_PER_PAIR)
    
    # Calculate average RD
    avg_rd = sum(g.rd for g in generators) / n if n > 0 else 0
    
    # Find generators needing more games
    new_generators = [g for g in generators if g.games_played < MIN_GAMES_FOR_SIGNIFICANCE]
    
    return {
        "total_generators": n,
        "total_possible_pairs": total_pairs,
        "pairs_with_battles": covered_pairs,
        "pairs_at_target": target_covered,
        "coverage_percent": (covered_pairs / total_pairs * 100) if total_pairs > 0 else 0,
        "target_coverage_percent": (target_covered / total_pairs * 100) if total_pairs > 0 else 0,
        "average_rd": avg_rd,
        "new_generators_count": len(new_generators),
        "target_battles_per_pair": TARGET_BATTLES_PER_PAIR,
        "min_games_for_significance": MIN_GAMES_FOR_SIGNIFICANCE,
    }

