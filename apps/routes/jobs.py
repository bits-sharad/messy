"""API routes for Jobs CRUD operations"""
from typing import Optional, List
from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from apps.schemas.requests import JobCreateRequest, JobUpdateRequest
from apps.schemas.responses import JobResponse
from apps.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job",
    description="Create a new job with the provided details"
)
async def create_job(job: JobCreateRequest):
    """Create a new job"""
    return await JobService.create_job(job)


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a job by ID",
    description="Retrieve a job by its ID"
)
async def get_job(job_id: str):
    """Get a job by ID"""
    return await JobService.get_job(job_id)


@router.get(
    "/",
    response_model=List[JobResponse],
    status_code=status.HTTP_200_OK,
    summary="List jobs",
    description="List all jobs with optional filtering by project_id and status"
)
async def list_jobs(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by status (draft, published, closed)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return")
):
    """List jobs with optional filters"""
    # Try to get jobs - if database is not connected, the service will handle it
    try:
        result = await JobService.list_jobs(
            project_id=project_id,
            status=status,
            skip=skip,
            limit=limit
        )
        return result
    except Exception as e:
        # Log the error but return empty list to prevent UI crashes
        import sys
        import traceback
        print(f"Error in list_jobs: {type(e).__name__}: {e}", file=sys.stderr)
        traceback.print_exc()
        return []


@router.put(
    "/{job_id}",
    response_model=JobResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a job",
    description="Update an existing job"
)
async def update_job(job_id: str, job_update: JobUpdateRequest):
    """Update a job"""
    return await JobService.update_job(job_id, job_update)


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a job",
    description="Delete a job"
)
async def delete_job(job_id: str):
    """Delete a job"""
    await JobService.delete_job(job_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)

