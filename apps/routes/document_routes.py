"""API routes for document processing"""
from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse

from apps.core.client import CoreAPIClient
from apps.core.principal import Principal
from apps.core.dependencies import get_core_api, get_principal
from apps.services.document_service import DocumentService
from apps.ai.services.rag_service import RAGService

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

# Singleton RAG service instance
_rag_service_instance: Optional[RAGService] = None

def get_rag_service() -> RAGService:
    """Get RAG service instance"""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance

def get_document_service(
    rag_service: RAGService = Depends(get_rag_service)
) -> DocumentService:
    """Dependency to get document service instance"""
    return DocumentService(rag_service=rag_service)


@router.post(
    "/process/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Process a document from job_documents collection",
    description="Extract text from PDF and generate embeddings for a document"
)
async def process_document(
    document_id: str,
    job_id: Optional[str] = None,
    generate_embeddings: bool = True,
    principal: Principal = Depends(get_principal),
    document_service: DocumentService = Depends(get_document_service)
):
    """Process a single document from job_documents collection"""
    try:
        result = await document_service.process_document(
            document_id=document_id,
            job_id=job_id,
            generate_embeddings=generate_embeddings
        )
        
        if result.get("success"):
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=result
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to process document")
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@router.post(
    "/process-all",
    status_code=status.HTTP_200_OK,
    summary="Process all unprocessed documents",
    description="Process all documents from job_documents collection that haven't been processed"
)
async def process_all_documents(
    job_id: Optional[str] = None,
    generate_embeddings: bool = True,
    principal: Principal = Depends(get_principal),
    document_service: DocumentService = Depends(get_document_service)
):
    """Process all unprocessed documents"""
    try:
        result = await document_service.process_all_documents(
            job_id=job_id,
            generate_embeddings=generate_embeddings
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing documents: {str(e)}"
        )


@router.get(
    "/job/{job_id}",
    status_code=status.HTTP_200_OK,
    summary="Get document content for a job",
    description="Retrieve all processed document content for a specific job"
)
async def get_job_documents(
    job_id: str,
    principal: Principal = Depends(get_principal),
    document_service: DocumentService = Depends(get_document_service)
):
    """Get document content for a job"""
    try:
        result = await document_service.get_document_content(job_id=job_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching documents: {str(e)}"
        )


@router.get(
    "/project/{project_id}",
    status_code=status.HTTP_200_OK,
    summary="Get document content for a project",
    description="Retrieve all processed document content for a project"
)
async def get_project_documents(
    project_id: str,
    principal: Principal = Depends(get_principal),
    document_service: DocumentService = Depends(get_document_service)
):
    """Get document content for a project"""
    try:
        result = await document_service.get_documents_for_project(project_id=project_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching documents: {str(e)}"
        )

