"""Tile endpoints."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.schemas import (
    ErrorResponse,
    TilePreviewRequest,
    TilePreviewResponse,
    TileScoreRequest,
    TileScoreResponse,
)
from app.services import tile as tile_service
from app.services import tile_score as score_service

router = APIRouter(prefix="/api", tags=["tile"])


@router.post(
    "/tile/preview",
    response_model=TilePreviewResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Generate a 3×3 tiling preview for a tile asset",
)
def create_tile_preview(req: TilePreviewRequest) -> TilePreviewResponse:
    """Arrange a single tile asset into a 3×3 grid so the user can
    visually inspect how it tiles."""
    try:
        result = tile_service.build_tile_preview(asset_id=req.asset_id)
    except FileNotFoundError as exc:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "ASSET_NOT_FOUND", "message": str(exc)}},
        )
    return TilePreviewResponse(**result)


@router.post(
    "/tile/score",
    response_model=TileScoreResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Score a tile's edge consistency for seamless tiling",
)
def score_tile_edges(req: TileScoreRequest) -> TileScoreResponse:
    """Compare opposing edges (top/bottom, left/right) and return a
    0–100 consistency score with a human-readable suggestion."""
    try:
        result = score_service.score_tile(asset_id=req.asset_id)
    except FileNotFoundError as exc:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "ASSET_NOT_FOUND", "message": str(exc)}},
        )
    return TileScoreResponse(**result)
