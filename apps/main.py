"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from apps.database.connection import db_manager
from apps.database.init_db import create_indexes
from apps.routes import projects, jobs
from apps.routes import document_routes
from apps.api import routes as api_routes
from apps.ai.routes import rag_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    print("=" * 60)
    print("Starting FastAPI application...")
    print("=" * 60)
    
    try:
        db_manager.connect()
        if db_manager.is_connected():
            print(f"[OK] Database connected: {db_manager.database_name}")
            try:
                create_indexes()
                print("[OK] Database indexes created/verified")
            except Exception as e:
                # Index creation might fail if indexes already exist, which is fine
                print(f"[NOTE] Index creation: {str(e)}")
        else:
            print("[WARNING] Database connection failed, but continuing...")
            print("The application will start but database operations will fail.")
            print(f"Connection string: {db_manager.connection_string}")
            print("Please ensure MongoDB is running and accessible.")
    except Exception as e:
        print(f"[ERROR] Failed to connect to database: {e}")
        print("The application will start but database operations will fail.")
    
    print("=" * 60)
    print("FastAPI application ready!")
    print("=" * 60)
    yield
    
    # Shutdown
    try:
        db_manager.disconnect()
        print("Database disconnected")
    except Exception as e:
        print(f"Error disconnecting from database: {e}")


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
# Include RAG/AI routes
app.include_router(rag_routes.router)
# Include document processing routes
app.include_router(document_routes.router)


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
        # Try to reconnect if not connected
        if not db_manager.is_connected():
            print("[HEALTH CHECK] Attempting to reconnect to MongoDB...")
            db_manager.connect()
        
        if db_manager.is_connected():
            db = db_manager.get_database()
            # Simple ping to check database connection
            db.command("ping")
            return {"status": "healthy", "database": "connected"}
        else:
            return {"status": "unhealthy", "database": "disconnected", "error": "Could not establish connection"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

