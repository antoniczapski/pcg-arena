# Secrets Management

## Overview

This project uses environment variables to manage secrets. Secrets are **never committed to git**.

## Files

- **`.env`** - Your local secrets (ignored by git)
- **`.env.example`** - Template file (committed to git)

## Setup

### Local Development

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Fill in your actual values in `.env`

3. The values are used by:
   - Docker Compose (backend)
   - Vite build (frontend)

### Production Deployment (GCP VM)

1. SSH into your VM
2. Create `/opt/pcg-arena/.env` (or wherever you deploy)
3. Copy the contents of `.env.example`
4. Fill in production values:
   - Use production URLs (`https://pcg-arena.com`)
   - **IMPORTANT**: Set `DEV_AUTH=false` and `VITE_DEV_AUTH=false`
   - Use production SendGrid API key
   - Use production Google Client ID

## Required Secrets

### SendGrid (Email Verification)

- **SENDGRID_API_KEY**: Get from https://app.sendgrid.com/settings/api_keys
- **SENDGRID_FROM_EMAIL**: Must be verified in SendGrid
- **SENDGRID_FROM_NAME**: Display name for emails

### Google OAuth

- **GOOGLE_CLIENT_ID**: From Google Cloud Console
  - Same value used in both backend and frontend

### Configuration

- **PUBLIC_URL**: Your site's public URL (for cookies/CORS)
- **DEV_AUTH**: MUST be `false` in production

## Security Checklist

- [ ] `.env` is in `.gitignore`
- [ ] `.env` is never committed
- [ ] Production `.env` has `DEV_AUTH=false`
- [ ] Production `.env` has real API keys
- [ ] Production VM `.env` has proper file permissions (chmod 600)

## Troubleshooting

**Q: My secrets are not loading**
- Docker: Restart containers (`docker compose down && docker compose up -d`)
- Frontend: Clear Vite cache and rebuild

**Q: I accidentally committed secrets**
- Immediately rotate all exposed keys
- Use `git filter-branch` or BFG Repo-Cleaner to remove from history
- Never reuse compromised keys

