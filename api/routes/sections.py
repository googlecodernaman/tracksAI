"""
Section-related API endpoints.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.models import Section, SectionStatus
from ..dependencies import get_db

router = APIRouter()


@router.get("/", response_model=List[Section])
async def get_sections(
    status: Optional[SectionStatus] = Query(None, description="Filter by section status"),
    db: Session = Depends(get_db)
):
    """Get all sections with optional filtering."""
    # This would use the actual repository implementation
    return []


@router.get("/{section_id}", response_model=Section)
async def get_section(section_id: UUID, db: Session = Depends(get_db)):
    """Get a specific section by ID."""
    # This would use the actual repository implementation
    raise HTTPException(status_code=404, detail="Section not found")


@router.put("/{section_id}/status")
async def update_section_status(
    section_id: UUID,
    status: SectionStatus,
    db: Session = Depends(get_db)
):
    """Update section status."""
    # This would use the actual repository implementation
    return {"message": "Section status updated", "section_id": section_id, "status": status}
