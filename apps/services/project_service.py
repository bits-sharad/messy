"""Service layer for Project CRUD operations"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status

from apps.models.project import Project
from apps.schemas.requests import ProjectCreateRequest, ProjectUpdateRequest
from apps.schemas.responses import ProjectResponse
from apps.database.connection import db_manager
from apps.database.connection import db_manager


class ProjectService:
    """Service for managing projects"""
    
    @staticmethod
    def _project_to_response(project: Project, job_count: Optional[int] = None) -> ProjectResponse:
        """Convert Project model to ProjectResponse"""
        return ProjectResponse(
            id=str(project._id),
            name=project.name,
            description=project.description,
            tenant_id=project.tenant_id,
            status=project.status,
            metadata=project.metadata,
            created_by=project.created_by,
            created_at=project.created_at,
            updated_at=project.updated_at,
            job_count=job_count
        )
    
    @staticmethod
    async def create_project(project_data: ProjectCreateRequest) -> ProjectResponse:
        """Create a new project"""
        db = db_manager.get_database()
        collection = Project.get_collection(db)
        
        # Create project model
        project = Project(
            name=project_data.name,
            description=project_data.description,
            tenant_id=project_data.tenant_id,
            status=project_data.status.value,
            metadata=project_data.metadata or {},
            created_by=project_data.created_by
        )
        
        try:
            # Insert into database
            result = collection.insert_one(project.to_dict())
            project._id = result.inserted_id
            
            return ProjectService._project_to_response(project, job_count=0)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create project: {str(e)}"
            )
    
    @staticmethod
    async def get_project(project_id: str) -> ProjectResponse:
        """Get a project by ID"""
        db = db_manager.get_database()
        collection = Project.get_collection(db)
        
        try:
            project_doc = collection.find_one({"_id": ObjectId(project_id)})
            if not project_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with id {project_id} not found"
                )
            
            project = Project.from_dict(project_doc)
            
            # Get job count
            job_collection = db.jobs
            job_count = job_collection.count_documents({"project_id": project_id})
            
            return ProjectService._project_to_response(project, job_count=job_count)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get project: {str(e)}"
            )
    
    @staticmethod
    async def list_projects(
        tenant_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProjectResponse]:
        """List projects with optional filters"""
        # Ensure database is connected, try to reconnect if needed
        if not db_manager.is_connected():
            print("[INFO] Database not connected, attempting to reconnect...")
            try:
                db_manager.connect()
            except Exception as e:
                print(f"[WARNING] Reconnection attempt failed: {e}")
            
            # Verify connection after attempt
            if not db_manager.is_connected():
                print("[WARNING] Still not connected after reconnection attempt")
                print("[INFO] Will try to get database anyway (might work)")
        
        try:
            # Try to get database - this will raise RuntimeError if not connected
            try:
                db = db_manager.get_database()
            except RuntimeError:
                # Database not connected, try to reconnect
                print("[INFO] get_database() failed - attempting reconnect...")
                db_manager.connect()
                db = db_manager.get_database()
            
            collection = Project.get_collection(db)
            
            # Build query
            query: Dict[str, Any] = {}
            if tenant_id:
                query["tenant_id"] = tenant_id
            if status:
                query["status"] = status
            
            # Get projects
            project_docs = collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            
            projects = []
            for doc in project_docs:
                project = Project.from_dict(doc)
                
                # Get job count for each project
                job_collection = db.jobs
                job_count = job_collection.count_documents({"project_id": str(project._id)})
                
                projects.append(ProjectService._project_to_response(project, job_count=job_count))
            
            return projects
        except RuntimeError as e:
            # Database connection error
            print(f"Database connection error in list_projects: {e}")
            return []
        except Exception as e:
            print(f"Error in list_projects: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list projects: {str(e)}"
            )
    
    @staticmethod
    async def update_project(project_id: str, update_data: ProjectUpdateRequest) -> ProjectResponse:
        """Update a project"""
        db = db_manager.get_database()
        collection = Project.get_collection(db)
        
        try:
            # Check if project exists
            project_doc = collection.find_one({"_id": ObjectId(project_id)})
            if not project_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with id {project_id} not found"
                )
            
            # Build update dictionary
            update_dict: Dict[str, Any] = {}
            if update_data.name is not None:
                update_dict["name"] = update_data.name
            if update_data.description is not None:
                update_dict["description"] = update_data.description
            if update_data.status is not None:
                update_dict["status"] = update_data.status.value
            if update_data.metadata is not None:
                # Merge metadata with existing
                existing_metadata = project_doc.get("metadata", {})
                existing_metadata.update(update_data.metadata)
                update_dict["metadata"] = existing_metadata
            
            # Always update the timestamp
            update_dict["updated_at"] = datetime.utcnow()
            collection.update_one(
                {"_id": ObjectId(project_id)},
                {"$set": update_dict}
            )
            
            # Get updated project
            updated_doc = collection.find_one({"_id": ObjectId(project_id)})
            project = Project.from_dict(updated_doc)
            
            # Get job count
            job_collection = db.jobs
            job_count = job_collection.count_documents({"project_id": project_id})
            
            return ProjectService._project_to_response(project, job_count=job_count)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update project: {str(e)}"
            )
    
    @staticmethod
    async def delete_project(project_id: str) -> bool:
        """Delete a project"""
        db = db_manager.get_database()
        collection = Project.get_collection(db)
        
        try:
            # Check if project exists
            project_doc = collection.find_one({"_id": ObjectId(project_id)})
            if not project_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with id {project_id} not found"
                )
            
            # Check if project has jobs
            job_collection = db.jobs
            job_count = job_collection.count_documents({"project_id": project_id})
            if job_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete project with {job_count} associated jobs. Please delete or reassign jobs first."
                )
            
            # Delete project
            result = collection.delete_one({"_id": ObjectId(project_id)})
            
            return result.deleted_count > 0
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete project: {str(e)}"
            )

