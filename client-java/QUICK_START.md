# PCG Arena Java Client - Quick Start Guide

**Version:** 0.1.0  
**Status:** ✅ Ready to Run

---

## Prerequisites

1. **Java 11 or later** installed
   ```bash
   java -version
   ```

2. **Backend running** at http://localhost:8080
   ```bash
   # From project root
   docker compose up --build
   ```
   
   Wait for: `"Application startup complete"`

---

## Running the Client

### Option 1: Using Gradle (Recommended)

**Windows:**
```cmd
cd client-java
gradlew.bat run
```

**Linux/Mac:**
```bash
cd client-java
./gradlew run
```

### Option 2: Using JAR

**Build first:**
```bash
cd client-java
./gradlew build
```

**Then run:**
```bash
java -jar build/libs/client-java-0.1.0.jar
```

---

## First Steps

1. **Window Opens**
   - Status shows "Backend OK - Ready"
   - Session ID displayed at top

2. **Click "Next Battle"**
   - Two levels appear side-by-side
   - Generator names shown under each level

3. **Vote**
   - Click: **Left Better**, **Right Better**, **Tie**, or **Skip**
   - Optionally select up to 3 tags
   - Vote is submitted

4. **View Results**
   - Vote ID shown
   - Leaderboard updates automatically
   - Ratings change

5. **Repeat**
   - Click "Next Battle" to continue

---

## Configuration

### Custom Backend URL

**CLI:**
```bash
./gradlew run --args="--base-url http://localhost:8080"
```

**Environment Variable:**
```bash
export ARENA_BASE_URL=http://localhost:8080
./gradlew run
```

---

## Troubleshooting

### "Backend Unreachable" Error

✅ **Solution:** Start the backend first
```bash
docker compose up
```

### Window Doesn't Appear

✅ **Solution:** Check Java version (must be 11+)
```bash
java -version
```

### Build Fails

✅ **Solution:** Clean and rebuild
```bash
./gradlew clean build
```

### Levels Don't Display

✅ **Solution:** Check logs
```bash
cat logs/client.log
```

---

## What You Can Do (Phase 1)

✅ View procedurally generated levels  
✅ Vote on which level is better  
✅ Tag levels with descriptive labels  
✅ View leaderboard and rating changes  
✅ See generator statistics (W/L/T)  

## What's Coming (Phase 2)

🔜 Actually play the levels  
🔜 Collect gameplay telemetry  
🔜 Submit votes with rich data  
🔜 Mario physics and enemies  

---

## Need Help?

- **Full Documentation:** See `README.md`
- **Acceptance Tests:** See `ACCEPTANCE.md`
- **Implementation Details:** See `IMPLEMENTATION_SUMMARY.md`
- **Logs:** Check `logs/client.log`

---

## Quick Demo Flow

```
1. Start backend: docker compose up
2. Start client:  ./gradlew run
3. Click:         "Next Battle"
4. Observe:       Two levels displayed
5. Click:         "Left Better" (or any vote)
6. Observe:       Vote accepted, leaderboard updates
7. Click:         "Next Battle"
8. Repeat:        Steps 3-7
```

**That's it!** You're now using the PCG Arena client.

---

**Happy voting!** 🎮

