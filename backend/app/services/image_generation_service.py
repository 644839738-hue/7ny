"""
Unified image-generation service.

Provides a pluggable provider interface so the generation backend can be
swapped between the built-in demo provider and an external AI API without
changing any orchestration code.

## Provider contract

    class ImageGenerationProvider(ABC):
        def generate(req) -> list[GeneratedAsset]
        def provider_name -> str

## Fallback behaviour

When ``ALLOW_DEMO_FALLBACK`` is true and a non-demo provider raises, the
service automatically falls back to the demo provider and includes a warning
in the returned assets' metadata.
"""

from __future__ import annotations

import logging
import os
import shutil
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import ALLOW_DEMO_FALLBACK, DEMO_MODE, IMAGE_PROVIDER, OUTPUT_DIR
from app.models.schemas import (
    AssetMetadata,
    GeneratedAsset,
    GenerateRequest,
)
from app.utils.demo_provider import resolve_sample_path

logger = logging.getLogger(__name__)

# Lazy import for Wanxiang (pulls in requests/dashscope)
try:
    from app.services.wanxiang_image_provider import WanxiangImageProvider  # noqa: F811
    _WANXIANG_AVAILABLE = True
except ImportError:
    _WANXIANG_AVAILABLE = False


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _copy_to_output(source_path: str, asset_id: str) -> str:
    ext = os.path.splitext(source_path)[1] or ".png"
    dest_name = f"{asset_id}{ext}"
    dest = Path(OUTPUT_DIR) / dest_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(source_path), str(dest))
    return f"/output/{dest_name}"


def _build_assets(
    req: GenerateRequest,
    source_path: str,
    generation_mode: str,
    warning: Optional[str] = None,
) -> list[GeneratedAsset]:
    assets: list[GeneratedAsset] = []
    meta_kwargs: dict = {
        "prompt": req.prompt,
        "generated_at": datetime.now(timezone.utc),
        "generation_mode": generation_mode,
    }
    if warning:
        meta_kwargs["warning"] = warning

    for i in range(req.count):
        asset_id = str(uuid.uuid4())
        name = f"{req.asset_type.value}_{req.size.value}x{req.size.value}_{i + 1}"
        image_url = _copy_to_output(source_path, asset_id)
        assets.append(
            GeneratedAsset(
                id=asset_id,
                name=name,
                type=req.asset_type,
                width=req.size.value,
                height=req.size.value,
                image_url=image_url,
                metadata=AssetMetadata(**meta_kwargs),
            )
        )
    return assets


# ---------------------------------------------------------------------------
# Abstract provider
# ---------------------------------------------------------------------------

class ImageGenerationProvider(ABC):
    """Contract that every image-generation backend must fulfil."""

    @abstractmethod
    def generate(self, req: GenerateRequest) -> list[GeneratedAsset]:
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...


# ---------------------------------------------------------------------------
# Demo provider
# ---------------------------------------------------------------------------

class DemoImageProvider(ImageGenerationProvider):

    @property
    def provider_name(self) -> str:
        return "demo"

    def generate(self, req: GenerateRequest) -> list[GeneratedAsset]:
        sample_path = resolve_sample_path(req.asset_type, req.size)
        if sample_path is None:
            raise RuntimeError(
                f"No sample asset for type={req.asset_type.value} "
                f"size={req.size.value}.  Run the sample-asset generation script."
            )
        return _build_assets(req, str(sample_path), generation_mode="demo")


# ---------------------------------------------------------------------------
# External AI provider (stub)
# ---------------------------------------------------------------------------

class ExternalImageProvider(ImageGenerationProvider):

    def __init__(self) -> None:
        self._base_url = os.getenv("IMAGE_API_BASE_URL", "").strip()
        self._api_key = os.getenv("IMAGE_API_KEY", "").strip()

    @property
    def provider_name(self) -> str:
        return "external"

    def generate(self, req: GenerateRequest) -> list[GeneratedAsset]:
        if not self._base_url or not self._api_key:
            raise RuntimeError(
                "External image API is not configured. "
                "Set IMAGE_API_BASE_URL and IMAGE_API_KEY environment variables."
            )
        raise NotImplementedError(
            "ExternalImageProvider.generate() is a stub."
        )


# ---------------------------------------------------------------------------
# Provider factory
# ---------------------------------------------------------------------------

def _create_provider(generation_provider: str = "auto") -> ImageGenerationProvider:
    """Return the appropriate provider based on request choice and env config."""

    if generation_provider == "demo":
        logger.info("Image generation: DEMO provider (request-level)")
        return DemoImageProvider()

    if generation_provider == "wanxiang":
        if not _WANXIANG_AVAILABLE:
            logger.warning("Wanxiang provider unavailable (import failed), falling back to demo")
            return DemoImageProvider()
        logger.info("Image generation: WANXIANG provider (request-level)")
        return WanxiangImageProvider()

    # "auto" — follow environment config
    if DEMO_MODE:
        logger.info("Image generation: DEMO provider (env default)")
        return DemoImageProvider()

    if IMAGE_PROVIDER == "wanxiang" and _WANXIANG_AVAILABLE:
        logger.info("Image generation: WANXIANG provider (env default)")
        return WanxiangImageProvider()

    logger.info("Image generation: using EXTERNAL provider")
    return ExternalImageProvider()


# ---------------------------------------------------------------------------
# Top-level API
# ---------------------------------------------------------------------------

class ImageGenerationResult:
    """Container returned by :func:`generate_assets`."""

    def __init__(
        self,
        assets: list[GeneratedAsset],
        provider_used: str,
        fallback_occurred: bool = False,
        warning: Optional[str] = None,
    ) -> None:
        self.assets = assets
        self.provider_used = provider_used
        self.fallback_occurred = fallback_occurred
        self.warning = warning


def generate_assets(req: GenerateRequest) -> ImageGenerationResult:
    """Run generation with automatic demo-fallback on failure."""

    provider = _create_provider(req.generation_provider)

    try:
        assets = provider.generate(req)
        return ImageGenerationResult(
            assets=assets,
            provider_used=provider.provider_name,
        )
    except Exception as exc:
        if provider.provider_name == "demo":
            raise

        logger.warning(
            "%s generation failed (%s), falling back to demo provider",
            provider.provider_name,
            exc,
        )

        if not ALLOW_DEMO_FALLBACK:
            raise

        fallback = DemoImageProvider()
        warning_msg = (
            f"{provider.provider_name} generation failed: {exc}. "
            f"Falling back to demo assets."
        )
        assets = fallback.generate(req)
        return ImageGenerationResult(
            assets=assets,
            provider_used="demo",
            fallback_occurred=True,
            warning=warning_msg,
        )
