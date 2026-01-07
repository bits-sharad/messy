# Transfer RAG and GenAI Files to Your Project

This guide lists all files you need to transfer to add RAG (Retrieval-Augmented Generation) and GenAI capabilities to your original project.

---

## 📦 **Complete Package to Transfer**

Transfer the entire `apps/ai/` folder to your project. This folder is self-contained and includes all RAG/GenAI functionality.

---

## 📁 **Required Files Structure**

```
your_project/
└── apps/
    └── ai/                           # ← Transfer this entire folder
        ├── __init__.py
        ├── services/
        │   ├── __init__.py
        │   ├── rag_service.py          # Core RAG service (ESSENTIAL)
        │   └── mercer_job_library.py   # Mercer integration (ESSENTIAL)
        ├── routes/
        │   ├── __init__.py
        │   └── rag_routes.py           # API endpoints (ESSENTIAL)
        ├── schemas/
        │   ├── __init__.py
        │   ├── requests.py             # Request models (ESSENTIAL)
        │   └── responses.py            # Response models (ESSENTIAL)
        ├── libs/
        │   ├── __init__.py
        │   └── dummy_mercer.py         # Dummy Mercer for dev (ESSENTIAL)
        └── requirements-rag.txt        # Dependencies (ESSENTIAL)
```

---

## ✅ **Files You MUST Transfer**

### 1. **Core RAG Service** (Critical)
```
apps/ai/services/rag_service.py
```
- **Purpose**: Main RAG service implementation
- **Features**: 
  - Semantic embeddings generation
  - Vector database (ChromaDB) management
  - Job indexing and semantic search
  - Candidate-job matching
  - LLM integration (OpenAI) for job description generation
  - Question answering using RAG
- **Dependencies**: sentence-transformers, chromadb, openai (optional)

### 2. **Mercer Job Library Integration** (Critical)
```
apps/ai/services/mercer_job_library.py
```
- **Purpose**: Integration with Mercer Job Library (or dummy fallback)
- **Features**: 
  - Hybrid matching (Mercer + RAG fallback)
  - Job taxonomy and competency models
  - Job enrichment with Mercer data
- **Dependencies**: Can use dummy implementation if Mercer library unavailable

### 3. **API Routes** (Critical)
```
apps/ai/routes/rag_routes.py
```
- **Purpose**: FastAPI routes/endpoints for RAG features
- **Endpoints**:
  - `POST /api/v1/ai/jobs/match-candidate` - Match candidates to jobs
  - `POST /api/v1/ai/jobs/generate-description` - Generate job descriptions
  - `POST /api/v1/ai/jobs/search-semantic` - Semantic job search
  - `POST /api/v1/ai/jobs/{job_id}/ask` - Q&A about jobs
  - `POST /api/v1/ai/jobs/{job_id}/index` - Index jobs for semantic search

### 4. **Request Schemas** (Critical)
```
apps/ai/schemas/requests.py
```
- **Purpose**: Pydantic models for API request bodies
- **Contains**:
  - `CandidateProfileRequest`
  - `JobDescriptionGenerationRequest`
  - `SemanticJobSearchRequest`
  - `JobQuestionRequest`

### 5. **Response Schemas** (Critical)
```
apps/ai/schemas/responses.py
```
- **Purpose**: Pydantic models for API responses
- **Contains**:
  - `MatchResultResponse`
  - `JobDescriptionResponse`
  - `SemanticSearchResultResponse`
  - `JobQuestionResponse`

### 6. **Dummy Mercer Library** (Critical)
```
apps/ai/libs/dummy_mercer.py
```
- **Purpose**: Mock implementation when real Mercer library is unavailable
- **Features**: Provides dummy `JobLibrary` and `JobMatcher` classes for development

### 7. **Dependencies File** (Critical)
```
apps/ai/requirements-rag.txt
```
- **Purpose**: Lists all Python packages needed for RAG/GenAI
- **Contains**:
  - sentence-transformers (embeddings)
  - chromadb (vector database)
  - openai (LLM API)
  - numpy, torch (dependencies)
  - PyPDF2, pdfplumber (PDF processing)

---

## 🔧 **Optional Supporting Files**

### 8. **PDF Processing Service** (Optional - if you need PDF extraction)
```
apps/services/pdf_service.py
apps/services/document_service.py
apps/routes/document_routes.py
```
- **Purpose**: Extract text from PDFs, generate embeddings, store processed content
- **Use case**: If you want to process job documents/resumes from PDFs

---

## 📋 **Integration Steps**

### Step 1: Copy Files
Copy the entire `apps/ai/` folder to your project:
```bash
cp -r apps/ai /path/to/your/project/apps/
```

### Step 2: Install Dependencies
```bash
cd /path/to/your/project
pip install -r apps/ai/requirements-rag.txt
```

### Step 3: Update Your Main App
In your `apps/main.py` (or equivalent), add:

```python
from apps.ai.routes import rag_routes

# Include RAG routes
app.include_router(rag_routes.router)
```

### Step 4: Set Environment Variables
Create or update your `.env` file:

```bash
# Optional: For LLM features (OpenAI)
OPENAI_API_KEY=your-openai-api-key-here

# Optional: For ChromaDB storage location
CHROMA_PERSIST_DIR=./chroma_db

# Optional: For Mercer library (if using real implementation)
MERCER_API_KEY=your-mercer-key
MERCER_API_URL=https://api.mercer.com
```

### Step 5: Update Import Paths (if needed)
If your project structure differs, update imports in:

- `apps/ai/routes/rag_routes.py` - Update job service import if different
- `apps/ai/services/rag_service.py` - Usually no changes needed
- `apps/ai/services/mercer_job_library.py` - Usually no changes needed

**Common import to check:**
```python
# In rag_routes.py, update this if your job service is in a different location:
from apps.services.mmc_jobs import JobService  # ← Change if needed
# OR
from apps.services.job_service import JobService  # ← Your path
```

---

## 🎯 **Quick Checklist**

- [ ] Copy `apps/ai/` folder to your project
- [ ] Install dependencies: `pip install -r apps/ai/requirements-rag.txt`
- [ ] Add `app.include_router(rag_routes.router)` to your main app
- [ ] Set `OPENAI_API_KEY` in `.env` (optional, for LLM features)
- [ ] Test endpoints at `http://localhost:8000/docs`
- [ ] Verify "AI & RAG" section appears in Swagger UI

---

## 🔍 **What Each File Does**

| File | Purpose | Can I Skip? |
|------|---------|-------------|
| `rag_service.py` | Core RAG logic | ❌ NO - Essential |
| `mercer_job_library.py` | Mercer integration | ❌ NO - Essential |
| `rag_routes.py` | API endpoints | ❌ NO - Essential |
| `requests.py` | Request models | ❌ NO - Essential |
| `responses.py` | Response models | ❌ NO - Essential |
| `dummy_mercer.py` | Dummy library | ❌ NO - Essential (fallback) |
| `requirements-rag.txt` | Dependencies | ❌ NO - Essential |
| PDF services | PDF processing | ✅ YES - Optional |

---

## 🚀 **Testing After Transfer**

1. **Start your server:**
   ```bash
   python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Check Swagger UI:**
   - Open: http://127.0.0.1:8000/docs
   - Look for "AI & RAG" section
   - You should see 5 endpoints

3. **Test an endpoint:**
   ```bash
   curl -X POST "http://127.0.0.1:8000/api/v1/ai/jobs/search-semantic" \
     -H "Content-Type: application/json" \
     -d '{"query": "software engineer", "limit": 5}'
   ```

---

## 🔗 **Dependencies on Other Files**

The RAG/GenAI module may depend on:

1. **Job Service** - To fetch job data
   - Expected location: `apps/services/mmc_jobs.py` or `apps/services/job_service.py`
   - **Fix**: Update import in `apps/ai/routes/rag_routes.py`

2. **Database Connection** - If jobs are stored in database
   - The RAG service works independently but routes may need database access

3. **Core Client/Principal** - For authentication (optional)
   - Expected: `apps/core/client.py`, `apps/core/principal.py`, `apps/core/dependencies.py`
   - **Fix**: Remove or update dependency injection in `rag_routes.py` if not using

---

## 💡 **Minimal Integration (Without Authentication)**

If your project doesn't have the `apps/core/` module, modify `apps/ai/routes/rag_routes.py`:

**Remove these lines:**
```python
from apps.core.client import CoreAPIClient
from apps.core.principal import Principal
from apps.core.dependencies import get_core_api, get_principal
```

**Update route decorators:**
```python
# Change from:
@router.post("/jobs/match-candidate", dependencies=[Depends(get_principal)])

# To:
@router.post("/jobs/match-candidate")
```

**Remove dependency parameters:**
```python
# Remove these from route functions:
core_api: CoreAPIClient = Depends(get_core_api),
principal: Principal = Depends(get_principal),
```

---

## 📊 **Feature Summary**

After transferring, you'll have:

✅ **Semantic Job Search** - Find jobs using natural language queries  
✅ **Candidate Matching** - Match candidates to jobs using RAG + Mercer  
✅ **Job Description Generation** - Generate job descriptions using LLM  
✅ **Question Answering** - Ask questions about jobs using RAG  
✅ **Job Indexing** - Index jobs in vector database for semantic search  

---

## 🆘 **Troubleshooting**

### Import Errors
- **Error**: `ModuleNotFoundError: No module named 'apps.ai'`
  - **Fix**: Ensure `apps/ai/` folder is in your project root

### Missing Dependencies
- **Error**: `ModuleNotFoundError: No module named 'sentence_transformers'`
  - **Fix**: `pip install -r apps/ai/requirements-rag.txt`

### Route Not Found
- **Error**: 404 on `/api/v1/ai/jobs/*`
  - **Fix**: Verify `app.include_router(rag_routes.router)` is in your main app

### ChromaDB Errors
- **Error**: ChromaDB connection issues
  - **Fix**: Ensure write permissions for `./chroma_db` directory

---

## 📝 **Summary**

**Transfer this folder:**
```
apps/ai/
```

**That's it!** Everything you need for RAG and GenAI is in this folder. Just copy it, install dependencies, and include the router in your main app. 🚀

