# GCP Deployment Spec — PCG Arena (Stage 1 → Stage 2)

**Project:** PCG Arena  
**Protocol:** `arena/v0`  
**Last Updated:** 2025-12-26  
**Current State:** ✅ Stage 2 deployed (Frontend + Backend) on a single GCP VM with HTTPS + domain  
**VM Public IP:** `34.116.232.204`  
**Domain:** `pcg-arena.com`, `www.pcg-arena.com`

---

## 0. Purpose of this document

This document describes the full GCP deployment of PCG Arena:

- **Stage 1 (historical):** hosted backend on a VM (public `:8080`), accessed by Java client.
- **Stage 2 (current):** hosted backend + hosted browser frontend under a custom domain with HTTPS.
  - Frontend served as **static files**.
  - Backend remains a Docker container, reachable **only on localhost**.
  - A web server (Caddy) is the single public entrypoint, handling TLS and reverse proxy.

This is intended to be a **reproducible runbook** for:
- provisioning the VM,
- deploying and updating code,
- resetting/rebuilding the DB,
- operating/monitoring the service,
- maintaining security boundaries.

---

## 1. Architecture (Current Stage 2)

### 1.1 Components on the VM

Single GCP Compute Engine VM hosts:

1. **Backend container**
   - FastAPI + Uvicorn
   - Exposes `localhost:8080` **only** (not public)
   - Uses SQLite DB stored on the VM filesystem (persisted across container rebuilds)
2. **SQLite database file**
   - `~/pcg-arena/db/local/arena.sqlite`
   - Persisted outside container via bind mount
3. **Caddy web server**
   - Terminates HTTPS (Let’s Encrypt)
   - Serves static frontend from `/var/www/pcg-arena`
   - Reverse proxies API endpoints to `localhost:8080`

### 1.2 Network behavior

Public internet:
- ✅ `https://www.pcg-arena.com/` → static frontend
- ✅ `https://www.pcg-arena.com/health` → backend via reverse proxy
- ✅ `https://www.pcg-arena.com/v1/*` → backend via reverse proxy

Not exposed publicly:
- ❌ `http://34.116.232.204:8080/*` (blocked; backend bound to localhost, firewall rule removed)

### 1.3 Why this architecture

- **Simple:** one VM, no managed DB services needed
- **Cheap:** compatible with e2-micro free tier; minimal additional costs (static IP)
- **Reliable:** DB survives container restarts; frontend served even when backend restarts
- **Safe-ish by default:** port 8080 not public; single ingress (80/443) controlled by Caddy

---

## 2. GCP Provisioning (Compute Engine VM)

### 2.1 Create a GCP project

- Create a new GCP project (e.g. `pcg-arena`)
- Enable billing (required for VM usage and networking resources)

### 2.2 Create VM instance

Compute Engine → VM instances → Create instance:

Recommended configuration:
- **Name:** `arena-backend`
- **Region:** `us-central1` (free tier eligible)
- **Zone:** any (e.g. `us-central1-a`)
- **Machine type:** `e2-micro` (free tier eligible)
- **Boot disk:** Ubuntu 22.04 LTS
- **Disk type:** Standard persistent disk
- **Disk size:** 10 GB (or slightly higher if storing many assets / backups)
- **Firewall:** enable
  - ✅ Allow HTTP traffic (port 80)
  - ✅ Allow HTTPS traffic (port 443)

### 2.3 Reserve static IP

VPC Network → IP addresses → External IP addresses:
- Reserve a static IPv4 for the VM (regional, same region as VM)
- This IP is used for DNS A records and stable hosting.

Current deployment uses:
- **Static external IP:** `34.116.232.204`

---

## 3. Firewall rules (historical vs current)

### 3.1 Stage 1 firewall (historical)

Stage 1 exposed backend on port `8080` publicly for remote Java client testing.

A firewall rule existed:
- **Name:** `arena-api`
- **Direction:** Ingress
- **Action:** Allow
- **Source:** `0.0.0.0/0`
- **Port:** `tcp:8080`

This allowed:
- `http://<VM_IP>:8080/health`
- `http://<VM_IP>:8080/v1/leaderboard`

### 3.2 Stage 2 firewall (current)

In Stage 2, port `8080` is **NOT** public.

Security change:
- ✅ The `arena-api` firewall rule for `tcp:8080` is deleted/disabled.
- ✅ Only ports **80** and **443** remain public.

Backend is bound to `127.0.0.1` on the VM via docker-compose override (see §6).

---

## 4. Domain + DNS (Namecheap)

### 4.1 Required DNS records

In Namecheap → Domain → Advanced DNS → Host Records:

Create **A records**:

1. Root domain:
- Type: `A Record`
- Host: `@`
- Value: `34.116.232.204`
- TTL: automatic

2. WWW:
- Type: `A Record`
- Host: `www`
- Value: `34.116.232.204`
- TTL: automatic

Remove any URL redirect record previously configured for `@`.

### 4.2 Expected behavior after propagation

- `pcg-arena.com` resolves to VM IP
- `www.pcg-arena.com` resolves to VM IP
- Caddy can request TLS certificates for both hostnames.

---

## 5. VM setup (OS packages)

SSH into VM from GCP Console and run:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git curl
sudo usermod -aG docker $USER
exit
````

Reconnect via SSH and verify:

```bash
docker --version
docker compose version
git --version
```

---

## 6. Backend deployment (Docker Compose)

### 6.1 Repo layout assumptions

Deployment assumes repository exists at:

* `~/pcg-arena`

and contains:

* `docker-compose.yml`
* `backend/`
* `db/seed`, `db/migrations`, `db/local` (local is persisted)
* `frontend/`

### 6.2 Clone and start (first time)

```bash
cd ~
git clone https://github.com/<YOUR_USERNAME>/pcg-arena.git
cd pcg-arena
mkdir -p db/local
docker compose up -d --build
curl -s http://localhost:8080/health
```

### 6.3 Persistent database

SQLite file is persisted by bind mount:

* Host path: `~/pcg-arena/db/local`
* Container path: `/data`
* DB file: `/data/arena.sqlite`

The container is safe to rebuild; DB remains on disk.

### 6.4 VM-specific config pattern (recommended)

Do not keep secrets and VM-specific overrides inside `docker-compose.yml` (tracked by git).

Instead use:

* `docker-compose.override.yml` (local-only, ignored by git)

Example:

```yaml
services:
  backend:
    ports:
      - "127.0.0.1:8080:8080"
    environment:
      - ARENA_DEBUG=true
      - ARENA_ADMIN_KEY=<REDACTED_SECRET>
      - ARENA_PUBLIC_URL=https://www.pcg-arena.com
```

Ensure it is ignored:

```bash
echo "docker-compose.override.yml" >> .gitignore
```

### 6.5 Verify backend health

On VM:

```bash
curl -s http://localhost:8080/health
curl -s http://localhost:8080/v1/leaderboard | head
```

---

## 7. Resetting the database (drop + rebuild from seed)

In Stage 2 setup, dropping DB and rebuilding was acceptable and used for clean state.

Recommended safe flow:

```bash
cd ~/pcg-arena
docker compose down

mkdir -p ~/arena-backups
cp -v ./db/local/arena.sqlite ~/arena-backups/arena.sqlite.$(date +%F_%H%M%S) || true

rm -f ./db/local/arena.sqlite

docker compose up -d --build
curl -s http://localhost:8080/health
```

After rebuild, leaderboard should show seeded generators at initial rating.

---

## 8. Frontend deployment (Stage 2)

### 8.1 Build frontend on the VM

Assuming `frontend/` is a Vite (React + TypeScript) project.

Install Node if needed:

```bash
node -v || true
npm -v || true
sudo apt install -y nodejs npm
```

Build:

```bash
cd ~/pcg-arena/frontend
npm install
npm run build
```

Build output:

* `~/pcg-arena/frontend/dist/`

### 8.2 Static files location

Static files are served from:

* `/var/www/pcg-arena`

Copy build output:

```bash
sudo mkdir -p /var/www/pcg-arena
sudo rm -rf /var/www/pcg-arena/*
sudo cp -r ~/pcg-arena/frontend/dist/* /var/www/pcg-arena/
```

---

## 9. HTTPS + reverse proxy (Caddy)

### 9.1 Install Caddy

```bash
sudo apt update
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl

curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
  | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg

curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
  | sudo tee /etc/apt/sources.list.d/caddy-stable.list

sudo apt update
sudo apt install -y caddy
```

Check status:

```bash
systemctl status caddy --no-pager
```

### 9.2 Configure Caddyfile

Edit:

```bash
sudo nano /etc/caddy/Caddyfile
```

Use:

```caddy
pcg-arena.com, www.pcg-arena.com {
    root * /var/www/pcg-arena
    file_server

    # Single Page App routing (React/Vite)
    try_files {path} /index.html

    # Reverse proxy backend API
    reverse_proxy /v1/* localhost:8080
    reverse_proxy /health localhost:8080
}
```

Restart:

```bash
sudo systemctl restart caddy
sudo systemctl status caddy --no-pager
```

### 9.3 Smoke test (on VM)

```bash
curl -I http://localhost
curl -s http://localhost/health
curl -s http://localhost/v1/leaderboard | head
```

### 9.4 Smoke test (from browser)

* `https://www.pcg-arena.com/`
* `https://www.pcg-arena.com/health`
* `https://www.pcg-arena.com/v1/leaderboard`

---

## 10. Operational commands

### 10.1 Check container status

```bash
cd ~/pcg-arena
docker compose ps
```

Expected:

* backend container is up
* port binding is localhost-only (e.g. `127.0.0.1:8080->8080`)

### 10.2 View backend logs

```bash
cd ~/pcg-arena
docker compose logs -f backend
```

### 10.3 Restart backend container

```bash
cd ~/pcg-arena
docker compose restart backend
```

### 10.4 Update code + rebuild containers

```bash
cd ~/pcg-arena
git pull
docker compose up -d --build
```

### 10.5 Update frontend after changes

```bash
cd ~/pcg-arena/frontend
npm install
npm run build
sudo rm -rf /var/www/pcg-arena/*
sudo cp -r dist/* /var/www/pcg-arena/
sudo systemctl reload caddy
```

---

## 11. Monitoring / uptime checks

### 11.1 Recommended endpoint

Once Stage 2 is deployed, monitor:

* `https://www.pcg-arena.com/health`

not `http://<IP>:8080/health`.

### 11.2 Options

* GCP Monitoring → Uptime checks → HTTP(S) check `/health`
* UptimeRobot (free) → HTTPS monitor on `/health`

---

## 12. Backups (SQLite)

A simple robust backup is a file copy of the SQLite DB, ideally while backend is running but low traffic.

Manual backup:

```bash
mkdir -p ~/backups
cp -v ~/pcg-arena/db/local/arena.sqlite ~/backups/arena.sqlite.$(date +%F_%H%M%S)
```

For automation, a daily cron job at 03:00 UTC:

```bash
crontab -e
```

Add:

```cron
0 3 * * * mkdir -p /home/$USER/backups && cp /home/$USER/pcg-arena/db/local/arena.sqlite /home/$USER/backups/arena.sqlite.$(date +\%F_\%H\%M\%S)
```

(For higher safety under write load, use SQLite online backup APIs or briefly stop container before copying; not required for small scale.)

---

## 13. Security notes / current posture

### 13.1 Port exposure

* Only **80/443** are public
* Backend port **8080** is localhost-only and not accessible externally
* The GCP firewall rule that exposed port 8080 (`arena-api`) was removed

### 13.2 Admin/debug endpoints

Backend debug/admin mode is enabled on this VM for operational convenience:

* `ARENA_DEBUG=true`
* `ARENA_ADMIN_KEY=<secret>`

Recommendations:

* Keep admin key only in `docker-compose.override.yml`
* Do not commit secrets to git
* Consider turning debug off for public demo if not needed

---

## 14. Current “known good” checklist

✅ DNS:

* `pcg-arena.com` → `34.116.232.204`
* `www.pcg-arena.com` → `34.116.232.204`

✅ Firewall:

* inbound 80/443 allowed
* inbound 8080 blocked (no firewall rule; container bound to localhost)

✅ Backend:

* `curl http://localhost:8080/health` works on VM
* DB persisted in `~/pcg-arena/db/local/arena.sqlite`

✅ Caddy:

* `https://www.pcg-arena.com/` serves frontend
* `https://www.pcg-arena.com/health` proxies to backend
* `https://www.pcg-arena.com/v1/leaderboard` proxies to backend

---

## 15. Troubleshooting

### 15.1 HTTPS certificate issues

Common causes:

* DNS not propagated or wrong A records
* port 80/443 not open in firewall
* domain not pointing to the VM public IP

Check:

```bash
sudo journalctl -u caddy --no-pager -n 200
```

### 15.2 Frontend loads but API calls fail

Usually wrong API base URL or cross-origin calls.

Fix:

* Prefer same-origin calls through Caddy proxy (`/v1/*`, `/health`).
* Rebuild frontend if it embeds an old base URL.

### 15.3 Backend not reachable from Caddy

Check backend is listening:

```bash
curl -s http://localhost:8080/health
docker compose ps
docker compose logs --tail=200 backend
```

---

## Appendix A: Key endpoints (Stage 2)

Public:

* `GET https://www.pcg-arena.com/` (frontend)
* `GET https://www.pcg-arena.com/health`
* `GET https://www.pcg-arena.com/v1/leaderboard`
* `POST https://www.pcg-arena.com/v1/battles:next`
* `POST https://www.pcg-arena.com/v1/votes`

Internal (VM):

* `GET http://localhost:8080/health`
* `GET http://localhost:8080/v1/leaderboard`

---

## Appendix B: Example deployment session (commands)

Backend update + DB reset:

```bash
cd ~/pcg-arena
git pull
docker compose down
rm -f ./db/local/arena.sqlite
docker compose up -d --build
curl -s http://localhost:8080/health
```

Frontend build + publish:

```bash
cd ~/pcg-arena/frontend
npm install
npm run build
sudo rm -rf /var/www/pcg-arena/*
sudo cp -r dist/* /var/www/pcg-arena/
sudo systemctl reload caddy
```
