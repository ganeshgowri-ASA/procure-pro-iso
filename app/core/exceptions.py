"""Custom exceptions for the application."""

from typing import Any, Optional


class AppException(Exception):
    """Base exception for all application exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundException(AppException):
    """Resource not found exception."""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with id '{identifier}' not found",
            status_code=404,
        )


class DuplicateException(AppException):
    """Duplicate resource exception."""

    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            message=f"{resource} with {field} '{value}' already exists",
            status_code=409,
        )


class ValidationException(AppException):
    """Validation error exception."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=422,
            details=details,
        )


class UnauthorizedException(AppException):
    """Unauthorized access exception."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=401,
        )


class ForbiddenException(AppException):
    """Forbidden access exception."""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            message=message,
            status_code=403,
        )


class WorkflowException(AppException):
    """Workflow state transition exception."""

    def __init__(self, current_status: str, target_status: str):
        super().__init__(
            message=f"Cannot transition from '{current_status}' to '{target_status}'",
            status_code=400,
        )
