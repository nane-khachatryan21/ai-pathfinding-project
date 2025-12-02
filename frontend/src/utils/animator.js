/**
 * Animation engine for step-by-step pathfinding visualization.
 * Uses requestAnimationFrame for smooth animation.
 */

class Animator {
  constructor() {
    this.animationFrameId = null;
    this.isRunning = false;
    this.lastTimestamp = 0;
    this.callback = null;
    this.speed = 1;
    this.baseInterval = 100; // Base interval in ms (10 steps per second)
  }

  /**
   * Start the animation loop
   * @param {Function} callback - Function to call on each frame
   * @param {number} speed - Animation speed multiplier (1x to 100x)
   */
  start(callback, speed = 1) {
    if (this.isRunning) return;

    this.callback = callback;
    this.speed = speed;
    this.isRunning = true;
    this.lastTimestamp = performance.now();
    this.animationFrameId = requestAnimationFrame(this.animate.bind(this));
  }

  /**
   * Stop the animation loop
   */
  stop() {
    this.isRunning = false;
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }

  /**
   * Update animation speed
   * @param {number} speed - New speed multiplier
   */
  setSpeed(speed) {
    this.speed = speed;
  }

  /**
   * Main animation loop
   * @param {number} timestamp - Current timestamp from requestAnimationFrame
   */
  animate(timestamp) {
    if (!this.isRunning) return;

    const elapsed = timestamp - this.lastTimestamp;
    const interval = this.baseInterval / this.speed;

    // Only call callback if enough time has passed
    if (elapsed >= interval) {
      if (this.callback) {
        const shouldContinue = this.callback();
        
        // Stop if callback returns false
        if (!shouldContinue) {
          this.stop();
          return;
        }
      }
      this.lastTimestamp = timestamp;
    }

    // Continue animation loop
    this.animationFrameId = requestAnimationFrame(this.animate.bind(this));
  }

  /**
   * Check if animation is currently running
   */
  isActive() {
    return this.isRunning;
  }
}

// Create singleton instance
const animator = new Animator();

export default animator;

