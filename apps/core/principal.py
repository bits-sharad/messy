"""Principal class for authorization context"""
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class Principal:
    """Represents an authenticated user/principal for authorization"""
    
    subject: str  # User ID or principal identifier
    tenant_id: Optional[str] = None  # Tenant/organization ID
    roles: Optional[List[str]] = None  # User roles (e.g., ['admin', 'user'])
    permissions: Optional[List[str]] = None  # Specific permissions
    
    def is_tenant_admin(self, tenant_id: Optional[str] = None) -> bool:
        """
        Check if principal is a tenant admin
        
        Args:
            tenant_id: Optional tenant ID to check against principal's tenant_id
            
        Returns:
            True if principal has admin role or is tenant admin
        """
        if self.roles and "admin" in self.roles:
            if tenant_id is None or self.tenant_id == tenant_id:
                return True
        return False
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if principal has a specific permission
        
        Args:
            permission: Permission string to check
            
        Returns:
            True if principal has the permission
        """
        if self.permissions:
            return permission in self.permissions
        return False
    
    def can_access_tenant(self, tenant_id: str) -> bool:
        """
        Check if principal can access a specific tenant
        
        Args:
            tenant_id: Tenant ID to check access for
            
        Returns:
            True if principal's tenant_id matches or is admin
        """
        if self.is_tenant_admin(tenant_id):
            return True
        return self.tenant_id == tenant_id

