# PCG Arena Java Client - Phase 1 Acceptance Checklist

**Version:** 0.1.0  
**Protocol:** arena/v0  
**Date:** 2025-12-25

## Pre-requisites

- [ ] Java 11+ installed and in PATH
- [ ] Backend running at http://localhost:8080
- [ ] Backend has seed data loaded (generators and levels)

## Test Setup

### Start Backend

```bash
cd <project-root>
docker compose up --build
```

Wait for: "Application startup complete"

### Start Client

```bash
cd client-java
./gradlew run
```

Or on Windows:

```cmd
cd client-java
gradlew.bat run
```

---

## Phase 1 Acceptance Criteria

### 1. Health Gate Works

**Test:** Client startup with backend running

- [ ] Client window opens
- [ ] Top bar shows "Status: Backend OK - Ready"
- [ ] Session ID is displayed (shortened, 8 chars)
- [ ] Backend URL is shown
- [ ] No error dialogs appear
- [ ] Log file created at `logs/client.log`

**Test:** Client startup with backend stopped

- [ ] Stop backend: `docker compose down`
- [ ] Start client
- [ ] Error dialog appears: "Backend Unreachable"
- [ ] Client exits cleanly after closing dialog

**Test:** Protocol version mismatch (manual test - requires backend modification)

- [ ] If backend returns different protocol version
- [ ] Error dialog appears: "Protocol Mismatch"
- [ ] Shows expected vs actual protocol version
- [ ] Client exits cleanly

---

### 2. Battle Fetch Works

**Test:** Fetch and display battle

- [ ] Start client with backend running
- [ ] Click "Next Battle" button
- [ ] Status changes to "Fetching battle..."
- [ ] Battle loads successfully
- [ ] Status shows "Battle loaded - Vote now"
- [ ] Battle ID displayed in top bar (format: `Battle: <uuid>`)
- [ ] LEFT panel shows tilemap with colored tiles
- [ ] RIGHT panel shows tilemap with colored tiles
- [ ] Generator names displayed under each panel
- [ ] Generator versions displayed
- [ ] Generator IDs displayed (shortened, 8 chars)
- [ ] Vote buttons become enabled
- [ ] "Next Battle" button becomes disabled

**Test:** Tilemap rendering

- [ ] Tiles are visually distinct (different colors)
- [ ] Solid blocks (X, S, #) are brown
- [ ] Air (-) is light blue
- [ ] Coins (o, C) are gold
- [ ] Question blocks (?, Q) are orange
- [ ] Pipes (t, T, <, >, [, ]) are green
- [ ] Enemies (E, g, k, r, K) are red
- [ ] Start marker (M) is bright green
- [ ] Finish marker (F) is magenta
- [ ] Levels are scrollable horizontally if wide
- [ ] No rendering errors or exceptions

---

### 3. Vote Submit Works

**Test:** Submit LEFT vote

- [ ] Load a battle
- [ ] Click "Left Better" button
- [ ] Status changes to "Submitting vote..."
- [ ] Vote buttons become disabled
- [ ] Status changes to "Vote accepted! Vote ID: <uuid>"
- [ ] Vote ID is displayed
- [ ] "Next Battle" button becomes enabled
- [ ] Vote buttons remain disabled for this battle

**Test:** Submit RIGHT vote

- [ ] Load a new battle
- [ ] Click "Right Better" button
- [ ] Vote is accepted
- [ ] Vote ID displayed

**Test:** Submit TIE vote

- [ ] Load a new battle
- [ ] Click "Tie" button
- [ ] Vote is accepted
- [ ] Vote ID displayed

**Test:** Submit SKIP vote

- [ ] Load a new battle
- [ ] Click "Skip" button
- [ ] Vote is accepted
- [ ] Vote ID displayed

**Test:** Vote with tags

- [ ] Load a new battle
- [ ] Select 1-3 tags (e.g., "interesting", "creative")
- [ ] Click any vote button
- [ ] Vote is accepted
- [ ] Check logs: tags are included in request

**Test:** Tag validation (max 3)

- [ ] Load a battle
- [ ] Try to select 4 tags
- [ ] Warning dialog appears: "Maximum 3 tags allowed"
- [ ] 4th tag is automatically deselected
- [ ] Can still submit vote with 3 tags

**Test:** Vote button safety (no double-submit)

- [ ] Load a battle
- [ ] Click "Left Better" rapidly multiple times
- [ ] Only one vote is submitted
- [ ] Buttons are disabled after first click
- [ ] No duplicate vote errors

---

### 4. Leaderboard Refresh Works

**Test:** Initial leaderboard load

- [ ] Client starts and health check passes
- [ ] Leaderboard panel shows top 10 generators
- [ ] Columns: Rank, Name, Rating, W, L, T, Battles
- [ ] All 3 generators visible (notch, hopper, genetic)
- [ ] Ratings shown (initially 1000.0 for all)
- [ ] Rating system info shown at bottom
- [ ] Shows: "Rating: ELO | Initial: 1000 | K-factor: 24"

**Test:** Leaderboard updates after vote

- [ ] Submit a non-SKIP vote (LEFT, RIGHT, or TIE)
- [ ] Leaderboard refreshes automatically
- [ ] Ratings change for the two generators in the battle
- [ ] Win/Loss/Tie counts update
- [ ] Total battles count increases
- [ ] Rankings may reorder based on new ratings

**Test:** Rating changes visible

- [ ] Submit a vote
- [ ] Observe rating changes in leaderboard
- [ ] Winner's rating increases
- [ ] Loser's rating decreases
- [ ] TIE: both ratings change slightly
- [ ] SKIP: ratings don't change (check by fetching new battle)

---

### 5. Idempotent Vote Replay Does Not Corrupt

**Test:** Retry button on network error (simulated)

- [ ] Load a battle
- [ ] Stop backend: `docker compose stop`
- [ ] Click a vote button
- [ ] Error appears: "Network error - Click Retry or fetch next battle"
- [ ] "Retry Submit" button appears
- [ ] Start backend: `docker compose start`
- [ ] Wait for backend to be ready (~5 seconds)
- [ ] Click "Retry Submit"
- [ ] Vote is accepted
- [ ] Same vote_id returned (backend deduplication)
- [ ] Leaderboard shows correct ratings (no double-update)

**Test:** Duplicate vote handling

- [ ] Load a battle
- [ ] Submit a vote successfully
- [ ] Note the battle_id
- [ ] Manually try to vote on same battle (requires code modification or API call)
- [ ] Backend returns error: "BATTLE_ALREADY_VOTED"
- [ ] Client shows message and allows "Next Battle"
- [ ] Leaderboard is not corrupted

---

### 6. Persistence Is Visible

**Test:** Votes persist across backend restart

- [ ] Submit 3-5 votes with the client
- [ ] Note the current leaderboard state (ratings, W/L/T counts)
- [ ] Stop backend: `docker compose down`
- [ ] Start backend: `docker compose up`
- [ ] Wait for backend to be ready
- [ ] Start client (or click "Next Battle" if still running)
- [ ] Fetch leaderboard
- [ ] Leaderboard shows same ratings and counts as before restart
- [ ] Previous votes are still recorded
- [ ] Can continue voting and ratings update correctly

---

## Error Handling Tests

### No Battle Available

**Test:** Exhaust battle pool (unlikely in Phase 1, but test error handling)

- [ ] If backend returns "NO_BATTLE_AVAILABLE"
- [ ] Status shows: "No battles available - Try again in a few seconds"
- [ ] "Next Battle" button is disabled for 3 seconds
- [ ] Button automatically re-enables after delay
- [ ] Can retry fetching battle

### Invalid Battle Payload

**Test:** Backend returns malformed tilemap (requires backend modification)

- [ ] If tilemap has wrong height (not 16 lines)
- [ ] Error message shown: "Failed to display battle: Invalid height..."
- [ ] Battle panel shows "No level loaded"
- [ ] Can fetch next battle
- [ ] Error logged to `logs/client.log`

### Invalid Tags

**Test:** Backend rejects tags (requires sending unlisted tag)

- [ ] If backend returns "INVALID_TAG" error
- [ ] Status shows error message
- [ ] Tag checkboxes are cleared
- [ ] Can reselect tags and vote again

---

## Logging Verification

**Test:** Log file contents

- [ ] Open `client-java/logs/client.log`
- [ ] Contains startup messages with version and config
- [ ] Contains health check request/response
- [ ] Contains battle fetch requests with battle_id
- [ ] Contains vote submissions with vote_id and result
- [ ] Contains error messages if any occurred
- [ ] Timestamps are present on all entries
- [ ] Log is human-readable and useful for debugging

---

## UI/UX Tests

### Window Layout

- [ ] Window opens at reasonable size
- [ ] All components visible without scrolling window
- [ ] Top bar clearly shows status, session, and battle ID
- [ ] Left and right panels are equal size
- [ ] Tilemap panels are scrollable if levels are wide
- [ ] Vote buttons are clearly labeled
- [ ] Tag checkboxes are readable
- [ ] Leaderboard table is readable
- [ ] No overlapping components

### State Transitions

- [ ] Starting → Ready (after health check)
- [ ] Ready → Fetching (click Next Battle)
- [ ] Fetching → Battle Loaded (battle arrives)
- [ ] Battle Loaded → Submitting (click vote)
- [ ] Submitting → Voted (vote accepted)
- [ ] Voted → Ready (click Next Battle)
- [ ] Any state → Error (on error)
- [ ] Error → Ready (after recovery)

### Button States

- [ ] Vote buttons only enabled when battle is loaded
- [ ] "Next Battle" only enabled when no pending battle
- [ ] "Retry" only visible after retryable error
- [ ] Tag checkboxes only enabled when battle is loaded
- [ ] Buttons have clear visual enabled/disabled states

---

## Performance Tests

### Response Times

- [ ] Health check completes in < 1 second
- [ ] Battle fetch completes in < 2 seconds
- [ ] Vote submission completes in < 2 seconds
- [ ] Leaderboard fetch completes in < 1 second
- [ ] UI remains responsive during API calls (background threads)

### Resource Usage

- [ ] Client uses reasonable memory (< 200 MB)
- [ ] No memory leaks after 20+ battles
- [ ] Log file doesn't grow excessively (< 1 MB after 50 battles)
- [ ] Window redraws smoothly

---

## Cross-Platform Tests (if applicable)

### Windows

- [ ] gradlew.bat works
- [ ] Application runs
- [ ] All features work

### Linux

- [ ] ./gradlew works (requires chmod +x)
- [ ] Application runs
- [ ] All features work

### macOS

- [ ] ./gradlew works
- [ ] Application runs
- [ ] All features work

---

## Configuration Tests

### Base URL Override

**Test:** CLI argument

```bash
./gradlew run --args="--base-url http://localhost:8080"
```

- [ ] Client uses specified URL
- [ ] Shown in session label
- [ ] Connects successfully

**Test:** Environment variable

```bash
export ARENA_BASE_URL=http://localhost:8080
./gradlew run
```

- [ ] Client uses env var URL
- [ ] Shown in session label
- [ ] Connects successfully

**Test:** Default

- [ ] No config provided
- [ ] Client uses http://localhost:8080
- [ ] Connects successfully

---

## Final Checklist

- [ ] All 6 Phase 1 acceptance criteria pass
- [ ] All error handling tests pass
- [ ] Logging works correctly
- [ ] UI/UX is functional and clear
- [ ] Performance is acceptable
- [ ] Configuration options work
- [ ] README.md is accurate and helpful
- [ ] Code is clean and well-structured
- [ ] No critical bugs or crashes

---

## Sign-Off

**Tester:** ___________________________  
**Date:** ___________________________  
**Result:** ☐ PASS  ☐ FAIL  ☐ PASS WITH NOTES

**Notes:**

___________________________________________________________________________

___________________________________________________________________________

___________________________________________________________________________

---

## Next Steps

After Phase 1 acceptance:

1. ✅ Phase 1 complete - static battle viewer working
2. 🔜 Begin Phase 2 planning - gameplay integration
3. 🔜 Design gameplay engine interface
4. 🔜 Implement telemetry collection
5. 🔜 Integrate actual Mario physics and gameplay

**Phase 1 Status:** Ready for acceptance testing  
**Phase 2 Status:** Not started (awaiting Phase 1 approval)

