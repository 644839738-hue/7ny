"""Unit tests for the export service."""

import io
import json
import os
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

import app.services.export_service as es
from app.models.schemas import EngineType


def _solid_png(w: int, h: int, dir_: str, stem: str) -> str:
    img = Image.new("RGBA", (w, h), (255, 0, 0, 255))
    path = Path(dir_) / f"{stem}.png"
    img.save(path, "PNG")
    return str(path)


class TestBuildExport:
    def test_basic_zip_structure(self):
        """Export of assets-only produces correct ZIP layout."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(es, "OUTPUT_DIR", tmpdir):
                # Create 2 fake assets
                _solid_png(32, 32, tmpdir, "asset_a")
                _solid_png(64, 64, tmpdir, "asset_b")

                result = es.build_export(
                    project_name="test-proj",
                    asset_ids=["asset_a", "asset_b"],
                    engine=EngineType.UNITY,
                    include_spritesheet=False,
                    include_tile_preview=False,
                )

                # Check response fields
                assert result["package_structure"]["engine"] == "unity"
                assert result["file_count"] == 4  # 2 images + manifest + README
                assert result["total_size_bytes"] > 0
                assert result["download_url"].startswith("/output/export_")
                assert result["download_url"].endswith(".zip")

                # Verify ZIP exists
                zip_fname = os.path.basename(result["download_url"])
                zip_path = os.path.join(tmpdir, zip_fname)
                assert os.path.isfile(zip_path)

                # Verify ZIP contents
                with zipfile.ZipFile(zip_path) as zf:
                    names = zf.namelist()
                    assert "images/asset_a.png" in names
                    assert "images/asset_b.png" in names
                    assert "manifest.json" in names
                    assert "README_IMPORT.md" in names
                    assert "spritesheets" not in str(names)
                    assert "tiles" not in str(names)

    def test_includes_spritesheets_when_present(self):
        """When spritesheet files exist they are included."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(es, "OUTPUT_DIR", tmpdir):
                _solid_png(32, 32, tmpdir, "asset_x")
                # Simulate a spritesheet file
                _solid_png(128, 64, tmpdir, "spritesheet_abc123")

                result = es.build_export(
                    project_name="p",
                    asset_ids=["asset_x"],
                    engine=EngineType.GODOT,
                    include_spritesheet=True,
                    include_tile_preview=False,
                )

                zip_fname = os.path.basename(result["download_url"])
                zip_path = os.path.join(tmpdir, zip_fname)
                with zipfile.ZipFile(zip_path) as zf:
                    names = zf.namelist()
                    assert "spritesheets/spritesheet_abc123.png" in names

    def test_includes_tile_previews_when_present(self):
        """When tile preview files exist they are included."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(es, "OUTPUT_DIR", tmpdir):
                _solid_png(32, 32, tmpdir, "tile_1")
                _solid_png(96, 96, tmpdir, "tile_preview_xyz")

                result = es.build_export(
                    project_name="p",
                    asset_ids=["tile_1"],
                    engine=EngineType.GENERIC,
                    include_tile_preview=True,
                    include_spritesheet=False,
                )

                zip_fname = os.path.basename(result["download_url"])
                zip_path = os.path.join(tmpdir, zip_fname)
                with zipfile.ZipFile(zip_path) as zf:
                    names = zf.namelist()
                    assert "tiles/tile_preview_xyz.png" in names

    def test_manifest_contents(self):
        """manifest.json contains correct project metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(es, "OUTPUT_DIR", tmpdir):
                _solid_png(32, 32, tmpdir, "asset_m")

                result = es.build_export(
                    project_name="my-manifest-test",
                    asset_ids=["asset_m"],
                    engine=EngineType.GODOT,
                    include_spritesheet=False,
                    include_tile_preview=False,
                )

                zip_fname = os.path.basename(result["download_url"])
                zip_path = os.path.join(tmpdir, zip_fname)
                with zipfile.ZipFile(zip_path) as zf:
                    with zf.open("manifest.json") as f:
                        manifest = json.load(io.TextIOWrapper(f, encoding="utf-8"))
                assert manifest["project_name"] == "my-manifest-test"
                assert manifest["target_engine"] == "godot"
                assert "exported_at" in manifest
                assert len(manifest["assets"]) == 1
                assert manifest["assets"][0]["id"] == "asset_m"

    def test_readme_unity(self):
        """Unity README contains engine-specific instructions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(es, "OUTPUT_DIR", tmpdir):
                _solid_png(32, 32, tmpdir, "a1")

                result = es.build_export(
                    project_name="p",
                    asset_ids=["a1"],
                    engine=EngineType.UNITY,
                    include_spritesheet=False,
                    include_tile_preview=False,
                )

                zip_fname = os.path.basename(result["download_url"])
                zip_path = os.path.join(tmpdir, zip_fname)
                with zipfile.ZipFile(zip_path) as zf:
                    with zf.open("README_IMPORT.md") as f:
                        text = f.read().decode("utf-8")
                assert "Unity" in text
                assert "Assets/Sprites/" in text
                assert "Filter Mode" in text

    def test_readme_godot(self):
        """Godot README contains engine-specific instructions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(es, "OUTPUT_DIR", tmpdir):
                _solid_png(32, 32, tmpdir, "a1")

                result = es.build_export(
                    project_name="p",
                    asset_ids=["a1"],
                    engine=EngineType.GODOT,
                    include_spritesheet=False,
                    include_tile_preview=False,
                )

                zip_fname = os.path.basename(result["download_url"])
                zip_path = os.path.join(tmpdir, zip_fname)
                with zipfile.ZipFile(zip_path) as zf:
                    with zf.open("README_IMPORT.md") as f:
                        text = f.read().decode("utf-8")
                assert "Godot" in text
                assert "assets/sprites/" in text

    def test_readme_generic(self):
        """Generic README contains multi-engine notes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(es, "OUTPUT_DIR", tmpdir):
                _solid_png(32, 32, tmpdir, "a1")

                result = es.build_export(
                    project_name="p",
                    asset_ids=["a1"],
                    engine=EngineType.GENERIC,
                    include_spritesheet=False,
                    include_tile_preview=False,
                )

                zip_fname = os.path.basename(result["download_url"])
                zip_path = os.path.join(tmpdir, zip_fname)
                with zipfile.ZipFile(zip_path) as zf:
                    with zf.open("README_IMPORT.md") as f:
                        text = f.read().decode("utf-8")
                assert "通用导入说明" in text
                assert "Unity" in text
                assert "Godot" in text

    def test_missing_assets_skipped_gracefully(self):
        """Asset IDs that don't exist are simply skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(es, "OUTPUT_DIR", tmpdir):
                _solid_png(32, 32, tmpdir, "real_asset")

                result = es.build_export(
                    project_name="p",
                    asset_ids=["real_asset", "no-such-id"],
                    engine=EngineType.UNITY,
                    include_spritesheet=False,
                    include_tile_preview=False,
                )

                zip_fname = os.path.basename(result["download_url"])
                zip_path = os.path.join(tmpdir, zip_fname)
                with zipfile.ZipFile(zip_path) as zf:
                    names = zf.namelist()
                    assert "images/real_asset.png" in names
                    assert "images/no-such-id" not in str(names)
