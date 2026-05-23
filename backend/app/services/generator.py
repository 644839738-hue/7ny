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

import uuid
from datetime import datetime, timezone
from typing import Optional

from app.config import DEMO_MODE
from app.models.schemas import (
    GeneratedAsset,
    GenerateRequest,
    TaskStatus,
)
from app.services.image_generation_service import generate_assets


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
        "provider": "demo" if DEMO_MODE else "external",
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

    return task_id
