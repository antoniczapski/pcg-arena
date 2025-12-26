# PCG Arena — Stage 2 Specification: Browser Frontend

**Created:** 2025-12-26  
**Author:** Planning document  
**Status:** Planning Phase  
**Protocol:** arena/v0 (unchanged from Stage 0/1)

---

## Table of Contents

1. [Stage 2 Overview](#1-stage-2-overview)
2. [Goals and Non-Goals](#2-goals-and-non-goals)
3. [Technical Architecture](#3-technical-architecture)
4. [Implementation Plan](#4-implementation-plan)
5. [Testing Strategy](#5-testing-strategy)
6. [Deployment](#6-deployment)
7. [Success Criteria](#7-success-criteria)

---

## 1. Stage 2 Overview

### Purpose

Replace the Java client validation prototype with a **browser-based frontend** that eliminates the download barrier and enables instant gameplay from any device.

### What Changes

| Aspect | Stage 0/1 | Stage 2 |
|--------|-----------|---------|
| **Client platform** | Java desktop app | Browser (no download) |
| **Distribution** | Manual JAR download | URL access |
| **Mario engine** | Ported from Mario AI Framework (Java) | JavaScript/TypeScript port |
| **Rendering** | Java Swing | HTML5 Canvas or WebGL |
| **Protocol** | arena/v0 | arena/v0 (unchanged) |
| **Backend** | Same | Same (no changes needed) |
| **Device support** | Desktop only | Desktop + mobile |

### What Stays the Same

- ✅ Backend API (all endpoints identical)
- ✅ Protocol version (arena/v0)
- ✅ Level format (ASCII tilemap)
- ✅ Rating system (ELO)
- ✅ Database schema
- ✅ Deployment infrastructure

**Key insight:** Stage 1's CORS configuration means the backend is already ready for browser clients.

---

## 2. Goals and Non-Goals

### Goals

**Primary goal:**
- Browser-playable Mario with identical gameplay to Java client
- Same UX flow: fetch battle → play left → play right → vote → next

**Secondary goals:**
- Mobile-friendly responsive design
- Fast load times (<5 seconds on 3G)
- No installation or plugins required
- Identical telemetry collection to Java client

### Non-Goals (Explicitly Out of Scope)

❌ User accounts or authentication (Stage 4)  
❌ Advanced matchmaking algorithms (Stage 3)  
❌ Social features or leaderboards (Stage 4)  
❌ Generator submission tools (Stage 4)  
❌ Multi-language support (future)  
❌ Accessibility features beyond basics (future)

### Success Criteria

Stage 2 is complete when:
1. ✅ User can access arena via URL (e.g., http://YOUR_VM_IP:8080/play)
2. ✅ Full Mario gameplay works in browser
3. ✅ Left-then-right sequential play enforced
4. ✅ Vote submission includes telemetry
5. ✅ Works on desktop Chrome, Firefox, Safari
6. ✅ Works on mobile (iOS Safari, Android Chrome)
7. ✅ Performance: 60 FPS gameplay on mid-range devices
8. ✅ 100+ battles collected via browser client

---

## 3. Technical Architecture

### 3.1 Technology Stack

**Frontend framework options:**

**Option A: Vanilla JavaScript + Canvas (Recommended)**
- Pros: Zero dependencies, fast load, full control
- Cons: More manual work
- Best for: Maximum performance and simplicity

**Option B: TypeScript + Phaser.js**
- Pros: Game framework, proven for platformers
- Cons: 1MB+ framework overhead
- Best for: Rapid development

**Option C: React + Canvas**
- Pros: Component architecture, state management
- Cons: Heavier bundle, more complex
- Best for: If scaling to complex UI

**Stage 2 recommendation:** Option A (Vanilla JS + Canvas) for performance and simplicity.

---

### 3.2 Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│              Browser Client                      │
│                                                   │
│  ┌─────────────┐      ┌──────────────┐         │
│  │  UI Layer   │◄────►│  Game Engine │         │
│  │  (HTML/CSS) │      │  (Canvas)    │         │
│  └─────────────┘      └──────────────┘         │
│         │                     │                  │
│         └─────────┬───────────┘                 │
│                   │                              │
│           ┌───────▼────────┐                    │
│           │  API Client    │                    │
│           │  (fetch)       │                    │
│           └───────┬────────┘                    │
└───────────────────┼─────────────────────────────┘
                    │ HTTPS (CORS enabled)
                    │
┌───────────────────▼─────────────────────────────┐
│         Backend (FastAPI)                        │
│                                                   │
│  GET  /play          → Serve frontend HTML       │
│  POST /v1/battles:next → Battle data             │
│  POST /v1/votes       → Vote + telemetry         │
│  GET  /v1/leaderboard → Ratings                  │
└───────────────────────────────────────────────────┘
```

---

### 3.3 File Structure

```
pcg-arena/
  frontend/                    # New directory
    index.html                 # Entry point
    styles/
      main.css                 # Core styles
      game.css                 # Game-specific styles
    js/
      main.js                  # Application entry
      api/
        client.js              # Backend API wrapper
        models.js              # TypeScript-style types (JSDoc)
      game/
        engine.js              # Mario physics engine
        level.js               # Level parser
        mario.js               # Mario entity
        enemies.js             # Enemy entities
        tilemap.js             # Tilemap rendering
        input.js               # Keyboard/touch input
        camera.js              # Camera/viewport
      ui/
        battle.js              # Battle screen
        vote.js                # Vote screen
        leaderboard.js         # Leaderboard display
      util/
        logger.js              # Logging utility
        storage.js             # localStorage wrapper
    assets/
      sprites/
        mario.png              # Mario sprite sheet
        enemies.png            # Enemy sprites
        tiles.png              # Block/tile sprites
      sounds/                  # (Optional for Stage 2)
        jump.wav
        coin.wav
```

---

### 3.4 Core Components

#### Component 1: API Client

**Responsibility:** All HTTP communication with backend

**Interface:**
```javascript
class ArenaApiClient {
  constructor(baseUrl) { /* ... */ }
  
  async health() { /* GET /health */ }
  async nextBattle(sessionId) { /* POST /v1/battles:next */ }
  async submitVote(voteData) { /* POST /v1/votes */ }
  async leaderboard() { /* GET /v1/leaderboard */ }
}
```

**Features:**
- Protocol version validation
- Error handling with retry logic
- Request correlation IDs
- Automatic JSON serialization

---

#### Component 2: Mario Game Engine

**Responsibility:** Physics, collision, entities, rendering

**Key classes:**
```javascript
class GameEngine {
  constructor(canvas, levelData) { /* ... */ }
  
  start() { /* Begin game loop */ }
  update(deltaTime) { /* Physics step */ }
  render(ctx) { /* Draw frame */ }
  getResult() { /* Return telemetry */ }
}

class Mario {
  constructor(x, y) { /* ... */ }
  update(input, level) { /* Movement + collision */ }
  takeDamage() { /* ... */ }
  jump() { /* ... */ }
}

class Level {
  constructor(tilemapText) { /* Parse ASCII → tile grid */ }
  getTileAt(x, y) { /* Collision query */ }
  render(ctx, camera) { /* Draw tiles */ }
}
```

**Physics target:** Match Java client behavior exactly

**Framerate:** 60 FPS with requestAnimationFrame

---

#### Component 3: UI Layer

**Responsibility:** HTML/CSS interface, state management

**Screens:**
1. **Loading screen** — Health check, session creation
2. **Battle screen** — Left panel, right panel, "Press SPACE to start"
3. **Vote screen** — Buttons: Left Better / Right Better / Tie / Skip
4. **Leaderboard screen** — Generator rankings (optional)

**State machine:**
```
LOADING → READY → PLAY_LEFT → PLAY_RIGHT → VOTE → LOADING
                     ↓                           ↓
                   SKIP ─────────────────────────┘
```

---

### 3.5 Mobile Considerations

**Input handling:**
- Desktop: Arrow keys + S (jump) + A (run)
- Mobile: On-screen virtual buttons (D-pad + A/B buttons)

**Layout:**
- Desktop: Side-by-side panels (1200px+ width)
- Mobile: Stacked panels (portrait) or single panel (landscape)

**Performance:**
- Target: 60 FPS on iPhone 8 / Galaxy S9 equivalent
- Canvas size: Scale down on mobile (480px max width)
- Sprite scaling: Use pixel-perfect scaling

---

## 4. Implementation Plan

### Phase 1: Foundation (Week 1)

**Tasks:**
1. Create `frontend/` directory structure
2. Implement API client with protocol validation
3. Create basic HTML layout
4. Test connectivity: health check + battle fetch
5. Parse and display ASCII tilemap (static rendering)

**Deliverable:** Can fetch a battle and display both levels as static images.

---

### Phase 2: Game Engine (Week 2-3)

**Tasks:**
1. Port Mario physics from Java client:
   - Movement (walk, run, jump)
   - Collision detection (tiles)
   - Gravity and acceleration
2. Implement enemies (Goomba, Koopa) with basic AI
3. Implement items (coins, blocks, powerups)
4. Camera scrolling
5. Win/lose conditions

**Deliverable:** Playable Mario game with single level.

---

### Phase 3: Battle Flow (Week 4)

**Tasks:**
1. Sequential play: enforce left-then-right order
2. Telemetry collection (deaths, coins, time, completion)
3. Vote screen with tag selection
4. Submit vote with full telemetry
5. Session management (localStorage)

**Deliverable:** Complete battle flow from fetch to vote.

---

### Phase 4: Polish & Mobile (Week 5)

**Tasks:**
1. Mobile layout and touch controls
2. Responsive design (breakpoints)
3. Loading states and error handling
4. Sprite sheets and animations
5. Performance optimization

**Deliverable:** Production-ready frontend.

---

### Phase 5: Testing & Deployment (Week 6)

**Tasks:**
1. Cross-browser testing (Chrome, Firefox, Safari)
2. Mobile device testing (iOS, Android)
3. Performance profiling
4. Deploy to GCP VM
5. Collect 100+ real battles

**Deliverable:** Deployed and validated with real users.

---

## 5. Testing Strategy

### Unit Tests

Test in isolation:
- API client (mock fetch)
- Level parser (ASCII → tile grid)
- Collision detection
- Input handling

**Tools:** Jest or Mocha

---

### Integration Tests

Test components together:
- Battle fetch → level parse → render
- Gameplay → telemetry collection
- Vote submission → backend response

**Tools:** Playwright or Cypress

---

### Manual Testing Checklist

**Desktop:**
- [ ] Chrome 120+ (Windows, Mac, Linux)
- [ ] Firefox 120+
- [ ] Safari 17+
- [ ] Edge 120+

**Mobile:**
- [ ] iOS Safari (iPhone 12+)
- [ ] Chrome Android (Galaxy S21+)

**Gameplay:**
- [ ] Mario responds to input
- [ ] Enemies move and collide
- [ ] Camera follows Mario
- [ ] Coins collected, score updates
- [ ] Win condition (reach flag)
- [ ] Lose condition (fall/die)

**Flow:**
- [ ] Battle fetches successfully
- [ ] Left level plays first
- [ ] Right level plays second
- [ ] Vote screen appears after both
- [ ] Telemetry submitted correctly
- [ ] Next battle loads

---

## 6. Deployment

### Backend Changes (Minimal)

Add endpoint to serve frontend HTML:

```python
@app.get("/play", response_class=HTMLResponse)
async def play_page():
    """Serve the browser frontend."""
    return FileResponse("frontend/index.html")
```

Add static file serving:

```python
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="frontend"), name="static")
```

**Docker compose update:**
```yaml
volumes:
  - ./frontend:/frontend:ro
```

---

### Deployment Steps

1. **Build frontend:** Bundle/minify JS/CSS (optional for Stage 2)
2. **Copy to VM:** `scp -r frontend/ user@vm:/app/`
3. **Restart backend:** `docker compose restart backend`
4. **Test:** Navigate to `http://YOUR_VM_IP:8080/play`

---

## 7. Success Criteria

### Technical Metrics

- [ ] **Load time:** <5 seconds on 3G
- [ ] **Bundle size:** <500 KB (gzipped)
- [ ] **Framerate:** 60 FPS on desktop, 30+ FPS on mobile
- [ ] **Memory:** <100 MB RAM usage
- [ ] **Battery:** <10% drain for 10-minute session (mobile)

### Functional Metrics

- [ ] **Protocol compliance:** All API calls match arena/v0
- [ ] **Telemetry accuracy:** Matches Java client data
- [ ] **Error rate:** <1% failed requests
- [ ] **Completion rate:** >80% of started battles reach vote
- [ ] **Device coverage:** Works on 95% of target devices

### User Metrics (Post-Deployment)

- [ ] **100+ battles** collected via browser
- [ ] **10+ unique sessions**
- [ ] **Average session:** 5+ battles
- [ ] **Vote distribution:** Balanced (no single generator >70%)

---

## 8. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Physics doesn't match Java | High | Port carefully, add tests |
| Performance issues on mobile | Medium | Profile early, optimize |
| Browser compatibility issues | Medium | Test early, use polyfills |
| Large asset files | Low | Compress sprites, lazy load |
| Input lag on touch | Medium | Optimize event handling |

---

## 9. Timeline Estimate

**Total: 6 weeks (full-time) or 12 weeks (part-time)**

- Week 1: Foundation + API client
- Week 2-3: Game engine port
- Week 4: Battle flow integration
- Week 5: Mobile + polish
- Week 6: Testing + deployment

**Milestone checkpoints:**
- End of Week 1: Static battle viewer works
- End of Week 3: Playable game works
- End of Week 5: Full flow works on mobile
- End of Week 6: 100+ battles collected

---

## 10. Future Enhancements (Stage 3+)

Not in scope for Stage 2, but documented for planning:

- **Audio:** Sound effects and music
- **Animations:** Smooth sprites, particle effects
- **Replays:** Save and replay gameplay
- **Social sharing:** Share favorite levels
- **Accessibility:** Keyboard navigation, screen reader
- **Offline mode:** Service worker, PWA
- **Analytics dashboard:** Real-time stats

---

**End of Stage 2 Specification**

**Next step:** Begin implementation with Phase 1 (Foundation).

