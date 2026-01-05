"""Custom exception classes for API error handling"""
from fastapi import HTTPException, status


class ResourceNotFoundError(HTTPException):
    """Exception raised when a resource is not found (404)"""
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_type} with id {resource_id} not found"
        )


class UnauthorizedError(HTTPException):
    """Exception raised when user lacks permissions (403)"""
    def __init__(self, message: str = "Not authorized to perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )


class ValidationError(HTTPException):
    """Exception raised when request data validation fails (400)"""
    def __init__(self, message: str, errors: dict = None):
        detail = {"message": message}
        if errors:
            detail["errors"] = errors
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class ConflictError(HTTPException):
    """Exception raised when there's a conflict (e.g., duplicate resource) (409)"""
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=message
        )


class InternalServerError(HTTPException):
    """Exception raised for internal server errors (500)"""
    def __init__(self, message: str = "An internal server error occurred"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )

