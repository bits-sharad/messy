"""Response schemas for API endpoints"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: str = Field(..., description="MongoDB ObjectId as string")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    tenant_id: str = Field(..., description="Tenant/organization ID")
    status: str = Field(..., description="Project status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_by: str = Field(..., description="Principal subject/user ID who created the project")
    created_at: datetime = Field(..., description="Creation timestamp in ISO 8601 format")
    updated_at: datetime = Field(..., description="Last update timestamp")
    job_count: Optional[int] = Field(None, description="Number of jobs in the project")

    class Config:
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Q4 Recruitment Drive",
                "description": "Recruitment project for Q4 2024",
                "tenant_id": "tenant_123",
                "status": "active",
                "metadata": {"department": "Engineering", "budget": 50000},
                "created_by": "user_456",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "job_count": 5
            }
        }


class JobResponse(BaseModel):
    """Schema for job response"""
    id: str = Field(..., description="MongoDB ObjectId as string")
    project_id: str = Field(..., description="Project ID this job belongs to")
    title: str = Field(..., description="Job title")
    description: Optional[str] = Field(None, description="Job description")
    job_code: str = Field(..., description="Job code, unique within project")
    status: str = Field(..., description="Job status")
    department: Optional[str] = Field(None, description="Department")
    level: Optional[str] = Field(None, description="Job level")
    required_skills: Optional[List[str]] = Field(None, description="Required skill tag IDs")
    responsibilities: Optional[List[str]] = Field(None, description="Job responsibilities")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_by: str = Field(..., description="Principal subject/user ID who created the job")
    created_at: datetime = Field(..., description="Creation timestamp in ISO 8601 format")
    updated_at: datetime = Field(..., description="Last update timestamp")
    match_count: Optional[int] = Field(None, description="Number of candidates matched")

    class Config:
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439012",
                "project_id": "507f1f77bcf86cd799439011",
                "title": "Senior Software Engineer",
                "description": "Looking for an experienced software engineer",
                "job_code": "ENG-001",
                "status": "published",
                "department": "Engineering",
                "level": "senior",
                "required_skills": ["skill_123", "skill_456"],
                "responsibilities": ["Design and develop APIs", "Mentor junior developers"],
                "metadata": {"salary_range": "100k-150k", "location": "Remote"},
                "created_by": "user_456",
                "created_at": "2024-01-15T11:00:00Z",
                "updated_at": "2024-01-15T11:00:00Z",
                "match_count": 5
            }
        }

