# PCG Arena — Stage 5 Specification: Research Analytics

**Location:** `docs/stage5-spec.md`  
**Protocol:** `arena/v0`  
**Status:** 📋 PLANNED  
**Purpose:** Enable research-grade data collection and analytics for PCG evaluation

---

## Table of Contents

1. [Overview](#1-overview)
2. [Research Goals](#2-research-goals)
3. [Data Collection Enhancements](#3-data-collection-enhancements)
4. [Database Schema Extensions](#4-database-schema-extensions)
5. [API Endpoints](#5-api-endpoints)
6. [Public Statistics](#6-public-statistics)
7. [Admin Data Export](#7-admin-data-export)
8. [Frontend Enhancements](#8-frontend-enhancements)
9. [Implementation Plan](#9-implementation-plan)
10. [Configuration](#10-configuration)
11. [Privacy Considerations](#11-privacy-considerations)

---

## 1. Overview

### 1.1 Purpose

Stage 5 transforms PCG Arena from a functional evaluation platform into a **research-grade data collection system**. The goal is to collect comprehensive data that enables:

1. **SOTA Generator Comparison** — Statistically rigorous comparison of generators
2. **Engagement Prediction** — Identify features that predict level "fun"
3. **Individual Differences** — Understand if preferences vary by player type
4. **Design Insights** — Actionable guidelines for PCG researchers

### 1.2 Key Additions

| Feature | Description | Visibility |
|---------|-------------|------------|
| **Enhanced Telemetry** | Full event streams, trajectories, death locations | Admin only |
| **Per-Level Statistics** | Aggregate performance metrics per level | Public |
| **Anonymous Player IDs** | Persistent tracking across sessions | System use |
| **Static Level Features** | Structural analysis of level content | Public |
| **Platform Statistics** | Overall platform health metrics | Public |
| **Data Export** | Research dataset download | Admin only |

### 1.3 Design Principles

1. **Collect Everything, Display Aggregates** — Raw data stays private, summaries are public
2. **Privacy-Respecting** — No fingerprinting; localStorage-based ID (user can clear)
3. **Research-Ready** — Data format suitable for academic publication
4. **Non-Breaking** — All changes are additive; existing API unchanged

---

## 2. Research Goals

### 2.1 Primary Research Questions

| ID | Question | Data Required |
|----|----------|---------------|
| **RQ1** | How do SOTA generators compare empirically? | Per-generator win rates, confidence intervals |
| **RQ2** | What features predict level engagement? | Telemetry, tags, level features, ratings |
| **RQ3** | Is "fun" universal or individual? | Player preference patterns, clustering |
| **RQ4** | What difficulty level maximizes engagement? | Death rates, completion rates, ratings |

### 2.2 Testable Hypotheses

| ID | Hypothesis | Measurement |
|----|------------|-------------|
| **H1** | Moderate difficulty (15-40% death rate) maximizes ratings | Correlate death_rate with win_rate |
| **H2** | Path variability correlates with higher ratings | Position variance vs. win_rate |
| **H3** | Different players prefer different generators | Cluster analysis on voting patterns |
| **H4** | Tags can be predicted from telemetry | ML model: telemetry → tags |
| **H5** | Generators produce levels with signature patterns | Feature distribution by generator |

### 2.3 Publication Metrics

With this data, a research paper can report:

- **N generators** compared with **M total battles**
- **Statistical significance** via confidence intervals (Glicko-2 RD)
- **Effect sizes** for engagement predictors
- **Clustering results** for player preference types
- **Heatmaps** showing aggregate death/exploration patterns

---

## 3. Data Collection Enhancements

### 3.1 Enhanced Telemetry Schema

**Current telemetry (limited):**
```typescript
interface LevelTelemetry {
  played: boolean;
  duration_seconds: number;
  completed: boolean;
  deaths: number;
  coins_collected: number;
  powerups_collected?: number;  // Always 0
  enemies_killed?: number;      // Always 0
}
```

**Enhanced telemetry (Stage 5):**
```typescript
interface EnhancedLevelTelemetry {
  // Basic stats (existing)
  played: boolean;
  duration_seconds: number;
  completed: boolean;
  
  // Accurate counts from events (NEW - fix hardcoded values)
  deaths: number;
  coins_collected: number;
  enemies_stomped: number;
  enemies_fire_killed: number;
  enemies_shell_killed: number;
  powerups_mushroom: number;
  powerups_flower: number;
  lives_collected: number;
  jumps: number;
  
  // Position trajectory (NEW - sampled every 15 ticks / 0.5s)
  trajectory: Array<{
    tick: number;      // Game tick (0, 15, 30, ...)
    x: number;         // Mario X position
    y: number;         // Mario Y position
    state: number;     // 0=small, 1=large, 2=fire
  }>;
  
  // Death locations (NEW)
  death_locations: Array<{
    x: number;
    y: number;
    tick: number;
    cause: 'enemy' | 'fall' | 'timeout';
  }>;
  
  // Full event stream (NEW - optional, for detailed analysis)
  events: Array<{
    type: string;      // EventType enum value
    param: number;     // Event-specific parameter
    x: number;         // Mario X at event
    y: number;         // Mario Y at event
    tick: number;      // Game tick
  }>;
  
  // Level identification (NEW)
  level_id: string;
}
```

### 3.2 Anonymous Persistent Player IDs

**Implementation: localStorage + Cookie Fallback**

```typescript
// frontend/src/utils/playerId.ts

const STORAGE_KEY = 'pcg_arena_player_id';
const COOKIE_NAME = 'pcg_arena_player_id';

export function getOrCreatePlayerId(): string {
  // Try localStorage first
  let playerId = localStorage.getItem(STORAGE_KEY);
  
  if (!playerId) {
    // Fallback to cookie
    playerId = getCookie(COOKIE_NAME);
  }
  
  if (!playerId) {
    // Generate new ID with 'anon_' prefix
    playerId = `anon_${crypto.randomUUID()}`;
    
    // Store in both for redundancy
    localStorage.setItem(STORAGE_KEY, playerId);
    setCookie(COOKIE_NAME, playerId, 365); // 1 year
  }
  
  return playerId;
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
}

function setCookie(name: string, value: string, days: number): void {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${value}; expires=${expires}; path=/; SameSite=Lax`;
}
```

**Properties:**
- Persists across browser sessions
- User can clear by deleting localStorage/cookies
- Prefix `anon_` distinguishes from authenticated user IDs
- Links to authenticated user if they later log in

### 3.3 Event Extraction from Game Engine

**Current gap:** Events are tracked in `MarioWorld.lastFrameEvents` but not extracted.

**Fix in GameCanvas.tsx:**

```typescript
// Extract telemetry from MarioWorld
function extractTelemetry(world: MarioWorld): EnhancedLevelTelemetry {
  const events = world.getAllEvents(); // NEW: Accumulator for all events
  
  return {
    played: true,
    duration_seconds: world.currentTick / 30, // 30 FPS
    completed: world.gameStatus === GameStatus.WIN,
    deaths: countEvents(events, EventType.HURT),
    coins_collected: world.coins,
    enemies_stomped: countEvents(events, EventType.STOMP_KILL),
    enemies_fire_killed: countEvents(events, EventType.FIRE_KILL),
    enemies_shell_killed: countEvents(events, EventType.SHELL_KILL),
    powerups_mushroom: countEvents(events, EventType.COLLECT, /* param= */ 0),
    powerups_flower: countEvents(events, EventType.COLLECT, /* param= */ 1),
    lives_collected: countEvents(events, EventType.COLLECT, /* param= */ 2),
    jumps: countEvents(events, EventType.JUMP),
    trajectory: world.positionHistory, // NEW: Sampled positions
    death_locations: world.deathLocations, // NEW: Death positions
    events: events.map(e => ({
      type: EventType[e.eventType],
      param: e.eventParam,
      x: e.marioX,
      y: e.marioY,
      tick: e.tick
    })),
    level_id: world.levelId // NEW: Track which level
  };
}
```

---

## 4. Database Schema Extensions

### 4.1 New Tables

#### `level_stats` — Per-Level Aggregate Statistics

```sql
-- Migration: 012_level_stats.sql

CREATE TABLE IF NOT EXISTS level_stats (
    level_id TEXT PRIMARY KEY,
    generator_id TEXT NOT NULL,
    
    -- Battle outcomes
    times_shown INTEGER DEFAULT 0,
    times_won INTEGER DEFAULT 0,
    times_lost INTEGER DEFAULT 0,
    times_tied INTEGER DEFAULT 0,
    times_skipped INTEGER DEFAULT 0,
    
    -- Gameplay metrics
    times_completed INTEGER DEFAULT 0,
    total_deaths INTEGER DEFAULT 0,
    total_play_time_seconds REAL DEFAULT 0,
    
    -- Computed averages
    win_rate REAL,                    -- wins / (wins + losses)
    completion_rate REAL,             -- completed / shown
    avg_deaths REAL,                  -- total_deaths / shown
    avg_duration_seconds REAL,        -- total_play_time / shown
    
    -- Tag counts
    tag_fun INTEGER DEFAULT 0,
    tag_boring INTEGER DEFAULT 0,
    tag_too_hard INTEGER DEFAULT 0,
    tag_too_easy INTEGER DEFAULT 0,
    tag_creative INTEGER DEFAULT 0,
    tag_good_flow INTEGER DEFAULT 0,
    tag_unfair INTEGER DEFAULT 0,
    tag_confusing INTEGER DEFAULT 0,
    tag_not_mario_like INTEGER DEFAULT 0,
    
    -- Difficulty classification (computed)
    difficulty_score REAL,            -- Normalized 0-1 based on deaths/completion
    
    updated_at_utc TEXT NOT NULL,
    
    FOREIGN KEY (level_id) REFERENCES levels(level_id),
    FOREIGN KEY (generator_id) REFERENCES generators(generator_id)
);

CREATE INDEX IF NOT EXISTS idx_level_stats_generator 
ON level_stats(generator_id);

CREATE INDEX IF NOT EXISTS idx_level_stats_win_rate 
ON level_stats(win_rate DESC);
```

#### `player_profiles` — Anonymous Player Tracking

```sql
-- Migration: 013_player_profiles.sql

CREATE TABLE IF NOT EXISTS player_profiles (
    player_id TEXT PRIMARY KEY,           -- 'anon_uuid' or 'u_uuid' for linked accounts
    
    -- Activity tracking
    first_seen_utc TEXT NOT NULL,
    last_seen_utc TEXT NOT NULL,
    total_battles INTEGER DEFAULT 0,
    total_votes INTEGER DEFAULT 0,
    
    -- Session info
    total_sessions INTEGER DEFAULT 1,
    avg_battles_per_session REAL,
    
    -- Skill estimation (optional: Glicko-2 for players)
    skill_rating REAL DEFAULT 1000.0,
    skill_rd REAL DEFAULT 350.0,
    
    -- Preference patterns (updated by triggers or batch job)
    prefers_harder_count INTEGER DEFAULT 0,   -- Voted for level with more deaths
    prefers_easier_count INTEGER DEFAULT 0,   -- Voted for level with fewer deaths
    prefers_longer_count INTEGER DEFAULT 0,   -- Voted for longer levels
    prefers_shorter_count INTEGER DEFAULT 0,  -- Voted for shorter levels
    
    -- Account linking
    linked_user_id TEXT,                      -- NULL or FK to users.user_id
    
    FOREIGN KEY (linked_user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS player_sessions (
    session_id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    started_at_utc TEXT NOT NULL,
    last_activity_utc TEXT NOT NULL,
    battles_completed INTEGER DEFAULT 0,
    user_agent TEXT,
    ip_hash TEXT,                             -- SHA256 of IP for rate limiting, not tracking
    
    FOREIGN KEY (player_id) REFERENCES player_profiles(player_id)
);

CREATE INDEX IF NOT EXISTS idx_player_sessions_player 
ON player_sessions(player_id);
```

#### `play_trajectories` — Detailed Position Data

```sql
-- Migration: 014_trajectories.sql

CREATE TABLE IF NOT EXISTS play_trajectories (
    trajectory_id TEXT PRIMARY KEY,
    vote_id TEXT NOT NULL,
    level_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    player_id TEXT,
    side TEXT NOT NULL CHECK (side IN ('left', 'right')),
    
    -- Compressed trajectory data
    trajectory_json TEXT NOT NULL,        -- Array of {tick, x, y, state}
    death_locations_json TEXT,            -- Array of {x, y, tick, cause}
    events_json TEXT,                     -- Full event stream (optional)
    
    -- Summary stats for quick queries
    duration_ticks INTEGER,
    max_x_reached REAL,
    death_count INTEGER,
    
    created_at_utc TEXT NOT NULL,
    
    FOREIGN KEY (vote_id) REFERENCES votes(vote_id),
    FOREIGN KEY (level_id) REFERENCES levels(level_id),
    FOREIGN KEY (player_id) REFERENCES player_profiles(player_id)
);

CREATE INDEX IF NOT EXISTS idx_trajectories_level 
ON play_trajectories(level_id);

CREATE INDEX IF NOT EXISTS idx_trajectories_player 
ON play_trajectories(player_id);
```

#### `level_features` — Static Level Analysis

```sql
-- Migration: 015_level_features.sql

CREATE TABLE IF NOT EXISTS level_features (
    level_id TEXT PRIMARY KEY,
    
    -- Dimensions
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    
    -- Tile counts
    ground_tiles INTEGER DEFAULT 0,
    platform_tiles INTEGER DEFAULT 0,
    pipe_tiles INTEGER DEFAULT 0,
    coin_tiles INTEGER DEFAULT 0,
    question_block_tiles INTEGER DEFAULT 0,
    brick_tiles INTEGER DEFAULT 0,
    empty_tiles INTEGER DEFAULT 0,
    
    -- Enemy counts (parsed from level)
    enemy_goomba INTEGER DEFAULT 0,
    enemy_koopa_red INTEGER DEFAULT 0,
    enemy_koopa_green INTEGER DEFAULT 0,
    enemy_spiky INTEGER DEFAULT 0,
    enemy_piranha INTEGER DEFAULT 0,
    enemy_bullet_bill INTEGER DEFAULT 0,
    enemy_total INTEGER DEFAULT 0,
    
    -- Structural metrics
    gap_count INTEGER DEFAULT 0,          -- Number of gaps (sequences of empty ground)
    max_gap_width INTEGER DEFAULT 0,      -- Widest gap
    platform_count INTEGER DEFAULT 0,     -- Distinct platforms
    avg_platform_height REAL,             -- Average height of platforms
    height_variance REAL,                 -- Variance in platform heights
    
    -- Computed complexity scores (0-1 normalized)
    enemy_density REAL,                   -- enemies / width
    coin_density REAL,                    -- coins / width
    gap_density REAL,                     -- gap_tiles / width
    structural_complexity REAL,           -- Combined metric
    
    -- Leniency score (higher = easier)
    leniency_score REAL,
    
    computed_at_utc TEXT NOT NULL,
    
    FOREIGN KEY (level_id) REFERENCES levels(level_id)
);
```

### 4.2 Modified Tables

#### `votes` — Add player_id column

```sql
-- Migration: 016_vote_player_id.sql

ALTER TABLE votes ADD COLUMN player_id TEXT;

CREATE INDEX IF NOT EXISTS idx_votes_player 
ON votes(player_id);
```

---

## 5. API Endpoints

### 5.1 Public Statistics Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/v1/stats/platform` | Platform-wide statistics | Public |
| `GET` | `/v1/stats/generators` | Enhanced generator stats | Public |
| `GET` | `/v1/stats/levels/{level_id}` | Per-level statistics | Public |
| `GET` | `/v1/stats/level/{level_id}/heatmap` | Aggregate death heatmap | Public |

#### GET /v1/stats/platform

Returns platform-wide aggregate statistics.

**Response 200:**
```json
{
  "protocol_version": "arena/v0",
  "updated_at_utc": "2025-12-30T12:00:00Z",
  
  "totals": {
    "battles_completed": 12456,
    "votes_cast": 12456,
    "unique_players": 2341,
    "active_generators": 15,
    "total_levels": 1250
  },
  
  "vote_distribution": {
    "left_percent": 38.2,
    "right_percent": 35.1,
    "tie_percent": 17.8,
    "skip_percent": 8.9
  },
  
  "engagement": {
    "avg_battles_per_player": 5.3,
    "avg_session_length_battles": 3.2,
    "completion_rate_percent": 67.4,
    "avg_deaths_per_level": 2.3,
    "avg_duration_seconds": 47.2
  },
  
  "activity": {
    "battles_last_24h": 234,
    "battles_last_7d": 1456,
    "peak_hour_utc": 18
  }
}
```

#### GET /v1/stats/generators

Returns enhanced statistics for all generators (extends leaderboard).

**Response 200:**
```json
{
  "protocol_version": "arena/v0",
  "updated_at_utc": "2025-12-30T12:00:00Z",
  "generators": [
    {
      "generator_id": "hopper",
      "name": "Hopper Level Generator",
      "version": "1.0.0",
      
      "rating": {
        "value": 1124.5,
        "rd": 45.2,
        "confidence_95_low": 1035.9,
        "confidence_95_high": 1213.1
      },
      
      "record": {
        "games_played": 847,
        "wins": 412,
        "losses": 298,
        "ties": 102,
        "skips": 35,
        "win_rate_percent": 58.1
      },
      
      "engagement": {
        "avg_completion_rate": 0.72,
        "avg_deaths": 1.8,
        "avg_duration_seconds": 42.3
      },
      
      "consistency": {
        "level_win_rate_std": 0.15,
        "level_count": 100
      },
      
      "top_tags": [
        {"tag": "fun", "count": 234},
        {"tag": "creative", "count": 156},
        {"tag": "good_flow", "count": 98}
      ]
    }
  ]
}
```

#### GET /v1/stats/levels/{level_id}

Returns detailed statistics for a specific level.

**Response 200:**
```json
{
  "protocol_version": "arena/v0",
  "level_id": "hopper::lvl-42.txt",
  "generator_id": "hopper",
  
  "performance": {
    "times_shown": 47,
    "win_rate": 0.67,
    "completion_rate": 0.89,
    "avg_deaths": 1.2,
    "avg_duration_seconds": 38.4
  },
  
  "outcomes": {
    "wins": 28,
    "losses": 14,
    "ties": 3,
    "skips": 2
  },
  
  "tags": {
    "fun": 12,
    "creative": 8,
    "good_flow": 6,
    "too_easy": 2,
    "total": 28
  },
  
  "difficulty": {
    "score": 0.32,
    "classification": "easy"
  },
  
  "features": {
    "width": 200,
    "enemy_count": 8,
    "gap_count": 5,
    "coin_count": 24,
    "enemy_density": 0.04,
    "leniency_score": 0.72
  }
}
```

#### GET /v1/stats/levels/{level_id}/heatmap

Returns aggregate position and death data for heatmap visualization.

**Response 200:**
```json
{
  "protocol_version": "arena/v0",
  "level_id": "hopper::lvl-42.txt",
  "sample_count": 47,
  
  "death_heatmap": {
    "tile_size": 16,
    "data": [
      {"tile_x": 12, "count": 3},
      {"tile_x": 45, "count": 8},
      {"tile_x": 89, "count": 12}
    ],
    "max_count": 12
  },
  
  "position_heatmap": {
    "tile_size": 16,
    "data": [
      {"tile_x": 0, "tile_y": 13, "density": 0.95},
      {"tile_x": 1, "tile_y": 13, "density": 0.92}
    ]
  },
  
  "progress_distribution": {
    "buckets": [0, 25, 50, 75, 100],
    "counts": [5, 8, 12, 15, 47]
  }
}
```

### 5.2 Admin-Only Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/v1/admin/export/votes` | Export all votes with telemetry | Admin |
| `GET` | `/v1/admin/export/trajectories` | Export trajectory data | Admin |
| `GET` | `/v1/admin/export/players` | Export player profiles | Admin |
| `GET` | `/v1/admin/export/level-stats` | Export level statistics | Admin |
| `GET` | `/v1/admin/export/dataset` | Full research dataset | Admin |

#### GET /v1/admin/export/dataset

Exports complete research dataset as ZIP or JSON.

**Query Parameters:**
- `format`: `json` (default) or `csv`
- `include`: Comma-separated list: `votes,trajectories,players,levels,generators,features`

**Response 200:** ZIP file or JSON depending on format

**Response Headers:**
```
Content-Type: application/zip
Content-Disposition: attachment; filename="pcg-arena-dataset-2025-12-30.zip"
```

---

## 6. Public Statistics

### 6.1 Platform Statistics Page

New page at `/stats` showing platform-wide metrics.

**Sections:**
1. **Overview Cards** — Total battles, players, generators
2. **Vote Distribution Chart** — Pie chart of LEFT/RIGHT/TIE/SKIP
3. **Engagement Metrics** — Completion rate, avg deaths, avg duration
4. **Activity Graph** — Battles over time (last 30 days)

### 6.2 Enhanced Generator Page

Extend `/generator/{id}` with detailed statistics:

**Current sections:**
- Generator info (name, description, tags)
- Level gallery with previews

**New sections:**
- **Performance Overview** — Win rate, completion rate, avg deaths
- **Rating Trend** — Graph of rating over time (if we track history)
- **Tag Distribution** — Bar chart of tag counts
- **Difficulty Distribution** — Histogram of level difficulties

### 6.3 Level Detail Page (NEW)

New page at `/level/{id}` for deep dive into a specific level.

**Sections:**
1. **Level Preview** — Full-width level visualization
2. **Performance Metrics** — Win rate, completion rate, deaths, duration
3. **Tag Distribution** — Bar chart of tags
4. **Death Heatmap** — Overlay on level preview showing death locations
5. **Structural Features** — Enemy count, gaps, coins, etc.

**UI Mockup:**
```
╔═══════════════════════════════════════════════════════════════════════════╗
║  LEVEL: hopper::lvl-42.txt                                                 ║
║  Generator: Hopper v1.0                                    [Back to Gen]   ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  ┌──────────────────────────────────────────────────────────────────────┐ ║
║  │                    [LEVEL PREVIEW - FULL WIDTH]                       │ ║
║  │     Toggle: [Tiles] [Deaths] [Heatmap]                                │ ║
║  │     🔴 = Death locations (size = frequency)                           │ ║
║  └──────────────────────────────────────────────────────────────────────┘ ║
║                                                                            ║
║  ┌───────────────────────────┐  ┌───────────────────────────────────────┐ ║
║  │ PERFORMANCE               │  │ TAG DISTRIBUTION                      │ ║
║  │ ─────────────────         │  │ ─────────────────                     │ ║
║  │ Shown:      47 times      │  │ fun        ████████████ 12            │ ║
║  │ Win Rate:   67%           │  │ creative   ████████ 8                 │ ║
║  │ Completion: 89%           │  │ good_flow  ██████ 6                   │ ║
║  │ Avg Deaths: 1.2           │  │ too_easy   ██ 2                       │ ║
║  │ Avg Time:   38s           │  │                                       │ ║
║  │ ─────────────────         │  │ Total: 28 tags                        │ ║
║  │ Difficulty: ★★☆☆☆ Easy    │  │ Sentiment: 78% Positive               │ ║
║  └───────────────────────────┘  └───────────────────────────────────────┘ ║
║                                                                            ║
║  ┌──────────────────────────────────────────────────────────────────────┐ ║
║  │ STRUCTURE                                                             │ ║
║  │ ───────────                                                           │ ║
║  │ Width: 200  │ Gaps: 5  │ Enemies: 8  │ Coins: 24  │ Pipes: 3         │ ║
║  │ Enemy Density: 0.04  │ Leniency: 0.72                                │ ║
║  └──────────────────────────────────────────────────────────────────────┘ ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### 6.4 Enhanced Generator Level Gallery

Update level cards on Generator Page to show stats:

```
┌─────────────────────┐
│ [Level Preview]     │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│                     │
│ lvl-42.txt          │
│ ────────────────    │
│ 🏆 67% win rate     │
│ ✓ 89% completion    │
│ 💀 1.2 avg deaths   │
│ ⏱ 38s avg time      │
│ ────────────────    │
│ Tags: fun (12)      │
│       creative (8)  │
│ ────────────────    │
│ [View Details]      │
└─────────────────────┘
```

**Sorting options:**
- Win Rate (high to low)
- Difficulty (easy to hard)
- Times Played (most to least)
- Newest First

---

## 7. Admin Data Export

### 7.1 Export Interface

Add to Admin Dashboard (`/admin`) a new "Data Export" tab:

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  ADMIN: DATA EXPORT                                                        ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  ⚠️  Raw data exports are for research purposes only.                      ║
║      Do not share until paper publication.                                 ║
║                                                                            ║
║  ┌────────────────────────────────────────────────────────────────────┐   ║
║  │ SELECT DATA                                                         │   ║
║  │                                                                     │   ║
║  │ ☑ votes.csv           All votes with telemetry (12,456 rows)       │   ║
║  │ ☑ battles.csv         All battles (12,456 rows)                    │   ║
║  │ ☑ trajectories.json   Position data (2.3M points, 45MB)            │   ║
║  │ ☑ player_profiles.csv Anonymous player data (2,341 rows)           │   ║
║  │ ☑ level_stats.csv     Per-level aggregates (1,250 rows)            │   ║
║  │ ☑ level_features.csv  Structural analysis (1,250 rows)             │   ║
║  │ ☑ generators.csv      Generator metadata (15 rows)                 │   ║
║  │ ☐ levels.csv          Level tilemaps (1,250 rows, 25MB)            │   ║
║  │                                                                     │   ║
║  │ Format: [JSON ▼]  [CSV]  [ZIP Bundle]                              │   ║
║  │                                                                     │   ║
║  │ Date Range: [All Time ▼]  [Last 30 Days]  [Custom...]              │   ║
║  │                                                                     │   ║
║  │                              [DOWNLOAD]                             │   ║
║  └────────────────────────────────────────────────────────────────────┘   ║
║                                                                            ║
║  Export History:                                                           ║
║  • 2025-12-30 14:32 — Full dataset (156MB) by admin@example.com           ║
║  • 2025-12-28 09:15 — Votes only (2.3MB) by admin@example.com             ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### 7.2 Export Format

**votes.csv:**
```csv
vote_id,battle_id,session_id,player_id,result,left_level_id,right_level_id,left_generator_id,right_generator_id,left_tags,right_tags,left_duration,left_completed,left_deaths,right_duration,right_completed,right_deaths,created_at_utc
v_abc123,btl_xyz789,sess_001,anon_uuid1,LEFT,hopper::lvl-1,genetic::lvl-5,hopper,genetic,"fun,creative","too_hard",42.3,true,1,67.8,false,4,2025-12-30T10:00:00Z
```

**trajectories.json:**
```json
{
  "metadata": {
    "exported_at": "2025-12-30T12:00:00Z",
    "total_trajectories": 24912
  },
  "trajectories": [
    {
      "trajectory_id": "traj_001",
      "vote_id": "v_abc123",
      "level_id": "hopper::lvl-1",
      "side": "left",
      "duration_ticks": 1269,
      "points": [
        {"t": 0, "x": 32, "y": 208, "s": 0},
        {"t": 15, "x": 48, "y": 208, "s": 0}
      ],
      "deaths": [
        {"x": 456, "y": 112, "t": 890, "cause": "enemy"}
      ]
    }
  ]
}
```

---

## 8. Frontend Enhancements

### 8.1 New Components

| Component | Path | Description |
|-----------|------|-------------|
| `StatsPage` | `pages/StatsPage.tsx` | Platform statistics page |
| `LevelDetailPage` | `pages/LevelDetailPage.tsx` | Individual level analysis |
| `DeathHeatmap` | `components/DeathHeatmap.tsx` | Heatmap overlay on level |
| `StatsCard` | `components/StatsCard.tsx` | Reusable statistics card |
| `TagChart` | `components/TagChart.tsx` | Tag distribution bar chart |
| `AdminExport` | `components/AdminExport.tsx` | Data export interface |

### 8.2 Modified Components

| Component | Changes |
|-----------|---------|
| `BattleFlow.tsx` | Add player_id to vote submission |
| `GameCanvas.tsx` | Extract enhanced telemetry from MarioWorld |
| `GeneratorPage.tsx` | Add statistics section, level sorting |
| `LevelPreview.tsx` | Add optional stats overlay |
| `AdminPage.tsx` | Add "Data Export" tab |

### 8.3 Engine Modifications

| File | Changes |
|------|---------|
| `MarioWorld.ts` | Add position sampling (every 15 ticks) |
| `MarioWorld.ts` | Accumulate all events (not just last frame) |
| `MarioWorld.ts` | Track death causes (enemy/fall/timeout) |
| `MarioGame.ts` | Pass level_id to MarioWorld |

### 8.4 New Routes

| Route | Component | Description |
|-------|-----------|-------------|
| `/stats` | `StatsPage` | Platform statistics |
| `/level/:id` | `LevelDetailPage` | Level detail page |

### 8.5 Navigation Update

```
[Play] [Leaderboard] [Statistics] [Builder Profile]
                        ^--- NEW
```

---

## 9. Implementation Plan

### 9.1 Phase Breakdown

| Phase | Description | Duration | Dependencies |
|-------|-------------|----------|--------------|
| **Phase 1** | Database migrations | 1 day | None |
| **Phase 2** | Enhanced telemetry collection | 2 days | Phase 1 |
| **Phase 3** | Player ID system | 1 day | Phase 1 |
| **Phase 4** | Per-level stats computation | 2 days | Phase 2 |
| **Phase 5** | Static level feature extraction | 1 day | Phase 1 |
| **Phase 6** | Public statistics API | 2 days | Phase 4, 5 |
| **Phase 7** | Admin export API | 1 day | Phase 4 |
| **Phase 8** | Frontend stats pages | 3 days | Phase 6 |
| **Phase 9** | Level detail + heatmaps | 2 days | Phase 6 |
| **Phase 10** | Admin export UI | 1 day | Phase 7 |
| **Phase 11** | Testing and polish | 2 days | All |

**Total: ~18 days**

### 9.2 Phase 1: Database Migrations

**Tasks:**
1. Create `012_level_stats.sql`
2. Create `013_player_profiles.sql`
3. Create `014_trajectories.sql`
4. Create `015_level_features.sql`
5. Create `016_vote_player_id.sql`
6. Test migration on fresh database
7. Test migration on existing database

### 9.3 Phase 2: Enhanced Telemetry

**Tasks:**
1. Add `positionHistory` array to MarioWorld
2. Add position sampling every 15 ticks
3. Add `deathLocations` array with cause tracking
4. Add `allEvents` accumulator (not just lastFrameEvents)
5. Update GameResult interface
6. Update GameCanvas to extract enhanced telemetry
7. Update BattleFlow to send enhanced telemetry
8. Update backend to store trajectory data

### 9.4 Phase 3: Player ID System

**Tasks:**
1. Create `playerId.ts` utility
2. Integrate player ID into BattleFlow
3. Send player_id with battle requests
4. Send player_id with vote submissions
5. Create/update player_profiles on backend
6. Link to user account if authenticated

### 9.5 Phase 4: Per-Level Stats

**Tasks:**
1. Create `update_level_stats()` function in backend
2. Call on vote submission (atomic with vote insert)
3. Compute derived metrics (win_rate, etc.)
4. Backfill existing data

### 9.6 Phase 5: Level Feature Extraction

**Tasks:**
1. Create `extract_level_features()` function
2. Parse tilemap for tile counts
3. Detect gaps and platforms
4. Count enemies by type
5. Compute complexity scores
6. Run on seed import
7. Backfill existing levels

### 9.7 Phase 6-10: API and Frontend

See detailed task lists in code comments.

---

## 10. Configuration

### 10.1 New Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ARENA_TRAJECTORY_SAMPLE_INTERVAL` | `15` | Ticks between position samples |
| `ARENA_STORE_FULL_EVENTS` | `true` | Store complete event stream |
| `ARENA_MAX_TRAJECTORY_POINTS` | `1000` | Max points per trajectory |
| `ARENA_EXPORT_RATE_LIMIT` | `5/hour` | Admin export rate limit |

### 10.2 Feature Flags

```python
# In config.py
collect_trajectories: bool = True      # Enable trajectory collection
collect_full_events: bool = True       # Store complete event stream
compute_level_features: bool = True    # Auto-compute on level import
public_stats_enabled: bool = True      # Enable /v1/stats/* endpoints
```

---

## 11. Privacy Considerations

### 11.1 Data Minimization

- **No IP addresses stored** — Only hashed for rate limiting
- **No device fingerprinting** — Only localStorage ID (clearable)
- **No PII in trajectories** — Just game positions

### 11.2 Player Control

- Players can clear localStorage to get new anonymous ID
- Authenticated users can request data deletion (future)
- No tracking across devices (localStorage is local)

### 11.3 Research Ethics

For publication, consider:
- IRB approval may be needed for human subjects research
- Anonymization of any published dataset
- Aggregate statistics only in paper (no individual trajectories)

### 11.4 Data Retention

- Trajectories: Keep indefinitely (research value)
- Player profiles: Keep indefinitely (anonymous)
- Consider GDPR compliance if EU users participate

---

## 12. Success Criteria

### 12.1 Data Collection

| Criterion | Target |
|-----------|--------|
| Trajectory capture rate | >95% of plays |
| Event capture accuracy | 100% match with game state |
| Player ID persistence | >80% returning players identified |
| Level feature coverage | 100% of levels analyzed |

### 12.2 Public Statistics

| Criterion | Target |
|-----------|--------|
| Stats page load time | <2 seconds |
| Level detail page load | <3 seconds |
| Heatmap render time | <1 second |
| Data freshness | <5 minute lag |

### 12.3 Research Utility

| Criterion | Target |
|-----------|--------|
| Export completeness | All data types available |
| Export format | Standard CSV/JSON |
| Dataset size | Manageable (<500MB) |
| Documentation | Codebook for all fields |

---

## 13. File Changes Summary

### New Files

| File | Description |
|------|-------------|
| `db/migrations/012_level_stats.sql` | Level statistics table |
| `db/migrations/013_player_profiles.sql` | Player tracking tables |
| `db/migrations/014_trajectories.sql` | Trajectory storage |
| `db/migrations/015_level_features.sql` | Static level analysis |
| `db/migrations/016_vote_player_id.sql` | Add player_id to votes |
| `backend/src/stats.py` | Statistics computation module |
| `backend/src/features.py` | Level feature extraction |
| `backend/src/export.py` | Data export module |
| `frontend/src/utils/playerId.ts` | Player ID management |
| `frontend/src/pages/StatsPage.tsx` | Platform statistics |
| `frontend/src/pages/LevelDetailPage.tsx` | Level analysis page |
| `frontend/src/components/DeathHeatmap.tsx` | Heatmap visualization |
| `frontend/src/components/TagChart.tsx` | Tag distribution chart |
| `frontend/src/styles/stats.css` | Statistics page styles |
| `docs/stage5-spec.md` | This specification |

### Modified Files

| File | Changes |
|------|---------|
| `frontend/src/engine/MarioWorld.ts` | Position sampling, event accumulation |
| `frontend/src/components/GameCanvas.tsx` | Enhanced telemetry extraction |
| `frontend/src/components/BattleFlow.tsx` | Player ID, enhanced telemetry |
| `frontend/src/api/types.ts` | New telemetry interfaces |
| `frontend/src/api/client.ts` | Stats endpoints |
| `frontend/src/pages/GeneratorPage.tsx` | Level stats, sorting |
| `frontend/src/pages/AdminPage.tsx` | Data export tab |
| `frontend/src/App.tsx` | New routes |
| `backend/src/main.py` | Stats and export endpoints |
| `backend/src/config.py` | New configuration options |

---

## Appendix A: Telemetry Data Dictionary

| Field | Type | Description |
|-------|------|-------------|
| `trajectory.tick` | int | Game tick (30 ticks = 1 second) |
| `trajectory.x` | float | Mario X position (pixels) |
| `trajectory.y` | float | Mario Y position (pixels) |
| `trajectory.state` | int | 0=small, 1=large, 2=fire |
| `death.cause` | string | 'enemy', 'fall', 'timeout' |
| `event.type` | string | EventType enum name |
| `event.param` | int | Event-specific parameter |

---

## Appendix B: Level Feature Definitions

| Feature | Formula | Range |
|---------|---------|-------|
| `enemy_density` | enemy_count / width | 0.0 - 1.0 |
| `gap_density` | gap_tiles / width | 0.0 - 1.0 |
| `leniency_score` | 1 - (enemy_density + gap_density * 0.5) | 0.0 - 1.0 |
| `difficulty_score` | 1 - completion_rate | 0.0 - 1.0 |

---

## Appendix C: Research Dataset Schema

When exporting for publication, the dataset should include:

1. **README.txt** — Dataset description and citation
2. **codebook.csv** — Field definitions for all tables
3. **generators.csv** — Generator metadata
4. **levels.csv** — Level metadata (optional: tilemaps)
5. **level_features.csv** — Structural analysis
6. **level_stats.csv** — Aggregate performance
7. **votes.csv** — All votes with telemetry summary
8. **trajectories.json** — Position data (large, optional)

---

**End of Stage 5 Specification**

**Status:** 📋 PLANNED  
**Priority:** HIGH (implement before public launch)  
**Estimated Duration:** ~18 days

