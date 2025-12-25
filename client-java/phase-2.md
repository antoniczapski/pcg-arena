# PCG Arena Java Client - Phase 2 Implementation Plan

**Created:** 2025-12-25  
**Target:** Gameplay Integration  
**Protocol:** arena/v0 (unchanged)  
**Status:** Planning Phase

---

## Overview

Phase 2 integrates actual Mario gameplay into the PCG Arena client while maintaining the same backend API protocol. Users will play both levels sequentially before voting, with rich telemetry data collected and submitted.

### Phase 2 Goals

1. **Sequential Gameplay:** Play top level, then bottom level
2. **Space to Start:** User presses SPACE to begin each level
3. **Full Game Mechanics:** Replicate Mario AI Framework physics, enemies, collisions
4. **Telemetry Collection:** Track deaths, completion, time, coins, jumps, etc.
5. **Same Protocol:** No backend changes required

### Phase 2 Non-Goals

- Custom level editors
- Multiplayer gameplay
- Network gameplay recording/replay
- AI agent integration
- Level generation

---

## Analysis: Mario AI Framework Structure

### Core Components Needed

After analyzing `./Mario-AI-Framework-PCG/src/engine/`, we need these subsystems:

#### 1. **Game Loop & Orchestration**
- `MarioGame.java` - Top-level game runner
- `MarioWorld.java` - World state, sprite management, physics tick
- `MarioResult.java` - Telemetry collection

#### 2. **Level Parsing & Rendering**
- `MarioLevel.java` - Parse ASCII level into tile grid + sprite templates
- `MarioRender.java` - Render world to screen
- `MarioTilemap.java` - Tile graphics mapping
- `MarioBackground.java` - Background rendering

#### 3. **Player Character**
- `Mario.java` - Player sprite, physics, collision, state
- `MarioAgent.java` - Interface for input providers
- Human agent (keyboard input handler)

#### 4. **Sprites (Enemies, Items, Effects)**
- `MarioSprite.java` - Base sprite class
- `Enemy.java` - Base enemy class
- `Goomba.java`, `Shell.java`, `BulletBill.java`, `FlowerEnemy.java`
- `Fireball.java` - Player fireball
- `Mushroom.java`, `FireFlower.java`, `LifeMushroom.java` - Powerups
- Effects: `BrickEffect`, `CoinEffect`, `DeathEffect`, etc.

#### 5. **Assets & Graphics**
- `Assets.java` - Load sprite sheets from `img/` folder
- `MarioImage.java` - Sprite rendering wrapper
- `MarioGraphics.java` - Graphics utilities

#### 6. **Helper Classes**
- `MarioActions.java` - Action enums (LEFT, RIGHT, JUMP, SPEED, DOWN)
- `GameStatus.java` - WIN, LOSE, RUNNING, TIME_OUT
- `EventType.java` - Game events (JUMP, LAND, COLLECT, HURT, etc.)
- `SpriteType.java` - Sprite type enums
- `TileFeature.java` - Tile properties (BLOCK, BREAKABLE, etc.)
- `MarioEvent.java` - Event recording for telemetry
- `MarioAgentEvent.java` - Agent action recording
- `MarioForwardModel.java` - Simulation model (not needed for Phase 2)
- `MarioTimer.java` - Timer utilities

### Files NOT Needed

- `src/agents/*` - AI agents (except human agent for reference)
- `src/levelGenerators/*` - Level generators
- `src/GenerateLevel.java`, `src/PlayLevel.java` - Standalone runners
- `levels/*` - Thousands of level files (backend provides levels)

### Asset Files Needed

From `Mario-AI-Framework-PCG/img/`:
- `mariosheet.png` - Large Mario sprites
- `smallmariosheet.png` - Small Mario sprites
- `firemariosheet.png` - Fire Mario sprites
- `enemysheet.png` - Enemy sprites
- `itemsheet.png` - Item/powerup sprites
- `mapsheet.png` - Tile graphics
- `particlesheet.png` - Effect particles
- `font.gif` - UI font

---

## Integration Strategy

### Package Structure

```
client-java/src/main/java/arena/
├── game/                           # NEW: Mario engine (ported from framework)
│   ├── core/
│   │   ├── MarioGame.java
│   │   ├── MarioWorld.java
│   │   ├── MarioLevel.java
│   │   ├── MarioRender.java
│   │   ├── MarioResult.java
│   │   ├── MarioSprite.java
│   │   ├── MarioAgent.java
│   │   ├── MarioEvent.java
│   │   └── MarioAgentEvent.java
│   ├── sprites/
│   │   ├── Mario.java
│   │   ├── Enemy.java
│   │   ├── Goomba.java (implicit in Enemy)
│   │   ├── Shell.java
│   │   ├── BulletBill.java
│   │   ├── FlowerEnemy.java
│   │   ├── Fireball.java
│   │   ├── Mushroom.java
│   │   ├── FireFlower.java
│   │   └── LifeMushroom.java
│   ├── effects/
│   │   ├── BrickEffect.java
│   │   ├── CoinEffect.java
│   │   ├── DeathEffect.java
│   │   ├── DustEffect.java
│   │   ├── FireballEffect.java
│   │   └── SquishEffect.java
│   ├── graphics/
│   │   ├── MarioImage.java
│   │   ├── MarioGraphics.java
│   │   ├── MarioTilemap.java
│   │   └── MarioBackground.java
│   ├── helper/
│   │   ├── Assets.java
│   │   ├── MarioActions.java
│   │   ├── GameStatus.java
│   │   ├── EventType.java
│   │   ├── SpriteType.java
│   │   ├── TileFeature.java
│   │   ├── MarioTimer.java
│   │   └── MarioForwardModel.java (minimal - for forward model)
│   └── input/
│       └── HumanAgent.java        # Keyboard input handler
│
├── ui/
│   ├── MainWindow.java             # MODIFIED: Add gameplay orchestration
│   ├── GameplayPanel.java          # NEW: Embedded game window
│   ├── BattlePanel.java            # MODIFIED: Show play status
│   ├── TilemapView.java            # KEEP: Static preview (optional)
│   ├── TilemapParser.java          # KEEP: Validation
│   ├── TileStyle.java              # KEEP: Static rendering
│   └── LeaderboardPanel.java       # KEEP: Unchanged
│
└── (existing packages unchanged)

client-java/src/main/resources/
└── img/                            # NEW: Mario sprite sheets
    ├── mariosheet.png
    ├── smallmariosheet.png
    ├── firemariosheet.png
    ├── enemysheet.png
    ├── itemsheet.png
    ├── mapsheet.png
    ├── particlesheet.png
    └── font.gif
```

### Key Architectural Decisions

#### 1. **Namespace Isolation**

All Mario engine code lives in `arena.game.*` package:
- Avoids name collisions with existing UI code
- Clear separation between game engine and arena client
- Engine can be tested independently

#### 2. **Input Handling**

Create `arena.game.input.HumanAgent` that:
- Implements `MarioAgent` interface
- Extends `KeyAdapter` for keyboard input
- Maps keyboard to `boolean[] actions`
- Attached to `GameplayPanel` for focus

#### 3. **Asset Loading**

Modify `Assets.java` to:
- Load from classpath: `getClass().getResourceAsStream("/img/...")`
- Fall back to filesystem if needed
- Use relative paths compatible with JAR packaging

#### 4. **Game Orchestration**

Create `arena.ui.GameplayPanel` that:
- Embeds `MarioRender` component
- Manages game state: WAITING_TO_START, PLAYING, FINISHED
- Displays "Press SPACE to start" overlay
- Captures telemetry on level completion
- Returns `LevelPlayResult` to `MainWindow`

#### 5. **Sequential Play Flow**

`MainWindow` orchestrates:
1. Fetch battle (unchanged)
2. Show top level in `GameplayPanel` (panel 1)
3. Wait for SPACE → play top level
4. Top level finishes → show "Level 1 Complete - Press SPACE for Level 2"
5. Show bottom level in `GameplayPanel` (panel 2)
6. Wait for SPACE → play bottom level
7. Bottom level finishes → enable vote buttons
8. Collect telemetry from both plays
9. Submit vote with telemetry (unchanged API)

---

## Telemetry Collection

### Data to Collect (from `MarioResult`)

For each level (top and bottom):

```java
{
  "played": true,
  "completed": boolean,              // GameStatus.WIN
  "game_status": "WIN|LOSE|TIME_OUT",
  "duration_ticks": int,             // currentTick
  "duration_seconds": float,         // ticks / 24
  "completion_percentage": float,    // 0.0 to 1.0
  "deaths": int,                     // 1 if LOSE, 0 otherwise
  "lives": int,                      // world.lives
  "coins": int,                      // world.coins
  "remaining_time": int,             // world.currentTimer / 1000
  "mario_final_mode": int,           // 0=small, 1=large, 2=fire
  "kills_total": int,
  "kills_stomp": int,
  "kills_fire": int,
  "kills_shell": int,
  "kills_fall": int,
  "num_jumps": int,
  "max_x_jump": float,
  "max_air_time": int,
  "num_collected_mushrooms": int,
  "num_collected_fireflower": int,
  "num_collected_coins": int,
  "num_destroyed_bricks": int,
  "num_hurt": int
}
```

### Vote Payload (Phase 2)

```json
{
  "client_version": "0.1.0",
  "session_id": "...",
  "battle_id": "...",
  "result": "TOP|BOTTOM|TIE|SKIP",
  "top_tags": ["too_hard", "creative"],
  "bottom_tags": ["boring"],
  "telemetry": {
    "top": { ... },
    "bottom": { ... }
  }
}
```

---

## UI Flow Changes

### Phase 1 (Current)

```
┌─────────────────────────────────────────┐
│ [Next Battle]                           │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────┐                │
│  │ Static Top Level    │                │
│  │ (TilemapView)       │                │
│  └─────────────────────┘                │
│                                         │
│  ┌─────────────────────┐                │
│  │ Static Bottom Level │                │
│  │ (TilemapView)       │                │
│  └─────────────────────┘                │
│                                         │
│ [Left Better] [Right Better] [Tie] [Skip]│
│ ☐ Tag1  ☐ Tag2  ☐ Tag3                  │
│                                         │
│ Leaderboard                             │
└─────────────────────────────────────────┘
```

### Phase 2 (Target)

```
┌─────────────────────────────────────────┐
│ [Next Battle]                           │
├─────────────────────────────────────────┤
│ Status: Playing Top Level (1/2)         │
│                                         │
│  ┌─────────────────────┐                │
│  │  ╔════════════════╗  │                │
│  │  ║ Press SPACE to ║  │  ← Overlay    │
│  │  ║ start Level 1  ║  │     when      │
│  │  ╚════════════════╝  │   waiting     │
│  │                     │                │
│  │   [Mario Gameplay]  │  ← MarioRender │
│  │   [Live rendering]  │    embedded    │
│  │                     │                │
│  └─────────────────────┘                │
│  Controls: Arrow Keys + S (Jump) + A (Run)│
│                                         │
│ [Left Better] [Right Better] [Tie] [Skip]│
│ (disabled until both levels played)     │
│                                         │
│ Leaderboard                             │
└─────────────────────────────────────────┘
```

### State Machine

```
States:
- READY_NO_BATTLE: "Click Next Battle"
- BATTLE_LOADED_WAITING_TOP: "Press SPACE to play top level"
- PLAYING_TOP: "Playing top level..." (vote buttons disabled)
- TOP_FINISHED_WAITING_BOTTOM: "Press SPACE to play bottom level"
- PLAYING_BOTTOM: "Playing bottom level..." (vote buttons disabled)
- BOTH_FINISHED_READY_TO_VOTE: "Vote now" (vote buttons enabled)
- SUBMITTING_VOTE: "Submitting..."
- VOTED_SHOW_RESULT: "Vote accepted, click Next Battle"
```

---

## Implementation Tasks

### Preparation Tasks (P1-P4)

#### P1: Copy Engine Files to client-java

**Description:** Copy all necessary `.java` files from `Mario-AI-Framework-PCG/src/engine/` to `client-java/src/main/java/arena/game/`.

**Steps:**
1. Create directory structure:
   ```
   client-java/src/main/java/arena/game/
     core/, sprites/, effects/, graphics/, helper/, input/
   ```

2. Copy files:
   - `engine/core/*` → `arena/game/core/`
   - `engine/sprites/*` → `arena/game/sprites/`
   - `engine/effects/*` → `arena/game/effects/`
   - `engine/graphics/*` → `arena/game/graphics/`
   - `engine/helper/*` → `arena/game/helper/`

3. Exclude files:
   - Do NOT copy `MarioForwardModel.java` (complex, not needed for human play)
   - Do NOT copy `MarioLevelGenerator.java`, `MarioLevelModel.java` (level gen)

**Acceptance:**
- All files copied with correct package structure
- No compilation errors (before next steps fix imports)

---

#### P2: Fix Package Declarations

**Description:** Update all copied files to use `arena.game.*` package instead of `engine.*`.

**Steps:**
1. Search and replace in all copied files:
   - `package engine.core;` → `package arena.game.core;`
   - `package engine.sprites;` → `package arena.game.sprites;`
   - `package engine.effects;` → `package arena.game.effects;`
   - `package engine.graphics;` → `package arena.game.graphics;`
   - `package engine.helper;` → `package arena.game.helper;`

2. Update imports in all files:
   - `import engine.` → `import arena.game.`

**Acceptance:**
- All package declarations correct
- All imports resolve within `arena.game.*`

---

#### P3: Copy and Configure Assets

**Description:** Copy sprite sheet images from `Mario-AI-Framework-PCG/img/` to `client-java/src/main/resources/img/`.

**Steps:**
1. Create directory:
   ```
   client-java/src/main/resources/img/
   ```

2. Copy files:
   - `Mario-AI-Framework-PCG/img/*.png` → `client-java/src/main/resources/img/`
   - `Mario-AI-Framework-PCG/img/font.gif` → same

3. Modify `Assets.java`:
   - Change loading strategy to use classpath resources:
     ```java
     BufferedImage source = ImageIO.read(
       Assets.class.getResourceAsStream("/img/" + imageName)
     );
     ```
   - Remove filesystem fallback for now (can add back later)

**Acceptance:**
- All 8 asset files present in resources
- `Assets.java` loads from classpath successfully
- Test: create dummy app that calls `Assets.init(gc)` and checks images != null

---

#### P4: Create HumanAgent Input Handler

**Description:** Create `arena.game.input.HumanAgent` that captures keyboard input.

**Steps:**
1. Create `client-java/src/main/java/arena/game/input/HumanAgent.java`

2. Port from `Mario-AI-Framework-PCG/src/agents/human/Agent.java`:
   ```java
   package arena.game.input;
   
   import arena.game.core.MarioAgent;
   import arena.game.core.MarioForwardModel;
   import arena.game.core.MarioTimer;
   import arena.game.helper.MarioActions;
   
   import java.awt.event.KeyAdapter;
   import java.awt.event.KeyEvent;
   
   public class HumanAgent extends KeyAdapter implements MarioAgent {
       private boolean[] actions;
       
       @Override
       public void initialize(MarioForwardModel model, MarioTimer timer) {
           actions = new boolean[MarioActions.numberOfActions()];
       }
       
       @Override
       public boolean[] getActions(MarioForwardModel model, MarioTimer timer) {
           return actions;
       }
       
       @Override
       public String getAgentName() {
           return "HumanPlayer";
       }
       
       @Override
       public void keyPressed(KeyEvent e) {
           toggleKey(e.getKeyCode(), true);
       }
       
       @Override
       public void keyReleased(KeyEvent e) {
           toggleKey(e.getKeyCode(), false);
       }
       
       private void toggleKey(int keyCode, boolean isPressed) {
           if (actions == null) return;
           switch (keyCode) {
               case KeyEvent.VK_LEFT:
                   actions[MarioActions.LEFT.getValue()] = isPressed;
                   break;
               case KeyEvent.VK_RIGHT:
                   actions[MarioActions.RIGHT.getValue()] = isPressed;
                   break;
               case KeyEvent.VK_DOWN:
                   actions[MarioActions.DOWN.getValue()] = isPressed;
                   break;
               case KeyEvent.VK_S:
                   actions[MarioActions.JUMP.getValue()] = isPressed;
                   break;
               case KeyEvent.VK_A:
                   actions[MarioActions.SPEED.getValue()] = isPressed;
                   break;
           }
       }
   }
   ```

**Acceptance:**
- File compiles
- Implements `MarioAgent` interface
- Extends `KeyAdapter`
- Maps arrow keys + S (jump) + A (run/fire)

---

### Core Engine Integration Tasks (E1-E6)

#### E1: Remove MarioForwardModel Dependencies

**Description:** Many engine classes reference `MarioForwardModel` for simulation. Since we only need human play (not AI planning), we can simplify or stub this out.

**Steps:**
1. Check which files import `MarioForwardModel`:
   - `MarioAgent.java` - interface requires it
   - `HumanAgent.java` - receives it but ignores it
   - Others?

2. Options:
   - **Option A (preferred):** Keep `MarioForwardModel` as a stub that just throws `UnsupportedOperationException` on most methods
   - **Option B:** Modify `MarioAgent` interface to make model parameter nullable

3. Implement Option A:
   - Copy `MarioForwardModel.java` skeleton
   - Keep constructor and clone methods
   - Throw `UnsupportedOperationException` on simulation methods
   - Add comment: "Phase 2: Forward model not needed for human play"

**Acceptance:**
- Engine compiles without `MarioForwardModel` errors
- Human agent works without using forward model

---

#### E2: Adapt MarioGame for Embedded Use

**Description:** Modify `MarioGame.java` to support embedded gameplay (not standalone window).

**Steps:**
1. Current behavior:
   - `playGame()` or `runGame()` creates a `JFrame` window
   - Blocks until game finishes
   - Returns `MarioResult`

2. New behavior needed:
   - Accept a parent `Container` to embed `MarioRender` into
   - Support non-blocking start (game loop in separate thread)
   - Support pausing/stopping mid-game
   - Return `MarioResult` via callback or getter

3. Add methods to `MarioGame`:
   ```java
   // New constructor for embedded mode
   public MarioGame(Container parent) { ... }
   
   // Non-blocking game start
   public void startGame(String level, int timer, int marioState,
                         GameplayCallback callback) {
       // Start game loop in background thread
       // Call callback.onFinished(result) when done
   }
   
   // Stop game early
   public void stopGame() {
       world.gameStatus = GameStatus.LOSE;
   }
   
   // Get current result (even if not finished)
   public MarioResult getCurrentResult() { ... }
   ```

4. Add callback interface:
   ```java
   public interface GameplayCallback {
       void onFinished(MarioResult result);
   }
   ```

**Acceptance:**
- `MarioGame` can be embedded in a parent container
- Game loop runs in background thread
- Callback fires on completion
- No standalone window created

---

#### E3: Create GameplayPanel Component

**Description:** Create `arena.ui.GameplayPanel` that wraps `MarioGame` and `MarioRender` for embedding in `MainWindow`.

**Steps:**
1. Create `client-java/src/main/java/arena/ui/GameplayPanel.java`:
   ```java
   package arena.ui;
   
   import arena.game.core.MarioGame;
   import arena.game.core.MarioResult;
   import arena.game.input.HumanAgent;
   
   import javax.swing.*;
   import java.awt.*;
   import java.awt.event.KeyAdapter;
   import java.awt.event.KeyEvent;
   
   public class GameplayPanel extends JPanel {
       public enum State {
           WAITING_TO_START,  // Show "Press SPACE"
           PLAYING,           // Game running
           FINISHED           // Game over
       }
       
       private State state;
       private MarioGame game;
       private HumanAgent agent;
       private MarioResult result;
       private String levelText;
       
       public GameplayPanel() {
           setLayout(new BorderLayout());
           setPreferredSize(new Dimension(256 * 2, 240 * 2));
           setFocusable(true);
           
           // Listen for SPACE key
           addKeyListener(new KeyAdapter() {
               @Override
               public void keyPressed(KeyEvent e) {
                   if (e.getKeyCode() == KeyEvent.VK_SPACE 
                       && state == State.WAITING_TO_START) {
                       startGameplay();
                   }
               }
           });
           
           state = State.WAITING_TO_START;
       }
       
       public void loadLevel(String levelText) {
           this.levelText = levelText;
           this.state = State.WAITING_TO_START;
           this.result = null;
           repaint();
       }
       
       private void startGameplay() {
           state = State.PLAYING;
           agent = new HumanAgent();
           game = new MarioGame();
           
           // Start game in background
           game.startGame(levelText, 200, 0, (result) -> {
               this.result = result;
               this.state = State.FINISHED;
               SwingUtilities.invokeLater(() -> {
                   // Notify parent that game finished
                   firePropertyChange("gameFinished", false, true);
               });
           });
           
           // Embed render component
           removeAll();
           add(game.getRenderComponent(), BorderLayout.CENTER);
           revalidate();
           repaint();
       }
       
       public State getState() { return state; }
       public MarioResult getResult() { return result; }
       
       @Override
       protected void paintComponent(Graphics g) {
           super.paintComponent(g);
           if (state == State.WAITING_TO_START) {
               // Draw "Press SPACE to start" overlay
               g.setColor(Color.BLACK);
               g.fillRect(0, 0, getWidth(), getHeight());
               g.setColor(Color.WHITE);
               g.setFont(new Font("Arial", Font.BOLD, 24));
               String msg = "Press SPACE to start";
               FontMetrics fm = g.getFontMetrics();
               int x = (getWidth() - fm.stringWidth(msg)) / 2;
               int y = getHeight() / 2;
               g.drawString(msg, x, y);
           }
       }
   }
   ```

2. Test standalone:
   - Create test main that shows `GameplayPanel` in a `JFrame`
   - Load a level from backend or hardcoded
   - Press SPACE and verify gameplay works

**Acceptance:**
- Panel shows "Press SPACE" overlay initially
- SPACE starts gameplay
- Game runs and is playable
- `gameFinished` property change fires on completion

---

#### E4: Create LevelPlayResult DTO

**Description:** Create a simple wrapper to hold telemetry from one level play.

**Steps:**
1. Create `client-java/src/main/java/arena/ui/LevelPlayResult.java`:
   ```java
   package arena.ui;
   
   import arena.game.core.MarioResult;
   import arena.game.helper.GameStatus;
   
   public class LevelPlayResult {
       public boolean played;
       public boolean completed;
       public String gameStatus;
       public int durationTicks;
       public float durationSeconds;
       public float completionPercentage;
       public int deaths;
       public int lives;
       public int coins;
       public int remainingTime;
       public int marioFinalMode;
       public int killsTotal;
       public int killsStomp;
       public int killsFire;
       public int killsShell;
       public int killsFall;
       public int numJumps;
       public float maxXJump;
       public int maxAirTime;
       public int numCollectedMushrooms;
       public int numCollectedFireflower;
       public int numCollectedCoins;
       public int numDestroyedBricks;
       public int numHurt;
       
       public static LevelPlayResult fromMarioResult(MarioResult result) {
           LevelPlayResult r = new LevelPlayResult();
           r.played = true;
           r.completed = result.getGameStatus() == GameStatus.WIN;
           r.gameStatus = result.getGameStatus().toString();
           r.durationTicks = result.getWorld().currentTick;
           r.durationSeconds = r.durationTicks / 24f;
           r.completionPercentage = result.getCompletionPercentage();
           r.deaths = result.getGameStatus() == GameStatus.LOSE ? 1 : 0;
           r.lives = result.getCurrentLives();
           r.coins = result.getCurrentCoins();
           r.remainingTime = result.getRemainingTime() / 1000;
           r.marioFinalMode = result.getMarioMode();
           r.killsTotal = result.getKillsTotal();
           r.killsStomp = result.getKillsByStomp();
           r.killsFire = result.getKillsByFire();
           r.killsShell = result.getKillsByShell();
           r.killsFall = result.getKillsByFall();
           r.numJumps = result.getNumJumps();
           r.maxXJump = result.getMaxXJump();
           r.maxAirTime = result.getMaxJumpAirTime();
           r.numCollectedMushrooms = result.getNumCollectedMushrooms();
           r.numCollectedFireflower = result.getNumCollectedFireflower();
           r.numCollectedCoins = result.getNumCollectedTileCoins();
           r.numDestroyedBricks = result.getNumDestroyedBricks();
           r.numHurt = result.getMarioNumHurts();
           return r;
       }
       
       // Add to telemetry map
       public void addToTelemetry(java.util.Map<String, Object> map) {
           map.put("played", played);
           map.put("completed", completed);
           map.put("game_status", gameStatus);
           map.put("duration_ticks", durationTicks);
           map.put("duration_seconds", durationSeconds);
           map.put("completion_percentage", completionPercentage);
           map.put("deaths", deaths);
           map.put("lives", lives);
           map.put("coins", coins);
           map.put("remaining_time", remainingTime);
           map.put("mario_final_mode", marioFinalMode);
           map.put("kills_total", killsTotal);
           map.put("kills_stomp", killsStomp);
           map.put("kills_fire", killsFire);
           map.put("kills_shell", killsShell);
           map.put("kills_fall", killsFall);
           map.put("num_jumps", numJumps);
           map.put("max_x_jump", maxXJump);
           map.put("max_air_time", maxAirTime);
           map.put("num_collected_mushrooms", numCollectedMushrooms);
           map.put("num_collected_fireflower", numCollectedFireflower);
           map.put("num_collected_coins", numCollectedCoins);
           map.put("num_destroyed_bricks", numDestroyedBricks);
           map.put("num_hurt", numHurt);
       }
   }
   ```

**Acceptance:**
- DTO compiles
- Converts `MarioResult` to flat telemetry structure
- Serializes to JSON correctly

---

#### E5: Integrate GameplayPanel into MainWindow

**Description:** Modify `MainWindow.java` to embed `GameplayPanel` instances and orchestrate sequential play.

**Steps:**
1. Add fields to `MainWindow`:
   ```java
   private GameplayPanel topGameplayPanel;
   private GameplayPanel bottomGameplayPanel;
   private LevelPlayResult topPlayResult;
   private LevelPlayResult bottomPlayResult;
   ```

2. Add new states:
   - `BATTLE_LOADED_WAITING_TOP`
   - `PLAYING_TOP`
   - `TOP_FINISHED_WAITING_BOTTOM`
   - `PLAYING_BOTTOM`
   - `BOTH_FINISHED_READY_TO_VOTE`

3. Modify `onBattleFetched()`:
   ```java
   private void onBattleFetched(BattleResponse battle) {
       currentBattle = battle;
       
       // Load levels into gameplay panels
       topGameplayPanel.loadLevel(battle.getLeft().getLevelPayload().getTilemap());
       bottomGameplayPanel.loadLevel(battle.getRight().getLevelPayload().getTilemap());
       
       // Reset play results
       topPlayResult = null;
       bottomPlayResult = null;
       
       // Update UI
       setState(State.BATTLE_LOADED_WAITING_TOP);
       updateStatusLabel("Press SPACE in top panel to play Level 1");
   }
   ```

4. Add property change listeners:
   ```java
   topGameplayPanel.addPropertyChangeListener("gameFinished", evt -> {
       topPlayResult = LevelPlayResult.fromMarioResult(
           topGameplayPanel.getResult()
       );
       setState(State.TOP_FINISHED_WAITING_BOTTOM);
       updateStatusLabel("Level 1 finished! Press SPACE in bottom panel to play Level 2");
   });
   
   bottomGameplayPanel.addPropertyChangeListener("gameFinished", evt -> {
       bottomPlayResult = LevelPlayResult.fromMarioResult(
           bottomGameplayPanel.getResult()
       );
       setState(State.BOTH_FINISHED_READY_TO_VOTE);
       updateStatusLabel("Both levels finished! Vote now.");
   });
   ```

5. Update vote submission to include telemetry:
   ```java
   private void onVoteSubmit(VoteResult result) {
       Map<String, Object> telemetry = new HashMap<>();
       
       Map<String, Object> topTelemetry = new HashMap<>();
       if (topPlayResult != null) {
           topPlayResult.addToTelemetry(topTelemetry);
       }
       telemetry.put("top", topTelemetry);
       
       Map<String, Object> bottomTelemetry = new HashMap<>();
       if (bottomPlayResult != null) {
           bottomPlayResult.addToTelemetry(bottomTelemetry);
       }
       telemetry.put("bottom", bottomTelemetry);
       
       VoteRequest request = new VoteRequest(
           clientConfig.getClientVersion(),
           sessionId,
           currentBattle.getBattleId(),
           result,
           getSelectedTopTags(),
           getSelectedBottomTags(),
           telemetry  // NEW: populated telemetry
       );
       
       // ... submit as before
   }
   ```

**Acceptance:**
- Top panel loads first level
- User presses SPACE → top level plays
- Top level finishes → bottom panel activates
- User presses SPACE → bottom level plays
- Bottom level finishes → vote buttons enable
- Telemetry collected from both plays

---

#### E6: Update VoteRequest to Support Telemetry

**Description:** Ensure `VoteRequest.java` DTO supports telemetry map.

**Steps:**
1. Check current `VoteRequest`:
   - Does it have `Map<String, Object> telemetry` field?
   - Is it serialized to JSON correctly?

2. If missing, add:
   ```java
   @JsonProperty("telemetry")
   private Map<String, Object> telemetry;
   
   // Constructor and getter
   ```

3. Ensure Jackson serializes nested maps correctly (should work by default)

**Acceptance:**
- `VoteRequest` includes telemetry field
- JSON serialization works
- Backend accepts payload (test with demo script)

---

### UI Polish Tasks (U1-U4)

#### U1: Add Gameplay Instructions to UI

**Description:** Show control instructions to user.

**Steps:**
1. Add label above gameplay panels:
   ```
   "Controls: Arrow Keys = Move, S = Jump, A = Run/Fire"
   ```

2. Style with clear font, centered

**Acceptance:**
- Instructions visible
- Clear and concise

---

#### U2: Show Level Play Progress

**Description:** Update status bar to show which level is being played.

**Steps:**
1. Status messages:
   - "Press SPACE to play Top Level (1/2)"
   - "Playing Top Level... (1/2)"
   - "Top Level Finished! Press SPACE to play Bottom Level (2/2)"
   - "Playing Bottom Level... (2/2)"
   - "Both Levels Finished! Cast your vote."

2. Update `setState()` method to set appropriate status text

**Acceptance:**
- User always knows which level they're playing
- Progress indicator (1/2, 2/2) clear

---

#### U3: Optional - Show Telemetry Summary

**Description:** After both levels finish, show a summary table comparing telemetry.

**Steps:**
1. Add optional panel below gameplay areas:
   ```
   ┌──────────────┬──────────┬──────────┐
   │ Metric       │ Top      │ Bottom   │
   ├──────────────┼──────────┼──────────┤
   │ Completed    │ Yes      │ No       │
   │ Deaths       │ 0        │ 1        │
   │ Coins        │ 23       │ 15       │
   │ Jumps        │ 45       │ 38       │
   │ Time (sec)   │ 87.5     │ 62.3     │
   └──────────────┴──────────┴──────────┘
   ```

2. Show only when state = `BOTH_FINISHED_READY_TO_VOTE`

**Acceptance:**
- Table shows key metrics side-by-side
- Helps user decide which level was better

---

#### U4: Handle Early Exit / Skip

**Description:** Allow user to skip playing a level (still count as "played" but incomplete).

**Steps:**
1. Add "Skip Level" button that appears during play

2. On click:
   - Stop game
   - Mark as incomplete
   - Create minimal telemetry (played=true, completed=false)
   - Move to next level

3. User can skip both levels and vote immediately (allowed by design)

**Acceptance:**
- User can skip if level is unplayable/broken
- Vote still submits with telemetry indicating skip

---

### Testing & Validation Tasks (T1-T4)

#### T1: Unit Test Engine Components

**Description:** Add basic tests for core engine classes.

**Steps:**
1. Create `client-java/src/test/java/arena/game/`

2. Test cases:
   - `MarioLevelTest`: Parse valid level, reject invalid level
   - `MarioActionsTest`: Enum values correct
   - `AssetsTest`: Load assets from classpath
   - `HumanAgentTest`: Key mappings correct

**Acceptance:**
- All tests pass
- Coverage > 50% for core classes

---

#### T2: Integration Test - Full Gameplay

**Description:** Test complete play-through of one level.

**Steps:**
1. Create integration test:
   - Load a short test level (10 tiles wide)
   - Start game programmatically
   - Simulate input: move right, jump, reach goal
   - Assert: `GameStatus.WIN`, telemetry collected

2. Use headless mode (no graphics)

**Acceptance:**
- Test runs in CI
- Takes < 5 seconds
- Verifies core gameplay loop

---

#### T3: Manual Acceptance Test - Phase 2

**Description:** Update `ACCEPTANCE.md` with Phase 2 test cases.

**Steps:**
1. Add Phase 2 section to `ACCEPTANCE.md`:
   - AC-P2-1: Fetch battle and see gameplay panels
   - AC-P2-2: Press SPACE on top level and play
   - AC-P2-3: Die or win, see transition to bottom level
   - AC-P2-4: Press SPACE on bottom level and play
   - AC-P2-5: Finish both, vote buttons enable
   - AC-P2-6: Submit vote with telemetry
   - AC-P2-7: Leaderboard updates
   - AC-P2-8: Backend logs show telemetry received

**Acceptance:**
- All test cases pass manually
- Documented in acceptance log

---

#### T4: Performance Validation

**Description:** Ensure game runs at 30 FPS on typical hardware.

**Steps:**
1. Profile game loop
2. Measure frame times
3. Optimize if needed (unlikely with original engine)

**Acceptance:**
- 30 FPS maintained on mid-range laptop
- No stuttering or lag

---

### Documentation Tasks (D1-D3)

#### D1: Update README.md

**Description:** Update README to reflect Phase 2 changes.

**Steps:**
1. Update "Known Limitations" section:
   - Remove "No gameplay"
   - Remove "No telemetry"
   - Add "No replay/spectate mode"

2. Update "Quick Start" to mention:
   - Press SPACE to start each level
   - Use arrow keys + S/A to play

**Acceptance:**
- README accurate for Phase 2

---

#### D2: Create GAMEPLAY.md

**Description:** Create a guide explaining Mario controls and mechanics.

**Steps:**
1. Create `client-java/GAMEPLAY.md`:
   ```markdown
   # Mario Gameplay Guide
   
   ## Controls
   - Arrow Keys: Move left/right, duck
   - S: Jump (hold for higher jump)
   - A: Run / Shoot fireballs (when Fire Mario)
   
   ## Mechanics
   - Stomp enemies by jumping on them
   - Hit ? blocks from below to get items
   - Collect mushrooms to grow
   - Collect fire flowers to shoot fireballs
   - Reach the flag to win
   
   ## Powerups
   - Mushroom: Small → Large Mario
   - Fire Flower: Large → Fire Mario
   - 1-Up Mushroom: Extra life
   
   ## Enemies
   - Goomba: Walk left/right, stomp to kill
   - Koopa: Walk, stomp to get shell, kick shell
   - Spiky: Cannot stomp, need fireball
   - Piranha Plant: Emerges from pipes
   - Bullet Bill: Flies from cannons
   ```

**Acceptance:**
- Guide exists
- Covers basic controls and mechanics

---

#### D3: Update IMPLEMENTATION_SUMMARY.md

**Description:** Document Phase 2 implementation.

**Steps:**
1. Add Phase 2 section:
   - Overview
   - Files added
   - Integration points
   - Challenges faced
   - Performance notes

**Acceptance:**
- Summary complete
- Future maintainers can understand Phase 2 changes

---

## Task Summary Table

| ID | Task | Category | Priority | Est. Hours |
|----|------|----------|----------|------------|
| P1 | Copy engine files | Prep | High | 1 |
| P2 | Fix package declarations | Prep | High | 1 |
| P3 | Copy and configure assets | Prep | High | 2 |
| P4 | Create HumanAgent | Prep | High | 1 |
| E1 | Remove MarioForwardModel deps | Engine | High | 2 |
| E2 | Adapt MarioGame for embedding | Engine | High | 4 |
| E3 | Create GameplayPanel | Engine | High | 4 |
| E4 | Create LevelPlayResult DTO | Engine | High | 1 |
| E5 | Integrate into MainWindow | Engine | High | 6 |
| E6 | Update VoteRequest | Engine | High | 1 |
| U1 | Add gameplay instructions | UI | Medium | 1 |
| U2 | Show level play progress | UI | Medium | 1 |
| U3 | Show telemetry summary | UI | Low | 3 |
| U4 | Handle early exit / skip | UI | Medium | 2 |
| T1 | Unit test engine | Testing | Medium | 3 |
| T2 | Integration test gameplay | Testing | High | 3 |
| T3 | Manual acceptance test | Testing | High | 2 |
| T4 | Performance validation | Testing | Low | 2 |
| D1 | Update README | Docs | Medium | 1 |
| D2 | Create GAMEPLAY.md | Docs | Low | 1 |
| D3 | Update IMPLEMENTATION_SUMMARY | Docs | Medium | 1 |
| **TOTAL** | | | | **43 hours** |

### Priority Key
- **High:** Required for Phase 2 completion
- **Medium:** Important for good UX
- **Low:** Nice-to-have, can defer

---

## Implementation Order

### Week 1: Engine Integration (P1-P4, E1-E2)
1. P1: Copy files
2. P2: Fix packages
3. P3: Copy assets
4. P4: HumanAgent
5. E1: Stub MarioForwardModel
6. E2: Adapt MarioGame

**Milestone:** Engine compiles, can run standalone test

### Week 2: UI Integration (E3-E6, U1-U2)
1. E3: GameplayPanel
2. E4: LevelPlayResult
3. E5: MainWindow integration
4. E6: VoteRequest telemetry
5. U1: Instructions
6. U2: Progress indicators

**Milestone:** Full sequential play works, telemetry submits

### Week 3: Polish & Testing (U3-U4, T1-T4, D1-D3)
1. U3: Telemetry summary (optional)
2. U4: Skip functionality
3. T1-T2: Automated tests
4. T3: Manual acceptance
5. T4: Performance check
6. D1-D3: Documentation

**Milestone:** Phase 2 complete, acceptance signed off

---

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Assets don't load from JAR | High | Medium | Test early (P3), add filesystem fallback |
| Game loop blocks UI thread | High | Low | Use background thread (E2) |
| Keyboard input not captured | High | Medium | Test focus management (E3) |
| Telemetry schema mismatch | Medium | Low | Validate with backend early (E6) |
| Poor performance on low-end hardware | Medium | Low | Profile early (T4), optimize if needed |
| Collision bugs from engine port | Medium | Medium | Compare with original framework behavior |

---

## Success Criteria

Phase 2 is complete when:

1. ✅ User can play both levels sequentially
2. ✅ SPACE key triggers level start
3. ✅ Game mechanics match Mario AI Framework
4. ✅ Telemetry collected and submitted correctly
5. ✅ Vote buttons only enable after both levels played
6. ✅ Skip option always available
7. ✅ No regressions in Phase 1 functionality
8. ✅ All acceptance tests pass
9. ✅ Documentation updated
10. ✅ Performance acceptable (30 FPS)

---

## Open Questions

1. **Q:** Should we show the static tilemap preview before gameplay starts?  
   **A:** Optional - could help orient the user, but adds UI complexity. Defer to polish phase.

2. **Q:** What happens if user closes window during gameplay?  
   **A:** Game stops, no telemetry submitted. Document as expected behavior.

3. **Q:** Should we enforce a minimum playtime before allowing vote?  
   **A:** No - if user quits immediately (e.g., broken level), that's valuable data.

4. **Q:** Do we need to support level restart?  
   **A:** Not in Phase 2 - user plays once, votes, moves on. Can add in Phase 3.

5. **Q:** How to handle levels that are too wide (>256 px viewport)?  
   **A:** Engine already has camera scrolling. Mario stays centered, world scrolls.

---

## Appendix A: Engine File Inventory

### Files to Copy (Total: ~35 files)

**core/ (8 files)**
- MarioGame.java
- MarioWorld.java
- MarioLevel.java
- MarioRender.java
- MarioResult.java
- MarioSprite.java
- MarioAgent.java (interface)
- MarioEvent.java
- MarioAgentEvent.java

**sprites/ (10 files)**
- Mario.java
- Enemy.java
- Shell.java
- BulletBill.java
- FlowerEnemy.java
- Fireball.java
- Mushroom.java
- FireFlower.java
- LifeMushroom.java

**effects/ (6 files)**
- BrickEffect.java
- CoinEffect.java
- DeathEffect.java
- DustEffect.java
- FireballEffect.java
- SquishEffect.java

**graphics/ (4 files)**
- MarioImage.java
- MarioGraphics.java
- MarioTilemap.java
- MarioBackground.java

**helper/ (8 files)**
- Assets.java
- MarioActions.java
- GameStatus.java
- EventType.java
- SpriteType.java
- TileFeature.java
- MarioTimer.java
- MarioForwardModel.java (stub)

**input/ (1 file, new)**
- HumanAgent.java

---

## Appendix B: Level Format Compatibility

The backend serves levels in ASCII tilemap format (Phase 1). The Mario engine expects the same format. Key symbols:

| Symbol | Meaning | Engine Support |
|--------|---------|----------------|
| `M` | Mario start | ✅ |
| `F` | Finish flag | ✅ |
| `X` | Ground block | ✅ |
| `#` | Pyramid block | ✅ |
| `S` | Brick | ✅ |
| `?`, `@` | Special block | ✅ |
| `!`, `Q` | Coin block | ✅ |
| `o` | Coin | ✅ |
| `t`, `T` | Pipe | ✅ |
| `g`, `E` | Goomba | ✅ |
| `k`, `r` | Koopa | ✅ |
| `y` | Spiky | ✅ |
| `-` | Air | ✅ |

**Compatibility:** 100% - backend levels will work directly with engine.

---

## Appendix C: Telemetry Schema (Full)

```json
{
  "top": {
    "played": true,
    "completed": false,
    "game_status": "LOSE",
    "duration_ticks": 523,
    "duration_seconds": 21.79,
    "completion_percentage": 0.67,
    "deaths": 1,
    "lives": 2,
    "coins": 15,
    "remaining_time": 178,
    "mario_final_mode": 0,
    "kills_total": 8,
    "kills_stomp": 6,
    "kills_fire": 0,
    "kills_shell": 2,
    "kills_fall": 0,
    "num_jumps": 42,
    "max_x_jump": 64.5,
    "max_air_time": 18,
    "num_collected_mushrooms": 1,
    "num_collected_fireflower": 0,
    "num_collected_coins": 15,
    "num_destroyed_bricks": 3,
    "num_hurt": 2
  },
  "bottom": {
    // ... same structure
  }
}
```

---

**End of Phase 2 Implementation Plan**

**Next Steps:**
1. Review plan with team/stakeholders
2. Create GitHub issues for each task (optional)
3. Begin Week 1 tasks (P1-P4)
4. Report progress daily/weekly
5. Iterate on open questions as they arise

**Good luck with Phase 2! 🚀**

