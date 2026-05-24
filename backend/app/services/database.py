"""
Database provider with PostgreSQL priority and SQLite fallback.

Supports three DATABASE_PROVIDER modes:
- ``auto``: try PostgreSQL first, fall back to SQLite
- ``postgres``: require PostgreSQL, fail if unavailable
- ``sqlite``: force SQLite

All config values are read dynamically from ``app.config`` so that tests
can monkeypatch them at runtime.
"""

from __future__ import annotations

import logging
from typing import Any

import app.config as _cfg

logger = logging.getLogger(__name__)

_ACTIVE_PROVIDER: str = ""
_FALLBACK: bool = False


def get_database_provider() -> str:
    """Return the active provider name (``sqlite`` or ``postgres``)."""
    global _ACTIVE_PROVIDER, _FALLBACK

    if _ACTIVE_PROVIDER:
        return _ACTIVE_PROVIDER

    if _cfg.DATABASE_PROVIDER == "sqlite":
        _ACTIVE_PROVIDER = "sqlite"
        _FALLBACK = False
    elif _cfg.DATABASE_PROVIDER == "postgres":
        if not test_postgres_connection():
            raise RuntimeError(
                "DATABASE_PROVIDER=postgres but PostgreSQL is unreachable "
                f"at {_cfg.POSTGRES_HOST}:{_cfg.POSTGRES_PORT}/{_cfg.POSTGRES_DB}"
            )
        _ACTIVE_PROVIDER = "postgres"
        _FALLBACK = False
    else:  # auto
        if test_postgres_connection():
            _ACTIVE_PROVIDER = "postgres"
            _FALLBACK = False
            logger.info("PostgreSQL available, using postgres")
        else:
            _ACTIVE_PROVIDER = "sqlite"
            _FALLBACK = True
            logger.info("PostgreSQL not available, falling back to SQLite")

    return _ACTIVE_PROVIDER


def test_postgres_connection() -> bool:
    """Try connecting to PostgreSQL.  Returns True on success, False otherwise."""
    try:
        import psycopg2

        conn = psycopg2.connect(
            host=_cfg.POSTGRES_HOST,
            port=_cfg.POSTGRES_PORT,
            dbname=_cfg.POSTGRES_DB,
            user=_cfg.POSTGRES_USER,
            password=_cfg.POSTGRES_PASSWORD,
            sslmode=_cfg.POSTGRES_SSLMODE,
            connect_timeout=3,
        )
        conn.close()
        return True
    except Exception:
        logger.debug("PostgreSQL connection test failed", exc_info=True)
        return False


def get_db_connection():
    """Return a connection object for the active database provider."""
    provider = get_database_provider()

    if provider == "postgres":
        import psycopg2

        return psycopg2.connect(
            host=_cfg.POSTGRES_HOST,
            port=_cfg.POSTGRES_PORT,
            dbname=_cfg.POSTGRES_DB,
            user=_cfg.POSTGRES_USER,
            password=_cfg.POSTGRES_PASSWORD,
            sslmode=_cfg.POSTGRES_SSLMODE,
        )

    # sqlite
    import os
    import sqlite3

    db_dir = os.path.dirname(_cfg.SQLITE_DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(_cfg.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def get_active_database_info() -> dict[str, Any]:
    """Return metadata about the currently active database."""
    provider = get_database_provider()

    if provider == "postgres":
        return {
            "provider": "postgres",
            "fallback": _FALLBACK,
            "host": _cfg.POSTGRES_HOST,
            "database": _cfg.POSTGRES_DB,
            "path": None,
        }

    return {
        "provider": "sqlite",
        "fallback": _FALLBACK,
        "host": None,
        "database": None,
        "path": _cfg.SQLITE_DB_PATH,
    }


def reset_database_provider() -> None:
    """Reset cached provider (used in tests)."""
    global _ACTIVE_PROVIDER, _FALLBACK
    _ACTIVE_PROVIDER = ""
    _FALLBACK = False
