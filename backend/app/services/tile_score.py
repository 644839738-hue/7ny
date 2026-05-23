"""
Tile edge-consistency scoring service.

Compares opposing edges of a tile image to estimate how seamless the
tiling will look when repeated.  Scores range 0–100 (higher = better).
"""

from __future__ import annotations

import statistics
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


def _edge_mean_rgb(img: Image.Image, edge: str) -> tuple[float, float, float]:
    """Return the mean (R, G, B) of a single-pixel *edge* of ``img``.

    *edge* must be one of ``"top"``, ``"bottom"``, ``"left"``, ``"right"``.
    """
    w, h = img.size
    pixels: list[tuple[int, int, int]] = []

    if edge == "top":
        pixels = [img.getpixel((x, 0))[:3] for x in range(w)]  # type: ignore[misc]
    elif edge == "bottom":
        pixels = [img.getpixel((x, h - 1))[:3] for x in range(w)]  # type: ignore[misc]
    elif edge == "left":
        pixels = [img.getpixel((0, y))[:3] for y in range(h)]  # type: ignore[misc]
    elif edge == "right":
        pixels = [img.getpixel((w - 1, y))[:3] for y in range(h)]  # type: ignore[misc]
    else:
        raise ValueError(f"Unknown edge: {edge}")

    r = statistics.mean(p[0] for p in pixels)
    g = statistics.mean(p[1] for p in pixels)
    b = statistics.mean(p[2] for p in pixels)
    return (r, g, b)


def _rgb_distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    """Euclidean distance between two RGB colour vectors (range 0–~441)."""
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def _similarity(dist: float) -> float:
    """Convert an RGB distance to a 0–100 similarity score.

    Max possible Euclidean distance in RGB space is ≈441.7, so we divide
    by 4.417 to normalise to 0–100, then subtract from 100.
    """
    raw = max(0.0, 100.0 - dist / 4.417)
    return round(raw, 1)


def _rating(score: float) -> str:
    if score >= 90:
        return "excellent"
    if score >= 70:
        return "good"
    if score >= 50:
        return "fair"
    return "poor"


def _suggestion(score: float) -> str:
    if score >= 80:
        return "适合平铺，边缘过渡自然，可直接用于游戏场景"
    if score >= 60:
        return "可用于原型开发，有轻微接缝，建议微调边缘像素"
    return "不建议作为无缝 Tile 使用，边缘断裂明显，建议重新生成"


def score_tile(asset_id: str) -> dict:
    """Compute edge-consistency scores for a tile asset.

    Returns a dict with ``score``, ``edge_scores`` (top_bottom_consistency
    and left_right_consistency), ``overall_rating``, and ``suggestion``.
    """
    path = _find_asset_file(asset_id)
    if path is None:
        raise FileNotFoundError(
            f"Asset '{asset_id}' not found in {OUTPUT_DIR}"
        )

    img = Image.open(path).convert("RGBA")

    top = _edge_mean_rgb(img, "top")
    bottom = _edge_mean_rgb(img, "bottom")
    left = _edge_mean_rgb(img, "left")
    right = _edge_mean_rgb(img, "right")

    tb_dist = _rgb_distance(top, bottom)
    lr_dist = _rgb_distance(left, right)

    tb_score = _similarity(tb_dist)
    lr_score = _similarity(lr_dist)
    overall = round((tb_score + lr_score) / 2, 1)

    return {
        "score": overall,
        "edge_scores": {
            "top_bottom_consistency": tb_score,
            "left_right_consistency": lr_score,
        },
        "overall_rating": _rating(overall),
        "suggestion": _suggestion(overall),
    }
