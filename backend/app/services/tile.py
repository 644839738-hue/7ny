"""
Tile preview service.

Takes a single tile asset, generates a 3×3 tiling preview image so users
can visually check how the tile repeats.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Optional

from PIL import Image

from app.config import OUTPUT_DIR


def _find_asset_file(asset_id: str) -> Optional[Path]:
    """Locate an asset file in OUTPUT_DIR by its UUID stem."""
    for candidate in Path(OUTPUT_DIR).iterdir():
        if candidate.is_file() and candidate.stem == asset_id:
            return candidate
    return None


def build_tile_preview(asset_id: str) -> dict:
    """Create a 3×3 tiling preview for a single tile asset.

    Returns a dict with ``tile_preview_url``, ``tile_size``, and
    ``preview_size``.
    """
    path = _find_asset_file(asset_id)
    if path is None:
        raise FileNotFoundError(
            f"Asset '{asset_id}' not found in {OUTPUT_DIR}"
        )

    tile = Image.open(path).convert("RGBA")
    tw, th = tile.size

    preview = Image.new("RGBA", (tw * 3, th * 3), (0, 0, 0, 0))
    for row in range(3):
        for col in range(3):
            preview.paste(tile, (col * tw, row * th), tile)

    preview_id = str(uuid.uuid4())
    preview_filename = f"tile_preview_{preview_id}.png"
    preview_path = Path(OUTPUT_DIR) / preview_filename
    preview.save(preview_path, "PNG")

    return {
        "tile_preview_url": f"/output/{preview_filename}",
        "tile_size": [tw, th],
        "preview_size": [tw * 3, th * 3],
    }
