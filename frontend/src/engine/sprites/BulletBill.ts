/**
 * Bullet Bill enemy sprite
 * Ported from client-java/src/main/java/arena/game/sprites/BulletBill.java
 */

import { MarioSprite } from '../MarioSprite';
import { SpriteType } from '../SpriteType';
import { EventType } from '../EventType';

const AIR_INERTIA = 0.95;

export class BulletBill extends MarioSprite {
  private life: number = 0;
  private dead: boolean = false;
  private onGround: boolean = false;

  constructor(visuals: boolean, x: number, y: number, dir: number) {
    super(x, y, SpriteType.BULLET_BILL);
    this.width = 4;
    this.height = 12;
    this.facing = dir;
    this.life = 0;
    this.dead = false;
  }

  clone(): MarioSprite {
    const bullet = new BulletBill(false, this.x, this.y, this.facing);
    bullet.xa = this.xa;
    bullet.ya = this.ya;
    bullet.width = this.width;
    bullet.height = this.height;
    bullet.life = this.life;
    bullet.dead = this.dead;
    bullet.onGround = this.onGround;
    return bullet;
  }

  collideCheck(): void {
    if (!this.alive || !this.world || this.dead) {
      return;
    }

    const xMarioD = this.world.mario.x - this.x;
    const yMarioD = this.world.mario.y - this.y;

    if (xMarioD > -16 && xMarioD < 16) {
      if (yMarioD > -this.height && yMarioD < this.world.mario.height) {
        if (
          this.world.mario.ya > 0 &&
          yMarioD <= 0 &&
          (!this.world.mario.onGround || !this.world.mario.wasOnGround)
        ) {
          this.world.mario.stomp(this);
          this.dead = true;
          this.xa = 0;
          this.ya = 1;
          this.world.addEvent(EventType.STOMP_KILL, this.type);
        } else {
          this.world.addEvent(EventType.HURT, this.type);
          this.world.mario.getHurt();
        }
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

    if (this.dead) {
      this.xa = 0;
      this.ya += 1;
      this.move(this.xa, this.ya);
      return;
    }

    const sideWaysSpeed = 4;

    if (this.xa > 2) {
      this.facing = 1;
    }
    if (this.xa < -2) {
      this.facing = -1;
    }

    this.xa = this.facing * sideWaysSpeed;
    this.move(this.xa, 0);

    this.xa *= AIR_INERTIA;
  }

  private move(xa: number, ya: number): boolean {
    this.x += xa;
    this.y += ya;
    return true;
  }

  shellCollideCheck(shell: any): boolean {
    if (!this.alive || !this.world || this.dead) {
      return false;
    }

    const xD = shell.x - this.x;
    const yD = shell.y - this.y;

    if (xD > -16 && xD < 16) {
      if (yD > -this.height && yD < shell.height) {
        this.xa = shell.facing * 2;
        this.ya = -5;
        this.dead = true;
        this.world.addEvent(EventType.SHELL_KILL, this.type);
        return true;
      }
    }
    return false;
  }

  fireballCollideCheck(fireball: any): boolean {
    if (!this.alive || !this.world || this.dead) {
      return false;
    }

    const xD = fireball.x - this.x;
    const yD = fireball.y - this.y;

    if (xD > -16 && xD < 16) {
      if (yD > -this.height && yD < fireball.height) {
        this.xa = fireball.facing * 2;
        this.ya = -5;
        this.dead = true;
        this.world.addEvent(EventType.FIRE_KILL, this.type);
        return true;
      }
    }
    return false;
  }

  bumpCheck(xTile: number, yTile: number): void {
    if (!this.alive || !this.world || this.dead) {
      return;
    }

    if (
      this.x + this.width > xTile * 16 &&
      this.x - this.width < xTile * 16 + 16 &&
      yTile === Math.floor((this.y - 1) / 16)
    ) {
      this.xa = -this.world.mario.facing * 2;
      this.ya = -5;
      this.dead = true;
    }
  }
}

