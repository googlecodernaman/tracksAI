"""
Dashboard and visualization API endpoints.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..dependencies import get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request, db: Session = Depends(get_db)):
    """Main dashboard page."""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Railway Traffic Control Dashboard"
    })


@router.get("/api/status")
async def get_dashboard_status(db: Session = Depends(get_db)):
    """Get current system status for dashboard."""
    # This would provide real-time system status
    return {
        "active_trains": 0,
        "delayed_trains": 0,
        "sections_occupied": 0,
        "total_sections": 0,
        "system_health": "operational",
        "last_optimization": None
    }


@router.get("/api/trains/positions")
async def get_train_positions(db: Session = Depends(get_db)):
    """Get current train positions for map visualization."""
    # This would provide real-time train positions
    return {"trains": []}


@router.get("/api/sections/status")
async def get_section_status(db: Session = Depends(get_db)):
    """Get current section status for visualization."""
    # This would provide real-time section status
    return {"sections": []}


@router.get("/api/metrics")
async def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Get key performance metrics for dashboard."""
    # This would provide real-time metrics
    return {
        "throughput": 0,
        "average_delay": 0,
        "on_time_percentage": 0,
        "optimization_confidence": 0
    }
