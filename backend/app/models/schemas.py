"""
Pydantic models for request / response validation.

Mirrors the TypeScript types in frontend/src/types/index.ts.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AssetType(str, Enum):
    CHARACTER = "character"
    ITEM = "item"
    TILE = "tile"
    UI = "ui"


class PixelSize(int, Enum):
    S32 = 32
    S64 = 64
    S128 = 128


class ArtStyle(str, Enum):
    PIXEL_ART = "pixel_art"
    CARTOON = "cartoon"
    DARK_FANTASY = "dark_fantasy"


class EngineType(str, Enum):
    UNITY = "unity"
    GODOT = "godot"
    GENERIC = "generic"


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str = "0.0.1"
    demo_mode: bool


# ---------------------------------------------------------------------------
# Runtime config (frontend-facing provider status)
# ---------------------------------------------------------------------------

class DatabaseInfo(BaseModel):
    provider: str = "sqlite"
    fallback: bool = False
    host: Optional[str] = None
    database: Optional[str] = None
    path: Optional[str] = None


class RuntimeConfigResponse(BaseModel):
    demo_mode: bool
    image_provider: str
    ai_enabled: bool
    provider_label: str
    wanxiang_configured: bool
    database: DatabaseInfo = Field(default_factory=DatabaseInfo)


# ---------------------------------------------------------------------------
# Common models
# ---------------------------------------------------------------------------

class AssetMetadata(BaseModel):
    prompt: str = ""
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generation_mode: str = "demo"
    provider: Optional[str] = None
    model: Optional[str] = None
    final_prompt: Optional[str] = None
    warning: Optional[str] = None


class AssetInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_type: AssetType
    size: PixelSize
    style: str = "pixel"
    image_url: str = ""
    thumbnail_url: str = ""
    metadata: AssetMetadata = Field(default_factory=AssetMetadata)


# ---------------------------------------------------------------------------
# Error
# ---------------------------------------------------------------------------

class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


# ---------------------------------------------------------------------------
# Generate
# ---------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    project_name: str = Field(min_length=1, max_length=100)
    asset_type: AssetType
    prompt: str = Field(min_length=1, max_length=500)
    style: ArtStyle = ArtStyle.PIXEL_ART
    size: PixelSize = PixelSize.S32
    count: int = Field(default=4, ge=1, le=16)
    target_engine: EngineType = EngineType.UNITY
    transparent_background: bool = True
    generation_provider: Literal["auto", "demo", "wanxiang"] = "auto"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

class TaskStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"


class GeneratedAsset(BaseModel):
    """A single asset produced by the generator."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: AssetType
    width: int
    height: int
    image_url: str
    metadata: AssetMetadata = Field(default_factory=AssetMetadata)


class GenerateResponse(BaseModel):
    """Returned immediately after POST /api/generate."""
    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    message: str = "Task created"


# ---------------------------------------------------------------------------
# Process / Trim
# ---------------------------------------------------------------------------

class TrimRequest(BaseModel):
    asset_id: str = Field(min_length=1)


class TrimResponse(BaseModel):
    asset_id: str
    original_size: list[int]
    trimmed_size: list[int]
    processed_url: str
    crop_box: list[int]


# ---------------------------------------------------------------------------
# Sprite Sheet
# ---------------------------------------------------------------------------

class SpriteSheetRequest(BaseModel):
    asset_ids: list[str] = Field(min_length=1, max_length=64)
    animation_name: str = Field(default="default", min_length=1, max_length=64)
    frame_width: int = Field(default=32, ge=1, le=1024)
    frame_height: int = Field(default=32, ge=1, le=1024)
    fps: int = Field(default=12, ge=1, le=120)
    columns: int = Field(default=4, ge=1, le=16)


class SpriteSheetFrame(BaseModel):
    index: int
    x: int
    y: int
    width: int
    height: int


class SpriteSheetResponse(BaseModel):
    spritesheet_url: str
    spritesheet_size: list[int]
    frames: list[SpriteSheetFrame]
    metadata_url: str
    animation_name: str
    frame_width: int
    frame_height: int
    frame_count: int
    fps: int


class TaskStatusResponse(BaseModel):
    """Returned by GET /api/tasks/{task_id}."""
    task_id: str
    status: TaskStatus
    progress: str = ""
    assets: list[GeneratedAsset] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    error: Optional[str] = None
    warning: Optional[str] = None
    provider: Optional[str] = None


# ---------------------------------------------------------------------------
# Tile Preview
# ---------------------------------------------------------------------------

class TilePreviewRequest(BaseModel):
    asset_id: str = Field(min_length=1)


class TilePreviewResponse(BaseModel):
    tile_preview_url: str
    tile_size: list[int]
    preview_size: list[int]


# ---------------------------------------------------------------------------
# Tile Scoring
# ---------------------------------------------------------------------------

class TileScoreRequest(BaseModel):
    asset_id: str = Field(min_length=1)


class EdgeScores(BaseModel):
    top_bottom_consistency: float
    left_right_consistency: float


class TileScoreResponse(BaseModel):
    score: float
    edge_scores: EdgeScores
    overall_rating: str
    suggestion: str


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

class ExportRequest(BaseModel):
    project_name: str = Field(min_length=1, max_length=100)
    asset_ids: list[str] = Field(min_length=1, max_length=128)
    engine: EngineType
    include_spritesheet: bool = True
    include_metadata: bool = True
    include_tile_preview: bool = True


class PackageStructure(BaseModel):
    engine: EngineType
    files: list[str]


class ExportResponse(BaseModel):
    download_url: str
    package_structure: PackageStructure
    file_count: int
    total_size_bytes: int


# ---------------------------------------------------------------------------
# Asset history (SQLite persistence)
# ---------------------------------------------------------------------------


class AssetRecord(BaseModel):
    """A single row from the generated_assets table."""
    id: str
    task_id: Optional[str] = None
    project_name: str = ""
    asset_type: str = ""
    name: str = ""
    prompt: str = ""
    style: str = ""
    size: int = 32
    target_engine: str = ""
    provider: str = ""
    image_url: str = ""
    local_path: str = ""
    metadata: Optional[dict] = None
    created_at: str = ""


class AssetListResponse(BaseModel):
    """Paginated response for GET /api/assets."""
    items: list[AssetRecord] = Field(default_factory=list)
    total: int = 0
