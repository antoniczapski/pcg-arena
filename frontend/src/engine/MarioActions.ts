/**
 * Mario action constants
 * Ported from client-java/src/main/java/arena/game/helper/MarioActions.java
 */

export enum MarioActions {
  LEFT = 0,
  RIGHT = 1,
  DOWN = 2,
  SPEED = 3,
  JUMP = 4,
}

export function numberOfActions(): number {
  return 5;
}

export function createActionArray(): boolean[] {
  return new Array(numberOfActions()).fill(false);
}

