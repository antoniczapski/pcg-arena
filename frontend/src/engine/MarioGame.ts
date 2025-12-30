/**
 * Mario game controller with game loop
 * Ported from client-java/src/main/java/arena/game/core/MarioGame.java
 */

import { MarioWorld } from './MarioWorld';
import { MarioEvent } from './MarioEvent';
import { GameStatus } from './GameStatus';
import { numberOfActions } from './MarioActions';

export interface MarioResult {
  world: MarioWorld;
  gameEvents: MarioEvent[];
  gameStatus: GameStatus;
  currentTick: number;
}

export class MarioGame {
  static readonly MAX_TIME = 40;
  static readonly GRACE_TIME = 10;
  static readonly WIDTH = 256;
  static readonly HEIGHT = 256;
  static readonly TILE_WIDTH = MarioGame.WIDTH / 16;
  static readonly TILE_HEIGHT = MarioGame.HEIGHT / 16;

  private world: MarioWorld | null = null;
  private killEvents: MarioEvent[] | null = null;
  private animationFrameId: number | null = null;
  private isRunning: boolean = false;
  private lastTime: number = 0;
  private fps: number = 30;
  private onFinish: ((result: MarioResult) => void) | null = null;

  constructor(killEvents: MarioEvent[] | null = null) {
    this.killEvents = killEvents;
  }

  /**
   * Start game with given level
   */
  async playGame(
    level: string,
    timer: number,
    marioState: number = 0,
    fps: number = 30,
    getActions: () => boolean[],
    onUpdate?: (world: MarioWorld) => void,
    levelId: string = ''  // Stage 5: Track which level is being played
  ): Promise<MarioResult> {
    return new Promise((resolve) => {
      this.fps = fps;
      this.onFinish = resolve;

      this.world = new MarioWorld(this.killEvents);
      this.world.visuals = true;
      this.world.initializeLevel(level, 1000 * timer, levelId);

      // Set Mario's initial state
      this.world.mario.isLarge = marioState > 0;
      this.world.mario.isFire = marioState > 1;
      this.world.update(new Array(numberOfActions()).fill(false));

      this.lastTime = performance.now();
      this.isRunning = true;

      const gameLoop = (currentTime: number) => {
        if (!this.isRunning || !this.world) {
          return;
        }

        const deltaTime = currentTime - this.lastTime;
        const targetDelta = 1000 / this.fps;

        if (deltaTime >= targetDelta) {
          this.lastTime = currentTime - (deltaTime % targetDelta);

          // Get actions from input
          const actions = getActions();

          // Update world
          this.world.update(actions);

          // Call update callback
          if (onUpdate) {
            onUpdate(this.world);
          }

          // Check if game is finished
          if (this.world.gameStatus !== GameStatus.RUNNING) {
            this.stopGame();
            if (this.onFinish) {
              this.onFinish({
                world: this.world,
                gameEvents: [], // Would collect events during game
                gameStatus: this.world.gameStatus,
                currentTick: this.world.currentTick,
              });
            }
            return;
          }
        }

        this.animationFrameId = requestAnimationFrame(gameLoop);
      };

      this.animationFrameId = requestAnimationFrame(gameLoop);
    });
  }

  /**
   * Stop the current game
   */
  stopGame(): void {
    this.isRunning = false;
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }

  /**
   * Get current world state (for telemetry even if game not finished)
   */
  getWorld(): MarioWorld | null {
    return this.world;
  }

  /**
   * Check if game is currently running
   */
  isGameRunning(): boolean {
    return this.isRunning;
  }
}

