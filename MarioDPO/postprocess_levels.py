"""
Level Post-Processing Script
============================

Ensures all generated levels have:
1. Mario spawn point (M) at the beginning (first 5 columns)
2. Flag pole (F) at the end (last 5 columns)

Level format (16 rows, variable width):
- Row 0: top
- Row 14-15: ground area
- Column 0: leftmost (Mario spawn area)
- Column -1: rightmost (flag pole area)
"""

import argparse
from pathlib import Path
from typing import List, Tuple


def parse_level(level_content: str) -> List[List[str]]:
    """Parse level string into 2D list of tiles."""
    lines = level_content.strip().split('\n')
    return [list(line) for line in lines]


def level_to_string(level: List[List[str]]) -> str:
    """Convert 2D list back to level string."""
    return '\n'.join(''.join(row) for row in level)


def find_tile(level: List[List[str]], tile: str) -> List[Tuple[int, int]]:
    """Find all occurrences of a tile. Returns list of (row, col) tuples."""
    positions = []
    for row_idx, row in enumerate(level):
        for col_idx, t in enumerate(row):
            if t == tile:
                positions.append((row_idx, col_idx))
    return positions


def remove_tile(level: List[List[str]], tile: str) -> int:
    """Remove all occurrences of a tile, replacing with empty. Returns count removed."""
    count = 0
    for row in level:
        for col_idx in range(len(row)):
            if row[col_idx] == tile:
                row[col_idx] = '-'
                count += 1
    return count


def find_ground_level(level: List[List[str]], col: int) -> int:
    """Find the ground row at a given column (first solid from bottom)."""
    ground_tiles = {'X', '[', ']', '%', 'S', '?', 'Q', '#'}
    for row_idx in range(len(level) - 1, -1, -1):
        if col < len(level[row_idx]) and level[row_idx][col] in ground_tiles:
            return row_idx
    return len(level) - 2  # Default ground row


def ensure_mario_spawn(level: List[List[str]]) -> bool:
    """
    Ensure Mario spawn point (M) is at the beginning of the level.
    Places M in the first 5 columns on a platform.
    Returns True if modification was made.
    """
    # Find existing Mario positions
    mario_positions = find_tile(level, 'M')
    
    # Check if Mario is already at the start (col 0-5)
    valid_mario = [pos for pos in mario_positions if pos[1] <= 5]
    if valid_mario:
        # Mario already at start, remove any duplicates elsewhere
        for pos in mario_positions:
            if pos[1] > 5:
                level[pos[0]][pos[1]] = '-'
        return False
    
    # Remove any existing Mario
    remove_tile(level, 'M')
    
    # Find best position for Mario (on ground, column 2-3)
    for col in range(2, 5):
        ground_row = find_ground_level(level, col)
        spawn_row = ground_row - 1  # One above ground
        
        if spawn_row >= 0 and col < len(level[spawn_row]):
            # Ensure position is empty or non-essential
            if level[spawn_row][col] in {'-', 'o', 'g', 'k'}:
                level[spawn_row][col] = 'M'
                return True
    
    # Fallback: place at row 13, col 2 (typical start position)
    if len(level) > 13 and len(level[13]) > 2:
        level[13][2] = 'M'
        return True
    
    return False


def ensure_flag_pole(level: List[List[str]]) -> bool:
    """
    Ensure flag pole (F) is at the end of the level.
    Places F in the last 5 columns.
    Returns True if modification was made.
    """
    width = len(level[0]) if level else 0
    
    # Find existing flag positions
    flag_positions = find_tile(level, 'F')
    
    # Check if flag is already at the end (within last 5 columns)
    valid_flag = [pos for pos in flag_positions if pos[1] >= width - 5]
    if valid_flag:
        # Flag already at end, remove any duplicates elsewhere
        for pos in flag_positions:
            if pos[1] < width - 5:
                level[pos[0]][pos[1]] = '-'
        return False
    
    # Remove any existing flags
    remove_tile(level, 'F')
    
    # Find best position for flag (column width-3, on platform)
    for col in range(width - 3, width - 6, -1):
        if col < 0:
            continue
            
        ground_row = find_ground_level(level, col)
        flag_row = ground_row - 1  # One above ground
        
        if flag_row >= 0:
            # Ensure we have space for the flag
            if col < len(level[flag_row]):
                # Clear any obstacles at flag position
                for r in range(max(0, flag_row - 5), flag_row + 1):
                    if col < len(level[r]) and level[r][col] not in {'-', 'X', '[', ']'}:
                        level[r][col] = '-'
                
                level[flag_row][col] = 'F'
                
                # Ensure ground under flag
                if ground_row < len(level) and col < len(level[ground_row]):
                    if level[ground_row][col] == '-':
                        level[ground_row][col] = 'X'
                
                return True
    
    # Fallback: place at row 13, column width-3
    fallback_col = width - 3
    if fallback_col > 0 and len(level) > 13 and fallback_col < len(level[13]):
        level[13][fallback_col] = 'F'
        return True
    
    return False


def ensure_solid_ground_at_start_end(level: List[List[str]]) -> bool:
    """Ensure there's solid ground at the start and end of the level."""
    modified = False
    width = len(level[0]) if level else 0
    ground_row = len(level) - 2 if len(level) >= 2 else len(level) - 1
    
    # Ensure ground at start (first 5 columns)
    for col in range(min(5, width)):
        if ground_row < len(level) and col < len(level[ground_row]):
            if level[ground_row][col] == '-':
                level[ground_row][col] = 'X'
                modified = True
    
    # Ensure ground at end (last 5 columns)
    for col in range(max(0, width - 5), width):
        if ground_row < len(level) and col < len(level[ground_row]):
            if level[ground_row][col] == '-':
                level[ground_row][col] = 'X'
                modified = True
    
    return modified


def postprocess_level(level_content: str) -> Tuple[str, dict]:
    """
    Post-process a single level.
    Returns the processed level and a dict of modifications made.
    """
    level = parse_level(level_content)
    
    modifications = {
        'mario_moved': ensure_mario_spawn(level),
        'flag_moved': ensure_flag_pole(level),
        'ground_fixed': ensure_solid_ground_at_start_end(level)
    }
    
    return level_to_string(level), modifications


def postprocess_directory(input_dir: Path, output_dir: Path = None, in_place: bool = False):
    """
    Post-process all levels in a directory.
    
    Args:
        input_dir: Directory containing level files
        output_dir: Directory to save processed levels (if not in_place)
        in_place: If True, overwrite original files
    """
    if not input_dir.exists():
        print(f"ERROR: Input directory not found: {input_dir}")
        return
    
    if not in_place and output_dir is None:
        output_dir = input_dir.parent / f"{input_dir.name}_postprocessed"
    
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    level_files = list(input_dir.glob('*.txt'))
    print(f"\nPost-processing {len(level_files)} levels...")
    print(f"  Input: {input_dir}")
    if in_place:
        print(f"  Mode: In-place modification")
    else:
        print(f"  Output: {output_dir}")
    
    stats = {
        'total': len(level_files),
        'mario_moved': 0,
        'flag_moved': 0,
        'ground_fixed': 0,
        'unchanged': 0
    }
    
    for i, level_file in enumerate(sorted(level_files)):
        with open(level_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        processed, mods = postprocess_level(content)
        
        # Update stats
        if mods['mario_moved']:
            stats['mario_moved'] += 1
        if mods['flag_moved']:
            stats['flag_moved'] += 1
        if mods['ground_fixed']:
            stats['ground_fixed'] += 1
        if not any(mods.values()):
            stats['unchanged'] += 1
        
        # Save
        if in_place:
            save_path = level_file
        else:
            save_path = output_dir / level_file.name
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(processed)
        
        # Progress
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(level_files)} levels")
    
    print(f"\nPost-processing complete!")
    print(f"\nStatistics:")
    print(f"  Total levels: {stats['total']}")
    print(f"  Mario spawn fixed: {stats['mario_moved']}")
    print(f"  Flag pole fixed: {stats['flag_moved']}")
    print(f"  Ground fixed: {stats['ground_fixed']}")
    print(f"  Already valid: {stats['unchanged']}")


def main():
    parser = argparse.ArgumentParser(description='Post-process Mario levels')
    parser.add_argument('input_dir', type=str, help='Input directory with level files')
    parser.add_argument('-o', '--output', type=str, default=None,
                       help='Output directory (default: input_dir_postprocessed)')
    parser.add_argument('--in-place', action='store_true',
                       help='Modify files in place instead of creating copies')
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output) if args.output else None
    
    postprocess_directory(input_dir, output_dir, args.in_place)


if __name__ == '__main__':
    main()
