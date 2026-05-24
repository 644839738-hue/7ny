"""Asset history API endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import AssetListResponse, AssetRecord
from app.services.asset_repository import (
    count_generated_assets,
    delete_generated_asset,
    get_generated_asset,
    list_generated_assets,
)

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.get("", response_model=AssetListResponse)
def list_assets(
    asset_type: Optional[str] = Query(None, description="Filter: character | item | tile | ui"),
    project_name: Optional[str] = Query(None, description="Filter by project name"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> AssetListResponse:
    items = list_generated_assets(
        asset_type=asset_type,
        project_name=project_name,
        limit=limit,
        offset=offset,
    )
    total = count_generated_assets(
        asset_type=asset_type,
        project_name=project_name,
    )
    return AssetListResponse(
        items=[AssetRecord(**item) for item in items],
        total=total,
    )


@router.get("/{asset_id}", response_model=AssetRecord)
def get_asset(asset_id: str) -> AssetRecord:
    record = get_generated_asset(asset_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetRecord(**record)


@router.delete("/{asset_id}")
def delete_asset(asset_id: str) -> dict:
    deleted = delete_generated_asset(asset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"ok": True}
