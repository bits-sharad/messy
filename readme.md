# CRUD Operations Implementation Plan: Projects & Jobs

## Overview
This document outlines the implementation plan for creating CRUD (Create, Read, Update, Delete) operations for **Projects** and **Jobs** entities in the MMC Job Matching Model API.

---

## 1. Data Models & Schemas

### 1.1 Project Entity

#### Schema Definition Location
`apps/schemas/requests.py` and `apps/schemas/responses.py`.

#### Required Fields
```python
# ProjectCreateRequest
- name: str (required, 1-255 characters)
- description: str (optional, max 2000 characters)
- tenant_id: str (required, reference to tenant/organization)
- status: str (required, enum: 'active', 'inactive', 'archived')
- metadata: dict (optional, key-value pairs for extensibility)
- created_by: str (required, principal subject/user ID)

# ProjectResponse
- id: str (MongoDB ObjectId as string)
- name: str
- description: str
- tenant_id: str
- status: str
- metadata: dict
- created_by: str
- created_at: datetime (ISO 8601 format)
- updated_at: datetime
- job_count: int (number of jobs in project, optional)

# ProjectUpdateRequest
- name: str (optional)
- description: str (optional)
- status: str (optional)
- metadata: dict (optional, merge with existing)

```

### 1.2 Job Entity

#### Schema Definition Location

`apps/schemas/requests.py` and `apps/schemas/responses.py`.

#### Required Fields

```python
# JobCreateRequest
- project_id: str (required, reference to Project)
- title: str (required, 1-255 characters)
- description: str (optional)
- job_code: str (required, unique within project)
- status: str (required, enum: 'draft', 'published', 'closed')
- department: str (optional)
- level: str (optional, enum: 'entry', 'mid', 'senior', 'lead')
- required_skills: list[str] (optional, skill tags)
- responsibilities: list[str] (optional)
- metadata: dict (optional)
- created_by: str (required, principal subject/user ID)

# JobResponse
- id: str (MongoDB ObjectId as string)
- project_id: str
- title: str
- description: str
- job_code: str
- status: str
- department: str
- level: str
- required_skills: list[str]
- responsibilities: list[str]
- metadata: dict
- created_by: str
- created_at: datetime
- updated_at: datetime
- match_count: int (optional, number of candidates matched)

# JobUpdateRequest
- title: str (optional)
- description: str (optional)
- status: str (optional)
- department: str (optional)
- level: str (optional)
- required_skills: list[str] (optional, replace/merge strategy to be decided)
- responsibilities: list[str] (optional)
- metadata: dict (optional)

```

---

## 2. Service Layer Implementation

### 2.1 Project Service

**File:** `apps/services/mmc_project.py`.

#### Methods to Implement

```python
class ProjectService:
    def __init__(self, core_api: CoreAPIClient)

    # CREATE
    async def create_project(self, project_data: ProjectCreateRequest, principal: Principal) -> dict

    # READ
    async def get_project(self, project_id: str) -> dict
    async def list_projects(self, tenant_id: str, skip: int = 0, limit: int = 10,
                            status: str | None = None) -> dict
    async def get_projects_by_owner(self, created_by: str, skip: int = 0, limit: int = 10) -> dict

    # UPDATE
    async def update_project(self, project_id: str, update_data: ProjectUpdateRequest,
                             principal: Principal) -> dict

    # DELETE
    async def delete_project(self, project_id: str, principal: Principal) -> dict
    async def soft_delete_project(self, project_id: str) -> dict  # Archive instead of hard delete

    # VALIDATION & HELPERS
    async def validate_project_exists(self, project_id: str) -> bool
    async def check_authorization(self, project_id: str, principal: Principal) -> bool

```

#### Storage Strategy

* Use `CoreAPIClient.metadata_put()` to store project documents.
* Use `CoreAPIClient.metadata_get()` to retrieve project documents.
* MongoDB collection: **`projects`**.
* Document structure: Include timestamps, audit info, soft-delete flag.

#### Authorization Rules

* **Create:** Any authenticated user (with valid principal).
* **Read:** Project owner or tenant admins (check `created_by` and `tenant_id`).
* **Update:** Project owner or tenant admins.
* **Delete:** Project owner or tenant admins only.

### 2.2 Job Service

**File:** `apps/services/mmc_jobs.py`.

#### Methods to Implement

```python
class JobService:
    def __init__(self, core_api: CoreAPIClient)

    # CREATE
    async def create_job(self, job_data: JobCreateRequest, principal: Principal) -> dict

    # READ
    async def get_job(self, job_id: str) -> dict
    async def list_jobs(self, project_id: str, skip: int = 0, limit: int = 10,
                        status: str | None = None) -> dict
    async def list_all_jobs(self, tenant_id: str, skip: int = 0, limit: int = 10) -> dict
    async def search_jobs(self, query: str, filters: dict | None = None) -> dict

    # UPDATE
    async def update_job(self, job_id: str, update_data: JobUpdateRequest,
                         principal: Principal) -> dict

    # DELETE
    async def delete_job(self, job_id: str, principal: Principal) -> dict
    async def soft_delete_job(self, job_id: str) -> dict  # Mark as closed

    # VALIDATION & HELPERS
    async def validate_job_code_unique(self, project_id: str, job_code: str) -> bool
    async def validate_project_exists(self, project_id: str) -> bool
    async def check_authorization(self, job_id: str, principal: Principal) -> bool
    async def get_job_count(self, project_id: str) -> int

```

#### Storage Strategy

* Use `CoreAPIClient.metadata_put()` to store job documents.
* Use `CoreAPIClient.metadata_get()` to retrieve job documents.
* MongoDB collection: **`jobs`**.
* Document structure: Include project_id reference, timestamps, audit info.

#### Authorization Rules

* **Create:** User must have access to the target project.
* **Read:** User must have access to the project this job belongs to.
* **Update:** Job owner or project owner.
* **Delete:** Job owner or project owner.
* Use job's `project_id` to validate access through ProjectService.

---

## 3. Route/API Endpoint Implementation

### 3.1 Project Endpoints

**File:** `apps/api/routes.py`.

```python
# CREATE
@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    req: ProjectCreateRequest,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(_core),
)
"""Create a new project"""

# READ - Get single project
@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(_core),
)
"""Get project details by ID"""

# READ - List projects by tenant
@router.get("/projects", response_model=list[ProjectResponse])
async def list_projects(
    tenant_id: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: str | None = Query(None),
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(_core),
)
"""List projects for a tenant with pagination"""

# UPDATE
@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    req: ProjectUpdateRequest,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(_core),
)
"""Update project details"""

# DELETE
@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(_core),
)
"""Delete (archive) a project"""

```

### 3.2 Job Endpoints

**File:** `apps/api/routes.py`.

```python
# CREATE
@router.post("/projects/{project_id}/jobs", response_model=JobResponse)
async def create_job(
    project_id: str,
    req: JobCreateRequest,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(_core),
)
"""Create a new job within a project"""

# READ - Get single job
@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(_core),
)
"""Get job details by ID"""

# READ - List jobs by project
@router.get("/projects/{project_id}/jobs", response_model=list[JobResponse])
async def list_jobs(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: str | None = Query(None),
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(_core),
)
"""List jobs in a project with pagination"""

# UPDATE
@router.put("/jobs/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    req: JobUpdateRequest,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(_core),
)
"""Update job details"""

# DELETE
@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(_core),
)
"""Delete (close) a job posting"""

# SEARCH (BONUS)
@router.get("/jobs/search", response_model=list[JobResponse])
async def search_jobs(
    q: str = Query(...),
    project_id: str | None = Query(None),
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(_core),
)
"""Search jobs by title, description, or job_code"""

```

---

## 4. Error Handling & Validation

### 4.1 Common Exceptions

Implement custom exceptions in `apps/core/exceptions.py` or extend existing error handling:

```python
- ResourceNotFoundError (404): Project/Job not found
- UnauthorizedError (403): User lacks permissions
- ValidationError (400): Invalid request data
- ConflictError (409): Duplicate job_code, etc.
- InternalServerError (500): Core API failures

```

### 4.2 Validation Rules

* **Project Name:** 1-255 chars, unique per tenant optional.
* **Job Code:** Alphanumeric, underscore allowed, unique within project.
* **Status Values:** Must match enum constraints.
* **Foreign Keys:** Validate project exists when creating jobs.
* **Timestamps:** Auto-generated, ISO 8601 format.
* **Authorization:** Always check user has access to parent project/tenant.

---

## 5. Audit & Logging

### 5.1 Audit Trail Integration

Use existing `AuditTrail` class from `apps/core/audit.py`.

```python
audit = AuditTrail()
audit.add("project_created", {
    "project_id": project_id,
    "created_by": principal.subject,
    "name": project_data.name
})
audit.add("project_updated", {...})
audit.add("project_deleted", {...})

```

### 5.2 Logging

Use `apps.core.logging` for structured logging:

* Log all CRUD operations.
* Log authorization failures.
* Include principal/user info.
* Track performance metrics.

---

## 6. Testing Requirements

### 6.1 Unit Tests

Create tests in `tests/`:

* `test_project_service.py`: Service layer logic.
* `test_job_service.py`: Job service logic.
* `test_routes_projects.py`: API endpoints.
* `test_routes_jobs.py`: Job API endpoints.

### 6.2 Test Coverage

* [x] Happy path (successful CRUD)
* [x] Authorization failures (403)
* [x] Not found (404)
* [x] Validation errors (400)
* [x] Duplicate constraints
* [x] Cascade operations (deleting project affects jobs)

---

## 7. Implementation Sequence

### Phase 1: Setup (1-2 hours)

1. Create request/response schemas in `apps/schemas/requests.py`, `apps/schemas/responses.py`.
2. Update exception handling if needed.
3. Create service file stubs with docstrings.

### Phase 2: Service Layer (4-6 hours)

1. Implement `ProjectService` with full CRUD.
2. Implement `ProjectService` authorization checks.
3. Implement `JobService` with full CRUD.
4. Implement `JobService` authorization checks.
5. Add comprehensive logging and audit trail.

### Phase 3: API Routes (3-4 hours)

1. Implement project endpoints.
2. Implement job endpoints.
3. Add request validation (FastAPI dependencies).
4. Add error responses and status codes.

### Phase 4: Testing (4-6 hours)

1. Unit tests for services.
2. Integration tests for routes.
3. Authorization/permission tests.
4. Edge case testing.

### Phase 5: Documentation & Review (1-2 hours)

1. Update API documentation.
2. Add docstrings to all functions.
3. Create example requests/responses.
4. Code review with team.

---

## 8. Key Considerations

### 8.1 Concurrency & Race Conditions

* **Job code uniqueness:** Use Core API metadata constraints.
* **Project deletion:** Implement cascade logic or prevent if jobs exist.

### 8.2 Performance

* Add pagination to all list endpoints (skip/limit).
* Consider indexing on `project_id`, `tenant_id`, `created_by`.
* Cache frequently accessed projects/jobs.

### 8.3 Data Consistency

* Validate foreign keys (project_id) before creating jobs.
* Use soft deletes (status='archived') for audit trails.
* Implement cascading updates where appropriate.

### 8.4 Security

* Always check user authorization (principal).
* Validate tenant_id matches user's tenant.
* Sanitize user inputs (avoid injection).
* Rate limit creation endpoints if needed.

---

## 9. Dependencies & Integration Points

### 9.1 External Services

* **CoreAPIClient:** Used for metadata CRUD operations.
* **principal:** From `apps.core.security` for user context.
* **AuditTrail:** From `apps.core.audit` for logging operations.

### 9.2 Pydantic Models

* All request/response models should use Pydantic `BaseModel`.
* Use `Field()` for validation and documentation.
* Support Optional fields appropriately.

---

## 10. Example Usage (Developer Reference)

```python
# Creating a project
project_data = ProjectCreateRequest(
    name="Q1 2025 Hiring",
    description="Year-end hiring initiative",
    tenant_id="tenant_123",
    status="active"
)
project_service = ProjectService(core_api)
new_project = await project_service.create_project(project_data, principal)

# Creating a job in the project
job_data = JobCreateRequest(
    project_id=new_project["id"],
    title="Senior Software Engineer",
    job_code="ENG-001",
    status="published",
    required_skills=["Python", "FastAPI", "MongoDB"]
)
job_service = JobService(core_api)
new_job = await job_service.create_job(job_data, principal)

# Listing jobs
jobs = await job_service.list_jobs(project_id=new_project["id"])

# Updating a job
update_data = JobUpdateRequest(
    status="closed"
)
updated_job = await job_service.update_job(job_id=new_job["id"],
                                           update_data=update_data,
                                           principal=principal)

```

---

## Appendix: File Checklist

* [x] `apps/schemas/requests.py` - Add ProjectCreateRequest, JobCreateRequest, etc..
* [x] `apps/schemas/responses.py` - Add ProjectResponse, JobResponse.
* [x] `apps/services/mmc_project.py` - Implement ProjectService.
* [x] `apps/services/mmc_jobs.py` - Implement JobService.
* [x] `apps/api/routes.py` - Add all project and job endpoints.
* [x] `apps/core/exceptions.py` - Add custom exceptions.
* [x] `apps/core/audit.py` - Add AuditTrail class.
* [x] `apps/core/client.py` - Add CoreAPIClient.
* [x] `apps/core/principal.py` - Add Principal class.
* [x] `apps/core/dependencies.py` - Add dependency injection functions.
* [ ] `tests/test_project_service.py` - Unit tests.
* [ ] `tests/test_job_service.py` - Unit tests.
* [ ] `tests/test_routes_projects.py` - Integration tests.
* [ ] `tests/test_routes_jobs.py` - Integration tests.
* [ ] Update `README.md` with API documentation.

```

```