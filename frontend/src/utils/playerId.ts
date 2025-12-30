/**
 * Stage 5: Anonymous persistent player ID management
 * 
 * Uses localStorage with cookie fallback for persistence across sessions.
 * Player can clear ID by deleting localStorage/cookies (privacy-respecting).
 */

const STORAGE_KEY = 'pcg_arena_player_id';
const COOKIE_NAME = 'pcg_arena_player_id';
const COOKIE_DAYS = 365; // 1 year expiry

/**
 * Get a cookie value by name
 */
function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

/**
 * Set a cookie with given name, value, and expiry days
 */
function setCookie(name: string, value: string, days: number): void {
  const expires = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toUTCString();
  document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
}

/**
 * Get or create a persistent anonymous player ID
 * 
 * @returns Player ID in format 'anon_<uuid>' for anonymous players
 */
export function getOrCreatePlayerId(): string {
  // Try localStorage first (most reliable for SPAs)
  try {
    let playerId = localStorage.getItem(STORAGE_KEY);
    
    if (!playerId) {
      // Fallback to cookie
      playerId = getCookie(COOKIE_NAME);
    }
    
    if (!playerId) {
      // Generate new ID with 'anon_' prefix to distinguish from authenticated users
      playerId = `anon_${crypto.randomUUID()}`;
    }
    
    // Store in both localStorage and cookie for redundancy
    localStorage.setItem(STORAGE_KEY, playerId);
    setCookie(COOKIE_NAME, playerId, COOKIE_DAYS);
    
    return playerId;
  } catch (e) {
    // If localStorage is unavailable, try cookie only
    let playerId = getCookie(COOKIE_NAME);
    
    if (!playerId) {
      playerId = `anon_${crypto.randomUUID()}`;
      setCookie(COOKIE_NAME, playerId, COOKIE_DAYS);
    }
    
    return playerId;
  }
}

/**
 * Check if player has a linked authenticated account
 */
export function isAnonymousPlayer(playerId: string): boolean {
  return playerId.startsWith('anon_');
}

/**
 * Clear the stored player ID (for privacy/testing)
 */
export function clearPlayerId(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (e) {
    // Ignore localStorage errors
  }
  // Clear cookie by setting expired date
  document.cookie = `${COOKIE_NAME}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
}

