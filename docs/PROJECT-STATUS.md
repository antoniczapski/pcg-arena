# PCG Arena — Project Status

**Last Updated:** 2025-12-26  
**Current Stage:** Stage 1 Complete → Moving to Stage 2

---

## Quick Summary

**What works right now:**
- ✅ Backend API deployed to GCP (http://YOUR_VM_IP:8080)
- ✅ SQLite database with 30 levels (3 generators)
- ✅ ELO rating system operational
- ✅ Java client can connect remotely
- ✅ Daily backups configured
- ✅ Admin endpoints secured

**What we're building next:**
- 🎯 Browser-based Mario gameplay (no download needed)
- 🎯 Mobile-friendly design
- 🎯 Same protocol, same backend

---

## Completed Stages

### Stage 0: Concept Validation ✅
**Duration:** ~4 weeks  
**Status:** Complete (2025-12-24)

**Achievements:**
- Local Docker backend with FastAPI
- SQLite database with 7 tables
- 8 API endpoints (health, battles, votes, leaderboard, debug)
- Java client with full Mario gameplay
- 30 seed levels across 3 generators
- Demo scripts for automated testing

**Key deliverable:** Proved end-to-end loop works locally

---

### Stage 1: Cloud Deployment ✅
**Duration:** ~1 week  
**Status:** Complete (2025-12-26)

**Achievements:**
- Deployed to GCP Compute Engine (e2-micro free tier)
- CORS enabled for browser access
- Enhanced health check with metrics
- Request logging middleware
- Rate limiting (SlowAPI)
- 5 admin endpoints with Bearer auth
- Backup/restore scripts (Windows & Linux)
- Remote validation with Java client

**Key deliverable:** Backend is cloud-hosted and remotely accessible

**Cost:** ~$3-4/month (static IP only, VM is free tier)

---

## Current Stage

### Stage 2: Browser Frontend 🎯 IN PROGRESS
**Started:** 2025-12-26  
**Estimated Duration:** 6-12 weeks  
**Target Completion:** February 2026

**Goals:**
- Replace Java client with browser-based gameplay
- HTML5 Canvas for rendering
- JavaScript port of Mario engine
- Mobile-responsive design
- Same protocol (arena/v0) - no backend changes needed

**Progress:**
- [ ] Foundation: API client + HTML layout
- [ ] Game engine: Mario physics port
- [ ] Battle flow: Sequential play + telemetry
- [ ] Polish: Mobile controls + optimization
- [ ] Testing: Cross-browser + mobile devices
- [ ] Deployment: 100+ real battles collected

See `docs/stage2-spec.md` for complete plan.

---

## Future Stages

### Stage 3: Backend Refinement 📋 PLANNED
**Purpose:** Research-grade platform

**Key features:**
- Advanced matchmaking (uncertainty-aware, coverage-aware)
- Generator versioning and seasons
- Diagnostic surfaces (completion rates, tag analytics)
- Exportable dataset for publications
- Enhanced integrity (anomaly detection)

**Target:** Enable academic research and publication

---

### Stage 4: Platform Expansion 💭 FUTURE
**Purpose:** Community scale

**Possible directions:**
- User accounts and authentication
- Social features (leaderboards, badges)
- Moderation tools
- Sandboxed generator submissions
- Public API for researchers

---

## Technical Stack

### Backend
- **Language:** Python 3.12
- **Framework:** FastAPI + Uvicorn
- **Database:** SQLite (single file)
- **Deployment:** Docker on GCP e2-micro
- **Protocol:** arena/v0 (stable)

### Frontend (Stage 2)
- **Language:** JavaScript (Vanilla) or TypeScript
- **Rendering:** HTML5 Canvas
- **Bundler:** Rollup or Webpack (TBD)
- **Testing:** Jest + Playwright

### Infrastructure
- **Cloud:** Google Cloud Platform
- **VM:** e2-micro (1 vCPU, 1 GB RAM) - free tier
- **Region:** us-central1
- **Backups:** Daily automated (cron)
- **Monitoring:** GCP uptime checks

---

## Repository Structure

```
pcg-arena/
├── README.md                    # Project overview
├── docker-compose.yml           # Container orchestration
│
├── backend/                     # FastAPI application
│   ├── src/                     # Python source
│   ├── scripts/                 # Backup/demo scripts
│   └── requirements.txt         # Dependencies
│
├── db/                          # Database layer
│   ├── migrations/              # SQL migrations
│   ├── seed/                    # Initial data
│   └── local/                   # Runtime DB (gitignored)
│
├── client-java/                 # Validation prototype
│   ├── src/                     # Java source
│   └── build.gradle             # Build config
│
├── frontend/                    # 🎯 NEXT: Browser client
│   ├── index.html               # Entry point
│   ├── js/                      # JavaScript modules
│   └── assets/                  # Sprites, audio
│
├── docs/                        # Documentation
│   ├── stage0-spec.md           # Stage 0 technical spec
│   ├── stage1-spec.md           # Stage 1 deployment guide
│   ├── stage2-spec.md           # Stage 2 frontend plan
│   ├── PROJECT-STATUS.md        # This file
│   └── TESTING-STAGE1.md        # Stage 1 testing guide
│
└── Mario-AI-Framework-PCG/      # Source of game engine
    ├── src/engine/              # Original Java engine
    └── levels/                  # 9000+ generated levels
```

---

## Metrics & Analytics

### Stage 1 Validation (Java Client)
- **Battles played:** ~15 (local testing)
- **Generators:** 3 (genetic, hopper, notch)
- **Levels in pool:** 30 (10 per generator)
- **Average battle duration:** ~3 minutes
- **Vote distribution:** Roughly balanced

### Stage 2 Target (Browser Client)
- **Target battles:** 100+ collected
- **Target users:** 10+ unique sessions
- **Device coverage:** Desktop + mobile
- **Completion rate:** >80% of started battles

---

## Key Decisions Log

### Architecture Decisions
1. **SQLite over Postgres:** Simplicity for Stage 0/1, sufficient for <1000 battles
2. **FastAPI over Django:** Minimal, async-capable, fast iteration
3. **Java for validation:** Proven engine from Mario AI Framework, easy port
4. **Browser for Stage 2:** Eliminate download barrier, enable mobile

### Deployment Decisions
1. **GCP over AWS:** Free tier e2-micro, simpler pricing
2. **Single VM over containers:** Cost optimization, simpler ops
3. **SQLite on disk:** No managed DB needed, backup via file copy
4. **Static IP:** $3-4/month for stable access (could use ephemeral for $0)

### Protocol Decisions
1. **arena/v0 stability:** Backend API unchanged across Stage 0→1→2
2. **ASCII tilemap format:** Human-readable, easy validation
3. **ELO rating:** Simple, deterministic, well-understood
4. **Idempotent votes:** Client retry safety built-in

---

## Testing Status

### Backend Tests
- ✅ Unit tests for level validation
- ✅ Integration tests for battle/vote flow
- ✅ Demo script (10 automated battles)
- ✅ Manual testing with Postman/curl

### Java Client Tests
- ✅ Protocol validation
- ✅ Battle fetch and rendering
- ✅ Vote submission with telemetry
- ✅ Remote connectivity to GCP
- ✅ 15+ manual gameplay sessions

### Browser Tests (Stage 2)
- ⏳ Not yet started
- 🎯 Target: Cross-browser + mobile

---

## Known Issues & Limitations

### Current Limitations
1. **No authentication:** Anyone with URL can vote (acceptable for Stage 1/2)
2. **No abuse prevention:** Rate limiting only (enhanced in Stage 3)
3. **Small level pool:** 30 levels (expandable on demand)
4. **No mobile client:** Addressed in Stage 2
5. **Manual backups only:** Automated via cron, but no restore UI

### Technical Debt
1. **Request counter resets:** On container restart (not persistent)
2. **No database migrations:** Schema is stable, but no migration framework beyond SQL files
3. **Hardcoded tile mapping:** In Java client (will need JS port)
4. **No telemetry analysis:** Data collected but not visualized

**None of these block Stage 2 progress.**

---

## Contact & Resources

**Deployment:**
- VM IP: (stored privately)
- Backend URL: http://YOUR_VM_IP:8080
- Health check: http://YOUR_VM_IP:8080/health
- HTML leaderboard: http://YOUR_VM_IP:8080/

**Documentation:**
- Full specs: `docs/*.md`
- Testing guide: `docs/TESTING-STAGE1.md`
- Backup scripts: `backend/scripts/README.md`

**Code:**
- Backend: `backend/src/main.py`
- Database: `db/migrations/001_init.sql`
- Java client: `client-java/src/main/java/arena/`

---

**Next Action:** Begin Stage 2 implementation — Browser frontend with Mario gameplay 🎮

