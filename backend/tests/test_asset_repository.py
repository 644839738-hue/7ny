"""Unit tests for the SQLite asset repository."""

import os
import sqlite3
import tempfile

import pytest


@pytest.fixture
def repo():
    """Create a temporary database and patch the repository module to use it."""
    import app.services.asset_repository as repo_mod

    tmpdir = tempfile.mkdtemp(prefix="spriteforge_test_")
    db_path = os.path.join(tmpdir, "test.db")

    # Swap in temp paths
    _orig_db_path = repo_mod.DB_PATH
    _orig_data_dir = repo_mod.DATA_DIR
    repo_mod.DB_PATH = db_path
    repo_mod.DATA_DIR = tmpdir

    # Ensure fresh table
    os.makedirs(tmpdir, exist_ok=True)
    repo_mod.init_db()

    yield repo_mod

    # Clean up
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM generated_assets")
    conn.commit()
    conn.close()

    repo_mod.DB_PATH = _orig_db_path
    repo_mod.DATA_DIR = _orig_data_dir


# Convenience imports via fixture
@pytest.fixture
def svc(repo):
    """Return commonly-used functions from the patched module."""
    return repo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_request(repo, **overrides):
    from app.models.schemas import (
        ArtStyle,
        AssetType,
        EngineType,
        GenerateRequest,
        PixelSize,
    )

    defaults = {
        "project_name": "test-project",
        "asset_type": AssetType.ITEM,
        "prompt": "a golden sword",
        "style": ArtStyle.PIXEL_ART,
        "size": PixelSize.S32,
        "count": 1,
        "target_engine": EngineType.GODOT,
        "transparent_background": True,
        "generation_provider": "wanxiang",
    }
    defaults.update(overrides)
    return GenerateRequest(**defaults)


def _make_asset(repo, **overrides):
    from app.models.schemas import (
        AssetMetadata,
        AssetType,
        GeneratedAsset,
    )

    defaults = {
        "id": "asset-001",
        "name": "test_item_32x32_1",
        "type": AssetType.ITEM,
        "width": 32,
        "height": 32,
        "image_url": "/output/test.png",
        "metadata": AssetMetadata(
            prompt="a golden sword",
            generation_mode="ai",
            provider="wanxiang",
            model="wanx-v1",
            final_prompt="game item icon, a golden sword, ...",
        ),
    }
    defaults.update(overrides)
    return GeneratedAsset(**defaults)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestInitDb:
    def test_creates_db_file(self, repo):
        assert os.path.isfile(repo.DB_PATH)

    def test_idempotent(self, repo):
        repo.init_db()
        repo.init_db()


class TestSaveAndList:
    def test_save_and_list_one(self, repo):
        req = _make_request(repo)
        asset = _make_asset(repo)
        repo.save_generated_asset(asset, req, "task-1")

        items = repo.list_generated_assets()
        assert len(items) == 1
        assert items[0]["id"] == "asset-001"
        assert items[0]["asset_type"] == "item"
        assert items[0]["project_name"] == "test-project"
        assert items[0]["provider"] == "wanxiang"
        assert items[0]["metadata"]["provider"] == "wanxiang"

    def test_list_multiple(self, repo):
        for i in range(3):
            req = _make_request(repo, project_name=f"proj-{i}")
            asset = _make_asset(repo, id=f"asset-00{i}", name=f"item_{i}")
            repo.save_generated_asset(asset, req, f"task-{i}")

        items = repo.list_generated_assets()
        assert len(items) == 3

    def test_filter_by_asset_type(self, repo):
        from app.models.schemas import AssetType

        req_item = _make_request(repo, asset_type=AssetType.ITEM)
        req_char = _make_request(repo, asset_type=AssetType.CHARACTER)
        repo.save_generated_asset(_make_asset(repo, id="a1"), req_item, "t1")
        repo.save_generated_asset(_make_asset(repo, id="a2", type=AssetType.CHARACTER), req_char, "t2")

        items = repo.list_generated_assets(asset_type="item")
        assert len(items) == 1
        assert items[0]["id"] == "a1"

        items = repo.list_generated_assets(asset_type="character")
        assert len(items) == 1
        assert items[0]["id"] == "a2"

    def test_filter_by_project_name(self, repo):
        repo.save_generated_asset(_make_asset(repo, id="a1"), _make_request(repo, project_name="proj-a"), "t1")
        repo.save_generated_asset(_make_asset(repo, id="a2"), _make_request(repo, project_name="proj-b"), "t2")

        items = repo.list_generated_assets(project_name="proj-a")
        assert len(items) == 1
        assert items[0]["id"] == "a1"

    def test_pagination(self, repo):
        for i in range(5):
            repo.save_generated_asset(_make_asset(repo, id=f"a{i}"), _make_request(repo), f"t{i}")

        items = repo.list_generated_assets(limit=2, offset=1)
        assert len(items) == 2

    def test_count(self, repo):
        for i in range(3):
            repo.save_generated_asset(_make_asset(repo, id=f"a{i}"), _make_request(repo), f"t{i}")

        assert repo.count_generated_assets() == 3
        assert repo.count_generated_assets(asset_type="item") == 3
        assert repo.count_generated_assets(asset_type="character") == 0


class TestGetAndDelete:
    def test_get_existing(self, repo):
        repo.save_generated_asset(_make_asset(repo, id="find-me"), _make_request(repo), "t1")
        record = repo.get_generated_asset("find-me")
        assert record is not None
        assert record["id"] == "find-me"

    def test_get_missing(self, repo):
        assert repo.get_generated_asset("no-such-id") is None

    def test_delete_existing(self, repo):
        repo.save_generated_asset(_make_asset(repo, id="del-me"), _make_request(repo), "t1")
        assert repo.delete_generated_asset("del-me") is True
        assert repo.get_generated_asset("del-me") is None

    def test_delete_missing(self, repo):
        assert repo.delete_generated_asset("no-such-id") is False
