/**
 * Tile feature flags
 * Ported from client-java/src/main/java/arena/game/helper/TileFeature.java
 */

export enum TileFeature {
  BLOCK_UPPER,
  BLOCK_ALL,
  BLOCK_LOWER,
  SPECIAL,
  LIFE,
  BUMPABLE,
  BREAKABLE,
  PICKABLE,
  ANIMATED,
  SPAWNER,
}

export function getTileType(index: number): TileFeature[] {
  const features: TileFeature[] = [];

  switch (index) {
    case 1:
    case 2:
    case 14:
    case 18:
    case 19:
    case 20:
    case 21:
    case 4:
    case 5:
    case 52:
    case 53:
      features.push(TileFeature.BLOCK_ALL);
      break;
    case 43:
    case 44:
    case 45:
    case 46:
      features.push(TileFeature.BLOCK_LOWER);
      break;
    case 48:
      features.push(TileFeature.BLOCK_UPPER);
      features.push(TileFeature.LIFE);
      features.push(TileFeature.BUMPABLE);
      break;
    case 49:
      features.push(TileFeature.BUMPABLE);
      features.push(TileFeature.BLOCK_UPPER);
      break;
    case 3:
      features.push(TileFeature.BLOCK_ALL);
      features.push(TileFeature.SPAWNER);
      break;
    case 8:
      features.push(TileFeature.BLOCK_ALL);
      features.push(TileFeature.SPECIAL);
      features.push(TileFeature.BUMPABLE);
      features.push(TileFeature.ANIMATED);
      break;
    case 11:
      features.push(TileFeature.BLOCK_ALL);
      features.push(TileFeature.BUMPABLE);
      features.push(TileFeature.ANIMATED);
      break;
    case 6:
      features.push(TileFeature.BLOCK_ALL);
      features.push(TileFeature.BREAKABLE);
      break;
    case 7:
      features.push(TileFeature.BLOCK_ALL);
      features.push(TileFeature.BUMPABLE);
      break;
    case 15:
      features.push(TileFeature.PICKABLE);
      features.push(TileFeature.ANIMATED);
      break;
    case 50:
      features.push(TileFeature.BLOCK_ALL);
      features.push(TileFeature.SPECIAL);
      features.push(TileFeature.BUMPABLE);
      break;
    case 51:
      features.push(TileFeature.BLOCK_ALL);
      features.push(TileFeature.LIFE);
      features.push(TileFeature.BUMPABLE);
      break;
  }

  return features;
}

export function hasTileFeature(features: TileFeature[], feature: TileFeature): boolean {
  return features.includes(feature);
}

