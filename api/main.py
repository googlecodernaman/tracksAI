"""
Main FastAPI application for the Railway Traffic Decision-Support System.

This module sets up the FastAPI application with all routes,
middleware, and configuration.
"""

import logging
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from prometheus_client import Counter, Histogram, generate_latest
import uvicorn

from .routes import trains, sections, stations, decisions, dashboard, optimization
from .dependencies import get_db, get_optimizer
from core.database import DatabaseConfig
from core.optimizer import RailwayOptimizer

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
OPTIMIZATION_COUNT = Counter('optimization_requests_total', 'Total optimization requests')
OPTIMIZATION_DURATION = Histogram('optimization_duration_seconds', 'Optimization duration')

# Global variables for dependency injection
db_config: DatabaseConfig = None
optimizer: RailwayOptimizer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global db_config, optimizer
    
    # Startup
    logger.info("Starting Railway Traffic Decision-Support System")
    
    # Initialize database
    database_url = "postgresql://user:password@localhost/railway_db"
    db_config = DatabaseConfig(database_url)
    db_config.create_tables()
    
    # Initialize optimizer
    optimizer = RailwayOptimizer(time_limit_seconds=30)
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    if db_config:
        db_config.close()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Railway Traffic Decision-Support System",
    description="AI-powered decision support for railway traffic management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(trains.router, prefix="/api/v1/trains", tags=["trains"])
app.include_router(sections.router, prefix="/api/v1/sections", tags=["sections"])
app.include_router(stations.router, prefix="/api/v1/stations", tags=["stations"])
app.include_router(decisions.router, prefix="/api/v1/decisions", tags=["decisions"])
app.include_router(optimization.router, prefix="/api/v1/optimization", tags=["optimization"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])


@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "name": "Railway Traffic Decision-Support System",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "api_docs": "/docs",
            "dashboard": "/dashboard",
            "metrics": "/metrics"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()


# Dependency injection functions
def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    if not db_config:
        raise HTTPException(status_code=503, detail="Database not initialized")
    return db_config


def get_optimizer_instance() -> RailwayOptimizer:
    """Get optimizer instance."""
    if not optimizer:
        raise HTTPException(status_code=503, detail="Optimizer not initialized")
    return optimizer


# Update dependencies module
import sys
sys.modules['api.dependencies'].get_db = get_database_config
sys.modules['api.dependencies'].get_optimizer = get_optimizer_instance


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        }
    )
