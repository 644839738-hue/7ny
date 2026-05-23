"""
Post‑processing service — orchestrates the asset processing pipeline.

The pipeline reads generated assets from ``OUTPUT_DIR``, runs them through
:mod:`image_utils.process_asset`, and writes the processed result back.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Optional

from PIL import Image

from app.config import OUTPUT_DIR
from app.utils import image_utils


def run_trim(asset_id: str) -> Optional[dict]:
    """Trim transparent edges from a previously generated asset.

    Args:
        asset_id: The asset UUID (filename without extension in OUTPUT_DIR).

    Returns:
        A result dict with ``asset_id``, ``original_size``, ``trimmed_size``,
        ``processed_url``, and ``crop_box``; or ``None`` if the file was not found.
    """
    # Locate the source file (try .png extension)
    src_path = None
    for ext in (".png", ".PNG"):
        candidate = Path(OUTPUT_DIR) / f"{asset_id}{ext}"
        if candidate.exists():
            src_path = candidate
            break

    if src_path is None:
        return None

    image = Image.open(src_path).convert("RGBA")
    original_size = list(image.size)

    processed, info = image_utils.process_asset(
        image,
        target_size=max(original_size),  # keep largest dimension as target
        trim=True,
        centre=False,  # centring is a separate step
        allow_upscale=False,
    )

    # Save processed image
    dest_name = f"{asset_id}_trimmed.png"
    dest_path = Path(OUTPUT_DIR) / dest_name
    processed.save(dest_path, "PNG")

    # Calculate crop box
    bbox = image_utils.get_content_bbox(image)
    crop_box = list(bbox) if bbox else [0, 0, original_size[0], original_size[1]]

    return {
        "asset_id": asset_id,
        "original_size": original_size,
        "trimmed_size": list(processed.size),
        "processed_url": f"/output/{dest_name}",
        "crop_box": crop_box,
    }
