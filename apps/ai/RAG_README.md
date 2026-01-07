# RAG (Retrieval-Augmented Generation) Features

This document describes the RAG and AI features added to the Job Matching API.

## Overview

The RAG service enables:
- **Semantic Job Search**: Find jobs using natural language queries
- **Candidate-Job Matching**: Match candidates to jobs using AI-powered similarity
- **Job Description Generation**: Generate professional job descriptions using LLM
- **Question Answering**: Answer questions about jobs using RAG

## Installation

Install the required dependencies:

```bash
pip install -r requirements-rag.txt
```

### Optional: OpenAI Configuration

For LLM features (job description generation, Q&A), set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

## Features

### 1. Semantic Job Search

Search for jobs using natural language instead of exact keyword matching.

**Endpoint**: `POST /api/v1/ai/jobs/search-semantic`

**Example Request**:
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

### 2. Candidate-Job Matching

Match candidates to jobs using semantic similarity and skill matching.

**Endpoint**: `POST /api/v1/ai/jobs/match-candidate`

**Example Request**:
```json
{
  "skills": ["Python", "FastAPI", "MongoDB", "Docker"],
  "experience_summary": "5+ years of backend development experience",
  "education": "BS Computer Science",
  "desired_role": "Senior Software Engineer",
  "years_of_experience": 5
}
```

**Response** includes:
- Match score (0-1)
- Match reasons
- Matched skills
- Missing skills

### 3. Job Description Generation

Generate professional job descriptions using AI.

**Endpoint**: `POST /api/v1/ai/jobs/generate-description`

**Example Request**:
```json
{
  "title": "Senior Software Engineer",
  "department": "Engineering",
  "level": "senior",
  "required_skills": ["Python", "FastAPI", "MongoDB"],
  "responsibilities": ["Design and develop APIs", "Lead code reviews"],
  "use_llm": true
}
```

### 4. Question Answering

Ask questions about jobs and get AI-powered answers using RAG.

**Endpoint**: `POST /api/v1/ai/jobs/{job_id}/ask`

**Example Request**:
```json
{
  "question": "What skills are required for this position?",
  "job_id": "507f1f77bcf86cd799439011"
}
```

### 5. Job Indexing

Index jobs in the vector database for semantic search.

**Endpoint**: `POST /api/v1/ai/jobs/{job_id}/index`

Automatically indexes the job for semantic search capabilities.

## Architecture

### Components

1. **RAGService** (`apps/services/rag_service.py`):
   - Handles embeddings generation
   - Manages vector database (ChromaDB)
   - Implements semantic search
   - Provides LLM integration

2. **Embedding Model**:
   - Default: `all-MiniLM-L6-v2` (Sentence Transformers)
   - Can be changed in RAGService initialization

3. **Vector Database**:
   - ChromaDB for persistent vector storage
   - Stores job embeddings with metadata

4. **LLM Integration**:
   - OpenAI GPT-3.5-turbo (optional)
   - Falls back to template-based generation if not configured

## Usage Flow

1. **Index Jobs**: When jobs are created/updated, index them for semantic search
   ```python
   POST /api/v1/ai/jobs/{job_id}/index
   ```

2. **Search**: Use semantic search to find relevant jobs
   ```python
   POST /api/v1/ai/jobs/search-semantic
   ```

3. **Match Candidates**: Match candidates to jobs
   ```python
   POST /api/v1/ai/jobs/match-candidate
   ```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for LLM features
- `CHROMA_PERSIST_DIR`: Directory for ChromaDB data (default: `./chroma_db`)

### Embedding Model

Change the embedding model in `RAGService.__init__()`:
```python
rag_service = RAGService(embedding_model_name="all-mpnet-base-v2")
```

## Limitations

- RAG features require `sentence-transformers` and `chromadb` packages
- LLM features require OpenAI API key (optional)
- Initial indexing may take time for large job databases
- Embeddings are generated on-demand (consider caching for production)

## Future Enhancements

- Automatic job indexing on create/update
- Batch job indexing
- Custom embedding models fine-tuned for job matching
- Support for other LLM providers (Anthropic, local models)
- Candidate profile indexing
- Advanced filtering and ranking

