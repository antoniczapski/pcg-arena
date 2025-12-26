# PCG Arena Frontend - Deployment Guide

## Prerequisites

- Node.js 18+ and npm
- Backend running and accessible
- Domain name (for production deployment)

## Local Development

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Backend URL

Update `vite.config.ts` if your backend is not running on `localhost:8080`:

```typescript
export default defineConfig({
  // ...
  server: {
    port: 3000,
    proxy: {
      '/health': 'http://your-backend-url:8080',
      '/v1': 'http://your-backend-url:8080',
    }
  }
})
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`.

### 4. Test Locally

- Open `http://localhost:3000` in Chrome, Firefox, or Edge
- Click "Start Battle"
- Verify:
  - Battle loads successfully
  - Left level is playable with keyboard controls
  - Right level is playable
  - Voting panel appears after both levels
  - Vote submission works
  - Leaderboard appears after voting

## Production Build

### 1. Build Static Assets

```bash
npm run build
```

This creates an optimized build in the `dist/` directory.

### 2. Preview Production Build Locally

```bash
npm run preview
```

## Deployment Options

### Option 1: Deploy with Backend on Same Server (Recommended)

If you're deploying to the same GCP VM as the backend:

1. **Build the frontend:**

```bash
npm run build
```

2. **Copy dist/ to backend static directory:**

```bash
# From frontend directory
cp -r dist/* ../backend/static/
```

3. **Configure backend to serve static files:**

Update `backend/src/main.py` to serve the frontend:

```python
from fastapi.staticfiles import StaticFiles

# Mount static files (frontend)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

4. **Access the app at your backend URL:**

```
http://your-domain.com
```

### Option 2: Deploy to Static Hosting (Netlify, Vercel, etc.)

1. **Update API URLs in `vite.config.ts`:**

Remove the proxy configuration and update API client to use absolute URLs:

```typescript
// In src/api/client.ts
constructor(baseUrl: string = 'https://your-backend-domain.com') {
  this.baseUrl = baseUrl;
}
```

2. **Build:**

```bash
npm run build
```

3. **Deploy `dist/` directory to your hosting service.**

4. **Configure CORS on backend:**

Add your frontend domain to CORS origins in backend:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Option 3: Docker Deployment

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Create `frontend/nginx.conf`:

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /health {
        proxy_pass http://backend:8080;
    }

    location /v1 {
        proxy_pass http://backend:8080;
    }
}
```

Build and run:

```bash
docker build -t pcg-arena-frontend .
docker run -p 3000:80 pcg-arena-frontend
```

## Post-Deployment Checklist

- [ ] Frontend loads without errors
- [ ] Health check succeeds
- [ ] Can fetch and start battles
- [ ] Gameplay works (keyboard controls, physics, rendering)
- [ ] All sprite assets load correctly
- [ ] Voting and vote submission work
- [ ] Leaderboard displays correctly
- [ ] Tested on Chrome, Firefox, Edge
- [ ] Mobile view disabled (desktop-only for initial release)

## Troubleshooting

### Assets Not Loading

- Check browser console for 404 errors
- Verify sprite sheets are in `public/assets/`
- Ensure `public/` directory is included in build

### Backend Connection Failed

- Verify backend is running and accessible
- Check CORS configuration on backend
- Verify proxy settings in `vite.config.ts` (dev) or API URLs (production)

### Gameplay Issues

- Clear browser cache
- Check for JavaScript errors in console
- Verify canvas rendering is working
- Test keyboard input responsiveness

### Performance Issues

- Enable production mode (`npm run build`)
- Check browser GPU acceleration is enabled
- Monitor browser console for warnings

## Monitoring

Monitor the following in production:

- API request success/failure rates
- Average battle completion time
- Browser compatibility issues (check error logs)
- Asset loading times
- Vote submission success rate

## Updates

To deploy updates:

1. Pull latest code
2. Run `npm install` (if dependencies changed)
3. Run `npm run build`
4. Deploy new `dist/` directory
5. Clear CDN cache if using one
6. Verify deployment with smoke tests

