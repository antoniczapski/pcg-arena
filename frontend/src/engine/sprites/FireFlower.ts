/**
 * Fire flower power-up sprite
 * Ported from client-java/src/main/java/arena/game/sprites/FireFlower.java
 */

import { MarioSprite } from '../MarioSprite';
import { SpriteType } from '../SpriteType';

export class FireFlower extends MarioSprite {
  private life: number = 0;

  constructor(_visuals: boolean, x: number, y: number) {
    super(x, y, SpriteType.FIRE_FLOWER);
    this.width = 4;
    this.height = 12;
    this.facing = 1;
    this.life = 0;
  }

  clone(): MarioSprite {
    const flower = new FireFlower(false, this.x, this.y);
    flower.xa = this.xa;
    flower.ya = this.ya;
    flower.width = this.width;
    flower.height = this.height;
    flower.facing = this.facing;
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
        this.world.mario.getFlower();
        this.world.removeSprite(this);
      }
    }
  }

  update(): void {
    if (!this.alive) {
      return;
    }

    if (this.life < 9) {
      this.life++;
    }
  }
}

