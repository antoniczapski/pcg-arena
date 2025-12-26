/**
 * Flower enemy sprite (piranha plant in pipes)
 * Ported from client-java/src/main/java/arena/game/sprites/FlowerEnemy.java
 */

import { MarioSprite } from '../MarioSprite';
import { SpriteType } from '../SpriteType';
import { EventType } from '../EventType';

export class FlowerEnemy extends MarioSprite {
  private life: number = 0;
  private yStart: number = 0;

  constructor(visuals: boolean, x: number, y: number) {
    super(x, y, SpriteType.ENEMY_FLOWER);
    this.width = 2;
    this.height = 12;
    this.facing = 1;
    this.yStart = y;
    this.ya = -8;
    this.y -= 1;
    this.life = 0;
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
    flower.life = this.life;
    return flower;
  }

  collideCheck(): void {
    if (!this.alive || !this.world) {
      return;
    }

    const xMarioD = this.world.mario.x - this.x;
    const yMarioD = this.world.mario.y - this.y;

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

    if (this.life < 10) {
      this.life++;
      return;
    }

    const xMarioD = this.world ? this.world.mario.x - this.x : 0;

    if (xMarioD > -32 && xMarioD < 32) {
      this.ya = 1;
    } else {
      this.ya = -1;
    }

    this.y += this.ya;
    if (this.y < this.yStart - 8) {
      this.y = this.yStart - 8;
      this.ya = 0;
    }
    if (this.y > this.yStart) {
      this.y = this.yStart;
      this.ya = 0;
    }
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
}

