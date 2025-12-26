# PCG Arena Frontend - Quick Start Guide

## Prerequisites Check

Before starting, ensure you have:

- ✅ Node.js 18+ installed (`node --version` to check)
- ✅ npm installed (comes with Node.js)
- ✅ Backend running at `localhost:8080`

## 5-Minute Setup

### 1. Install Node.js (if needed)

**Windows:**
1. Download from https://nodejs.org/ (LTS version)
2. Run installer
3. Restart terminal/PowerShell
4. Verify: `node --version` should show v18+ or v20+

**Mac/Linux:**
```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
```

### 2. Install Dependencies

```bash
cd frontend
npm install
```

This will take 1-2 minutes. You should see output like:

```
added 234 packages, and audited 235 packages in 45s
```

### 3. Start Development Server

```bash
npm run dev
```

You should see:

```
  VITE v5.0.8  ready in 432 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### 4. Open in Browser

Navigate to http://localhost:3000

You should see the PCG Arena welcome screen!

## First Test

1. **Click "Start Battle"**
   - Battle should load
   - You'll see "Loading assets..." briefly

2. **Play Left Level**
   - Use Arrow keys to move
   - Press S to jump
   - Press A to run

3. **Play Right Level**
   - Same controls

4. **Vote**
   - Choose which level you preferred
   - Optionally add tags
   - Submit vote

5. **View Leaderboard**
   - See generator rankings
   - Click "Next Battle" to continue

## Troubleshooting

### "Backend unreachable"

**Problem:** Frontend can't connect to backend

**Solutions:**
1. Verify backend is running: `curl http://localhost:8080/health`
2. Check backend port in `vite.config.ts`:
   ```typescript
   proxy: {
     '/health': 'http://localhost:8080',  // Update if different
     '/v1': 'http://localhost:8080',      // Update if different
   }
   ```
3. Restart dev server after changing config

### "npm: command not found"

**Problem:** Node.js not installed or not in PATH

**Solution:**
1. Install Node.js from https://nodejs.org/
2. Restart terminal
3. Try `node --version` again

### Assets not loading / sprites broken

**Problem:** Sprite sheets not found

**Solution:**
1. Check `frontend/public/assets/` contains PNG files:
   - mariosheet.png
   - smallmariosheet.png
   - firemariosheet.png
   - enemysheet.png
   - mapsheet.png
   - itemsheet.png
   - particlesheet.png
2. If missing, copy from `client-java/src/main/resources/img/*.png`

### Port 3000 already in use

**Problem:** Another app is using port 3000

**Solution:**
Update `vite.config.ts`:
```typescript
server: {
  port: 3001,  // Change to any free port
  // ...
}
```

### Keyboard controls not working

**Problem:** Keys not registering

**Solutions:**
1. Click on the game canvas to focus it
2. Check browser console for errors
3. Try different browser (Chrome/Firefox/Edge)
4. Ensure no browser extensions are blocking input

## Development Tips

### Hot Reload

Changes to `.tsx` and `.ts` files automatically reload the browser.

### Console Logs

Open browser DevTools (F12) to see:
- API requests and responses
- Game events
- Error messages

### Asset Changes

If you update sprite sheets in `public/assets/`:
1. Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
2. Or clear cache in DevTools

### Backend URL

To use a different backend:

**Development:**
Update `vite.config.ts` proxy

**Production:**
Update `src/api/client.ts`:
```typescript
constructor(baseUrl: string = 'https://your-backend.com') {
```

## Next Steps

Once it's working locally:

1. **Test Thoroughly:** Run through `TESTING.md` checklist
2. **Build for Production:** `npm run build`
3. **Deploy:** Follow `DEPLOYMENT.md` guide

## Common Questions

**Q: Can I use this on mobile?**
A: Not yet - desktop only for initial release (keyboard controls)

**Q: What browsers are supported?**
A: Chrome, Firefox, Edge (latest versions)

**Q: Can I customize the UI?**
A: Yes! Edit `src/styles/components.css` and `src/styles/global.css`

**Q: How do I add new features?**
A: The code is well-documented. Start with `src/components/` for UI or `src/engine/` for game logic.

**Q: Something broke, how do I reset?**
A:
```bash
rm -rf node_modules
rm package-lock.json
npm install
npm run dev
```

## Getting Help

If you encounter issues:

1. Check browser console (F12) for errors
2. Check backend logs
3. Verify backend health: http://localhost:8080/health
4. Try different browser
5. Clear cache and hard reload

## Success!

If you can complete a full battle (play both levels, vote, see leaderboard), everything is working correctly! 🎉

You're now ready to:
- Test more battles
- Make customizations
- Prepare for production deployment

Enjoy the PCG Arena! 🎮

