/**
 * Asset loader for sprite sheets
 * Ported from client-java/src/main/java/arena/game/helper/Assets.java
 */

export interface SpriteSheet {
  image: HTMLImageElement;
  tileWidth: number;
  tileHeight: number;
  loaded: boolean;
}

class AssetLoaderClass {
  private assets: Map<string, SpriteSheet> = new Map();
  private loadingPromise: Promise<void> | null = null;
  private isLoadingComplete: boolean = false;

  /**
   * Load a single sprite sheet image
   */
  private loadImage(name: string, path: string, tileWidth: number, tileHeight: number): Promise<void> {
    return new Promise((resolve, reject) => {
      // Check if already loaded
      if (this.assets.has(name)) {
        console.log('[AssetLoader] Already loaded:', name);
        resolve();
        return;
      }

      console.log('[AssetLoader] Loading:', name, 'from', path);

      const img = new Image();
      
      img.onload = () => {
        console.log('[AssetLoader] ✓ Loaded:', name, img.width, 'x', img.height);
        this.assets.set(name, {
          image: img,
          tileWidth,
          tileHeight,
          loaded: true,
        });
        resolve();
      };
      
      img.onerror = (e) => {
        console.error('[AssetLoader] ✗ Failed to load:', name, path, e);
        // Create a placeholder 1x1 image to prevent crashes
        const placeholder = document.createElement('canvas');
        placeholder.width = tileWidth;
        placeholder.height = tileHeight;
        const ctx = placeholder.getContext('2d');
        if (ctx) {
          ctx.fillStyle = '#ff00ff'; // Magenta for debugging
          ctx.fillRect(0, 0, tileWidth, tileHeight);
        }
        
        // Still add it so we don't get stuck
        this.assets.set(name, {
          image: img, // Will be invalid but won't crash
          tileWidth,
          tileHeight,
          loaded: false,
        });
        resolve(); // Resolve anyway to not block other assets
      };
      
      img.src = path;
    });
  }

  /**
   * Load all Mario sprite sheets
   */
  async loadAllAssets(): Promise<void> {
    // If already loaded, return immediately
    if (this.isLoadingComplete) {
      console.log('[AssetLoader] Assets already loaded');
      return;
    }

    // If currently loading, wait for that to complete
    if (this.loadingPromise) {
      console.log('[AssetLoader] Already loading, waiting...');
      return this.loadingPromise;
    }

    console.log('[AssetLoader] Starting asset load...');

    this.loadingPromise = (async () => {
      const assetList = [
        { name: 'mario', path: '/assets/mariosheet.png', tileWidth: 32, tileHeight: 32 },
        { name: 'smallMario', path: '/assets/smallmariosheet.png', tileWidth: 16, tileHeight: 16 },
        { name: 'fireMario', path: '/assets/firemariosheet.png', tileWidth: 32, tileHeight: 32 },
        { name: 'enemies', path: '/assets/enemysheet.png', tileWidth: 16, tileHeight: 32 },
        { name: 'items', path: '/assets/itemsheet.png', tileWidth: 16, tileHeight: 16 },
        { name: 'level', path: '/assets/mapsheet.png', tileWidth: 16, tileHeight: 16 },
        { name: 'particles', path: '/assets/particlesheet.png', tileWidth: 8, tileHeight: 8 },
      ];

      // Load all assets
      await Promise.all(
        assetList.map(({ name, path, tileWidth, tileHeight }) =>
          this.loadImage(name, path, tileWidth, tileHeight)
        )
      );

      console.log('[AssetLoader] All assets processed. Total:', this.assets.size);
      this.isLoadingComplete = true;
    })();

    await this.loadingPromise;
  }

  /**
   * Get a loaded sprite sheet
   */
  getSpriteSheet(name: string): SpriteSheet | null {
    return this.assets.get(name) || null;
  }

  /**
   * Check if all assets are loaded
   */
  isLoaded(): boolean {
    return this.isLoadingComplete;
  }

  /**
   * Draw a sprite from a sheet
   */
  drawSprite(
    ctx: CanvasRenderingContext2D,
    sheetName: string,
    tileX: number,
    tileY: number,
    destX: number,
    destY: number,
    flipX: boolean = false,
    flipY: boolean = false
  ): void {
    const sheet = this.getSpriteSheet(sheetName);
    if (!sheet || !sheet.loaded) {
      // Draw placeholder if sprite not loaded
      ctx.fillStyle = '#ff00ff';
      ctx.fillRect(destX, destY, sheet?.tileWidth || 16, sheet?.tileHeight || 16);
      return;
    }

    const sx = tileX * sheet.tileWidth;
    const sy = tileY * sheet.tileHeight;
    const sWidth = sheet.tileWidth;
    const sHeight = sheet.tileHeight;

    ctx.save();
    
    if (flipX || flipY) {
      ctx.translate(destX + sWidth / 2, destY + sHeight / 2);
      ctx.scale(flipX ? -1 : 1, flipY ? -1 : 1);
      ctx.drawImage(sheet.image, sx, sy, sWidth, sHeight, -sWidth / 2, -sHeight / 2, sWidth, sHeight);
    } else {
      ctx.drawImage(sheet.image, sx, sy, sWidth, sHeight, destX, destY, sWidth, sHeight);
    }
    
    ctx.restore();
  }

  /**
   * Draw a tile from the level sheet
   */
  drawTile(
    ctx: CanvasRenderingContext2D,
    tileIndex: number,
    destX: number,
    destY: number
  ): void {
    const sheet = this.getSpriteSheet('level');
    if (!sheet || !sheet.loaded || tileIndex === 0) {
      return;
    }

    const tilesPerRow = Math.floor(sheet.image.width / sheet.tileWidth);
    const tileX = tileIndex % tilesPerRow;
    const tileY = Math.floor(tileIndex / tilesPerRow);

    const sx = tileX * sheet.tileWidth;
    const sy = tileY * sheet.tileHeight;

    ctx.drawImage(
      sheet.image,
      sx,
      sy,
      sheet.tileWidth,
      sheet.tileHeight,
      destX,
      destY,
      sheet.tileWidth,
      sheet.tileHeight
    );
  }
}

// Singleton instance
export const assetLoader = new AssetLoaderClass();
