/**
 * Sprite type enum with sprite spawning logic
 * Ported from client-java/src/main/java/arena/game/helper/SpriteType.java
 */

export enum SpriteType {
  NONE = -1,
  MARIO = 0,
  GOOMBA = 2,
  GOOMBA_WINGED = 3,
  RED_KOOPA = 4,
  RED_KOOPA_WINGED = 5,
  GREEN_KOOPA = 6,
  GREEN_KOOPA_WINGED = 7,
  SPIKY = 8,
  SPIKY_WINGED = 9,
  BULLET_BILL = 10,
  ENEMY_FLOWER = 12,
  MUSHROOM = 13,
  FIRE_FLOWER = 14,
  FIREBALL = 15,
  SHELL = 16,
  LIFE_MUSHROOM = 17,
}

export function getSpriteTypeValue(type: SpriteType): number {
  return type;
}

export function getSpriteTypeStartIndex(type: SpriteType): number {
  switch (type) {
    case SpriteType.GOOMBA:
    case SpriteType.GOOMBA_WINGED:
      return 44;
    case SpriteType.RED_KOOPA:
    case SpriteType.RED_KOOPA_WINGED:
      return 41;
    case SpriteType.GREEN_KOOPA:
    case SpriteType.GREEN_KOOPA_WINGED:
      return 42;
    case SpriteType.SPIKY:
    case SpriteType.SPIKY_WINGED:
      return 45;
    default:
      return 0;
  }
}

export function spawnSprite(
  type: SpriteType,
  visuals: boolean,
  x: number,
  y: number,
  dir: number
): any {
  // Import sprites (circular dependency avoided via dynamic imports in actual usage)
  // For now, these will be imported by MarioWorld when needed
  switch (type) {
    case SpriteType.GOOMBA:
    case SpriteType.GOOMBA_WINGED:
    case SpriteType.RED_KOOPA:
    case SpriteType.RED_KOOPA_WINGED:
    case SpriteType.GREEN_KOOPA:
    case SpriteType.GREEN_KOOPA_WINGED:
    case SpriteType.SPIKY:
    case SpriteType.SPIKY_WINGED:
      // Enemy will be spawned by MarioWorld
      return { type, visuals, x: x * 16 + 8, y: y * 16 + 15, dir };
    case SpriteType.ENEMY_FLOWER:
      // FlowerEnemy spawns at different offset to be centered in pipe
      // Java: xTile * 16 + 17, yTile * 16 + 18
      return { type, visuals, x: x * 16 + 17, y: y * 16 + 18, dir: 0 };
    default:
      return null;
  }
}

