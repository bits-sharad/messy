"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from apps.database.connection import db_manager
from apps.database.init_db import create_indexes
from apps.routes import projects, jobs
from apps.api import routes as api_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    db_manager.connect()
    try:
        create_indexes()
    except Exception as e:
        # Index creation might fail if indexes already exist, which is fine
        print(f"Note: Index creation completed with message: {str(e)}")
    yield
    # Shutdown
    db_manager.disconnect()


app = FastAPI(
    title="MMC Job Matching Model API",
    description="API for managing Projects and Jobs in the MMC Job Matching Model",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router)
app.include_router(jobs.router)
# Include new API routes with CoreAPIClient and Principal
app.include_router(api_routes.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "MMC Job Matching Model API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        db = db_manager.get_database()
        # Simple ping to check database connection
        db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

