# Production Build Testing Guide

## Prerequisites
Ensure Node.js and npm are in your PATH. If not, restart your terminal after Node.js installation.

## Test Production Build

### 1. Build the production version
```bash
cd frontend
npm run build
```

This will:
- Use `.env.production` configuration
- Connect to `https://www.pcg-arena.com`
- Create optimized files in `dist/`

### 2. Preview the production build locally
```bash
npm run preview
```

This starts a local server to preview the production build at `http://localhost:4173`.

### 3. Verify the configuration

Open browser DevTools (F12) → Network tab and check:
- API requests go to `https://www.pcg-arena.com` (not localhost)
- Health check endpoint: `/health`
- Battle endpoint: `/v1/battle`

### 4. Test the build

- [ ] Frontend loads without errors
- [ ] Health check succeeds (if backend is accessible)
- [ ] Can start a battle
- [ ] Gameplay works correctly
- [ ] Assets load properly
- [ ] No console errors

## Deploy to Production

Once testing passes, copy the `dist/` folder to your web server:

```bash
# Option 1: Copy to backend static directory
cp -r dist/* ../backend/static/

# Option 2: Deploy to separate static hosting
# Upload dist/ contents to your hosting service
```

## Environment Variables Summary

- **Development**: Uses `.env` → `http://localhost:8080`
- **Production**: Uses `.env.production` → `https://www.pcg-arena.com`
- **Local override**: Create `.env.local` (gitignored) for custom settings

## Troubleshooting

### "npm: command not found"
Node.js is not in your PATH. Restart your terminal or add Node.js to PATH manually.

### API connection fails
- Ensure backend is running and accessible at the configured URL
- Check CORS settings on backend
- Verify DNS is pointing to correct IP (34.116.232.204)

### Assets not loading
- Verify `public/assets/` directory exists
- Check browser console for 404 errors
- Ensure `public/` is included in build


