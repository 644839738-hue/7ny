"""
Pydantic models for request / response validation.

Mirrors the TypeScript types in frontend/src/types/index.ts.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AssetType(str, Enum):
    CHARACTER = "character"
    PROP = "prop"
    TILE = "tile"
    UI = "ui"


class PixelSize(int, Enum):
    S32 = 32
    S64 = 64


class EngineType(str, Enum):
    UNITY = "unity"
    GODOT = "godot"


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str = "0.0.1"
    demo_mode: bool


# ---------------------------------------------------------------------------
# Common models (placeholder — will be enriched in later PRs)
# ---------------------------------------------------------------------------

class AssetMetadata(BaseModel):
    prompt: str = ""
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generation_mode: Literal["demo", "ai"] = "demo"


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
