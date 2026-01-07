# Complete Workflow Guide - Job Matching System

This guide provides a comprehensive understanding of how the entire job matching system works, from frontend requests to database operations, including AI/RAG features.

---

## 📋 Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Request Flow - Complete Journey](#request-flow-complete-journey)
3. [Authentication & Authorization Flow](#authentication--authorization-flow)
4. [Database Operations Flow](#database-operations-flow)
5. [AI/RAG Workflow](#airag-workflow)
6. [Frontend-Backend Communication](#frontend-backend-communication)
7. [Component Interactions](#component-interactions)
8. [Development Workflow](#development-workflow)

---

## 🏗️ System Architecture Overview

### **High-Level Architecture**

```
┌─────────────────┐
│   Angular UI    │  (Frontend - Port 4200)
│  (apps/ui/)     │
└────────┬────────┘
         │ HTTP/JSON
         │
         ▼
┌─────────────────────────────────────┐
│      FastAPI Backend                │  (Backend - Port 8000)
│     (apps/main.py)                  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Route Handlers             │  │
│  │  - /projects (apps/routes)   │  │
│  │  - /jobs (apps/routes)       │  │
│  │  - /api/v1/* (apps/api)      │  │
│  │  - /api/v1/ai/* (apps/ai)    │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│  ┌──────────▼───────────────────┐  │
│  │   Service Layer              │  │
│  │  - ProjectService            │  │
│  │  - JobService                │  │
│  │  - RAGService (AI)           │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│  ┌──────────▼───────────────────┐  │
│  │   Core Components            │  │
│  │  - CoreAPIClient             │  │
│  │  - Principal (Auth)          │  │
│  └──────────┬───────────────────┘  │
└─────────────┼───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│      MongoDB Database               │  (Port 27017)
│  Collections:                       │
│  - projects                         │
│  - jobs                             │
│  - (vector store: chroma_db)        │
└─────────────────────────────────────┘
```

### **Folder Structure**

```
mecy_api/
├── apps/
│   ├── main.py                    # FastAPI app entry point
│   ├── core/                      # Core infrastructure
│   │   ├── client.py             # CoreAPIClient - DB abstraction
│   │   ├── principal.py          # Authentication context
│   │   ├── dependencies.py       # FastAPI dependency injection
│   │   └── exceptions.py         # Custom exceptions
│   ├── routes/                    # Basic routes (legacy)
│   │   ├── projects.py
│   │   └── jobs.py
│   ├── api/                       # Modern API routes with auth
│   │   └── routes.py             # /api/v1/* endpoints
│   ├── ai/                        # AI/RAG module
│   │   ├── routes/               # RAG API routes
│   │   ├── services/             # RAG & Mercer services
│   │   ├── schemas/              # AI request/response models
│   │   └── libs/                 # Dummy Mercer library
│   ├── services/                  # Business logic services
│   │   ├── mmc_project.py       # Project service
│   │   └── mmc_jobs.py          # Job service
│   ├── models/                    # Data models
│   │   ├── project.py
│   │   └── job.py
│   ├── schemas/                   # Pydantic schemas
│   │   ├── requests.py           # Request models
│   │   └── responses.py          # Response models
│   ├── database/                  # Database management
│   │   ├── connection.py         # MongoDB connection
│   │   └── seed_data.py          # Dummy data seeding
│   └── ui/                        # Angular frontend
│       └── src/
│           └── app/
│               ├── services/
│               │   └── api.service.ts  # HTTP client
│               └── pages/              # UI components
```

---

## 🔄 Request Flow - Complete Journey

### **Example: Creating a Job**

Let's trace a complete request from UI to database and back:

#### **Step 1: User Action (Frontend)**
```typescript
// apps/ui/src/app/pages/jobs/jobs.component.ts
onCreateJob() {
  const jobData = {
    project_id: "507f1f77bcf86cd799439011",
    title: "Senior Software Engineer",
    description: "We are looking for...",
    job_code: "ENG-001",
    status: "published",
    // ... other fields
  };
  
  this.apiService.createJob(projectId, jobData)
    .subscribe(response => {
      console.log('Job created:', response);
    });
}
```

#### **Step 2: API Service (Frontend HTTP Client)**
```typescript
// apps/ui/src/app/services/api.service.ts
createJob(projectId: string, job: any): Observable<any> {
  return this.http.post<any>(
    `${this.baseUrl}/api/v1/projects/${projectId}/jobs`, 
    job, 
    {
      headers: this.getHeaders()  // Includes X-Principal-Subject, X-Tenant-ID, etc.
    }
  );
}
```

**Headers Sent:**
- `Content-Type: application/json`
- `X-Principal-Subject: ui-user`
- `X-Tenant-ID: default`
- `X-Roles: user`
- `X-Permissions: read,write`

#### **Step 3: FastAPI Route Handler**
```python
# apps/api/routes.py
@router.post("/projects/{project_id}/jobs", ...)
async def create_job(
    project_id: str,
    req: JobCreateRequest,  # Pydantic validates request body
    principal: Principal = Depends(get_principal),  # Extracts from headers
    core_api: CoreAPIClient = Depends(get_core_api)  # DB client
):
    job_service = JobService(core_api)
    result = await job_service.create_job(req, principal)
    return result
```

**What happens:**
1. **Pydantic Validation**: `JobCreateRequest` validates the request body
2. **Dependency Injection**: 
   - `get_principal()` extracts user info from headers
   - `get_core_api()` provides database client
3. **Service Call**: Delegates to `JobService`

#### **Step 4: Service Layer (Business Logic)**
```python
# apps/services/mmc_jobs.py
async def create_job(
    self,
    job_data: JobCreateRequest,
    principal: Principal
) -> dict:
    # 1. Validate project exists
    if not await self.validate_project_exists(job_data.project_id):
        raise ResourceNotFoundError("Project", job_data.project_id)
    
    # 2. Check authorization
    project_result = await self.core_api.metadata_get(...)
    if not principal.can_access_tenant(project_doc.get("tenant_id")):
        raise UnauthorizedError(...)
    
    # 3. Validate job_code uniqueness
    if not await self.validate_job_code_unique(...):
        raise ConflictError(...)
    
    # 4. Build job document
    job_doc = {
        "_id": ObjectId(),
        "project_id": job_data.project_id,
        "title": job_data.title,
        # ... all fields
        "created_by": principal.subject,  # From auth
        "created_at": datetime.utcnow(),
    }
    
    # 5. Save to database
    result = await self.core_api.metadata_put(
        collection="jobs",
        document_id=str(job_doc["_id"]),
        document=job_doc
    )
    
    return self._job_to_dict(result["document"])
```

**Business Logic:**
- **Validation**: Project exists, job_code unique
- **Authorization**: User can access project's tenant
- **Data Transformation**: Converts request → database document
- **Persistence**: Saves via CoreAPIClient

#### **Step 5: CoreAPIClient (Database Abstraction)**
```python
# apps/core/client.py
async def metadata_put(
    self,
    collection: str,
    document_id: str,
    document: Dict[str, Any],
    upsert: bool = True
) -> Dict[str, Any]:
    db = self._get_db()  # Gets MongoDB connection
    coll = db[collection]  # Gets "jobs" collection
    
    obj_id = ObjectId(document_id)
    document["_id"] = obj_id
    
    # Ensure timestamps
    document["created_at"] = datetime.utcnow()
    document["updated_at"] = datetime.utcnow()
    
    # Upsert to MongoDB
    coll.replace_one({"_id": obj_id}, document, upsert=True)
    
    return {
        "success": True,
        "document": document
    }
```

**Database Operations:**
- Converts string ID to MongoDB ObjectId
- Manages timestamps
- Performs upsert operation

#### **Step 6: MongoDB Storage**
```
Database: job_matching_db
Collection: jobs

Document:
{
  "_id": ObjectId("507f1f77bcf86cd799439012"),
  "project_id": "507f1f77bcf86cd799439011",
  "title": "Senior Software Engineer",
  "description": "We are looking for...",
  "job_code": "ENG-001",
  "status": "published",
  "created_by": "ui-user",
  "created_at": ISODate("2024-01-15T10:30:00Z"),
  "updated_at": ISODate("2024-01-15T10:30:00Z"),
  "deleted_at": null
}
```

#### **Step 7: Response Flow Back**

The response follows the same path in reverse:
1. MongoDB → CoreAPIClient: Returns document
2. CoreAPIClient → JobService: Returns dict
3. JobService → Route: Returns JobResponse (validated)
4. Route → FastAPI: Serializes to JSON
5. FastAPI → Angular: HTTP response
6. Angular → Component: Updates UI

---

## 🔐 Authentication & Authorization Flow

### **Principal Extraction**

```python
# apps/core/dependencies.py
def get_principal(
    x_principal_subject: Optional[str] = Header(None, alias="X-Principal-Subject"),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    x_roles: Optional[str] = Header(None, alias="X-Roles"),
    x_permissions: Optional[str] = Header(None, alias="X-Permissions")
) -> Principal:
    if not x_principal_subject:
        raise HTTPException(status_code=401, detail="Missing X-Principal-Subject")
    
    return Principal(
        subject=x_principal_subject,  # User ID
        tenant_id=x_tenant_id,         # Organization ID
        roles=[r.strip() for r in x_roles.split(",")] if x_roles else None,
        permissions=[p.strip() for p in x_permissions.split(",")] if x_permissions else None
    )
```

### **Principal Object**

```python
# apps/core/principal.py
@dataclass
class Principal:
    subject: str              # "user-123"
    tenant_id: Optional[str]  # "tenant-abc"
    roles: Optional[List[str]]      # ["admin", "user"]
    permissions: Optional[List[str]] # ["read", "write"]
    
    def is_tenant_admin(self, tenant_id: Optional[str] = None) -> bool:
        """Check if user is admin for tenant"""
        return "admin" in (self.roles or []) and (
            tenant_id is None or self.tenant_id == tenant_id
        )
    
    def can_access_tenant(self, tenant_id: str) -> bool:
        """Check if user can access tenant"""
        return self.is_tenant_admin(tenant_id) or self.tenant_id == tenant_id
```

### **Authorization Checks**

```python
# Example from JobService
async def check_authorization(self, job_id: str, principal: Principal) -> bool:
    # Get job
    job = await self.core_api.metadata_get("jobs", job_id)
    
    # 1. Check if job owner
    if job["created_by"] == principal.subject:
        return True
    
    # 2. Get project and check project owner
    project = await self.core_api.metadata_get("projects", job["project_id"])
    if project["created_by"] == principal.subject:
        return True
    
    # 3. Check if tenant admin
    if principal.is_tenant_admin(project["tenant_id"]):
        return True
    
    return False
```

---

## 💾 Database Operations Flow

### **Connection Management**

```python
# apps/database/connection.py
class DatabaseManager:
    def connect(self):
        self.client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=3000)
        self.client.server_info()  # Test connection
        self.db = self.client["job_matching_db"]
    
    def get_database(self) -> Database:
        if not self.db:
            raise RuntimeError("Database not connected")
        return self.db

# Singleton instance
db_manager = DatabaseManager()

# In main.py lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    db_manager.connect()  # Startup
    try:
        create_indexes()  # Create MongoDB indexes
    except Exception as e:
        print(f"Index creation: {e}")
    yield
    db_manager.disconnect()  # Shutdown
```

### **CoreAPIClient - Database Abstraction Layer**

The `CoreAPIClient` provides a unified interface for all database operations:

#### **Create/Update (Upsert)**
```python
await core_api.metadata_put(
    collection="jobs",
    document_id="507f1f77bcf86cd799439012",
    document={...},
    upsert=True  # Create if not exists, update if exists
)
```

#### **Read (Single Document)**
```python
result = await core_api.metadata_get(
    collection="jobs",
    document_id="507f1f77bcf86cd799439012"
)
# Returns: {"success": True, "document": {...}}
```

#### **Read (Query Multiple)**
```python
result = await core_api.metadata_get(
    collection="jobs",
    query={"project_id": "507f1f77bcf86cd799439011", "status": "published"},
    skip=0,
    limit=10
)
# Returns: {"success": True, "documents": [...], "count": 5}
```

#### **Delete**
```python
await core_api.metadata_delete(
    collection="jobs",
    document_id="507f1f77bcf86cd799439012",
    hard_delete=False  # False = soft delete (sets deleted_at)
)
```

### **Data Model Structure**

#### **Project Document**
```json
{
  "_id": ObjectId("..."),
  "name": "Q4 Recruitment Drive",
  "description": "Recruitment for Q4 2024",
  "tenant_id": "tenant_123",
  "status": "active",
  "metadata": {"department": "Engineering", "budget": 50000},
  "created_by": "user_456",
  "created_at": ISODate("2024-01-15T10:00:00Z"),
  "updated_at": ISODate("2024-01-15T10:00:00Z"),
  "deleted_at": null  // Soft delete flag
}
```

#### **Job Document**
```json
{
  "_id": ObjectId("..."),
  "project_id": "507f1f77bcf86cd799439011",
  "title": "Senior Software Engineer",
  "description": "We are looking for...",
  "job_code": "ENG-001",
  "status": "published",
  "department": "Engineering",
  "level": "senior",
  "required_skills": ["Python", "FastAPI", "MongoDB"],
  "responsibilities": ["Design APIs", "Code reviews"],
  "metadata": {"remote": true},
  "created_by": "user_456",
  "created_at": ISODate("2024-01-15T11:00:00Z"),
  "updated_at": ISODate("2024-01-15T11:00:00Z"),
  "deleted_at": null
}
```

---

## 🤖 AI/RAG Workflow

### **RAG Service Architecture**

```
┌─────────────────────┐
│   RAG Routes        │  /api/v1/ai/jobs/match-candidate
│  (apps/ai/routes)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   RAGService        │
│  (apps/ai/services) │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌─────────┐  ┌─────────────────┐
│ ChromaDB│  │ Mercer Library  │
│ Vector  │  │ (Dummy/Real)    │
│ Store   │  │                 │
└─────────┘  └─────────────────┘
```

### **Complete RAG Flow: Candidate Matching**

#### **1. API Request**
```python
# POST /api/v1/ai/jobs/match-candidate
{
  "skills": ["Python", "FastAPI", "MongoDB"],
  "experience_summary": "5+ years backend development",
  "education": "BS Computer Science",
  "desired_role": "Senior Software Engineer",
  "years_of_experience": 5
}
```

#### **2. Route Handler**
```python
# apps/ai/routes/rag_routes.py
@router.post("/jobs/match-candidate")
async def match_candidate_to_jobs(
    candidate: CandidateProfileRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    matches = rag_service.match_candidate_to_jobs(
        candidate_profile=candidate.dict(),
        job_ids=None,  # Search all jobs
        limit=10
    )
    return [MatchResultResponse(...) for match in matches]
```

#### **3. RAG Service - Matching Logic**
```python
# apps/ai/services/rag_service.py
def match_candidate_to_jobs(
    self,
    candidate_profile: Dict[str, Any],
    job_ids: Optional[List[str]] = None,
    limit: int = 10,
    use_mercer: Optional[bool] = None
) -> List[MatchResult]:
    
    # Option 1: Try Mercer library first (if available)
    if self.use_mercer and self.mercer_service:
        mercer_matches = self.mercer_service.match_candidate_to_jobs(
            candidate_profile=candidate_profile,
            job_ids=job_ids,
            limit=limit
        )
        if mercer_matches:
            return convert_mercer_to_match_results(mercer_matches)
    
    # Option 2: Fallback to RAG-based semantic matching
    # Create searchable query from candidate profile
    candidate_query = self._create_candidate_query(candidate_profile)
    # "Python FastAPI MongoDB 5+ years backend development Senior Software Engineer"
    
    # Generate embedding
    query_embedding = self.generate_embedding(candidate_query)
    
    # Search ChromaDB for similar jobs
    matches = self.collection.query(
        query_embeddings=[query_embedding],
        n_results=limit,
        where={"status": "published"}
    )
    
    # Calculate detailed scores
    results = []
    for match in matches:
        # Calculate skill overlap
        matched_skills = candidate_skills.intersection(job_skills)
        missing_skills = job_skills - candidate_skills
        
        # Generate match score and reasons
        match_score = calculate_score(match, matched_skills)
        match_reasons = generate_reasons(match_score, matched_skills)
        
        results.append(MatchResult(
            job_id=match["job_id"],
            job_title=match["title"],
            match_score=match_score,
            match_reasons=match_reasons,
            matched_skills=list(matched_skills),
            missing_skills=list(missing_skills)
        ))
    
    return sorted(results, key=lambda x: x.match_score, reverse=True)[:limit]
```

#### **4. Embedding Generation**
```python
def generate_embedding(self, text: str) -> List[float]:
    # Uses sentence-transformers model
    embedding = self.embedding_model.encode(text, normalize_embeddings=True)
    return embedding.tolist()  # [0.123, -0.456, 0.789, ...] (384 dims)
```

#### **5. Vector Search in ChromaDB**
```python
# ChromaDB stores job embeddings
# When job is indexed:
self.collection.add(
    ids=["job_123"],
    embeddings=[[0.123, -0.456, ...]],  # Job embedding
    documents=["Senior Software Engineer Python FastAPI MongoDB..."],
    metadatas=[{"job_id": "job_123", "title": "...", "status": "published"}]
)

# When searching:
results = self.collection.query(
    query_embeddings=[candidate_embedding],  # Candidate query embedding
    n_results=10,  # Top 10 matches
    where={"status": "published"}  # Filter
)
# Returns jobs ordered by similarity (cosine distance)
```

#### **6. Response**
```json
[
  {
    "job_id": "507f1f77bcf86cd799439012",
    "job_title": "Senior Software Engineer",
    "match_score": 0.85,
    "match_reasons": [
      "Excellent semantic match",
      "Matches 4 required skills",
      "Level: senior"
    ],
    "matched_skills": ["Python", "FastAPI", "MongoDB", "Docker"],
    "missing_skills": ["Kubernetes"]
  },
  ...
]
```

### **Other RAG Features**

#### **Job Description Generation**
```python
POST /api/v1/ai/jobs/generate-description
{
  "title": "Senior Software Engineer",
  "department": "Engineering",
  "required_skills": ["Python", "FastAPI"],
  "use_llm": true  # Use OpenAI GPT, or false for template
}

# RAGService generates job description using:
# - Template-based (if use_llm=False)
# - OpenAI GPT-3.5 (if use_llm=True and OPENAI_API_KEY set)
```

#### **Semantic Job Search**
```python
POST /api/v1/ai/jobs/search-semantic
{
  "query": "Python developer with MongoDB experience",
  "limit": 10
}

# Uses semantic similarity search in ChromaDB
# Finds jobs based on meaning, not just keywords
```

#### **Question Answering (RAG)**
```python
POST /api/v1/ai/jobs/{job_id}/ask
{
  "question": "What skills are required for this position?",
  "job_id": "507f1f77bcf86cd799439012"
}

# RAGService:
# 1. Retrieves job context
# 2. Constructs prompt with context
# 3. Queries OpenAI GPT
# 4. Returns answer
```

---

## 🌐 Frontend-Backend Communication

### **API Service Structure**

```typescript
// apps/ui/src/app/services/api.service.ts
export class ApiService {
  private baseUrl = 'http://127.0.0.1:8000';  // From environment.ts
  
  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'X-Principal-Subject': 'ui-user',
      'X-Tenant-ID': 'default',
      'X-Roles': 'user',
      'X-Permissions': 'read,write'
    });
  }
  
  // Example method
  getProjects(tenantId: string = 'default'): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.baseUrl}/projects/`,  // Old route (no auth required)
      { params: { tenant_id: tenantId } }
    );
  }
  
  createProject(project: any): Observable<any> {
    return this.http.post<any>(
      `${this.baseUrl}/api/v1/projects`,  // New route (auth required)
      project,
      { headers: this.getHeaders() }
    );
  }
}
```

### **Component Usage**

```typescript
// apps/ui/src/app/pages/projects/projects.component.ts
export class ProjectsComponent implements OnInit {
  projects: any[] = [];
  
  constructor(private apiService: ApiService) {}
  
  ngOnInit() {
    this.loadProjects();
  }
  
  loadProjects() {
    this.apiService.getProjects('default')
      .subscribe({
        next: (projects) => {
          this.projects = projects;
        },
        error: (error) => {
          console.error('Failed to load projects:', error);
        }
      });
  }
}
```

### **Route Types**

#### **Old Routes (No Auth Required)**
- `GET /projects/` - List projects
- `GET /jobs/` - List jobs
- No authentication headers needed

#### **New Routes (Auth Required)**
- `POST /api/v1/projects` - Create project (needs headers)
- `GET /api/v1/projects/{id}` - Get project
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project
- `POST /api/v1/projects/{id}/jobs` - Create job
- All `/api/v1/*` routes require `X-Principal-Subject` header

#### **AI/RAG Routes (Auth Required)**
- `POST /api/v1/ai/jobs/match-candidate` - Match candidate
- `POST /api/v1/ai/jobs/generate-description` - Generate JD
- `POST /api/v1/ai/jobs/search-semantic` - Semantic search
- `POST /api/v1/ai/jobs/{id}/ask` - Q&A
- `POST /api/v1/ai/jobs/{id}/index` - Index job for search

---

## 🔗 Component Interactions

### **Dependency Graph**

```
main.py
  ├── CORS Middleware
  ├── Database Connection (lifespan)
  │
  ├── routes/projects.router (legacy)
  │   └── services/project_service.py
  │       └── core/client.py
  │           └── database/connection.py
  │
  ├── routes/jobs.router (legacy)
  │   └── services/job_service.py
  │       └── core/client.py
  │
  ├── api/routes.router (/api/v1/*)
  │   ├── Depends(get_principal) → core/dependencies.py
  │   ├── Depends(get_core_api) → core/client.py
  │   ├── services/mmc_project.py
  │   └── services/mmc_jobs.py
  │
  └── ai/routes/rag_routes.router (/api/v1/ai/*)
      ├── Depends(get_principal)
      ├── Depends(get_core_api)
      ├── ai/services/rag_service.py
      │   ├── ai/services/mercer_job_library.py
      │   │   └── ai/libs/dummy_mercer.py (fallback)
      │   ├── sentence_transformers (embeddings)
      │   ├── chromadb (vector store)
      │   └── openai (LLM)
      └── services/mmc_jobs.py (for job data)
```

### **Service Layer Responsibilities**

#### **ProjectService / JobService**
- Business logic validation
- Authorization checks
- Data transformation (request ↔ database)
- Calls CoreAPIClient for persistence

#### **CoreAPIClient**
- Database abstraction layer
- Handles ObjectId conversion
- Manages timestamps
- Provides CRUD operations

#### **RAGService**
- AI/ML operations
- Embedding generation
- Vector search
- LLM integration

#### **MercerJobLibraryService**
- Integration with external Mercer library
- Fallback to dummy implementation
- Job taxonomy and competency models

---

## 🚀 Development Workflow

### **1. Starting the Backend**

```bash
# Terminal 1: Start MongoDB (if not running)
mongod

# Terminal 2: Start FastAPI
cd mecy_api
python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload

# Access:
# - API: http://127.0.0.1:8000
# - Docs: http://127.0.0.1:8000/docs
```

### **2. Starting the Frontend**

```bash
# Terminal 3: Start Angular UI
cd apps/ui
npm install  # First time only
npm start

# Access:
# - UI: http://localhost:4200
```

### **3. Seeding Dummy Data**

```bash
# Terminal: Seed database
python run_seed_data.py

# Creates:
# - Sample projects
# - Sample jobs
# - Dummy principal/user data
```

### **4. Testing API Endpoints**

#### **Using Swagger UI**
- Visit: http://127.0.0.1:8000/docs
- Try endpoints interactively
- View request/response schemas

#### **Using cURL**
```bash
# List projects (no auth)
curl http://127.0.0.1:8000/projects/

# Create project (with auth)
curl -X POST http://127.0.0.1:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -H "X-Principal-Subject: user123" \
  -H "X-Tenant-ID: tenant456" \
  -d '{
    "name": "My Project",
    "tenant_id": "tenant456",
    "status": "active",
    "created_by": "user123"
  }'

# Match candidate (AI)
curl -X POST http://127.0.0.1:8000/api/v1/ai/jobs/match-candidate \
  -H "Content-Type: application/json" \
  -H "X-Principal-Subject: user123" \
  -d '{
    "skills": ["Python", "FastAPI"],
    "experience_summary": "5 years backend",
    "years_of_experience": 5
  }'
```

### **5. Adding a New Feature**

#### **Example: Add a "Favorite Jobs" Feature**

**Step 1: Create Database Model**
```python
# apps/models/favorite.py
class Favorite:
    def __init__(self, user_id: str, job_id: str):
        self.user_id = user_id
        self.job_id = job_id
        self.created_at = datetime.utcnow()
```

**Step 2: Create Service**
```python
# apps/services/favorite_service.py
class FavoriteService:
    def __init__(self, core_api: CoreAPIClient):
        self.core_api = core_api
    
    async def add_favorite(self, user_id: str, job_id: str, principal: Principal):
        # Authorization check
        if principal.subject != user_id:
            raise UnauthorizedError(...)
        
        # Create favorite document
        favorite_doc = {
            "_id": ObjectId(),
            "user_id": user_id,
            "job_id": job_id,
            "created_at": datetime.utcnow()
        }
        
        # Save via CoreAPIClient
        return await self.core_api.metadata_put(
            collection="favorites",
            document_id=str(favorite_doc["_id"]),
            document=favorite_doc
        )
```

**Step 3: Create Schema**
```python
# apps/schemas/requests.py
class FavoriteCreateRequest(BaseModel):
    job_id: str
```

**Step 4: Create Route**
```python
# apps/api/routes.py
@router.post("/users/{user_id}/favorites")
async def add_favorite(
    user_id: str,
    req: FavoriteCreateRequest,
    principal: Principal = Depends(get_principal),
    core_api: CoreAPIClient = Depends(get_core_api)
):
    favorite_service = FavoriteService(core_api)
    return await favorite_service.add_favorite(user_id, req.job_id, principal)
```

**Step 5: Add Frontend Method**
```typescript
// apps/ui/src/app/services/api.service.ts
addFavorite(userId: string, jobId: string): Observable<any> {
  return this.http.post<any>(
    `${this.baseUrl}/api/v1/users/${userId}/favorites`,
    { job_id: jobId },
    { headers: this.getHeaders() }
  );
}
```

---

## 🎯 Key Patterns & Conventions

### **1. Dependency Injection**
FastAPI uses dependency injection for reusable components:
```python
async def my_endpoint(
    principal: Principal = Depends(get_principal),  # Injected
    core_api: CoreAPIClient = Depends(get_core_api)  # Injected
):
    pass
```

### **2. Service Layer Pattern**
- Routes handle HTTP concerns (status codes, validation)
- Services handle business logic
- CoreAPIClient handles database operations

### **3. Error Handling**
```python
try:
    # Operation
except ResourceNotFoundError:
    raise  # Re-raise custom exceptions
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

### **4. Soft Delete Pattern**
- Set `deleted_at` timestamp instead of hard delete
- Filter out soft-deleted documents in queries
- Allows data recovery and audit trails

### **5. Multi-tenancy**
- Every project has a `tenant_id`
- Authorization checks tenant access
- Data isolation by tenant

---

## 📚 Summary: Complete Request Journey

```
1. User clicks button in Angular UI
   ↓
2. Component calls ApiService method
   ↓
3. HTTP request sent with headers
   ↓
4. FastAPI receives request
   ↓
5. Route handler validates request (Pydantic)
   ↓
6. Dependency injection: get_principal(), get_core_api()
   ↓
7. Service layer: Business logic + authorization
   ↓
8. CoreAPIClient: Database abstraction
   ↓
9. MongoDB: Data persistence
   ↓
10. Response flows back through layers
    ↓
11. Angular receives JSON response
    ↓
12. Component updates UI
```

This workflow ensures:
- ✅ **Separation of Concerns**: Each layer has a specific responsibility
- ✅ **Reusability**: Services can be used by multiple routes
- ✅ **Testability**: Easy to mock dependencies
- ✅ **Security**: Authorization at every layer
- ✅ **Scalability**: Easy to add new features

---

## 🔧 Environment Variables

```bash
# .env file
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=job_matching_db
OPENAI_API_KEY=sk-...  # For RAG LLM features
MERCER_API_KEY=...     # For Mercer library (optional)
```

---

## 📖 Next Steps

1. **Explore the Code**: Start with `apps/main.py` and trace through a request
2. **Read the Docs**: Check `apps/ai/RAG_README.md` for AI features
3. **Run the Project**: Follow `RUN_PROJECT.md`
4. **Experiment**: Try creating new endpoints using the patterns above
5. **Understand MongoDB**: Review `apps/database/connection.py` and MongoDB queries

---

**You now have a complete understanding of the system workflow!** 🎉

Use this guide as a reference when working on similar projects or extending this one.

