/**
 * Mario player sprite with physics
 * Ported from client-java/src/main/java/arena/game/sprites/Mario.java
 */

import { MarioSprite } from '../MarioSprite';
import { SpriteType } from '../SpriteType';
import { MarioActions } from '../MarioActions';
import { TileFeature, getTileType, hasTileFeature } from '../TileFeature';
import { EventType } from '../EventType';
import { Fireball } from './Fireball';

const GROUND_INERTIA = 0.89;
const AIR_INERTIA = 0.89;
const POWERUP_TIME = 3;

export class Mario extends MarioSprite {
  isLarge: boolean = false;
  isFire: boolean = false;
  onGround: boolean = false;
  wasOnGround: boolean = false;
  isDucking: boolean = false;
  canShoot: boolean = false;
  mayJump: boolean = false;
  actions: boolean[] = [false, false, false, false, false];
  jumpTime: number = 0;

  private xJumpSpeed: number = 0;
  private yJumpSpeed: number = 0;
  private invulnerableTime: number = 0;
  private xJumpStart: number = -100;

  constructor(_visuals: boolean, x: number, y: number) {
    super(x + 8, y + 15, SpriteType.MARIO);
    this.isLarge = false;
    this.isFire = false;
    this.width = 4;
    this.height = 24;
  }

  clone(): MarioSprite {
    const sprite = new Mario(false, this.x - 8, this.y - 15);
    sprite.xa = this.xa;
    sprite.ya = this.ya;
    sprite.initialCode = this.initialCode;
    sprite.width = this.width;
    sprite.height = this.height;
    sprite.facing = this.facing;
    sprite.isLarge = this.isLarge;
    sprite.isFire = this.isFire;
    sprite.wasOnGround = this.wasOnGround;
    sprite.onGround = this.onGround;
    sprite.isDucking = this.isDucking;
    sprite.canShoot = this.canShoot;
    sprite.mayJump = this.mayJump;
    sprite.actions = [...this.actions];
    sprite.xJumpSpeed = this.xJumpSpeed;
    sprite.yJumpSpeed = this.yJumpSpeed;
    sprite.invulnerableTime = this.invulnerableTime;
    sprite.jumpTime = this.jumpTime;
    sprite.xJumpStart = this.xJumpStart;
    return sprite;
  }

  collideCheck(): void {
    // Collision checking is done in MarioWorld
  }

  update(): void {
    if (!this.alive) {
      return;
    }

    if (this.invulnerableTime > 0) {
      this.invulnerableTime--;
    }
    this.wasOnGround = this.onGround;

    const sideWaysSpeed = this.actions[MarioActions.SPEED] ? 1.2 : 0.6;

    if (this.onGround) {
      this.isDucking = this.actions[MarioActions.DOWN] && this.isLarge;
    }

    if (this.isLarge) {
      this.height = this.isDucking ? 12 : 24;
    } else {
      this.height = 12;
    }

    if (this.xa > 2) {
      this.facing = 1;
    }
    if (this.xa < -2) {
      this.facing = -1;
    }

    if (this.actions[MarioActions.JUMP] || (this.jumpTime < 0 && !this.onGround)) {
      if (this.jumpTime < 0) {
        this.xa = this.xJumpSpeed;
        this.ya = -this.jumpTime * this.yJumpSpeed;
        this.jumpTime++;
      } else if (this.onGround && this.mayJump) {
        this.xJumpSpeed = 0;
        this.yJumpSpeed = -1.9;
        this.jumpTime = 7;
        this.ya = this.jumpTime * this.yJumpSpeed;
        this.onGround = false;
        if (
          !(
            this.isBlocking(this.x, this.y - 4 - this.height, 0, -4) ||
            this.isBlocking(this.x - this.width, this.y - 4 - this.height, 0, -4) ||
            this.isBlocking(this.x + this.width, this.y - 4 - this.height, 0, -4)
          )
        ) {
          this.xJumpStart = this.x;
          if (this.world) {
            this.world.addEvent(EventType.JUMP, 0);
          }
        }
      } else if (this.jumpTime > 0) {
        this.xa += this.xJumpSpeed;
        this.ya = this.jumpTime * this.yJumpSpeed;
        this.jumpTime--;
      }
    } else {
      this.jumpTime = 0;
    }

    if (this.actions[MarioActions.LEFT] && !this.isDucking) {
      this.xa -= sideWaysSpeed;
      if (this.jumpTime >= 0) this.facing = -1;
    }

    if (this.actions[MarioActions.RIGHT] && !this.isDucking) {
      this.xa += sideWaysSpeed;
      if (this.jumpTime >= 0) this.facing = 1;
    }

    if (
      this.actions[MarioActions.SPEED] &&
      this.canShoot &&
      this.isFire &&
      this.world &&
      this.world.fireballsOnScreen < 2
    ) {
      this.world.addSprite(new Fireball(true, this.x + this.facing * 6, this.y - 20, this.facing));
    }

    this.canShoot = !this.actions[MarioActions.SPEED];
    this.mayJump = this.onGround && !this.actions[MarioActions.JUMP];

    if (Math.abs(this.xa) < 0.5) {
      this.xa = 0;
    }

    this.onGround = false;
    this.move(this.xa, 0);
    this.move(0, this.ya);

    if (!this.wasOnGround && this.onGround && this.xJumpStart >= 0 && this.world) {
      this.world.addEvent(EventType.LAND, 0);
      this.xJumpStart = -100;
    }

    if (this.x < 0) {
      this.x = 0;
      this.xa = 0;
    }

    if (this.world && this.x > this.world.level.exitTileX * 16) {
      this.x = this.world.level.exitTileX * 16;
      this.xa = 0;
      this.world.win();
    }

    this.ya *= 0.85;
    if (this.onGround) {
      this.xa *= GROUND_INERTIA;
    } else {
      this.xa *= AIR_INERTIA;
    }

    if (!this.onGround) {
      this.ya += 3;
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
        // Round to tile boundary: move left edge to tile boundary
        this.x = Math.floor((this.x - this.width) / 16) * 16 + this.width;
        this.xa = 0;
      }
      if (xa > 0) {
        // Round to tile boundary: move right edge to 1 pixel before next tile
        // Java: (int) ((x + width) / 16 + 1) * 16 - width - 1
        const rightEdge = this.x + this.width;
        const nextTileRight = (Math.floor(rightEdge / 16) + 1) * 16;
        this.x = nextTileRight - this.width - 1;
        this.xa = 0;
      }
      if (ya < 0) {
        // Round to tile boundary: move top edge to tile boundary
        this.y = Math.floor((this.y - this.height) / 16) * 16 + this.height;
        this.jumpTime = 0;
        this.ya = 0;
      }
      if (ya > 0) {
        // Round to tile boundary: move bottom to tile boundary
        // Java: (int) ((y - 1) / 16 + 1) * 16 - 1
        this.y = (Math.floor((this.y - 1) / 16) + 1) * 16 - 1;
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
    const xTile = Math.floor(_x / 16);
    const yTile = Math.floor(_y / 16);
    if (xTile === Math.floor(this.x / 16) && yTile === Math.floor(this.y / 16)) return false;

    if (!this.world) return false;

    const blocking = this.world.level.isBlocking(xTile, yTile, xa, ya);
    const block = this.world.level.getBlock(xTile, yTile);

    const features = getTileType(block);
    if (hasTileFeature(features, TileFeature.PICKABLE)) {
      this.world.addEvent(EventType.COLLECT, block);
      this.collectCoin();
      this.world.level.setBlock(xTile, yTile, 0);
    }
    if (blocking && ya < 0) {
      this.world.bump(xTile, yTile, this.isLarge);
    }
    return blocking;
  }

  stomp(enemy: any): void {
    if (!this.alive) return;
    const targetY = enemy.y - enemy.height / 2;
    this.move(0, targetY - this.y);

    this.xJumpSpeed = 0;
    this.yJumpSpeed = -1.9;
    this.jumpTime = 8;
    this.ya = this.jumpTime * this.yJumpSpeed;
    this.onGround = false;
    this.invulnerableTime = 1;
  }

  getHurt(): void {
    if (this.invulnerableTime > 0 || !this.alive) return;

    if (this.isLarge && this.world) {
      this.world.pauseTimer = 3 * POWERUP_TIME;
      if (this.isFire) {
        this.isFire = false;
      } else {
        this.isLarge = false;
      }
      this.invulnerableTime = 32;
    } else {
      if (this.world) {
        this.world.lose();
      }
    }
  }

  getFlower(): void {
    if (!this.alive) return;

    if (!this.isFire && this.world) {
      this.world.pauseTimer = 3 * POWERUP_TIME;
      this.isFire = true;
      this.isLarge = true;
    } else {
      this.collectCoin();
    }
  }

  getMushroom(): void {
    if (!this.alive) return;

    if (!this.isLarge && this.world) {
      this.world.pauseTimer = 3 * POWERUP_TIME;
      this.isLarge = true;
    } else {
      this.collectCoin();
    }
  }

  kick(_shell: any): void {
    if (!this.alive) return;
    this.invulnerableTime = 1;
  }

  getMarioType(): string {
    if (this.isFire) return 'fire';
    if (this.isLarge) return 'large';
    return 'small';
  }

  collect1Up(): void {
    if (!this.alive || !this.world) return;
    this.world.lives++;
  }

  collectCoin(): void {
    if (!this.alive || !this.world) return;
    this.world.coins++;
    if (this.world.coins % 100 === 0) {
      this.collect1Up();
    }
  }
}

