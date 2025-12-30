/**
 * Arena API Client for browser
 * Ported from client-java/src/main/java/arena/api/ArenaApiClient.java
 */

import {
  PROTOCOL_VERSION,
  CLIENT_VERSION,
  ArenaApiException,
  type HealthResponse,
  type BattleRequest,
  type BattleResponse,
  type VoteRequest,
  type VoteResponse,
  type LeaderboardResponse,
  type GeneratorDetailsResponse,
  type ErrorResponse,
  type PlatformStatsResponse,
  type GeneratorStatsResponse,
  type LevelStatsResponse,
  type LevelHeatmapResponse,
} from './types';

export class ArenaApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = '') {
    // Empty string means use relative URLs (goes through Vite proxy in dev)
    this.baseUrl = baseUrl;
  }

  /**
   * Health check - verifies backend is reachable and protocol matches
   */
  async health(): Promise<HealthResponse> {
    try {
      console.log('[API] GET /health');
      
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });

      console.log(`[API] Response status: ${response.status}`);

      if (!response.ok) {
        throw new ArenaApiException(
          'HEALTH_CHECK_FAILED',
          `Health check failed with status ${response.status}`,
          true
        );
      }

      const data: HealthResponse = await response.json();
      this.verifyProtocol(data.protocol_version);
      
      return data;
    } catch (error) {
      if (error instanceof ArenaApiException) {
        throw error;
      }
      console.error('[API] Health check failed:', error);
      throw new ArenaApiException(
        'BACKEND_UNREACHABLE',
        `Backend unreachable: ${error instanceof Error ? error.message : String(error)}`,
        true
      );
    }
  }

  /**
   * Request next battle
   */
  async nextBattle(sessionId: string, playerId?: string): Promise<BattleResponse> {
    const request: BattleRequest = {
      client_version: CLIENT_VERSION,
      session_id: sessionId,
      player_id: playerId || null,  // Stage 5: Include player ID if provided
      preferences: {
        mode: 'standard',
      },
    };

    const path = '/v1/battles:next';

    try {
      console.log('[API] POST', path);
      const responseBody = await this.sendJson('POST', path, JSON.stringify(request));

      // Check if it's an error response
      if (responseBody.includes('"error"')) {
        const errorResponse: ErrorResponse = JSON.parse(responseBody);
        this.verifyProtocol(errorResponse.protocol_version);
        throw this.createException(errorResponse);
      }

      const battleResponse: BattleResponse = JSON.parse(responseBody);
      this.verifyProtocol(battleResponse.protocol_version);

      console.log('[API] Battle received:', battleResponse.battle.battle_id);
      return battleResponse;
    } catch (error) {
      if (error instanceof ArenaApiException) {
        throw error;
      }
      console.error('[API] Failed to fetch battle:', error);
      throw new ArenaApiException(
        'FETCH_BATTLE_FAILED',
        `Failed to fetch battle: ${error instanceof Error ? error.message : String(error)}`,
        true
      );
    }
  }

  /**
   * Submit a vote
   */
  async submitVote(
    sessionId: string,
    battleId: string,
    result: 'LEFT' | 'RIGHT' | 'TIE' | 'SKIP',
    leftTags: string[],
    rightTags: string[],
    telemetry: VoteRequest['telemetry'],
    playerId?: string  // Stage 5: Persistent player ID
  ): Promise<VoteResponse> {
    const request: VoteRequest = {
      client_version: CLIENT_VERSION,
      session_id: sessionId,
      player_id: playerId,  // Stage 5: Include player ID
      battle_id: battleId,
      result,
      left_tags: leftTags,
      right_tags: rightTags,
      telemetry,
    };

    const path = '/v1/votes';

    try {
      console.log('[API] POST', path);
      const responseBody = await this.sendJson('POST', path, JSON.stringify(request));

      // Check if it's an error response
      if (responseBody.includes('"error"')) {
        const errorResponse: ErrorResponse = JSON.parse(responseBody);
        this.verifyProtocol(errorResponse.protocol_version);
        throw this.createException(errorResponse);
      }

      const voteResponse: VoteResponse = JSON.parse(responseBody);
      this.verifyProtocol(voteResponse.protocol_version);

      console.log('[API] Vote accepted:', voteResponse.vote_id);
      return voteResponse;
    } catch (error) {
      if (error instanceof ArenaApiException) {
        throw error;
      }
      console.error('[API] Failed to submit vote:', error);
      throw new ArenaApiException(
        'SUBMIT_VOTE_FAILED',
        `Failed to submit vote: ${error instanceof Error ? error.message : String(error)}`,
        true
      );
    }
  }

  /**
   * Fetch leaderboard
   */
  async leaderboard(): Promise<LeaderboardResponse> {
    const path = '/v1/leaderboard';

    try {
      console.log('[API] GET', path);

      const response = await fetch(`${this.baseUrl}${path}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });

      console.log(`[API] Response status: ${response.status}`);

      if (!response.ok) {
        throw new ArenaApiException(
          'LEADERBOARD_FETCH_FAILED',
          `Leaderboard request failed with status ${response.status}`,
          true
        );
      }

      const data: LeaderboardResponse = await response.json();
      this.verifyProtocol(data.protocol_version);

      return data;
    } catch (error) {
      if (error instanceof ArenaApiException) {
        throw error;
      }
      console.error('[API] Failed to fetch leaderboard:', error);
      throw new ArenaApiException(
        'LEADERBOARD_FETCH_FAILED',
        `Failed to fetch leaderboard: ${error instanceof Error ? error.message : String(error)}`,
        true
      );
    }
  }

  /**
   * Fetch generator details with all levels
   */
  async getGenerator(generatorId: string): Promise<GeneratorDetailsResponse> {
    const path = `/v1/generators/${encodeURIComponent(generatorId)}`;

    try {
      console.log('[API] GET', path);

      const response = await fetch(`${this.baseUrl}${path}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });

      console.log(`[API] Response status: ${response.status}`);

      if (!response.ok) {
        const errorBody = await response.text();
        if (errorBody) {
          try {
            const errorResponse: ErrorResponse = JSON.parse(errorBody);
            throw this.createException(errorResponse);
          } catch (parseError) {
            // Not JSON, throw generic error
          }
        }
        throw new ArenaApiException(
          'GENERATOR_FETCH_FAILED',
          `Generator request failed with status ${response.status}`,
          response.status >= 500
        );
      }

      const data: GeneratorDetailsResponse = await response.json();
      this.verifyProtocol(data.protocol_version);

      console.log('[API] Generator received:', data.generator.generator_id, 'with', data.levels.length, 'levels');
      return data;
    } catch (error) {
      if (error instanceof ArenaApiException) {
        throw error;
      }
      console.error('[API] Failed to fetch generator:', error);
      throw new ArenaApiException(
        'GENERATOR_FETCH_FAILED',
        `Failed to fetch generator: ${error instanceof Error ? error.message : String(error)}`,
        true
      );
    }
  }

  // =============================================================================
  // Stage 5: Statistics API Methods
  // =============================================================================

  /**
   * Fetch platform-wide statistics
   */
  async getPlatformStats(): Promise<PlatformStatsResponse> {
    const path = '/v1/stats/platform';

    try {
      console.log('[API] GET', path);

      const response = await fetch(`${this.baseUrl}${path}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new ArenaApiException(
          'STATS_FETCH_FAILED',
          `Stats request failed with status ${response.status}`,
          true
        );
      }

      const data: PlatformStatsResponse = await response.json();
      this.verifyProtocol(data.protocol_version);
      return data;
    } catch (error) {
      if (error instanceof ArenaApiException) {
        throw error;
      }
      console.error('[API] Failed to fetch platform stats:', error);
      throw new ArenaApiException(
        'STATS_FETCH_FAILED',
        `Failed to fetch platform stats: ${error instanceof Error ? error.message : String(error)}`,
        true
      );
    }
  }

  /**
   * Fetch generator statistics
   */
  async getGeneratorStats(generatorId: string): Promise<GeneratorStatsResponse> {
    const path = `/v1/stats/generators/${encodeURIComponent(generatorId)}`;

    try {
      console.log('[API] GET', path);

      const response = await fetch(`${this.baseUrl}${path}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new ArenaApiException(
          'GENERATOR_STATS_FETCH_FAILED',
          `Generator stats request failed with status ${response.status}`,
          response.status >= 500
        );
      }

      const data: GeneratorStatsResponse = await response.json();
      this.verifyProtocol(data.protocol_version);
      return data;
    } catch (error) {
      if (error instanceof ArenaApiException) {
        throw error;
      }
      console.error('[API] Failed to fetch generator stats:', error);
      throw new ArenaApiException(
        'GENERATOR_STATS_FETCH_FAILED',
        `Failed to fetch generator stats: ${error instanceof Error ? error.message : String(error)}`,
        true
      );
    }
  }

  /**
   * Fetch level statistics
   */
  async getLevelStats(levelId: string): Promise<LevelStatsResponse> {
    const path = `/v1/stats/levels/${encodeURIComponent(levelId)}`;

    try {
      console.log('[API] GET', path);

      const response = await fetch(`${this.baseUrl}${path}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new ArenaApiException(
          'LEVEL_STATS_FETCH_FAILED',
          `Level stats request failed with status ${response.status}`,
          response.status >= 500
        );
      }

      const data: LevelStatsResponse = await response.json();
      this.verifyProtocol(data.protocol_version);
      return data;
    } catch (error) {
      if (error instanceof ArenaApiException) {
        throw error;
      }
      console.error('[API] Failed to fetch level stats:', error);
      throw new ArenaApiException(
        'LEVEL_STATS_FETCH_FAILED',
        `Failed to fetch level stats: ${error instanceof Error ? error.message : String(error)}`,
        true
      );
    }
  }

  /**
   * Fetch level heatmap data
   */
  async getLevelHeatmap(levelId: string): Promise<LevelHeatmapResponse> {
    const path = `/v1/stats/levels/${encodeURIComponent(levelId)}/heatmap`;

    try {
      console.log('[API] GET', path);

      const response = await fetch(`${this.baseUrl}${path}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new ArenaApiException(
          'HEATMAP_FETCH_FAILED',
          `Heatmap request failed with status ${response.status}`,
          response.status >= 500
        );
      }

      const data: LevelHeatmapResponse = await response.json();
      this.verifyProtocol(data.protocol_version);
      return data;
    } catch (error) {
      if (error instanceof ArenaApiException) {
        throw error;
      }
      console.error('[API] Failed to fetch heatmap:', error);
      throw new ArenaApiException(
        'HEATMAP_FETCH_FAILED',
        `Failed to fetch heatmap: ${error instanceof Error ? error.message : String(error)}`,
        true
      );
    }
  }

  /**
   * Send a JSON request and return the response body
   */
  private async sendJson(method: string, path: string, jsonBody: string): Promise<string> {
    const fullUrl = `${this.baseUrl}${path}`;
    console.log(`[API] Sending ${method} request to:`, fullUrl);

    const response = await fetch(fullUrl, {
      method,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json',
      },
      body: jsonBody,
    });

    console.log(`[API] Response status: ${response.status}`);

    const responseBody = await response.text();

    if (!response.ok && responseBody) {
      return responseBody; // Return error response for parsing
    }

    if (!response.ok) {
      throw new ArenaApiException(
        'HTTP_ERROR',
        `HTTP ${response.status}`,
        response.status >= 500
      );
    }

    return responseBody;
  }

  /**
   * Verify protocol version matches expected
   */
  private verifyProtocol(protocolVersion: string): void {
    if (protocolVersion !== PROTOCOL_VERSION) {
      throw new ArenaApiException(
        'PROTOCOL_MISMATCH',
        `Incompatible backend protocol: expected ${PROTOCOL_VERSION}, got ${protocolVersion}`,
        false
      );
    }
  }

  /**
   * Create exception from error response
   */
  private createException(errorResponse: ErrorResponse): ArenaApiException {
    const error = errorResponse.error;
    console.error('[API] Error:', error.code, error.message);
    return new ArenaApiException(error.code, error.message, error.retryable, error.details);
  }
}

