"""API routes for Projects and Jobs with CoreAPIClient and Principal"""
from typing import Optional, List
from fastapi import APIRouter, Query, Depends, status
from fastapi.responses import JSONResponse

from apps.core.client import CoreAPIClient
from apps.core.principal import Principal
from apps.core.dependencies import get_core_api, get_principal
from apps.schemas.requests import ProjectCreateRequest, ProjectUpdateRequest, JobCreateRequest, JobUpdateRequest
from apps.schemas.responses import ProjectResponse, JobResponse
from apps.services.mmc_project import ProjectService
from apps.services.mmc_jobs import JobService
from apps.core.audit import AuditTrail

router = APIRouter(prefix="/api/v1", tags=["Projects & Jobs"])

# Initialize audit trail (in production, this would be a singleton)
audit = AuditTrail()


# PROJECT ENDPOINTS

@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    description="Create a new project with the provided details"
)
async def create_project(
    req: ProjectCreateRequest,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(get_core_api)
):
    """Create a new project"""
    project_service = ProjectService(core_api)
    result = await project_service.create_project(req, principal)
    
    # Audit log
    audit.add("project_created", {
        "project_id": result["id"],
        "name": result["name"],
        "tenant_id": result["tenant_id"]
    }, resource_type="project", resource_id=result["id"], principal=principal.subject)
    
    return result


@router.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get project details by ID",
    description="Get project details by ID"
)
async def get_project(
    project_id: str,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(get_core_api)
):
    """Get project details by ID"""
    project_service = ProjectService(core_api)
    result = await project_service.get_project(project_id)
    return result


@router.get(
    "/projects",
    response_model=List[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List projects for a tenant with pagination",
    description="List projects for a tenant with pagination"
)
async def list_projects(
    tenant_id: str = Query(..., description="Tenant ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(get_core_api)
):
    """List projects for a tenant with pagination"""
    project_service = ProjectService(core_api)
    result = await project_service.list_projects(
        tenant_id=tenant_id,
        skip=skip,
        limit=limit,
        status=status
    )
    # Return list of projects (not the dict wrapper)
    return result.get("projects", [])


@router.put(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update project details",
    description="Update project details"
)
async def update_project(
    project_id: str,
    req: ProjectUpdateRequest,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(get_core_api)
):
    """Update project details"""
    project_service = ProjectService(core_api)
    result = await project_service.update_project(project_id, req, principal)
    
    # Audit log
    audit.add("project_updated", {
        "project_id": project_id,
        "updates": req.dict(exclude_unset=True)
    }, resource_type="project", resource_id=project_id, principal=principal.subject)
    
    return result


@router.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete (archive) a project",
    description="Delete (archive) a project"
)
async def delete_project(
    project_id: str,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(get_core_api)
):
    """Delete (archive) a project"""
    project_service = ProjectService(core_api)
    result = await project_service.soft_delete_project(project_id)
    
    # Audit log
    audit.add("project_deleted", {
        "project_id": project_id
    }, resource_type="project", resource_id=project_id, principal=principal.subject)
    
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


# JOB ENDPOINTS

@router.post(
    "/projects/{project_id}/jobs",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job within a project",
    description="Create a new job within a project"
)
async def create_job(
    project_id: str,
    req: JobCreateRequest,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(get_core_api)
):
    """Create a new job within a project"""
    # Ensure project_id in request matches path parameter
    if req.project_id != project_id:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="project_id in request body must match path parameter"
        )
    
    job_service = JobService(core_api)
    result = await job_service.create_job(req, principal)
    
    # Audit log
    audit.add("job_created", {
        "job_id": result["id"],
        "project_id": result["project_id"],
        "job_code": result["job_code"],
        "title": result["title"]
    }, resource_type="job", resource_id=result["id"], principal=principal.subject)
    
    return result


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    status_code=status.HTTP_200_OK,
    summary="Get job details by ID",
    description="Get job details by ID"
)
async def get_job(
    job_id: str,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(get_core_api)
):
    """Get job details by ID"""
    job_service = JobService(core_api)
    result = await job_service.get_job(job_id)
    return result


@router.get(
    "/projects/{project_id}/jobs",
    response_model=List[JobResponse],
    status_code=status.HTTP_200_OK,
    summary="List jobs in a project with pagination",
    description="List jobs in a project with pagination"
)
async def list_jobs(
    project_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(get_core_api)
):
    """List jobs in a project with pagination"""
    job_service = JobService(core_api)
    result = await job_service.list_jobs(
        project_id=project_id,
        skip=skip,
        limit=limit,
        status=status
    )
    # Return list of jobs (not the dict wrapper)
    return result.get("jobs", [])


@router.put(
    "/jobs/{job_id}",
    response_model=JobResponse,
    status_code=status.HTTP_200_OK,
    summary="Update job details",
    description="Update job details"
)
async def update_job(
    job_id: str,
    req: JobUpdateRequest,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(get_core_api)
):
    """Update job details"""
    job_service = JobService(core_api)
    result = await job_service.update_job(job_id, req, principal)
    
    # Audit log
    audit.add("job_updated", {
        "job_id": job_id,
        "updates": req.dict(exclude_unset=True)
    }, resource_type="job", resource_id=job_id, principal=principal.subject)
    
    return result


@router.delete(
    "/jobs/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete (close) a job posting",
    description="Delete (close) a job posting"
)
async def delete_job(
    job_id: str,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(get_core_api)
):
    """Delete (close) a job posting"""
    # Check authorization before soft delete
    job_service = JobService(core_api)
    if not await job_service.check_authorization(job_id, principal):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this job"
        )
    
    result = await job_service.soft_delete_job(job_id)
    
    # Audit log
    audit.add("job_deleted", {
        "job_id": job_id
    }, resource_type="job", resource_id=job_id, principal=principal.subject)
    
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


# SEARCH ENDPOINT (BONUS)

@router.get(
    "/jobs/search",
    response_model=List[JobResponse],
    status_code=status.HTTP_200_OK,
    summary="Search jobs by title, description, or job_code",
    description="Search jobs by title, description, or job_code"
)
async def search_jobs(
    q: str = Query(..., description="Search query string"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(get_core_api)
):
    """Search jobs by title, description, or job_code"""
    job_service = JobService(core_api)
    
    filters = {}
    if project_id:
        filters["project_id"] = project_id
    
    result = await job_service.search_jobs(query=q, filters=filters if filters else None)
    
    # Return list of jobs (not the dict wrapper)
    return result.get("jobs", [])

