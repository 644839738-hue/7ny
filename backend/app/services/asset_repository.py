"""
SQLite repository for generated assets.

Provides CRUD operations over the ``generated_assets`` table stored in
``backend/data/spriteforge.db``.  Uses only Python stdlib ``sqlite3``.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import BASE_DIR
from app.models.schemas import GenerateRequest, GeneratedAsset

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(BASE_DIR, "..", "data", "spriteforge.db")
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

DDL = """
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


def _connect() -> sqlite3.Connection:
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def init_db() -> None:
    """Create database directory and table.  Safe to call repeatedly."""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = _connect()
    try:
        conn.execute(DDL)
        conn.commit()
        logger.info("Database initialised at %s", DB_PATH)
    finally:
        conn.close()


def save_generated_asset(
    asset: GeneratedAsset,
    request: GenerateRequest,
    task_id: str,
) -> None:
    """Persist a single generated asset record."""
    conn = _connect()
    try:
        metadata = asset.metadata.model_dump() if asset.metadata else {}
        metadata_json = json.dumps(metadata, default=str, ensure_ascii=False)

        provider = getattr(asset.metadata, "provider", None) or "unknown"

        conn.execute(
            """INSERT OR REPLACE INTO generated_assets
               (id, task_id, project_name, asset_type, name, prompt, style, size,
                target_engine, provider, image_url, local_path, metadata_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                asset.id,
                task_id,
                request.project_name,
                request.asset_type.value if hasattr(request.asset_type, "value") else str(request.asset_type),
                asset.name,
                request.prompt,
                request.style.value if hasattr(request.style, "value") else str(request.style),
                request.size.value if hasattr(request.size, "value") else int(request.size),
                request.target_engine.value if hasattr(request.target_engine, "value") else str(request.target_engine),
                str(provider),
                asset.image_url,
                "",  # local_path — populated when we track local files
                metadata_json,
                _now(),
            ),
        )
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
    conn = _connect()
    try:
        where: list[str] = []
        params: list = []

        if asset_type:
            where.append("asset_type = ?")
            params.append(asset_type)
        if project_name:
            where.append("project_name = ?")
            params.append(project_name)

        clause = f"WHERE {' AND '.join(where)}" if where else ""
        sql = f"SELECT * FROM generated_assets {clause} ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(sql, params).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def count_generated_assets(
    asset_type: Optional[str] = None,
    project_name: Optional[str] = None,
) -> int:
    """Return total count of records matching the given filters."""
    conn = _connect()
    try:
        where: list[str] = []
        params: list = []
        if asset_type:
            where.append("asset_type = ?")
            params.append(asset_type)
        if project_name:
            where.append("project_name = ?")
            params.append(project_name)

        clause = f"WHERE {' AND '.join(where)}" if where else ""
        row = conn.execute(f"SELECT COUNT(*) FROM generated_assets {clause}", params).fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()


def get_generated_asset(asset_id: str) -> Optional[dict]:
    """Return a single asset record by id, or None."""
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM generated_assets WHERE id = ?", (asset_id,)).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()


def delete_generated_asset(asset_id: str) -> bool:
    """Delete a database record.  Does NOT delete the image file.  Returns True if deleted."""
    conn = _connect()
    try:
        cursor = conn.execute("DELETE FROM generated_assets WHERE id = ?", (asset_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    if d.get("metadata_json"):
        try:
            d["metadata"] = json.loads(d["metadata_json"])
        except json.JSONDecodeError:
            d["metadata"] = {}
    else:
        d["metadata"] = {}
    return d
