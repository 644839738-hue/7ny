"""Sprite-sheet endpoints."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.schemas import (
    ErrorResponse,
    SpriteSheetRequest,
    SpriteSheetResponse,
)
from app.services import spritesheet as ss_service

router = APIRouter(prefix="/api", tags=["spritesheet"])


@router.post(
    "/spritesheet",
    response_model=SpriteSheetResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Build a sprite-sheet from generated assets",
)
def create_spritesheet(req: SpriteSheetRequest) -> SpriteSheetResponse:
    """Stitch multiple asset frames into a single sprite-sheet image.

    Frames are laid out left-to-right, top-to-bottom in the specified number
    of *columns*.  A JSON metadata file is generated alongside the image.
    """
    try:
        result = ss_service.build_spritesheet(
            asset_ids=req.asset_ids,
            animation_name=req.animation_name,
            frame_width=req.frame_width,
            frame_height=req.frame_height,
            columns=req.columns,
            fps=req.fps,
        )
    except FileNotFoundError as exc:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "ASSET_NOT_FOUND", "message": str(exc)}},
        )
    return SpriteSheetResponse(**result)
