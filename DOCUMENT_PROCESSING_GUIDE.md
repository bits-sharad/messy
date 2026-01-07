# Document Processing Guide

This guide explains how to process PDF documents from the `job_documents` MongoDB collection, extract text, generate embeddings, and display them in Swagger.

## 📋 Overview

The system processes PDF documents stored in MongoDB's `job_documents` collection by:
1. **Extracting text** from PDF files
2. **Generating embeddings** using sentence transformers
3. **Storing processed content** in `processed_documents` collection
4. **Including content** in job/project API responses

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install PyPDF2 pdfplumber
# Or install from requirements-rag.txt
pip install -r requirements-rag.txt
```

### 2. MongoDB Setup

Ensure MongoDB is running and you have a `job_documents` collection with documents:

```javascript
// Example document structure in job_documents collection
{
  "_id": ObjectId("..."),
  "job_id": "507f1f77bcf86cd799439012",
  "project_id": "507f1f77bcf86cd799439011",
  "title": "Job Description PDF",
  "content": <Binary PDF content>,  // or "file_content"
  "file_name": "job_description.pdf",
  "uploaded_at": ISODate("2024-01-15T10:00:00Z"),
  "processed": false
}
```

### 3. Process Documents

#### Option A: Process All Documents (Script)

```bash
python process_documents.py
```

This will:
- Connect to MongoDB
- Find all unprocessed documents in `job_documents`
- Extract text from PDFs
- Generate embeddings
- Store in `processed_documents` collection

#### Option B: Process via API

```bash
# Process a specific document
curl -X POST "http://127.0.0.1:8000/api/v1/documents/process/{document_id}" \
  -H "X-Principal-Subject: user123" \
  -H "X-Tenant-ID: tenant456"

# Process all unprocessed documents
curl -X POST "http://127.0.0.1:8000/api/v1/documents/process-all" \
  -H "X-Principal-Subject: user123" \
  -H "X-Tenant-ID: tenant456"
```

## 📁 Architecture

### Collections

1. **`job_documents`** - Original documents with PDF content
   - Contains raw PDF files
   - Marks documents as processed

2. **`processed_documents`** - Processed documents with extracted text
   - Contains extracted text
   - Contains embeddings
   - Linked to original document

### Services

1. **`PDFService`** (`apps/services/pdf_service.py`)
   - Extracts text from PDF files
   - Supports PyPDF2 and pdfplumber

2. **`DocumentService`** (`apps/services/document_service.py`)
   - Processes documents from `job_documents`
   - Generates embeddings via RAGService
   - Stores in `processed_documents`

3. **`RAGService`** (`apps/ai/services/rag_service.py`)
   - Generates embeddings using sentence transformers

## 🔌 API Endpoints

### Process Documents

#### Process Single Document
```
POST /api/v1/documents/process/{document_id}
```

**Query Parameters:**
- `job_id` (optional): Link document to a job
- `generate_embeddings` (default: true): Generate embeddings

**Response:**
```json
{
  "success": true,
  "processed_document_id": "...",
  "original_document_id": "...",
  "content_length": 5000,
  "word_count": 850,
  "has_embedding": true
}
```

#### Process All Documents
```
POST /api/v1/documents/process-all
```

**Query Parameters:**
- `job_id` (optional): Filter by job
- `generate_embeddings` (default: true)

**Response:**
```json
{
  "total": 10,
  "processed": 9,
  "failed": 1,
  "results": [...]
}
```

### Get Document Content

#### Get Job Documents
```
GET /api/v1/documents/job/{job_id}
```

**Response:**
```json
{
  "has_documents": true,
  "document_count": 2,
  "documents": [
    {
      "id": "...",
      "title": "Job Description",
      "extracted_text": "Full text content...",
      "content_length": 5000,
      "word_count": 850,
      "has_embedding": true
    }
  ],
  "total_content": "Combined text from all documents...",
  "total_content_length": 10000,
  "total_word_count": 1700
}
```

#### Get Project Documents
```
GET /api/v1/documents/project/{project_id}
```

**Response:**
```json
{
  "project_id": "...",
  "has_documents": true,
  "document_count": 5,
  "documents_by_job": {
    "job_id_1": [...],
    "job_id_2": [...]
  }
}
```

## 📊 Job/Project API Integration

Document content is automatically included in job and project responses:

### Job Response (GET /api/v1/jobs/{job_id})

```json
{
  "id": "...",
  "title": "Senior Software Engineer",
  "description": "...",
  ...
  "document_content": {
    "has_documents": true,
    "document_count": 2,
    "total_content": "Full extracted text...",
    "total_content_length": 10000,
    "total_word_count": 1700,
    "documents": [...]
  }
}
```

### Project Response (GET /api/v1/projects/{project_id})

```json
{
  "id": "...",
  "name": "Q4 Recruitment",
  ...
  "documents": {
    "job_id_1": [
      {
        "id": "...",
        "title": "Job Description",
        "extracted_text": "...",
        ...
      }
    ],
    "job_id_2": [...]
  }
}
```

## 🔍 Viewing in Swagger

1. **Start the server:**
   ```bash
   python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Open Swagger UI:**
   - Visit: http://127.0.0.1:8000/docs

3. **Try the endpoints:**
   - `/api/v1/documents/process/{document_id}` - Process a document
   - `/api/v1/documents/job/{job_id}` - Get job documents
   - `/api/v1/jobs/{job_id}` - Get job (includes document_content)
   - `/api/v1/projects/{project_id}` - Get project (includes documents)

4. **View document content:**
   - Expand any job or project response
   - Look for `document_content` or `documents` field
   - See extracted text, word counts, and metadata

## 📝 Example Workflow

```python
# 1. Process all documents
POST /api/v1/documents/process-all
# → Processes all unprocessed documents

# 2. Get job with document content
GET /api/v1/jobs/{job_id}
# → Returns job + document_content field

# 3. Get project with documents
GET /api/v1/projects/{project_id}
# → Returns project + documents grouped by job
```

## 🔧 Configuration

### MongoDB Connection

Set in `.env` or environment:
```bash
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=job_matching_db
```

### Embedding Model

The system uses `all-MiniLM-L6-v2` by default (via RAGService).

To change:
```python
# In apps/ai/services/rag_service.py
rag_service = RAGService(embedding_model_name="your-model-name")
```

## 🐛 Troubleshooting

### "No PDF processing library available"
```bash
pip install PyPDF2 pdfplumber
```

### "Document not found in job_documents"
- Verify document exists in `job_documents` collection
- Check `_id` format (must be valid ObjectId)

### "Failed to generate embedding"
- Ensure sentence-transformers is installed
- Check RAGService initialization

### Documents not showing in responses
- Process documents first using `/process-all` endpoint
- Verify `job_id` matches between documents and jobs
- Check `processed` field is `true` in `job_documents`

## 📚 Files Reference

- `apps/services/pdf_service.py` - PDF text extraction
- `apps/services/document_service.py` - Document processing logic
- `apps/routes/document_routes.py` - API endpoints
- `apps/schemas/responses.py` - Response schemas with document fields
- `apps/services/mmc_jobs.py` - Job service (includes document fetching)
- `apps/services/mmc_project.py` - Project service (includes document fetching)
- `process_documents.py` - Batch processing script

## ✅ Next Steps

1. **Process your documents:**
   ```bash
   python process_documents.py
   ```

2. **View in Swagger:**
   - Open http://127.0.0.1:8000/docs
   - Try GET endpoints for jobs/projects
   - See document content in responses

3. **Use in your application:**
   - Document content is automatically included
   - Access via `job.document_content` or `project.documents`
   - Use embeddings for semantic search

---

**The document processing system is ready to use!** 🎉

