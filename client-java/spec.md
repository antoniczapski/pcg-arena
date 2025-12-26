# `client-java/spec.md` — PCG Arena Java Client (Validation Prototype)

**Location:** `./client-java/spec.md`
**Protocol:** `arena/v0`
**Scope:** Stage 0/1 validation client for local and remote testing
**Status:** ✅ COMPLETE — Both Phase 1 and Phase 2 implemented and validated

**Note:** This client was built as a validation prototype to prove the end-to-end loop. Future stages will use a browser-based frontend (Stage 2). The Java client remains useful for:
- Local testing during backend development
- Validation of protocol changes
- Reference implementation for gameplay mechanics

---

## 0) Goals and non-goals

### Phase 1 goal (this document)

Build a **local Java executable** that can:

1. Call the backend to request a battle (`POST /v1/battles:next`)
2. **Render two levels** (left/right) as static visualizations
3. Collect a basic **vote** (LEFT/RIGHT/TIE/SKIP) without gameplay
4. Submit the vote (`POST /v1/votes`)
5. Fetch and show leaderboard (`GET /v1/leaderboard`)

This validates:

* HTTP wiring (requests + JSON parsing + error handling)
* protocol version enforcement (`arena/v0`)
* correct rendering of the tilemap payload
* the full “battle → vote → rating change” loop

### Phase 1 non-goals

* No Mario physics, no collision, no enemies, no scrolling camera.
* No telemetry beyond minimal placeholders.
* No fancy UI/menus. Keep it debuggable.

### Phase 2 goal (broad)

Replace “static view + vote” with:

* “play left, then play right” in your gameplay engine
* then submit vote + telemetry

---

## 1) Architecture overview

The Java client has three internal layers:

1. **API Client (HTTP + JSON)**

   * Owns all communication with backend.
   * Converts JSON payloads to typed Java objects.
   * Handles errors and protocol checks.

2. **Battle Viewer UI**

   * Displays *two* levels side-by-side (left and right) horizontally.
   * Shows minimal battle metadata (battle_id).
   * Offers voting controls and displays responses.

3. **App Orchestrator**

   * Startup: create session_id, probe `/health`.
   * Loop: request battle → display → collect vote → submit → refresh leaderboard.
   * Responsible for retries/backoff only where safe (see error handling).

All state that must persist across requests in Phase 1:

* `session_id` (client-generated UUID for the run)
* `battle_id` (current outstanding battle)
* optional: last fetched leaderboard (for display)

---

## 2) Runtime and packaging requirements

### Execution

* Runs locally on developer machine.
* Talks to backend at `http://localhost:8080` by default.

### Configuration

Allow overriding base URL via:

* CLI arg: `--base-url http://localhost:8080`
* or env var: `ARENA_BASE_URL`

Phase 1 default:

* `ARENA_BASE_URL=http://localhost:8080`

### Build and artifact

* Build tool: Gradle or Maven (choose one; Gradle is common for desktop apps).
* Output: runnable artifact:

  * either “fat jar” (`client-java/build/libs/client-java-all.jar`)
  * or platform-specific packaging later (not needed in Phase 1)

---

## 3) Protocol contract (client-side strictness)

### 3.1 Protocol version gate

On every successful response, the client MUST verify:

* field `protocol_version` exists
* equals `"arena/v0"`

If not, client must stop and show a clear message:

* “Incompatible backend protocol: expected arena/v0, got …”

### 3.2 Health check on startup

Client performs:

* `GET /health`
  If failed:
* show backend unreachable / wrong protocol and exit (Phase 1 simplicity).

---

## 4) API integration details (Phase 1)

### 4.1 Fetch battle

**Endpoint:** `POST /v1/battles:next`

**Request body:**

```json
{
  "client_version": "0.1.0",
  "session_id": "<uuid>",
  "player_id": null,
  "preferences": { "mode": "standard" }
}
```

**Client requirements:**

* Generate `session_id` once at startup.
* Store returned `battle_id` in memory until vote submission succeeds.

**Response:**

* `battle.left.level_payload.tilemap` is the authoritative level text for the left level.
* `battle.left.format.width` and `.height` describe dimensions.
* Same structure for `battle.right`.

### 4.2 Submit vote

**Endpoint:** `POST /v1/votes`

**Request body:**

```json
{
  "client_version": "0.1.0",
  "session_id": "<uuid>",
  "battle_id": "<battle_id>",
  "result": "LEFT",
  "left_tags": [],
  "right_tags": [],
  "telemetry": {}
}
```

**Phase 1 rules:**

* Tags: allow selecting 0–3 tags per level from the allowed list (optional UI).
* Telemetry: empty object `{}` in Phase 1.

### 4.3 Fetch leaderboard

**Endpoint:** `GET /v1/leaderboard`

**Phase 1 usage:**

* After vote is accepted, fetch leaderboard and render top N rows (N=10 by default).
* Also show the two generators involved in the last battle and their ratings.

---

## 5) Static battle viewer UI (Phase 1)

Phase 1 UI should be minimal but functional. Two recommended options:

### Option A (recommended): Swing desktop window

Pros: standard library, fast iteration, no extra deps.
Cons: old-school UI.

### Option B: JavaFX

Pros: nicer UI.
Cons: setup overhead depending on JDK distribution.

**Phase 1 recommendation:** Swing.

### 5.1 Screen layout (Phase 1)

Single main window:

* Top bar:

  * backend status (OK / error)
  * session_id (shortened)
  * battle_id
* Main content:

  * Left panel: rendered tilemap
  * Right panel: rendered tilemap (side by side horizontally)
* Under each panel:

  * generator name + id + version (revealed after vote)
* Bottom bar:

  * voting buttons: **Left Better**, **Right Better**, **Tie**, **Skip**
  * optional tag toggles (checkboxes)
  * status text: "Vote submitted", "Error: …"
  * button: "Next battle" (enabled only when no pending battle)

### 5.2 Rendering approach

The backend returns ASCII tilemap text. The client should render it deterministically:

**Canonical rendering rules:**

* Split by `\n` into exactly 16 lines.
* For each character, draw a colored rectangle (tile) or a glyph.
* Scale:

  * Use fixed tile size (e.g., 6–10 px) so the full width fits.
  * If width=150, a tile size of 6 px gives 900 px wide per panel—too big. Prefer ~3–5 px or implement horizontal scaling.
* Scroll:

  * For Phase 1, simplest is to place each panel in a scroll container horizontally and vertically.
  * Later, gameplay will not need scroll because camera is part of engine.

**Tile-to-visual mapping (Phase 1):**

* `-` (air): empty / background
* `X`, `S`, `#`: solid blocks
* `o`, `C`, `Q`, `!`, `?`, `@`: coin / question blocks
* `t`, `T`, `<`, `>`, `[`, `]`: pipe tiles
* enemy chars: draw as small marker (no behavior)
* `M` start and `F` finish: special markers

Important: **Phase 1 does not need to perfectly represent semantics**, only to visually differentiate tiles reliably.

### 5.3 User interaction rules (Phase 1)

* When a battle is shown, exactly one vote can be sent.
* After “Vote submitted”:

  * disable voting buttons for that battle
  * enable “Next battle”
* On retryable errors (if backend says retryable=true):

  * allow user to retry manually (button: “Retry submit”)
* On non-retryable errors:

  * show message and force “Next battle” (or restart)

---

## 6) Client-side error handling (Phase 1)

### Error response shape

Backend errors return:

```json
{
  "protocol_version": "arena/v0",
  "error": { "code": "...", "message": "...", "retryable": false, "details": {} }
}
```

### Phase 1 behavior by error type

* `NO_BATTLE_AVAILABLE`: show message, disable Next battle for a few seconds, allow retry.
* `BATTLE_NOT_FOUND`: show message, request a new battle.
* `BATTLE_ALREADY_VOTED`: show message, request a new battle.
* `DUPLICATE_VOTE_CONFLICT`: show message, request a new battle (Phase 1 simplicity).
* `INVALID_TAG`: show message, clear tags UI selection.
* `INVALID_PAYLOAD`: show message and log full payload for debugging.
* `INTERNAL_ERROR` / network failure:

  * show message + allow manual retry

### Logging (Phase 1)

Write a local log file:

* `client-java/logs/client.log`
  Include:
* timestamps
* request URL + method
* response status
* error codes/messages
* battle_id and vote_id

This helps debug integration issues before gameplay exists.

---

## 7) Phase 1 acceptance criteria (must-pass)

1. **Health gate works**

* If backend is off: client shows “backend unreachable” and exits cleanly.
* If protocol mismatch: client refuses to proceed.

2. **Battle fetch works**

* Client can fetch a battle and display left/right tilemaps.
* Displays generator metadata correctly.

3. **Vote submit works**

* Pressing any vote button triggers POST /v1/votes.
* On success, client shows accepted=true + vote_id.

4. **Leaderboard refresh works**

* After a non-skip vote, leaderboard changes and is visible in UI.

5. **Idempotent vote replay does not corrupt**

* If you click vote twice quickly (or simulate a retry), backend should not double-update.
* Client should show a stable result (same vote_id or conflict handled).

6. **Persistence is visible**

* After restarting backend container, previously submitted votes still affect leaderboard.

---

## 8) Suggested directory structure for client-java

```
client-java/
  spec.md
  build.gradle or pom.xml

  src/main/java/arena/
    App.java                  # Main entry
    config/
      ClientConfig.java
    api/
      ArenaApiClient.java     # HTTP wrapper
      models/                 # Pydantic-equivalent Java DTOs
        HealthResponse.java
        BattleRequest.java
        BattleResponse.java
        VoteRequest.java
        VoteResponse.java
        LeaderboardResponse.java
        ErrorResponse.java
    ui/
      MainWindow.java
      BattlePanel.java         # Left/right panel composition
      TilemapView.java         # Tile rendering
      LeaderboardPanel.java
    util/
      JsonUtil.java
      HashUtil.java            # (optional) if you ever compute hashes
      TimeUtil.java
      LoggerUtil.java

  logs/                        # gitignored
  dist/                        # gitignored
```

---

## 9) Phase 2 (gameplay integration) — broad plan only

Phase 2 replaces the static viewer with a gameplay loop while keeping the **same protocol**.

### Phase 2 UI flow

1. Fetch battle
2. Play LEFT level (engine)
3. Play RIGHT level (engine)
4. Vote screen (same 4 outcomes + per-level tags)
5. Submit vote with telemetry
6. Show leaderboard summary (optional)

### Telemetry to add in Phase 2 (recommended minimal set)

In `telemetry`:

* for each side:

  * `played` (bool)
  * `duration_seconds`
  * `completed` (bool)
  * `deaths` (int)
  * optional: `coins_collected`, `jumps`, `damage_taken`

Backend stores telemetry as JSON without enforcing schema (Stage 0), but client should generate consistent keys.

### Engine integration boundary

Create a minimal interface the Arena client calls:

* `LevelSessionResult playLevel(String tilemapText, LevelMetadata meta)`

  * returns telemetry and “did the user quit early”

That interface lets you plug in your existing engine without rewriting the Arena client.

### Phase 2 acceptance criteria (high level)

* same as Phase 1, plus:

  * user can play both levels and vote
  * telemetry is populated and stored
  * client enforces LEFT_THEN_RIGHT play order
