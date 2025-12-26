# PCG Arena - Public Deployment Guide

## Your Setup
- **Domain**: www.pcg-arena.com
- **Backend IP**: 34.116.232.204
- **Platform**: GCP VM
- **Frontend**: React + TypeScript (built to static files)
- **Backend**: FastAPI + Docker

---

## Pre-Deployment Checklist

### 1. DNS Configuration
Set up your domain to point to your GCP VM:

```
A Record:
  Name: @
  Value: 34.116.232.204
  TTL: 3600

A Record (www subdomain):
  Name: www
  Value: 34.116.232.204
  TTL: 3600
```

Verify DNS propagation:
```bash
nslookup www.pcg-arena.com
# Should return 34.116.232.204
```

### 2. SSL/TLS Certificate
Set up HTTPS using Let's Encrypt (free):

```bash
# On your GCP VM
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d www.pcg-arena.com -d pcg-arena.com
```

### 3. Backend CORS Configuration
Update backend to allow your domain:

```bash
# On your GCP VM, set environment variable
export ARENA_ALLOWED_ORIGINS="https://www.pcg-arena.com,https://pcg-arena.com"
```

Or add to your Docker Compose / systemd service file permanently.

---

## Deployment Steps

### Step 1: Build Frontend Locally

On your Windows machine:

```powershell
cd C:\Users\user\Studia\DataScience\Semestr_V\pcg-arena\frontend
npm install
npm run build
```

This creates optimized files in `frontend/dist/` configured to connect to `https://www.pcg-arena.com`.

### Step 2: Copy Frontend to GCP VM

Use SCP or SFTP to copy the built files:

```powershell
# Using SCP (if you have it)
scp -r dist/* user@34.116.232.204:/path/to/backend/static/

# Or use WinSCP, FileZilla, or similar tool
# Source: C:\Users\user\Studia\DataScience\Semestr_V\pcg-arena\frontend\dist\
# Destination: /path/to/your/backend/static/ on 34.116.232.204
```

### Step 3: Configure Backend to Serve Static Files

On your GCP VM, update `backend/src/main.py`:

```python
from fastapi.staticfiles import StaticFiles

# ... after all API routes are defined ...

# Mount static files (frontend) - MUST be last!
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

**Important**: This must be the LAST mount in your app, after all API routes.

### Step 4: Update Backend Environment

On your GCP VM:

```bash
# Edit your environment file or Docker Compose
export ARENA_ALLOWED_ORIGINS="https://www.pcg-arena.com,https://pcg-arena.com"
export ARENA_PUBLIC_URL="https://www.pcg-arena.com"

# Restart backend
docker compose down
docker compose up -d --build
```

### Step 5: Configure Nginx (Recommended)

Set up Nginx as a reverse proxy on your GCP VM:

```nginx
# /etc/nginx/sites-available/pcg-arena

server {
    listen 80;
    server_name www.pcg-arena.com pcg-arena.com;
    
    # Let's Encrypt will add SSL config here
    
    location / {
        # Serve static files first, fallback to backend
        root /path/to/backend/static;
        try_files $uri $uri/ @backend;
    }
    
    location @backend {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API endpoints go directly to backend
    location /health {
        proxy_pass http://localhost:8080;
    }
    
    location /v1 {
        proxy_pass http://localhost:8080;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/pcg-arena /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Verification Steps

### 1. Check DNS
```bash
nslookup www.pcg-arena.com
# Should show 34.116.232.204
```

### 2. Test Backend Health
```bash
curl https://www.pcg-arena.com/health
# Should return: {"status":"ok","protocol_version":"arena/v0",...}
```

### 3. Test Frontend
Open `https://www.pcg-arena.com` in a browser:
- [ ] Page loads without errors
- [ ] "Connecting to backend..." appears briefly
- [ ] "Start Battle" button appears
- [ ] Click "Start Battle" - battle loads
- [ ] Complete battle flow works

### 4. Check Browser Console
Press F12 → Console:
- [ ] No red errors
- [ ] API requests go to `www.pcg-arena.com` (not localhost)

### 5. Check Network Tab
F12 → Network:
- [ ] `/health` request succeeds
- [ ] `/v1/battle` request succeeds
- [ ] Assets load from `/assets/`

---

## Troubleshooting

### Frontend shows "Failed to connect to backend"
- Check backend is running: `curl http://localhost:8080/health`
- Check CORS settings include your domain
- Check firewall allows port 80/443

### API requests fail with CORS error
Add domain to backend CORS configuration:
```python
allow_origins=["https://www.pcg-arena.com", "https://pcg-arena.com"]
```

### Assets (sprites) not loading
- Verify `public/assets/*.png` files are in `dist/assets/`
- Check Nginx/backend serves static files correctly
- Test: `curl https://www.pcg-arena.com/assets/mariosheet.png`

### SSL certificate issues
Re-run certbot:
```bash
sudo certbot renew --dry-run
sudo certbot --nginx -d www.pcg-arena.com -d pcg-arena.com
```

---

## Update Process

When you make changes:

1. **Code changes**: Rebuild frontend locally (`npm run build`)
2. **Copy dist/ to server**: Use SCP/SFTP
3. **Restart backend**: `docker compose restart` (if needed)
4. **Clear browser cache**: Ctrl+Shift+Delete

---

## Monitoring

Monitor these endpoints:

- Health: `https://www.pcg-arena.com/health`
- Leaderboard: `https://www.pcg-arena.com/v1/leaderboard`

Check logs on GCP VM:
```bash
docker compose logs -f backend
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## Rollback

If something goes wrong:

1. **Frontend**: Replace `static/` with previous version
2. **Backend**: `git checkout <previous-commit>`
3. **Restart**: `docker compose up -d --build`

---

## Next Steps After Deployment

1. Test with multiple users
2. Monitor error rates and performance
3. Set up automated backups
4. Consider CDN for static assets (Cloudflare)
5. Add analytics (Google Analytics, Plausible, etc.)
6. Set up status monitoring (UptimeRobot, Pingdom)


