"""Domain exceptions used across the backend."""
from __future__ import annotations


class AppError(Exception):
    """Base application error.

    Subclasses translate to HTTP errors via the FastAPI exception handlers.
    """

    code: str = "internal_error"
    http_status: int = 500
    message: str = "Internal server error"

    def __init__(self, message: str | None = None, details: dict | None = None) -> None:
        super().__init__(message or self.message)
        self.message_override = message
        self.details = details or {}

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message_override or self.message,
            "details": self.details,
        }


class NotFoundError(AppError):
    code = "not_found"
    http_status = 404
    message = "Resource not found"


class ValidationError(AppError):
    code = "validation_error"
    http_status = 400
    message = "Invalid input"


class ConflictError(AppError):
    code = "conflict"
    http_status = 409
    message = "Conflict with existing data"


class NotConfiguredError(AppError):
    code = "not_configured"
    http_status = 501
    message = "Provider not configured"