/**
 * Type definitions for PCG Arena API (protocol arena/v0)
 * Ported from client-java/src/main/java/arena/api/models/
 */

export const PROTOCOL_VERSION = 'arena/v0';
export const CLIENT_VERSION = '0.1.0';

// Health Response
export interface BuildInfo {
  git_sha?: string;
  backend_version: string;
}

export interface HealthResponse {
  protocol_version: string;
  status: string;
  server_time_utc: string;
  build: BuildInfo;
}

// Battle Request/Response
export interface BattleRequest {
  client_version: string;
  session_id: string;
  player_id: null;
  preferences: {
    mode: string;
  };
}

export interface GeneratorInfo {
  generator_id: string;
  name: string;
  version: string;
  documentation_url?: string;
}

export interface LevelFormat {
  type: string;
  width: number;
  height: number;
  newline: string;
}

export interface LevelPayload {
  encoding: string;
  tilemap: string;
}

export interface LevelMetadata {
  seed?: number;
  controls: Record<string, unknown>;
}

export interface LevelInfo {
  level_id: string;
  generator: GeneratorInfo;
  format: LevelFormat;
  level_payload: LevelPayload;
  content_hash: string;
  metadata: LevelMetadata;
}

export interface BattlePresentation {
  play_order: string;
  reveal_generator_names_after_vote: boolean;
  suggested_time_limit_seconds: number;
}

export interface Battle {
  battle_id: string;
  issued_at_utc: string;
  expires_at_utc: string | null;
  presentation: BattlePresentation;
  left: LevelInfo;
  right: LevelInfo;
}

export interface BattleResponse {
  protocol_version: string;
  battle: Battle;
}

// Vote Request/Response
export interface LevelTelemetry {
  played: boolean;
  duration_seconds: number;
  completed: boolean;
  deaths: number;
  coins_collected: number;
  powerups_collected?: number;
  enemies_killed?: number;
}

export interface VoteRequest {
  client_version: string;
  session_id: string;
  battle_id: string;
  result: 'LEFT' | 'RIGHT' | 'TIE' | 'SKIP';
  left_tags: string[];
  right_tags: string[];
  telemetry: {
    left: LevelTelemetry;
    right: LevelTelemetry;
  };
}

export interface GeneratorPreview {
  generator_id: string;
  name: string;
  rating: number;
  games_played: number;
}

export interface LeaderboardPreview {
  updated_at_utc: string;
  generators: GeneratorPreview[];
}

export interface VoteResponse {
  protocol_version: string;
  accepted: boolean;
  vote_id: string;
  leaderboard_preview: LeaderboardPreview;
}

// Leaderboard Response
export interface RatingSystem {
  name: string;
  initial_rating: number;
  k_factor: number;
}

export interface GeneratorRanking {
  rank: number;
  generator_id: string;
  name: string;
  documentation_url?: string;
  version: string;
  rating: number;
  games_played: number;
  wins: number;
  losses: number;
  ties: number;
  skips: number;
}

export interface LeaderboardResponse {
  protocol_version: string;
  updated_at_utc: string;
  rating_system: RatingSystem;
  generators: GeneratorRanking[];
}

// Generator Details Response (for generator page)
export interface GeneratorDetails {
  generator_id: string;
  name: string;
  version: string;
  description: string;
  tags: string[];
  documentation_url: string | null;
  is_active: boolean;
  created_at_utc: string;
  updated_at_utc: string;
  rank: number | null;
  rating: number;
  games_played: number;
  wins: number;
  losses: number;
  ties: number;
  skips: number;
  level_count: number;
}

export interface LevelPreviewData {
  level_id: string;
  format: {
    type: string;
    width: number;
    height: number;
  };
  tilemap: string;
  content_hash: string;
  created_at_utc: string;
}

export interface GeneratorDetailsResponse {
  protocol_version: string;
  generator: GeneratorDetails;
  levels: LevelPreviewData[];
}

// Error Response
export interface ErrorInfo {
  code: string;
  message: string;
  retryable: boolean;
  details?: Record<string, unknown>;
}

export interface ErrorResponse {
  protocol_version: string;
  error: ErrorInfo;
}

// API Exception
export class ArenaApiException extends Error {
  constructor(
    public code: string,
    message: string,
    public retryable: boolean = false,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'ArenaApiException';
  }
}

