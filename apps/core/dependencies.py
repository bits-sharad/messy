"""Dependency injection for FastAPI"""
from fastapi import Header, HTTPException, status
from typing import Optional

from apps.core.client import CoreAPIClient
from apps.core.principal import Principal


# Singleton instance of CoreAPIClient
_core_api_instance: Optional[CoreAPIClient] = None


def get_core_api() -> CoreAPIClient:
    """
    Dependency function to get CoreAPIClient instance
    
    Returns:
        CoreAPIClient instance
    """
    global _core_api_instance
    if _core_api_instance is None:
        _core_api_instance = CoreAPIClient()
    return _core_api_instance


def get_principal(
    x_principal_subject: Optional[str] = Header(None, alias="X-Principal-Subject"),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    x_roles: Optional[str] = Header(None, alias="X-Roles"),
    x_permissions: Optional[str] = Header(None, alias="X-Permissions")
) -> Principal:
    """
    Dependency function to extract Principal from headers
    
    In a real application, this would validate tokens, extract from JWT, etc.
    For now, we'll use headers to pass principal information.
    
    Args:
        x_principal_subject: Principal subject (user ID) from header
        x_tenant_id: Tenant ID from header
        x_roles: Comma-separated roles from header
        x_permissions: Comma-separated permissions from header
        
    Returns:
        Principal object
        
    Raises:
        HTTPException: If principal subject is missing
    """
    if not x_principal_subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Principal-Subject header"
        )
    
    roles = None
    if x_roles:
        roles = [r.strip() for r in x_roles.split(",") if r.strip()]
    
    permissions = None
    if x_permissions:
        permissions = [p.strip() for p in x_permissions.split(",") if p.strip()]
    
    return Principal(
        subject=x_principal_subject,
        tenant_id=x_tenant_id,
        roles=roles,
        permissions=permissions
    )

