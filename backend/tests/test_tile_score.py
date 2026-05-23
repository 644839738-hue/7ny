"""Unit tests for tile edge-consistency scoring."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

import app.services.tile_score as ts


def _solid_img(w: int, h: int, color=(128, 64, 32, 255)) -> Image.Image:
    return Image.new("RGBA", (w, h), color)


def _save_png(img: Image.Image, dir_: str, stem: str) -> str:
    path = Path(dir_) / f"{stem}.png"
    img.save(path, "PNG")
    return str(path)


class TestEdgeMeanRgb:
    def test_solid_image_all_edges_equal(self):
        """All edges of a solid-colour image have identical mean RGB."""
        img = _solid_img(32, 32, (100, 150, 200, 255))
        top = ts._edge_mean_rgb(img, "top")
        bottom = ts._edge_mean_rgb(img, "bottom")
        left = ts._edge_mean_rgb(img, "left")
        right = ts._edge_mean_rgb(img, "right")
        assert top == (100.0, 150.0, 200.0)
        assert top == bottom == left == right

    def test_gradient_top_bottom_differ(self):
        """Top-half red, bottom-half blue → edges differ."""
        img = Image.new("RGBA", (32, 32))
        for y in range(32):
            color = (255, 0, 0) if y < 16 else (0, 0, 255)
            for x in range(32):
                img.putpixel((x, y), (*color, 255))
        top = ts._edge_mean_rgb(img, "top")
        bottom = ts._edge_mean_rgb(img, "bottom")
        assert top == (255.0, 0.0, 0.0)
        assert bottom == (0.0, 0.0, 255.0)

    def test_unknown_edge_raises(self):
        img = _solid_img(16, 16)
        with pytest.raises(ValueError, match="Unknown edge"):
            ts._edge_mean_rgb(img, "north")


class TestScoreTile:
    def test_solid_tile_perfect_score(self):
        """A solid-colour tile scores 100 — edges are identical."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(ts, "OUTPUT_DIR", tmpdir):
                _save_png(_solid_img(32, 32, (64, 128, 192, 255)), tmpdir, "solid")

                result = ts.score_tile("solid")

                assert result["score"] == 100.0
                assert result["edge_scores"]["top_bottom_consistency"] == 100.0
                assert result["edge_scores"]["left_right_consistency"] == 100.0
                assert result["overall_rating"] == "excellent"

    def test_different_edges_lowers_score(self):
        """Manually different edges should produce a sub-100 score."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(ts, "OUTPUT_DIR", tmpdir):
                img = Image.new("RGBA", (32, 32), (0, 0, 0, 255))
                # paint top edge red
                for x in range(32):
                    img.putpixel((x, 0), (255, 0, 0, 255))
                # paint left edge green
                for y in range(32):
                    img.putpixel((0, y), (0, 255, 0, 255))

                _save_png(img, tmpdir, "edgy")

                result = ts.score_tile("edgy")

                assert result["score"] < 100.0
                assert result["overall_rating"] in ("excellent", "good", "fair", "poor")
                assert isinstance(result["suggestion"], str)

    def test_missing_asset_raises(self):
        with pytest.raises(FileNotFoundError):
            ts.score_tile("no-such-tile")

    def test_rating_tiers(self):
        """Verify that _rating() maps scores to correct tiers."""
        assert ts._rating(95) == "excellent"
        assert ts._rating(90) == "excellent"
        assert ts._rating(75) == "good"
        assert ts._rating(70) == "good"
        assert ts._rating(55) == "fair"
        assert ts._rating(50) == "fair"
        assert ts._rating(30) == "poor"

    def test_suggestion_tiers(self):
        """Verify that _suggestion() maps scores to correct suggestions."""
        assert "适合平铺" in ts._suggestion(85)
        assert "可用于原型" in ts._suggestion(70)
        assert "不建议" in ts._suggestion(50)
