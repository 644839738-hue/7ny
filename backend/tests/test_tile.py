"""Unit tests for tile preview service."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

import app.services.tile as tile


def _solid_img(w: int, h: int, color=(128, 64, 32, 255)) -> Image.Image:
    return Image.new("RGBA", (w, h), color)


def _save_png(img: Image.Image, dir_: str, stem: str) -> str:
    path = Path(dir_) / f"{stem}.png"
    img.save(path, "PNG")
    return str(path)


class TestBuildTilePreview:
    def test_3x3_grid_dimensions(self):
        """A 32×32 tile produces a 96×96 preview."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(tile, "OUTPUT_DIR", tmpdir):
                _save_png(_solid_img(32, 32), tmpdir, "test_tile")

                result = tile.build_tile_preview("test_tile")

                assert result["tile_size"] == [32, 32]
                assert result["preview_size"] == [96, 96]

    def test_output_file_exists_and_correct_size(self):
        """The preview PNG is saved and has 3×3 dimensions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(tile, "OUTPUT_DIR", tmpdir):
                _save_png(_solid_img(48, 64), tmpdir, "tile_48x64")

                result = tile.build_tile_preview("tile_48x64")

                fname = os.path.basename(result["tile_preview_url"])
                ppath = os.path.join(tmpdir, fname)
                assert os.path.isfile(ppath)

                with Image.open(ppath) as preview:
                    assert preview.size == (144, 192)  # 48*3 × 64*3

    def test_non_square_tile(self):
        """Rectangular tiles (e.g. 64×32) should tile correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(tile, "OUTPUT_DIR", tmpdir):
                _save_png(_solid_img(64, 32, (255, 0, 0, 255)), tmpdir, "rect_tile")

                result = tile.build_tile_preview("rect_tile")

                assert result["tile_size"] == [64, 32]
                assert result["preview_size"] == [192, 96]

    def test_missing_asset_raises(self):
        with pytest.raises(FileNotFoundError):
            tile.build_tile_preview("no-such-tile")

    def test_url_format(self):
        """The preview URL points into /output/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(tile, "OUTPUT_DIR", tmpdir):
                _save_png(_solid_img(32, 32), tmpdir, "url_tile")

                result = tile.build_tile_preview("url_tile")

                assert result["tile_preview_url"].startswith("/output/tile_preview_")
                assert result["tile_preview_url"].endswith(".png")
