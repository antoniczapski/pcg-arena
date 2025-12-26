/**
 * Shell sprite (kicked Koopa shell)
 * Ported from client-java/src/main/java/arena/game/sprites/Shell.java
 */

import { MarioSprite } from '../MarioSprite';
import { SpriteType } from '../SpriteType';
import { EventType } from '../EventType';

const GROUND_INERTIA = 0.89;
const AIR_INERTIA = 0.89;

export class Shell extends MarioSprite {
  private onGround: boolean = false;
  private _shellType: number = 0; // 0=red, 1=green (called avoidCliffs in Java)
  private life: number = 0;

  /** Get shell type: 0=red, 1=green */
  get shellType(): number {
    return this._shellType;
  }

  constructor(_visuals: boolean, x: number, y: number, avoidCliffs: number, initialCode: string) {
    super(x, y, SpriteType.SHELL);
    this.width = 4;
    this.height = 12;
    this.facing = 0;
    this.ya = -5; // Initial bounce when shell is created
    this._shellType = avoidCliffs; // 0=red, 1=green
    this.initialCode = initialCode;
    this.life = 0;
  }

  clone(): MarioSprite {
    const shell = new Shell(false, this.x, this.y, this._shellType, this.initialCode);
    shell.xa = this.xa;
    shell.ya = this.ya;
    shell.width = this.width;
    shell.height = this.height;
    shell.facing = this.facing;
    shell.onGround = this.onGround;
    shell.life = this.life;
    return shell;
  }

  collideCheck(): void {
    if (!this.alive || !this.world) {
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
          // Mario stomped the shell from above
          this.world.mario.stomp(this);
          if (this.facing !== 0) {
            // Shell was moving - stop it
            this.xa = 0;
            this.facing = 0;
          } else {
            // Shell was stopped - start it in Mario's direction
            this.facing = this.world.mario.facing;
          }
        } else {
          // Mario touched shell from the side
          if (this.facing !== 0) {
            // Shell is moving - hurts Mario
            this.world.addEvent(EventType.HURT, this.type);
            this.world.mario.getHurt();
          } else {
            // Shell is stopped - Mario kicks it
            this.world.addEvent(EventType.KICK, this.type);
            this.world.mario.kick(this);
            this.facing = this.world.mario.facing;
          }
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
    }

    const sideWaysSpeed = 11;
    if (this.xa > 2) {
      this.facing = 1;
    }
    if (this.xa < -2) {
      this.facing = -1;
    }

    this.xa = this.facing * sideWaysSpeed;
    if (this.facing !== 0) {
      if (this.world) {
        this.world.checkShellCollide(this);
      }
    }

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

      if (
        this._shellType !== 0 &&
        this.onGround &&
        this.world &&
        !this.world.level.isBlocking(Math.floor((this.x + xa + this.width) / 16), Math.floor(this.y / 16 + 1), xa, 1)
      ) {
        collide = true;
      }
    }
    if (xa < 0) {
      if (this.isBlocking(this.x + xa - this.width, this.y + ya - this.height, xa, ya)) collide = true;
      if (this.isBlocking(this.x + xa - this.width, this.y + ya - this.height / 2, xa, ya)) collide = true;
      if (this.isBlocking(this.x + xa - this.width, this.y + ya, xa, ya)) collide = true;

      if (
        this._shellType !== 0 &&
        this.onGround &&
        this.world &&
        !this.world.level.isBlocking(Math.floor((this.x + xa - this.width) / 16), Math.floor(this.y / 16 + 1), xa, 1)
      ) {
        collide = true;
      }
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

  fireballCollideCheck(fireball: any): boolean {
    if (!this.alive || !this.world) {
      return false;
    }

    const xD = fireball.x - this.x;
    const yD = fireball.y - this.y;

    if (xD > -16 && xD < 16) {
      if (yD > -this.height && yD < fireball.height) {
        if (this.facing !== 0) {
          return true;
        }

        this.xa = fireball.facing * 2;
        this.ya = -5;
        if (this.world.mario.facing !== 0) {
          this.facing = this.world.mario.facing;
        }
        return true;
      }
    }
    return false;
  }

  bumpCheck(xTile: number, yTile: number): void {
    if (!this.alive || !this.world) {
      return;
    }

    if (
      this.x + this.width > xTile * 16 &&
      this.x - this.width < xTile * 16 + 16 &&
      yTile === Math.floor((this.y - 1) / 16)
    ) {
      this.xa = -this.world.mario.facing * 2;
      this.ya = -5;
    }
  }
}

