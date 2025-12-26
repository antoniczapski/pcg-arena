/**
 * Base sprite class
 * Ported from client-java/src/main/java/arena/game/core/MarioSprite.java
 */

import { SpriteType } from './SpriteType';
import type { MarioWorld } from './MarioWorld';

export abstract class MarioSprite {
  type: SpriteType;
  alive: boolean = false;
  x: number;
  y: number;
  xa: number = 0;
  ya: number = 0;
  width: number = 0;
  height: number = 0;
  facing: number = 1;
  initialCode: string = '';
  world: MarioWorld | null = null;

  constructor(x: number, y: number, type: SpriteType) {
    this.x = x;
    this.y = y;
    this.type = type;
  }

  abstract clone(): MarioSprite;
  abstract update(): void;
  abstract collideCheck(): void;

  added(): void {
    // Default implementation - can be overridden
  }

  removed(): void {
    // Default implementation - can be overridden
  }

  getMapX(): number {
    return Math.floor(this.x / 16);
  }

  getMapY(): number {
    return Math.floor(this.y / 16);
  }

  shellCollideCheck(_shell: any): boolean {
    return false;
  }

  fireballCollideCheck(_fireball: any): boolean {
    return false;
  }

  bumpCheck(_xTile: number, _yTile: number): void {
    // Default implementation - can be overridden
  }

  render(_ctx: CanvasRenderingContext2D, _cameraX: number, _cameraY: number): void {
    // Default implementation - will be overridden by sprites with graphics
  }
}

