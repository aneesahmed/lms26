from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models.asset import Asset
from app.services.auth import require_role

router = APIRouter(prefix="/asset", tags=["Asset"])

class AssetCreate(BaseModel):
    name: str
    type: str # BUILDING, FLOOR, CLASSROOM, GROUND
    parent_id: Optional[int] = None
    org_id: Optional[int] = None
    capacity: Optional[int] = None
    status: Optional[str] = "ACTIVE"

class AssetResponse(BaseModel):
    id: int
    name: str
    type: str
    parent_id: Optional[int]
    org_id: Optional[int]
    capacity: Optional[int]
    status: str

    class Config:
        from_attributes = True

@router.post("/", response_model=AssetResponse)
async def create_asset(
    asset: AssetCreate,
    db: AsyncSession = Depends(get_db),
    _current=Depends(require_role("ADMIN")),
):
    db_asset = Asset(**asset.dict())
    db.add(db_asset)
    await db.commit()
    await db.refresh(db_asset)
    return db_asset

@router.get("/", response_model=List[AssetResponse])
async def list_assets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset))
    return result.scalars().all()

@router.get("/{asset_id}/children", response_model=List[AssetResponse])
async def get_asset_children(asset_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset).where(Asset.parent_id == asset_id))
    return result.scalars().all()
