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

When ``DEMO_MODE`` is *off* and the external provider raises, the service
automatically falls back to the demo provider and includes a warning in the
returned assets' metadata.
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

from app.config import DEMO_MODE, OUTPUT_DIR
from app.models.schemas import (
    AssetMetadata,
    GeneratedAsset,
    GenerateRequest,
)
from app.utils.demo_provider import resolve_sample_path

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _copy_to_output(source_path: str, asset_id: str) -> str:
    """Copy *source_path* into OUTPUT_DIR using *asset_id* as the filename.

    Returns the public ``/output/<name>`` URL path.
    """
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
    """Build *count* ``GeneratedAsset`` objects from a single sample image."""
    assets: list[GeneratedAsset] = []
    meta_kwargs: dict = {
        "prompt": req.prompt,
        "generated_at": datetime.now(timezone.utc),
        "generation_mode": generation_mode,
    }
    if warning:
        meta_kwargs["warning"] = warning  # type: ignore[assignment]

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
        """Produce *req.count* assets for the given request."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier (e.g. ``"demo"``, ``"openai"``)."""
        ...


# ---------------------------------------------------------------------------
# Demo provider (always available)
# ---------------------------------------------------------------------------

class DemoImageProvider(ImageGenerationProvider):
    """Returns pre-built sample assets from ``examples/sample-assets/``."""

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
# External AI provider (stub — real implementation in a future PR)
# ---------------------------------------------------------------------------

class ExternalImageProvider(ImageGenerationProvider):
    """Calls an external image-generation API.

    The API endpoint and key are read from the environment:

    * ``IMAGE_API_BASE_URL`` — base URL of the generation API
    * ``IMAGE_API_KEY`` — bearer token or API key

    If either is missing the provider raises ``RuntimeError`` on the first
    ``generate()`` call, which triggers the automatic demo fallback.
    """

    def __init__(self) -> None:
        self._base_url = os.getenv("IMAGE_API_BASE_URL", "").strip()
        self._api_key = os.getenv("IMAGE_API_KEY", "").strip()

    @property
    def provider_name(self) -> str:
        return "external"

    def generate(self, req: GenerateRequest) -> list[GeneratedAsset]:
        """Attempt external generation; raise if not configured.

        .. note::
           This is a **stub**.  Replace the ``NotImplementedError`` with a
           real HTTP call (e.g. ``httpx`` / ``requests``) to an image API
           such as OpenAI DALL·E, Stability AI, or a self-hosted model.
        """
        if not self._base_url or not self._api_key:
            raise RuntimeError(
                "External image API is not configured. "
                "Set IMAGE_API_BASE_URL and IMAGE_API_KEY environment variables, "
                "or enable DEMO_MODE=true."
            )

        # ------------------------------------------------------------------
        # STUB — replace with real API call
        # ------------------------------------------------------------------
        # import httpx
        # async with httpx.AsyncClient() as client:
        #     resp = await client.post(
        #         f"{self._base_url}/v1/images/generate",
        #         headers={"Authorization": f"Bearer {self._api_key}"},
        #         json={...},
        #     )
        #     resp.raise_for_status()
        #     ...
        # ------------------------------------------------------------------

        raise NotImplementedError(
            "ExternalImageProvider.generate() is a stub.  "
            "Implement the API call for your chosen image-generation backend."
        )


# ---------------------------------------------------------------------------
# Provider factory (decides which backend to use)
# ---------------------------------------------------------------------------

def _create_provider() -> ImageGenerationProvider:
    """Return the appropriate provider based on ``DEMO_MODE``."""
    if DEMO_MODE:
        logger.info("Image generation: using DEMO provider")
        return DemoImageProvider()

    logger.info("Image generation: using EXTERNAL provider")
    return ExternalImageProvider()


# ---------------------------------------------------------------------------
# Top-level API used by the generator orchestrator
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
    """Run generation with automatic demo-fallback on failure.

    *Always* returns assets — if the external provider fails and
    ``DEMO_MODE`` is off, the demo provider is used as a safety net.
    """
    provider = _create_provider()

    try:
        assets = provider.generate(req)
        return ImageGenerationResult(
            assets=assets,
            provider_used=provider.provider_name,
        )
    except Exception as exc:
        if provider.provider_name == "demo":
            raise  # demo itself failed — nothing left to fall back to

        logger.warning(
            "External generation failed (%s), falling back to demo provider",
            exc,
        )
        fallback = DemoImageProvider()
        warning_msg = (
            f"External generation failed: {exc}. "
            f"Falling back to demo assets. "
            f"Set IMAGE_API_BASE_URL and IMAGE_API_KEY to use real AI generation."
        )
        assets = fallback.generate(req)
        return ImageGenerationResult(
            assets=assets,
            provider_used="demo",
            fallback_occurred=True,
            warning=warning_msg,
        )
