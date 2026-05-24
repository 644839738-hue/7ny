"""Health-check and runtime-config endpoints."""

from fastapi import APIRouter

from app.config import DEMO_MODE, DASHSCOPE_API_KEY, IMAGE_PROVIDER
from app.models.schemas import HealthResponse, RuntimeConfigResponse

router = APIRouter(tags=["health"])

try:
    from app.services.wanxiang_image_provider import WanxiangImageProvider  # noqa: F401
    _WANXIANG_IMPORT_OK = True
except ImportError:
    _WANXIANG_IMPORT_OK = False


def _resolve_provider_label() -> str:
    """Return a human-readable provider label for the frontend."""
    if DEMO_MODE:
        return "Demo 内置素材"
    if IMAGE_PROVIDER == "wanxiang":
        return "通义万相 AI 生成"
    return f"External ({IMAGE_PROVIDER})"


def _wanxiang_configured() -> bool:
    """True when Wanxiang can actually be called (imports work + API key set)."""
    return _WANXIANG_IMPORT_OK and bool(DASHSCOPE_API_KEY)


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return service status and configuration mode."""
    return HealthResponse(demo_mode=DEMO_MODE)


@router.get("/api/runtime-config", response_model=RuntimeConfigResponse)
def runtime_config() -> RuntimeConfigResponse:
    """Return the actual backend provider status for the frontend."""
    return RuntimeConfigResponse(
        demo_mode=DEMO_MODE,
        image_provider=IMAGE_PROVIDER,
        ai_enabled=bool(DASHSCOPE_API_KEY),
        provider_label=_resolve_provider_label(),
        wanxiang_configured=_wanxiang_configured(),
    )
