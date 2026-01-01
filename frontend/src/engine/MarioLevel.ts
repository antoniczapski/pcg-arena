/**
 * Mario level parser and state
 * Ported from client-java/src/main/java/arena/game/core/MarioLevel.java
 */

import { SpriteType } from './SpriteType';
import { TileFeature, getTileType, hasTileFeature } from './TileFeature';

export const GAME_WIDTH = 256;
export const GAME_HEIGHT = 256;
export const MIN_LEVEL_HEIGHT_TILES = 16;  // Minimum height for gameplay (pad shorter levels)

export class MarioLevel {
  width: number = GAME_WIDTH;
  tileWidth: number = GAME_WIDTH / 16;
  height: number = GAME_HEIGHT;
  tileHeight: number = GAME_HEIGHT / 16;
  totalCoins: number = 0;
  marioTileX: number = 0;
  marioTileY: number = 0;
  exitTileX: number = 0;
  exitTileY: number = 0;

  private levelTiles: number[][] = [];
  private spriteTemplates: SpriteType[][] = [];
  private lastSpawnTime: number[][] = [];

  constructor(level: string, _visuals: boolean) {
    const trimmed = level.trim();
    if (trimmed.length === 0) {
      this.tileWidth = 0;
      this.width = 0;
      this.tileHeight = 0;
      this.height = 0;
      return;
    }

    const lines = level.split(/\r?\n/);
    const actualTileHeight = lines.length;
    this.tileWidth = lines[0].length;
    this.width = this.tileWidth * 16;
    
    // Use minimum height of 16 tiles for gameplay, padding shorter levels at the top
    this.tileHeight = Math.max(actualTileHeight, MIN_LEVEL_HEIGHT_TILES);
    this.height = this.tileHeight * 16;
    
    // Calculate vertical offset: for shorter levels, content goes at the bottom
    const yOffset = this.tileHeight - actualTileHeight;

    // Initialize arrays with the padded height
    this.levelTiles = Array(this.tileWidth)
      .fill(null)
      .map(() => Array(this.tileHeight).fill(0));
    this.spriteTemplates = Array(this.tileWidth)
      .fill(null)
      .map(() => Array(this.tileHeight).fill(SpriteType.NONE));
    this.lastSpawnTime = Array(this.tileWidth)
      .fill(null)
      .map(() => Array(this.tileHeight).fill(-40));

    let marioLocInit = false;
    let exitLocInit = false;

    // Parse tilemap - apply yOffset so shorter levels appear at the bottom
    for (let y = 0; y < lines.length; y++) {
      const tileY = y + yOffset;  // Offset for shorter levels
      for (let x = 0; x < lines[y].length; x++) {
        const c = lines[y].charAt(x);
        let tempIndex = 0;
        let singlePipe = false;

        switch (c) {
          case 'M':
            this.marioTileX = x;
            this.marioTileY = tileY;
            marioLocInit = true;
            break;
          case 'F':
            this.exitTileX = x;
            this.exitTileY = tileY;
            exitLocInit = true;
            break;
          case 'y':
            this.spriteTemplates[x][tileY] = SpriteType.SPIKY;
            break;
          case 'Y':
            this.spriteTemplates[x][tileY] = SpriteType.SPIKY_WINGED;
            break;
          case 'E':
          case 'g':
            this.spriteTemplates[x][tileY] = SpriteType.GOOMBA;
            break;
          case 'G':
            this.spriteTemplates[x][tileY] = SpriteType.GOOMBA_WINGED;
            break;
          case 'k':
            this.spriteTemplates[x][tileY] = SpriteType.GREEN_KOOPA;
            break;
          case 'K':
            this.spriteTemplates[x][tileY] = SpriteType.GREEN_KOOPA_WINGED;
            break;
          case 'r':
            this.spriteTemplates[x][tileY] = SpriteType.RED_KOOPA;
            break;
          case 'R':
            this.spriteTemplates[x][tileY] = SpriteType.RED_KOOPA_WINGED;
            break;
          case 'X':
            // floor
            this.levelTiles[x][tileY] = 1;
            break;
          case '#':
            // pyramid block
            this.levelTiles[x][tileY] = 2;
            break;
          case '%':
            // jump through block
            tempIndex = 0;
            if (x > 0 && lines[y].charAt(x - 1) === '%') {
              tempIndex += 2;
            }
            if (x < this.levelTiles.length - 1 && lines[y].charAt(x + 1) === '%') {
              tempIndex += 1;
            }
            this.levelTiles[x][tileY] = 43 + tempIndex;
            break;
          case '|':
            // background for jump through block
            this.levelTiles[x][tileY] = 47;
            break;
          case '*':
            // bullet bill
            tempIndex = 0;
            if (y > 0 && lines[y - 1].charAt(x) === '*') {
              tempIndex += 1;
            }
            if (y > 1 && lines[y - 2].charAt(x) === '*') {
              tempIndex += 1;
            }
            this.levelTiles[x][tileY] = 3 + tempIndex;
            break;
          case 'B':
            // bullet bill head
            this.levelTiles[x][tileY] = 3;
            break;
          case 'b':
            // bullet bill neck and body
            tempIndex = 0;
            if (y > 1 && lines[y - 2].charAt(x) === 'B') {
              tempIndex += 1;
            }
            this.levelTiles[x][tileY] = 4 + tempIndex;
            break;
          case '?':
          case '@':
            // mushroom question block
            this.levelTiles[x][tileY] = 8;
            break;
          case 'Q':
          case '!':
            // coin question block
            this.totalCoins += 1;
            this.levelTiles[x][tileY] = 11;
            break;
          case '1':
            // invisible 1 up block
            this.levelTiles[x][tileY] = 48;
            break;
          case '2':
            // invisible coin block
            this.totalCoins += 1;
            this.levelTiles[x][tileY] = 49;
            break;
          case 'D':
            // used
            this.levelTiles[x][tileY] = 14;
            break;
          case 'S':
            // normal block
            this.levelTiles[x][tileY] = 6;
            break;
          case 'C':
            // coin block
            this.totalCoins += 1;
            this.levelTiles[x][tileY] = 7;
            break;
          case 'U':
            // mushroom block
            this.levelTiles[x][tileY] = 50;
            break;
          case 'L':
            // 1up block
            this.levelTiles[x][tileY] = 51;
            break;
          case 'o':
            // coin
            this.totalCoins += 1;
            this.levelTiles[x][tileY] = 15;
            break;
          case 't':
            // empty pipe
            tempIndex = 0;
            singlePipe = false;
            if (
              x < lines[y].length - 1 &&
              lines[y].charAt(x + 1).toLowerCase() !== 't' &&
              x > 0 &&
              lines[y].charAt(x - 1).toLowerCase() !== 't'
            ) {
              singlePipe = true;
            }
            if (x > 0 && (this.levelTiles[x - 1][tileY] === 18 || this.levelTiles[x - 1][tileY] === 20)) {
              tempIndex += 1;
            }
            if (y > 0 && lines[y - 1].charAt(x).toLowerCase() === 't') {
              if (singlePipe) {
                tempIndex += 1;
              } else {
                tempIndex += 2;
              }
            }
            if (singlePipe) {
              this.levelTiles[x][tileY] = 52 + tempIndex;
            } else {
              this.levelTiles[x][tileY] = 18 + tempIndex;
            }
            break;
          case 'T':
            // flower pipe
            tempIndex = 0;
            singlePipe =
              x < lines[y].length - 1 &&
              lines[y].charAt(x + 1).toLowerCase() !== 't' &&
              x > 0 &&
              lines[y].charAt(x - 1).toLowerCase() !== 't';
            if (x > 0 && (this.levelTiles[x - 1][tileY] === 18 || this.levelTiles[x - 1][tileY] === 20)) {
              tempIndex += 1;
            }
            if (y > 0 && lines[y - 1].charAt(x).toLowerCase() === 't') {
              if (singlePipe) {
                tempIndex += 1;
              } else {
                tempIndex += 2;
              }
            }
            if (singlePipe) {
              this.levelTiles[x][tileY] = 52 + tempIndex;
            } else {
              if (tempIndex === 0) {
                this.spriteTemplates[x][tileY] = SpriteType.ENEMY_FLOWER;
              }
              this.levelTiles[x][tileY] = 18 + tempIndex;
            }
            break;
          case '<':
            // pipe top left
            this.levelTiles[x][tileY] = 18;
            break;
          case '>':
            // pipe top right
            this.levelTiles[x][tileY] = 19;
            break;
          case '[':
            // pipe body left
            this.levelTiles[x][tileY] = 20;
            break;
          case ']':
            // pipe body right
            this.levelTiles[x][tileY] = 21;
            break;
        }
      }
    }

    // Set default Mario position if not found
    if (!marioLocInit) {
      this.marioTileX = 0;
      const floorY = this.findFirstFloor(lines, this.marioTileX);
      this.marioTileY = floorY >= 0 ? floorY + yOffset : yOffset;
    }

    // Set default exit position if not found
    if (!exitLocInit) {
      this.exitTileX = lines[0].length - 1;
      const floorY = this.findFirstFloor(lines, this.exitTileX);
      this.exitTileY = floorY >= 0 ? floorY + yOffset : yOffset;
    }

    // Add flag pole at exit
    for (let y = this.exitTileY; y > Math.max(1 + yOffset, this.exitTileY - 11); y--) {
      this.levelTiles[this.exitTileX][y] = 40;
    }
    this.levelTiles[this.exitTileX][Math.max(1 + yOffset, this.exitTileY - 11)] = 39;
  }

  clone(): MarioLevel {
    const level = new MarioLevel('', false);
    level.width = this.width;
    level.height = this.height;
    level.tileWidth = this.tileWidth;
    level.tileHeight = this.tileHeight;
    level.totalCoins = this.totalCoins;
    level.marioTileX = this.marioTileX;
    level.marioTileY = this.marioTileY;
    level.exitTileX = this.exitTileX;
    level.exitTileY = this.exitTileY;

    level.levelTiles = this.levelTiles.map((row) => [...row]);
    level.lastSpawnTime = this.lastSpawnTime.map((row) => [...row]);
    level.spriteTemplates = this.spriteTemplates.map((row) => [...row]);

    return level;
  }

  isBlocking(xTile: number, yTile: number, _xa: number, ya: number): boolean {
    const block = this.getBlock(xTile, yTile);
    const features = getTileType(block);
    let blocking = hasTileFeature(features, TileFeature.BLOCK_ALL);
    blocking = blocking || (ya < 0 && hasTileFeature(features, TileFeature.BLOCK_UPPER));
    blocking = blocking || (ya > 0 && hasTileFeature(features, TileFeature.BLOCK_LOWER));
    return blocking;
  }

  getBlock(xTile: number, yTile: number): number {
    let x = xTile;
    if (x < 0) {
      x = 0;
    }
    if (x > this.tileWidth - 1) {
      x = this.tileWidth - 1;
    }
    if (yTile < 0 || yTile > this.tileHeight - 1) {
      return 0;
    }
    return this.levelTiles[x][yTile];
  }

  setBlock(xTile: number, yTile: number, index: number): void {
    if (xTile < 0 || yTile < 0 || xTile > this.tileWidth - 1 || yTile > this.tileHeight - 1) {
      return;
    }
    this.levelTiles[xTile][yTile] = index;
  }

  setShiftIndex(_xTile: number, _yTile: number, _shift: number): void {
    // Graphics related - will be implemented in rendering phase
  }

  getSpriteType(xTile: number, yTile: number): SpriteType {
    if (xTile < 0 || yTile < 0 || xTile >= this.tileWidth || yTile >= this.tileHeight) {
      return SpriteType.NONE;
    }
    return this.spriteTemplates[xTile][yTile];
  }

  getLastSpawnTick(xTile: number, yTile: number): number {
    if (xTile < 0 || yTile < 0 || xTile > this.tileWidth - 1 || yTile > this.tileHeight - 1) {
      return 0;
    }
    return this.lastSpawnTime[xTile][yTile];
  }

  setLastSpawnTick(xTile: number, yTile: number, tick: number): void {
    if (xTile < 0 || yTile < 0 || xTile > this.tileWidth - 1 || yTile > this.tileHeight - 1) {
      return;
    }
    this.lastSpawnTime[xTile][yTile] = tick;
  }

  getSpriteCode(xTile: number, yTile: number): string {
    return `${xTile}_${yTile}_${this.getSpriteType(xTile, yTile)}`;
  }

  update(_cameraX: number, _cameraY: number): void {
    // Update logic - can be expanded if needed
  }

  render(_ctx: CanvasRenderingContext2D, _cameraX: number, _cameraY: number): void {
    // Rendering is done by TilemapRenderer
  }

  private isSolid(c: string): boolean {
    return (
      c === 'X' ||
      c === '#' ||
      c === '@' ||
      c === '!' ||
      c === 'B' ||
      c === 'C' ||
      c === 'Q' ||
      c === '<' ||
      c === '>' ||
      c === '[' ||
      c === ']' ||
      c === '?' ||
      c === 'S' ||
      c === 'U' ||
      c === 'D' ||
      c === '%' ||
      c === 't' ||
      c === 'T'
    );
  }

  private findFirstFloor(lines: string[], x: number): number {
    let skipLines = true;
    for (let i = lines.length - 1; i >= 0; i--) {
      const c = lines[i].charAt(x);
      if (this.isSolid(c)) {
        skipLines = false;
        continue;
      }
      if (!skipLines && !this.isSolid(c)) {
        return i;
      }
    }
    return -1;
  }
}

