"""Image post‑processing endpoints."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.schemas import ErrorResponse, TrimRequest, TrimResponse
from app.services.processor import run_trim

router = APIRouter(prefix="/api", tags=["process"])


@router.post(
    "/process/trim",
    response_model=TrimResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Trim transparent edges from an asset",
)
def trim_asset(req: TrimRequest) -> TrimResponse:
    """Crop transparent borders from a previously generated asset.

    The trimmed version is saved alongside the original in ``/output/``
    with a ``_trimmed`` suffix.
    """
    result = run_trim(req.asset_id)
    if result is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "ASSET_NOT_FOUND",
                    "message": f"No asset found with id '{req.asset_id}'",
                }
            },
        )
    return TrimResponse(**result)
