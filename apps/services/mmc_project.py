"""MMC Project Service Layer with CoreAPIClient integration"""
from typing import Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status

from apps.core.client import CoreAPIClient
from apps.core.principal import Principal
from apps.schemas.requests import ProjectCreateRequest, ProjectUpdateRequest
from apps.schemas.responses import ProjectResponse


class ProjectService:
    """Service for managing projects with CoreAPIClient and authorization"""
    
    def __init__(self, core_api: CoreAPIClient):
        """
        Initialize ProjectService with CoreAPIClient
        
        Args:
            core_api: CoreAPIClient instance for metadata operations
        """
        self.core_api = core_api
        self.collection = "projects"
    
    def _project_to_dict(
        self,
        project_data: Dict[str, Any],
        job_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Convert project data dictionary to response format
        
        Args:
            project_data: Project document from database
            job_count: Optional job count for the project
            
        Returns:
            Dictionary with project data in response format
        """
        return {
            "id": str(project_data.get("_id", project_data.get("id", ""))),
            "name": project_data.get("name"),
            "description": project_data.get("description"),
            "tenant_id": project_data.get("tenant_id"),
            "status": project_data.get("status"),
            "metadata": project_data.get("metadata", {}),
            "created_by": project_data.get("created_by"),
            "created_at": project_data.get("created_at"),
            "updated_at": project_data.get("updated_at"),
            "job_count": job_count
        }
    
    async def _get_job_count(self, project_id: str) -> int:
        """
        Get the number of jobs associated with a project
        
        Args:
            project_id: Project ID
            
        Returns:
            Number of jobs in the project
        """
        job_count = await self.core_api.metadata_count(
            collection="jobs",
            query={"project_id": project_id}
        )
        return job_count
    
    # CREATE
    async def create_project(
        self,
        project_data: ProjectCreateRequest,
        principal: Principal
    ) -> dict:
        """
        Create a new project
        
        Args:
            project_data: Project creation data
            principal: Authenticated principal
            
        Returns:
            Dictionary with created project data
            
        Raises:
            HTTPException: If creation fails or authorization fails
        """
        try:
            # Generate new ObjectId for project
            project_id = str(ObjectId())
            
            # Build project document
            # Convert project_id string to ObjectId for MongoDB
            obj_id = ObjectId(project_id)
            project_doc = {
                "_id": obj_id,
                "name": project_data.name,
                "description": project_data.description,
                "tenant_id": project_data.tenant_id,
                "status": project_data.status.value if hasattr(project_data.status, 'value') else project_data.status,
                "metadata": project_data.metadata or {},
                "created_by": principal.subject,  # Use principal subject for audit trail
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "deleted_at": None  # Soft delete flag
            }
            
            # Validate tenant access
            if not principal.can_access_tenant(project_data.tenant_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to create project for this tenant"
                )
            
            # Store project using CoreAPIClient
            result = await self.core_api.metadata_put(
                collection=self.collection,
                document_id=project_id,
                document=project_doc,
                upsert=True
            )
            
            if not result.get("success"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create project"
                )
            
            # Return project data with job_count = 0
            response = self._project_to_dict(result["document"], job_count=0)
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create project: {str(e)}"
            )
    
    # READ
    async def get_project(self, project_id: str, include_documents: bool = True) -> dict:
        """
        Get a project by ID
        
        Args:
            project_id: Project ID
            include_documents: Whether to include document content from PDFs
            
        Returns:
            Dictionary with project data
            
        Raises:
            HTTPException: If project not found
        """
        try:
            result = await self.core_api.metadata_get(
                collection=self.collection,
                document_id=project_id
            )
            
            if not result.get("success") or not result.get("document"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with id {project_id} not found"
                )
            
            project_doc = result["document"]
            
            # Check if project is soft-deleted
            if project_doc.get("deleted_at"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with id {project_id} not found"
                )
            
            # Get job count
            job_count = await self._get_job_count(project_id)
            
            response = self._project_to_dict(project_doc, job_count=job_count)
            
            # Include document content if requested
            if include_documents:
                try:
                    from apps.services.document_service import DocumentService
                    from apps.ai.services.rag_service import RAGService
                    
                    rag_service = RAGService()
                    doc_service = DocumentService(rag_service=rag_service)
                    doc_content = await doc_service.get_documents_for_project(project_id=project_id)
                    
                    if doc_content.get("has_documents"):
                        response["documents"] = doc_content.get("documents_by_job", {})
                    else:
                        response["documents"] = {}
                except Exception as e:
                    # If document service fails, just continue without document content
                    print(f"Warning: Could not fetch document content: {e}")
                    response["documents"] = {}
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get project: {str(e)}"
            )
    
    async def list_projects(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None
    ) -> dict:
        """
        List projects with optional filtering
        
        Args:
            tenant_id: Tenant ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Optional status filter
            
        Returns:
            Dictionary with list of projects and pagination info
        """
        try:
            # Build query
            query: Dict[str, Any] = {
                "tenant_id": tenant_id,
                "deleted_at": None  # Exclude soft-deleted projects
            }
            
            if status:
                query["status"] = status
            
            result = await self.core_api.metadata_get(
                collection=self.collection,
                query=query,
                skip=skip,
                limit=limit
            )
            
            projects = []
            for doc in result.get("documents", []):
                project_id = str(doc.get("_id", ""))
                job_count = await self._get_job_count(project_id)
                projects.append(self._project_to_dict(doc, job_count=job_count))
            
            total_count = await self.core_api.metadata_count(
                collection=self.collection,
                query=query
            )
            
            return {
                "projects": projects,
                "count": len(projects),
                "total": total_count,
                "skip": skip,
                "limit": limit
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list projects: {str(e)}"
            )
    
    async def get_projects_by_owner(
        self,
        created_by: str,
        skip: int = 0,
        limit: int = 10
    ) -> dict:
        """
        Get projects created by a specific user
        
        Args:
            created_by: User ID (principal subject)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Dictionary with list of projects and pagination info
        """
        try:
            query: Dict[str, Any] = {
                "created_by": created_by,
                "deleted_at": None  # Exclude soft-deleted projects
            }
            
            result = await self.core_api.metadata_get(
                collection=self.collection,
                query=query,
                skip=skip,
                limit=limit
            )
            
            projects = []
            for doc in result.get("documents", []):
                project_id = str(doc.get("_id", ""))
                job_count = await self._get_job_count(project_id)
                projects.append(self._project_to_dict(doc, job_count=job_count))
            
            total_count = await self.core_api.metadata_count(
                collection=self.collection,
                query=query
            )
            
            return {
                "projects": projects,
                "count": len(projects),
                "total": total_count,
                "skip": skip,
                "limit": limit
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get projects by owner: {str(e)}"
            )
    
    # UPDATE
    async def update_project(
        self,
        project_id: str,
        update_data: ProjectUpdateRequest,
        principal: Principal
    ) -> dict:
        """
        Update an existing project
        
        Args:
            project_id: Project ID
            update_data: Update data
            principal: Authenticated principal
            
        Returns:
            Dictionary with updated project data
            
        Raises:
            HTTPException: If update fails or authorization fails
        """
        try:
            # Check authorization
            if not await self.check_authorization(project_id, principal):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to update this project"
                )
            
            # Get existing project
            get_result = await self.core_api.metadata_get(
                collection=self.collection,
                document_id=project_id
            )
            
            if not get_result.get("success") or not get_result.get("document"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with id {project_id} not found"
                )
            
            project_doc = get_result["document"]
            
            # Check if soft-deleted
            if project_doc.get("deleted_at"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with id {project_id} not found"
                )
            
            # Build update dictionary
            if update_data.name is not None:
                project_doc["name"] = update_data.name
            if update_data.description is not None:
                project_doc["description"] = update_data.description
            if update_data.status is not None:
                project_doc["status"] = update_data.status.value if hasattr(update_data.status, 'value') else update_data.status
            if update_data.metadata is not None:
                # Merge metadata with existing
                existing_metadata = project_doc.get("metadata", {})
                existing_metadata.update(update_data.metadata)
                project_doc["metadata"] = existing_metadata
            
            # Always update timestamp
            project_doc["updated_at"] = datetime.utcnow()
            
            # Store updated project
            result = await self.core_api.metadata_put(
                collection=self.collection,
                document_id=project_id,
                document=project_doc,
                upsert=True
            )
            
            if not result.get("success"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update project"
                )
            
            # Get job count
            job_count = await self._get_job_count(project_id)
            
            response = self._project_to_dict(result["document"], job_count=job_count)
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update project: {str(e)}"
            )
    
    # DELETE
    async def delete_project(
        self,
        project_id: str,
        principal: Principal
    ) -> dict:
        """
        Hard delete a project (permanent deletion)
        
        Args:
            project_id: Project ID
            principal: Authenticated principal
            
        Returns:
            Dictionary with deletion result
            
        Raises:
            HTTPException: If deletion fails or authorization fails
        """
        try:
            # Check authorization (only project owner or tenant admin)
            if not await self.check_authorization(project_id, principal):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to delete this project"
                )
            
            # Check if project exists
            if not await self.validate_project_exists(project_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with id {project_id} not found"
                )
            
            # Check if project has jobs
            job_count = await self._get_job_count(project_id)
            if job_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete project with {job_count} associated jobs. Please delete or reassign jobs first."
                )
            
            # Perform hard delete
            result = await self.core_api.metadata_delete(
                collection=self.collection,
                document_id=project_id,
                hard_delete=True
            )
            
            if not result.get("success"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete project"
                )
            
            return {
                "success": True,
                "id": project_id,
                "message": "Project deleted successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete project: {str(e)}"
            )
    
    async def soft_delete_project(self, project_id: str) -> dict:
        """
        Soft delete a project (archive instead of hard delete)
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary with soft deletion result
            
        Raises:
            HTTPException: If soft deletion fails
        """
        try:
            # Check if project exists
            if not await self.validate_project_exists(project_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with id {project_id} not found"
                )
            
            # Get existing project
            get_result = await self.core_api.metadata_get(
                collection=self.collection,
                document_id=project_id
            )
            
            if not get_result.get("success") or not get_result.get("document"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with id {project_id} not found"
                )
            
            project_doc = get_result["document"]
            
            # Update project to archived status with deleted_at timestamp
            project_doc["status"] = "archived"
            project_doc["deleted_at"] = datetime.utcnow()
            project_doc["updated_at"] = datetime.utcnow()
            
            # Store updated project
            result = await self.core_api.metadata_put(
                collection=self.collection,
                document_id=project_id,
                document=project_doc,
                upsert=True
            )
            
            if not result.get("success"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to soft delete project"
                )
            
            return {
                "success": True,
                "id": project_id,
                "message": "Project archived successfully",
                "status": "archived"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to soft delete project: {str(e)}"
            )
    
    # VALIDATION & HELPERS
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
                collection=self.collection,
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
        project_id: str,
        principal: Principal
    ) -> bool:
        """
        Check if principal is authorized to perform operations on the project
        
        Authorization rules:
        - Project owner (created_by matches principal.subject)
        - Tenant admin (principal has admin role for the project's tenant)
        
        Args:
            project_id: Project ID
            principal: Authenticated principal
            
        Returns:
            True if authorized, False otherwise
        """
        try:
            result = await self.core_api.metadata_get(
                collection=self.collection,
                document_id=project_id
            )
            
            if not result.get("success") or not result.get("document"):
                return False
            
            project_doc = result["document"]
            
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

