"""Health-check and runtime-config endpoints."""

from fastapi import APIRouter

from app.config import DEMO_MODE, IMAGE_PROVIDER
from app.models.schemas import HealthResponse, RuntimeConfigResponse

router = APIRouter(tags=["health"])


def _resolve_provider_label() -> str:
    """Return a human-readable label for the current generation backend."""
    if DEMO_MODE:
        return "Demo 内置素材"
    if IMAGE_PROVIDER == "wanxiang":
        return "通义万相 AI 生成"
    return f"External ({IMAGE_PROVIDER})"


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return service status and configuration mode."""
    return HealthResponse(demo_mode=DEMO_MODE)


@router.get(
    "/api/runtime-config",
    response_model=RuntimeConfigResponse,
    summary="Return backend runtime generation mode",
)
def runtime_config() -> RuntimeConfigResponse:
    """Frontend uses this to display the real backend generation mode.

    The generation mode is controlled by ``backend/.env`` — the frontend
    does **not** have the ability to switch modes.
    """
    return RuntimeConfigResponse(
        demo_mode=DEMO_MODE,
        image_provider="demo" if DEMO_MODE else IMAGE_PROVIDER,
        ai_enabled=not DEMO_MODE and IMAGE_PROVIDER != "demo",
        provider_label=_resolve_provider_label(),
    )
