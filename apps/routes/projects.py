"""API routes for Projects CRUD operations"""
from typing import Optional, List
from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from apps.schemas.requests import ProjectCreateRequest, ProjectUpdateRequest
from apps.schemas.responses import ProjectResponse
from apps.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    description="Create a new project with the provided details"
)
async def create_project(project: ProjectCreateRequest):
    """Create a new project"""
    return await ProjectService.create_project(project)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a project by ID",
    description="Retrieve a project by its ID"
)
async def get_project(project_id: str):
    """Get a project by ID"""
    return await ProjectService.get_project(project_id)


@router.get(
    "/",
    response_model=List[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List projects",
    description="List all projects with optional filtering by tenant_id and status"
)
async def list_projects(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    status: Optional[str] = Query(None, description="Filter by status (active, inactive, archived)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return")
):
    """List projects with optional filters"""
    # Try to get projects - if database is not connected, the service will handle it
    try:
        result = await ProjectService.list_projects(
            tenant_id=tenant_id,
            status=status,
            skip=skip,
            limit=limit
        )
        return result
    except Exception as e:
        # Log the error but return empty list to prevent UI crashes
        import sys
        import traceback
        print(f"Error in list_projects: {type(e).__name__}: {e}", file=sys.stderr)
        traceback.print_exc()
        return []


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a project",
    description="Update an existing project"
)
async def update_project(project_id: str, project_update: ProjectUpdateRequest):
    """Update a project"""
    return await ProjectService.update_project(project_id, project_update)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
    description="Delete a project. Project must not have any associated jobs."
)
async def delete_project(project_id: str):
    """Delete a project"""
    await ProjectService.delete_project(project_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)

