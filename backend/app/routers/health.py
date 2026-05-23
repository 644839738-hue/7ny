"""Health-check endpoint."""

from fastapi import APIRouter

from app.config import DEMO_MODE
from app.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return service status and configuration mode."""
    return HealthResponse(demo_mode=DEMO_MODE)
