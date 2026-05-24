"""
Abstract base for image-generation providers.

Extracted to its own module to break the circular import between
``image_generation_service`` and ``wanxiang_image_provider``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.models.schemas import GeneratedAsset, GenerateRequest


class ImageGenerationProvider(ABC):
    """Contract that every image-generation backend must fulfil."""

    @abstractmethod
    def generate(self, req: GenerateRequest) -> list[GeneratedAsset]:
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...


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
