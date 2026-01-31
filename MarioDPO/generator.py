"""
Mario-DPO Level Generator
=========================

Generates Mario levels using a character-level Markov chain model
trained on Original (Nintendo-style) levels. This serves as:
1. A baseline for comparison with future DPO-aligned models
2. A demonstration of the generation pipeline
3. A source of levels for PCG Arena evaluation

Uses n-gram patterns from Original levels with:
- Column-by-column generation (respects vertical structure)
- Playability constraints (ground continuity, reachability)
- Style matching (maintains Original level characteristics)
"""

import json
import numpy as np
import random
from pathlib import Path
from collections import defaultdict, Counter
import re
from typing import List, Tuple, Dict, Optional
import argparse

# Paths
MARIO_DPO_DIR = Path(__file__).parent
LEVELS_DIR = MARIO_DPO_DIR.parent / 'db' / 'seed' / 'levels'
OUTPUT_DIR = MARIO_DPO_DIR / 'generated_levels'

# Level constants
LEVEL_HEIGHT = 16
MIN_WIDTH = 150
MAX_WIDTH = 200
GROUND_ROW = 14  # Row index for ground (0-indexed from top)

# Tile types
EMPTY = '-'
SOLID = 'X'
PIPE_TOP_LEFT = '<'
PIPE_TOP_RIGHT = '>'
PIPE_BODY_LEFT = '['
PIPE_BODY_RIGHT = ']'
QUESTION_BLOCK = '?'
BRICK = 'S'
COIN = 'o'
GOOMBA = 'g'
KOOPA = 'k'
PLATFORM = '%'

# Important tiles for structure
GROUND_TILES = {SOLID, PIPE_BODY_LEFT, PIPE_BODY_RIGHT, '[', ']'}
HAZARD_TILES = {'g', 'k', 'E', 'r', 'y', 'G', 'K', 'R', 'Y'}
REWARD_TILES = {'?', 'Q', 'o', 'C', '@', '!', '1', '2', 'U', 'L'}


class ColumnMarkovGenerator:
    """
    Generates levels column-by-column using learned patterns from Original levels.
    Uses n-gram patterns where each "token" is a full column of 16 tiles.
    """
    
    def __init__(self, n_gram: int = 3):
        self.n_gram = n_gram
        self.column_transitions: Dict[Tuple[str, ...], Counter] = defaultdict(Counter)
        self.start_columns: List[Tuple[str, ...]] = []
        self.all_columns: List[str] = []
        self.original_levels: List[List[str]] = []
        
    def load_original_levels(self) -> int:
        """Load all Original (Nintendo) levels"""
        original_dir = LEVELS_DIR / 'original'
        if not original_dir.exists():
            print(f"Warning: Original levels directory not found at {original_dir}")
            return 0
        
        count = 0
        for level_file in sorted(original_dir.glob('*.txt')):
            try:
                with open(level_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.strip().split('\n')
                    
                    # Pad to standard height
                    while len(lines) < LEVEL_HEIGHT:
                        lines.insert(0, EMPTY * len(lines[0]) if lines else EMPTY * 150)
                    
                    # Truncate if too tall
                    lines = lines[:LEVEL_HEIGHT]
                    
                    # Store as list of rows
                    self.original_levels.append(lines)
                    count += 1
            except Exception as e:
                print(f"Error loading {level_file}: {e}")
        
        print(f"Loaded {count} Original levels")
        return count
    
    def train(self):
        """Learn column transition patterns from Original levels"""
        print("Training column Markov model...")
        
        for level in self.original_levels:
            # Convert rows to columns
            width = len(level[0])
            columns = []
            for col_idx in range(width):
                column = ''.join(row[col_idx] if col_idx < len(row) else EMPTY 
                               for row in level)
                columns.append(column)
                self.all_columns.append(column)
            
            # Learn n-gram transitions
            if len(columns) >= self.n_gram:
                # Store start sequence
                self.start_columns.append(tuple(columns[:self.n_gram]))
                
                # Learn transitions
                for i in range(len(columns) - self.n_gram):
                    context = tuple(columns[i:i + self.n_gram])
                    next_col = columns[i + self.n_gram]
                    self.column_transitions[context][next_col] += 1
        
        print(f"  Learned {len(self.column_transitions)} unique contexts")
        print(f"  Total columns seen: {len(self.all_columns)}")
        print(f"  Start sequences: {len(self.start_columns)}")
    
    def _sample_next_column(self, context: Tuple[str, ...], temperature: float = 1.0) -> str:
        """Sample next column given context"""
        if context in self.column_transitions:
            candidates = self.column_transitions[context]
            columns = list(candidates.keys())
            counts = np.array(list(candidates.values()), dtype=float)
            
            # Apply temperature
            if temperature != 1.0:
                counts = np.power(counts, 1.0 / temperature)
            
            probs = counts / counts.sum()
            return np.random.choice(columns, p=probs)
        else:
            # Fallback: sample from all seen columns with bias toward common ones
            return random.choice(self.all_columns)
    
    def _ensure_ground_continuity(self, columns: List[str], max_gap: int = 3) -> List[str]:
        """Ensure there are no death gaps longer than max_gap"""
        result = []
        gap_count = 0
        
        for i, col in enumerate(columns):
            col_list = list(col)
            
            # Check if this column has ground
            has_ground = col_list[GROUND_ROW] in GROUND_TILES or col_list[GROUND_ROW + 1] in GROUND_TILES
            
            if not has_ground:
                gap_count += 1
                if gap_count > max_gap:
                    # Force add ground
                    col_list[GROUND_ROW] = SOLID
                    col_list[GROUND_ROW + 1] = SOLID
                    gap_count = 0
            else:
                gap_count = 0
            
            result.append(''.join(col_list))
        
        return result
    
    def _add_start_platform(self, columns: List[str]) -> List[str]:
        """Ensure starting area is safe for player spawn"""
        for i in range(min(5, len(columns))):
            col_list = list(columns[i])
            # Ensure ground at start
            col_list[GROUND_ROW] = SOLID
            col_list[GROUND_ROW + 1] = SOLID
            # Clear spawn area
            for row in range(GROUND_ROW - 3, GROUND_ROW):
                col_list[row] = EMPTY
            columns[i] = ''.join(col_list)
        return columns
    
    def _add_flag_pole(self, columns: List[str]) -> List[str]:
        """Add flag pole at the end"""
        # Last few columns should have flag
        if len(columns) < 10:
            return columns
        
        # Add flag pole structure
        flag_col = len(columns) - 3
        for i in range(flag_col, min(flag_col + 2, len(columns))):
            col_list = list(columns[i])
            # Flag pole
            for row in range(3, GROUND_ROW):
                col_list[row] = '|' if i == flag_col else EMPTY
            col_list[GROUND_ROW] = SOLID
            col_list[GROUND_ROW + 1] = SOLID
            columns[i] = ''.join(col_list)
        
        return columns
    
    def generate_level(self, 
                       target_width: int = None,
                       temperature: float = 0.8,
                       seed: int = None) -> str:
        """Generate a single level"""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        if target_width is None:
            target_width = random.randint(MIN_WIDTH, MAX_WIDTH)
        
        # Start with a random learned start sequence
        if self.start_columns:
            columns = list(random.choice(self.start_columns))
        else:
            # Fallback: create simple start
            start_col = EMPTY * (GROUND_ROW) + SOLID * 2
            columns = [start_col] * self.n_gram
        
        # Generate remaining columns
        while len(columns) < target_width:
            context = tuple(columns[-self.n_gram:])
            next_col = self._sample_next_column(context, temperature)
            columns.append(next_col)
        
        # Post-processing for playability
        columns = self._ensure_ground_continuity(columns, max_gap=3)
        columns = self._add_start_platform(columns)
        columns = self._add_flag_pole(columns)
        
        # Convert columns back to rows
        rows = []
        for row_idx in range(LEVEL_HEIGHT):
            row = ''.join(col[row_idx] if row_idx < len(col) else EMPTY 
                         for col in columns)
            rows.append(row)
        
        return '\n'.join(rows)
    
    def calculate_style_score(self, level: str) -> float:
        """Calculate how similar a level is to Original style"""
        lines = level.strip().split('\n')
        
        # Metrics
        total_tiles = sum(len(line) for line in lines)
        
        # Count tile frequencies
        tile_counts = Counter()
        for line in lines:
            tile_counts.update(line)
        
        # Original levels have specific tile ratios
        empty_ratio = tile_counts.get(EMPTY, 0) / total_tiles
        solid_ratio = tile_counts.get(SOLID, 0) / total_tiles
        
        # Ideal ratios (from Original level analysis)
        ideal_empty = 0.85
        ideal_solid = 0.05
        
        # Score based on deviation from ideal
        empty_score = 1.0 - abs(empty_ratio - ideal_empty)
        solid_score = 1.0 - abs(solid_ratio - ideal_solid) * 10
        
        return (empty_score + solid_score) / 2


class StyleConditionedGenerator(ColumnMarkovGenerator):
    """
    Extended generator with style conditioning.
    Can generate levels with different difficulty/style profiles.
    """
    
    def __init__(self, n_gram: int = 3):
        super().__init__(n_gram)
        self.style_profiles = {
            'easy': {'gap_prob': 0.05, 'enemy_prob': 0.02, 'platform_prob': 0.1},
            'medium': {'gap_prob': 0.10, 'enemy_prob': 0.05, 'platform_prob': 0.15},
            'hard': {'gap_prob': 0.15, 'enemy_prob': 0.08, 'platform_prob': 0.20},
            'nintendo': {'gap_prob': 0.08, 'enemy_prob': 0.04, 'platform_prob': 0.12},
        }
    
    def _apply_style(self, columns: List[str], style: str = 'nintendo') -> List[str]:
        """Apply style modifications to generated columns"""
        profile = self.style_profiles.get(style, self.style_profiles['nintendo'])
        result = []
        
        for i, col in enumerate(columns):
            col_list = list(col)
            
            # Skip first and last sections
            if i < 10 or i > len(columns) - 10:
                result.append(col)
                continue
            
            # Randomly add gaps (remove ground)
            if random.random() < profile['gap_prob']:
                if col_list[GROUND_ROW] == SOLID:
                    col_list[GROUND_ROW] = EMPTY
                    col_list[GROUND_ROW + 1] = EMPTY
            
            # Randomly add enemies
            if random.random() < profile['enemy_prob']:
                # Find a platform to place enemy on
                for row in range(GROUND_ROW - 1, 0, -1):
                    if col_list[row] == EMPTY and col_list[row + 1] in GROUND_TILES:
                        col_list[row] = random.choice(['g', 'k'])
                        break
            
            # Randomly add platforms
            if random.random() < profile['platform_prob']:
                platform_row = random.randint(5, GROUND_ROW - 4)
                if col_list[platform_row] == EMPTY:
                    col_list[platform_row] = '%'
            
            result.append(''.join(col_list))
        
        return result
    
    def generate_level(self,
                       target_width: int = None,
                       temperature: float = 0.8,
                       style: str = 'nintendo',
                       seed: int = None) -> str:
        """Generate a level with style conditioning"""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        if target_width is None:
            target_width = random.randint(MIN_WIDTH, MAX_WIDTH)
        
        # Generate base level
        if self.start_columns:
            columns = list(random.choice(self.start_columns))
        else:
            start_col = EMPTY * (GROUND_ROW) + SOLID * 2
            columns = [start_col] * self.n_gram
        
        while len(columns) < target_width:
            context = tuple(columns[-self.n_gram:])
            next_col = self._sample_next_column(context, temperature)
            columns.append(next_col)
        
        # Apply style modifications
        columns = self._apply_style(columns, style)
        
        # Post-processing
        columns = self._ensure_ground_continuity(columns, max_gap=4 if style == 'hard' else 3)
        columns = self._add_start_platform(columns)
        columns = self._add_flag_pole(columns)
        
        # Convert to rows
        rows = []
        for row_idx in range(LEVEL_HEIGHT):
            row = ''.join(col[row_idx] if row_idx < len(col) else EMPTY 
                         for col in columns)
            rows.append(row)
        
        return '\n'.join(rows)


def generate_levels(n_levels: int = 500,
                   output_dir: Path = OUTPUT_DIR,
                   style: str = 'nintendo',
                   temperature: float = 0.8,
                   seed: int = 42) -> List[str]:
    """
    Generate n_levels using MarioDPO baseline generator.
    
    Args:
        n_levels: Number of levels to generate
        output_dir: Directory to save generated levels
        style: Style profile ('easy', 'medium', 'hard', 'nintendo')
        temperature: Sampling temperature (lower = more conservative)
        seed: Random seed for reproducibility
    
    Returns:
        List of generated level strings
    """
    print("="*60)
    print(f"MARIO-DPO LEVEL GENERATOR")
    print("="*60)
    print(f"  Levels to generate: {n_levels}")
    print(f"  Style: {style}")
    print(f"  Temperature: {temperature}")
    print(f"  Output: {output_dir}")
    print()
    
    # Initialize generator
    generator = StyleConditionedGenerator(n_gram=3)
    
    # Load and train on Original levels
    n_original = generator.load_original_levels()
    if n_original == 0:
        print("ERROR: No Original levels found. Cannot train generator.")
        return []
    
    generator.train()
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate levels
    print(f"\nGenerating {n_levels} levels...")
    generated = []
    
    random.seed(seed)
    np.random.seed(seed)
    
    for i in range(n_levels):
        level = generator.generate_level(
            temperature=temperature,
            style=style,
            seed=seed + i
        )
        generated.append(level)
        
        # Save to file
        filename = f"mariodpo_{style}_{i:04d}.txt"
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(level)
        
        # Progress
        if (i + 1) % 50 == 0:
            print(f"  Generated {i + 1}/{n_levels} levels")
    
    print(f"\nGeneration complete!")
    print(f"  Saved to: {output_dir}")
    
    # Calculate statistics
    print("\nLevel Statistics:")
    widths = [len(level.split('\n')[0]) for level in generated]
    print(f"  Width range: {min(widths)} - {max(widths)} (mean: {np.mean(widths):.1f})")
    
    # Style scores
    scores = [generator.calculate_style_score(level) for level in generated]
    print(f"  Style score range: {min(scores):.3f} - {max(scores):.3f} (mean: {np.mean(scores):.3f})")
    
    return generated


def main():
    parser = argparse.ArgumentParser(description='Generate Mario levels using MarioDPO')
    parser.add_argument('-n', '--num-levels', type=int, default=500,
                       help='Number of levels to generate (default: 500)')
    parser.add_argument('-s', '--style', type=str, default='nintendo',
                       choices=['easy', 'medium', 'hard', 'nintendo'],
                       help='Style profile (default: nintendo)')
    parser.add_argument('-t', '--temperature', type=float, default=0.8,
                       help='Sampling temperature (default: 0.8)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed (default: 42)')
    parser.add_argument('-o', '--output', type=str, default=None,
                       help='Output directory')
    
    args = parser.parse_args()
    
    output_dir = Path(args.output) if args.output else OUTPUT_DIR
    
    generate_levels(
        n_levels=args.num_levels,
        output_dir=output_dir,
        style=args.style,
        temperature=args.temperature,
        seed=args.seed
    )


if __name__ == '__main__':
    main()
