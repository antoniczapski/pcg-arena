/**
 * Mario world state and game logic
 * Ported from client-java/src/main/java/arena/game/core/MarioWorld.java
 */

import { GameStatus } from './GameStatus';
import { MarioSprite } from './MarioSprite';
import { Mario } from './sprites/Mario';
import { Enemy } from './sprites/Enemy';
import { Mushroom } from './sprites/Mushroom';
import { FireFlower } from './sprites/FireFlower';
import { LifeMushroom } from './sprites/LifeMushroom';
import { FlowerEnemy } from './sprites/FlowerEnemy';
import { BulletBill } from './sprites/BulletBill';
import { MarioLevel, GAME_WIDTH, GAME_HEIGHT } from './MarioLevel';
import { MarioEvent } from './MarioEvent';
import { EventType } from './EventType';
import { SpriteType } from './SpriteType';
import { TileFeature, getTileType, hasTileFeature } from './TileFeature';

const TILE_WIDTH = GAME_WIDTH / 16;
const TILE_HEIGHT = GAME_HEIGHT / 16;

export class MarioWorld {
  gameStatus: GameStatus = GameStatus.RUNNING;
  pauseTimer: number = 0;
  fireballsOnScreen: number = 0;
  currentTimer: number = -1;
  cameraX: number = 0;
  cameraY: number = 0;
  mario: Mario;
  level: MarioLevel;
  visuals: boolean = false;
  currentTick: number = 0;
  coins: number = 0;
  lives: number = 0;
  lastFrameEvents: MarioEvent[] = [];

  private killEvents: MarioEvent[] | null = null;
  private sprites: MarioSprite[] = [];
  private shellsToCheck: any[] = [];
  private fireballsToCheck: any[] = [];
  private addedSprites: MarioSprite[] = [];
  private removedSprites: MarioSprite[] = [];

  constructor(killEvents: MarioEvent[] | null = null) {
    this.pauseTimer = 0;
    this.gameStatus = GameStatus.RUNNING;
    this.sprites = [];
    this.shellsToCheck = [];
    this.fireballsToCheck = [];
    this.addedSprites = [];
    this.removedSprites = [];
    this.lastFrameEvents = [];
    this.killEvents = killEvents;

    // Mario will be initialized in initializeLevel
    this.mario = new Mario(false, 0, 0);
    this.level = new MarioLevel('', false);
  }

  initializeLevel(level: string, timer: number): void {
    this.currentTimer = timer;
    this.level = new MarioLevel(level, this.visuals);

    this.mario = new Mario(this.visuals, this.level.marioTileX * 16, this.level.marioTileY * 16);
    this.mario.alive = true;
    this.mario.world = this;
    this.sprites.push(this.mario);
  }

  getEnemies(): MarioSprite[] {
    return this.sprites.filter((sprite) => this.isEnemy(sprite));
  }

  clone(): MarioWorld {
    const world = new MarioWorld(this.killEvents);
    world.visuals = false;
    world.cameraX = this.cameraX;
    world.cameraY = this.cameraY;
    world.fireballsOnScreen = this.fireballsOnScreen;
    world.gameStatus = this.gameStatus;
    world.pauseTimer = this.pauseTimer;
    world.currentTimer = this.currentTimer;
    world.currentTick = this.currentTick;
    world.level = this.level.clone();

    for (const sprite of this.sprites) {
      const cloneSprite = sprite.clone();
      cloneSprite.world = world;
      if (cloneSprite.type === SpriteType.MARIO) {
        world.mario = cloneSprite as Mario;
      }
      world.sprites.push(cloneSprite);
    }

    if (!world.mario.alive) {
      world.mario = this.mario.clone() as Mario;
    }

    world.coins = this.coins;
    world.lives = this.lives;
    return world;
  }

  addEvent(eventType: EventType, eventParam: number): void {
    let marioState = 0;
    if (this.mario.isLarge) {
      marioState = 1;
    }
    if (this.mario.isFire) {
      marioState = 2;
    }
    this.lastFrameEvents.push(
      new MarioEvent(eventType, eventParam, this.mario.x, this.mario.y, marioState, this.currentTick)
    );
  }

  addSprite(sprite: MarioSprite): void {
    this.addedSprites.push(sprite);
    sprite.alive = true;
    sprite.world = this;
    sprite.added();
    sprite.update();
  }

  removeSprite(sprite: MarioSprite): void {
    this.removedSprites.push(sprite);
    sprite.alive = false;
    sprite.removed();
    sprite.world = null;
  }

  checkShellCollide(shell: any): void {
    this.shellsToCheck.push(shell);
  }

  checkFireballCollide(fireball: any): void {
    this.fireballsToCheck.push(fireball);
  }

  win(): void {
    this.addEvent(EventType.WIN, 0);
    this.gameStatus = GameStatus.WIN;
  }

  lose(): void {
    this.addEvent(EventType.LOSE, 0);
    this.gameStatus = GameStatus.LOSE;
    this.mario.alive = false;
  }

  timeout(): void {
    this.gameStatus = GameStatus.TIME_OUT;
    this.mario.alive = false;
  }

  getSceneObservation(centerX: number, centerY: number, _detail: number): number[][] {
    const ret: number[][] = Array(TILE_WIDTH)
      .fill(null)
      .map(() => Array(TILE_HEIGHT).fill(0));
    const centerXInMap = Math.floor(centerX / 16);
    const centerYInMap = Math.floor(centerY / 16);

    for (let y = centerYInMap - TILE_HEIGHT / 2, obsY = 0; y < centerYInMap + TILE_HEIGHT / 2; y++, obsY++) {
      for (let x = centerXInMap - TILE_WIDTH / 2, obsX = 0; x < centerXInMap + TILE_WIDTH / 2; x++, obsX++) {
        let currentX = x;
        if (currentX < 0) currentX = 0;
        if (currentX > this.level.tileWidth - 1) currentX = this.level.tileWidth - 1;
        let currentY = y;
        if (currentY < 0) currentY = 0;
        if (currentY > this.level.tileHeight - 1) currentY = this.level.tileHeight - 1;
        ret[obsX][obsY] = this.level.getBlock(currentX, currentY); // Simplified - full implementation would use generalization
      }
    }
    return ret;
  }

  update(actions: boolean[]): void {
    if (this.gameStatus !== GameStatus.RUNNING) {
      return;
    }
    if (this.pauseTimer > 0) {
      this.pauseTimer -= 1;
      return;
    }

    if (this.currentTimer > 0) {
      this.currentTimer -= 30;
      if (this.currentTimer <= 0) {
        this.currentTimer = 0;
        this.timeout();
        return;
      }
    }

    this.currentTick += 1;
    this.cameraX = this.mario.x - GAME_WIDTH / 2;
    if (this.cameraX + GAME_WIDTH > this.level.width) {
      this.cameraX = this.level.width - GAME_WIDTH;
    }
    if (this.cameraX < 0) {
      this.cameraX = 0;
    }
    this.cameraY = this.mario.y - GAME_HEIGHT / 2;
    if (this.cameraY + GAME_HEIGHT > this.level.height) {
      this.cameraY = this.level.height - GAME_HEIGHT;
    }
    if (this.cameraY < 0) {
      this.cameraY = 0;
    }

    this.lastFrameEvents = [];

    this.fireballsOnScreen = 0;
    for (const sprite of this.sprites) {
      if (
        sprite.x < this.cameraX - 64 ||
        sprite.x > this.cameraX + GAME_WIDTH + 64 ||
        sprite.y > this.level.height + 32
      ) {
        if (sprite.type === SpriteType.MARIO) {
          this.lose();
        }
        this.removeSprite(sprite);
        if (this.isEnemy(sprite) && sprite.y > GAME_HEIGHT + 32) {
          this.addEvent(EventType.FALL_KILL, sprite.type);
        }
        continue;
      }
      if (sprite.type === SpriteType.FIREBALL) {
        this.fireballsOnScreen += 1;
      }
    }

    this.level.update(Math.floor(this.cameraX), Math.floor(this.cameraY));

    // Sprite spawning logic
    for (let x = Math.floor(this.cameraX / 16) - 1; x <= Math.floor((this.cameraX + GAME_WIDTH) / 16) + 1; x++) {
      for (let y = Math.floor(this.cameraY / 16) - 1; y <= Math.floor((this.cameraY + GAME_HEIGHT) / 16) + 1; y++) {
        let dir = 0;
        if (x * 16 + 8 > this.mario.x + 16) dir = -1;
        if (x * 16 + 8 < this.mario.x - 16) dir = 1;

        const type = this.level.getSpriteType(x, y);
        if (type !== SpriteType.NONE) {
          const spriteCode = this.level.getSpriteCode(x, y);
          let found = false;
          for (const sprite of this.sprites) {
            if (sprite.initialCode === spriteCode) {
              found = true;
              break;
            }
          }
          if (!found) {
            if (this.level.getLastSpawnTick(x, y) !== this.currentTick - 1) {
              let sprite: MarioSprite | null = null;
              
              switch (type) {
                case SpriteType.GOOMBA:
                case SpriteType.GOOMBA_WINGED:
                case SpriteType.RED_KOOPA:
                case SpriteType.RED_KOOPA_WINGED:
                case SpriteType.GREEN_KOOPA:
                case SpriteType.GREEN_KOOPA_WINGED:
                case SpriteType.SPIKY:
                case SpriteType.SPIKY_WINGED:
                  sprite = new Enemy(this.visuals, x * 16 + 8, y * 16 + 15, dir, type);
                  break;
                case SpriteType.ENEMY_FLOWER:
                  // FlowerEnemy spawns centered in pipe: Java uses xTile * 16 + 17, yTile * 16 + 18
                  sprite = new FlowerEnemy(this.visuals, x * 16 + 17, y * 16 + 18);
                  break;
              }
              
              if (sprite) {
                sprite.initialCode = spriteCode;
                this.addSprite(sprite);
              }
            }
          }
          this.level.setLastSpawnTick(x, y, this.currentTick);
        }

        if (dir !== 0) {
          const features = getTileType(this.level.getBlock(x, y));
          if (hasTileFeature(features, TileFeature.SPAWNER)) {
            if (this.currentTick % 100 === 0) {
              this.addSprite(new BulletBill(this.visuals, x * 16 + 8 + dir * 8, y * 16 + 15, dir));
            }
          }
        }
      }
    }

    this.mario.actions = actions;
    for (const sprite of this.sprites) {
      if (!sprite.alive) continue;
      sprite.update();
    }
    for (const sprite of this.sprites) {
      if (!sprite.alive) continue;
      sprite.collideCheck();
    }

    for (const shell of this.shellsToCheck) {
      for (const sprite of this.sprites) {
        if (sprite !== shell && shell.alive && sprite.alive) {
          if (sprite.shellCollideCheck(shell)) {
            this.removeSprite(sprite);
          }
        }
      }
    }
    this.shellsToCheck = [];

    for (const fireball of this.fireballsToCheck) {
      for (const sprite of this.sprites) {
        if (sprite !== fireball && fireball.alive && sprite.alive) {
          if (sprite.fireballCollideCheck(fireball)) {
            this.removeSprite(fireball);
          }
        }
      }
    }
    this.fireballsToCheck = [];

    this.sprites.unshift(...this.addedSprites);
    this.sprites = this.sprites.filter((s) => !this.removedSprites.includes(s));
    this.addedSprites = [];
    this.removedSprites = [];

    // Punishing forward model
    if (this.killEvents) {
      for (const k of this.killEvents) {
        for (const event of this.lastFrameEvents) {
          if (event.equals(k)) {
            this.lose();
          }
        }
      }
    }
  }

  bump(xTile: number, yTile: number, canBreakBricks: boolean): void {
    const block = this.level.getBlock(xTile, yTile);
    const features = getTileType(block);

    if (hasTileFeature(features, TileFeature.BUMPABLE)) {
      this.bumpInto(xTile, yTile - 1);
      this.addEvent(EventType.BUMP, 2); // OBS_QUESTION_BLOCK
      this.level.setBlock(xTile, yTile, 14);
      this.level.setShiftIndex(xTile, yTile, 4);

      if (hasTileFeature(features, TileFeature.SPECIAL)) {
        if (!this.mario.isLarge) {
          this.addSprite(new Mushroom(this.visuals, xTile * 16 + 9, yTile * 16 + 8));
        } else {
          this.addSprite(new FireFlower(this.visuals, xTile * 16 + 9, yTile * 16 + 8));
        }
      } else if (hasTileFeature(features, TileFeature.LIFE)) {
        this.addSprite(new LifeMushroom(this.visuals, xTile * 16 + 9, yTile * 16 + 8));
      } else {
        this.mario.collectCoin();
      }
    }

    if (hasTileFeature(features, TileFeature.BREAKABLE)) {
      this.bumpInto(xTile, yTile - 1);
      if (canBreakBricks) {
        this.addEvent(EventType.BUMP, 1); // OBS_BRICK
        this.level.setBlock(xTile, yTile, 0);
      } else {
        this.level.setShiftIndex(xTile, yTile, 4);
      }
    }
  }

  bumpInto(xTile: number, yTile: number): void {
    const block = this.level.getBlock(xTile, yTile);
    const features = getTileType(block);
    if (hasTileFeature(features, TileFeature.PICKABLE)) {
      this.addEvent(EventType.COLLECT, block);
      this.mario.collectCoin();
      this.level.setBlock(xTile, yTile, 0);
    }

    for (const sprite of this.sprites) {
      sprite.bumpCheck(xTile, yTile);
    }
  }

  render(ctx: CanvasRenderingContext2D, tilemapRenderer: any, spriteRenderer: any, camera: any): void {
    // Render tilemap
    tilemapRenderer.render(ctx, this.level, camera);

    // Render sprites
    for (const sprite of this.sprites) {
      if (sprite.alive) {
        spriteRenderer.renderSprite(ctx, sprite, camera);
      }
    }

    // Update sprite animations
    spriteRenderer.updateAnimations();
  }

  private isEnemy(sprite: MarioSprite): boolean {
    return (
      sprite.type === SpriteType.GOOMBA ||
      sprite.type === SpriteType.GOOMBA_WINGED ||
      sprite.type === SpriteType.RED_KOOPA ||
      sprite.type === SpriteType.RED_KOOPA_WINGED ||
      sprite.type === SpriteType.GREEN_KOOPA ||
      sprite.type === SpriteType.GREEN_KOOPA_WINGED ||
      sprite.type === SpriteType.SPIKY ||
      sprite.type === SpriteType.SPIKY_WINGED ||
      sprite.type === SpriteType.ENEMY_FLOWER ||
      sprite.type === SpriteType.BULLET_BILL
    );
  }
}

