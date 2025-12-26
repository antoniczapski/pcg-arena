/**
 * Sprite renderer for game objects
 */

import { assetLoader } from './AssetLoader';
import { Camera } from './Camera';
import { MarioSprite } from '../MarioSprite';
import { Mario } from '../sprites/Mario';
import { Enemy } from '../sprites/Enemy';
import { Shell } from '../sprites/Shell';
import { Fireball } from '../sprites/Fireball';
import { Mushroom } from '../sprites/Mushroom';
import { FireFlower } from '../sprites/FireFlower';
import { LifeMushroom } from '../sprites/LifeMushroom';
import { FlowerEnemy } from '../sprites/FlowerEnemy';
import { BulletBill } from '../sprites/BulletBill';
import { SpriteType } from '../SpriteType';

export class SpriteRenderer {
  private animationTick: number = 0;

  /**
   * Update animation frame counter
   */
  updateAnimations(): void {
    this.animationTick++;
  }

  /**
   * Render a sprite
   */
  renderSprite(ctx: CanvasRenderingContext2D, sprite: MarioSprite, camera: Camera): void {
    if (!sprite.alive) {
      return;
    }

    const screenPos = camera.worldToScreen(sprite.x, sprite.y);

    switch (sprite.type) {
      case SpriteType.MARIO:
        this.renderMario(ctx, sprite as Mario, screenPos.x, screenPos.y);
        break;
      case SpriteType.GOOMBA:
      case SpriteType.GOOMBA_WINGED:
      case SpriteType.RED_KOOPA:
      case SpriteType.RED_KOOPA_WINGED:
      case SpriteType.GREEN_KOOPA:
      case SpriteType.GREEN_KOOPA_WINGED:
      case SpriteType.SPIKY:
      case SpriteType.SPIKY_WINGED:
        this.renderEnemy(ctx, sprite as Enemy, screenPos.x, screenPos.y);
        break;
      case SpriteType.SHELL:
        this.renderShell(ctx, sprite as Shell, screenPos.x, screenPos.y);
        break;
      case SpriteType.FIREBALL:
        this.renderFireball(ctx, sprite as Fireball, screenPos.x, screenPos.y);
        break;
      case SpriteType.MUSHROOM:
        this.renderMushroom(ctx, sprite as Mushroom, screenPos.x, screenPos.y);
        break;
      case SpriteType.FIRE_FLOWER:
        this.renderFireFlower(ctx, sprite as FireFlower, screenPos.x, screenPos.y);
        break;
      case SpriteType.LIFE_MUSHROOM:
        this.renderLifeMushroom(ctx, sprite as LifeMushroom, screenPos.x, screenPos.y);
        break;
      case SpriteType.ENEMY_FLOWER:
        this.renderFlowerEnemy(ctx, sprite as FlowerEnemy, screenPos.x, screenPos.y);
        break;
      case SpriteType.BULLET_BILL:
        this.renderBulletBill(ctx, sprite as BulletBill, screenPos.x, screenPos.y);
        break;
    }
  }

  private renderMario(ctx: CanvasRenderingContext2D, mario: Mario, x: number, y: number): void {
    // Mario's y is the bottom of the sprite
    // Small Mario: 16x16 sprite, height=12, render at y-16
    // Large Mario: 32x32 sprite, height=24, render at y-32
    
    let sheetName = 'smallMario';
    let spriteHeight = 16;
    let offsetX = -8;
    
    if (mario.isFire) {
      sheetName = 'fireMario';
      spriteHeight = 32;
      offsetX = -16;
    } else if (mario.isLarge) {
      sheetName = 'mario';
      spriteHeight = 32;
      offsetX = -16;
    }

    const frameX = Math.floor(this.animationTick / 5) % 4;
    const frameY = mario.isDucking ? 1 : 0;
    
    // Render from top-left: x is center, y is bottom
    assetLoader.drawSprite(ctx, sheetName, frameX, frameY, x + offsetX, y - spriteHeight, mario.facing === -1);
  }

  private renderEnemy(ctx: CanvasRenderingContext2D, enemy: Enemy, x: number, y: number): void {
    // Enemy's y is the bottom of the sprite
    // ALL enemy sprites in the sprite sheet are 32 pixels tall (16x32 tiles)
    // The collision height (12 vs 24) is only for physics, not rendering
    // originY = 31 means bottom pixel, so render at y - 32 to get top-left
    
    let frameY = 0;
    
    // Determine sprite row based on type (from Java startIndex / 8)
    // RED_KOOPA: startIndex=0 → row 0
    // GREEN_KOOPA: startIndex=8 → row 1
    // GOOMBA: startIndex=16 → row 2
    // SPIKY: startIndex=24 → row 3
    switch (enemy.type) {
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
    }

    const frameX = Math.floor(this.animationTick / 6) % 2;
    const ENEMY_SPRITE_HEIGHT = 32; // All enemies are 32 pixels tall in sprite sheet
    
    // Render from top-left: x is center, y is bottom
    assetLoader.drawSprite(ctx, 'enemies', frameX, frameY, x - 8, y - ENEMY_SPRITE_HEIGHT, enemy.facing === -1);
  }

  private renderShell(ctx: CanvasRenderingContext2D, shell: Shell, x: number, y: number): void {
    // Shell sprite index = shellType * 8 + 3
    // Red shell (shellType=0): index=3 → column 3, row 0
    // Green shell (shellType=1): index=11 → column 3, row 1
    const row = shell.shellType; // 0=red (row 0), 1=green (row 1)
    assetLoader.drawSprite(ctx, 'enemies', 3, row, x - 8, y - 32, shell.facing === -1);
  }

  private renderFireball(ctx: CanvasRenderingContext2D, _fireball: Fireball, x: number, y: number): void {
    // Fireball is 8x8 sprite
    const frameX = Math.floor(this.animationTick / 3) % 2;
    assetLoader.drawSprite(ctx, 'particles', frameX, 0, x - 4, y - 8);
  }

  private renderMushroom(ctx: CanvasRenderingContext2D, _mushroom: Mushroom, x: number, y: number): void {
    // Mushroom is 16x16 sprite, height=12
    assetLoader.drawSprite(ctx, 'items', 0, 0, x - 8, y - 16);
  }

  private renderFireFlower(ctx: CanvasRenderingContext2D, _flower: FireFlower, x: number, y: number): void {
    // Fire flower is 16x16 sprite, height=12
    const frameX = Math.floor(this.animationTick / 4) % 2;
    assetLoader.drawSprite(ctx, 'items', frameX, 1, x - 8, y - 16);
  }

  private renderLifeMushroom(ctx: CanvasRenderingContext2D, _mushroom: LifeMushroom, x: number, y: number): void {
    // Life mushroom is 16x16 sprite, height=12
    assetLoader.drawSprite(ctx, 'items', 1, 0, x - 8, y - 16);
  }

  private renderFlowerEnemy(ctx: CanvasRenderingContext2D, _flower: FlowerEnemy, x: number, y: number): void {
    // FlowerEnemy uses enemy sprite sheet at row 6 (startIndex = 48)
    // Animation cycles through frames: ((tick / 2) & 1) * 2 + ((tick / 6) & 1) = 0, 1, 2, or 3
    // With originY = 24, the origin is 24px from top, so render at y - 24 to get top-left
    const frame = ((Math.floor(this.animationTick / 2) & 1) * 2) + (Math.floor(this.animationTick / 6) & 1);
    assetLoader.drawSprite(ctx, 'enemies', frame, 6, x - 8, y - 24);
  }

  private renderBulletBill(ctx: CanvasRenderingContext2D, bullet: BulletBill, x: number, y: number): void {
    // BulletBill: startIndex=40 → row 5 (40/8=5)
    // Enemy sprite sheet tiles are 16x32, so render at y - 32
    assetLoader.drawSprite(ctx, 'enemies', 0, 5, x - 8, y - 32, bullet.facing === -1);
  }

  /**
   * Render debug bounding boxes
   */
  renderDebug(ctx: CanvasRenderingContext2D, sprite: MarioSprite, camera: Camera): void {
    if (!sprite.alive) {
      return;
    }

    const screenPos = camera.worldToScreen(sprite.x, sprite.y);

    // Draw bounding box
    ctx.strokeStyle = sprite.type === SpriteType.MARIO ? 'lime' : 'red';
    ctx.lineWidth = 1;
    ctx.strokeRect(
      screenPos.x - sprite.width,
      screenPos.y - sprite.height,
      sprite.width * 2,
      sprite.height
    );

    // Draw center point
    ctx.fillStyle = 'yellow';
    ctx.fillRect(screenPos.x - 1, screenPos.y - 1, 2, 2);
  }
}
