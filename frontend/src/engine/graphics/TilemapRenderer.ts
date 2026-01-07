/**
 * Tilemap renderer for level rendering
 * Ported from client-java/src/main/java/arena/game/graphics/MarioTilemap.java
 */

import { assetLoader } from './AssetLoader';
import { MarioLevel } from '../MarioLevel';
import { Camera } from './Camera';

export class TilemapRenderer {
  /**
   * Render the level tilemap
   */
  render(ctx: CanvasRenderingContext2D, level: MarioLevel, camera: Camera): void {
    // Calculate visible tile range
    const startTileX = Math.floor(camera.x / 16);
    const endTileX = Math.min(Math.ceil((camera.x + camera.width) / 16), level.tileWidth);
    const startTileY = Math.floor(camera.y / 16);
    const endTileY = Math.min(Math.ceil((camera.y + camera.height) / 16), level.tileHeight);

    // Render tiles
    for (let tileY = startTileY; tileY < endTileY; tileY++) {
      for (let tileX = startTileX; tileX < endTileX; tileX++) {
        const tileIndex = level.getBlock(tileX, tileY);
        if (tileIndex !== 0) {
          const screenPos = camera.worldToScreen(tileX * 16, tileY * 16);
          assetLoader.drawTile(ctx, tileIndex, screenPos.x, screenPos.y);
        }
      }
    }
  }

  /**
   * Render debug grid
   */
  renderDebugGrid(ctx: CanvasRenderingContext2D, level: MarioLevel, camera: Camera): void {
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 1;

    const startTileX = Math.floor(camera.x / 16);
    const endTileX = Math.min(Math.ceil((camera.x + camera.width) / 16), level.tileWidth);
    const startTileY = Math.floor(camera.y / 16);
    const endTileY = Math.min(Math.ceil((camera.y + camera.height) / 16), level.tileHeight);

    // Vertical lines
    for (let tileX = startTileX; tileX <= endTileX; tileX++) {
      const screenPos = camera.worldToScreen(tileX * 16, 0);
      ctx.beginPath();
      ctx.moveTo(screenPos.x, 0);
      ctx.lineTo(screenPos.x, camera.height);
      ctx.stroke();
    }

    // Horizontal lines
    for (let tileY = startTileY; tileY <= endTileY; tileY++) {
      const screenPos = camera.worldToScreen(0, tileY * 16);
      ctx.beginPath();
      ctx.moveTo(0, screenPos.y);
      ctx.lineTo(camera.width, screenPos.y);
      ctx.stroke();
    }
  }
}

