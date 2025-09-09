"""
Dependency injection for the API layer.

This module provides dependency functions for database sessions,
optimizer instances, and other shared resources.
"""

from typing import Generator
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import DatabaseConfig, SystemStateRepository
from core.optimizer import RailwayOptimizer


def get_db() -> Generator[Session, None, None]:
    """
    Get database session dependency.
    
    This function will be overridden by the main application
    to provide the actual database configuration.
    """
    raise HTTPException(status_code=503, detail="Database not configured")


def get_optimizer() -> RailwayOptimizer:
    """
    Get optimizer instance dependency.
    
    This function will be overridden by the main application
    to provide the actual optimizer instance.
    """
    raise HTTPException(status_code=503, detail="Optimizer not configured")


def get_system_state_repository(
    db: Session = Depends(get_db)
) -> SystemStateRepository:
    """Get system state repository."""
    # This would be implemented with actual repository
    # For now, return a placeholder
    raise NotImplementedError("System state repository not implemented")
