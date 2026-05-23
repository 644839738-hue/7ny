"""
Sprite-sheet stitching service.

Takes a list of generated asset IDs, loads them from ``OUTPUT_DIR``,
composes a sprite-sheet grid, and writes the result plus a JSON metadata
file.
"""

from __future__ import annotations

import json
import math
import uuid
from pathlib import Path
from typing import Optional

from PIL import Image

from app.config import OUTPUT_DIR
from app.models.schemas import SpriteSheetFrame


def _find_asset_file(asset_id: str) -> Optional[Path]:
    """Locate an asset file in OUTPUT_DIR by its UUID (any extension)."""
    for candidate in Path(OUTPUT_DIR).iterdir():
        if candidate.is_file() and candidate.stem == asset_id:
            return candidate
    return None


def build_spritesheet(
    asset_ids: list[str],
    animation_name: str,
    frame_width: int,
    frame_height: int,
    columns: int,
    fps: int = 12,
) -> dict:
    """Compose a sprite-sheet from previously generated assets.

    Each source image is resized (preserving aspect ratio, no upscale) to
    fit within *frame_width* × *frame_height* and centred on a transparent
    canvas.  Frames are laid out left-to-right, top-to-bottom.

    Returns a dict with ``spritesheet_url``, ``spritesheet_size``,
    ``frames``, ``metadata_url``, and animation metadata.
    """
    images: list[Image.Image] = []
    for aid in asset_ids:
        path = _find_asset_file(aid)
        if path is None:
            raise FileNotFoundError(
                f"Asset '{aid}' not found in {OUTPUT_DIR}"
            )
        img = Image.open(path).convert("RGBA")
        # Fit inside the frame without upscaling
        img = _fit_in_frame(img, frame_width, frame_height)
        images.append(img)

    frame_count = len(images)
    rows = math.ceil(frame_count / columns)

    sheet_w = columns * frame_width
    sheet_h = rows * frame_height
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

    frames: list[SpriteSheetFrame] = []
    for i, img in enumerate(images):
        col = i % columns
        row = i // columns
        ox = col * frame_width + (frame_width - img.width) // 2
        oy = row * frame_height + (frame_height - img.height) // 2
        sheet.paste(img, (ox, oy), img)

        frames.append(SpriteSheetFrame(
            index=i,
            x=col * frame_width,
            y=row * frame_height,
            width=frame_width,
            height=frame_height,
        ))

    # Save spritesheet image
    ss_id = str(uuid.uuid4())
    ss_filename = f"spritesheet_{ss_id}.png"
    ss_path = Path(OUTPUT_DIR) / ss_filename
    sheet.save(ss_path, "PNG")

    # Build & save JSON metadata
    metadata = {
        "animation_name": animation_name,
        "frame_width": frame_width,
        "frame_height": frame_height,
        "frame_count": frame_count,
        "columns": columns,
        "rows": rows,
        "fps": fps,
        "spritesheet_size": [sheet_w, sheet_h],
        "animations": {
            animation_name: {
                "from": 0,
                "to": frame_count - 1,
                "fps": fps,
            }
        },
        "frames": [f.model_dump() for f in frames],
    }
    meta_filename = f"spritesheet_{ss_id}.json"
    meta_path = Path(OUTPUT_DIR) / meta_filename
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2, ensure_ascii=False)

    return {
        "spritesheet_url": f"/output/{ss_filename}",
        "spritesheet_size": [sheet_w, sheet_h],
        "frames": frames,
        "metadata_url": f"/output/{meta_filename}",
        "animation_name": animation_name,
        "frame_width": frame_width,
        "frame_height": frame_height,
        "frame_count": frame_count,
        "fps": fps,
    }


def _fit_in_frame(img: Image.Image, fw: int, fh: int) -> Image.Image:
    """Resize *img* to fit within ``fw×fh`` (no upscale), centred on a
    transparent canvas of that size."""
    w, h = img.size
    scale = min(1.0, fw / max(w, 1), fh / max(h, 1))
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    resized = img.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    ox = (fw - new_w) // 2
    oy = (fh - new_h) // 2
    canvas.paste(resized, (ox, oy), resized)
    return canvas
