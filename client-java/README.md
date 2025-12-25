# PCG Arena Java Client - Phase 1

**Version:** 0.1.0  
**Protocol:** arena/v0  
**Status:** Phase 1 Implementation Complete

## Overview

This is a Java desktop client for the PCG Arena system. Phase 1 implements a static battle viewer that allows you to:

- View two procedurally generated levels side-by-side
- Vote on which level is better (LEFT/RIGHT/TIE/SKIP)
- Tag levels with descriptive labels
- View the leaderboard and rating changes

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

### 3. Use the Client

1. The client performs a health check on startup
2. Click **"Next Battle"** to fetch a battle
3. View the two levels displayed side-by-side
4. Optionally select up to 3 tags
5. Click one of the vote buttons: **Left Better**, **Right Better**, **Tie**, or **Skip**
6. View the rating changes and updated leaderboard
7. Repeat!

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

## Known Limitations (Phase 1)

- No gameplay - levels are static visualizations only
- No telemetry - empty object sent in Phase 1
- Tile rendering is simple colored rectangles
- No scrolling camera - entire level shown in scrollable panel
- Small tile size (4px) to fit wide levels

## Next Steps (Phase 2)

Phase 2 will integrate actual gameplay:

- Play left level, then right level
- Collect telemetry (deaths, completion, duration, etc.)
- Submit vote with rich telemetry data
- Same protocol and API, enhanced client experience

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

