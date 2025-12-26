/**
 * Mario game event
 * Ported from client-java/src/main/java/arena/game/core/MarioEvent.java
 */

import { EventType } from './EventType';

export class MarioEvent {
  eventType: EventType;
  eventParam: number;
  marioX: number;
  marioY: number;
  marioState: number;
  tick: number;

  constructor(
    eventType: EventType,
    eventParam: number,
    marioX: number,
    marioY: number,
    marioState: number,
    tick: number
  ) {
    this.eventType = eventType;
    this.eventParam = eventParam;
    this.marioX = marioX;
    this.marioY = marioY;
    this.marioState = marioState;
    this.tick = tick;
  }

  equals(other: MarioEvent): boolean {
    return (
      this.eventType === other.eventType &&
      this.eventParam === other.eventParam
    );
  }
}

