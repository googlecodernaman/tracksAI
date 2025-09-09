"""
Optimization-related API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from core.models import OptimizationResult, SystemState
from core.optimizer import RailwayOptimizer
from ..dependencies import get_db, get_optimizer

router = APIRouter()


@router.post("/optimize", response_model=OptimizationResult)
async def optimize_traffic(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    optimizer: RailwayOptimizer = Depends(get_optimizer)
):
    """
    Trigger optimization for current system state.
    
    This endpoint analyzes the current railway system state and
    generates optimal decisions for train precedence and routing.
    """
    try:
        # Get current system state from database
        # This would be implemented with actual repository
        system_state = await _get_current_system_state(db)
        
        # Run optimization
        result = optimizer.optimize(system_state)
        
        # Save optimization result to database
        background_tasks.add_task(_save_optimization_result, result, db)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.get("/results/latest", response_model=OptimizationResult)
async def get_latest_optimization_result(db: Session = Depends(get_db)):
    """Get the latest optimization result."""
    # This would use the actual repository implementation
    raise HTTPException(status_code=404, detail="No optimization results found")


@router.get("/results/history")
async def get_optimization_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get optimization history."""
    # This would use the actual repository implementation
    return {"results": [], "total": 0}


@router.post("/panic-mode")
async def enable_panic_mode(db: Session = Depends(get_db)):
    """
    Enable panic mode - disable auto-recommendations and revert to manual mode.
    
    This is an emergency endpoint as specified in the cursorules.
    """
    # This would implement panic mode logic
    return {"message": "Panic mode enabled", "auto_recommendations": False}


@router.delete("/panic-mode")
async def disable_panic_mode(db: Session = Depends(get_db)):
    """Disable panic mode and re-enable auto-recommendations."""
    # This would implement panic mode logic
    return {"message": "Panic mode disabled", "auto_recommendations": True}


async def _get_current_system_state(db: Session) -> SystemState:
    """Get current system state from database."""
    # This would be implemented with actual repository
    # For now, return a mock state
    from core.models import Train, Section, Station, TrainType, TrainStatus, SectionStatus
    from datetime import datetime
    from uuid import uuid4
    
    # Mock data for demonstration
    station1 = Station(
        id=uuid4(),
        name="Mumbai Central",
        code="BCT",
        latitude=19.0176,
        longitude=72.8562,
        platforms=8,
        is_junction=True
    )
    
    station2 = Station(
        id=uuid4(),
        name="Delhi",
        code="DLI",
        latitude=28.6139,
        longitude=77.2090,
        platforms=12,
        is_junction=True
    )
    
    section = Section(
        id=uuid4(),
        from_station=station1,
        to_station=station2,
        length_km=1384.0,
        max_speed_kmh=120,
        tracks=2,
        status=SectionStatus.AVAILABLE
    )
    
    train = Train(
        id=uuid4(),
        number="12345",
        name="Rajdhani Express",
        train_type=TrainType.EXPRESS,
        max_speed=120,
        length=500,
        current_section=section,
        status=TrainStatus.RUNNING,
        delay_minutes=15
    )
    
    return SystemState(
        timestamp=datetime.utcnow(),
        trains=[train],
        sections=[section],
        stations=[station1, station2]
    )


async def _save_optimization_result(result: OptimizationResult, db: Session):
    """Save optimization result to database."""
    # This would be implemented with actual repository
    pass
