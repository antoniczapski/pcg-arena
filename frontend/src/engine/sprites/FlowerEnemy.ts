/**
 * Flower enemy sprite (piranha plant in pipes)
 * Ported from client-java/src/main/java/arena/game/sprites/FlowerEnemy.java
 */

import { MarioSprite } from '../MarioSprite';
import { SpriteType } from '../SpriteType';
import { EventType } from '../EventType';

export class FlowerEnemy extends MarioSprite {
  private yStart: number;
  private waitTime: number = 0;
  private _tick: number = 0;

  constructor(_visuals: boolean, x: number, y: number) {
    super(x, y, SpriteType.ENEMY_FLOWER);
    this.width = 2;
    this.height = 12;
    this.yStart = this.y;
    this.ya = -1; // Start moving up
  }

  clone(): MarioSprite {
    const flower = new FlowerEnemy(false, this.x, this.yStart);
    flower.xa = this.xa;
    flower.ya = this.ya;
    flower.width = this.width;
    flower.height = this.height;
    flower.facing = this.facing;
    flower.yStart = this.yStart;
    flower.y = this.y;
    flower.waitTime = this.waitTime;
    flower._tick = this._tick;
    return flower;
  }

  collideCheck(): void {
    if (!this.alive || !this.world) {
      return;
    }

    const xMarioD = this.world.mario.x - this.x;
    const yMarioD = this.world.mario.y - this.y;

    // FlowerEnemy always hurts Mario on contact (can't be stomped)
    if (xMarioD > -16 && xMarioD < 16) {
      if (yMarioD > -this.height && yMarioD < this.world.mario.height) {
        this.world.addEvent(EventType.HURT, this.type);
        this.world.mario.getHurt();
      }
    }
  }

  update(): void {
    if (!this.alive) {
      return;
    }

    // Moving down (ya > 0)
    if (this.ya > 0) {
      if (this.y >= this.yStart) {
        // At bottom position
        this.y = this.yStart;
        const xd = this.world ? Math.abs(this.world.mario.x - this.x) : 100;
        this.waitTime++;
        // Wait for 40 ticks AND Mario must be far enough away (> 24 pixels)
        if (this.waitTime > 40 && xd > 24) {
          this.waitTime = 0;
          this.ya = -1; // Start moving up
        }
      }
    } else if (this.ya < 0) {
      // Moving up (ya < 0)
      if (this.yStart - this.y > 20) {
        // At top position (20 pixels above start)
        this.y = this.yStart - 20;
        this.waitTime++;
        // Wait for 40 ticks at top
        if (this.waitTime > 40) {
          this.waitTime = 0;
          this.ya = 1; // Start moving down
        }
      }
    }

    this.y += this.ya;
    this._tick++;
  }

  fireballCollideCheck(fireball: any): boolean {
    if (!this.alive || !this.world) {
      return false;
    }

    const xD = fireball.x - this.x;
    const yD = fireball.y - this.y;

    if (xD > -16 && xD < 16) {
      if (yD > -this.height && yD < fireball.height) {
        this.world.addEvent(EventType.FIRE_KILL, this.type);
        this.world.removeSprite(this);
        return true;
      }
    }
    return false;
  }

  // FlowerEnemy doesn't respond to shell collisions like other enemies
  shellCollideCheck(_shell: any): boolean {
    return false;
  }

  // FlowerEnemy doesn't respond to bumps
  bumpCheck(_xTile: number, _yTile: number): void {
    // Do nothing
  }
}
