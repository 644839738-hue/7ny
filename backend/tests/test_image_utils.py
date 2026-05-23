"""Unit tests for the image processing utilities."""

import pytest
from PIL import Image

from app.utils.image_utils import (
    get_content_bbox,
    has_alpha,
    process_asset,
    remove_background,
    resize_to_target,
    trim_transparent_edges,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _solid_rgba(w: int, h: int, color=(255, 0, 0, 255)) -> Image.Image:
    return Image.new("RGBA", (w, h), color)


def _transparent_rgba(w: int, h: int) -> Image.Image:
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def _solid_rgb(w: int, h: int) -> Image.Image:
    return Image.new("RGB", (w, h), (255, 0, 0))


# ---------------------------------------------------------------------------
# has_alpha
# ---------------------------------------------------------------------------


class TestHasAlpha:
    def test_rgba_true(self):
        assert has_alpha(_solid_rgba(32, 32)) is True

    def test_rgb_false(self):
        assert has_alpha(_solid_rgb(32, 32)) is False


# ---------------------------------------------------------------------------
# get_content_bbox
# ---------------------------------------------------------------------------


class TestGetContentBbox:
    def test_solid_image_returns_full_bounds(self):
        img = _solid_rgba(32, 64)
        bbox = get_content_bbox(img)
        assert bbox == (0, 0, 32, 64)

    def test_fully_transparent_returns_none(self):
        img = _transparent_rgba(32, 32)
        assert get_content_bbox(img) is None

    def test_centred_content(self):
        """A 10×10 solid square centred on a 32×32 transparent canvas."""
        img = _transparent_rgba(32, 32)
        inner = _solid_rgba(10, 10)
        img.paste(inner, (11, 11))
        bbox = get_content_bbox(img)
        assert bbox == (11, 11, 21, 21)

    def test_no_alpha_returns_full_bounds(self):
        img = _solid_rgb(32, 32)
        bbox = get_content_bbox(img)
        assert bbox == (0, 0, 32, 32)


# ---------------------------------------------------------------------------
# trim_transparent_edges
# ---------------------------------------------------------------------------


class TestTrimTransparentEdges:
    def test_trims_surrounding_transparency(self):
        img = _transparent_rgba(64, 64)
        inner = _solid_rgba(16, 16, (0, 255, 0, 255))
        img.paste(inner, (24, 24))
        trimmed = trim_transparent_edges(img)
        assert trimmed.size == (16, 16)

    def test_fully_transparent_returns_1x1(self):
        img = _transparent_rgba(32, 32)
        trimmed = trim_transparent_edges(img)
        assert trimmed.size == (1, 1)
        assert trimmed.getpixel((0, 0)) == (0, 0, 0, 0)

    def test_no_alpha_returns_unchanged(self):
        img = _solid_rgb(32, 32)
        trimmed = trim_transparent_edges(img)
        # No alpha → no trim; copy is returned
        assert trimmed.size == img.size


# ---------------------------------------------------------------------------
# resize_to_target
# ---------------------------------------------------------------------------


class TestResizeToTarget:
    def test_larger_image_scales_down(self):
        img = _solid_rgba(64, 64)
        result = resize_to_target(img, 32)
        assert result.size == (32, 32)

    def test_smaller_image_not_upscaled_by_default(self):
        img = _solid_rgba(16, 16)
        result = resize_to_target(img, 32)
        # 16×16 stays 16×16 but pasted on 32×32 canvas
        assert result.size == (32, 32)
        bbox = get_content_bbox(result)
        assert bbox == (8, 8, 24, 24)  # centred

    def test_smaller_image_upscaled_when_allowed(self):
        img = _solid_rgba(16, 16)
        result = resize_to_target(img, 32, allow_upscale=True)
        assert result.size == (32, 32)
        bbox = get_content_bbox(result)
        assert bbox == (0, 0, 32, 32)

    def test_rectangular_preserves_aspect(self):
        img = _solid_rgba(64, 32)
        result = resize_to_target(img, 32)
        assert result.size == (32, 32)
        bbox = get_content_bbox(result)
        # 64×32 → scale 0.5 → 32×16, centred vertically
        assert bbox == (0, 8, 32, 24)


# ---------------------------------------------------------------------------
# remove_background (stub)
# ---------------------------------------------------------------------------


class TestRemoveBackground:
    def test_rgb_converts_to_rgba(self):
        img = _solid_rgb(32, 32)
        result = remove_background(img)
        assert result.mode == "RGBA"

    def test_rgba_unchanged(self):
        img = _solid_rgba(32, 32)
        result = remove_background(img)
        assert result.mode == "RGBA"
        assert result.size == (32, 32)


# ---------------------------------------------------------------------------
# process_asset (full pipeline)
# ---------------------------------------------------------------------------


class TestProcessAsset:
    def test_pipeline_trim_and_centre(self):
        img = _transparent_rgba(64, 64)
        inner = _solid_rgba(32, 32, (0, 0, 255, 255))
        img.paste(inner, (16, 16))
        processed, info = process_asset(img, target_size=32, trim=True, centre=True)
        assert processed.size == (32, 32)
        assert info["original_size"] == [64, 64]
        assert info["trimmed_size"] == [32, 32]
        assert info["final_size"] == [32, 32]

    def test_pipeline_no_trim(self):
        img = _solid_rgba(48, 48)
        processed, info = process_asset(img, target_size=32, trim=False, centre=True)
        assert processed.size == (32, 32)
        assert info["trimmed_size"] == [48, 48]
