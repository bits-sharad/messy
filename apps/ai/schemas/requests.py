"""AI/RAG request schemas"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CandidateProfileRequest(BaseModel):
    """Schema for candidate profile for job matching"""
    skills: List[str] = Field(..., description="List of candidate skills")
    experience_summary: Optional[str] = Field(None, description="Experience summary or resume text")
    education: Optional[str] = Field(None, description="Education background")
    desired_role: Optional[str] = Field(None, description="Desired job role or title")
    years_of_experience: Optional[int] = Field(None, description="Years of experience")
    location: Optional[str] = Field(None, description="Preferred location")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional candidate information")

    class Config:
        schema_extra = {
            "example": {
                "skills": ["Python", "FastAPI", "MongoDB", "Docker", "AWS"],
                "experience_summary": "5+ years of backend development experience...",
                "education": "BS Computer Science",
                "desired_role": "Senior Software Engineer",
                "years_of_experience": 5,
                "location": "Remote",
                "metadata": {"certifications": ["AWS Certified"]}
            }
        }


class JobDescriptionGenerationRequest(BaseModel):
    """Schema for generating job description using AI"""
    title: str = Field(..., description="Job title")
    department: Optional[str] = Field(None, description="Department")
    level: Optional[str] = Field(None, description="Job level")
    required_skills: Optional[List[str]] = Field(None, description="Required skills")
    responsibilities: Optional[List[str]] = Field(None, description="Key responsibilities")
    use_llm: bool = Field(True, description="Whether to use LLM or template-based generation")

    class Config:
        schema_extra = {
            "example": {
                "title": "Senior Software Engineer",
                "department": "Engineering",
                "level": "senior",
                "required_skills": ["Python", "FastAPI", "MongoDB"],
                "responsibilities": ["Design and develop APIs", "Lead code reviews"],
                "use_llm": True
            }
        }


class JobQuestionRequest(BaseModel):
    """Schema for asking questions about a job using RAG"""
    question: str = Field(..., description="Question about the job")
    job_id: str = Field(..., description="Job ID to ask about")

    class Config:
        schema_extra = {
            "example": {
                "question": "What skills are required for this position?",
                "job_id": "507f1f77bcf86cd799439011"
            }
        }


class SemanticJobSearchRequest(BaseModel):
    """Schema for semantic job search"""
    query: str = Field(..., description="Natural language search query")
    limit: int = Field(5, ge=1, le=50, description="Maximum number of results")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional filters (status, department, level)")

    class Config:
        schema_extra = {
            "example": {
                "query": "Python developer with MongoDB experience",
                "limit": 10,
                "filters": {"status": "published", "level": "senior"}
            }
        }


class JobIndexRequest(BaseModel):
    """Schema for indexing a job for semantic search"""
    job_id: str = Field(..., description="Job ID to index")

    class Config:
        schema_extra = {
            "example": {
                "job_id": "507f1f77bcf86cd799439011"
            }
        }


