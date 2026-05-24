"""Tests for database provider selection and fallback logic."""

import os
import sqlite3
import tempfile

import pytest


@pytest.fixture(autouse=True)
def _reset_provider():
    """Reset cached provider between tests."""
    from app.services.database import reset_database_provider
    reset_database_provider()
    yield
    reset_database_provider()


class TestGetDatabaseProvider:
    def test_sqlite_forced(self):
        import app.config as cfg
        from app.services.database import get_database_provider, reset_database_provider

        orig = cfg.DATABASE_PROVIDER
        try:
            cfg.DATABASE_PROVIDER = "sqlite"
            reset_database_provider()
            assert get_database_provider() == "sqlite"
        finally:
            cfg.DATABASE_PROVIDER = orig

    def test_auto_falls_back_to_sqlite_when_postgres_unavailable(self):
        import app.config as cfg
        from app.services.database import get_database_provider, reset_database_provider

        orig_provider = cfg.DATABASE_PROVIDER
        orig_host = cfg.POSTGRES_HOST
        try:
            cfg.DATABASE_PROVIDER = "auto"
            cfg.POSTGRES_HOST = "255.255.255.255"  # non-routable, will timeout
            reset_database_provider()
            assert get_database_provider() == "sqlite"
        finally:
            cfg.DATABASE_PROVIDER = orig_provider
            cfg.POSTGRES_HOST = orig_host


class TestGetDbConnection:
    def test_sqlite_connection(self):
        import app.config as cfg
        from app.services.database import get_db_connection, reset_database_provider

        tmpdir = tempfile.mkdtemp(prefix="spriteforge_db_test_")
        db_path = os.path.join(tmpdir, "test.db")

        orig_provider = cfg.DATABASE_PROVIDER
        orig_path = cfg.SQLITE_DB_PATH
        try:
            cfg.DATABASE_PROVIDER = "sqlite"
            cfg.SQLITE_DB_PATH = db_path
            reset_database_provider()

            conn = get_db_connection()
            assert isinstance(conn, sqlite3.Connection)
            conn.close()
        finally:
            cfg.DATABASE_PROVIDER = orig_provider
            cfg.SQLITE_DB_PATH = orig_path


class TestActiveDatabaseInfo:
    def test_sqlite_info(self):
        import app.config as cfg
        from app.services.database import get_active_database_info, reset_database_provider

        orig = cfg.DATABASE_PROVIDER
        try:
            cfg.DATABASE_PROVIDER = "sqlite"
            reset_database_provider()
            info = get_active_database_info()
            assert info["provider"] == "sqlite"
            assert "path" in info
        finally:
            cfg.DATABASE_PROVIDER = orig


class TestFallbackFlag:
    def test_auto_fallback_sets_flag(self):
        import app.config as cfg
        from app.services.database import get_active_database_info, reset_database_provider

        orig_provider = cfg.DATABASE_PROVIDER
        orig_host = cfg.POSTGRES_HOST
        try:
            cfg.DATABASE_PROVIDER = "auto"
            cfg.POSTGRES_HOST = "255.255.255.255"
            reset_database_provider()
            info = get_active_database_info()
            assert info["provider"] == "sqlite"
            assert info["fallback"] is True
        finally:
            cfg.DATABASE_PROVIDER = orig_provider
            cfg.POSTGRES_HOST = orig_host


class TestRepositoryWithProvider:
    """Verify CRUD works through the repository regardless of provider."""

    def test_init_db_and_save(self):
        import app.config as cfg
        from app.services.asset_repository import (
            init_db,
            list_generated_assets,
            save_generated_asset,
        )
        from app.services.database import reset_database_provider

        tmpdir = tempfile.mkdtemp(prefix="spriteforge_int_test_")
        db_path = os.path.join(tmpdir, "test.db")

        orig_provider = cfg.DATABASE_PROVIDER
        orig_path = cfg.SQLITE_DB_PATH
        try:
            cfg.DATABASE_PROVIDER = "sqlite"
            cfg.SQLITE_DB_PATH = db_path
            reset_database_provider()

            init_db()
            assert os.path.isfile(db_path)

            from app.models.schemas import (
                ArtStyle,
                AssetMetadata,
                AssetType,
                EngineType,
                GenerateRequest,
                GeneratedAsset,
                PixelSize,
            )

            req = GenerateRequest(
                project_name="test-proj",
                asset_type=AssetType.ITEM,
                prompt="a sword",
                style=ArtStyle.PIXEL_ART,
                size=PixelSize.S32,
                count=1,
                target_engine=EngineType.GENERIC,
                transparent_background=True,
                generation_provider="demo",
            )
            asset = GeneratedAsset(
                id="int-001",
                name="sword_32x32_1",
                type=AssetType.ITEM,
                width=32,
                height=32,
                image_url="/output/sword.png",
                metadata=AssetMetadata(
                    prompt="a sword",
                    generation_mode="demo",
                    provider="demo",
                ),
            )
            save_generated_asset(asset, req, "task-int")

            records = list_generated_assets()
            assert len(records) == 1
            assert records[0]["id"] == "int-001"
            assert records[0]["asset_type"] == "item"
            assert records[0]["metadata"]["provider"] == "demo"
        finally:
            cfg.DATABASE_PROVIDER = orig_provider
            cfg.SQLITE_DB_PATH = orig_path
            reset_database_provider()
