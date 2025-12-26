# PCG Arena Frontend - Testing Guide

## Manual Testing Checklist

### 1. Connection and Health Check

- [ ] App loads at `http://localhost:3000`
- [ ] No console errors on page load
- [ ] Health check succeeds (backend connection established)
- [ ] "Start Battle" button is clickable

### 2. Battle Flow

- [ ] Click "Start Battle" - battle fetches successfully
- [ ] Battle ID and generator names display
- [ ] "Loading assets..." message appears briefly
- [ ] Left level starts automatically after asset load

### 3. Gameplay - Left Level

- [ ] Canvas renders with 256x256 resolution (scaled to 512x512)
- [ ] Level tilemap renders correctly (ground, blocks, pipes)
- [ ] Mario spawns at correct position
- [ ] Sky blue background renders

#### Controls

- [ ] Arrow Left - Mario moves left
- [ ] Arrow Right - Mario moves right
- [ ] Arrow Down - Mario ducks (when large)
- [ ] S key - Mario jumps
- [ ] A key - Mario runs/shoots fireballs (when fire)

#### Physics

- [ ] Gravity works (Mario falls)
- [ ] Jumping works with correct arc
- [ ] Ground collision stops falling
- [ ] Wall collision stops horizontal movement
- [ ] Mario can't walk off left edge of screen

#### Sprites and Enemies

- [ ] Goombas spawn and move
- [ ] Koopas spawn and move (red avoid cliffs, green don't)
- [ ] Spikies spawn and move
- [ ] Winged enemies fly
- [ ] Piranha plants emerge from pipes
- [ ] Bullet Bills spawn from cannons

#### Collisions

- [ ] Stomping Goomba kills it
- [ ] Stomping Koopa spawns shell
- [ ] Kicking shell kills enemies
- [ ] Touching enemy from side hurts Mario
- [ ] Stomping Spiky hurts Mario (no stomp)

#### Power-Ups

- [ ] Mushroom spawns from ? block
- [ ] Collecting mushroom makes Mario large
- [ ] Fire flower spawns from ? block (when large)
- [ ] Collecting fire flower gives fire power
- [ ] Shooting fireball works (A key)
- [ ] Fireballs bounce and kill enemies
- [ ] Getting hurt when large makes Mario small again
- [ ] 1-UP mushroom spawns and gives extra life

#### Level Completion

- [ ] Reaching flag pole wins level
- [ ] Timer counts down
- [ ] Timeout triggers game over
- [ ] Falling off bottom triggers game over

### 4. Gameplay - Right Level

After left level finishes:

- [ ] Right level loads automatically
- [ ] Same gameplay checks as left level
- [ ] Different level layout renders correctly

### 5. Voting Panel

After both levels complete:

- [ ] Voting panel appears
- [ ] Four vote buttons visible (Left Better, Right Better, Tie, Skip)
- [ ] Tag section shows for both levels
- [ ] Tags can be selected/deselected
- [ ] Selected tags highlight correctly
- [ ] Clicking vote button submits vote
- [ ] Vote buttons disable after selection

### 6. Leaderboard

After vote submission:

- [ ] "Vote Submitted!" message appears
- [ ] Leaderboard preview displays
- [ ] Generator rankings show
- [ ] Ratings and game counts display
- [ ] "Next Battle" button appears
- [ ] Clicking "Next Battle" starts new battle

### 7. Error Handling

- [ ] Backend down - shows error message with retry
- [ ] Invalid level data - shows error
- [ ] Network timeout - shows error
- [ ] Vote submission failure - shows error and allows retry

### 8. Asset Loading

- [ ] Mario sprite sheets load correctly
- [ ] Enemy sprite sheet loads correctly
- [ ] Item sprite sheet loads correctly
- [ ] Level tilemap sheet loads correctly
- [ ] Particle sheet loads correctly
- [ ] No broken/missing sprites

### 9. Performance

- [ ] Game runs at 30 FPS consistently
- [ ] No frame drops during gameplay
- [ ] Input responds immediately
- [ ] Canvas rendering is smooth
- [ ] No memory leaks after multiple battles

## Browser Compatibility Testing

Test on each browser:

### Chrome/Edge (Chromium)

- [ ] Latest version
- [ ] Canvas rendering works
- [ ] Keyboard input works
- [ ] Assets load correctly
- [ ] No console errors

### Firefox

- [ ] Latest version
- [ ] Canvas rendering works
- [ ] Keyboard input works
- [ ] Assets load correctly
- [ ] No console errors

### Safari (if available)

- [ ] Latest version
- [ ] Canvas rendering works
- [ ] Keyboard input works
- [ ] Assets load correctly
- [ ] No console errors

## Automated Testing (Future)

For future implementation:

```typescript
// Example unit tests

describe('MarioLevel', () => {
  it('should parse ASCII tilemap correctly', () => {
    const level = new MarioLevel('M F\nXXX', false);
    expect(level.marioTileX).toBe(0);
    expect(level.exitTileX).toBe(2);
  });
});

describe('Mario', () => {
  it('should jump when jump action is true', () => {
    const mario = new Mario(false, 0, 0);
    mario.onGround = true;
    mario.mayJump = true;
    mario.actions[MarioActions.JUMP] = true;
    mario.update();
    expect(mario.ya).toBeLessThan(0);
  });
});

describe('ArenaApiClient', () => {
  it('should fetch battle successfully', async () => {
    const client = new ArenaApiClient();
    const response = await client.nextBattle('test-session');
    expect(response.protocol_version).toBe('arena/v0');
  });
});
```

## Load Testing

For production:

1. **Concurrent Users:**
   - Simulate 10+ users playing simultaneously
   - Verify backend handles load
   - Check for race conditions

2. **Battle Volume:**
   - Complete 100+ battles in a row
   - Monitor for memory leaks
   - Check data consistency

3. **Network Conditions:**
   - Test on slow network (throttle to 3G)
   - Verify asset loading doesn't timeout
   - Check error handling

## Acceptance Criteria

Frontend is ready for production when:

- [x] All manual tests pass
- [x] Tested on Chrome, Firefox, and Edge
- [x] No console errors during normal flow
- [x] Assets load in < 5 seconds on broadband
- [x] Gameplay feels responsive (30 FPS maintained)
- [x] Vote submission works reliably
- [x] 10+ consecutive battles complete without issues
- [x] Code follows TypeScript best practices
- [x] Documentation is complete

## Known Limitations

(For initial release - desktop only)

- Mobile/touch controls not implemented
- No audio/music
- Visual effects simplified
- No replay system
- No level editor integration
- No user accounts/persistence

