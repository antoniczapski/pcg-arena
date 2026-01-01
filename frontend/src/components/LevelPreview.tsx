/**
 * LevelPreview - A reusable component that renders a static preview of a Mario level
 * 
 * This component uses the same tile graphics as the gameplay engine to render
 * a complete level overview as a wide, scrollable image.
 */

import { useEffect, useRef, useState } from 'react';
import { assetLoader } from '../engine/graphics/AssetLoader';
import { MarioLevel } from '../engine/MarioLevel';
import { SpriteType } from '../engine/SpriteType';

interface LevelPreviewProps {
  /** The level ID (used for identification) */
  levelId: string;
  /** ASCII tilemap string (10-20 lines) */
  tilemap: string;
  /** Width of the level in tiles */
  width: number;
  /** Height of the level in tiles (10-20) */
  height: number;
  /** Scale factor for rendering (default: 1 = 16px per tile) */
  scale?: number;
  /** Optional click handler */
  onClick?: () => void;
  /** Show level ID label */
  showLabel?: boolean;
  /** CSS class for container */
  className?: string;
}

const TILE_SIZE = 16;
const SKY_COLOR = '#5c94fc'; // Mario sky blue

export function LevelPreview({
  levelId,
  tilemap,
  width,
  height,
  scale = 1,
  onClick,
  showLabel = true,
  className = '',
}: LevelPreviewProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function renderLevel() {
      try {
        // Ensure assets are loaded
        await assetLoader.loadAllAssets();
        
        if (!mounted) return;
        
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) {
          setError('Failed to get canvas context');
          return;
        }

        // Parse level first to get actual dimensions
        const level = new MarioLevel(tilemap, true);
        
        // Use actual level dimensions from the parsed tilemap
        const actualWidth = level.tileWidth;
        const actualHeight = level.tileHeight;

        // Set canvas dimensions based on actual level size
        const canvasWidth = actualWidth * TILE_SIZE * scale;
        const canvasHeight = actualHeight * TILE_SIZE * scale;
        canvas.width = canvasWidth;
        canvas.height = canvasHeight;

        // Fill background
        ctx.fillStyle = SKY_COLOR;
        ctx.fillRect(0, 0, canvasWidth, canvasHeight);

        // If scaling, use an offscreen canvas at 1:1 then scale
        if (scale !== 1) {
          const offscreen = document.createElement('canvas');
          offscreen.width = actualWidth * TILE_SIZE;
          offscreen.height = actualHeight * TILE_SIZE;
          const offCtx = offscreen.getContext('2d');
          
          if (offCtx) {
            offCtx.fillStyle = SKY_COLOR;
            offCtx.fillRect(0, 0, offscreen.width, offscreen.height);
            renderTiles(offCtx, level, actualWidth, actualHeight);
            renderEnemies(offCtx, level, actualWidth, actualHeight);
            
            // Scale to final canvas
            ctx.imageSmoothingEnabled = false;
            ctx.drawImage(offscreen, 0, 0, canvasWidth, canvasHeight);
          }
        } else {
          renderTiles(ctx, level, actualWidth, actualHeight);
          renderEnemies(ctx, level, actualWidth, actualHeight);
        }

        setIsLoaded(true);
        setError(null);
      } catch (err) {
        console.error('Failed to render level preview:', err);
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to render');
        }
      }
    }

    renderLevel();

    return () => {
      mounted = false;
    };
  }, [tilemap, width, height, scale]);

  function renderTiles(ctx: CanvasRenderingContext2D, level: MarioLevel, tileWidth: number, tileHeight: number) {
    for (let tileY = 0; tileY < tileHeight; tileY++) {
      for (let tileX = 0; tileX < tileWidth; tileX++) {
        const tileIndex = level.getBlock(tileX, tileY);
        if (tileIndex !== 0) {
          assetLoader.drawTile(ctx, tileIndex, tileX * TILE_SIZE, tileY * TILE_SIZE);
        }
      }
    }
  }

  function renderEnemies(ctx: CanvasRenderingContext2D, level: MarioLevel, tileWidth: number, tileHeight: number) {
    for (let tileY = 0; tileY < tileHeight; tileY++) {
      for (let tileX = 0; tileX < tileWidth; tileX++) {
        const spriteType = level.getSpriteType(tileX, tileY);
        if (spriteType !== SpriteType.NONE) {
          renderEnemy(ctx, spriteType, tileX, tileY);
        }
      }
    }
  }

  function renderEnemy(ctx: CanvasRenderingContext2D, spriteType: SpriteType, tileX: number, tileY: number) {
    // Determine sprite row based on enemy type
    let frameY = 0;
    const ENEMY_SPRITE_HEIGHT = 32;

    switch (spriteType) {
      case SpriteType.RED_KOOPA:
      case SpriteType.RED_KOOPA_WINGED:
        frameY = 0;
        break;
      case SpriteType.GREEN_KOOPA:
      case SpriteType.GREEN_KOOPA_WINGED:
        frameY = 1;
        break;
      case SpriteType.GOOMBA:
      case SpriteType.GOOMBA_WINGED:
        frameY = 2;
        break;
      case SpriteType.SPIKY:
      case SpriteType.SPIKY_WINGED:
        frameY = 3;
        break;
      case SpriteType.BULLET_BILL:
        frameY = 5;
        break;
      case SpriteType.ENEMY_FLOWER:
        // Flower enemy at row 6, render at different offset (centered in pipe)
        const flowerX = tileX * TILE_SIZE + 9; // centered
        const flowerY = tileY * TILE_SIZE - 8; // slightly above
        assetLoader.drawSprite(ctx, 'enemies', 0, 6, flowerX, flowerY);
        return;
      default:
        return; // Skip non-enemy sprites like items
    }

    // Enemy position: center of tile, bottom aligned
    // Enemies spawn at x * 16 + 8, y * 16 + 15 (bottom of sprite)
    const x = tileX * TILE_SIZE;
    const y = (tileY + 1) * TILE_SIZE - ENEMY_SPRITE_HEIGHT;
    
    // Use frame 0 for static preview
    assetLoader.drawSprite(ctx, 'enemies', 0, frameY, x, y);
  }

  const containerStyle: React.CSSProperties = {
    display: 'inline-block',
    position: 'relative',
    cursor: onClick ? 'pointer' : 'default',
  };

  const canvasStyle: React.CSSProperties = {
    display: 'block',
    imageRendering: 'pixelated',
  };

  return (
    <div 
      className={`level-preview ${className}`} 
      style={containerStyle}
      onClick={onClick}
    >
      <canvas
        ref={canvasRef}
        style={canvasStyle}
        width={width * TILE_SIZE * scale}
        height={height * TILE_SIZE * scale}
      />
      {showLabel && (
        <div className="level-preview-label">
          {levelId}
        </div>
      )}
      {!isLoaded && !error && (
        <div className="level-preview-loading">Loading...</div>
      )}
      {error && (
        <div className="level-preview-error">{error}</div>
      )}
    </div>
  );
}

/**
 * LevelPreviewList - Displays multiple level previews in a vertical list
 */
interface LevelPreviewListProps {
  levels: Array<{
    level_id: string;
    tilemap: string;
    format: {
      width: number;
      height: number;
    };
  }>;
  scale?: number;
  onLevelClick?: (levelId: string) => void;
}

export function LevelPreviewList({ 
  levels, 
  scale = 1,
  onLevelClick,
}: LevelPreviewListProps) {
  return (
    <div className="level-preview-list">
      {levels.map((level) => (
        <LevelPreview
          key={level.level_id}
          levelId={level.level_id}
          tilemap={level.tilemap}
          width={level.format.width}
          height={level.format.height}
          scale={scale}
          onClick={onLevelClick ? () => onLevelClick(level.level_id) : undefined}
          showLabel={true}
        />
      ))}
    </div>
  );
}

