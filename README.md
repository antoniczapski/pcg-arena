# PCG Arena

**A Web Platform for Blind A/B Testing of Procedural Content Generators**

🎮 **Live at:** [https://pcg-arena.com](https://pcg-arena.com)

---

## What is PCG Arena?

PCG Arena is a research platform for evaluating **Mario level generators** through human preference data. Players play two procedurally generated levels side-by-side in their browser, vote for their favorite, and the platform maintains a **Glicko-2 leaderboard** ranking generators based on pairwise comparisons.

### The Problem We Solve

How do we know if a PCG algorithm produces "good" levels?

- ❌ Automated metrics miss **player experience**
- ❌ Lab studies have **limited participants**  
- ❌ Generator reputation creates **evaluation bias**

**Our Solution:** Web-based **blind A/B testing** at scale — players never know which generator made each level.

---

## Research Overview

### Dataset Statistics

| Metric | Value |
|--------|-------|
| **Generators** | 15 |
| **Levels** | 748 |
| **Human Votes** | 571 |
| **Player Trajectories** | 1,142 |
| **Unique Players** | 27 |

### Research Questions

1. **RQ1:** What structural and gameplay features make levels "good"?
2. **RQ2:** Are player preferences consistent across individuals?
3. **RQ3:** Can we build an automated reward model (judge function) for RLHF/DPO training?

---

## Generators Under Test

We compare **15 PCG algorithms** representing different generation paradigms:

| Category | Generators |
|----------|------------|
| **Neural/ML-Based** | MarioGPT (GPT-2), MarioGAN (DCGAN), MarioDiffusion, **MarioDPO (ours)** |
| **Search-Based** | Genetic Algorithm, Hopper (agent simulation) |
| **Grammar/Pattern** | Notch (3 variants), Pattern-based (3 variants), ORE (occupancy) |
| **Baseline** | Original Super Mario Bros. (15 hand-crafted levels) |

Each generator contributes **100 levels** (except Original: 15 levels).

---

## Key Findings

### H1: Flow Channel Hypothesis — ❌ Not Supported

**Hypothesis:** Moderate difficulty (15–40% death rate) maximizes enjoyment.

**Result:** Linear relationship — easier = better (r = -0.227, p = 0.046). Players prefer levels they can **complete**. No inverted-U "flow channel" pattern found.

### H2: Creativity Hypothesis — ✅ Partially Supported

**Hypothesis:** Higher terrain variety and enemy diversity preferred.

**Result:** Levels tagged "creative" win significantly more (r = 0.42, p < 0.01).

### H3: Agency Hypothesis — ✅ Partial Support

**Hypothesis:** Levels allowing more exploration are preferred.

**Result:** Winning levels have **63% more tiles explored** and lower backtrack ratios (p = 0.019).

### H4: Player Clusters — ✅ Supported

**Result:** K-means clustering identifies **3 distinct player types**:
- **Explorers** (n=2): Long sessions, high completion rates
- **Mainstream** (n=6): Most votes, balanced playstyle  
- **Strugglers** (n=4): Low completion, high death rates

### H6: Tag Validation — ✅ Supported

**Result:** Subjective player tags correlate with objective telemetry metrics (5/6 tags validated):
- `fun` ≈ playable + beatable
- `creative` ≈ engaging design
- `too_hard` ≈ high death rate
- `too_easy` ≈ high completion rate

**Conclusion:** Tags can be **trusted as quality signals** for machine learning.

---

## Judge Function & MarioDPO

### Automated Judge Function

We developed a reward model that predicts human preferences from level features:

**Stage 1 — Static Features:**

$$J_{static} = \frac{w_{style}}{1+D_M} - w_{gap} \cdot \text{Gap}$$

**Stage 2 — Dynamic Features:**

$$J_{final} = J_{static} + w_{vert} \cdot \sigma_y$$

| Weight | Value | Source |
|--------|-------|--------|
| w_style | 0.32 | Style matching (Exp D) |
| w_vert | 0.26 | Vertical movement (Exp A) |
| w_gap | 0.50 | Gap penalty (Exp B) |

**Key Result:** Judge function correlates with human preference: **Spearman r = 0.812**, p < 0.001

### The "Nintendo Factor"

Levels closer to **Original SMB style** win more often:
- Mahalanobis distance to Original centroid: r = -0.279, p = 0.011
- Style reward: r_style = 1 / (1 + D_M)

### MarioDPO: RLHF-Aligned Level Generation

We trained a generator using **Direct Preference Optimization (DPO)**:

| Component | Details |
|-----------|---------|
| **Base Model** | GPT-2 small, character-level tokenization |
| **Training Data** | 571 human pairs (×10 weight) + 3,500 synthetic pairs |
| **Effective Dataset** | 9,200+ preference pairs |
| **DPO β** | 0.1 |

---

## Generator Rankings

| Rank | Generator | Win Rate | Notes |
|------|-----------|----------|-------|
| 1 | **Original (SMB)** | 89.6% | Hand-crafted baseline |
| 2 | **MarioDPO (ours)** | **83.3%** | 🏆 Best among PCG methods |
| 3 | ORE | 69.3% | Occupancy-based |
| 4 | Notch | 67.4% | Grammar-based |
| 5 | MarioGPT | 63.8% | GPT-2 based |
| ... | ... | ... | |
| 12 | patternOccur | 26.1% | Pattern matching |
| 13 | notchParam | 23.9% | Parameterized grammar |
| 14 | patternCount | 20.4% | Pattern counting |

**Key Achievement:** MarioDPO achieves the **highest win rate among all PCG generators**, second only to hand-crafted Original SMB levels!

---

## Conclusions

1. **Playability > Challenge** — Players prefer levels they can complete
2. **Exploration Matters** — Non-linear, explorable levels win more
3. **Style Matching Works** — Closer to Original SMB → higher win rate
4. **Tags are Valid** — Subjective tags correlate with objective metrics
5. **DPO Alignment Succeeds** — MarioDPO achieves SOTA among PCG methods

---

## Platform Architecture

PCG Arena is a full-stack web application:

| Layer | Technology |
|-------|------------|
| **Frontend** | React + TypeScript, Mario engine ported from Java |
| **Backend** | FastAPI (Python), Glicko-2 rating, AGIS matchmaking |
| **Database** | SQLite (17 tables) |
| **Infrastructure** | Docker, Google Cloud Platform |
| **Auth** | Google OAuth, email/password with SendGrid |

### Key Features

**For Players:**
- Browser-based gameplay (no download)
- Blind A/B comparisons
- Tag gameplay characteristics

**For Researchers:**
- Submit custom generators (ZIP upload)
- Live leaderboard with uncertainty intervals
- Export votes, trajectories, heatmaps

---

## Quick Links

| Resource | Description |
|----------|-------------|
| [Live Platform](https://pcg-arena.com) | Play battles and vote |
| [Leaderboard](https://pcg-arena.com/leaderboard) | Current generator rankings |
| [Builder Profile](https://pcg-arena.com/builder) | Submit your generator |

---

## Repository Structure

```
pcg-arena/
├── backend/          # FastAPI server, Glicko-2, matchmaking
├── frontend/         # React/TypeScript Mario engine
├── db/               # SQLite schema, migrations, seed data
├── eda/              # Exploratory data analysis notebooks
├── MarioDPO/         # DPO training pipeline
├── generators/       # MarioGPT, MarioGAN, MarioDiffusion
├── latex/            # Full research report
└── presentation/     # Beamer slides
```

---

## Adding Your Generator

### Via Web UI (Recommended)
1. Go to [pcg-arena.com/builder](https://pcg-arena.com/builder)
2. Sign in with Google
3. Upload ZIP with 50–200 level files (ASCII tilemap format)
4. Your generator appears on the leaderboard immediately

### Via Seed Data (Developers)
1. Add entry to `db/seed/generators.json`
2. Create `db/seed/levels/{generator_id}/` directory
3. Add `.txt` level files (ASCII tilemap, 16 rows)
4. Restart: `docker compose up --build`

---

## Local Development

```bash
# Backend
docker compose up --build
# → http://localhost:8080

# Frontend (dev mode)
cd frontend && npm install && npm run dev
# → http://localhost:3000

# Tests
cd backend && pytest
```

---

## Future Work

- **Short-term:** More votes, more generators, improved matchmaking
- **Long-term:** Transfer to other games, online DPO training, multi-objective PCG

---

## License

Open source. See LICENSE file for details.
