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
    let sheetName = 'smallMario';
    let offsetY = -12;
    
    if (mario.isFire) {
      sheetName = 'fireMario';
      offsetY = -24;
    } else if (mario.isLarge) {
      sheetName = 'mario';
      offsetY = -24;
    }

    const frameX = Math.floor(this.animationTick / 5) % 4;
    const frameY = mario.isDucking ? 1 : 0;
    
    assetLoader.drawSprite(ctx, sheetName, frameX, frameY, x - 16, y + offsetY, mario.facing === -1);
  }

  private renderEnemy(ctx: CanvasRenderingContext2D, enemy: Enemy, x: number, y: number): void {
    let frameY = 0;
    
    // Determine sprite row based on type
    switch (enemy.type) {
      case SpriteType.GOOMBA:
      case SpriteType.GOOMBA_WINGED:
        frameY = 0;
        break;
      case SpriteType.RED_KOOPA:
      case SpriteType.RED_KOOPA_WINGED:
        frameY = 2;
        break;
      case SpriteType.GREEN_KOOPA:
      case SpriteType.GREEN_KOOPA_WINGED:
        frameY = 1;
        break;
      case SpriteType.SPIKY:
      case SpriteType.SPIKY_WINGED:
        frameY = 3;
        break;
    }

    const frameX = Math.floor(this.animationTick / 6) % 2;
    const offsetY = enemy.height === 12 ? -12 : -24;
    
    assetLoader.drawSprite(ctx, 'enemies', frameX, frameY, x - 8, y + offsetY, enemy.facing === -1);
  }

  private renderShell(ctx: CanvasRenderingContext2D, shell: Shell, x: number, y: number): void {
    assetLoader.drawSprite(ctx, 'enemies', 2, 1, x - 8, y - 12);
  }

  private renderFireball(ctx: CanvasRenderingContext2D, _fireball: Fireball, x: number, y: number): void {
    const frameX = Math.floor(this.animationTick / 3) % 2;
    assetLoader.drawSprite(ctx, 'particles', frameX, 0, x - 4, y - 4);
  }

  private renderMushroom(ctx: CanvasRenderingContext2D, _mushroom: Mushroom, x: number, y: number): void {
    assetLoader.drawSprite(ctx, 'items', 0, 0, x - 8, y - 12);
  }

  private renderFireFlower(ctx: CanvasRenderingContext2D, _flower: FireFlower, x: number, y: number): void {
    const frameX = Math.floor(this.animationTick / 4) % 2;
    assetLoader.drawSprite(ctx, 'items', frameX, 1, x - 8, y - 12);
  }

  private renderLifeMushroom(ctx: CanvasRenderingContext2D, _mushroom: LifeMushroom, x: number, y: number): void {
    assetLoader.drawSprite(ctx, 'items', 1, 0, x - 8, y - 12);
  }

  private renderFlowerEnemy(ctx: CanvasRenderingContext2D, _flower: FlowerEnemy, x: number, y: number): void {
    const frameX = Math.floor(this.animationTick / 6) % 2;
    assetLoader.drawSprite(ctx, 'enemies', frameX, 4, x - 8, y - 12);
  }

  private renderBulletBill(ctx: CanvasRenderingContext2D, bullet: BulletBill, x: number, y: number): void {
    assetLoader.drawSprite(ctx, 'enemies', 0, 5, x - 8, y - 12, bullet.facing === -1);
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

