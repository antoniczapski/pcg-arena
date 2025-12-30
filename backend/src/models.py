"""
PCG Arena Backend - Pydantic Models
Protocol: arena/v0

Defines request/response models for battles and votes endpoints.
All models match the Stage 0 API specification.
"""

from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


# Protocol version constant
PROTOCOL_VERSION = "arena/v0"


# Enums
class VoteResult(str, Enum):
    """Vote result enum."""
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    TIE = "TIE"
    SKIP = "SKIP"


class ErrorCode(str, Enum):
    """API error codes."""
    NO_BATTLE_AVAILABLE = "NO_BATTLE_AVAILABLE"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"
    INVALID_TAG = "INVALID_TAG"
    BATTLE_NOT_FOUND = "BATTLE_NOT_FOUND"
    BATTLE_ALREADY_VOTED = "BATTLE_ALREADY_VOTED"
    DUPLICATE_VOTE_CONFLICT = "DUPLICATE_VOTE_CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    UNSUPPORTED_CLIENT_VERSION = "UNSUPPORTED_CLIENT_VERSION"
    # Stage 5: Additional error codes
    GENERATOR_NOT_FOUND = "GENERATOR_NOT_FOUND"
    LEVEL_NOT_FOUND = "LEVEL_NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"


class PlayOrder(str, Enum):
    """Battle presentation play order."""
    LEFT_THEN_RIGHT = "LEFT_THEN_RIGHT"


class LevelFormatType(str, Enum):
    """Level format type."""
    ASCII_TILEMAP = "ASCII_TILEMAP"


class Encoding(str, Enum):
    """Level payload encoding."""
    UTF8 = "utf-8"


# Request Models
class BattlePreferences(BaseModel):
    """Battle request preferences (reserved for future use)."""
    mode: Optional[str] = Field(default="standard", description="Reserved for future use")


class BattleRequest(BaseModel):
    """Request model for POST /v1/battles:next"""
    client_version: str = Field(..., description="Client version string")
    session_id: str = Field(..., description="Client-generated UUID for session tracking")
    player_id: Optional[str] = Field(default=None, description="Reserved for future use, null for Stage 0")
    preferences: Optional[BattlePreferences] = Field(default_factory=BattlePreferences, description="Optional preferences")


class TrajectoryPoint(BaseModel):
    """Stage 5: Position sample for trajectory tracking."""
    tick: int
    x: int
    y: int
    state: int  # 0=small, 1=large, 2=fire


class DeathLocation(BaseModel):
    """Stage 5: Death location with cause."""
    x: float
    y: float
    tick: int
    cause: str  # 'enemy', 'fall', 'timeout'


class SerializedEvent(BaseModel):
    """Stage 5: Serialized game event."""
    type: str
    param: int
    x: int
    y: int
    tick: int


class SideTelemetry(BaseModel):
    """Telemetry data for one side of a battle."""
    played: bool = Field(..., description="Whether the level was played")
    duration_seconds: Optional[float] = Field(default=None, description="Time spent playing (seconds)")
    completed: Optional[bool] = Field(default=None, description="Whether the level was completed")
    coins_collected: Optional[int] = Field(default=None, description="Number of coins collected")
    deaths: Optional[int] = Field(default=None, description="Number of deaths")
    powerups_collected: Optional[int] = Field(default=None, description="Number of powerups collected")
    enemies_killed: Optional[int] = Field(default=None, description="Number of enemies killed")
    
    # Stage 5: Enhanced telemetry fields
    level_id: Optional[str] = Field(default=None, description="Level ID")
    jumps: Optional[int] = Field(default=None, description="Number of jumps")
    enemies_stomped: Optional[int] = Field(default=None, description="Enemies killed by stomping")
    enemies_fire_killed: Optional[int] = Field(default=None, description="Enemies killed by fire")
    enemies_shell_killed: Optional[int] = Field(default=None, description="Enemies killed by shell")
    powerups_mushroom: Optional[int] = Field(default=None, description="Mushrooms collected")
    powerups_flower: Optional[int] = Field(default=None, description="Fire flowers collected")
    lives_collected: Optional[int] = Field(default=None, description="1-ups collected")
    trajectory: Optional[List[TrajectoryPoint]] = Field(default=None, description="Position samples")
    death_locations: Optional[List[DeathLocation]] = Field(default=None, description="Death locations")
    events: Optional[List[SerializedEvent]] = Field(default=None, description="Game events")


class Telemetry(BaseModel):
    """Telemetry data for both sides of a battle."""
    left: Optional[SideTelemetry] = Field(default=None, description="Telemetry for left level")
    right: Optional[SideTelemetry] = Field(default=None, description="Telemetry for right level")


class VoteRequest(BaseModel):
    """Request model for POST /v1/votes"""
    client_version: str = Field(..., description="Client version string")
    session_id: str = Field(..., description="Client-generated UUID matching the battle session")
    player_id: Optional[str] = Field(default=None, description="Persistent player ID (Stage 5)")
    battle_id: str = Field(..., description="Battle ID from the battle response")
    result: VoteResult = Field(..., description="Vote outcome: LEFT, RIGHT, TIE, or SKIP")
    left_tags: Optional[List[str]] = Field(default=None, description="Optional tags describing the left level")
    right_tags: Optional[List[str]] = Field(default=None, description="Optional tags describing the right level")
    telemetry: Optional[Telemetry] = Field(default=None, description="Optional gameplay telemetry")


# Response Models - Nested structures
class GeneratorInfo(BaseModel):
    """Generator metadata included in battle responses."""
    generator_id: str = Field(..., description="Generator identifier")
    name: str = Field(..., description="Display name")
    version: str = Field(..., description="Version string")
    documentation_url: Optional[str] = Field(default=None, description="URL to generator documentation")


class LevelFormat(BaseModel):
    """Level format metadata."""
    type: LevelFormatType = Field(..., description="Format type (ASCII_TILEMAP for Stage 0)")
    width: int = Field(..., description="Level width in characters", ge=1, le=250)
    height: int = Field(..., description="Level height in lines (must be 16)", ge=16, le=16)
    newline: str = Field(default="\n", description="Newline character used")


class LevelPayload(BaseModel):
    """Level content payload."""
    encoding: Encoding = Field(default=Encoding.UTF8, description="Text encoding")
    tilemap: str = Field(..., description="Full ASCII tilemap content (16 lines)")


class LevelMetadata(BaseModel):
    """Level metadata."""
    seed: Optional[int] = Field(default=None, description="Optional random seed")
    controls: Dict[str, Any] = Field(default_factory=dict, description="Optional control parameters")


class BattleSide(BaseModel):
    """One side of a battle (level + generator bundle)."""
    level_id: str = Field(..., description="Level identifier")
    generator: GeneratorInfo = Field(..., description="Generator information")
    format: LevelFormat = Field(..., description="Level format metadata")
    level_payload: LevelPayload = Field(..., description="Level content")
    content_hash: str = Field(..., description="Content hash (e.g., sha256:...)")
    metadata: LevelMetadata = Field(default_factory=LevelMetadata, description="Level metadata")


class BattlePresentation(BaseModel):
    """Battle presentation instructions."""
    play_order: PlayOrder = Field(..., description="Order in which levels should be played")
    reveal_generator_names_after_vote: bool = Field(..., description="Whether to reveal generator names after voting")
    suggested_time_limit_seconds: int = Field(..., description="Suggested time limit for playing both levels")


class Battle(BaseModel):
    """Battle data structure."""
    battle_id: str = Field(..., description="Unique battle identifier")
    issued_at_utc: str = Field(..., description="ISO timestamp when battle was issued")
    expires_at_utc: Optional[str] = Field(default=None, description="ISO timestamp when battle expires (null = no expiry)")
    presentation: BattlePresentation = Field(..., description="Presentation instructions")
    left: BattleSide = Field(..., description="Left level and generator")
    right: BattleSide = Field(..., description="Right level and generator")


class BattleResponse(BaseModel):
    """Response model for POST /v1/battles:next"""
    protocol_version: str = Field(default=PROTOCOL_VERSION, description="Protocol version")
    battle: Battle = Field(..., description="Battle data")


# Vote Response Models
class LeaderboardGeneratorPreview(BaseModel):
    """Generator preview in leaderboard snapshot."""
    generator_id: str = Field(..., description="Generator identifier")
    name: str = Field(..., description="Display name")
    rating: float = Field(..., description="Current rating")
    games_played: int = Field(..., description="Total games played")


class LeaderboardPreview(BaseModel):
    """Leaderboard snapshot included in vote response."""
    updated_at_utc: str = Field(..., description="ISO timestamp of last update")
    generators: List[LeaderboardGeneratorPreview] = Field(..., description="Generators list (may be partial)")


class VoteResponse(BaseModel):
    """Response model for POST /v1/votes"""
    protocol_version: str = Field(default=PROTOCOL_VERSION, description="Protocol version")
    accepted: bool = Field(..., description="Whether vote was accepted")
    vote_id: str = Field(..., description="Unique vote identifier")
    leaderboard_preview: LeaderboardPreview = Field(..., description="Updated leaderboard snapshot")


# Error Response Models
class ErrorInfo(BaseModel):
    """Error information structure."""
    code: str = Field(..., description="Error code enum")
    message: str = Field(..., description="Human-readable error message")
    retryable: bool = Field(default=False, description="Whether the error is retryable")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Optional additional error details")


class ErrorResponse(BaseModel):
    """Standard error response format."""
    protocol_version: str = Field(default=PROTOCOL_VERSION, description="Protocol version")
    error: ErrorInfo = Field(..., description="Error information")
    
    @classmethod
    def create(cls, code: str, message: str, retryable: bool = False, details: Optional[Dict[str, Any]] = None) -> "ErrorResponse":
        """Factory method to create a standardized error response."""
        error_info = ErrorInfo(
            code=code,
            message=message,
            retryable=retryable,
            details=details
        )
        return cls(error=error_info)
