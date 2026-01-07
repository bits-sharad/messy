# Files Required for GenAI, RAG, and Job Matching

This document lists all files needed for Generative AI, RAG (Retrieval-Augmented Generation), and Job Matching features.

---

## 📁 **Core RAG & AI Service Files**

### 1. **RAG Service** (Main Implementation)
- **`apps/services/rag_service.py`**
  - Core RAG service implementation
  - Semantic embeddings generation
  - Vector database management (ChromaDB)
  - Job indexing and semantic search
  - Candidate-job matching
  - LLM integration (OpenAI)
  - Job description generation
  - Question answering using RAG

### 2. **RAG API Routes** (Endpoints)
- **`apps/api/rag_routes.py`**
  - FastAPI routes for RAG endpoints
  - `/api/v1/ai/jobs/match-candidate` - Match candidates to jobs
  - `/api/v1/ai/jobs/generate-description` - Generate job descriptions
  - `/api/v1/ai/jobs/search-semantic` - Semantic job search
  - `/api/v1/ai/jobs/{job_id}/ask` - Q&A about jobs
  - `/api/v1/ai/jobs/{job_id}/index` - Index jobs for semantic search

---

## 📁 **Mercer Job Library Integration**

### 3. **Mercer Service**
- **`apps/services/mercer_job_library.py`**
  - Integration with Mercer Job Library
  - Hybrid matching (Mercer + RAG fallback)
  - Job taxonomy and competency models
  - Job enrichment with Mercer data
  - Dummy/mock implementation when library unavailable

### 4. **Dummy Mercer Library** (For Development)
- **`apps/libs/dummy_mercer.py`**
  - Mock implementation of Mercer Job Library
  - `DummyJobLibrary` class
  - `DummyJobMatcher` class
  - Used when actual Mercer library is not available

### 5. **Libs Package Init**
- **`apps/libs/__init__.py`**
  - Package initialization

---

## 📁 **API Schemas (Request/Response Models)**

### 6. **Request Schemas**
- **`apps/schemas/requests.py`**
  - Contains these RAG/AI request models:
    - `CandidateProfileRequest` - Candidate profile for matching
    - `JobDescriptionGenerationRequest` - Job description generation input
    - `SemanticJobSearchRequest` - Semantic search query
    - `JobQuestionRequest` - Q&A about jobs
    - `JobIndexRequest` - Job indexing request

### 7. **Response Schemas**
- **`apps/schemas/responses.py`**
  - Contains these RAG/AI response models:
    - `MatchResultResponse` - Candidate-job match results
    - `JobDescriptionResponse` - Generated job description
    - `SemanticSearchResultResponse` - Semantic search results
    - `JobQuestionResponse` - Q&A answers

---

## 📁 **Main Application Integration**

### 8. **Main App File**
- **`apps/main.py`**
  - FastAPI application entry point
  - Includes RAG routes: `app.include_router(rag_routes.router)`

### 9. **API Package Init**
- **`apps/api/__init__.py`**
  - API package initialization

---

## 📁 **Dependencies & Configuration**

### 10. **RAG Dependencies**
- **`requirements-rag.txt`**
  - Python packages required for RAG:
    - `sentence-transformers>=2.2.0` - Embedding models
    - `chromadb>=0.4.0` - Vector database
    - `openai>=1.0.0` - OpenAI API (optional, for LLM)
    - `numpy>=1.24.0`
    - `torch>=2.0.0` - Required by sentence-transformers

### 11. **Environment Variables** (`.env` file - not in repo)
  - `OPENAI_API_KEY` - OpenAI API key for LLM features (optional)
  - `CHROMA_PERSIST_DIR` - ChromaDB storage directory (default: `./chroma_db`)
  - `MERCER_API_KEY` - Mercer library API key (optional)
  - `MERCER_API_URL` - Mercer API URL (optional)
  - `MERCER_CONFIG_PATH` - Mercer config path (optional)
  - `MERCER_ALGORITHM` - Matching algorithm (optional)

---

## 📁 **Documentation**

### 12. **RAG Documentation**
- **`apps/RAG_README.md`**
  - Complete RAG feature documentation
  - Installation instructions
  - API endpoint documentation
  - Usage examples
  - Configuration guide

### 13. **Mercer Integration Documentation**
- **`apps/MERCER_INTEGRATION.md`**
  - Mercer library integration guide
  - Configuration instructions
  - Usage examples
  - Hybrid matching explanation

---

## 📁 **Data Storage**

### 14. **Vector Database Storage** (Generated at runtime)
- **`chroma_db/`** (directory - created automatically)
  - ChromaDB persistent storage
  - Stores job embeddings and metadata
  - Created automatically when RAG service initializes

---

## 📁 **Supporting Files** (Required by RAG/AI features)

### 15. **Core Client & Dependencies**
- **`apps/core/client.py`** - Core API client
- **`apps/core/principal.py`** - Principal/authentication
- **`apps/core/dependencies.py`** - FastAPI dependencies

### 16. **Job Service** (Used by RAG for job data)
- **`apps/services/mmc_jobs.py`** - Job CRUD service
- Used by RAG routes to fetch job data

---

## 📋 **Summary Checklist**

### ✅ **Essential Files** (Must have):
- [x] `apps/services/rag_service.py`
- [x] `apps/api/rag_routes.py`
- [x] `apps/services/mercer_job_library.py`
- [x] `apps/libs/dummy_mercer.py`
- [x] `apps/schemas/requests.py` (with RAG request models)
- [x] `apps/schemas/responses.py` (with RAG response models)
- [x] `apps/main.py` (with RAG routes included)
- [x] `requirements-rag.txt`

### ✅ **Documentation Files**:
- [x] `apps/RAG_README.md`
- [x] `apps/MERCER_INTEGRATION.md`

### ✅ **Dependencies** (Install via pip):
```bash
pip install -r requirements-rag.txt
```

### ✅ **Optional Configuration**:
- `.env` file with API keys (OpenAI, Mercer)
- `chroma_db/` directory (auto-created)

---

## 🚀 **Quick Setup**

1. **Install dependencies:**
   ```bash
   pip install -r requirements-rag.txt
   ```

2. **Set environment variables** (optional):
   ```bash
   export OPENAI_API_KEY="your-key-here"
   export MERCER_API_KEY="your-key-here"  # if using real Mercer library
   ```

3. **Verify files exist:**
   - Check all files listed above are present

4. **Start the server:**
   ```bash
   python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
   ```

5. **Test endpoints:**
   - Visit: `http://127.0.0.1:8000/docs`
   - Look for "AI & RAG" section

---

## 📊 **File Dependencies Diagram**

```
apps/main.py
    └── includes → apps/api/rag_routes.py
                        ├── depends on → apps/services/rag_service.py
                        │                   ├── uses → apps/services/mercer_job_library.py
                        │                   │               └── uses → apps/libs/dummy_mercer.py (fallback)
                        │                   ├── uses → sentence-transformers (embeddings)
                        │                   ├── uses → chromadb (vector DB)
                        │                   └── uses → openai (LLM)
                        ├── uses → apps/schemas/requests.py
                        ├── uses → apps/schemas/responses.py
                        └── uses → apps/services/mmc_jobs.py
```

---

## 🔍 **Feature Breakdown by File**

### **Semantic Search:**
- `rag_service.py` - `search_similar_jobs()` method
- `rag_routes.py` - `/jobs/search-semantic` endpoint

### **Candidate Matching:**
- `rag_service.py` - `match_candidate_to_jobs()` method
- `mercer_job_library.py` - Hybrid matching
- `rag_routes.py` - `/jobs/match-candidate` endpoint

### **Job Description Generation:**
- `rag_service.py` - `generate_job_description()` method
- `rag_routes.py` - `/jobs/generate-description` endpoint

### **Question Answering (RAG):**
- `rag_service.py` - `answer_job_question()` method
- `rag_routes.py` - `/jobs/{job_id}/ask` endpoint

### **Job Indexing:**
- `rag_service.py` - `index_job()` method
- `rag_routes.py` - `/jobs/{job_id}/index` endpoint

