/**
 * Keyboard input handler
 * Maps keyboard inputs to Mario actions
 */

import { MarioActions, createActionArray } from '../MarioActions';

// Keys used by the game that should have default behavior prevented
const GAME_KEYS = new Set([
  'ArrowLeft',
  'ArrowRight',
  'ArrowUp',
  'ArrowDown',
  'KeyS',
  'KeyA',
  'Space',
]);

export class KeyboardInput {
  private keys: Set<string> = new Set();
  private actions: boolean[] = createActionArray();
  private cleanupFns: Array<() => void> = [];
  private isActive: boolean = true;

  constructor() {
    this.setupEventListeners();
    console.log('[KeyboardInput] Created and listening');
  }

  private setupEventListeners(): void {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!this.isActive) return;
      
      // Prevent default for game keys (stops arrow keys from scrolling)
      if (GAME_KEYS.has(e.code)) {
        e.preventDefault();
      }
      
      this.keys.add(e.code);
      this.updateActions();
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      if (!this.isActive) return;
      
      if (GAME_KEYS.has(e.code)) {
        e.preventDefault();
      }
      
      this.keys.delete(e.code);
      this.updateActions();
    };

    // Use capture phase to get events before they bubble
    window.addEventListener('keydown', handleKeyDown, { capture: true });
    window.addEventListener('keyup', handleKeyUp, { capture: true });

    // Store cleanup function
    this.cleanupFns.push(() => {
      window.removeEventListener('keydown', handleKeyDown, { capture: true });
      window.removeEventListener('keyup', handleKeyUp, { capture: true });
    });
  }

  private updateActions(): void {
    // Arrow keys for movement
    this.actions[MarioActions.LEFT] = this.keys.has('ArrowLeft');
    this.actions[MarioActions.RIGHT] = this.keys.has('ArrowRight');
    this.actions[MarioActions.DOWN] = this.keys.has('ArrowDown');

    // S for jump (also support Space and ArrowUp as alternatives)
    this.actions[MarioActions.JUMP] = 
      this.keys.has('KeyS') || 
      this.keys.has('Space') || 
      this.keys.has('ArrowUp');

    // A for run/fire (also support Shift as alternative)
    this.actions[MarioActions.SPEED] = 
      this.keys.has('KeyA') || 
      this.keys.has('ShiftLeft') || 
      this.keys.has('ShiftRight');
  }

  /**
   * Get current action state
   */
  getActions(): boolean[] {
    return [...this.actions];
  }

  /**
   * Reset all inputs
   */
  reset(): void {
    this.keys.clear();
    this.actions = createActionArray();
  }

  /**
   * Check if a specific key is pressed
   */
  isKeyPressed(code: string): boolean {
    return this.keys.has(code);
  }

  /**
   * Cleanup event listeners
   */
  destroy(): void {
    console.log('[KeyboardInput] Destroying');
    this.isActive = false;
    this.cleanupFns.forEach((cleanup) => cleanup());
    this.cleanupFns = [];
    this.keys.clear();
  }
}
