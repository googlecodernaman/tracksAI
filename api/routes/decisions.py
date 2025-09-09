"""
Decision-related API endpoints.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.models import Decision
from ..dependencies import get_db

router = APIRouter()


@router.get("/", response_model=List[Decision])
async def get_decisions(db: Session = Depends(get_db)):
    """Get all decisions."""
    # This would use the actual repository implementation
    return []


@router.get("/{decision_id}", response_model=Decision)
async def get_decision(decision_id: UUID, db: Session = Depends(get_db)):
    """Get a specific decision by ID."""
    # This would use the actual repository implementation
    raise HTTPException(status_code=404, detail="Decision not found")


@router.get("/train/{train_id}", response_model=List[Decision])
async def get_decisions_for_train(train_id: UUID, db: Session = Depends(get_db)):
    """Get decisions for a specific train."""
    # This would use the actual repository implementation
    return []


@router.get("/pending/", response_model=List[Decision])
async def get_pending_decisions(db: Session = Depends(get_db)):
    """Get decisions that haven't been applied yet."""
    # This would use the actual repository implementation
    return []


@router.put("/{decision_id}/apply")
async def apply_decision(decision_id: UUID, db: Session = Depends(get_db)):
    """Apply a decision."""
    # This would use the actual repository implementation
    return {"message": "Decision applied", "decision_id": decision_id}
