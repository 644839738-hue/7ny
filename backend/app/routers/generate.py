"""Asset generation endpoints."""

from fastapi import APIRouter

from app.models.schemas import (
    ErrorResponse,
    GeneratedAsset,
    GenerateRequest,
    GenerateResponse,
    TaskStatus,
    TaskStatusResponse,
)
from app.services.generator import get_task, run_generation

router = APIRouter(prefix="/api", tags=["generate"])


@router.post(
    "/generate",
    response_model=GenerateResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Create asset generation task",
)
def create_generation(req: GenerateRequest) -> GenerateResponse:
    """Submit a generation request.  Returns a `task_id` immediately.

    Poll `GET /api/tasks/{task_id}` to check progress and retrieve results.
    In **DEMO mode** the task completes synchronously and is ready immediately.
    """
    task_id = run_generation(req)
    task = get_task(task_id)
    return GenerateResponse(
        task_id=task_id,
        status=task["status"] if task else TaskStatus.PENDING,
    )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskStatusResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Query generation task status",
)
def query_task(task_id: str) -> TaskStatusResponse:
    """Return the current status and (when ready) the generated assets."""
    task = get_task(task_id)
    if task is None:
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "TASK_NOT_FOUND",
                    "message": f"No task with id '{task_id}'",
                }
            },
        )

    return TaskStatusResponse(
        task_id=task["task_id"],
        status=task["status"],
        progress=task.get("progress", ""),
        assets=[GeneratedAsset(**a) for a in task.get("assets", [])],
        created_at=task.get("created_at"),
        error=task.get("error"),
    )
