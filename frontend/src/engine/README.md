# Mario Game Engine (TypeScript Port)

This directory contains the TypeScript port of the Mario game engine from the Java client.

## Core Classes

- **MarioGame.ts** - Game loop controller with requestAnimationFrame
- **MarioWorld.ts** - World state, sprite management, game logic
- **MarioLevel.ts** - ASCII tilemap parser and level data
- **MarioSprite.ts** - Base sprite class
- **Mario.ts** (sprites/) - Player character with physics

## Helper Modules

- **GameStatus.ts** - Game state enum (RUNNING, WIN, LOSE, TIME_OUT)
- **MarioActions.ts** - Input action enum and utilities
- **EventType.ts** - Game event types for telemetry
- **SpriteType.ts** - Sprite type enum
- **TileFeature.ts** - Tile property flags
- **MarioEvent.ts** - Game event data structure

## Physics Constants

The engine preserves exact physics constants from the Java version:
- Ground Inertia: 0.89
- Air Inertia: 0.89
- Gravity: 3.0
- Jump Velocity: -1.9
- Walk Speed: 0.6
- Run Speed: 1.2

## Implementation Status

- ✅ Core engine (Phase 2)
- ⏳ Enemy sprites (Phase 3)
- ⏳ Rendering system (Phase 4)
- ⏳ Visual effects (Phase 5)
- ⏳ Input handling (Phase 6)

