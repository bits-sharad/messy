"""AI/RAG response schemas"""
from typing import List, Optional
from pydantic import BaseModel, Field


class MatchResultResponse(BaseModel):
    """Schema for job-candidate match result"""
    job_id: str = Field(..., description="Job ID")
    job_title: str = Field(..., description="Job title")
    match_score: float = Field(..., ge=0.0, le=1.0, description="Match score (0-1)")
    match_reasons: List[str] = Field(..., description="Reasons for the match")
    missing_skills: List[str] = Field(default_factory=list, description="Required skills candidate lacks")
    matched_skills: List[str] = Field(default_factory=list, description="Skills that match")

    class Config:
        schema_extra = {
            "example": {
                "job_id": "507f1f77bcf86cd799439012",
                "job_title": "Senior Software Engineer",
                "match_score": 0.85,
                "match_reasons": ["Excellent semantic match", "Matches 4 required skills", "Level: senior"],
                "missing_skills": ["Kubernetes"],
                "matched_skills": ["Python", "FastAPI", "MongoDB", "Docker"]
            }
        }


class JobDescriptionResponse(BaseModel):
    """Schema for generated job description"""
    description: str = Field(..., description="Generated job description")
    generated_by: str = Field(..., description="Generation method (llm or template)")

    class Config:
        schema_extra = {
            "example": {
                "description": "# Senior Software Engineer\n\n**Department:** Engineering\n...",
                "generated_by": "llm"
            }
        }


class SemanticSearchResultResponse(BaseModel):
    """Schema for semantic search result"""
    job_id: str = Field(..., description="Job ID")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    title: str = Field(..., description="Job title")
    department: Optional[str] = Field(None, description="Department")
    level: Optional[str] = Field(None, description="Job level")

    class Config:
        schema_extra = {
            "example": {
                "job_id": "507f1f77bcf86cd799439012",
                "score": 0.92,
                "title": "Senior Software Engineer",
                "department": "Engineering",
                "level": "senior"
            }
        }


class JobQuestionResponse(BaseModel):
    """Schema for job question answer"""
    answer: str = Field(..., description="Answer to the question")
    job_id: str = Field(..., description="Job ID the answer is about")

    class Config:
        schema_extra = {
            "example": {
                "answer": "This position requires Python, FastAPI, and MongoDB experience...",
                "job_id": "507f1f77bcf86cd799439012"
            }
        }


class JobIndexResponse(BaseModel):
    """Schema for job indexing response"""
    job_id: str = Field(..., description="Job ID")
    success: bool = Field(..., description="Whether indexing was successful")
    message: str = Field(..., description="Status message")

    class Config:
        schema_extra = {
            "example": {
                "job_id": "507f1f77bcf86cd799439012",
                "success": True,
                "message": "Job indexed successfully"
            }
        }


