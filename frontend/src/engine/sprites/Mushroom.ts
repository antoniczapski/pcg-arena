/**
 * Mushroom power-up sprite
 * Ported from client-java/src/main/java/arena/game/sprites/Mushroom.java
 */

import { MarioSprite } from '../MarioSprite';
import { SpriteType } from '../SpriteType';

const GROUND_INERTIA = 0.89;
const AIR_INERTIA = 0.89;

export class Mushroom extends MarioSprite {
  private onGround: boolean = false;
  private life: number = 0;

  constructor(_visuals: boolean, x: number, y: number) {
    super(x, y, SpriteType.MUSHROOM);
    this.width = 4;
    this.height = 12;
    this.facing = 1;
    this.life = 0;
  }

  clone(): MarioSprite {
    const mushroom = new Mushroom(false, this.x, this.y);
    mushroom.xa = this.xa;
    mushroom.ya = this.ya;
    mushroom.width = this.width;
    mushroom.height = this.height;
    mushroom.facing = this.facing;
    mushroom.onGround = this.onGround;
    mushroom.life = this.life;
    return mushroom;
  }

  collideCheck(): void {
    if (!this.alive || !this.world) {
      return;
    }

    const xMarioD = this.world.mario.x - this.x;
    const yMarioD = this.world.mario.y - this.y;

    if (xMarioD > -16 && xMarioD < 16) {
      if (yMarioD > -this.height && yMarioD < this.world.mario.height) {
        this.world.mario.getMushroom();
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
      return;
    }

    const sideWaysSpeed = 1.75;
    if (this.xa > 2) {
      this.facing = 1;
    }
    if (this.xa < -2) {
      this.facing = -1;
    }

    this.xa = this.facing * sideWaysSpeed;

    if (!this.move(this.xa, 0)) {
      this.facing = -this.facing;
    }

    this.onGround = false;
    this.move(0, this.ya);

    this.ya *= 0.85;
    if (this.onGround) {
      this.xa *= GROUND_INERTIA;
    } else {
      this.xa *= AIR_INERTIA;
    }

    if (!this.onGround) {
      this.ya += 2;
    }
  }

  private move(xa: number, ya: number): boolean {
    while (xa > 8) {
      if (!this.move(8, 0)) return false;
      xa -= 8;
    }
    while (xa < -8) {
      if (!this.move(-8, 0)) return false;
      xa += 8;
    }
    while (ya > 8) {
      if (!this.move(0, 8)) return false;
      ya -= 8;
    }
    while (ya < -8) {
      if (!this.move(0, -8)) return false;
      ya += 8;
    }

    let collide = false;
    if (ya > 0) {
      if (this.isBlocking(this.x + xa - this.width, this.y + ya, xa, 0)) collide = true;
      else if (this.isBlocking(this.x + xa + this.width, this.y + ya, xa, 0)) collide = true;
      else if (this.isBlocking(this.x + xa - this.width, this.y + ya + 1, xa, ya)) collide = true;
      else if (this.isBlocking(this.x + xa + this.width, this.y + ya + 1, xa, ya)) collide = true;
    }
    if (ya < 0) {
      if (this.isBlocking(this.x + xa, this.y + ya - this.height, xa, ya)) collide = true;
      else if (collide || this.isBlocking(this.x + xa - this.width, this.y + ya - this.height, xa, ya))
        collide = true;
      else if (collide || this.isBlocking(this.x + xa + this.width, this.y + ya - this.height, xa, ya))
        collide = true;
    }
    if (xa > 0) {
      if (this.isBlocking(this.x + xa + this.width, this.y + ya - this.height, xa, ya)) collide = true;
      if (this.isBlocking(this.x + xa + this.width, this.y + ya - this.height / 2, xa, ya)) collide = true;
      if (this.isBlocking(this.x + xa + this.width, this.y + ya, xa, ya)) collide = true;
    }
    if (xa < 0) {
      if (this.isBlocking(this.x + xa - this.width, this.y + ya - this.height, xa, ya)) collide = true;
      if (this.isBlocking(this.x + xa - this.width, this.y + ya - this.height / 2, xa, ya)) collide = true;
      if (this.isBlocking(this.x + xa - this.width, this.y + ya, xa, ya)) collide = true;
    }

    if (collide) {
      if (xa < 0) {
        this.x = Math.floor((this.x - this.width) / 16) * 16 + this.width;
        this.xa = 0;
      }
      if (xa > 0) {
        this.x = Math.floor((this.x + this.width) / 16 + 1) * 16 - this.width - 1;
        this.xa = 0;
      }
      if (ya < 0) {
        this.y = Math.floor((this.y - this.height) / 16) * 16 + this.height;
        this.ya = 0;
      }
      if (ya > 0) {
        this.y = Math.floor(this.y / 16 + 1) * 16 - 1;
        this.onGround = true;
      }
      return false;
    } else {
      this.x += xa;
      this.y += ya;
      return true;
    }
  }

  private isBlocking(_x: number, _y: number, xa: number, ya: number): boolean {
    const x = Math.floor(_x / 16);
    const y = Math.floor(_y / 16);
    if (x === Math.floor(this.x / 16) && y === Math.floor(this.y / 16)) return false;

    if (!this.world) return false;
    return this.world.level.isBlocking(x, y, xa, ya);
  }
}

