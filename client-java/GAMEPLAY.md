# Mario Gameplay Guide

**PCG Arena Java Client - Phase 2**

---

## Controls

### Basic Movement
- **←/→ Arrow Keys**: Move left/right
- **↓ Arrow Key**: Duck (when Large Mario or Fire Mario)
- **S Key**: Jump (hold for higher jump)
- **A Key**: Run / Shoot fireballs (when Fire Mario)

### Tips
- Hold S longer to jump higher
- Hold A while moving to run faster
- Press A while Fire Mario to shoot fireballs
- Duck to fit through tight spaces

---

## Gameplay Mechanics

### Winning the Level
- Reach the **flag (F)** at the end of the level to win
- You have a timer - don't run out of time!

### Enemies
Stomp enemies by jumping on top of them:
- **Goomba (g)**: Basic enemy, walk left/right
- **Green Koopa (k)**: Leaves a shell when stomped
- **Red Koopa (r)**: Like green but doesn't fall off edges
- **Spiky (y)**: Cannot stomp! Need fireballs
- **Piranha Plant (T)**: Emerges from pipes
- **Bullet Bill (B/b)**: Flies from cannons

### Items & Powerups
Hit **? blocks** from below to get items:

- **Mushroom**: Small Mario → Large Mario
  - Can break bricks
  - Takes one more hit before dying

- **Fire Flower**: Large Mario → Fire Mario
  - Can shoot fireballs (press A)
  - Takes one more hit before reverting to Large

- **1-Up Mushroom (L)**: Extra life
- **Coins (o)**: Collect 100 for an extra life

### Tiles & Obstacles
- **X**: Ground - solid, can't pass through
- **S**: Bricks - Large/Fire Mario can break them by hitting from below
- **?/@**: Question blocks - hit from below for items
- **!**: Coin blocks - hit multiple times for coins
- **t/T**: Pipes - solid obstacles (T has Piranha Plant)
- **#**: Pyramid blocks - solid, decorative

---

## Scoring Your Experience

After playing both levels, you'll vote on which was better. Consider:

### Positive Factors
- **Fun gameplay**: Enjoyable to play
- **Good flow**: Smooth progression
- **Creative design**: Interesting layouts
- **Fair difficulty**: Challenging but beatable

### Negative Factors
- **Too hard**: Impossible or frustrating
- **Too easy**: No challenge
- **Boring**: Repetitive or empty
- **Unfair**: Cheap deaths or bad design
- **Broken/Unplayable**: Bugs or impossible sections

### Tags Available
When voting, you can select up to 3 tags per level:
- `fun`
- `boring`
- `good_flow`
- `creative`
- `unfair`
- `confusing`
- `too_hard`
- `too_easy`
- `not_mario_like`

---

## Phase 2 Flow

1. **Fetch Battle**: Click "Next Battle" to get two levels
2. **Play Top Level**: 
   - Press **SPACE** in the top panel to start
   - Play until you win, die, or run out of time
3. **Play Bottom Level**:
   - Press **SPACE** in the bottom panel to start
   - Play until you win, die, or run out of time
4. **Vote**: Choose which level was better
   - Top Better / Bottom Better / Tie / Skip
   - Optionally select tags
5. **Repeat**: Click "Next Battle" for another comparison

### Skip Option
- You can **skip** at any time if:
  - Level is unplayable or broken
  - You don't want to play
  - You've seen enough to make a decision
- Skipped levels still count as "played" with incomplete status

---

## Technical Details

### Game Physics
- Based on Mario AI Framework (10th Anniversary Edition)
- Classic Super Mario Bros mechanics
- 30 FPS gameplay
- Infinite retries within time limit

### Telemetry Collected
The system tracks (for research purposes):
- Completion status (win/lose/timeout)
- Deaths count
- Coins collected
- Time taken
- Enemies defeated
- Jumps performed
- Powerups collected

This data helps evaluate level quality objectively.

---

## Troubleshooting

**Controls not responding?**
- Click inside the game panel to focus it
- Make sure you pressed SPACE to start the level

**Level too hard?**
- You can skip and move to the next level
- Vote "too_hard" tag to provide feedback

**Game runs slowly?**
- Close other applications
- Game targets 30 FPS on mid-range hardware

**Level appears broken?**
- Vote "broken" or "unplayable" tag
- Skip and move to next battle

---

**Have fun and help us evaluate procedurally generated content!** 🎮

