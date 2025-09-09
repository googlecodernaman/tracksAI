#!/usr/bin/env python3
"""
Local development server for Railway Traffic Decision-Support System.

This script runs the system locally without Docker dependencies,
using SQLite for the database and in-memory storage for development.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def setup_environment():
    """Set up environment variables for local development."""
    os.environ.setdefault('DATABASE_URL', 'sqlite:///./railway_dev.db')
    os.environ.setdefault('DEBUG', 'true')
    os.environ.setdefault('ENVIRONMENT', 'development')
    os.environ.setdefault('LOG_LEVEL', 'INFO')
    
    logger.info("Environment configured for local development")

def create_simple_app():
    """Create a simplified FastAPI app for local development."""
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    
    # Create FastAPI app
    app = FastAPI(
        title="Railway Traffic Decision-Support System (Local Dev)",
        description="AI-powered decision support for railway traffic management",
        version="1.0.0-dev"
    )
    
    # Mount static files if they exist
    static_dir = project_root / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Set up templates
    templates_dir = project_root / "templates"
    if templates_dir.exists():
        templates = Jinja2Templates(directory=str(templates_dir))
    else:
        templates = None
    
    @app.get("/")
    async def root():
        """Root endpoint with system information."""
        return {
            "name": "Railway Traffic Decision-Support System",
            "version": "1.0.0-dev",
            "status": "operational (local development)",
            "endpoints": {
                "api_docs": "/docs",
                "dashboard": "/dashboard",
                "health": "/health"
            }
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "mode": "local_development"}
    
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        """Simple dashboard for local development."""
        if templates:
            return templates.TemplateResponse("dashboard.html", {
                "request": None,
                "title": "Railway Traffic Control Dashboard (Local Dev)"
            })
        else:
            return HTMLResponse("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Railway Traffic Control Dashboard</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <h1>🚆 Railway Traffic Decision-Support System</h1>
                    <div class="alert alert-info">
                        <h4>Local Development Mode</h4>
                        <p>This is a simplified version running locally. The full system is being developed.</p>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">System Status</h5>
                                    <p class="card-text">✅ System is operational</p>
                                    <p class="card-text">🔧 Running in development mode</p>
                                    <p class="card-text">📊 Database: SQLite (local)</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">Quick Actions</h5>
                                    <a href="/docs" class="btn btn-primary">API Documentation</a>
                                    <a href="/health" class="btn btn-secondary">Health Check</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """)
    
    @app.get("/api/v1/status")
    async def api_status():
        """API status endpoint."""
        return {
            "status": "operational",
            "mode": "local_development",
            "features": {
                "optimization": "available",
                "dashboard": "available",
                "database": "sqlite",
                "real_time": "simulated"
            }
        }
    
    return app

def main():
    """Main entry point for local development server."""
    try:
        logger.info("Starting Railway Traffic Decision-Support System (Local Dev)")
        
        # Set up environment
        setup_environment()
        
        # Create app
        app = create_simple_app()
        
        # Run server
        logger.info("Starting server on http://localhost:8000")
        logger.info("API documentation available at http://localhost:8000/docs")
        logger.info("Dashboard available at http://localhost:8000/dashboard")
        
        import uvicorn
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            reload=True
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
