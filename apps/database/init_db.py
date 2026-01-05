"""Database initialization utilities"""
from apps.database.connection import db_manager


def create_indexes():
    """Create database indexes for optimal performance and data integrity"""
    db = db_manager.get_database()
    
    # Create unique index on job_code + project_id for jobs
    # This ensures job_code is unique within each project
    jobs_collection = db.jobs
    jobs_collection.create_index(
        [("project_id", 1), ("job_code", 1)],
        unique=True,
        name="unique_job_code_per_project"
    )
    
    # Create index on project_id for faster queries
    jobs_collection.create_index("project_id")
    
    # Create index on status for faster filtering
    jobs_collection.create_index("status")
    
    # Create indexes for projects collection
    projects_collection = db.projects
    projects_collection.create_index("tenant_id")
    projects_collection.create_index("status")
    
    print("Database indexes created successfully")

