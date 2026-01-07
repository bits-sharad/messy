"""Service layer for Job CRUD operations"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status

from apps.models.job import Job
from apps.models.project import Project
from apps.schemas.requests import JobCreateRequest, JobUpdateRequest
from apps.schemas.responses import JobResponse
from apps.database.connection import db_manager


class JobService:
    """Service for managing jobs"""
    
    @staticmethod
    def _job_to_response(job: Job, match_count: Optional[int] = None) -> JobResponse:
        """Convert Job model to JobResponse"""
        return JobResponse(
            id=str(job._id),
            project_id=job.project_id,
            title=job.title,
            description=job.description,
            job_code=job.job_code,
            status=job.status,
            department=job.department,
            level=job.level,
            required_skills=job.required_skills,
            responsibilities=job.responsibilities,
            metadata=job.metadata,
            created_by=job.created_by,
            created_at=job.created_at,
            updated_at=job.updated_at,
            match_count=match_count
        )
    
    @staticmethod
    async def create_job(job_data: JobCreateRequest) -> JobResponse:
        """Create a new job"""
        db = db_manager.get_database()
        collection = Job.get_collection(db)
        project_collection = Project.get_collection(db)
        
        # Verify project exists
        try:
            project_doc = project_collection.find_one({"_id": ObjectId(job_data.project_id)})
            if not project_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with id {job_data.project_id} not found"
                )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid project_id: {str(e)}"
            )
        
        # Check if job_code is unique within project
        existing_job = collection.find_one({
            "project_id": job_data.project_id,
            "job_code": job_data.job_code
        })
        if existing_job:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job code '{job_data.job_code}' already exists in project {job_data.project_id}"
            )
        
        # Create job model
        job = Job(
            project_id=job_data.project_id,
            title=job_data.title,
            description=job_data.description,
            job_code=job_data.job_code,
            status=job_data.status.value,
            department=job_data.department,
            level=job_data.level.value if job_data.level else None,
            required_skills=job_data.required_skills or [],
            responsibilities=job_data.responsibilities or [],
            metadata=job_data.metadata or {},
            created_by=job_data.created_by
        )
        
        try:
            # Insert into database
            result = collection.insert_one(job.to_dict())
            job._id = result.inserted_id
            
            return JobService._job_to_response(job, match_count=0)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create job: {str(e)}"
            )
    
    @staticmethod
    async def get_job(job_id: str) -> JobResponse:
        """Get a job by ID"""
        db = db_manager.get_database()
        collection = Job.get_collection(db)
        
        try:
            job_doc = collection.find_one({"_id": ObjectId(job_id)})
            if not job_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Job with id {job_id} not found"
                )
            
            job = Job.from_dict(job_doc)
            
            # Get match count (placeholder - would need to query matches collection)
            # For now, returning None as match_count is optional
            match_count = None  # TODO: Implement match count calculation
            
            return JobService._job_to_response(job, match_count=match_count)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get job: {str(e)}"
            )
    
    @staticmethod
    async def list_jobs(
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[JobResponse]:
        """List jobs with optional filters"""
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
            db = db_manager.get_database()
            collection = Job.get_collection(db)
            
            # Build query
            query: Dict[str, Any] = {}
            if project_id:
                query["project_id"] = project_id
            if status:
                query["status"] = status
            # Get jobs
            job_docs = collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            
            jobs = []
            for doc in job_docs:
                job = Job.from_dict(doc)
                # Match count would be calculated here if needed
                match_count = None  # TODO: Implement match count calculation
                jobs.append(JobService._job_to_response(job, match_count=match_count))
            
            return jobs
        except RuntimeError as e:
            # Database connection error
            print(f"Database connection error in list_jobs: {e}")
            return []
        except Exception as e:
            print(f"Error in list_jobs: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list jobs: {str(e)}"
            )
    
    @staticmethod
    async def update_job(job_id: str, update_data: JobUpdateRequest) -> JobResponse:
        """Update a job"""
        db = db_manager.get_database()
        collection = Job.get_collection(db)
        
        try:
            # Check if job exists
            job_doc = collection.find_one({"_id": ObjectId(job_id)})
            if not job_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Job with id {job_id} not found"
                )
            
            # Build update dictionary
            update_dict: Dict[str, Any] = {}
            if update_data.title is not None:
                update_dict["title"] = update_data.title
            if update_data.description is not None:
                update_dict["description"] = update_data.description
            if update_data.status is not None:
                update_dict["status"] = update_data.status.value
            if update_data.department is not None:
                update_dict["department"] = update_data.department
            if update_data.level is not None:
                update_dict["level"] = update_data.level.value
            if update_data.required_skills is not None:
                # Replace required_skills (can be changed to merge if needed)
                update_dict["required_skills"] = update_data.required_skills
            if update_data.responsibilities is not None:
                # Replace responsibilities (can be changed to merge if needed)
                update_dict["responsibilities"] = update_data.responsibilities
            if update_data.metadata is not None:
                # Merge metadata with existing
                existing_metadata = job_doc.get("metadata", {})
                existing_metadata.update(update_data.metadata)
                update_dict["metadata"] = existing_metadata
            
            # Always update the timestamp
            update_dict["updated_at"] = datetime.utcnow()
            
            # Update in database
            collection.update_one(
                {"_id": ObjectId(job_id)},
                {"$set": update_dict}
            )
            
            # Get updated job
            updated_doc = collection.find_one({"_id": ObjectId(job_id)})
            job = Job.from_dict(updated_doc)
            
            # Match count would be calculated here if needed
            match_count = None  # TODO: Implement match count calculation
            
            return JobService._job_to_response(job, match_count=match_count)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update job: {str(e)}"
            )
    
    @staticmethod
    async def delete_job(job_id: str) -> bool:
        """Delete a job"""
        db = db_manager.get_database()
        collection = Job.get_collection(db)
        
        try:
            # Check if job exists
            job_doc = collection.find_one({"_id": ObjectId(job_id)})
            if not job_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Job with id {job_id} not found"
                )
            
            # Delete job
            result = collection.delete_one({"_id": ObjectId(job_id)})
            
            return result.deleted_count > 0
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete job: {str(e)}"
            )

