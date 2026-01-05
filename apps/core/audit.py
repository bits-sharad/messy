"""Audit trail for tracking operations"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class AuditEntry:
    """Represents a single audit log entry"""
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    principal: Optional[str] = None


class AuditTrail:
    """Audit trail manager for logging operations"""
    
    def __init__(self):
        """Initialize audit trail"""
        self._entries: List[AuditEntry] = []
    
    def add(
        self,
        action: str,
        metadata: Dict[str, Any],
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        principal: Optional[str] = None
    ) -> None:
        """
        Add an audit entry
        
        Args:
            action: Action performed (e.g., "project_created", "job_updated")
            metadata: Additional metadata about the action
            resource_type: Type of resource (e.g., "project", "job")
            resource_id: ID of the resource affected
            principal: Principal/user who performed the action
        """
        # Try to extract resource info from metadata if not provided
        if not resource_type:
            resource_type = metadata.get("resource_type", "unknown")
        if not resource_id:
            resource_id = metadata.get("resource_id") or metadata.get("id")
        if not principal:
            principal = metadata.get("principal") or metadata.get("created_by") or metadata.get("principal_subject")
        
        entry = AuditEntry(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata,
            principal=principal
        )
        
        self._entries.append(entry)
        
        # In production, this would typically write to a database or logging service
        # For now, we'll print it (can be replaced with proper logging)
        print(f"[AUDIT] {entry.timestamp.isoformat()} | {action} | {resource_type}:{resource_id} | principal:{principal}")
    
    def get_entries(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        principal: Optional[str] = None
    ) -> List[AuditEntry]:
        """
        Get audit entries matching filters
        
        Args:
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            action: Filter by action
            principal: Filter by principal
            
        Returns:
            List of matching audit entries
        """
        entries = self._entries
        
        if resource_type:
            entries = [e for e in entries if e.resource_type == resource_type]
        if resource_id:
            entries = [e for e in entries if e.resource_id == resource_id]
        if action:
            entries = [e for e in entries if e.action == action]
        if principal:
            entries = [e for e in entries if e.principal == principal]
        
        return entries
    
    def clear(self) -> None:
        """Clear all audit entries (mainly for testing)"""
        self._entries.clear()
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """
        Convert audit entries to list of dictionaries
        
        Returns:
            List of dictionaries representing audit entries
        """
        return [
            {
                "action": entry.action,
                "resource_type": entry.resource_type,
                "resource_id": entry.resource_id,
                "metadata": entry.metadata,
                "timestamp": entry.timestamp.isoformat(),
                "principal": entry.principal
            }
            for entry in self._entries
        ]

