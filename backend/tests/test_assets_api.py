"""Integration tests for the asset history API endpoints."""

import os
import sqlite3
import tempfile

import pytest

# ---------------------------------------------------------------------------
# Set up isolated database BEFORE importing the app
# ---------------------------------------------------------------------------
_TMPDIR = tempfile.mkdtemp(prefix="spriteforge_api_test_")
_DB_PATH = os.path.join(_TMPDIR, "test.db")

import app.services.asset_repository as repo_mod  # noqa: E402

_orig_db_path = repo_mod.DB_PATH
_orig_data_dir = repo_mod.DATA_DIR
repo_mod.DB_PATH = _DB_PATH
repo_mod.DATA_DIR = _TMPDIR
repo_mod.init_db()

# Now safe to import the app (routers will use the patched module)
from app.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def _fresh_db():
    """Clear database contents between tests."""
    yield
    conn = sqlite3.connect(_DB_PATH)
    conn.execute("DELETE FROM generated_assets")
    conn.commit()
    conn.close()


def _seed_one():
    """Insert a single test record directly into the DB."""
    conn = sqlite3.connect(_DB_PATH)
    conn.execute(
        """INSERT INTO generated_assets
           (id, task_id, project_name, asset_type, name, prompt, style, size,
            target_engine, provider, image_url, local_path, metadata_json, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "seed-001", "task-seed", "test-proj", "item", "gold_sword_32x32_1",
            "a golden sword", "pixel_art", 32, "godot", "wanxiang",
            "/output/test.png", "", '{"provider":"wanxiang"}',
            "2025-01-01T00:00:00Z",
        ),
    )
    conn.commit()
    conn.close()


class TestListAssets:
    def test_empty(self):
        resp = client.get("/api/assets")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_with_data(self):
        _seed_one()
        resp = client.get("/api/assets")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == "seed-001"
        assert data["items"][0]["provider"] == "wanxiang"
        assert data["items"][0]["metadata"]["provider"] == "wanxiang"

    def test_filter_by_asset_type(self):
        _seed_one()
        resp = client.get("/api/assets?asset_type=character")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

        resp = client.get("/api/assets?asset_type=item")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    def test_filter_by_project_name(self):
        _seed_one()
        resp = client.get("/api/assets?project_name=other")
        assert resp.json()["total"] == 0

        resp = client.get("/api/assets?project_name=test-proj")
        assert resp.json()["total"] == 1


class TestGetAsset:
    def test_existing(self):
        _seed_one()
        resp = client.get("/api/assets/seed-001")
        assert resp.status_code == 200
        assert resp.json()["id"] == "seed-001"

    def test_missing(self):
        resp = client.get("/api/assets/no-such-id")
        assert resp.status_code == 404


class TestDeleteAsset:
    def test_delete_existing(self):
        _seed_one()
        resp = client.delete("/api/assets/seed-001")
        assert resp.status_code == 200
        assert resp.json() == {"ok": True}

        resp = client.get("/api/assets/seed-001")
        assert resp.status_code == 404

    def test_delete_missing(self):
        resp = client.delete("/api/assets/no-such-id")
        assert resp.status_code == 404
