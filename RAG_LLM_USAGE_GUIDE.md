# RAG Search & LLM Job Description Generation - Complete Guide

This guide shows you how to use RAG (Retrieval-Augmented Generation) search and LLM (Large Language Model) features for job descriptions.

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements-rag.txt
```

This installs:
- `sentence-transformers` - For generating embeddings
- `chromadb` - Vector database for semantic search
- `openai` - For LLM features (optional)
- `PyPDF2` & `pdfplumber` - For PDF processing (if needed)

### Step 2: Configure OpenAI (Optional - for LLM features)

**For LLM-powered job description generation**, set your OpenAI API key:

```bash
# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file in the project root:
```
OPENAI_API_KEY=your-api-key-here
```

**Note**: Without OpenAI API key, job description generation will use template-based generation (still works, but less sophisticated).

---

## 📋 Available RAG/LLM Endpoints

All endpoints are under `/api/v1/ai/*`:

1. **Semantic Job Search** - `POST /api/v1/ai/jobs/search-semantic`
2. **Job Description Generation** - `POST /api/v1/ai/jobs/generate-description`
3. **Candidate-Job Matching** - `POST /api/v1/ai/jobs/match-candidate`
4. **Job Question Answering** - `POST /api/v1/ai/jobs/{job_id}/ask`
5. **Index Job for Search** - `POST /api/v1/ai/jobs/{job_id}/index`

---

## 1️⃣ Semantic Job Search (RAG)

Search for jobs using natural language instead of exact keywords.

### Endpoint
```
POST /api/v1/ai/jobs/search-semantic
```

### How It Works
1. Your query is converted to an embedding (vector)
2. The system searches for similar job embeddings in ChromaDB
3. Returns jobs ranked by semantic similarity

### Prerequisites
- Jobs must be **indexed** first (see Section 5)

### Example: Using Swagger UI

1. **Open Swagger**: http://127.0.0.1:8000/docs
2. **Find**: `POST /api/v1/ai/jobs/search-semantic` in "AI & RAG" section
3. **Click "Try it out"**
4. **Enter request body**:
   ```json
   {
     "query": "Python developer with MongoDB experience",
     "limit": 10,
     "filters": {
       "status": "published",
       "level": "senior"
     }
   }
   ```
5. **Set headers** (required):
   ```
   X-Principal-Subject: user123
   X-Tenant-ID: default
   ```
6. **Click "Execute"**

### Example: Using cURL

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ai/jobs/search-semantic" \
  -H "Content-Type: application/json" \
  -H "X-Principal-Subject: user123" \
  -H "X-Tenant-ID: default" \
  -d '{
    "query": "Python developer with MongoDB experience",
    "limit": 10,
    "filters": {
      "status": "published"
    }
  }'
```

### Response Example
```json
[
  {
    "job_id": "695e3221efa74c826ffa04f3",
    "score": 0.92,
    "title": "Senior Software Engineer - Backend",
    "department": "Engineering",
    "level": "senior"
  },
  {
    "job_id": "695e3221efa74c826ffa04f4",
    "score": 0.85,
    "title": "Full Stack Developer",
    "department": "Engineering",
    "level": "mid"
  }
]
```

### Example: Using Python

```python
import requests

url = "http://127.0.0.1:8000/api/v1/ai/jobs/search-semantic"
headers = {
    "Content-Type": "application/json",
    "X-Principal-Subject": "user123",
    "X-Tenant-ID": "default"
}

payload = {
    "query": "Looking for a backend engineer experienced with Python and databases",
    "limit": 5,
    "filters": {"status": "published"}
}

response = requests.post(url, json=payload, headers=headers)
results = response.json()

for job in results:
    print(f"{job['title']} - Score: {job['score']:.2f}")
```

---

## 2️⃣ Generate Job Description Using LLM

Generate professional job descriptions using AI (OpenAI GPT) or templates.

### Endpoint
```
POST /api/v1/ai/jobs/generate-description
```

### Two Modes

#### Mode 1: LLM Generation (with OpenAI API key)
- Uses GPT-3.5-turbo to generate professional descriptions
- More creative and contextual
- Requires `OPENAI_API_KEY`

#### Mode 2: Template Generation (without OpenAI)
- Uses structured templates
- Works without API key
- Less sophisticated but still functional

### Example: Generate with LLM

**Request:**
```json
{
  "title": "Senior Software Engineer",
  "department": "Engineering",
  "level": "senior",
  "required_skills": ["Python", "FastAPI", "MongoDB", "Docker", "AWS"],
  "responsibilities": [
    "Design and develop scalable APIs",
    "Lead code reviews and mentor junior developers",
    "Optimize database queries and system performance"
  ],
  "use_llm": true
}
```

**Response:**
```json
{
  "description": "# Senior Software Engineer\n\n**Department:** Engineering\n**Level:** Senior\n\nWe are seeking a Senior Software Engineer to join our Engineering team...\n\n## Key Responsibilities\n- Design and develop scalable APIs...\n\n## Required Skills\n- Python\n- FastAPI\n- MongoDB...",
  "generated_by": "llm"
}
```

### Example: Generate with Template (No API Key)

**Request:**
```json
{
  "title": "Data Scientist",
  "department": "Data Science",
  "level": "mid",
  "required_skills": ["Python", "Machine Learning", "SQL"],
  "responsibilities": ["Build ML models", "Analyze data"],
  "use_llm": false
}
```

**Response:**
```json
{
  "description": "# Data Scientist\n\n**Department:** Data Science\n**Level:** mid\n\n## Job Summary\nWe are looking for a mid Data Scientist to join our Data Science team...",
  "generated_by": "template"
}
```

### Using Swagger UI

1. Open: http://127.0.0.1:8000/docs
2. Find: `POST /api/v1/ai/jobs/generate-description`
3. Click "Try it out"
4. Enter request body (see examples above)
5. Set headers:
   ```
   X-Principal-Subject: user123
   X-Tenant-ID: default
   ```
6. Click "Execute"

### Using cURL

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ai/jobs/generate-description" \
  -H "Content-Type: application/json" \
  -H "X-Principal-Subject: user123" \
  -H "X-Tenant-ID: default" \
  -d '{
    "title": "Senior Software Engineer",
    "department": "Engineering",
    "level": "senior",
    "required_skills": ["Python", "FastAPI", "MongoDB"],
    "responsibilities": ["Design APIs", "Code reviews"],
    "use_llm": true
  }'
```

### Using Python

```python
import requests

url = "http://127.0.0.1:8000/api/v1/ai/jobs/generate-description"
headers = {
    "Content-Type": "application/json",
    "X-Principal-Subject": "user123",
    "X-Tenant-ID": "default"
}

payload = {
    "title": "Machine Learning Engineer",
    "department": "AI/ML",
    "level": "senior",
    "required_skills": ["Python", "TensorFlow", "PyTorch", "MLOps"],
    "responsibilities": [
        "Develop ML models",
        "Deploy models to production",
        "Optimize model performance"
    ],
    "use_llm": True  # Set to False for template generation
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()

print("Generated Description:")
print(result["description"])
print(f"\nGenerated by: {result['generated_by']}")
```

---

## 3️⃣ Index Jobs for Semantic Search

Before you can search jobs semantically, you need to index them in the vector database.

### Endpoint
```
POST /api/v1/ai/jobs/{job_id}/index
```

### What It Does
1. Takes job data from MongoDB
2. Generates an embedding (vector representation)
3. Stores it in ChromaDB for semantic search

### Example: Index a Single Job

**Using Swagger:**
1. Get a job ID from `/api/v1/jobs/` or `/jobs/`
2. Find: `POST /api/v1/ai/jobs/{job_id}/index`
3. Enter job ID in path
4. Set headers
5. Execute

**Using cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ai/jobs/695e3221efa74c826ffa04f3/index" \
  -H "X-Principal-Subject: user123" \
  -H "X-Tenant-ID: default"
```

**Response:**
```json
{
  "message": "Job 695e3221efa74c826ffa04f3 indexed successfully",
  "job_id": "695e3221efa74c826ffa04f3"
}
```

### Batch Index All Jobs

Create a script to index all existing jobs:

```python
import requests
import asyncio
from apps.database.connection import db_manager
from apps.services.mmc_jobs import JobService
from apps.core.client import CoreAPIClient

async def index_all_jobs():
    """Index all jobs for semantic search"""
    db_manager.connect()
    core_api = CoreAPIClient()
    job_service = JobService(core_api)
    
    # Get all jobs
    result = await job_service.list_all_jobs(tenant_id="default", skip=0, limit=1000)
    jobs = result.get("jobs", [])
    
    print(f"Found {len(jobs)} jobs to index")
    
    base_url = "http://127.0.0.1:8000/api/v1/ai/jobs"
    headers = {
        "X-Principal-Subject": "system",
        "X-Tenant-ID": "default"
    }
    
    indexed = 0
    for job in jobs:
        job_id = job.get("id")
        try:
            response = requests.post(
                f"{base_url}/{job_id}/index",
                headers=headers
            )
            if response.status_code == 200:
                indexed += 1
                print(f"[OK] Indexed: {job.get('title')}")
            else:
                print(f"[FAILED] {job.get('title')}: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {job.get('title')}: {e}")
    
    print(f"\nIndexed {indexed}/{len(jobs)} jobs")

if __name__ == "__main__":
    asyncio.run(index_all_jobs())
```

---

## 4️⃣ Complete Workflow Example

Here's a complete workflow for using RAG and LLM:

### Step 1: Generate Job Description with LLM

```python
import requests

# Generate job description
response = requests.post(
    "http://127.0.0.1:8000/api/v1/ai/jobs/generate-description",
    headers={
        "Content-Type": "application/json",
        "X-Principal-Subject": "user123",
        "X-Tenant-ID": "default"
    },
    json={
        "title": "Senior Backend Engineer",
        "department": "Engineering",
        "level": "senior",
        "required_skills": ["Python", "FastAPI", "MongoDB"],
        "responsibilities": ["Build APIs", "Optimize performance"],
        "use_llm": True
    }
)

description = response.json()["description"]
print("Generated Description:")
print(description)
```

### Step 2: Create Job with Generated Description

```python
# Create job using the generated description
job_response = requests.post(
    "http://127.0.0.1:8000/api/v1/projects/{project_id}/jobs",
    headers={
        "Content-Type": "application/json",
        "X-Principal-Subject": "user123",
        "X-Tenant-ID": "default"
    },
    json={
        "project_id": "your_project_id",
        "title": "Senior Backend Engineer",
        "description": description,  # Use generated description
        "job_code": "ENG-005",
        "status": "published",
        "department": "Engineering",
        "level": "senior",
        "required_skills": ["Python", "FastAPI", "MongoDB"],
        "created_by": "user123"
    }
)

job_id = job_response.json()["id"]
print(f"Created job: {job_id}")
```

### Step 3: Index the Job

```python
# Index the job for semantic search
index_response = requests.post(
    f"http://127.0.0.1:8000/api/v1/ai/jobs/{job_id}/index",
    headers={
        "X-Principal-Subject": "user123",
        "X-Tenant-ID": "default"
    }
)

print("Job indexed for semantic search")
```

### Step 4: Search Jobs Semantically

```python
# Search for similar jobs
search_response = requests.post(
    "http://127.0.0.1:8000/api/v1/ai/jobs/search-semantic",
    headers={
        "Content-Type": "application/json",
        "X-Principal-Subject": "user123",
        "X-Tenant-ID": "default"
    },
    json={
        "query": "Python backend developer with API experience",
        "limit": 5
    }
)

results = search_response.json()
for job in results:
    print(f"{job['title']} - Similarity: {job['score']:.2%}")
```

---

## 5️⃣ Question Answering (RAG + LLM)

Ask questions about specific jobs and get AI-powered answers.

### Endpoint
```
POST /api/v1/ai/jobs/{job_id}/ask
```

### Example

**Request:**
```json
{
  "question": "What skills are required for this position?",
  "job_id": "695e3221efa74c826ffa04f3"
}
```

**Response:**
```json
{
  "answer": "This position requires Python, FastAPI, MongoDB, Docker, and AWS experience. The role is for a senior-level engineer with 5+ years of backend development experience.",
  "job_id": "695e3221efa74c826ffa04f3"
}
```

**Using cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ai/jobs/695e3221efa74c826ffa04f3/ask" \
  -H "Content-Type: application/json" \
  -H "X-Principal-Subject: user123" \
  -H "X-Tenant-ID: default" \
  -d '{
    "question": "What are the main responsibilities for this role?",
    "job_id": "695e3221efa74c826ffa04f3"
  }'
```

---

## 6️⃣ Candidate-Job Matching

Match candidates to jobs using semantic similarity and skill matching.

### Endpoint
```
POST /api/v1/ai/jobs/match-candidate
```

### Example

**Request:**
```json
{
  "skills": ["Python", "FastAPI", "MongoDB", "Docker"],
  "experience_summary": "5+ years of backend development experience with Python and REST APIs",
  "education": "BS Computer Science",
  "desired_role": "Senior Software Engineer",
  "years_of_experience": 5,
  "location": "Remote"
}
```

**Response:**
```json
[
  {
    "job_id": "695e3221efa74c826ffa04f3",
    "job_title": "Senior Software Engineer - Backend",
    "match_score": 0.85,
    "match_reasons": [
      "Excellent semantic match",
      "Matches 4 required skills",
      "Level: senior"
    ],
    "matched_skills": ["Python", "FastAPI", "MongoDB", "Docker"],
    "missing_skills": ["Kubernetes"]
  }
]
```

---

## 🛠️ Configuration & Setup

### Environment Variables

Create a `.env` file in project root:
```
OPENAI_API_KEY=sk-your-key-here
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=job_matching_db
```

### Check if RAG is Working

```python
from apps.ai.services.rag_service import RAGService

rag_service = RAGService()

# Check if embeddings are available
if rag_service.embedding_model:
    print("✅ Embeddings initialized")
else:
    print("❌ Embeddings not available - install sentence-transformers")

# Check if OpenAI is configured
if rag_service.llm_api_key:
    print("✅ OpenAI configured")
else:
    print("⚠️ OpenAI not configured - LLM features will use templates")
```

---

## 📊 Testing in Swagger UI

### Step-by-Step

1. **Open Swagger**: http://127.0.0.1:8000/docs

2. **Generate Job Description**:
   - Find `POST /api/v1/ai/jobs/generate-description`
   - Click "Try it out"
   - Use the example request body
   - Set headers: `X-Principal-Subject: user123`, `X-Tenant-ID: default`
   - Execute

3. **Index Jobs** (if needed):
   - Find `POST /api/v1/ai/jobs/{job_id}/index`
   - Enter a job ID from your database
   - Execute

4. **Search Semantically**:
   - Find `POST /api/v1/ai/jobs/search-semantic`
   - Enter a natural language query
   - Execute

5. **Ask Questions**:
   - Find `POST /api/v1/ai/jobs/{job_id}/ask`
   - Enter a question and job ID
   - Execute

---

## 🔍 Understanding How It Works

### RAG Search Flow

```
1. User Query: "Python developer with MongoDB"
   ↓
2. Generate Embedding: [0.123, -0.456, 0.789, ...] (384 dimensions)
   ↓
3. Search ChromaDB: Find similar job embeddings
   ↓
4. Calculate Similarity: Cosine similarity scores
   ↓
5. Return Results: Jobs ranked by relevance
```

### LLM Job Description Generation Flow

```
1. Job Requirements Input
   ↓
2. Construct Prompt for GPT-3.5
   ↓
3. Call OpenAI API
   ↓
4. Receive Generated Description
   ↓
5. Return Formatted Description
```

---

## ⚙️ Advanced Configuration

### Change Embedding Model

Edit `apps/ai/services/rag_service.py`:

```python
# Default model (smaller, faster)
rag_service = RAGService(embedding_model_name="all-MiniLM-L6-v2")

# Better quality model (larger, slower)
rag_service = RAGService(embedding_model_name="all-mpnet-base-v2")
```

### Custom ChromaDB Location

```python
rag_service = RAGService(chroma_persist_dir="./custom_chroma_db")
```

---

## 🐛 Troubleshooting

### "Embeddings not available"
```bash
pip install sentence-transformers chromadb
```

### "LLM service not available"
- Set `OPENAI_API_KEY` environment variable
- Or use `use_llm: false` for template generation

### "No search results"
- Jobs must be indexed first: `POST /api/v1/ai/jobs/{job_id}/index`
- Check if jobs exist in database
- Verify ChromaDB collection exists

### "ChromaDB collection not found"
- It's created automatically on first use
- Check `./chroma_db` directory exists

---

## 📝 Complete Python Example Script

```python
"""Complete example: Generate JD, Index, and Search"""
import requests
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"
HEADERS = {
    "Content-Type": "application/json",
    "X-Principal-Subject": "user123",
    "X-Tenant-ID": "default"
}

# Step 1: Generate job description
print("1. Generating job description with LLM...")
jd_response = requests.post(
    f"{BASE_URL}/ai/jobs/generate-description",
    headers=HEADERS,
    json={
        "title": "DevOps Engineer",
        "department": "Engineering",
        "level": "mid",
        "required_skills": ["Docker", "Kubernetes", "AWS", "CI/CD"],
        "responsibilities": [
            "Manage infrastructure",
            "Automate deployments",
            "Monitor systems"
        ],
        "use_llm": True
    }
)
description = jd_response.json()["description"]
print(f"Generated description ({len(description)} chars)")

# Step 2: Create job (assuming you have a project_id)
project_id = "your_project_id_here"
job_response = requests.post(
    f"{BASE_URL}/projects/{project_id}/jobs",
    headers=HEADERS,
    json={
        "project_id": project_id,
        "title": "DevOps Engineer",
        "description": description,
        "job_code": "DEV-OPS-001",
        "status": "published",
        "required_skills": ["Docker", "Kubernetes", "AWS"],
        "created_by": "user123"
    }
)
job_id = job_response.json()["id"]
print(f"2. Created job: {job_id}")

# Step 3: Index job
print("3. Indexing job for semantic search...")
index_response = requests.post(
    f"{BASE_URL}/ai/jobs/{job_id}/index",
    headers=HEADERS
)
print(f"Indexed: {index_response.json().get('message')}")

# Step 4: Search semantically
print("4. Searching jobs semantically...")
search_response = requests.post(
    f"{BASE_URL}/ai/jobs/search-semantic",
    headers=HEADERS,
    json={
        "query": "DevOps engineer with container orchestration experience",
        "limit": 5
    }
)
results = search_response.json()
print(f"Found {len(results)} matching jobs:")
for job in results:
    print(f"  - {job['title']} (Score: {job['score']:.2%})")

print("\n✅ Complete workflow finished!")
```

---

## 🎯 Quick Reference

| Feature | Endpoint | Method | Requires |
|---------|----------|--------|----------|
| Generate JD | `/api/v1/ai/jobs/generate-description` | POST | OpenAI (optional) |
| Semantic Search | `/api/v1/ai/jobs/search-semantic` | POST | Indexed jobs |
| Index Job | `/api/v1/ai/jobs/{id}/index` | POST | Job exists |
| Match Candidate | `/api/v1/ai/jobs/match-candidate` | POST | Indexed jobs |
| Ask Question | `/api/v1/ai/jobs/{id}/ask` | POST | OpenAI |

---

**Ready to use!** 🚀

For more details, see:
- `apps/ai/RAG_README.md` - Complete RAG documentation
- Swagger UI: http://127.0.0.1:8000/docs (section "AI & RAG")

