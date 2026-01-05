"""Project database model"""
from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
from pymongo.collection import Collection


class Project:
    """Project entity model"""
    
    def __init__(
        self,
        name: str,
        tenant_id: str,
        status: str,
        created_by: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.name = name
        self.description = description
        self.tenant_id = tenant_id
        self.status = status
        self.metadata = metadata or {}
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert project to dictionary"""
        return {
            "_id": self._id,
            "name": self.name,
            "description": self.description,
            "tenant_id": self.tenant_id,
            "status": self.status,
            "metadata": self.metadata,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """Create project from dictionary"""
        return cls(
            _id=data.get("_id"),
            name=data["name"],
            description=data.get("description"),
            tenant_id=data["tenant_id"],
            status=data["status"],
            metadata=data.get("metadata", {}),
            created_by=data["created_by"],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

    @staticmethod
    def get_collection(db) -> Collection:
        """Get MongoDB collection for projects"""
        return db.projects

