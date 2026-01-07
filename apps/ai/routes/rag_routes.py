"""API routes for RAG and AI features"""
from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse

from apps.core.client import CoreAPIClient
from apps.core.principal import Principal
from apps.core.dependencies import get_core_api, get_principal
from apps.ai.services.rag_service import RAGService
from apps.services.mmc_jobs import JobService
from apps.ai.schemas.requests import (
    CandidateProfileRequest,
    JobDescriptionGenerationRequest,
    JobQuestionRequest,
    SemanticJobSearchRequest
)
from apps.ai.schemas.responses import (
    MatchResultResponse,
    JobDescriptionResponse,
    SemanticSearchResultResponse,
    JobQuestionResponse
)

router = APIRouter(prefix="/api/v1/ai", tags=["AI & RAG"])

# Initialize RAG service (singleton)
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Dependency to get RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


@router.post(
    "/jobs/match-candidate",
    response_model=List[MatchResultResponse],
    status_code=status.HTTP_200_OK,
    summary="Match candidate to jobs using RAG and Mercer library",
    description="Use RAG and/or Mercer job library to find the best matching jobs for a candidate profile"
)
async def match_candidate_to_jobs(
    candidate: CandidateProfileRequest,
    job_ids: Optional[List[str]] = None,
    limit: int = 10,
    use_mercer: Optional[bool] = None,
    principal: Principal = Depends(get_principal),
    rag_service: RAGService = Depends(get_rag_service),
    core_api: CoreAPIClient = Depends(get_core_api)
):
    """Match a candidate profile to relevant jobs using RAG and/or Mercer library"""
    try:
        # Convert candidate request to dict
        candidate_profile = candidate.dict()
        
        # Match candidate to jobs (will use Mercer if available and enabled)
        matches = rag_service.match_candidate_to_jobs(
            candidate_profile=candidate_profile,
            job_ids=job_ids,
            limit=limit,
            use_mercer=use_mercer
        )
        
        # Convert to response format
        results = [
            MatchResultResponse(
                job_id=match.job_id,
                job_title=match.job_title,
                match_score=match.match_score,
                match_reasons=match.match_reasons,
                missing_skills=match.missing_skills,
                matched_skills=match.matched_skills
            )
            for match in matches
        ]
        
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error matching candidate: {str(e)}"
        )


@router.post(
    "/jobs/generate-description",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate job description using AI",
    description="Generate a professional job description using LLM or template"
)
async def generate_job_description(
    request: JobDescriptionGenerationRequest,
    principal: Principal = Depends(get_principal),
    rag_service: RAGService = Depends(get_rag_service)
):
    """Generate a job description using AI"""
    try:
        requirements = request.dict()
        use_llm = requirements.pop("use_llm", True)
        
        description = rag_service.generate_job_description(
            requirements=requirements,
            use_llm=use_llm
        )
        
        return JobDescriptionResponse(
            description=description,
            generated_by="llm" if use_llm else "template"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating job description: {str(e)}"
        )


@router.post(
    "/jobs/search-semantic",
    response_model=List[SemanticSearchResultResponse],
    status_code=status.HTTP_200_OK,
    summary="Semantic search for jobs",
    description="Search jobs using natural language query with semantic similarity"
)
async def semantic_job_search(
    request: SemanticJobSearchRequest,
    principal: Principal = Depends(get_principal),
    rag_service: RAGService = Depends(get_rag_service)
):
    """Search jobs using semantic similarity"""
    try:
        results = rag_service.search_similar_jobs(
            query=request.query,
            limit=request.limit,
            filters=request.filters
        )
        
        # Convert to response format
        search_results = [
            SemanticSearchResultResponse(
                job_id=result["job_id"],
                score=result["score"],
                title=result["metadata"].get("title", "Unknown"),
                department=result["metadata"].get("department"),
                level=result["metadata"].get("level")
            )
            for result in results
        ]
        
        return search_results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing semantic search: {str(e)}"
        )


@router.post(
    "/jobs/{job_id}/ask",
    response_model=JobQuestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask questions about a job using RAG",
    description="Answer questions about a specific job using RAG and LLM"
)
async def ask_job_question(
    job_id: str,
    question_request: JobQuestionRequest,
    principal: Principal = Depends(get_principal),
    rag_service: RAGService = Depends(get_rag_service),
    core_api: CoreAPIClient = Depends(get_core_api)
):
    """Answer a question about a job using RAG"""
    try:
        # Validate job_id matches request
        if question_request.job_id != job_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="job_id in path must match job_id in request body"
            )
        
        # Get job details for context
        job_service = JobService(core_api)
        try:
            job_data = await job_service.get_job(job_id)
            context_jobs = [job_data]
        except Exception:
            context_jobs = None
        
        # Answer question using RAG
        answer = rag_service.answer_job_question(
            question=question_request.question,
            job_id=job_id,
            context_jobs=context_jobs
        )
        
        return JobQuestionResponse(
            answer=answer,
            job_id=job_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error answering question: {str(e)}"
        )


@router.post(
    "/jobs/{job_id}/index",
    status_code=status.HTTP_200_OK,
    summary="Index a job for semantic search",
    description="Add or update a job in the vector database for semantic search"
)
async def index_job(
    job_id: str,
    principal: Principal = Depends(get_principal),
    rag_service: RAGService = Depends(get_rag_service),
    core_api: CoreAPIClient = Depends(get_core_api)
):
    """Index a job for semantic search"""
    try:
        # Get job data
        job_service = JobService(core_api)
        job_data = await job_service.get_job(job_id)
        
        # Index the job
        success = rag_service.index_job(job_id=job_id, job_data=job_data)
        
        if success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": f"Job {job_id} indexed successfully", "job_id": job_id}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to index job. RAG service may not be properly configured."
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error indexing job: {str(e)}"
        )

