"""
Tongyi Wanxiang / DashScope text-to-image provider.

Generates 2D game sprites by calling the DashScope ImageSynthesis API,
downloading the resulting PNGs, and saving them to ``output/generated/``.
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone

import requests

from app.config import (
    DASHSCOPE_API_KEY,
    GENERATED_DIR,
    WANXIANG_MODEL,
    WANXIANG_N,
    WANXIANG_SIZE,
)
from app.models.schemas import AssetMetadata, GeneratedAsset, GenerateRequest

logger = logging.getLogger(__name__)

DASHSCOPE_URL = (
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/"
    "text2image/image-synthesis"
)

# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

_STYLE_HINTS: dict[str, str] = {
    "pixel_art": (
        "pixel art style, crisp clean pixels, limited color palette, "
        "retro 16-bit game aesthetic, sharp edges, no anti-aliasing"
    ),
    "cartoon": (
        "cartoon style, smooth clean lines, bright vibrant colors, "
        "cel-shaded, cheerful game art"
    ),
    "dark_fantasy": (
        "dark fantasy style, moody atmospheric lighting, gothic undertones, "
        "hand-painted texture, dark souls inspired game art"
    ),
}

_TYPE_PREFIX: dict[str, str] = {
    "character": "a single 2D game character sprite",
    "item": "a single 2D game item icon or prop",
    "tile": "a seamless tileable 2D ground or wall texture tile",
    "ui": "a single 2D game UI element or HUD component",
}

_TYPE_HINTS: dict[str, str] = {
    "character": (
        "full-body character, standing pose, front-facing, "
        "centered on transparent background, game sprite sheet ready, "
        "no text no watermark"
    ),
    "item": (
        "single isolated item, centered on transparent background, "
        "icon view, game inventory ready, no text no watermark"
    ),
    "tile": (
        "seamless tileable pattern, top-down view, flat ground texture, "
        "edges must match for tiling, no text no watermark"
    ),
    "ui": (
        "game UI element, centered on transparent background, "
        "clean interface design, no text no watermark"
    ),
}


def _build_prompt(req: GenerateRequest) -> str:
    at = req.asset_type.value
    st = req.style.value
    prefix = _TYPE_PREFIX.get(at, "a 2D game asset")
    type_hint = _TYPE_HINTS.get(at, "no text no watermark")
    style_hint = _STYLE_HINTS.get(st, "pixel art style")
    return (
        f"{prefix}, {req.prompt}, {style_hint}, "
        f"{req.size.value}x{req.size.value} pixels, {type_hint}"
    )


# ---------------------------------------------------------------------------
# API call
# ---------------------------------------------------------------------------

def _call_dashscope(prompt: str, size: str, n: int) -> list[str]:
    """Call DashScope text-to-image, return list of image URLs."""
    if not DASHSCOPE_API_KEY:
        raise RuntimeError(
            "DASHSCOPE_API_KEY is not set. "
            "Copy backend/.env.example to backend/.env and fill in your API key."
        )

    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": WANXIANG_MODEL,
        "input": {"prompt": prompt},
        "parameters": {"size": size, "n": n},
    }

    logger.info("Calling DashScope model=%s size=%s n=%d", WANXIANG_MODEL, size, n)
    resp = requests.post(DASHSCOPE_URL, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()

    body = resp.json()
    if "code" in body and body.get("code") != "":
        code = body.get("code", "UNKNOWN")
        msg = body.get("message", "DashScope returned an error")
        raise RuntimeError(f"DashScope error [{code}]: {msg}")

    results = body.get("output", {}).get("results", [])
    if not results:
        raise RuntimeError("DashScope returned no image results")

    return [r["url"] for r in results if r.get("url")]


# ---------------------------------------------------------------------------
# Download helper
# ---------------------------------------------------------------------------

def _download_image(url: str, dest_dir: str) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    filename = f"{uuid.uuid4()}.png"
    dest = os.path.join(dest_dir, filename)
    logger.info("Downloading %s -> %s", url, dest)
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    with open(dest, "wb") as f:
        f.write(resp.content)
    return dest


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------

class WanxiangImageProvider:
    """Image generation provider backed by Tongyi Wanxiang (DashScope)."""

    @property
    def provider_name(self) -> str:
        return "wanxiang"

    def generate(self, req: GenerateRequest) -> list[GeneratedAsset]:
        final_prompt = _build_prompt(req)
        logger.info(
            "Wanxiang generate: type=%s style=%s count=%d",
            req.asset_type.value,
            req.style.value,
            req.count,
        )

        n_per_call = max(1, min(WANXIANG_N, 4))
        assets: list[GeneratedAsset] = []

        remaining = req.count
        while remaining > 0:
            n = min(remaining, n_per_call)
            try:
                urls = _call_dashscope(final_prompt, WANXIANG_SIZE, n)
            except Exception:
                logger.exception("DashScope call failed")
                raise

            for url in urls:
                asset_id = str(uuid.uuid4())
                name = (
                    f"{req.asset_type.value}_{req.size.value}x{req.size.value}"
                    f"_{len(assets) + 1}"
                )
                saved_path = _download_image(url, GENERATED_DIR)
                rel_path = os.path.relpath(
                    saved_path,
                    os.path.join(os.path.dirname(GENERATED_DIR)),
                ).replace("\\", "/")

                assets.append(
                    GeneratedAsset(
                        id=asset_id,
                        name=name,
                        type=req.asset_type,
                        width=req.size.value,
                        height=req.size.value,
                        image_url=f"/output/{rel_path}",
                        metadata=AssetMetadata(
                            prompt=req.prompt,
                            generated_at=datetime.now(timezone.utc),
                            generation_mode="ai",
                            provider="wanxiang",
                            model=WANXIANG_MODEL,
                            final_prompt=final_prompt,
                        ),
                    )
                )
            remaining -= len(urls)

        return assets
