"""Export endpoints."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.schemas import (
    ErrorResponse,
    ExportRequest,
    ExportResponse,
)
from app.services import export_service

router = APIRouter(prefix="/api", tags=["export"])


@router.post(
    "/export",
    response_model=ExportResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Export assets as a ZIP package for a target engine",
)
def export_assets(req: ExportRequest) -> ExportResponse:
    """Bundle selected assets, sprite-sheets, and tile previews into a
    ZIP archive with engine-specific import instructions."""
    try:
        result = export_service.build_export(
            project_name=req.project_name,
            asset_ids=req.asset_ids,
            engine=req.engine,
            include_spritesheet=req.include_spritesheet,
            include_metadata=req.include_metadata,
            include_tile_preview=req.include_tile_preview,
        )
    except Exception as exc:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "EXPORT_FAILED", "message": str(exc)}},
        )
    return ExportResponse(**result)
