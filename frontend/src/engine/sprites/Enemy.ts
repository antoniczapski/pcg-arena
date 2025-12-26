/**
 * Base enemy sprite class
 * Ported from client-java/src/main/java/arena/game/sprites/Enemy.java
 */

import { MarioSprite } from '../MarioSprite';
import { SpriteType } from '../SpriteType';
import { EventType } from '../EventType';
import { Shell } from './Shell';

const GROUND_INERTIA = 0.89;
const AIR_INERTIA = 0.89;

export class Enemy extends MarioSprite {
  protected onGround: boolean = false;
  protected avoidCliffs: boolean = true;
  protected winged: boolean = true;
  protected noFireballDeath: boolean = false;
  protected runTime: number = 0;
  protected wingTime: number = 0;

  constructor(_visuals: boolean, x: number, y: number, dir: number, type: SpriteType) {
    super(x, y, type);
    this.width = 4;
    this.height = 24;
    
    if (
      this.type !== SpriteType.RED_KOOPA &&
      this.type !== SpriteType.GREEN_KOOPA &&
      this.type !== SpriteType.RED_KOOPA_WINGED &&
      this.type !== SpriteType.GREEN_KOOPA_WINGED
    ) {
      this.height = 12;
    }
    
    this.winged = this.type % 2 === 1;
    this.avoidCliffs = this.type === SpriteType.RED_KOOPA || this.type === SpriteType.RED_KOOPA_WINGED;
    this.noFireballDeath = this.type === SpriteType.SPIKY || this.type === SpriteType.SPIKY_WINGED;
    this.facing = dir;
    if (this.facing === 0) {
      this.facing = 1;
    }
  }

  clone(): MarioSprite {
    const e = new Enemy(false, this.x, this.y, this.facing, this.type);
    e.xa = this.xa;
    e.ya = this.ya;
    e.initialCode = this.initialCode;
    e.width = this.width;
    e.height = this.height;
    e.onGround = this.onGround;
    e.winged = this.winged;
    e.avoidCliffs = this.avoidCliffs;
    e.noFireballDeath = this.noFireballDeath;
    return e;
  }

  collideCheck(): void {
    if (!this.alive || !this.world) {
      return;
    }

    const xMarioD = this.world.mario.x - this.x;
    const yMarioD = this.world.mario.y - this.y;
    
    if (xMarioD > -this.width * 2 - 4 && xMarioD < this.width * 2 + 4) {
      if (yMarioD > -this.height && yMarioD < this.world.mario.height) {
        if (
          this.type !== SpriteType.SPIKY &&
          this.type !== SpriteType.SPIKY_WINGED &&
          this.type !== SpriteType.ENEMY_FLOWER &&
          this.world.mario.ya > 0 &&
          yMarioD <= 0 &&
          (!this.world.mario.onGround || !this.world.mario.wasOnGround)
        ) {
          this.world.mario.stomp(this);
          if (this.winged) {
            this.winged = false;
            this.ya = 0;
          } else {
            if (this.type === SpriteType.GREEN_KOOPA || this.type === SpriteType.GREEN_KOOPA_WINGED) {
              this.world.addSprite(new Shell(true, this.x, this.y, 1, this.initialCode));
            } else if (this.type === SpriteType.RED_KOOPA || this.type === SpriteType.RED_KOOPA_WINGED) {
              this.world.addSprite(new Shell(true, this.x, this.y, 0, this.initialCode));
            }
            this.world.addEvent(EventType.STOMP_KILL, this.type);
            this.world.removeSprite(this);
          }
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

    this.ya *= this.winged ? 0.95 : 0.85;
    if (this.onGround) {
      this.xa *= GROUND_INERTIA;
    } else {
      this.xa *= AIR_INERTIA;
    }

    if (!this.onGround) {
      if (this.winged) {
        this.ya += 0.6;
      } else {
        this.ya += 2;
      }
    } else if (this.winged) {
      this.ya = -10;
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
        this.avoidCliffs &&
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
        this.avoidCliffs &&
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

  shellCollideCheck(shell: any): boolean {
    if (!this.alive || !this.world) {
      return false;
    }

    const xD = shell.x - this.x;
    const yD = shell.y - this.y;

    if (xD > -16 && xD < 16) {
      if (yD > -this.height && yD < shell.height) {
        this.xa = shell.facing * 2;
        this.ya = -5;
        this.world.addEvent(EventType.SHELL_KILL, this.type);
        this.world.removeSprite(this);
        return true;
      }
    }
    return false;
  }

  fireballCollideCheck(fireball: any): boolean {
    if (!this.alive || !this.world) {
      return false;
    }

    const xD = fireball.x - this.x;
    const yD = fireball.y - this.y;

    if (xD > -16 && xD < 16) {
      if (yD > -this.height && yD < fireball.height) {
        if (this.noFireballDeath) return true;

        this.xa = fireball.facing * 2;
        this.ya = -5;
        this.world.addEvent(EventType.FIRE_KILL, this.type);
        this.world.removeSprite(this);
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
      this.world.removeSprite(this);
    }
  }
}

