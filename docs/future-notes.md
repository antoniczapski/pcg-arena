# PCG Arena — Future Notes

## Stage 5: Research Analytics (NEXT PRIORITY)

See `docs/stage5-spec.md` for full specification. Key features:

### Stage 5a: Enhanced Data Collection
- [ ] Enhanced telemetry (trajectories, events, death locations)
- [ ] Anonymous persistent player IDs (localStorage + cookie)
- [ ] Per-level statistics table
- [ ] Static level feature extraction

### Stage 5b: Public Statistics
- [ ] Platform statistics page (`/stats`)
- [ ] Enhanced generator page with charts
- [ ] Level detail page with death heatmaps
- [ ] Level gallery sorting options

### Stage 5c: Admin Data Export
- [ ] Research dataset export (CSV/JSON)
- [ ] Trajectory export
- [ ] Date range filtering

---

## Future Ideas (Post Stage 5)

### Level Validation & AI
- [ ] Validate levels with Robin agent (check if passable)
- [ ] AI gameplay finish after player dies (smooth transition)
- [ ] Calibration battles (control battles between best/worst)

### Anti-Abuse
- [ ] IP address rate limiting (hashed, not stored)
- [ ] Scoring alignment verification
- [ ] Admin: kickout builders, delete generators, ban users
- [ ] Throttling per session
- [ ] CAPTCHA for suspicious activity

### UX Improvements
- [ ] Replay option (repeat current level)
- [ ] Score using arrow keys (no mouse required)
- [ ] PCG audio for engagement
- [ ] Exclude repeated level playing

### Platform Growth
- [ ] Community duty: play 10 battles when submitting generator
- [ ] Prepare OAuth for >100 users (Google verification)
- [ ] Hosted deployment with Postgres/managed storage
- [ ] TrueSkill/Bradley-Terry preference model comparison

---

## Completed Items ✅

+ showcase the whole map
+ login + builder profile
+ fix kill mechanics
+ smarter generator selection (AGIS matchmaking)
+ admin mode
+ add statistics for builders (Stage 5 will complete this)

---

## Commands Reference

### DB hard reset
```bash
# Delete database
docker compose down
Remove-Item db\local\arena.sqlite  # PowerShell
# rm db/local/arena.sqlite          # Bash

# Recreate everything from scratch
docker compose up --build
```

### Run Java client against remote
```bash
cd client-java
./gradlew run --args="--base-url http://34.116.232.204:8080"     
```

---

## Known Bugs

- [ ] Internal error when submitting generator with two-letter ID (need min length validation)
- [ ] Site asks for network device permission on first load (investigate)