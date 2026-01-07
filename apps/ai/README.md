# AI and RAG Module

This folder contains all Generative AI (GenAI) and Retrieval-Augmented Generation (RAG) related functionality for the Job Matching system.

## 📁 Folder Structure

```
apps/ai/
├── __init__.py
├── services/
│   ├── __init__.py
│   ├── rag_service.py          # Core RAG service
│   └── mercer_job_library.py   # Mercer job library integration
├── routes/
│   ├── __init__.py
│   └── rag_routes.py           # FastAPI routes for RAG endpoints
├── schemas/
│   ├── __init__.py
│   ├── requests.py             # RAG/AI request schemas
│   └── responses.py            # RAG/AI response schemas
├── libs/
│   ├── __init__.py
│   └── dummy_mercer.py         # Dummy Mercer library for development
├── requirements-rag.txt        # RAG dependencies
├── RAG_README.md              # RAG documentation
├── MERCER_INTEGRATION.md      # Mercer integration guide
└── GENAI_RAG_FILES_LIST.md    # Complete file list
```

## 🚀 Quick Start

### Installation

```bash
pip install -r apps/ai/requirements-rag.txt
```

### Configuration

Set environment variables:
```bash
export OPENAI_API_KEY="your-key-here"  # For LLM features
export MONGODB_URL="mongodb://localhost:27017/"  # For database
```

### Usage

The RAG routes are automatically included in the main FastAPI app via `apps/main.py`:

```python
from apps.ai.routes import rag_routes
app.include_router(rag_routes.router)
```

## 📚 Documentation

- **RAG_README.md** - Complete RAG feature documentation
- **MERCER_INTEGRATION.md** - Mercer library integration guide
- **GENAI_RAG_FILES_LIST.md** - List of all AI/RAG files

## 🔧 Features

- ✅ Semantic Job Search
- ✅ Candidate-Job Matching
- ✅ Job Description Generation (GenAI)
- ✅ Question Answering (RAG)
- ✅ Mercer Job Library Integration

## 📝 Import Examples

```python
# Services
from apps.ai.services.rag_service import RAGService
from apps.ai.services.mercer_job_library import get_mercer_service

# Routes
from apps.ai.routes import rag_routes

# Schemas
from apps.ai.schemas.requests import CandidateProfileRequest
from apps.ai.schemas.responses import MatchResultResponse
```


