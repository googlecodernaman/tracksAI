"""
Train-related API endpoints.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.models import Train, TrainType, TrainStatus
from core.database import TrainRepository
from ..dependencies import get_db

router = APIRouter()


@router.get("/", response_model=List[Train])
async def get_trains(
    status: Optional[TrainStatus] = Query(None, description="Filter by train status"),
    train_type: Optional[TrainType] = Query(None, description="Filter by train type"),
    db: Session = Depends(get_db)
):
    """Get all trains with optional filtering."""
    # This would use the actual repository implementation
    # For now, return mock data
    return []


@router.get("/{train_id}", response_model=Train)
async def get_train(train_id: UUID, db: Session = Depends(get_db)):
    """Get a specific train by ID."""
    # This would use the actual repository implementation
    raise HTTPException(status_code=404, detail="Train not found")


@router.get("/number/{train_number}", response_model=Train)
async def get_train_by_number(train_number: str, db: Session = Depends(get_db)):
    """Get a train by its number."""
    # This would use the actual repository implementation
    raise HTTPException(status_code=404, detail="Train not found")


@router.get("/active/", response_model=List[Train])
async def get_active_trains(db: Session = Depends(get_db)):
    """Get all currently active trains."""
    # This would use the actual repository implementation
    return []


@router.put("/{train_id}/status")
async def update_train_status(
    train_id: UUID,
    status: TrainStatus,
    db: Session = Depends(get_db)
):
    """Update train status."""
    # This would use the actual repository implementation
    return {"message": "Train status updated", "train_id": train_id, "status": status}


@router.put("/{train_id}/position")
async def update_train_position(
    train_id: UUID,
    section_id: Optional[UUID] = None,
    station_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """Update train position."""
    # This would use the actual repository implementation
    return {
        "message": "Train position updated",
        "train_id": train_id,
        "section_id": section_id,
        "station_id": station_id
    }
