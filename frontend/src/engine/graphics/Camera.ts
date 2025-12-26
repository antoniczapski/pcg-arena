/**
 * Camera for game viewport
 */

export class Camera {
  x: number = 0;
  y: number = 0;
  width: number = 256;
  height: number = 256;

  constructor(width: number = 256, height: number = 256) {
    this.width = width;
    this.height = height;
  }

  /**
   * Update camera position to follow target
   */
  follow(targetX: number, targetY: number, levelWidth: number, levelHeight: number): void {
    // Center on target
    this.x = targetX - this.width / 2;
    this.y = targetY - this.height / 2;

    // Clamp to level bounds
    if (this.x + this.width > levelWidth) {
      this.x = levelWidth - this.width;
    }
    if (this.x < 0) {
      this.x = 0;
    }

    if (this.y + this.height > levelHeight) {
      this.y = levelHeight - this.height;
    }
    if (this.y < 0) {
      this.y = 0;
    }
  }

  /**
   * Convert world coordinates to screen coordinates
   */
  worldToScreen(worldX: number, worldY: number): { x: number; y: number } {
    return {
      x: worldX - this.x,
      y: worldY - this.y,
    };
  }

  /**
   * Convert screen coordinates to world coordinates
   */
  screenToWorld(screenX: number, screenY: number): { x: number; y: number } {
    return {
      x: screenX + this.x,
      y: screenY + this.y,
    };
  }

  /**
   * Check if a point is visible in the camera
   */
  isVisible(worldX: number, worldY: number, margin: number = 0): boolean {
    return (
      worldX >= this.x - margin &&
      worldX <= this.x + this.width + margin &&
      worldY >= this.y - margin &&
      worldY <= this.y + this.height + margin
    );
  }
}

