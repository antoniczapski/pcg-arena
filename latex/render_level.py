"""
Render the ASCII level from the thesis (lvl-3) into a colored sprite image,
using tile sprites from the client-java project's mapsheet.png, enemysheet.png,
and smallmariosheet.png.

The rendered image shows the beginning and end of the level with a visual cut
indicator (...) matching the thesis ASCII listing.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# ─── Paths ──────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE, "img")
RES = os.path.join(BASE, "..", "client-java", "src", "main", "resources", "img")
MAPSHEET = os.path.join(RES, "mapsheet.png")
ENEMYSHEET = os.path.join(RES, "enemysheet.png")
SMALLMARIO = os.path.join(RES, "smallmariosheet.png")
LEVEL_FILE = os.path.join(BASE, "..", "Mario-AI-Framework-PCG", "levels", "original", "lvl-3.txt")
OUTPUT = os.path.join(IMG_DIR, "ascii-level-rendered.png")

TILE = 16  # pixels per tile

# ─── Load and slice sprite sheets ───────────────────────────────────────────
def cut_sheet(path, tw, th):
    """Cut a spritesheet into a 2D list: sheet[col][row]."""
    img = Image.open(path).convert("RGBA")
    cols = img.width // tw
    rows = img.height // th
    sheet = [[None] * rows for _ in range(cols)]
    for c in range(cols):
        for r in range(rows):
            sheet[c][r] = img.crop((c * tw, r * th, (c + 1) * tw, (r + 1) * th))
    return sheet, cols, rows


mapsheet, map_cols, map_rows = cut_sheet(MAPSHEET, 16, 16)    # 8 cols x 7 rows
enemysheet, en_cols, en_rows = cut_sheet(ENEMYSHEET, 16, 32)  # 8 cols x 7 rows
mariosheet, sm_cols, sm_rows = cut_sheet(SMALLMARIO, 16, 16)  # 11 cols x 1 row


def get_map_tile(index):
    """Get a 16x16 tile from mapsheet by flat index."""
    col = index % map_cols  # % 8
    row = index // map_cols  # // 8
    return mapsheet[col][row]


def get_enemy_tile(index):
    """Get a 16x32 tile from enemysheet by flat index."""
    col = index % en_cols
    row = index // en_cols
    return enemysheet[col][row]


def get_mario_tile(index):
    """Get a 16x16 tile from smallmariosheet by flat index."""
    col = index % sm_cols
    row = index // sm_cols
    return mariosheet[col][row]


# ─── Read level file ────────────────────────────────────────────────────────
with open(LEVEL_FILE) as f:
    full_lines = [line.rstrip("\n") for line in f.readlines()]

num_rows = len(full_lines)  # 16
num_cols = len(full_lines[0])  # 150

# ─── Parse ASCII → tile indices (replicating MarioLevel.java logic) ─────────
level_tiles = [[0] * num_rows for _ in range(num_cols)]  # [x][y]
sprite_types = [[None] * num_rows for _ in range(num_cols)]
exit_x, exit_y = num_cols - 1, 0
mario_x, mario_y = 0, 0
mario_found = False
exit_found = False

# The thesis shows M at column 1, row 13 (added for illustration; not in file)
# We force this here to match the thesis figure
mario_x, mario_y = 1, 13
mario_found = True

for y in range(num_rows):
    for x in range(len(full_lines[y])):
        c = full_lines[y][x]
        if c == 'M':
            mario_x, mario_y = x, y
            mario_found = True
        elif c == 'F':
            exit_x, exit_y = x, y
            exit_found = True
        elif c == 'E' or c == 'g':
            sprite_types[x][y] = ('goomba', 16)
        elif c == 'G':
            sprite_types[x][y] = ('goomba_winged', 16)
        elif c == 'r':
            sprite_types[x][y] = ('red_koopa', 0)
        elif c == 'R':
            sprite_types[x][y] = ('red_koopa_winged', 0)
        elif c == 'k':
            sprite_types[x][y] = ('green_koopa', 8)
        elif c == 'K':
            sprite_types[x][y] = ('green_koopa_winged', 8)
        elif c == 'y':
            sprite_types[x][y] = ('spiky', 24)
        elif c == 'Y':
            sprite_types[x][y] = ('spiky_winged', 24)
        elif c == 'X':
            level_tiles[x][y] = 1
        elif c == '#':
            level_tiles[x][y] = 2
        elif c == '%':
            temp = 0
            if x > 0 and full_lines[y][x - 1] == '%':
                temp += 2
            if x < num_cols - 1 and full_lines[y][x + 1] == '%':
                temp += 1
            level_tiles[x][y] = 43 + temp
        elif c == '|':
            level_tiles[x][y] = 47
        elif c == '*':
            temp = 0
            if y > 0 and full_lines[y - 1][x] == '*':
                temp += 1
            if y > 1 and full_lines[y - 2][x] == '*':
                temp += 1
            level_tiles[x][y] = 3 + temp
        elif c == 'B':
            level_tiles[x][y] = 3
        elif c == 'b':
            temp = 0
            if y > 1 and full_lines[y - 2][x] == 'B':
                temp += 1
            level_tiles[x][y] = 4 + temp
        elif c in ('?', '@'):
            level_tiles[x][y] = 8
        elif c in ('Q', '!'):
            level_tiles[x][y] = 11
        elif c == '1':
            level_tiles[x][y] = 48
        elif c == '2':
            level_tiles[x][y] = 49
        elif c == 'D':
            level_tiles[x][y] = 14
        elif c == 'S':
            level_tiles[x][y] = 6
        elif c == 'C':
            level_tiles[x][y] = 7
        elif c == 'U':
            level_tiles[x][y] = 50
        elif c == 'L':
            level_tiles[x][y] = 51
        elif c == 'o':
            level_tiles[x][y] = 15
        elif c == 't':
            # Pipe logic
            line = full_lines[y]
            single = True
            if x < len(line) - 1 and line[x + 1].lower() == 't':
                single = False
            if x > 0 and line[x - 1].lower() == 't':
                single = False
            temp = 0
            if x > 0 and level_tiles[x - 1][y] in (18, 20):
                temp += 1
            if y > 0 and full_lines[y - 1][x].lower() == 't':
                if single:
                    temp += 1
                else:
                    temp += 2
            if single:
                level_tiles[x][y] = 52 + temp
            else:
                level_tiles[x][y] = 18 + temp
        elif c == 'T':
            line = full_lines[y]
            single = (x < len(line) - 1 and line[x + 1].lower() != 't' and
                       x > 0 and line[x - 1].lower() != 't')
            temp = 0
            if x > 0 and level_tiles[x - 1][y] in (18, 20):
                temp += 1
            if y > 0 and full_lines[y - 1][x].lower() == 't':
                if single:
                    temp += 1
                else:
                    temp += 2
            if single:
                level_tiles[x][y] = 52 + temp
            else:
                level_tiles[x][y] = 18 + temp
            # Flower enemy at pipe top-left
            if not single and temp == 0:
                sprite_types[x][y] = ('flower', 48)
        elif c == '<':
            level_tiles[x][y] = 18
        elif c == '>':
            level_tiles[x][y] = 19
        elif c == '[':
            level_tiles[x][y] = 20
        elif c == ']':
            level_tiles[x][y] = 21

# Find floor for exit if not explicitly set
def find_first_floor(lines, col):
    for row in range(len(lines) - 1, -1, -1):
        if col < len(lines[row]) and lines[row][col] == 'X':
            return row
    return len(lines) - 1

if not mario_found:
    mario_y = find_first_floor(full_lines, mario_x)
if not exit_found:
    exit_y = find_first_floor(full_lines, exit_x)

# Add flag pole tiles at exit column
for row in range(exit_y, max(1, exit_y - 11), -1):
    level_tiles[exit_x][row] = 40  # pole body
level_tiles[exit_x][max(1, exit_y - 11)] = 39  # pole top


# ─── Determine which columns to render (thesis shows cut view) ──────────────
# The thesis shows 81 columns at start + "..." + 6 columns at end
LEFT_COLS = 81   # columns 0..80
RIGHT_COLS = 6   # last 6 columns (144..149)
CUT_WIDTH_PX = 24  # width of the "..." cut indicator in pixels

left_start = 0
left_end = LEFT_COLS  # exclusive
right_start = num_cols - RIGHT_COLS
right_end = num_cols

# ─── Render ─────────────────────────────────────────────────────────────────
canvas_w = (LEFT_COLS + RIGHT_COLS) * TILE + CUT_WIDTH_PX
canvas_h = num_rows * TILE

# Sky tile (index 42) as background
sky_tile = get_map_tile(42)
canvas = Image.new("RGBA", (canvas_w, canvas_h))

# Fill background with sky
for px in range(0, canvas_w, TILE):
    for py in range(0, canvas_h, TILE):
        canvas.paste(sky_tile, (px, py))

# Also render background layer 1 (hills) - tiled pattern
hill_pattern = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [31, 32, 33, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [34, 35, 36, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 31, 32, 33, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 34, 35, 36, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
hill_w = len(hill_pattern[0])  # 16 tiles wide
hill_h = len(hill_pattern)  # 9 rows tall


def draw_bg_hills(canvas, offset_x, col_start, col_end):
    """Draw the tiled hill background for the given column range."""
    for col_idx in range(col_start, col_end):
        px = offset_x + (col_idx - col_start) * TILE
        bg_x = col_idx % hill_w
        for row_idx in range(num_rows):
            bg_y = row_idx % hill_h
            tile_idx = hill_pattern[bg_y][bg_x]
            if tile_idx != 0:
                tile = get_map_tile(tile_idx)
                canvas.paste(tile, (px, row_idx * TILE), tile)


draw_bg_hills(canvas, 0, left_start, left_end)
draw_bg_hills(canvas, LEFT_COLS * TILE + CUT_WIDTH_PX, right_start, right_end)


def draw_tile_at(canvas, px, py, tile_index):
    """Draw a map tile at pixel position, alpha-compositing."""
    if tile_index == 0:
        return  # air – skip
    tile = get_map_tile(tile_index)
    canvas.paste(tile, (px, py), tile)


def draw_enemy_at(canvas, px, py, start_index):
    """Draw an enemy sprite (16x32) centered on the tile position."""
    tile = get_enemy_tile(start_index)
    # Enemy sprites are 16x32, placed so their feet are at the bottom of the tile
    canvas.paste(tile, (px, py - TILE), tile)


def draw_mario_at(canvas, px, py):
    """Draw small Mario (idle frame 0) at position."""
    tile = get_mario_tile(0)
    canvas.paste(tile, (px, py), tile)


# Render left section (columns 0..80)
for col in range(left_start, left_end):
    for row in range(num_rows):
        px = (col - left_start) * TILE
        py = row * TILE
        draw_tile_at(canvas, px, py, level_tiles[col][row])

# Render right section (last 6 columns)
for col in range(right_start, right_end):
    for row in range(num_rows):
        px = LEFT_COLS * TILE + CUT_WIDTH_PX + (col - right_start) * TILE
        py = row * TILE
        draw_tile_at(canvas, px, py, level_tiles[col][row])

# Render enemies and Mario for left section
for col in range(left_start, left_end):
    for row in range(num_rows):
        st = sprite_types[col][row]
        if st is not None:
            px = (col - left_start) * TILE
            py = row * TILE
            if st[0] == 'flower':
                # Skip flower enemy in static render (inside pipe)
                pass
            else:
                draw_enemy_at(canvas, px, py, st[1])

# Mario at spawn
if left_start <= mario_x < left_end:
    px = (mario_x - left_start) * TILE
    py = mario_y * TILE
    draw_mario_at(canvas, px, py)

# Render enemies for right section
for col in range(right_start, right_end):
    for row in range(num_rows):
        st = sprite_types[col][row]
        if st is not None:
            px = LEFT_COLS * TILE + CUT_WIDTH_PX + (col - right_start) * TILE
            py = row * TILE
            if st[0] != 'flower':
                draw_enemy_at(canvas, px, py, st[1])

# Flag sprite (tile 41) - draw near the flag pole top
if right_start <= exit_x < right_end:
    flag_px = LEFT_COLS * TILE + CUT_WIDTH_PX + (exit_x - right_start) * TILE
    flag_top_y = max(1, exit_y - 11)
    flag_sprite = get_map_tile(41)
    canvas.paste(flag_sprite, (flag_px - TILE, (flag_top_y + 1) * TILE), flag_sprite)

# ─── Draw cut indicator ("...") ─────────────────────────────────────────────
cut_x_start = LEFT_COLS * TILE
cut_x_end = cut_x_start + CUT_WIDTH_PX

# Draw a subtle dashed/dotted separator
draw = ImageDraw.Draw(canvas)

# Fill cut region with a lighter sky shade
for py in range(0, canvas_h, TILE):
    sky_crop = sky_tile.copy()
    # Darken slightly to indicate cut
    darkener = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 50))
    sky_crop = Image.alpha_composite(sky_crop, darkener)
    # Tile it across the cut width
    for px_off in range(0, CUT_WIDTH_PX, TILE):
        w = min(TILE, CUT_WIDTH_PX - px_off)
        canvas.paste(sky_crop.crop((0, 0, w, TILE)), (cut_x_start + px_off, py))

# Draw vertical dashed lines at cut boundaries
for py in range(0, canvas_h, 4):
    if (py // 4) % 2 == 0:
        draw.line([(cut_x_start, py), (cut_x_start, py + 3)], fill=(255, 255, 255, 180), width=1)
        draw.line([(cut_x_end - 1, py), (cut_x_end - 1, py + 3)], fill=(255, 255, 255, 180), width=1)

# Draw "..." dots in the cut region
dot_y = canvas_h // 2
dot_spacing = CUT_WIDTH_PX // 4
for i in range(3):
    dx = cut_x_start + dot_spacing * (i + 1) - 1
    draw.ellipse([dx - 2, dot_y - 2, dx + 2, dot_y + 2], fill=(255, 255, 255, 220))

# ─── Scale up 3x for better visibility in thesis ────────────────────────────
scale = 3
canvas_scaled = canvas.resize(
    (canvas_w * scale, canvas_h * scale), Image.NEAREST
)

# Convert to RGB (no alpha) for LaTeX compatibility
canvas_rgb = Image.new("RGB", canvas_scaled.size, (109, 143, 252))
canvas_rgb.paste(canvas_scaled, mask=canvas_scaled.split()[3])

# ─── Save ───────────────────────────────────────────────────────────────────
os.makedirs(IMG_DIR, exist_ok=True)
canvas_rgb.save(OUTPUT)
print(f"Saved: {OUTPUT}")
print(f"Size: {canvas_rgb.size[0]}x{canvas_rgb.size[1]}")
