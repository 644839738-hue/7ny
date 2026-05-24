"""
Asset generation orchestrator — manages generation tasks end-to-end.

Responsibilities
----------------
* Task lifecycle (create, store, update status)
* Delegating generation to :mod:`image_generation_service`
* Handling provider fallback warnings

This module does **not** contain image-generation logic itself — that
lives in :class:`image_generation_service.ImageGenerationProvider`.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.models.schemas import (
    GeneratedAsset,
    GenerateRequest,
    TaskStatus,
)
from app.services.image_generation_service import generate_assets

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# In-memory task store  (replaced by DB in a later PR)
# ---------------------------------------------------------------------------

_TASKS: dict[str, dict] = {}


def _store_task(task_id: str, **fields) -> None:
    _TASKS[task_id] = {
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "progress": "",
        "assets": [],
        "created_at": datetime.now(timezone.utc),
        "error": None,
        "warning": None,
        "provider": None,
        **fields,
    }


def get_task(task_id: str) -> Optional[dict]:
    return _TASKS.get(task_id)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_generation(req: GenerateRequest) -> str:
    """Create a task, run generation, return ``task_id``.

    Generation is currently **synchronous** (both demo and external stub
    complete in-process).  When a real async AI provider is added the call
    to ``generate_assets`` should be dispatched to a background worker.
    """
    task_id = str(uuid.uuid4())
    _store_task(task_id)

    task = _TASKS[task_id]
    task["status"] = TaskStatus.GENERATING

    try:
        result = generate_assets(req)
    except Exception as exc:
        task["status"] = TaskStatus.FAILED
        task["error"] = str(exc)
        return task_id

    task["status"] = TaskStatus.READY
    task["assets"] = [a.model_dump() for a in result.assets]
    task["progress"] = (
        f"{len(result.assets)}/{req.count} assets generated "
        f"({result.provider_used})"
    )
    task["provider"] = result.provider_used

    if result.fallback_occurred and result.warning:
        task["warning"] = result.warning

    # Persist assets to SQLite (best-effort; failure must not fail the task)
    _save_assets_to_db(result.assets, req, task_id)

    return task_id


def _save_assets_to_db(
    assets: list[GeneratedAsset],
    req: GenerateRequest,
    task_id: str,
) -> None:
    """Best-effort persistence of generated assets to SQLite."""
    try:
        from app.services.asset_repository import save_generated_asset

        for asset in assets:
            save_generated_asset(asset, req, task_id)
    except Exception:
        logger.warning(
            "Failed to persist assets for task %s to SQLite", task_id, exc_info=True
        )
