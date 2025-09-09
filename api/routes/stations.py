"""
Station-related API endpoints.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.models import Station
from ..dependencies import get_db

router = APIRouter()


@router.get("/", response_model=List[Station])
async def get_stations(db: Session = Depends(get_db)):
    """Get all stations."""
    # This would use the actual repository implementation
    return []


@router.get("/{station_id}", response_model=Station)
async def get_station(station_id: UUID, db: Session = Depends(get_db)):
    """Get a specific station by ID."""
    # This would use the actual repository implementation
    raise HTTPException(status_code=404, detail="Station not found")


@router.get("/code/{station_code}", response_model=Station)
async def get_station_by_code(station_code: str, db: Session = Depends(get_db)):
    """Get a station by its code."""
    # This would use the actual repository implementation
    raise HTTPException(status_code=404, detail="Station not found")
