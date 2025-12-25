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
    TOP = "TOP"
    BOTTOM = "BOTTOM"
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


class PlayOrder(str, Enum):
    """Battle presentation play order."""
    TOP_THEN_BOTTOM = "TOP_THEN_BOTTOM"


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


class SideTelemetry(BaseModel):
    """Telemetry data for one side of a battle."""
    played: bool = Field(..., description="Whether the level was played")
    duration_seconds: Optional[float] = Field(default=None, description="Time spent playing (seconds)")
    completed: Optional[bool] = Field(default=None, description="Whether the level was completed")
    coins_collected: Optional[int] = Field(default=None, description="Number of coins collected")


class Telemetry(BaseModel):
    """Telemetry data for both sides of a battle."""
    top: Optional[SideTelemetry] = Field(default=None, description="Telemetry for top level")
    bottom: Optional[SideTelemetry] = Field(default=None, description="Telemetry for bottom level")


class VoteRequest(BaseModel):
    """Request model for POST /v1/votes"""
    client_version: str = Field(..., description="Client version string")
    session_id: str = Field(..., description="Client-generated UUID matching the battle session")
    battle_id: str = Field(..., description="Battle ID from the battle response")
    result: VoteResult = Field(..., description="Vote outcome: TOP, BOTTOM, TIE, or SKIP")
    top_tags: Optional[List[str]] = Field(default=None, description="Optional tags describing the top level")
    bottom_tags: Optional[List[str]] = Field(default=None, description="Optional tags describing the bottom level")
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
    top: BattleSide = Field(..., description="Top level and generator")
    bottom: BattleSide = Field(..., description="Bottom level and generator")


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
    generators: List[LeaderboardGeneratorPreview] = Field(..., description="Top generators (may be partial list)")


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

