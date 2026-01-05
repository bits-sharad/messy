"""Core module for API client, principal, exceptions, and audit"""
from apps.core.client import CoreAPIClient
from apps.core.principal import Principal
from apps.core.exceptions import (
    ResourceNotFoundError,
    UnauthorizedError,
    ValidationError,
    ConflictError,
    InternalServerError
)
from apps.core.audit import AuditTrail, AuditEntry
from apps.core.dependencies import get_core_api, get_principal

__all__ = [
    "CoreAPIClient",
    "Principal",
    "ResourceNotFoundError",
    "UnauthorizedError",
    "ValidationError",
    "ConflictError",
    "InternalServerError",
    "AuditTrail",
    "AuditEntry",
    "get_core_api",
    "get_principal"
]

