"""Unit tests for sprite-sheet service."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

import app.services.spritesheet as ss


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _solid_img(w: int, h: int, color=(255, 0, 0, 255)) -> Image.Image:
    return Image.new("RGBA", (w, h), color)


def _save_png(img: Image.Image, dir_: str, stem: str) -> str:
    path = Path(dir_) / f"{stem}.png"
    img.save(path, "PNG")
    return str(path)


# ---------------------------------------------------------------------------
# _fit_in_frame
# ---------------------------------------------------------------------------


class TestFitInFrame:
    def test_smaller_than_frame_not_upscaled(self):
        img = _solid_img(16, 16, (0, 255, 0, 255))
        result = ss._fit_in_frame(img, 32, 32)
        assert result.size == (32, 32)
        # content stays 16×16, centred
        alpha = result.getchannel("A")
        bbox = alpha.getbbox()
        assert bbox == (8, 8, 24, 24)

    def test_larger_than_frame_scaled_down(self):
        img = _solid_img(64, 64, (0, 0, 255, 255))
        result = ss._fit_in_frame(img, 32, 32)
        assert result.size == (32, 32)
        alpha = result.getchannel("A")
        bbox = alpha.getbbox()
        assert bbox == (0, 0, 32, 32)


# ---------------------------------------------------------------------------
# build_spritesheet
# ---------------------------------------------------------------------------


class TestBuildSpritesheet:
    def test_4_frames_2x2_grid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(ss, "OUTPUT_DIR", tmpdir):
                # Create 4 solid-colour assets
                colors = [
                    (255, 0, 0, 255),
                    (0, 255, 0, 255),
                    (0, 0, 255, 255),
                    (255, 255, 0, 255),
                ]
                aid_list = []
                for i, c in enumerate(colors):
                    name = f"asset{i}"
                    _save_png(_solid_img(32, 32, c), tmpdir, name)
                    aid_list.append(name)

                result = ss.build_spritesheet(
                    asset_ids=aid_list,
                    animation_name="walk",
                    frame_width=32,
                    frame_height=32,
                    columns=2,
                    fps=10,
                )

                # Check response fields
                assert result["animation_name"] == "walk"
                assert result["frame_count"] == 4
                assert result["fps"] == 10
                assert result["spritesheet_size"] == [64, 64]
                assert len(result["frames"]) == 4

                # Check spritesheet file exists (resolve against tmpdir)
                ss_fname = os.path.basename(result["spritesheet_url"])
                ss_path = os.path.join(tmpdir, ss_fname)
                assert os.path.isfile(ss_path)

                # Verify spritesheet dimensions
                with Image.open(ss_path) as sheet:
                    assert sheet.size == (64, 64)

                # Check frame coordinates
                assert result["frames"][0].x == 0
                assert result["frames"][0].y == 0
                assert result["frames"][1].x == 32
                assert result["frames"][1].y == 0
                assert result["frames"][2].x == 0
                assert result["frames"][2].y == 32
                assert result["frames"][3].x == 32
                assert result["frames"][3].y == 32

                # Check metadata JSON exists and is valid
                meta_fname = os.path.basename(result["metadata_url"])
                meta_path = os.path.join(tmpdir, meta_fname)
                assert os.path.isfile(meta_path)
                with open(meta_path) as fh:
                    meta = json.load(fh)
                assert meta["animation_name"] == "walk"
                assert meta["frame_count"] == 4
                assert meta["fps"] == 10
                assert "animations" in meta
                assert "walk" in meta["animations"]

    def test_3_frames_single_row(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(ss, "OUTPUT_DIR", tmpdir):
                aids = []
                for i in range(3):
                    name = f"f{i}"
                    _save_png(_solid_img(16, 16), tmpdir, name)
                    aids.append(name)

                result = ss.build_spritesheet(
                    asset_ids=aids,
                    animation_name="idle",
                    frame_width=32,
                    frame_height=32,
                    columns=4,
                )

                assert result["spritesheet_size"] == [128, 32]
                assert result["frame_count"] == 3
                # 3 frames in 4 columns → 1 row
                assert len(result["frames"]) == 3

    def test_missing_asset_raises(self):
        with pytest.raises(FileNotFoundError):
            ss.build_spritesheet(
                asset_ids=["no-such-id"],
                animation_name="x",
                frame_width=32,
                frame_height=32,
                columns=4,
            )

    def test_metadata_json_has_animation_range(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(ss, "OUTPUT_DIR", tmpdir):
                name = "single"
                _save_png(_solid_img(32, 32), tmpdir, name)

                result = ss.build_spritesheet(
                    asset_ids=[name],
                    animation_name="idle",
                    frame_width=32,
                    frame_height=32,
                    columns=1,
                )

                mfname = os.path.basename(result["metadata_url"])
                meta_path = os.path.join(tmpdir, mfname)
                with open(meta_path) as fh:
                    meta = json.load(fh)
                assert meta["animations"]["idle"] == {
                    "from": 0,
                    "to": 0,
                    "fps": 12,
                }
