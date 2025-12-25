# PCG Arena Java Client - Phase 2

**Version:** 0.2.0  
**Protocol:** arena/v0  
**Status:** Phase 2 Implementation Complete

## Overview

This is a Java desktop client for the PCG Arena system. Phase 2 implements full gameplay integration that allows you to:

- **Play** two procedurally generated levels sequentially
- Experience full Mario gameplay mechanics (jump, run, enemies, powerups)
- Vote on which level is better (TOP/BOTTOM/TIE/SKIP)
- Tag levels with descriptive labels
- View the leaderboard and rating changes
- Submit rich telemetry data for research

## Requirements

- Java 11 or later
- Backend running at `http://localhost:8080` (or configured URL)

## Quick Start

### 1. Start the Backend

From the project root:

```bash
cd ..
docker compose up --build
```

Wait for the backend to start and show "Application startup complete".

### 2. Run the Client

From the `client-java` directory:

**On Linux/Mac:**
```bash
./gradlew run
```

**On Windows:**
```cmd
gradlew.bat run
```

The application window will open automatically.

### 3. Use the Client (Phase 2)

1. The client performs a health check on startup
2. Click **"Next Battle"** to fetch a battle
3. **Play Top Level**:
   - Press **SPACE** in the top panel to start
   - Use Arrow Keys to move, **S** to jump, **A** to run/fire
   - Play until you win, die, or time runs out
4. **Play Bottom Level**:
   - Press **SPACE** in the bottom panel to start
   - Play the second level with the same controls
5. **Vote**: After playing both levels
   - Click: **Top Better**, **Bottom Better**, **Tie**, or **Skip**
   - Optionally select up to 3 tags per level
6. View the rating changes and updated leaderboard
7. Repeat!

**Controls:**
- Arrow Keys: Move left/right, duck
- S: Jump (hold for higher jump)
- A: Run / Shoot fireballs (when Fire Mario)
- SPACE: Start level (when waiting)

## Configuration

### Backend URL

Override the backend URL using:

**CLI argument:**
```bash
./gradlew run --args="--base-url http://localhost:8080"
```

**Environment variable:**
```bash
export ARENA_BASE_URL=http://localhost:8080
./gradlew run
```

**Default:** `http://localhost:8080`

## Building

### Build JAR

```bash
./gradlew build
```

Output: `build/libs/client-java-0.1.0.jar`

### Run JAR

```bash
java -jar build/libs/client-java-0.1.0.jar
```

Or with custom base URL:

```bash
java -jar build/libs/client-java-0.1.0.jar --base-url http://localhost:8080
```

## Project Structure

```
client-java/
├── src/main/java/arena/
│   ├── App.java                       # Main entry point
│   ├── config/
│   │   └── ClientConfig.java          # Configuration loader
│   ├── api/
│   │   ├── ArenaApiClient.java        # HTTP client
│   │   ├── ArenaApiException.java     # API exception
│   │   └── models/                    # Request/Response DTOs
│   ├── ui/
│   │   ├── MainWindow.java            # Main application window
│   │   ├── BattlePanel.java           # Left/right level display
│   │   ├── TilemapView.java           # Tilemap rendering component
│   │   ├── TilemapParser.java         # Tilemap validation/parsing
│   │   ├── TileStyle.java             # Tile visual mapping
│   │   └── LeaderboardPanel.java      # Leaderboard display
│   └── util/
│       ├── JsonUtil.java              # JSON serialization
│       ├── LoggerUtil.java            # Logging utilities
│       └── TimeUtil.java              # Time formatting
└── logs/
    └── client.log                     # Application log file
```

## Logging

All activity is logged to `logs/client.log` including:

- Configuration and startup
- API requests and responses
- Battle IDs and vote IDs
- Errors and exceptions

This helps with debugging and troubleshooting.

## Allowed Tags

You can select up to 3 tags when voting:

- `too_easy` - Level is too easy
- `too_hard` - Level is too hard
- `boring` - Level is boring or repetitive
- `unfair` - Level has unfair elements
- `interesting` - Level has interesting design
- `creative` - Level is creative or novel
- `broken` - Level is broken or unplayable
- `unplayable` - Level cannot be completed

## Error Handling

The client handles various error scenarios:

- **Backend unreachable:** Shows error and exits
- **Protocol mismatch:** Shows error and exits
- **No battles available:** Shows message and allows retry after 3 seconds
- **Battle already voted:** Shows message and enables "Next Battle"
- **Network errors on vote:** Shows "Retry" button for manual retry
- **Invalid tags:** Clears tags and allows reselection

## Phase 1 Acceptance Criteria

✅ **Health gate works** - Client verifies protocol version on startup  
✅ **Battle fetch works** - Client fetches and displays battles  
✅ **Vote submit works** - Client submits votes and shows vote ID  
✅ **Leaderboard refresh works** - Client fetches and displays leaderboard  
✅ **Idempotent vote replay** - Backend handles duplicate votes safely  
✅ **Persistence visible** - Votes persist across backend restarts

## Known Limitations (Phase 2)

- No level restart - you play each level once per battle
- No replay/spectate mode - cannot watch previous plays
- No AI agent integration - human play only
- Timer is fixed at 200 seconds per level
- Cannot pause during gameplay

## Phase 2 Features

✅ **Full Mario gameplay mechanics**
✅ **Sequential level play (top then bottom)**
✅ **Rich telemetry collection** (18+ metrics per level)
✅ **SPACE to start** each level
✅ **Classic controls** (Arrow Keys, S, A)
✅ **Enemies, powerups, physics**
✅ **30 FPS smooth gameplay**

## Gameplay Guide

For detailed information about controls, mechanics, enemies, and powerups, see:

**[GAMEPLAY.md](GAMEPLAY.md)** - Complete Mario gameplay guide

Topics covered:
- Controls and movement
- Enemies and how to defeat them
- Powerups (Mushroom, Fire Flower, etc.)
- Scoring and voting guidelines
- Phase 2 gameplay flow
- Troubleshooting gameplay issues

## Troubleshooting

### "Backend unreachable" error

- Verify backend is running: `docker compose ps`
- Check backend URL configuration
- Check backend logs: `docker compose logs backend`

### "Protocol mismatch" error

- Ensure backend and client are both using `arena/v0`
- Update client or backend to matching versions

### Window doesn't appear

- Check Java version: `java -version` (must be 11+)
- Check logs: `tail -f logs/client.log`
- Try running from command line instead of IDE

### Levels don't render

- Check backend returned valid tilemap
- Check `logs/client.log` for parsing errors
- Verify level format in backend response

## Development

### Clean build

```bash
./gradlew clean build
```

### Run with debug logging

Edit `src/main/resources/logback.xml` and change:

```xml
<root level="DEBUG">
```

### IDE Setup

Import as Gradle project in:
- IntelliJ IDEA
- Eclipse
- VS Code (with Java extension)

## License

See LICENSE file in project root.

