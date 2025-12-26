/**
 * Base effect class for particle effects
 * Ported from client-java/src/main/java/arena/game/core/MarioEffect.java
 */

import type { MarioWorld } from '../MarioWorld';

export abstract class MarioEffect {
  x: number;
  y: number;
  xa: number = 0;
  ya: number = 0;
  life: number = 0;
  world: MarioWorld | null = null;
  alive: boolean = true;

  constructor(x: number, y: number) {
    this.x = x;
    this.y = y;
  }

  abstract update(): void;
  abstract render(ctx: CanvasRenderingContext2D, cameraX: number, cameraY: number): void;
}

