"""Job database model"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
from pymongo.collection import Collection


class Job:
    """Job entity model"""
    
    def __init__(
        self,
        project_id: str,
        title: str,
        job_code: str,
        status: str,
        created_by: str,
        description: Optional[str] = None,
        department: Optional[str] = None,
        level: Optional[str] = None,
        required_skills: Optional[List[str]] = None,
        responsibilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.project_id = project_id
        self.title = title
        self.description = description
        self.job_code = job_code
        self.status = status
        self.department = department
        self.level = level
        self.required_skills = required_skills or []
        self.responsibilities = responsibilities or []
        self.metadata = metadata or {}
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert job to dictionary"""
        return {
            "_id": self._id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "job_code": self.job_code,
            "status": self.status,
            "department": self.department,
            "level": self.level,
            "required_skills": self.required_skills,
            "responsibilities": self.responsibilities,
            "metadata": self.metadata,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Job":
        """Create job from dictionary"""
        return cls(
            _id=data.get("_id"),
            project_id=data["project_id"],
            title=data["title"],
            description=data.get("description"),
            job_code=data["job_code"],
            status=data["status"],
            department=data.get("department"),
            level=data.get("level"),
            required_skills=data.get("required_skills", []),
            responsibilities=data.get("responsibilities", []),
            metadata=data.get("metadata", {}),
            created_by=data["created_by"],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

    @staticmethod
    def get_collection(db) -> Collection:
        """Get MongoDB collection for jobs"""
        return db.jobs

