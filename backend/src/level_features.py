"""
Stage 5: Level Feature Extraction Module

Extracts static structural features from Mario level tilemaps for research analysis.
"""

import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from db import get_connection


# Tile character mappings (from frontend MarioLevel.ts)
TILE_CHARS = {
    # Empty
    '-': 'empty',
    # Ground
    'X': 'ground',
    '#': 'platform',
    '@': 'platform',
    'B': 'ground',
    'C': 'ground',
    'D': 'ground',
    'U': 'ground',
    'L': 'ground',
    'R': 'ground',
    # Bricks and blocks
    'S': 'brick',
    '?': 'question_block',
    'Q': 'question_block',
    '!': 'question_block',
    'M': 'question_block',
    '1': 'question_block',
    '2': 'question_block',
    # Pipes
    '<': 'pipe',
    '>': 'pipe',
    '[': 'pipe',
    ']': 'pipe',
    't': 'pipe_top',
    'T': 'pipe_top',
    # Coins
    'o': 'coin',
    '*': 'coin',
    # Special
    'b': 'bullet_spawner',
    'F': 'flag',
    'E': 'end',
}

# Enemy character mappings
ENEMY_CHARS = {
    'g': 'goomba',
    'G': 'goomba_winged',
    'k': 'koopa_green',
    'K': 'koopa_green_winged',
    'r': 'koopa_red',
    'R': 'koopa_red_winged',
    'y': 'spiky',
    'Y': 'spiky_winged',
    '*': 'piranha',  # Sometimes used for piranha
}


def extract_features_from_tilemap(tilemap: str, level_id: str) -> dict:
    """
    Extract structural features from a level tilemap.
    
    Args:
        tilemap: ASCII tilemap string (newline-separated rows)
        level_id: Level ID for reference
        
    Returns:
        Dictionary of extracted features
    """
    lines = tilemap.strip().split('\n')
    height = len(lines)
    width = max(len(line) for line in lines) if lines else 0
    
    # Initialize counters
    ground_tiles = 0
    platform_tiles = 0
    pipe_tiles = 0
    coin_tiles = 0
    question_block_tiles = 0
    brick_tiles = 0
    empty_tiles = 0
    
    # Enemy counts
    enemy_goomba = 0
    enemy_koopa_red = 0
    enemy_koopa_green = 0
    enemy_spiky = 0
    enemy_piranha = 0
    enemy_bullet_bill = 0
    
    # Gap analysis (track ground at bottom row)
    bottom_row = lines[-1] if lines else ''
    in_gap = False
    current_gap_width = 0
    gaps = []
    
    # Platform detection - track elevated solid tiles
    platforms = []
    
    for y, line in enumerate(lines):
        is_bottom_row = (y == height - 1)
        
        for x, char in enumerate(line):
            tile_type = TILE_CHARS.get(char, 'empty')
            enemy_type = ENEMY_CHARS.get(char)
            
            # Count tile types
            if tile_type == 'ground':
                ground_tiles += 1
            elif tile_type == 'platform':
                platform_tiles += 1
            elif tile_type in ['pipe', 'pipe_top']:
                pipe_tiles += 1
            elif tile_type == 'coin':
                coin_tiles += 1
            elif tile_type == 'question_block':
                question_block_tiles += 1
            elif tile_type == 'brick':
                brick_tiles += 1
            elif tile_type == 'empty' or tile_type == 'bullet_spawner':
                empty_tiles += 1
                
            # Count enemies
            if enemy_type == 'goomba':
                enemy_goomba += 1
            elif enemy_type == 'goomba_winged':
                enemy_goomba += 1
            elif enemy_type == 'koopa_green':
                enemy_koopa_green += 1
            elif enemy_type == 'koopa_green_winged':
                enemy_koopa_green += 1
            elif enemy_type == 'koopa_red':
                enemy_koopa_red += 1
            elif enemy_type == 'koopa_red_winged':
                enemy_koopa_red += 1
            elif enemy_type == 'spiky' or enemy_type == 'spiky_winged':
                enemy_spiky += 1
            elif enemy_type == 'piranha':
                enemy_piranha += 1
            
            if tile_type == 'bullet_spawner':
                enemy_bullet_bill += 1
            
            # Gap detection at bottom row
            if is_bottom_row:
                is_solid = tile_type in ['ground', 'platform', 'pipe', 'pipe_top', 'brick']
                if not is_solid:
                    if not in_gap:
                        in_gap = True
                        current_gap_width = 1
                    else:
                        current_gap_width += 1
                else:
                    if in_gap:
                        gaps.append(current_gap_width)
                        in_gap = False
                        current_gap_width = 0
    
    # Finish final gap
    if in_gap:
        gaps.append(current_gap_width)
    
    # Compute derived features
    enemy_total = enemy_goomba + enemy_koopa_red + enemy_koopa_green + enemy_spiky + enemy_piranha + enemy_bullet_bill
    gap_count = len(gaps)
    max_gap_width = max(gaps) if gaps else 0
    
    # Densities (per column)
    enemy_density = enemy_total / width if width > 0 else 0
    coin_density = coin_tiles / width if width > 0 else 0
    gap_density = sum(gaps) / width if width > 0 else 0
    
    # Structural complexity: combination of variety
    unique_tile_types = sum([
        1 if ground_tiles > 0 else 0,
        1 if platform_tiles > 0 else 0,
        1 if pipe_tiles > 0 else 0,
        1 if question_block_tiles > 0 else 0,
        1 if brick_tiles > 0 else 0,
    ])
    structural_complexity = min(1.0, (unique_tile_types / 5) + (gap_count / 10) + (enemy_total / 20))
    
    # Leniency score (higher = easier)
    # Based on: fewer gaps, fewer enemies, more powerups
    leniency = 1.0 - min(1.0, (gap_density * 2) + (enemy_density * 0.5) + (0.1 * (1 - coin_density)))
    
    return {
        "level_id": level_id,
        "width": width,
        "height": height,
        "ground_tiles": ground_tiles,
        "platform_tiles": platform_tiles,
        "pipe_tiles": pipe_tiles,
        "coin_tiles": coin_tiles,
        "question_block_tiles": question_block_tiles,
        "brick_tiles": brick_tiles,
        "empty_tiles": empty_tiles,
        "enemy_goomba": enemy_goomba,
        "enemy_koopa_red": enemy_koopa_red,
        "enemy_koopa_green": enemy_koopa_green,
        "enemy_spiky": enemy_spiky,
        "enemy_piranha": enemy_piranha,
        "enemy_bullet_bill": enemy_bullet_bill,
        "enemy_total": enemy_total,
        "gap_count": gap_count,
        "max_gap_width": max_gap_width,
        "platform_count": 0,  # TODO: implement platform detection
        "avg_platform_height": None,
        "height_variance": None,
        "enemy_density": round(enemy_density, 4),
        "coin_density": round(coin_density, 4),
        "gap_density": round(gap_density, 4),
        "structural_complexity": round(structural_complexity, 4),
        "leniency_score": round(leniency, 4),
    }


def store_level_features(cursor: sqlite3.Cursor, features: dict, now_utc: str) -> None:
    """Store extracted features in the database."""
    cursor.execute(
        """
        INSERT OR REPLACE INTO level_features (
            level_id, width, height,
            ground_tiles, platform_tiles, pipe_tiles, coin_tiles,
            question_block_tiles, brick_tiles, empty_tiles,
            enemy_goomba, enemy_koopa_red, enemy_koopa_green, enemy_spiky,
            enemy_piranha, enemy_bullet_bill, enemy_total,
            gap_count, max_gap_width, platform_count,
            avg_platform_height, height_variance,
            enemy_density, coin_density, gap_density,
            structural_complexity, leniency_score,
            computed_at_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            features["level_id"],
            features["width"],
            features["height"],
            features["ground_tiles"],
            features["platform_tiles"],
            features["pipe_tiles"],
            features["coin_tiles"],
            features["question_block_tiles"],
            features["brick_tiles"],
            features["empty_tiles"],
            features["enemy_goomba"],
            features["enemy_koopa_red"],
            features["enemy_koopa_green"],
            features["enemy_spiky"],
            features["enemy_piranha"],
            features["enemy_bullet_bill"],
            features["enemy_total"],
            features["gap_count"],
            features["max_gap_width"],
            features["platform_count"],
            features["avg_platform_height"],
            features["height_variance"],
            features["enemy_density"],
            features["coin_density"],
            features["gap_density"],
            features["structural_complexity"],
            features["leniency_score"],
            now_utc,
        )
    )


def extract_and_store_all_level_features() -> int:
    """Extract features for all levels that don't have them yet."""
    conn = get_connection()
    now_utc = datetime.now(timezone.utc).isoformat()
    
    # Get levels without features
    cursor = conn.execute(
        """
        SELECT l.level_id, l.level_data
        FROM levels l
        LEFT JOIN level_features lf ON l.level_id = lf.level_id
        WHERE lf.level_id IS NULL
        """
    )
    
    count = 0
    for row in cursor.fetchall():
        level_id = row["level_id"]
        level_data = row["level_data"]
        
        if level_data:
            features = extract_features_from_tilemap(level_data, level_id)
            write_cursor = conn.cursor()
            store_level_features(write_cursor, features, now_utc)
            count += 1
    
    conn.commit()
    return count


def get_level_features(level_id: str) -> Optional[dict]:
    """Get features for a specific level."""
    conn = get_connection()
    
    cursor = conn.execute(
        "SELECT * FROM level_features WHERE level_id = ?",
        (level_id,)
    )
    row = cursor.fetchone()
    
    if not row:
        return None
    
    return {
        "level_id": row["level_id"],
        "dimensions": {
            "width": row["width"],
            "height": row["height"]
        },
        "tiles": {
            "ground": row["ground_tiles"],
            "platform": row["platform_tiles"],
            "pipe": row["pipe_tiles"],
            "coin": row["coin_tiles"],
            "question_block": row["question_block_tiles"],
            "brick": row["brick_tiles"],
            "empty": row["empty_tiles"]
        },
        "enemies": {
            "goomba": row["enemy_goomba"],
            "koopa_red": row["enemy_koopa_red"],
            "koopa_green": row["enemy_koopa_green"],
            "spiky": row["enemy_spiky"],
            "piranha": row["enemy_piranha"],
            "bullet_bill": row["enemy_bullet_bill"],
            "total": row["enemy_total"]
        },
        "structure": {
            "gap_count": row["gap_count"],
            "max_gap_width": row["max_gap_width"],
            "platform_count": row["platform_count"]
        },
        "metrics": {
            "enemy_density": row["enemy_density"],
            "coin_density": row["coin_density"],
            "gap_density": row["gap_density"],
            "structural_complexity": row["structural_complexity"],
            "leniency_score": row["leniency_score"]
        }
    }

