# PCG Arena - Browser Frontend

Browser-based Mario gameplay client for the PCG Arena platform.

## Technology Stack

- **React 18** - UI framework
- **TypeScript 5** - Type safety
- **Vite 5** - Fast build tool and dev server
- **HTML5 Canvas** - Game rendering

## Prerequisites

- Node.js 18+ and npm
- Backend running (see Configuration section below)

## Configuration

The frontend connects to the backend API using environment variables:

### Environment Files

- `.env` - Default configuration (localhost, committed to git)
- `.env.local` - Local overrides (gitignored, not committed)
- `.env.production` - Production configuration (www.pcg-arena.com)
- `.env.local.example` - Template for local customization

### Backend API URL

Set `VITE_API_BASE_URL` to configure where the frontend connects:

```bash
# For local development (default)
VITE_API_BASE_URL=http://localhost:8080

# For production
VITE_API_BASE_URL=https://www.pcg-arena.com
```

**Local development:** The default `.env` file points to `localhost:8080`. No changes needed.

**Custom backend:** Create `.env.local` (gitignored) to override:
```bash
cp .env.local.example .env.local
# Edit .env.local with your backend URL
```

## Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Development

The dev server will start at `http://localhost:3000` with hot module replacement.

By default, it connects to a backend at `http://localhost:8080`. Make sure your backend is running, or configure a different URL in `.env.local`.

## Production Build

To build for production (connects to https://www.pcg-arena.com):

```bash
npm run build
```

This creates optimized files in `dist/` using `.env.production` configuration.

To preview the production build locally:

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── api/              # API client and types
│   ├── engine/           # Mario game engine (TypeScript port)
│   ├── components/       # React components
│   ├── hooks/            # Custom React hooks
│   └── styles/           # CSS stylesheets
├── public/
│   └── assets/           # Sprite sheets and images
└── index.html            # Entry HTML file
```

## Protocol

This client implements the `arena/v0` protocol defined in `docs/stage0-spec.md`.

## Implementation Status

- ✅ **Phase 1:** Project setup and API client
- ✅ **Phase 2:** Game engine core
- ✅ **Phase 3:** Enemy sprites
- ✅ **Phase 4:** Rendering system
- ✅ **Phase 5:** Visual effects
- ✅ **Phase 6:** Input handling
- ✅ **Phase 7:** Battle UI and flow
- ✅ **Phase 8:** Telemetry collection
- ✅ **Phase 9:** Styling and polish
- ✅ **Phase 10:** Testing and deployment

## Key Features

- No download required - runs in any modern browser
- Faithful recreation of Java client gameplay
- Same protocol and telemetry as Java client
- Desktop keyboard controls (Arrow keys, S for jump, A for run/fire)
- Retro pixel art aesthetic

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

Part of the PCG Arena project.

