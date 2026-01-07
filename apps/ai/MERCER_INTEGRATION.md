# Mercer Job Library Integration

This document describes how the Mercer Job Library is integrated with the job matching system.

## Overview

The Mercer Job Library provides industry-standard job taxonomy, competency models, and matching algorithms. This integration allows the system to leverage Mercer's job classification and matching capabilities alongside our RAG-based semantic search.

## Features

### 1. **Hybrid Matching**
- Primary: Mercer library matching (if available)
- Fallback: RAG-based semantic matching
- Combines both approaches for best results

### 2. **Job Taxonomy**
- Access to Mercer's standardized job classifications
- Industry-standard job titles and hierarchies

### 3. **Competency Models**
- Pre-defined competency frameworks for different roles
- Skill and competency scoring

### 4. **Enriched Job Data**
- Automatically enrich job postings with Mercer taxonomy
- Add competency requirements from Mercer library

## Configuration

### Environment Variables

```bash
# Mercer Library Configuration
export MERCER_API_KEY="your-mercer-api-key"
export MERCER_API_URL="https://api.mercer.com/jobs"
export MERCER_CONFIG_PATH="/path/to/mercer/config"
export MERCER_ALGORITHM="default"  # or "advanced", "custom"
```

### Code Configuration

The Mercer service can be configured when initializing:

```python
from apps.services.mercer_job_library import get_mercer_service

mercer_config = {
    "api_key": "your-api-key",
    "api_url": "https://api.mercer.com/jobs",
    "algorithm": "default"
}

mercer_service = get_mercer_service(config=mercer_config)
```

## API Usage

### Match Candidate (with Mercer)

```bash
POST /api/v1/ai/jobs/match-candidate
Content-Type: application/json

{
  "skills": ["Python", "FastAPI", "MongoDB"],
  "experience_summary": "5+ years backend development",
  "years_of_experience": 5,
  "desired_role": "Senior Software Engineer"
}
```

**Query Parameters:**
- `use_mercer=true` - Force use of Mercer library
- `use_mercer=false` - Use only RAG matching
- `use_mercer` not specified - Use default (Mercer if available, else RAG)

### Get Job Taxonomy

The system can automatically enrich jobs with Mercer taxonomy when indexing:

```python
from apps.services.mercer_job_library import get_mercer_service

mercer_service = get_mercer_service()
taxonomy = mercer_service.get_job_taxonomy(job_id)
```

### Get Competency Model

```python
competency_model = mercer_service.get_competency_model(job_id)
```

## Integration Points

### 1. RAG Service Integration

The RAG service automatically uses Mercer when:
- Mercer library is installed and configured
- `use_mercer=True` is set
- Mercer service initialization succeeds

**Matching Flow:**
1. Try Mercer library matching first (if enabled)
2. If Mercer fails or is unavailable, fallback to RAG
3. Convert Mercer results to MatchResult format
4. Return unified results

### 2. Job Enrichment

Jobs can be automatically enriched with Mercer data:

```python
# In job service or indexing
from apps.services.mercer_job_library import get_mercer_service

mercer_service = get_mercer_service()
enriched_job = mercer_service.enrich_job_data(job_data)
```

## Mercer Library Implementation

### Expected Interface

The Mercer library should provide:

```python
# JobMatcher
class JobMatcher:
    def match(candidate, jobs, top_n) -> List[Match]
    
# JobLibrary
class JobLibrary:
    def get_job(job_id) -> Job
    def list_jobs(status) -> List[Job]
    def get_job_taxonomy(job_id) -> Dict
    def get_competency_model(job_id) -> Dict
    def search(criteria, limit) -> List[Job]
```

### Custom Implementation

If you have a custom Mercer library, update the import in `apps/services/mercer_job_library.py`:

```python
# Option 1: Package import
from mercer_job_library import JobMatcher, JobLibrary

# Option 2: Local module
from apps.libs.mercer import JobMatcher, JobLibrary

# Option 3: API client
from apps.clients.mercer_api import MercerAPIClient
```

## Example: Custom Mercer Integration

If your Mercer library has a different interface, modify `_initialize_mercer_library()`:

```python
def _initialize_mercer_library(self):
    """Initialize the Mercer job library components"""
    try:
        # Example: Using API client
        from apps.clients.mercer_api import MercerAPIClient
        
        self.api_client = MercerAPIClient(
            api_key=self.config.get("api_key"),
            base_url=self.config.get("api_url")
        )
        
        # Wrap in adapter if needed
        self.job_library = MercerLibraryAdapter(self.api_client)
        self.job_matcher = MercerMatcherAdapter(self.api_client)
        
        self.initialized = True
    except Exception as e:
        print(f"Failed to initialize Mercer library: {e}")
```

## Testing Without Mercer Library

If Mercer library is not installed, the system will:
1. Print a warning message
2. Use fallback RAG matching
3. Continue to function normally

No errors will occur - the system gracefully degrades.

## Troubleshooting

### Issue: "Mercer job library not found"

**Solution:**
1. Install the Mercer library package
2. Or update the import path in `mercer_job_library.py`
3. Or configure the library location

### Issue: "Failed to initialize Mercer library"

**Solutions:**
- Check `MERCER_API_KEY` is set correctly
- Verify `MERCER_API_URL` is accessible
- Check network connectivity
- Review error logs for specific issues

### Issue: Mercer matches not appearing

**Solutions:**
- Check `use_mercer` parameter is set correctly
- Verify Mercer service initialized successfully
- Check job IDs exist in Mercer library
- Review fallback to RAG is working

## Performance Considerations

- **Mercer First**: If Mercer is available, it's used first (typically faster for structured matching)
- **RAG Fallback**: Semantic matching provides flexibility when Mercer data is incomplete
- **Caching**: Consider caching Mercer taxonomy and competency models
- **Batch Operations**: For bulk matching, batch API calls if supported

## Future Enhancements

- [ ] Combine Mercer and RAG scores for hybrid ranking
- [ ] Cache Mercer taxonomy lookups
- [ ] Support for batch job enrichment
- [ ] Mercer competency-based filtering
- [ ] Integration with Mercer salary data
- [ ] Real-time job taxonomy updates

