"""
Asset generation service — orchestrates the generation pipeline.

In DEMO mode, copies sample assets into the output directory.  When a
real AI provider is available it will be called instead (future PR).
"""

from __future__ import annotations

import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import DEMO_MODE, OUTPUT_DIR
from app.models.schemas import (
    AssetMetadata,
    AssetType,
    GeneratedAsset,
    GenerateRequest,
    TaskStatus,
)
from app.utils.demo_provider import resolve_sample_path


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
        **fields,
    }


def get_task(task_id: str) -> Optional[dict]:
    return _TASKS.get(task_id)


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

def run_generation(req: GenerateRequest) -> str:
    """Create a task and begin generation.  Returns the task_id immediately."""
    task_id = str(uuid.uuid4())
    _store_task(task_id, status=TaskStatus.PENDING)

    if DEMO_MODE:
        _run_demo(task_id, req)
    else:
        _store_task(task_id, status=TaskStatus.GENERATING)
        # AI provider integration goes here (future PR)

    return task_id


def _run_demo(task_id: str, req: GenerateRequest) -> None:
    """Copy matching sample assets as the generation result."""
    task = _TASKS[task_id]
    task["status"] = TaskStatus.GENERATING

    sample_path = resolve_sample_path(req.asset_type, req.size)
    if sample_path is None:
        task["status"] = TaskStatus.FAILED
        task["error"] = (
            f"No sample asset found for type={req.asset_type.value} "
            f"size={req.size.value}"
        )
        return

    assets: list[GeneratedAsset] = []
    for i in range(req.count):
        asset_id = str(uuid.uuid4())
        name = f"{req.asset_type.value}_{req.size.value}x{req.size.value}_{i+1}"
        ext = sample_path.suffix

        # Copy to output directory so it's served as static
        dest_name = f"{asset_id}{ext}"
        dest = Path(OUTPUT_DIR) / dest_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(sample_path), str(dest))

        image_url = f"/output/{dest_name}"
        assets.append(
            GeneratedAsset(
                id=asset_id,
                name=name,
                type=req.asset_type,
                width=req.size.value,
                height=req.size.value,
                image_url=image_url,
                metadata=AssetMetadata(
                    prompt=req.prompt,
                    generated_at=datetime.now(timezone.utc),
                    generation_mode="demo",
                ),
            )
        )

    task["status"] = TaskStatus.READY
    task["assets"] = [a.model_dump() for a in assets]
    task["progress"] = f"{len(assets)}/{req.count} assets generated (demo)"
