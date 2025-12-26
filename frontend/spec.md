# PCG Arena - Frontend Specification

**Created:** 2025-12-26  
**Protocol:** arena/v0  
**Status:** ✅ COMPLETE (Deployed and operational)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Technology Stack](#2-technology-stack)
3. [Architecture](#3-architecture)
4. [Implementation Phases](#4-implementation-phases)
5. [Engine Components](#5-engine-components)
6. [API Integration](#6-api-integration)
7. [Rendering System](#7-rendering-system)
8. [Input System](#8-input-system)
9. [Battle Flow](#9-battle-flow)
10. [Telemetry](#10-telemetry)
11. [Configuration](#11-configuration)
12. [Development](#12-development)
13. [Production Build](#13-production-build)
14. [Browser Support](#14-browser-support)

---

## 1. Overview

### 1.1 Purpose

The browser frontend is a TypeScript/React implementation that allows users to play Mario levels directly in the browser without downloading a client. It implements the same `arena/v0` protocol as the Java validation client.

### 1.2 Key Features

- **No Download Required:** Runs in any modern browser
- **Faithful Recreation:** Identical gameplay to Java client
- **Keyboard Controls:** Desktop-focused (Arrow keys, S, A)
- **Protocol Compliance:** Full `arena/v0` implementation
- **Telemetry Collection:** Same event tracking as Java client
- **Responsive Design:** Side-by-side level comparison

### 1.3 Design Goals

1. **Accessibility:** Remove download barrier for users
2. **Fidelity:** Match Java client gameplay exactly
3. **Performance:** 60 FPS gameplay on modern hardware
4. **Maintainability:** Clean TypeScript codebase
5. **Browser Compatibility:** Support major browsers (Chrome, Firefox, Safari)

---

## 2. Technology Stack

### 2.1 Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.3 | UI framework and component management |
| **TypeScript** | 5.6 | Type safety and development tooling |
| **Vite** | 5.4 | Build tool and dev server |
| **HTML5 Canvas** | Native | Game rendering |

### 2.2 Key Dependencies

```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "typescript": "~5.6.2",
  "vite": "^5.4.10"
}
```

### 2.3 Why These Choices

- **React:** Component-based architecture, familiar ecosystem
- **TypeScript:** Catch errors at compile time, better IDE support
- **Vite:** Fast HMR, modern build tool, simple configuration
- **Canvas:** Direct pixel manipulation, proven for 2D games

---

## 3. Architecture

### 3.1 Directory Structure

```
frontend/
├── src/
│   ├── api/                    # Backend communication
│   │   ├── client.ts           # ArenaApiClient implementation
│   │   └── types.ts            # API response types
│   │
│   ├── engine/                 # Game engine (ported from Java)
│   │   ├── MarioGame.ts        # Game loop manager
│   │   ├── MarioWorld.ts       # Game state and logic
│   │   ├── MarioLevel.ts       # Level parsing and tile queries
│   │   ├── MarioSprite.ts      # Base sprite class
│   │   │
│   │   ├── sprites/            # Sprite implementations
│   │   │   ├── Mario.ts        # Player character
│   │   │   ├── Enemy.ts        # Base enemy class
│   │   │   ├── Shell.ts        # Koopa shell
│   │   │   ├── Fireball.ts     # Mario's fireball
│   │   │   ├── Mushroom.ts     # Power-up items
│   │   │   ├── FireFlower.ts
│   │   │   ├── LifeMushroom.ts
│   │   │   ├── FlowerEnemy.ts  # Piranha plant
│   │   │   └── BulletBill.ts   # Bullet Bill enemy
│   │   │
│   │   ├── graphics/           # Rendering system
│   │   │   ├── AssetLoader.ts  # Asset management
│   │   │   ├── Camera.ts       # Viewport scrolling
│   │   │   ├── SpriteRenderer.ts    # Sprite drawing
│   │   │   └── TilemapRenderer.ts   # Level tile rendering
│   │   │
│   │   ├── input/              # Input handling
│   │   │   └── KeyboardInput.ts     # Keyboard controls
│   │   │
│   │   ├── effects/            # Visual effects
│   │   │   ├── MarioEffect.ts  # Base effect class
│   │   │   ├── BrickEffect.ts  # Brick particles
│   │   │   ├── CoinEffect.ts   # Coin sparkle
│   │   │   ├── DeathEffect.ts  # Enemy death animation
│   │   │   ├── DustEffect.ts   # Running dust
│   │   │   ├── FireballEffect.ts    # Fireball impact
│   │   │   └── SquishEffect.ts      # Enemy squish
│   │   │
│   │   └── [Enums & Constants] # TileFeature, SpriteType, GameStatus, etc.
│   │
│   ├── components/             # React components
│   │   ├── BattleFlow.tsx      # Battle orchestration
│   │   ├── GameCanvas.tsx      # Canvas wrapper with game loop
│   │   ├── VotingPanel.tsx     # Vote submission UI
│   │   ├── Leaderboard.tsx     # Generator rankings
│   │   └── StatusBar.tsx       # Battle info display
│   │
│   ├── styles/                 # CSS stylesheets
│   │   ├── global.css          # Base styles
│   │   └── components.css      # Component-specific styles
│   │
│   ├── App.tsx                 # Root component
│   ├── main.tsx                # React entry point
│   └── vite-env.d.ts           # Vite environment types
│
├── public/
│   └── assets/                 # Sprite sheets
│       ├── mariosheet.png      # Mario sprites
│       ├── enemysheet.png      # Enemy sprites
│       ├── mapsheet.png        # Tile sprites
│       ├── firemariosheet.png  # Fire Mario sprites
│       └── items.png           # Item sprites
│
├── .env                        # Default config (localhost)
├── .env.production             # Production config
├── .env.local.example          # Template for local overrides
├── package.json                # Dependencies
├── tsconfig.json               # TypeScript config
├── vite.config.ts              # Vite build config
└── index.html                  # HTML entry point
```

### 3.2 Component Hierarchy

```
App
└── BattleFlow
    ├── StatusBar (battle info)
    ├── GameCanvas (left level)
    ├── GameCanvas (right level)
    ├── VotingPanel (after both played)
    └── Leaderboard (after vote submitted)
```

### 3.3 Data Flow

1. **Battle Fetch:** `BattleFlow` → `ArenaApiClient` → Backend
2. **Level Data:** Backend → `BattleFlow` → `GameCanvas`
3. **Game Loop:** `GameCanvas` → `MarioGame` → `MarioWorld` → Sprites
4. **Rendering:** `MarioWorld` → Renderers → Canvas
5. **Input:** Browser events → `KeyboardInput` → `MarioWorld` → `Mario`
6. **Telemetry:** `MarioWorld` events → `BattleFlow` state
7. **Vote:** `VotingPanel` → `ArenaApiClient` → Backend

---

## 4. Implementation Phases

### 4.1 Phase Breakdown

| Phase | Description | Status | Key Files |
|-------|-------------|--------|-----------|
| **Phase 1** | API client + project setup | ✅ Complete | `api/client.ts`, `api/types.ts` |
| **Phase 2** | Core game engine | ✅ Complete | `MarioGame.ts`, `MarioWorld.ts`, `MarioLevel.ts` |
| **Phase 3** | Sprite implementations | ✅ Complete | `sprites/*.ts` |
| **Phase 4** | Rendering system | ✅ Complete | `graphics/*.ts` |
| **Phase 5** | Visual effects | ✅ Complete | `effects/*.ts` |
| **Phase 6** | Input handling | ✅ Complete | `input/KeyboardInput.ts` |
| **Phase 7** | Battle UI | ✅ Complete | `components/*.tsx` |
| **Phase 8** | Telemetry | ✅ Complete | Event tracking in `MarioWorld.ts` |
| **Phase 9** | Styling | ✅ Complete | `styles/*.css` |
| **Phase 10** | Testing + deployment | ✅ Complete | Production build validated |

### 4.2 Development Timeline

- **Phase 1-2:** Foundation (2 days)
- **Phase 3-4:** Core gameplay (3 days)
- **Phase 5-6:** Polish and input (2 days)
- **Phase 7-9:** UI and styling (2 days)
- **Phase 10:** Testing and fixes (3 days)

**Total:** ~12 days of development

---

## 5. Engine Components

### 5.1 MarioGame (Game Loop Manager)

**Responsibility:** Manages the game loop at 30 FPS.

**Key Methods:**
- `start()` - Begin game loop
- `stop()` - Stop game loop
- `tick()` - Execute one game tick (update + render)

**Ported from:** `client-java/.../game/MarioGame.java`

---

### 5.2 MarioWorld (Game State)

**Responsibility:** Central game state manager. Handles sprites, level, collision, events.

**Key Properties:**
- `mario: Mario` - Player character
- `sprites: MarioSprite[]` - All active sprites
- `effects: MarioEffect[]` - Visual effects
- `level: MarioLevel` - Current level
- `camera: Camera` - Viewport
- `events: GameEvent[]` - Event log for telemetry

**Key Methods:**
- `update()` - Update all sprites and physics
- `checkCollisions()` - Sprite vs sprite and sprite vs level
- `addSprite()` / `removeSprite()` - Sprite lifecycle
- `getSceneObservation()` - Generate telemetry snapshot

**Ported from:** `client-java/.../game/MarioWorld.java`

---

### 5.3 MarioLevel (Level Data)

**Responsibility:** Parse ASCII tilemap and provide tile queries.

**Key Methods:**
- `loadFromString(tilemap: string)` - Parse ASCII level
- `getTileFeature(x, y)` - Get tile type at world coordinates
- `isBlocking(x, y)` - Check if tile blocks movement
- `setTile(x, y, feature)` - Modify tile (for brick breaking)

**ASCII Format:**
- Width: Variable (up to 250)
- Height: 16 lines
- Characters: See `docs/stage0-spec.md` Section 8

**Ported from:** `client-java/.../game/MarioLevel.java`

---

### 5.4 MarioSprite (Base Sprite Class)

**Responsibility:** Base class for all game entities.

**Key Properties:**
- `x, y` - Position (center-bottom)
- `xa, ya` - Velocity
- `width, height` - Collision box
- `onGround` - Grounded state
- `removed` - Lifecycle flag

**Key Methods:**
- `update(world)` - Update logic (overridden by subclasses)
- `collideCheck(world)` - Handle collisions
- `move(world)` - Apply velocity with collision detection

**Ported from:** `client-java/.../game/sprites/MarioSprite.java`

---

### 5.5 Mario (Player Character)

**Responsibility:** Player physics, actions, power-ups, collision.

**Key Features:**
- **Movement:** Walking, running, jumping
- **Power-ups:** Small, large (mushroom), fire (fire flower)
- **Actions:** Jump (S/Space), run/fire (A/Shift)
- **Collision:** vs enemies (stomp/damage), vs items, vs level
- **Death:** Respawn or game over

**Controls:**
- Arrow keys: Move left/right
- S or Space: Jump
- A or Shift: Run / Fire fireball

**Ported from:** `client-java/.../game/sprites/Mario.java`

---

### 5.6 Enemy Sprites

| Sprite | Behavior | Ported From |
|--------|----------|-------------|
| **Enemy (base)** | Walking, cliff avoidance, stomp/shell mechanics | `Enemy.java` |
| **Shell** | Sliding when kicked, stops when stomped, kills enemies | `Shell.java` |
| **FlowerEnemy** | Piranha plant: moves up/down, waits, emerges when safe | `FlowerEnemy.java` |
| **BulletBill** | Flies straight, not affected by stomping | `BulletBill.java` |

**Enemy Types:**
- Goomba (brown mushroom enemy)
- Red Koopa (red turtle)
- Green Koopa (green turtle)
- Spiky (spiky turtle, can't stomp)
- Flower (piranha plant in pipe)

**Winged Variants:**
- First stomp removes wings
- Second stomp turns into shell (Koopas) or kills (Goombas)

---

### 5.7 Item Sprites

| Sprite | Effect | Ported From |
|--------|--------|-------------|
| **Mushroom** | Power-up to large Mario | `Mushroom.java` |
| **FireFlower** | Power-up to fire Mario | `FireFlower.java` |
| **LifeMushroom** | Extra life | `LifeMushroom.java` |
| **Fireball** | Mario's projectile (fire mode) | `Fireball.java` |

---

### 5.8 Visual Effects

| Effect | Purpose | Trigger |
|--------|---------|---------|
| **BrickEffect** | Brick fragments | Breaking brick block |
| **CoinEffect** | Coin sparkle | Collecting coin |
| **DeathEffect** | Enemy flip and fall | Enemy defeated |
| **DustEffect** | Running dust | Mario running |
| **FireballEffect** | Impact spark | Fireball hits wall/enemy |
| **SquishEffect** | Squish animation | Enemy stomped |

All effects inherit from `MarioEffect` base class.

---

## 6. API Integration

### 6.1 ArenaApiClient

**Responsibility:** HTTP communication with backend.

**Key Methods:**
```typescript
async checkHealth(): Promise<HealthResponse>
async getNextBattle(sessionId: string): Promise<BattleResponse>
async submitVote(request: VoteRequest): Promise<VoteResponse>
async getLeaderboard(): Promise<LeaderboardResponse>
```

**Configuration:**
- Base URL from environment variable `VITE_API_BASE_URL`
- Fallback to `http://localhost:8080` for development

**Error Handling:**
- Network errors throw with descriptive messages
- Non-200 responses throw with server error code

**Ported from:** `client-java/.../api/ArenaApiClient.java`

---

### 6.2 API Types

All TypeScript interfaces match the `arena/v0` protocol:

```typescript
interface BattleResponse {
  protocol_version: string;
  battle: {
    battle_id: string;
    left: LevelData;
    right: LevelData;
    // ...
  };
}

interface VoteRequest {
  battle_id: string;
  session_id: string;
  result: 'LEFT' | 'RIGHT' | 'TIE' | 'SKIP';
  telemetry?: TelemetryData;
}
```

**Defined in:** `src/api/types.ts`

---

## 7. Rendering System

### 7.1 AssetLoader

**Responsibility:** Load and manage sprite sheets.

**Assets:**
- `mariosheet.png` - Mario sprites (16x32 per frame)
- `enemysheet.png` - Enemy sprites (16x16 per frame)
- `mapsheet.png` - Tile sprites (16x16 per tile)
- `firemariosheet.png` - Fire Mario sprites
- `items.png` - Item sprites

**Loading:**
- All assets loaded before game starts
- Error handling with magenta placeholder rectangles
- Promise-based API for async loading

---

### 7.2 Camera

**Responsibility:** Viewport scrolling to follow Mario.

**Behavior:**
- Scrolls right as Mario moves
- Never scrolls left (one-way progression)
- Keeps Mario centered horizontally when possible
- Viewport: 320x240 pixels (scaled to canvas size)

**Ported from:** Java client camera logic

---

### 7.3 TilemapRenderer

**Responsibility:** Draw level tiles (background and foreground).

**Tile Rendering:**
- Each tile is 16x16 pixels
- Two passes: background layer, then foreground layer
- Uses `mapsheet.png` for tile graphics
- Camera offset applied for scrolling

**Ported from:** Java client tilemap rendering

---

### 7.4 SpriteRenderer

**Responsibility:** Draw all sprites (Mario, enemies, items, effects).

**Rendering Details:**
- Sprites positioned by center-bottom coordinate
- Animation frames based on sprite state
- Flip sprites horizontally based on facing direction
- Special cases:
  - Mario: Different sheets for small/large/fire
  - Enemies: Row-based sprite indexing
  - Shells: Type-based sprite selection
  - FlowerEnemy: Vertical position in pipe

**Key Fixes:**
- Enemy Y-offset corrected to `y - spriteHeight`
- FlowerEnemy sprite row changed to 6 (Piranha Plant)
- Shell rendering uses `shellType * 8 + 3` for correct sprite
- Enemy sprite rows aligned with Java `startIndex` values

**Ported from:** Java client sprite rendering

---

## 8. Input System

### 8.1 KeyboardInput

**Responsibility:** Capture keyboard events and map to Mario actions.

**Key Bindings:**

| Key | Action |
|-----|--------|
| Arrow Left | Move left |
| Arrow Right | Move right |
| S or Space or Arrow Up | Jump |
| A or Shift | Run / Fire fireball |

**Implementation:**
- Uses `keydown` and `keyup` events
- Calls `e.preventDefault()` to prevent browser scrolling
- Uses `{ capture: true }` for early event capture
- Maintains action state array matching `MarioActions` enum

**Key Fixes:**
- Added `preventDefault()` for all game keys
- Used capture phase to prevent default browser behavior
- Fixed lifecycle to prevent premature cleanup

**Ported from:** Java client input handling

---

## 9. Battle Flow

### 9.1 BattleFlow Component

**Responsibility:** Orchestrate the complete battle experience.

**Flow Stages:**

1. **Idle:** Waiting for user to click "Next Battle"
2. **Loading:** Fetching battle from backend
3. **Playing Left:** User plays left level
4. **Playing Right:** User plays right level
5. **Voting:** User selects winner (LEFT/RIGHT/TIE/SKIP)
6. **Submitted:** Vote sent, leaderboard displayed

**Layout:**
- Side-by-side level display (horizontal split)
- Active panel highlighted
- Generator names hidden until after vote

**State Management:**
- Tracks completion status for both levels
- Collects telemetry from both GameCanvas instances
- Handles errors and retries

---

### 9.2 GameCanvas Component

**Responsibility:** React wrapper for Canvas element with game loop.

**Lifecycle:**
1. Mount: Create canvas, load assets
2. Assets Loaded: Initialize `MarioGame` and `MarioWorld`
3. Start: Begin game loop, register input handlers
4. Playing: Game loop running at 30 FPS
5. Game Over: Report result to parent (win/lose/timeout)
6. Unmount: Clean up game loop, input handlers

**Props:**
- `levelData: LevelData` - Level to play
- `onGameComplete: (telemetry) => void` - Callback with results
- `active: boolean` - Whether this level is currently being played

**Key Features:**
- Canvas resizing for responsive layout
- Asset loading state management
- Error recovery with placeholders
- Telemetry extraction from game events

---

### 9.3 VotingPanel Component

**Responsibility:** Display vote options and submit vote.

**UI Elements:**
- Four buttons: LEFT, RIGHT, TIE, SKIP
- Level preview info (generator name, visible after vote)
- Submission status (loading, error, success)

**Behavior:**
- Disabled until both levels played (or user chooses SKIP)
- Sends vote + telemetry to backend
- Shows confirmation on success

---

### 9.4 Leaderboard Component

**Responsibility:** Display generator rankings after vote.

**Data:**
- Generator name, rank, rating
- Win/loss/tie counts
- Games played

**Layout:**
- Table sorted by rating (descending)
- Highlight recently changed generators (optional future feature)

---

## 10. Telemetry

### 10.1 Event Collection

The game engine tracks events during gameplay:

| Event Type | Data |
|------------|------|
| `STOMP` | Enemy stomped |
| `KILL` | Enemy killed by fireball/shell |
| `HURT` | Mario hurt by enemy |
| `FIRE` | Fireball fired |
| `JUMP` | Mario jumped |
| `COIN` | Coin collected |
| `MUSHROOM` | Mushroom collected |
| `FLOWER` | Fire flower collected |
| `LIFE` | 1-Up collected |
| `DEATH` | Mario died |
| `WIN` | Level completed |
| `LOSE` | Time ran out / too many deaths |

**Implementation:** `MarioWorld.events[]` array tracks all events.

---

### 10.2 Telemetry Format

```typescript
interface Telemetry {
  played: boolean;
  completed: boolean;
  duration_seconds: number;
  coins_collected: number;
  enemies_killed: number;
  deaths: number;
  jumps: number;
  // ... other metrics
}
```

**Sent with vote submission to backend.**

---

## 11. Configuration

### 11.1 Environment Variables

**`.env` (Default - localhost):**
```bash
VITE_API_BASE_URL=http://localhost:8080
```

**`.env.production` (Production):**
```bash
VITE_API_BASE_URL=https://www.pcg-arena.com
```

**`.env.local` (Gitignored - user overrides):**
```bash
# Example: connect to remote backend during development
VITE_API_BASE_URL=http://34.116.232.204:8080
```

### 11.2 Vite Configuration

**File:** `vite.config.ts`

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000
  }
});
```

### 11.3 TypeScript Configuration

**Files:** `tsconfig.json`, `tsconfig.node.json`

**Key settings:**
- `strict: true` - Full type checking
- `noUnusedLocals: true` - Catch unused variables
- `target: ES2020` - Modern JS features
- `jsx: "react-jsx"` - React 18 JSX transform

---

## 12. Development

### 12.1 Setup

```bash
# Install Node.js 18+ from https://nodejs.org/

# Clone repository
cd pcg-arena/frontend

# Install dependencies
npm install
```

### 12.2 Running Locally

```bash
# Start dev server (connects to localhost:8080 by default)
npm run dev

# Dev server runs at http://localhost:3000
# Hot module replacement enabled
```

**Requirements:**
- Backend running at `http://localhost:8080`
- Or create `.env.local` with custom backend URL

### 12.3 Development Commands

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start dev server with HMR |
| `npm run build` | Production build to `dist/` |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint (if configured) |

### 12.4 Debugging

**Browser DevTools:**
- Console: Game engine logs
- Network: API requests
- Performance: FPS monitoring

**Common Issues:**
1. **Assets not loading:** Check `public/assets/` folder
2. **Backend connection:** Verify `.env` or `.env.local`
3. **Controls not working:** Check browser console for errors
4. **Performance:** Check FPS counter (should be 30 FPS)

---

## 13. Production Build

### 13.1 Building

```bash
# Build for production
npm run build

# Output: dist/ folder with optimized files
```

**Build includes:**
- Minified JS/CSS
- Asset optimization
- Source maps (optional)
- Environment variables from `.env.production`

### 13.2 Testing Production Build

```bash
# Preview production build locally
npm run preview

# Runs at http://localhost:4173 (default)
```

**Verify:**
- ✅ Assets load correctly
- ✅ API connects to production backend
- ✅ Game plays smoothly
- ✅ No console errors

### 13.3 Deployment

**Static Hosting Options:**
1. **Caddy/Nginx on same VM as backend**
2. **Netlify/Vercel** (free tier)
3. **GCP Cloud Storage + CDN**
4. **GitHub Pages**

**Deployment Process (Caddy example):**
```bash
# Build frontend
npm run build

# Copy to web server
scp -r dist/* user@vm:/var/www/pcg-arena/

# Caddy serves from /var/www/pcg-arena/
```

**Caddyfile:**
```
www.pcg-arena.com {
    root * /var/www/pcg-arena
    file_server
    try_files {path} /index.html
}
```

---

## 14. Browser Support

### 14.1 Supported Browsers

| Browser | Minimum Version | Status |
|---------|-----------------|--------|
| Chrome | 90+ | ✅ Fully tested |
| Edge | 90+ | ✅ Fully tested |
| Firefox | 88+ | ✅ Tested |
| Safari | 14+ | ✅ Expected to work |
| Opera | 76+ | ✅ Expected to work |

### 14.2 Required Features

- HTML5 Canvas 2D context
- ES2020 JavaScript features
- Fetch API for HTTP requests
- Local Storage (for session ID)

### 14.3 Known Limitations

- **Mobile:** Not optimized (desktop keyboard required)
- **Older browsers:** No IE11 support
- **Touch:** No touch controls implemented

---

## Appendix A: Key Files Reference

### Core Engine Files

| File | Lines | Purpose |
|------|-------|---------|
| `MarioGame.ts` | ~100 | Game loop manager |
| `MarioWorld.ts` | ~600 | Central game state |
| `MarioLevel.ts` | ~300 | Level parsing |
| `Mario.ts` | ~700 | Player physics |
| `Enemy.ts` | ~300 | Enemy base class |
| `Shell.ts` | ~200 | Shell physics |
| `FlowerEnemy.ts` | ~150 | Piranha plant |

### Rendering Files

| File | Lines | Purpose |
|------|-------|---------|
| `AssetLoader.ts` | ~150 | Asset management |
| `Camera.ts` | ~100 | Viewport scrolling |
| `SpriteRenderer.ts` | ~500 | Sprite drawing |
| `TilemapRenderer.ts` | ~200 | Tile rendering |

### Component Files

| File | Lines | Purpose |
|------|-------|---------|
| `BattleFlow.tsx` | ~400 | Battle orchestration |
| `GameCanvas.tsx` | ~300 | Canvas wrapper |
| `VotingPanel.tsx` | ~150 | Vote submission |
| `Leaderboard.tsx` | ~150 | Generator rankings |

---

## Appendix B: Differences from Java Client

### Intentional Changes

1. **Framework:** Java Swing → React + Canvas
2. **Language:** Java → TypeScript
3. **Layout:** Vertical → Horizontal (side-by-side)
4. **Generator Names:** Always visible → Hidden until vote

### Gameplay Parity

All gameplay mechanics are identical:
- ✅ Physics (gravity, jump, speed)
- ✅ Collision detection
- ✅ Enemy behavior
- ✅ Power-up effects
- ✅ Tile interactions
- ✅ Event tracking

---

## Appendix C: Testing Checklist

### Functional Tests

- [x] Battle fetch works
- [x] Levels render correctly
- [x] Mario moves and jumps
- [x] Enemies spawn and move
- [x] Collisions work (stomp, damage, items)
- [x] Power-ups work (mushroom, flower)
- [x] Level completion detected
- [x] Telemetry collected
- [x] Vote submission works
- [x] Leaderboard updates

### Visual Tests

- [x] Sprite alignment correct
- [x] Camera scrolls smoothly
- [x] Effects render properly
- [x] UI is readable
- [x] Side-by-side layout works

### Input Tests

- [x] Arrow keys work
- [x] S/Space jump works
- [x] A/Shift run/fire works
- [x] Keys don't scroll page
- [x] Input doesn't break on focus loss

### Edge Cases

- [x] Empty levels
- [x] Very short levels
- [x] Very long levels (200+ tiles)
- [x] Levels with many enemies
- [x] Network errors handled
- [x] Asset load failures handled

---

## Appendix D: Performance Notes

### Target Performance

- **FPS:** 30 (game loop)
- **Frame Time:** ~33ms per frame
- **Render Time:** <10ms per frame

### Optimization Techniques

1. **Canvas:** Single canvas, batch draws
2. **Sprites:** Only render visible sprites (camera culling)
3. **Collision:** Spatial partitioning (tile-based)
4. **Assets:** Preload, cache image objects

### Profiling

Use browser Performance tab to identify bottlenecks:
- **Update:** Should be <5ms
- **Render:** Should be <10ms
- **Input:** Should be <1ms

---

**End of Frontend Specification**

**Status:** Complete and operational as of 2025-12-26.  
**Next:** Public deployment to www.pcg-arena.com.

