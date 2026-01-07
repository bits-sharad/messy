# PDF Document Processing Implementation Summary

## ✅ Implementation Complete

All features for processing PDF documents from MongoDB `job_documents` collection have been implemented and integrated.

## 📦 What Was Created

### 1. **PDF Processing Service** (`apps/services/pdf_service.py`)
- Extracts text from PDF files
- Supports both PyPDF2 and pdfplumber (pdfplumber preferred for better quality)
- Handles PDF bytes or file paths
- Extracts metadata (title, author, page count, etc.)
- Returns structured data with text content and metadata

### 2. **Document Service** (`apps/services/document_service.py`)
- Reads documents from `job_documents` MongoDB collection
- Processes PDFs to extract text
- Generates embeddings using RAGService
- Stores processed content in `processed_documents` collection
- Links processed documents to jobs/projects
- Provides methods to fetch document content for jobs/projects

### 3. **Document API Routes** (`apps/routes/document_routes.py`)
- `POST /api/v1/documents/process/{document_id}` - Process single document
- `POST /api/v1/documents/process-all` - Process all unprocessed documents
- `GET /api/v1/documents/job/{job_id}` - Get documents for a job
- `GET /api/v1/documents/project/{project_id}` - Get documents for a project

### 4. **Updated Schemas** (`apps/schemas/responses.py`)
- Added `DocumentContentResponse` schema
- Updated `JobResponse` to include `document_content` field
- Updated `ProjectResponse` to include `documents` field

### 5. **Updated Services**
- **JobService** (`apps/services/mmc_jobs.py`):
  - `get_job()` now includes document content automatically
  - Fetches from `processed_documents` collection
  
- **ProjectService** (`apps/services/mmc_project.py`):
  - `get_project()` now includes documents grouped by job
  - Fetches from `processed_documents` collection

### 6. **Batch Processing Script** (`process_documents.py`)
- Standalone script to process all documents
- Can be run independently
- Shows progress and results

### 7. **Updated Requirements** (`requirements-rag.txt`)
- Added `PyPDF2>=3.0.0`
- Added `pdfplumber>=0.9.0`

### 8. **Documentation**
- `DOCUMENT_PROCESSING_GUIDE.md` - Complete guide on how to use the system

## 🗄️ MongoDB Collections

### `job_documents` (Input Collection)
Your existing collection with PDF documents:
```javascript
{
  "_id": ObjectId("..."),
  "job_id": "507f1f77bcf86cd799439012",
  "project_id": "507f1f77bcf86cd799439011",
  "title": "Job Description PDF",
  "content": <Binary PDF data>,  // or "file_content"
  "file_name": "job_description.pdf",
  "processed": false
}
```

### `processed_documents` (Output Collection)
Created automatically to store processed content:
```javascript
{
  "_id": ObjectId("..."),
  "original_document_id": "...",
  "job_id": "...",
  "project_id": "...",
  "title": "Job Description PDF",
  "extracted_text": "Full text extracted from PDF...",
  "pdf_metadata": {
    "total_pages": 5,
    "title": "...",
    "author": "..."
  },
  "embedding": [0.123, -0.456, ...],  // 384 dimensions
  "content_length": 5000,
  "word_count": 850,
  "processing_metadata": {
    "processed_at": ISODate("..."),
    "embedding_model": "all-MiniLM-L6-v2",
    "embedding_dim": 384
  },
  "status": "processed",
  "created_at": ISODate("..."),
  "updated_at": ISODate("...")
}
```

## 🚀 How to Use

### Step 1: Install Dependencies
```bash
pip install PyPDF2 pdfplumber
# Or
pip install -r requirements-rag.txt
```

### Step 2: Start Server
```bash
python -m uvicorn apps.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 3: Process Documents

**Option A: Use the script**
```bash
python process_documents.py
```

**Option B: Use API**
```bash
# Process all documents
curl -X POST "http://127.0.0.1:8000/api/v1/documents/process-all" \
  -H "X-Principal-Subject: user123" \
  -H "X-Tenant-ID: tenant456"

# Process single document
curl -X POST "http://127.0.0.1:8000/api/v1/documents/process/{document_id}" \
  -H "X-Principal-Subject: user123" \
  -H "X-Tenant-ID: tenant456"
```

### Step 4: View in Swagger

1. Open: http://127.0.0.1:8000/docs
2. Try these endpoints:
   - `GET /api/v1/jobs/{job_id}` - See job with `document_content` field
   - `GET /api/v1/projects/{project_id}` - See project with `documents` field
   - `GET /api/v1/documents/job/{job_id}` - Get job documents
   - `GET /api/v1/documents/project/{project_id}` - Get project documents

## 📊 API Response Examples

### Job Response (includes documents)
```json
{
  "id": "507f1f77bcf86cd799439012",
  "title": "Senior Software Engineer",
  "description": "...",
  "document_content": {
    "has_documents": true,
    "document_count": 2,
    "total_content": "Full extracted text from PDFs...",
    "total_content_length": 10000,
    "total_word_count": 1700,
    "documents": [
      {
        "id": "...",
        "title": "Job Description",
        "extracted_text": "...",
        "content_length": 5000,
        "word_count": 850,
        "has_embedding": true
      }
    ]
  }
}
```

### Project Response (includes documents)
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "Q4 Recruitment",
  "documents": {
    "job_id_1": [
      {
        "id": "...",
        "title": "Job Description",
        "extracted_text": "...",
        "content_length": 5000,
        "word_count": 850
      }
    ],
    "job_id_2": [...]
  }
}
```

## ✨ Key Features

1. **Automatic PDF Text Extraction**
   - Handles PDF bytes from MongoDB
   - Extracts all text content
   - Preserves structure (page breaks)

2. **Embedding Generation**
   - Uses sentence-transformers (`all-MiniLM-L6-v2`)
   - 384-dimensional embeddings
   - Stored in MongoDB for semantic search

3. **Integration with Jobs/Projects**
   - Document content automatically included in responses
   - No need for separate API calls
   - Grouped by job for projects

4. **Swagger Documentation**
   - All endpoints documented
   - Example responses shown
   - Interactive testing available

## 🔧 Configuration

### MongoDB Connection
Set in `.env` or environment:
```bash
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=job_matching_db
```

### Embedding Model
Default: `all-MiniLM-L6-v2`
- Can be changed in RAGService initialization
- Model downloads automatically on first use

## 📝 Files Modified/Created

**Created:**
- `apps/services/pdf_service.py`
- `apps/services/document_service.py`
- `apps/routes/document_routes.py`
- `process_documents.py`
- `DOCUMENT_PROCESSING_GUIDE.md`

**Modified:**
- `apps/main.py` - Added document routes
- `apps/schemas/responses.py` - Added document fields
- `apps/services/mmc_jobs.py` - Added document fetching
- `apps/services/mmc_project.py` - Added document fetching
- `requirements-rag.txt` - Added PDF libraries

## 🎯 Next Steps

1. **Process your documents:**
   ```bash
   python process_documents.py
   ```

2. **Test in Swagger:**
   - Visit http://127.0.0.1:8000/docs
   - Try the endpoints

3. **Verify document content:**
   - Check `processed_documents` collection in MongoDB
   - View job/project responses in Swagger

## 📚 Documentation

- **Complete Guide**: See `DOCUMENT_PROCESSING_GUIDE.md`
- **API Docs**: Visit http://127.0.0.1:8000/docs
- **Workflow Guide**: See `COMPLETE_WORKFLOW_GUIDE.md`

---

**All features are implemented and ready to use!** 🎉

The system will:
- ✅ Read PDFs from `job_documents` collection
- ✅ Extract text content
- ✅ Generate embeddings
- ✅ Store in `processed_documents`
- ✅ Display in Swagger for jobs and projects

