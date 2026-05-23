"""
Demo asset provider — returns built-in sample PNGs instead of calling
an external AI API.  Used when DEMO_MODE is enabled.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from app.config import SAMPLE_ASSETS_DIR
from app.models.schemas import AssetType, PixelSize

# Map AssetType enum value → sample-assets subdirectory name
_TYPE_DIR: dict[AssetType, str] = {
    AssetType.CHARACTER: "characters",
    AssetType.ITEM: "items",
    AssetType.TILE: "tiles",
    AssetType.UI: "ui",
}

# Filename template:  {prefix}_{size}x{size}.png
_PREFIX: dict[AssetType, str] = {
    AssetType.CHARACTER: "character",
    AssetType.ITEM: "item",
    AssetType.TILE: "tile",
    AssetType.UI: "ui",
}


def resolve_sample_path(asset_type: AssetType, size: PixelSize) -> Optional[Path]:
    """Return the filesystem path to a matching sample asset, or None."""
    subdir = _TYPE_DIR.get(asset_type, "characters")
    prefix = _PREFIX.get(asset_type, "character")
    filename = f"{prefix}_{size.value}x{size.value}.png"
    full = Path(os.path.join(SAMPLE_ASSETS_DIR, subdir, filename)).resolve()

    if full.exists() and full.is_file():
        return full
    return None


def list_available() -> list[dict]:
    """List all available sample assets (for debugging / status)."""
    results: list[dict] = []
    for at in AssetType:
        for sz in PixelSize:
            path = resolve_sample_path(at, sz)
            results.append({
                "asset_type": at.value,
                "size": sz.value,
                "available": path is not None,
                "path": str(path) if path else None,
            })
    return results
