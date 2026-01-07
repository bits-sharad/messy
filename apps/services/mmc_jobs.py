"""MMC Job Service Layer with CoreAPIClient integration"""
from typing import Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status

from apps.core.client import CoreAPIClient
from apps.core.principal import Principal
from apps.core.exceptions import ResourceNotFoundError, UnauthorizedError, ConflictError
from apps.schemas.requests import JobCreateRequest, JobUpdateRequest
from apps.schemas.responses import JobResponse


class JobService:
    """Service for managing jobs with CoreAPIClient and authorization"""
    
    def __init__(self, core_api: CoreAPIClient):
        """
        Initialize JobService with CoreAPIClient
        
        Args:
            core_api: CoreAPIClient instance for metadata operations
        """
        self.core_api = core_api
        self.collection = "jobs"
        self.project_collection = "projects"
    
    def _job_to_dict(
        self,
        job_data: Dict[str, Any],
        match_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Convert job data dictionary to response format
        
        Args:
            job_data: Job document from database
            match_count: Optional match count for the job
            
        Returns:
            Dictionary with job data in response format
        """
        return {
            "id": str(job_data.get("_id", job_data.get("id", ""))),
            "project_id": job_data.get("project_id"),
            "title": job_data.get("title"),
            "description": job_data.get("description"),
            "job_code": job_data.get("job_code"),
            "status": job_data.get("status"),
            "department": job_data.get("department"),
            "level": job_data.get("level"),
            "required_skills": job_data.get("required_skills", []),
            "responsibilities": job_data.get("responsibilities", []),
            "metadata": job_data.get("metadata", {}),
            "created_by": job_data.get("created_by"),
            "created_at": job_data.get("created_at"),
            "updated_at": job_data.get("updated_at"),
            "match_count": match_count
        }
    
    async def _get_match_count(self, job_id: str) -> Optional[int]:
        """
        Get the number of candidates matched to a job
        
        Args:
            job_id: Job ID
            
        Returns:
            Number of matches (None if not implemented yet)
        """
        # TODO: Implement match count calculation when matches collection is available
        # For now, returning None as match_count is optional
        return None
    
    # CREATE
    async def create_job(
        self,
        job_data: JobCreateRequest,
        principal: Principal
    ) -> dict:
        """
        Create a new job
        
        Args:
            job_data: Job creation data
            principal: Authenticated principal
            
        Returns:
            Dictionary with created job data
            
        Raises:
            HTTPException: If creation fails or authorization fails
        """
        try:
            # Validate project exists
            if not await self.validate_project_exists(job_data.project_id):
                raise ResourceNotFoundError("Project", job_data.project_id)
            
            # Check authorization - user must have access to the target project
            # Get project to check tenant and ownership
            project_result = await self.core_api.metadata_get(
                collection=self.project_collection,
                document_id=job_data.project_id
            )
            
            if not project_result.get("success") or not project_result.get("document"):
                raise ResourceNotFoundError("Project", job_data.project_id)
            
            project_doc = project_result["document"]
            
            # Check if user has access to the project
            if not principal.can_access_tenant(project_doc.get("tenant_id")):
                raise UnauthorizedError("Not authorized to create job in this project")
            
            # Validate job_code is unique within project
            if not await self.validate_job_code_unique(job_data.project_id, job_data.job_code):
                raise ConflictError(
                    f"Job code '{job_data.job_code}' already exists in project {job_data.project_id}"
                )
            
            # Generate new ObjectId for job
            job_id = str(ObjectId())
            
            # Build job document
            obj_id = ObjectId(job_id)
            job_doc = {
                "_id": obj_id,
                "project_id": job_data.project_id,
                "title": job_data.title,
                "description": job_data.description,
                "job_code": job_data.job_code,
                "status": job_data.status.value if hasattr(job_data.status, 'value') else job_data.status,
                "department": job_data.department,
                "level": job_data.level.value if job_data.level and hasattr(job_data.level, 'value') else job_data.level,
                "required_skills": job_data.required_skills or [],
                "responsibilities": job_data.responsibilities or [],
                "metadata": job_data.metadata or {},
                "created_by": principal.subject,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "deleted_at": None  # Soft delete flag
            }
            
            # Store job using CoreAPIClient
            result = await self.core_api.metadata_put(
                collection=self.collection,
                document_id=job_id,
                document=job_doc,
                upsert=True
            )
            
            if not result.get("success"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create job"
                )
            
            # Return job data with match_count = None (to be implemented)
            response = self._job_to_dict(result["document"], match_count=None)
            return response
            
        except (ResourceNotFoundError, UnauthorizedError, ConflictError):
            raise
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create job: {str(e)}"
            )
    
    # READ
    async def get_job(self, job_id: str, include_documents: bool = True) -> dict:
        """
        Get a job by ID
        
        Args:
            job_id: Job ID
            include_documents: Whether to include document content from PDFs
            
        Returns:
            Dictionary with job data
            
        Raises:
            HTTPException: If job not found
        """
        try:
            result = await self.core_api.metadata_get(
                collection=self.collection,
                document_id=job_id
            )
            
            if not result.get("success") or not result.get("document"):
                raise ResourceNotFoundError("Job", job_id)
            
            job_doc = result["document"]
            
            # Check if job is soft-deleted
            if job_doc.get("deleted_at"):
                raise ResourceNotFoundError("Job", job_id)
            
            # Get match count
            match_count = await self._get_match_count(job_id)
            
            response = self._job_to_dict(job_doc, match_count=match_count)
            
            # Include document content if requested
            if include_documents:
                try:
                    from apps.services.document_service import DocumentService
                    from apps.ai.services.rag_service import RAGService
                    
                    rag_service = RAGService()
                    doc_service = DocumentService(rag_service=rag_service)
                    doc_content = await doc_service.get_document_content(job_id=job_id)
                    
                    if doc_content.get("has_documents"):
                        response["document_content"] = {
                            "has_documents": True,
                            "document_count": doc_content.get("document_count", 0),
                            "total_content": doc_content.get("total_content", ""),
                            "total_content_length": doc_content.get("total_content_length", 0),
                            "total_word_count": doc_content.get("total_word_count", 0),
                            "documents": doc_content.get("documents", [])
                        }
                    else:
                        response["document_content"] = {
                            "has_documents": False,
                            "document_count": 0
                        }
                except Exception as e:
                    # If document service fails, just continue without document content
                    print(f"Warning: Could not fetch document content: {e}")
                    response["document_content"] = {"has_documents": False, "error": str(e)}
            
            return response
            
        except ResourceNotFoundError:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get job: {str(e)}"
            )
    
    async def list_jobs(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None
    ) -> dict:
        """
        List jobs in a project with optional filtering
        
        Args:
            project_id: Project ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Optional status filter
            
        Returns:
            Dictionary with list of jobs and pagination info
        """
        try:
            # Build query
            query: Dict[str, Any] = {
                "project_id": project_id,
                "deleted_at": None  # Exclude soft-deleted jobs
            }
            
            if status:
                query["status"] = status
            
            result = await self.core_api.metadata_get(
                collection=self.collection,
                query=query,
                skip=skip,
                limit=limit
            )
            
            jobs = []
            for doc in result.get("documents", []):
                job_id = str(doc.get("_id", ""))
                match_count = await self._get_match_count(job_id)
                jobs.append(self._job_to_dict(doc, match_count=match_count))
            
            total_count = await self.core_api.metadata_count(
                collection=self.collection,
                query=query
            )
            
            return {
                "jobs": jobs,
                "count": len(jobs),
                "total": total_count,
                "skip": skip,
                "limit": limit
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list jobs: {str(e)}"
            )
    
    async def list_all_jobs(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> dict:
        """
        List all jobs across projects for a tenant
        
        Args:
            tenant_id: Tenant ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Dictionary with list of jobs and pagination info
        """
        try:
            # First get all project IDs for this tenant
            project_query = {
                "tenant_id": tenant_id,
                "deleted_at": None
            }
            projects_result = await self.core_api.metadata_get(
                collection=self.project_collection,
                query=project_query
            )
            
            project_ids = [str(p.get("_id", "")) for p in projects_result.get("documents", [])]
            
            if not project_ids:
                return {
                    "jobs": [],
                    "count": 0,
                    "total": 0,
                    "skip": skip,
                    "limit": limit
                }
            
            # Query jobs for these projects
            # Note: MongoDB query with $in operator
            if len(project_ids) == 1:
                query: Dict[str, Any] = {
                    "project_id": project_ids[0],
                    "deleted_at": None
                }
            else:
                query: Dict[str, Any] = {
                    "project_id": {"$in": project_ids},
                    "deleted_at": None
                }
            
            result = await self.core_api.metadata_get(
                collection=self.collection,
                query=query,
                skip=skip,
                limit=limit
            )
            
            jobs = []
            for doc in result.get("documents", []):
                job_id = str(doc.get("_id", ""))
                match_count = await self._get_match_count(job_id)
                jobs.append(self._job_to_dict(doc, match_count=match_count))
            
            total_count = await self.core_api.metadata_count(
                collection=self.collection,
                query=query
            )
            
            return {
                "jobs": jobs,
                "count": len(jobs),
                "total": total_count,
                "skip": skip,
                "limit": limit
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list all jobs: {str(e)}"
            )
    
    async def search_jobs(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        Search jobs by title, description, or job_code
        
        Args:
            query: Search query string
            filters: Optional filters (project_id, status, etc.)
            
        Returns:
            Dictionary with list of matching jobs
        """
        try:
            # Build MongoDB text search query
            # Note: For full-text search, MongoDB text indexes would be needed
            # For now, we'll do a simple regex search on title, description, and job_code
            search_query: Dict[str, Any] = {
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                    {"job_code": {"$regex": query, "$options": "i"}}
                ],
                "deleted_at": None
            }
            
            # Apply additional filters
            if filters:
                if "project_id" in filters:
                    search_query["project_id"] = filters["project_id"]
                if "status" in filters:
                    search_query["status"] = filters["status"]
                if "department" in filters:
                    search_query["department"] = filters["department"]
                if "level" in filters:
                    search_query["level"] = filters["level"]
            
            result = await self.core_api.metadata_get(
                collection=self.collection,
                query=search_query,
                skip=0,
                limit=100  # Default limit for search
            )
            
            jobs = []
            for doc in result.get("documents", []):
                job_id = str(doc.get("_id", ""))
                match_count = await self._get_match_count(job_id)
                jobs.append(self._job_to_dict(doc, match_count=match_count))
            
            return {
                "jobs": jobs,
                "count": len(jobs),
                "query": query
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to search jobs: {str(e)}"
            )
    
    # UPDATE
    async def update_job(
        self,
        job_id: str,
        update_data: JobUpdateRequest,
        principal: Principal
    ) -> dict:
        """
        Update an existing job
        
        Args:
            job_id: Job ID
            update_data: Update data
            principal: Authenticated principal
            
        Returns:
            Dictionary with updated job data
            
        Raises:
            HTTPException: If update fails or authorization fails
        """
        try:
            # Check authorization
            if not await self.check_authorization(job_id, principal):
                raise UnauthorizedError("Not authorized to update this job")
            
            # Get existing job
            get_result = await self.core_api.metadata_get(
                collection=self.collection,
                document_id=job_id
            )
            
            if not get_result.get("success") or not get_result.get("document"):
                raise ResourceNotFoundError("Job", job_id)
            
            job_doc = get_result["document"]
            
            # Check if soft-deleted
            if job_doc.get("deleted_at"):
                raise ResourceNotFoundError("Job", job_id)
            
            # If job_code is being updated, validate uniqueness
            if update_data.job_code and update_data.job_code != job_doc.get("job_code"):
                if not await self.validate_job_code_unique(job_doc.get("project_id"), update_data.job_code, exclude_job_id=job_id):
                    raise ConflictError(
                        f"Job code '{update_data.job_code}' already exists in project"
                    )
            
            # Build update dictionary
            if update_data.title is not None:
                job_doc["title"] = update_data.title
            if update_data.description is not None:
                job_doc["description"] = update_data.description
            if update_data.status is not None:
                job_doc["status"] = update_data.status.value if hasattr(update_data.status, 'value') else update_data.status
            if update_data.department is not None:
                job_doc["department"] = update_data.department
            if update_data.level is not None:
                job_doc["level"] = update_data.level.value if hasattr(update_data.level, 'value') else update_data.level
            if update_data.required_skills is not None:
                # Replace required_skills (not merge)
                job_doc["required_skills"] = update_data.required_skills
            if update_data.responsibilities is not None:
                # Replace responsibilities (not merge)
                job_doc["responsibilities"] = update_data.responsibilities
            if update_data.metadata is not None:
                # Merge metadata with existing
                existing_metadata = job_doc.get("metadata", {})
                existing_metadata.update(update_data.metadata)
                job_doc["metadata"] = existing_metadata
            
            # Always update timestamp
            job_doc["updated_at"] = datetime.utcnow()
            
            # Store updated job
            result = await self.core_api.metadata_put(
                collection=self.collection,
                document_id=job_id,
                document=job_doc,
                upsert=True
            )
            
            if not result.get("success"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update job"
                )
            
            # Get match count
            match_count = await self._get_match_count(job_id)
            
            response = self._job_to_dict(result["document"], match_count=match_count)
            return response
            
        except (ResourceNotFoundError, UnauthorizedError, ConflictError):
            raise
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update job: {str(e)}"
            )
    
    # DELETE
    async def delete_job(
        self,
        job_id: str,
        principal: Principal
    ) -> dict:
        """
        Hard delete a job (permanent deletion)
        
        Args:
            job_id: Job ID
            principal: Authenticated principal
            
        Returns:
            Dictionary with deletion result
            
        Raises:
            HTTPException: If deletion fails or authorization fails
        """
        try:
            # Check authorization
            if not await self.check_authorization(job_id, principal):
                raise UnauthorizedError("Not authorized to delete this job")
            
            # Check if job exists
            get_result = await self.core_api.metadata_get(
                collection=self.collection,
                document_id=job_id
            )
            
            if not get_result.get("success") or not get_result.get("document"):
                raise ResourceNotFoundError("Job", job_id)
            
            # Perform hard delete
            result = await self.core_api.metadata_delete(
                collection=self.collection,
                document_id=job_id,
                hard_delete=True
            )
            
            if not result.get("success"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete job"
                )
            
            return {
                "success": True,
                "id": job_id,
                "message": "Job deleted successfully"
            }
            
        except (ResourceNotFoundError, UnauthorizedError):
            raise
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete job: {str(e)}"
            )
    
    async def soft_delete_job(self, job_id: str) -> dict:
        """
        Soft delete a job (mark as closed)
        
        Args:
            job_id: Job ID
            
        Returns:
            Dictionary with soft deletion result
            
        Raises:
            HTTPException: If soft deletion fails
        """
        try:
            # Get existing job
            get_result = await self.core_api.metadata_get(
                collection=self.collection,
                document_id=job_id
            )
            
            if not get_result.get("success") or not get_result.get("document"):
                raise ResourceNotFoundError("Job", job_id)
            
            job_doc = get_result["document"]
            
            # Update job to closed status with deleted_at timestamp
            job_doc["status"] = "closed"
            job_doc["deleted_at"] = datetime.utcnow()
            job_doc["updated_at"] = datetime.utcnow()
            
            # Store updated job
            result = await self.core_api.metadata_put(
                collection=self.collection,
                document_id=job_id,
                document=job_doc,
                upsert=True
            )
            
            if not result.get("success"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to soft delete job"
                )
            
            return {
                "success": True,
                "id": job_id,
                "message": "Job closed successfully",
                "status": "closed"
            }
            
        except ResourceNotFoundError:
            raise
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to soft delete job: {str(e)}"
            )
    
    # VALIDATION & HELPERS
    async def validate_job_code_unique(
        self,
        project_id: str,
        job_code: str,
        exclude_job_id: Optional[str] = None
    ) -> bool:
        """
        Validate that job_code is unique within a project
        
        Args:
            project_id: Project ID
            job_code: Job code to validate
            exclude_job_id: Optional job ID to exclude from check (for updates)
            
        Returns:
            True if unique, False otherwise
        """
        try:
            query: Dict[str, Any] = {
                "project_id": project_id,
                "job_code": job_code,
                "deleted_at": None
            }
            
            result = await self.core_api.metadata_get(
                collection=self.collection,
                query=query,
                skip=0,
                limit=1
            )
            
            jobs = result.get("documents", [])
            
            if not jobs:
                return True
            
            # If excluding a job ID (for updates), check if the found job is the excluded one
            if exclude_job_id:
                found_job = jobs[0]
                if str(found_job.get("_id", "")) == exclude_job_id:
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def validate_project_exists(self, project_id: str) -> bool:
        """
        Validate if a project exists and is not soft-deleted
        
        Args:
            project_id: Project ID to validate
            
        Returns:
            True if project exists and is not deleted, False otherwise
        """
        try:
            result = await self.core_api.metadata_get(
                collection=self.project_collection,
                document_id=project_id
            )
            
            if not result.get("success") or not result.get("document"):
                return False
            
            project_doc = result["document"]
            
            # Check if soft-deleted
            if project_doc.get("deleted_at"):
                return False
            
            return True
            
        except Exception:
            return False
    
    async def check_authorization(
        self,
        job_id: str,
        principal: Principal
    ) -> bool:
        """
        Check if principal is authorized to perform operations on the job
        
        Authorization rules:
        - Job owner (created_by matches principal.subject)
        - Project owner (project's created_by matches principal.subject)
        - Tenant admin (principal has admin role for the project's tenant)
        
        Args:
            job_id: Job ID
            principal: Authenticated principal
            
        Returns:
            True if authorized, False otherwise
        """
        try:
            # Get job
            result = await self.core_api.metadata_get(
                collection=self.collection,
                document_id=job_id
            )
            
            if not result.get("success") or not result.get("document"):
                return False
            
            job_doc = result["document"]
            
            # Check if job owner
            if job_doc.get("created_by") == principal.subject:
                return True
            
            # Get project to check project ownership and tenant admin
            project_id = job_doc.get("project_id")
            if not project_id:
                return False
            
            project_result = await self.core_api.metadata_get(
                collection=self.project_collection,
                document_id=project_id
            )
            
            if not project_result.get("success") or not project_result.get("document"):
                return False
            
            project_doc = project_result["document"]
            
            # Check if project owner
            if project_doc.get("created_by") == principal.subject:
                return True
            
            # Check if tenant admin
            tenant_id = project_doc.get("tenant_id")
            if tenant_id and principal.is_tenant_admin(tenant_id):
                return True
            
            return False
            
        except Exception:
            return False
    
    async def get_job_count(self, project_id: str) -> int:
        """
        Get the number of jobs in a project
        
        Args:
            project_id: Project ID
            
        Returns:
            Number of jobs in the project
        """
        try:
            count = await self.core_api.metadata_count(
                collection=self.collection,
                query={"project_id": project_id, "deleted_at": None}
            )
            return count
        except Exception:
            return 0

