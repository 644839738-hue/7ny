"""
Asset repository — dual SQLite / PostgreSQL persistence.

Uses ``database.get_database_provider()`` to decide which backend to use.
SQLite and PostgreSQL DDL / DML are kept inline to avoid ORM dependencies.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from app.models.schemas import GenerateRequest, GeneratedAsset
from app.services.database import get_db_connection, get_database_provider

logger = logging.getLogger(__name__)

DDL_SQLITE = """
CREATE TABLE IF NOT EXISTS generated_assets (
    id              TEXT PRIMARY KEY,
    task_id         TEXT,
    project_name    TEXT NOT NULL,
    asset_type      TEXT NOT NULL,
    name            TEXT NOT NULL,
    prompt          TEXT NOT NULL DEFAULT '',
    style           TEXT NOT NULL DEFAULT '',
    size            INTEGER NOT NULL DEFAULT 32,
    target_engine   TEXT NOT NULL DEFAULT 'generic',
    provider        TEXT NOT NULL DEFAULT 'unknown',
    image_url       TEXT NOT NULL DEFAULT '',
    local_path      TEXT NOT NULL DEFAULT '',
    metadata_json   TEXT NOT NULL DEFAULT '{}',
    created_at      TEXT NOT NULL DEFAULT ''
)
"""

DDL_POSTGRES = """
CREATE TABLE IF NOT EXISTS generated_assets (
    id              TEXT PRIMARY KEY,
    task_id         TEXT,
    project_name    TEXT NOT NULL,
    asset_type      TEXT NOT NULL,
    name            TEXT NOT NULL,
    prompt          TEXT NOT NULL DEFAULT '',
    style           TEXT NOT NULL DEFAULT '',
    size            INTEGER NOT NULL DEFAULT 32,
    target_engine   TEXT NOT NULL DEFAULT 'generic',
    provider        TEXT NOT NULL DEFAULT 'unknown',
    image_url       TEXT NOT NULL DEFAULT '',
    local_path      TEXT NOT NULL DEFAULT '',
    metadata_json   TEXT NOT NULL DEFAULT '{}',
    created_at      TEXT NOT NULL DEFAULT ''
)
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_postgres() -> bool:
    return get_database_provider() == "postgres"


def _placeholder() -> str:
    return "%s" if _is_postgres() else "?"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def init_db() -> None:
    """Create the generated_assets table if it does not exist."""
    provider = get_database_provider()
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        ddl = DDL_POSTGRES if _is_postgres() else DDL_SQLITE
        cur.execute(ddl)
        conn.commit()

        if provider == "postgres":
            info = getattr(conn, "info", None)
            if info:
                logger.info("Database initialised: PostgreSQL %s:%s/%s",
                            info.host, info.port, info.dbname)
            else:
                logger.info("Database initialised: PostgreSQL")
        else:
            from app.config import SQLITE_DB_PATH
            logger.info("Database initialised at %s", SQLITE_DB_PATH)
    finally:
        conn.close()


def save_generated_asset(
    asset: GeneratedAsset,
    request: GenerateRequest,
    task_id: str,
) -> None:
    """Persist a single generated asset record."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        metadata = asset.metadata.model_dump() if asset.metadata else {}
        metadata_json = json.dumps(metadata, default=str, ensure_ascii=False)
        provider_val = getattr(asset.metadata, "provider", None) or "unknown"

        if _is_postgres():
            sql = """
                INSERT INTO generated_assets
                    (id, task_id, project_name, asset_type, name, prompt, style, size,
                     target_engine, provider, image_url, local_path, metadata_json, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    task_id = EXCLUDED.task_id,
                    project_name = EXCLUDED.project_name,
                    asset_type = EXCLUDED.asset_type,
                    name = EXCLUDED.name,
                    prompt = EXCLUDED.prompt,
                    style = EXCLUDED.style,
                    size = EXCLUDED.size,
                    target_engine = EXCLUDED.target_engine,
                    provider = EXCLUDED.provider,
                    image_url = EXCLUDED.image_url,
                    local_path = EXCLUDED.local_path,
                    metadata_json = EXCLUDED.metadata_json,
                    created_at = EXCLUDED.created_at
            """
        else:
            sql = """
                INSERT OR REPLACE INTO generated_assets
                    (id, task_id, project_name, asset_type, name, prompt, style, size,
                     target_engine, provider, image_url, local_path, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

        cur.execute(sql, (
            asset.id,
            task_id,
            request.project_name,
            request.asset_type.value if hasattr(request.asset_type, "value") else str(request.asset_type),
            asset.name,
            request.prompt,
            request.style.value if hasattr(request.style, "value") else str(request.style),
            request.size.value if hasattr(request.size, "value") else int(request.size),
            request.target_engine.value if hasattr(request.target_engine, "value") else str(request.target_engine),
            str(provider_val),
            asset.image_url,
            "",
            metadata_json,
            _now(),
        ))
        conn.commit()
        logger.debug("Saved asset %s to database", asset.id)
    except Exception:
        logger.warning("Failed to save asset %s to database", asset.id, exc_info=True)
    finally:
        conn.close()


def list_generated_assets(
    asset_type: Optional[str] = None,
    project_name: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """Return asset records, newest first, with optional filters."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        ph = _placeholder()
        where: list[str] = []
        params: list = []

        if asset_type:
            where.append(f"asset_type = {ph}")
            params.append(asset_type)
        if project_name:
            where.append(f"project_name = {ph}")
            params.append(project_name)

        clause = f"WHERE {' AND '.join(where)}" if where else ""
        sql = f"SELECT * FROM generated_assets {clause} ORDER BY created_at DESC LIMIT {ph} OFFSET {ph}"
        params.extend([limit, offset])

        cur.execute(sql, params)
        rows = cur.fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def count_generated_assets(
    asset_type: Optional[str] = None,
    project_name: Optional[str] = None,
) -> int:
    """Return total count of records matching the given filters."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        ph = _placeholder()
        where: list[str] = []
        params: list = []

        if asset_type:
            where.append(f"asset_type = {ph}")
            params.append(asset_type)
        if project_name:
            where.append(f"project_name = {ph}")
            params.append(project_name)

        clause = f"WHERE {' AND '.join(where)}" if where else ""
        cur.execute(f"SELECT COUNT(*) FROM generated_assets {clause}", params)
        row = cur.fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()


def get_generated_asset(asset_id: str) -> Optional[dict]:
    """Return a single asset record by id, or None."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        ph = _placeholder()
        cur.execute(f"SELECT * FROM generated_assets WHERE id = {ph}", (asset_id,))
        row = cur.fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()


def delete_generated_asset(asset_id: str) -> bool:
    """Delete a database record. Does NOT delete the image file. Returns True if deleted."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        ph = _placeholder()
        cur.execute(f"DELETE FROM generated_assets WHERE id = {ph}", (asset_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _row_to_dict(row) -> dict:
    """Convert a database row (sqlite3.Row or psycopg2 tuple) to a dict."""
    if row is None:
        return {}

    # psycopg2 returns real tuples — convert via cursor.description
    if isinstance(row, tuple):
        # attempt to get column names from row description set by caller
        # if we have a tuple, convert by position
        return {
            "id": row[0] if len(row) > 0 else "",
            "task_id": row[1] if len(row) > 1 else None,
            "project_name": row[2] if len(row) > 2 else "",
            "asset_type": row[3] if len(row) > 3 else "",
            "name": row[4] if len(row) > 4 else "",
            "prompt": row[5] if len(row) > 5 else "",
            "style": row[6] if len(row) > 6 else "",
            "size": row[7] if len(row) > 7 else 32,
            "target_engine": row[8] if len(row) > 8 else "",
            "provider": row[9] if len(row) > 9 else "",
            "image_url": row[10] if len(row) > 10 else "",
            "local_path": row[11] if len(row) > 11 else "",
            "metadata_json": row[12] if len(row) > 12 else "{}",
            "created_at": row[13] if len(row) > 13 else "",
            "metadata": {},
        }

    # sqlite3.Row or psycopg2.extras.RealDictRow are dict-like
    try:
        d = dict(row)
    except (TypeError, ValueError):
        return {}

    if d.get("metadata_json"):
        try:
            d["metadata"] = json.loads(d["metadata_json"])
        except json.JSONDecodeError:
            d["metadata"] = {}
    else:
        d["metadata"] = {}
    return d
