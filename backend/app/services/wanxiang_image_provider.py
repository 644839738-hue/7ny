"""
Wanxiang (Tongyi Wanxiang) image generation provider.

Calls the DashScope text-to-image API for game-asset generation.
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

from app.config import (
    DASHSCOPE_API_KEY,
    GENERATED_DIR,
    WANXIANG_MODEL,
    WANXIANG_N,
    WANXIANG_SIZE,
)
from app.models.schemas import (
    AssetMetadata,
    GeneratedAsset,
    GenerateRequest,
)
from app.services.image_generation_service import ImageGenerationProvider

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt-building helpers
# ---------------------------------------------------------------------------

_TYPE_PREFIX: dict[str, str] = {
    "character": "game character sprite",
    "item": "game item icon",
    "tile": "seamless game tile",
    "ui": "game UI element",
}

_TYPE_HINTS: dict[str, str] = {
    "character": "full body, front view, centered, game asset",
    "item": "top-down view, isolated, game asset",
    "tile": "seamless, top-down, repeatable, game asset",
    "ui": "clean, minimal, game UI, centered",
}

_STYLE_HINTS: dict[str, str] = {
    "pixel_art": "pixel art style, crisp pixels, retro game, 16-bit",
    "cartoon": "cartoon style, smooth lines, vibrant colors, cel shaded",
    "dark_fantasy": "dark fantasy style, moody, gothic, dark colors, dramatic lighting",
}


def _build_prompt(req: GenerateRequest) -> str:
    prefix = _TYPE_PREFIX.get(req.asset_type.value, "game asset")
    type_hint = _TYPE_HINTS.get(req.asset_type.value, "")
    style_hint = _STYLE_HINTS.get(req.style.value, "")
    parts = [prefix, req.prompt, type_hint, style_hint]
    if req.transparent_background:
        parts.append("transparent background")
    return ", ".join(p for p in parts if p)


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------

class WanxiangImageProvider(ImageGenerationProvider):
    """Calls DashScope Tongyi Wanxiang text-to-image API."""

    @property
    def provider_name(self) -> str:
        return "wanxiang"

    def generate(self, req: GenerateRequest) -> list[GeneratedAsset]:
        if not DASHSCOPE_API_KEY:
            raise RuntimeError(
                "DASHSCOPE_API_KEY is not set. "
                "Set it in backend/.env or switch to demo mode."
            )

        prompt = _build_prompt(req)
        size = WANXIANG_SIZE
        n = min(req.count, WANXIANG_N)

        image_urls = self._call_dashscope(prompt, size, n)
        assets: list[GeneratedAsset] = []

        for i, url in enumerate(image_urls):
            asset_id = str(uuid.uuid4())
            local_path = self._download_image(url, asset_id)
            name = f"{req.asset_type.value}_{req.size.value}x{req.size.value}_{i + 1}"
            rel_path = os.path.relpath(local_path, os.path.join(GENERATED_DIR, ".."))
            image_url = f"/output/{rel_path.replace(os.sep, '/')}"

            assets.append(
                GeneratedAsset(
                    id=asset_id,
                    name=name,
                    type=req.asset_type,
                    width=req.size.value,
                    height=req.size.value,
                    image_url=image_url,
                    metadata=AssetMetadata(
                        prompt=req.prompt,
                        generated_at=datetime.now(timezone.utc),
                        generation_mode="ai",
                        provider="wanxiang",
                        model=WANXIANG_MODEL,
                        final_prompt=prompt,
                    ),
                )
            )

        return assets

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _call_dashscope(self, prompt: str, size: str, n: int) -> list[str]:
        """Call DashScope API, return list of image URLs."""
        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": WANXIANG_MODEL,
            "input": {
                "prompt": prompt,
            },
            "parameters": {
                "size": size,
                "n": n,
            },
        }

        resp = requests.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis",
            headers=headers,
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()

        if "output" not in data:
            raise RuntimeError(
                f"DashScope returned unexpected response: {data}"
            )

        results = data["output"].get("results", [])
        if not results:
            raise RuntimeError("DashScope returned no image results")

        return [r["url"] for r in results if "url" in r]

    def _download_image(self, url: str, asset_id: str) -> str:
        """Download an image URL into GENERATED_DIR, return local path."""
        dest_dir = Path(GENERATED_DIR)
        dest_dir.mkdir(parents=True, exist_ok=True)

        resp = requests.get(url, timeout=60)
        resp.raise_for_status()

        ext = ".png"
        content_type = resp.headers.get("content-type", "")
        if "jpeg" in content_type or "jpg" in content_type:
            ext = ".jpg"
        elif "webp" in content_type:
            ext = ".webp"

        filename = f"{asset_id}{ext}"
        dest_path = dest_dir / filename
        dest_path.write_bytes(resp.content)
        logger.info("Downloaded %s → %s", url, dest_path)
        return str(dest_path)
