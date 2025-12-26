# PCG Arena — Stage 1 Specification

**Created:** 2025-12-25  
**Author:** AI-assisted planning  
**Status:** Planning Phase  
**Protocol:** arena/v0 (unchanged from Stage 0)

---

## Table of Contents

1. [Stage 0 Completion Status](#1-stage-0-completion-status)
2. [Missing Stage 0 Tasks](#2-missing-stage-0-tasks)
3. [Stage 1 Overview](#3-stage-1-overview)
4. [Cloud Platform Cost Analysis](#4-cloud-platform-cost-analysis)
5. [Stage 1 Implementation Tasks](#5-stage-1-implementation-tasks)
6. [Stage 1 Non-Implementation Tasks](#6-stage-1-non-implementation-tasks)
7. [Deployment Guide](#7-deployment-guide)
8. [Success Criteria](#8-success-criteria)

---

## 1. Stage 0 Completion Status

### 1.1 Summary

**Stage 0 is SUBSTANTIALLY COMPLETE** ✅

The core end-to-end loop works locally:
- Battle assignment → Play two levels → Vote → Update leaderboard
- Data persists across container restarts
- Demo scripts validate the full flow

### 1.2 Component Completion Matrix

| Component | Status | Details |
|-----------|--------|---------|
| **Backend API** | ✅ Complete | All 4 core endpoints + debug endpoints |
| **Database** | ✅ Complete | SQLite with 7 tables, migrations, indexes |
| **Persistence** | ✅ Complete | Docker volume mount survives restarts |
| **Seed Data** | ✅ Complete | 3 generators, 30 levels |
| **ELO Ratings** | ✅ Complete | Update logic, atomic transactions |
| **Java Client Phase 1** | ✅ Complete | Static battle viewer, vote submission |
| **Java Client Phase 2** | ✅ Complete | Full Mario gameplay integration |

### 1.3 Backend Endpoints (All Implemented)

| Endpoint | Status | Description |
|----------|--------|-------------|
| `GET /health` | ✅ | Health check with protocol version |
| `GET /` | ✅ | HTML leaderboard for browsers |
| `GET /v1/leaderboard` | ✅ | JSON leaderboard API |
| `POST /v1/battles:next` | ✅ | Issue new battle with two levels |
| `POST /v1/votes` | ✅ | Submit vote, update ratings |
| `GET /debug/db-status` | ✅ | Database statistics (debug mode) |
| `GET /debug/battles` | ✅ | List battles (debug mode) |
| `GET /debug/votes` | ✅ | List votes (debug mode) |

### 1.4 Java Client Features (All Implemented)

**Phase 1 (Static Viewer):**
- ✅ Health check and protocol validation
- ✅ Battle fetching with session management
- ✅ Static tilemap rendering (colored tiles)
- ✅ Vote submission with tags
- ✅ Leaderboard display and refresh
- ✅ Error handling with recovery
- ✅ Logging to `logs/client.log`

**Phase 2 (Gameplay Integration):**
- ✅ Mario game engine ported from Mario AI Framework
- ✅ Sequential play (left then right)
- ✅ SPACE to start gameplay
- ✅ Full physics and enemy mechanics
- ✅ Telemetry collection (deaths, coins, time, etc.)
- ✅ Skip functionality for broken levels

### 1.5 Seed Data Inventory

```
db/seed/
├── generators.json      # 3 generators: hopper, genetic, notch
└── levels/
    ├── genetic/         # 10 levels
    ├── hopper/          # 10 levels
    └── notch/           # 10 levels
```

**Mario AI Framework levels available but not imported:**
```
Mario-AI-Framework-PCG/levels/
├── ge/              # 1000 levels
├── hopper/          # 1000 levels
├── notch/           # 1000 levels
├── notchParam/      # 1000 levels
├── notchParamRand/  # 1001 levels
├── ore/             # 1000 levels
├── patternCount/    # 1000 levels
├── patternOccur/    # 1000 levels
├── patternWeightCount/ # 1000 levels
└── original/        # 15 levels (human-designed)
```

### 1.6 Stage 0 Success Criteria Check

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Run 10+ battles end-to-end | ✅ | `demo.ps1` script runs 10 battles |
| Ratings update after votes | ✅ | ELO logic in `main.py` |
| Ratings persist across restart | ✅ | SQLite file outside container |
| Audit logs for debugging | ✅ | `rating_events` table, `votes` table |

---

## 2. Missing Stage 0 Tasks

### 2.1 Required Before Stage 1

| ID | Task | Priority | Est. Hours | Description |
|----|------|----------|------------|-------------|
| **S0-1** | Update README.md | High | 1 | README still says "Java client ⏳ Not started" — needs update to reflect complete Phase 1+2 |
| **S0-2** | Phase 2 Acceptance Testing | High | 2 | Run through `ACCEPTANCE.md` checklist for gameplay features |
| **S0-3** | Build Fat JAR | High | 1 | Verify `./gradlew build` produces standalone runnable JAR |
| **S0-4** | Document Client Distribution | Medium | 1 | Add instructions for distributing JAR to testers |

**Total: ~5 hours**

### 2.2 Task Details

#### S0-1: Update README.md

**Current state:** README says:
```
| **Java client** | ⏳ Not started | High - gameplay + vote UI |
```

**Required changes:**
1. Update implementation status table to show Java client complete
2. Add Java client quick start instructions
3. Document Phase 2 gameplay features
4. Add troubleshooting section for Java client

---

#### S0-2: Phase 2 Acceptance Testing

**Description:** Execute the acceptance tests in `client-java/ACCEPTANCE.md` for Phase 2 gameplay features.

**Key test cases:**
- [ ] Play left level with full gameplay
- [ ] Play right level with full gameplay
- [ ] Verify telemetry is submitted in vote
- [ ] Verify ratings update correctly
- [ ] Test skip functionality
- [ ] Test persistence across restart

---

#### S0-3: Build Fat JAR

**Description:** Verify the client can be distributed as a single executable JAR.

**Steps:**
```bash
cd client-java
./gradlew clean build
java -jar build/libs/client-java-0.1.0.jar
```

**Verify:**
- JAR file exists and is reasonably sized (~5-10 MB)
- Runs without additional dependencies
- Assets are bundled inside JAR

---

#### S0-4: Document Client Distribution

**Description:** Create clear instructions for testers to download and run the client.

**Contents:**
- Prerequisites (Java 11+)
- Download link (GitHub releases or direct share)
- How to configure backend URL
- Troubleshooting common issues

---

### 2.3 Nice-to-Have (Not Blocking)

| ID | Task | Priority | Description |
|----|------|----------|-------------|
| S0-5 | Expand seed levels | Low | Import more levels from Mario AI Framework |
| S0-6 | Add more generators | Low | Add notchParam, ore, pattern generators |
| S0-7 | Unit tests for Java client | Low | Add JUnit tests for API client, tilemap parser |

---

## 3. Stage 1 Overview

### 3.1 Purpose

**Stage 1: MVP Public Pilot**

Deploy the backend to cloud hosting so a small group of testers can rate levels remotely. Collect real preference data with minimal ops burden.

### 3.2 What Changes from Stage 0

| Aspect | Stage 0 | Stage 1 |
|--------|---------|---------|
| Backend location | Docker on localhost | VM or container in cloud |
| Database | SQLite on local volume | SQLite on VM disk or cloud storage |
| Client connection | `localhost:8080` | Public URL (e.g., `https://arena.example.com`) |
| Access | Developer only | Small tester group |
| Backups | Manual file copy | Automated daily backups |

### 3.3 What Stays the Same

- Protocol: `arena/v0` (no changes)
- API endpoints: Same structure
- Java client: Same code, just different `--base-url`
- Rating system: Same ELO logic

### 3.4 Scope

**In Scope:**
- Hosted backend on single VM/container
- SQLite persistence on VM disk
- HTTPS endpoint with domain
- Minimal web portal (leaderboard + download link)
- Daily database backups
- Basic admin controls (via debug endpoints)

**Out of Scope:**
- User accounts / authentication
- Browser-playable Mario
- Anti-cheat systems
- Horizontal scaling
- Managed database (PostgreSQL)

---

## 4. Cloud Platform Cost Analysis

### 4.1 Requirements for Stage 1

| Requirement | Specification |
|-------------|---------------|
| Compute | 1 vCPU, 1-2 GB RAM (sufficient for <100 users) |
| Storage | 10 GB SSD (SQLite + backups) |
| Network | Low traffic (~1 GB/month egress) |
| Uptime | 99% (can tolerate brief downtime) |
| SSL | Required (HTTPS) |
| Domain | Custom domain (optional but nice) |

### 4.2 Platform Comparison

#### Google Cloud Platform (GCP)

**Option A: Compute Engine VM (e2-micro/e2-small)**

| Resource | Spec | Monthly Cost |
|----------|------|--------------|
| VM (e2-micro) | 0.25 vCPU, 1 GB RAM | $6-8 |
| VM (e2-small) | 0.5 vCPU, 2 GB RAM | $13-15 |
| Boot disk | 10 GB SSD | $1-2 |
| Static IP | 1 external IP | $3-4 |
| Egress | 1 GB/month | Free (first 1 GB) |
| **Total (e2-micro)** | | **~$10-14/month** |
| **Total (e2-small)** | | **~$18-22/month** |

**Pros:**
- Free tier: 1 e2-micro instance per month (always free)
- Simple VM setup, full control
- SQLite on local disk (no extra cost)
- $300 free trial credit for 90 days

**Cons:**
- Requires manual VM management
- No auto-scaling (not needed for Stage 1)

**Option B: Cloud Run (Container-based)**

| Resource | Spec | Monthly Cost |
|----------|------|--------------|
| CPU | Pay per request | ~$0.00002/request |
| Memory | 512 MB-1 GB | ~$0.00001/GiB-second |
| Requests | ~1000 battles/month | ~$1-3 |
| Cloud Storage | For SQLite | ~$0.02/GB = $0.20 |
| **Total** | | **~$2-5/month** |

**Pros:**
- Very cheap for low traffic
- Auto-scaling (not needed but nice)
- Managed infrastructure

**Cons:**
- SQLite doesn't work well (ephemeral containers)
- Would need Cloud SQL (~$10-25/month) or GCS-based storage
- Adds complexity for minimal benefit

**Recommendation for GCP:** Compute Engine e2-micro (Free Tier)

---

#### Amazon Web Services (AWS)

**Option A: EC2 (t3.micro/t3.small)**

| Resource | Spec | Monthly Cost |
|----------|------|--------------|
| t3.micro | 2 vCPU, 1 GB RAM | $8-10 |
| t3.small | 2 vCPU, 2 GB RAM | $15-18 |
| EBS Storage | 10 GB gp3 | $1-2 |
| Elastic IP | 1 IP | $3-4 |
| **Total (t3.micro)** | | **~$12-16/month** |

**Pros:**
- 12-month free tier (750 hours t3.micro)
- Mature ecosystem
- Easy to migrate later

**Cons:**
- Free tier expires after 12 months
- More complex pricing than GCP

**Option B: Lightsail (Simplified VPS)**

| Resource | Spec | Monthly Cost |
|----------|------|--------------|
| Lightsail | 1 vCPU, 1 GB RAM, 40 GB SSD | **$5/month** |
| Lightsail | 1 vCPU, 2 GB RAM, 60 GB SSD | **$10/month** |

**Pros:**
- Simplest AWS option
- Predictable pricing
- Includes storage, IP, transfer
- 3-month free trial

**Cons:**
- Less flexibility than EC2
- Still AWS complexity for setup

**Recommendation for AWS:** Lightsail $5/month or t3.micro (Free Tier)

---

#### Microsoft Azure

**Option A: Azure VM (B1s/B1ms)**

| Resource | Spec | Monthly Cost |
|----------|------|--------------|
| B1s | 1 vCPU, 1 GB RAM | $7-10 |
| B1ms | 1 vCPU, 2 GB RAM | $15-18 |
| Disk | 32 GB | $1-2 |
| Static IP | 1 IP | $3-4 |
| **Total (B1s)** | | **~$12-16/month** |

**Pros:**
- 12-month free tier (750 hours B1s)
- Good integration with VS Code

**Cons:**
- Similar to AWS in complexity
- No "always free" tier like GCP

---

#### DigitalOcean

**Droplet (Basic)**

| Resource | Spec | Monthly Cost |
|----------|------|--------------|
| Basic Droplet | 1 vCPU, 1 GB RAM, 25 GB SSD | **$6/month** |
| Basic Droplet | 1 vCPU, 2 GB RAM, 50 GB SSD | **$12/month** |

**Pros:**
- Simple, developer-friendly
- Predictable pricing
- Good documentation
- Free $200 credit for 60 days (new users)

**Cons:**
- No always-free tier
- Less ecosystem than big 3

---

#### Hetzner Cloud

**CX11 (Cheapest)**

| Resource | Spec | Monthly Cost |
|----------|------|--------------|
| CX11 | 1 vCPU, 2 GB RAM, 20 GB SSD | **€3.79/month (~$4)** |
| CX21 | 2 vCPU, 4 GB RAM, 40 GB SSD | **€5.77/month (~$6)** |

**Pros:**
- Cheapest option by far
- European data centers (GDPR-friendly)
- Simple pricing

**Cons:**
- Smaller company than big 3
- Fewer managed services
- EU-only data centers (latency for US users)

---

#### Fly.io

**Pay-as-you-go**

| Resource | Spec | Monthly Cost |
|----------|------|--------------|
| Shared CPU | 256 MB RAM | Free tier (up to 3 VMs) |
| Shared CPU | 1 GB RAM | ~$5-7/month |
| Persistent Volume | 3 GB | Free tier |
| Persistent Volume | 10 GB | ~$1.50/month |
| **Total** | | **Free - $10/month** |

**Pros:**
- Free tier with persistent volumes
- Container-native (uses your Dockerfile)
- Simple deployment (`fly deploy`)
- Global edge network

**Cons:**
- Less mature than big 3
- Pricing can be unpredictable at scale

---

#### Render

**Web Service**

| Resource | Spec | Monthly Cost |
|----------|------|--------------|
| Free tier | Spins down after 15 min inactivity | Free |
| Starter | 0.5 vCPU, 512 MB RAM | $7/month |
| Standard | 1 vCPU, 2 GB RAM | $25/month |
| Persistent Disk | 1 GB | $0.25/month |
| **Total (Starter + Disk)** | | **~$8-10/month** |

**Pros:**
- Simple deployment from Git
- Automatic HTTPS
- Easy to use

**Cons:**
- Free tier spins down (30-second cold start)
- Persistent disk requires paid plan
- More expensive than raw VMs

---

### 4.3 Cost Comparison Summary

| Platform | Tier | Monthly Cost | Free Trial |
|----------|------|--------------|------------|
| **GCP Compute Engine** | e2-micro | $0 (always free) | $300/90 days |
| **Hetzner** | CX11 | ~$4 | None |
| **AWS Lightsail** | 1GB | $5 | 3 months |
| **Fly.io** | Shared | $0-7 | Free tier |
| **DigitalOcean** | Basic | $6 | $200/60 days |
| **Render** | Starter | $8 | Free tier (sleeps) |
| **Azure** | B1s | $12-16 | $200/30 days |
| **AWS EC2** | t3.micro | $12-16 | 12 months |

### 4.4 Recommendation

**Primary Recommendation: Google Cloud Platform (Compute Engine e2-micro)**

**Why:**
1. **Free Tier:** e2-micro is always free (1 instance per month in us-west1, us-central1, or us-east1)
2. **$300 Credit:** Additional credit for 90 days if you need more resources
3. **Simple:** VM with Docker is straightforward
4. **Familiar:** GCP is widely used, good documentation
5. **Flexible:** Easy to upgrade later if needed

**Alternative: Fly.io**

**Why:**
1. Container-native (your Dockerfile works directly)
2. Free tier with persistent volumes
3. Very simple deployment (`fly deploy`)
4. Good for "deploy and forget" scenarios

**Budget Option: Hetzner CX11 (~$4/month)**

If free tier is not available or you want a European server.

---

## 5. Stage 1 Implementation Tasks

### 5.1 Backend Changes

| ID | Task | Priority | Est. Hours | Description |
|----|------|----------|------------|-------------|
| **S1-B1** | Add CORS headers | High | 1 | Allow browser access to API |
| **S1-B2** | Environment-based config | High | 2 | Support `ARENA_BASE_URL`, cloud database paths |
| **S1-B3** | Health check improvements | Medium | 1 | Add uptime, version info for monitoring |
| **S1-B4** | Request logging | Medium | 2 | Log all requests with session_id for debugging |
| **S1-B5** | Rate limiting (basic) | Low | 2 | Prevent abuse (100 requests/minute per IP) |

**Total Backend: ~8 hours**

---

### 5.2 Task Details

#### S1-B1: Add CORS Headers

**Description:** The backend needs CORS headers so browsers can call the API (for future web portal).

**Changes to `main.py`:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

#### S1-B2: Environment-Based Configuration

**Description:** Cloud deployment needs configurable settings.

**New environment variables:**
```
ARENA_PUBLIC_URL=https://arena.example.com
ARENA_ALLOWED_ORIGINS=https://arena.example.com
ARENA_LOG_LEVEL=INFO
ARENA_BACKUP_PATH=/backups
```

---

#### S1-B3: Health Check Improvements

**Description:** Add more info to `/health` for monitoring.

**New fields:**
```json
{
  "uptime_seconds": 86400,
  "requests_total": 1500,
  "battles_served": 300,
  "votes_received": 280,
  "db_size_bytes": 1048576
}
```

---

#### S1-B4: Request Logging

**Description:** Log all API requests for debugging and audit.

**Log format:**
```
2025-01-15 10:30:00 POST /v1/votes session=abc123 battle=btl_xyz status=200 duration=45ms
```

---

#### S1-B5: Rate Limiting (Optional)

**Description:** Prevent abuse with basic rate limiting.

**Implementation:**
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/v1/battles:next")
@limiter.limit("10/minute")
async def next_battle(request: Request):
    ...
```

---

### 5.3 Web Portal (Minimal)

**Status:** SKIPPED - Not needed for Java client deployment

All web portal tasks have been removed as they are not required for Stage 1 deployment with Java client. Future browser-based frontend will be implemented in later stages.

---

### 5.4 Admin Endpoints

| ID | Task | Priority | Est. Hours | Description |
|----|------|----------|------------|-------------|
| **S1-A1** | Generator enable/disable | High | 2 | `POST /admin/generators/{id}/disable` |
| **S1-A2** | Season reset | Medium | 2 | `POST /admin/season/reset` |
| **S1-A3** | Session flagging | Low | 2 | `POST /admin/sessions/{id}/flag` |
| **S1-A4** | Backup trigger | Medium | 1 | `POST /admin/backup` |

**Total Admin: ~7 hours**

**Note:** Admin endpoints should be protected with a simple API key:
```
Authorization: Bearer ARENA_ADMIN_KEY
```

---

### 5.5 Backup System

| ID | Task | Priority | Est. Hours | Description |
|----|------|----------|------------|-------------|
| **S1-K1** | Backup script | High | 2 | Script to copy SQLite to backup location |
| **S1-K2** | Cron job for daily backups | High | 1 | Schedule daily at 3 AM UTC |
| **S1-K3** | Backup rotation | Medium | 1 | Keep last 7 daily backups |
| **S1-K4** | Restore documentation | Medium | 1 | How to restore from backup |

**Total Backup: ~5 hours**

---

### 5.6 Level Pool Expansion (Optional)

| ID | Task | Priority | Est. Hours | Description |
|----|------|----------|------------|-------------|
| **S1-L1** | Import 100 levels per generator | Low | 2 | From Mario AI Framework (genetic, hopper, notch) |
| **S1-L2** | Add new generators | Low | 2 | Add 2-3 more generators from framework |

**Total Levels: ~4 hours**

---

### 5.7 Implementation Summary

| Category | Tasks | Total Hours |
|----------|-------|-------------|
| Backend changes | 5 | 8 |
| Web portal | 0 | 0 |
| Admin endpoints | 4 | 7 |
| Backup system | 4 | 5 |
| Level expansion | 2 | 4 |
| **TOTAL** | **15** | **24 hours** |

---

## 6. Stage 1 Non-Implementation Tasks

These are operational tasks that don't require code changes.

### 6.1 Cloud Setup (GCP Recommended)

#### Step 1: Create GCP Account and Project

1. Go to https://console.cloud.google.com
2. Sign in with Google account
3. Accept terms, start free trial ($300 credit)
4. Create new project: "pcg-arena"
5. Enable billing (required, won't charge for free tier)

**Time estimate:** 15 minutes

---

#### Step 2: Create Compute Engine VM

1. Go to Compute Engine → VM instances
2. Click "Create Instance"
3. Configure:
   - **Name:** `arena-backend`
   - **Region:** `us-central1` (free tier eligible)
   - **Machine type:** `e2-micro` (free tier)
   - **Boot disk:**
     - OS: Ubuntu 22.04 LTS
     - Size: 10 GB
     - Type: Standard persistent disk
   - **Firewall:** Allow HTTP and HTTPS traffic
4. Click "Create"

**Time estimate:** 10 minutes

---

#### Step 3: Reserve Static IP

1. Go to VPC network → External IP addresses
2. Click "Reserve Static Address"
3. Configure:
   - **Name:** `arena-ip`
   - **Region:** Same as VM
   - **Attached to:** Your VM instance
4. Note the IP address

**Time estimate:** 5 minutes

---

#### Step 4: Configure Firewall Rules

1. Go to VPC network → Firewall
2. Create rule for port 8080:
   - **Name:** `arena-api`
   - **Direction:** Ingress
   - **Targets:** All instances (or specific network tag)
   - **Source:** 0.0.0.0/0
   - **Ports:** tcp:8080

**Time estimate:** 5 minutes

---

#### Step 5: SSH into VM and Install Docker

```bash
# SSH from GCP Console or:
gcloud compute ssh arena-backend --zone=us-central1-a

# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER

# Logout and login again for group change
exit
gcloud compute ssh arena-backend --zone=us-central1-a

# Verify
docker --version
docker compose version
```

**Time estimate:** 15 minutes

---

#### Step 6: Deploy Backend

```bash
# Clone repository
git clone https://github.com/YOUR_REPO/pcg-arena.git
cd pcg-arena

# Create data directory for persistence
mkdir -p db/local

# Start backend
docker compose up -d --build

# Verify
curl http://localhost:8080/health
```

**Time estimate:** 10 minutes

---

#### Step 7: Set Up HTTPS with Caddy (Optional but Recommended)

```bash
# Install Caddy
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# Create Caddyfile
sudo nano /etc/caddy/Caddyfile
```

**Caddyfile content:**
```
arena.yourdomain.com {
    reverse_proxy localhost:8080
}
```

```bash
# Restart Caddy
sudo systemctl restart caddy

# Caddy automatically provisions SSL certificate via Let's Encrypt
```

**Time estimate:** 20 minutes

---

#### Step 8: Configure Domain (Optional)

1. Go to your domain registrar (e.g., Namecheap, Cloudflare)
2. Add DNS A record:
   - **Name:** `arena` (or `@` for root)
   - **Type:** A
   - **Value:** Your static IP
3. Wait for DNS propagation (5-30 minutes)

**Time estimate:** 10 minutes + propagation wait

---

#### Step 9: Set Up Daily Backups

```bash
# Create backup script
sudo nano /opt/arena-backup.sh
```

**Script content:**
```bash
#!/bin/bash
BACKUP_DIR="/home/$USER/backups"
DB_PATH="/home/$USER/pcg-arena/db/local/arena.sqlite"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR
cp $DB_PATH $BACKUP_DIR/arena-$DATE.sqlite

# Keep only last 7 backups
ls -t $BACKUP_DIR/arena-*.sqlite | tail -n +8 | xargs -r rm
```

```bash
# Make executable
sudo chmod +x /opt/arena-backup.sh

# Add cron job for daily 3 AM UTC
crontab -e
# Add line:
0 3 * * * /opt/arena-backup.sh
```

**Time estimate:** 10 minutes

---

#### Step 10: Configure Monitoring (Optional)

**Option A: GCP Monitoring (Free)**
1. Go to Monitoring in GCP Console
2. Create uptime check for your URL
3. Set up alert policy for downtime

**Option B: External monitoring**
- UptimeRobot (free): https://uptimerobot.com
- Create HTTP monitor for your health endpoint

**Time estimate:** 15 minutes

---

### 6.2 Non-Implementation Task Summary

| Step | Task | Time Est. |
|------|------|-----------|
| 1 | Create GCP account and project | 15 min |
| 2 | Create Compute Engine VM | 10 min |
| 3 | Reserve static IP | 5 min |
| 4 | Configure firewall rules | 5 min |
| 5 | SSH and install Docker | 15 min |
| 6 | Deploy backend | 10 min |
| 7 | Set up HTTPS with Caddy | 20 min |
| 8 | Configure domain (optional) | 10 min |
| 9 | Set up daily backups | 10 min |
| 10 | Configure monitoring | 15 min |
| **TOTAL** | | **~2 hours** |

---

### 6.3 Client Distribution

#### Option A: GitHub Releases

1. Create GitHub release
2. Build fat JAR: `./gradlew clean build`
3. Upload `client-java-0.1.0.jar` to release
4. Link from web portal

#### Option B: Direct Download

1. Host JAR on the same server
2. Serve via Caddy: `arena.yourdomain.com/downloads/client-java.jar`

#### Option C: Google Drive/Dropbox

1. Upload JAR to cloud storage
2. Share public link
3. Link from web portal

---

### 6.4 Tester Onboarding

Create instructions for testers:

```markdown
# How to Join PCG Arena Testing

## Requirements
- Java 11 or newer
- Windows, macOS, or Linux

## Quick Start
1. Download the client: [client-java.jar](link)
2. Open terminal/command prompt
3. Run: `java -jar client-java.jar --base-url https://arena.yourdomain.com`
4. Play and vote!

## Controls
- Arrow keys: Move
- S: Jump
- A: Run/Fire

## Feedback
Report issues at: [GitHub Issues link]
```

---

## 7. Deployment Guide

### 7.1 Pre-Deployment Checklist

- [ ] Complete Stage 0 missing tasks (S0-1 to S0-4)
- [ ] Build and test client JAR locally
- [ ] Verify backend runs with `docker compose up`
- [ ] Run demo script successfully
- [ ] Have GCP account ready

### 7.2 Deployment Commands (GCP)

```bash
# On VM after cloning repo:

# 1. Start backend
cd pcg-arena
docker compose up -d --build

# 2. Verify
curl http://localhost:8080/health
curl http://localhost:8080/v1/leaderboard

# 3. Check logs
docker compose logs -f backend

# 4. Update (after code changes)
git pull
docker compose up -d --build
```

### 7.3 Rollback Procedure

```bash
# Stop current deployment
docker compose down

# Restore from backup
cp ~/backups/arena-YYYYMMDD.sqlite db/local/arena.sqlite

# Restart
docker compose up -d
```

### 7.4 Monitoring Commands

```bash
# Check container status
docker compose ps

# View logs
docker compose logs --tail=100 backend

# Database stats
curl http://localhost:8080/debug/db-status

# Check disk space
df -h
```

---

## 8. Success Criteria

### 8.1 Stage 1 Definition of Done

| Criterion | Measurement |
|-----------|-------------|
| Backend accessible online | `curl https://arena.yourdomain.com/health` returns 200 |
| Client connects to cloud backend | Configure with `--base-url`, battles load |
| Data persists across container restart | Stop/start container, leaderboard unchanged |
| Daily backups running | Backup files exist in backup directory |
| 100+ battles completed | Check via `/debug/db-status` or leaderboard |
| Leaderboard shows rating changes | Generators have different ratings after votes |
| No data loss incidents | Verified by audit log consistency |

### 8.2 Acceptance Testing (Stage 1)

1. **Remote Access Test**
   - [ ] Health endpoint accessible from internet
   - [ ] Leaderboard loads in browser
   - [ ] API responds to client requests

2. **Persistence Test**
   - [ ] Submit 5 votes
   - [ ] Restart container (`docker compose restart`)
   - [ ] Leaderboard shows same data

3. **Backup Test**
   - [ ] Trigger manual backup
   - [ ] Verify backup file exists
   - [ ] Test restore procedure

4. **Multi-User Test**
   - [ ] Two different clients connect simultaneously
   - [ ] Both can fetch battles and vote
   - [ ] Leaderboard updates for both

5. **Longevity Test**
   - [ ] Run for 24 hours
   - [ ] Collect 50+ battles
   - [ ] No crashes or data corruption

---

## Appendix A: Quick Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ARENA_DB_PATH` | `/data/arena.sqlite` | Database file path |
| `ARENA_HOST` | `0.0.0.0` | Bind address |
| `ARENA_PORT` | `8080` | HTTP port |
| `ARENA_INITIAL_RATING` | `1000.0` | Starting ELO |
| `ARENA_K_FACTOR` | `24` | ELO K-factor |
| `ARENA_DEBUG` | `false` | Enable debug endpoints |
| `ARENA_ADMIN_KEY` | None | Admin API key |

### Common Commands

```bash
# Start
docker compose up -d --build

# Stop
docker compose down

# View logs
docker compose logs -f backend

# Restart
docker compose restart

# Rebuild
docker compose up -d --build

# Check status
docker compose ps
```

### URLs

| Endpoint | Purpose |
|----------|---------|
| `/health` | Health check |
| `/` | HTML leaderboard |
| `/v1/leaderboard` | JSON leaderboard |
| `/v1/battles:next` | Get next battle |
| `/v1/votes` | Submit vote |
| `/debug/db-status` | DB stats (debug) |

---

## Appendix B: Alternative Deployment (Fly.io)

If you prefer Fly.io over GCP:

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch app
cd pcg-arena
fly launch

# Create persistent volume
fly volumes create arena_data --size 1 --region ord

# Deploy
fly deploy

# Set secrets
fly secrets set ARENA_ADMIN_KEY=your-secret-key

# View logs
fly logs
```

**Fly.toml configuration:**
```toml
app = "pcg-arena"
primary_region = "ord"

[build]
  dockerfile = "backend/Dockerfile"

[mounts]
  source = "arena_data"
  destination = "/data"

[[services]]
  http_checks = []
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

---

---

## 9. Stage 1 Completion Status

**Status:** ✅ COMPLETE (Deployed 2025-12-26)

### Deployment Summary

**Infrastructure:**
- Platform: Google Cloud Platform (GCP)
- VM: Compute Engine e2-micro (free tier)
- Region: us-central1
- OS: Ubuntu 22.04 LTS
- Database: SQLite on persistent disk
- Cost: ~$3-4/month (static IP only)

**Implementation Completed:**
- ✅ All backend changes (S1-B1 through S1-B5)
- ✅ Admin endpoints with Bearer token authentication (S1-A1 through S1-A4)
- ✅ Backup system with scripts for Windows and Linux (S1-K1 through S1-K4)
- ✅ Level pool maintained at 30 levels for initial deployment
- ✅ Environment-based configuration implemented
- ✅ Remote connectivity validated with Java client

**Operational Setup:**
- ✅ VM created and configured
- ✅ Static IP reserved and attached
- ✅ Firewall rules configured (port 8080)
- ✅ Docker installed and backend deployed
- ✅ Daily backups configured
- ✅ Health monitoring available

**Testing Results:**
- ✅ Health check responds with metrics
- ✅ Battle creation works remotely
- ✅ Vote submission works remotely
- ✅ Leaderboard updates correctly
- ✅ Java client connects successfully
- ✅ Admin endpoints secured with key
- ✅ Backup/restore scripts verified

### Lessons Learned

1. **Docker Compose syntax:** Multiple compose files (compose.yml vs docker-compose.yml) can cause conflicts. Standardized on docker-compose.yml.

2. **Environment variables:** Backend configuration fully externalized via env vars, making deployment flexible.

3. **Cost optimization:** GCP e2-micro free tier is perfect for Stage 1 validation phase. Static IP is the only recurring cost.

4. **Remote testing:** Java client `--base-url` flag works perfectly for connecting to cloud backend without code changes.

5. **Persistence verified:** Database survives container restarts and rebuilds as expected.

### Next Phase: Stage 2 (Browser Frontend)

Stage 1 has validated:
- ✅ Cloud deployment model works
- ✅ Backend API is stable and remotely accessible
- ✅ CORS and rate limiting are in place
- ✅ Operational procedures (backups, monitoring) are established

**Ready to proceed with browser-based frontend implementation.**

---

**End of Stage 1 Specification**

**Stage 1 Achievement:** Successfully transitioned from local-only prototype to cloud-hosted validation platform with operational excellence. 🚀

