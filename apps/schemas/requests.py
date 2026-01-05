"""Request schemas for API endpoints"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class ProjectStatus(str, Enum):
    """Project status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class JobStatus(str, Enum):
    """Job status enum"""
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"


class JobLevel(str, Enum):
    """Job level enum"""
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"


class ProjectCreateRequest(BaseModel):
    """Schema for creating a new project"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=2000, description="Project description")
    tenant_id: str = Field(..., description="Tenant/organization ID")
    status: ProjectStatus = Field(..., description="Project status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata as key-value pairs")
    created_by: str = Field(..., description="Principal subject/user ID who created the project")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Q4 Recruitment Drive",
                "description": "Recruitment project for Q4 2024",
                "tenant_id": "tenant_123",
                "status": "active",
                "metadata": {"department": "Engineering", "budget": 50000},
                "created_by": "user_456"
            }
        }


class ProjectUpdateRequest(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=2000, description="Project description")
    status: Optional[ProjectStatus] = Field(None, description="Project status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata (will be merged with existing)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Q4 Recruitment Drive - Updated",
                "description": "Updated recruitment project for Q4 2024",
                "status": "active",
                "metadata": {"department": "Engineering", "budget": 60000}
            }
        }


class JobCreateRequest(BaseModel):
    """Schema for creating a new job"""
    project_id: str = Field(..., description="Project ID this job belongs to")
    title: str = Field(..., min_length=1, max_length=255, description="Job title")
    description: Optional[str] = Field(None, description="Job description")
    job_code: str = Field(..., description="Job code, must be unique within project")
    status: JobStatus = Field(..., description="Job status")
    department: Optional[str] = Field(None, description="Department")
    level: Optional[JobLevel] = Field(None, description="Job level")
    required_skills: Optional[List[str]] = Field(None, description="Required skill tags")
    responsibilities: Optional[List[str]] = Field(None, description="Job responsibilities")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_by: str = Field(..., description="Principal subject/user ID who created the job")

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "507f1f77bcf86cd799439011",
                "title": "Senior Software Engineer",
                "description": "Looking for an experienced software engineer",
                "job_code": "ENG-001",
                "status": "published",
                "department": "Engineering",
                "level": "senior",
                "required_skills": ["Python", "FastAPI", "MongoDB"],
                "responsibilities": ["Design and develop APIs", "Mentor junior developers"],
                "metadata": {"salary_range": "100k-150k", "location": "Remote"},
                "created_by": "user_456"
            }
        }


class JobUpdateRequest(BaseModel):
    """Schema for updating a job"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Job title")
    description: Optional[str] = Field(None, description="Job description")
    status: Optional[JobStatus] = Field(None, description="Job status")
    department: Optional[str] = Field(None, description="Department")
    level: Optional[JobLevel] = Field(None, description="Job level")
    required_skills: Optional[List[str]] = Field(None, description="Required skill tags (replaces existing)")
    responsibilities: Optional[List[str]] = Field(None, description="Job responsibilities (replaces existing)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata (will be merged with existing)")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Senior Software Engineer - Updated",
                "description": "Updated job description",
                "status": "published",
                "department": "Engineering",
                "level": "senior",
                "required_skills": ["Python", "FastAPI", "MongoDB", "Docker"],
                "responsibilities": ["Design and develop APIs", "Mentor junior developers", "Code reviews"],
                "metadata": {"salary_range": "110k-160k", "location": "Hybrid"}
            }
        }

