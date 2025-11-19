"""
API Error Handling

Standardized error responses and error codes for the Cosmic Flight Simulator API.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """Machine-readable error codes for API responses."""

    # Authentication Errors
    AUTH_REQUIRED = "AUTH_REQUIRED"
    AUTH_INVALID_TOKEN = "AUTH_INVALID_TOKEN"
    AUTH_EXPIRED_TOKEN = "AUTH_EXPIRED_TOKEN"
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_USER_NOT_FOUND = "AUTH_USER_NOT_FOUND"

    # Validation Errors
    VALIDATION_REQUIRED = "VALIDATION_REQUIRED"
    VALIDATION_INVALID_FORMAT = "VALIDATION_INVALID_FORMAT"
    VALIDATION_OUT_OF_RANGE = "VALIDATION_OUT_OF_RANGE"
    VALIDATION_PASSWORD_POLICY = "VALIDATION_PASSWORD_POLICY"
    VALIDATION_EMAIL_INVALID = "VALIDATION_EMAIL_INVALID"
    VALIDATION_USERNAME_INVALID = "VALIDATION_USERNAME_INVALID"

    # Resource Errors
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"

    # Server Errors
    SERVER_INTERNAL_ERROR = "SERVER_INTERNAL_ERROR"
    SERVER_TOKEN_GENERATION_FAILED = "SERVER_TOKEN_GENERATION_FAILED"
    SERVER_DATABASE_ERROR = "SERVER_DATABASE_ERROR"
    SERVER_SERVICE_UNAVAILABLE = "SERVER_SERVICE_UNAVAILABLE"


class ErrorDetail(BaseModel):
    """Error response detail structure."""

    code: ErrorCode = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error message")
    details: Optional[dict[str, Any]] = Field(
        default=None, description="Additional error context"
    )
    timestamp: str = Field(description="ISO 8601 timestamp of the error")
    path: str = Field(description="API endpoint path where error occurred")


class ErrorResponse(BaseModel):
    """Standardized error response format."""

    error: ErrorDetail


class APIError(Exception):
    """
    Custom exception for API errors with standardized format.

    Args:
        code: Error code from ErrorCode enum
        message: Human-readable error message
        status_code: HTTP status code
        details: Optional additional context
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

    def to_response(self, request: Request) -> ErrorResponse:
        """Convert APIError to standardized ErrorResponse."""
        return ErrorResponse(
            error=ErrorDetail(
                code=self.code,
                message=self.message,
                details=self.details,
                timestamp=datetime.now(timezone.utc).isoformat(),
                path=str(request.url.path),
            )
        )


def create_error_response(
    request: Request,
    code: ErrorCode,
    message: str,
    status_code: int,
    details: Optional[dict[str, Any]] = None,
) -> JSONResponse:
    """
    Create a standardized error response.

    Args:
        request: FastAPI request object
        code: Error code
        message: Error message
        status_code: HTTP status code
        details: Optional additional context

    Returns:
        JSONResponse with standardized error format
    """
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
            details=details,
            timestamp=datetime.now(timezone.utc).isoformat(),
            path=str(request.url.path),
        )
    )
    return JSONResponse(status_code=status_code, content=error_response.model_dump())


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle APIError exceptions."""
    return create_error_response(
        request=request,
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = exc.errors()
    field_errors: dict[str, list[str]] = {}

    for error in errors:
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        if not field:
            field = "body"
        if field not in field_errors:
            field_errors[field] = []
        field_errors[field].append(error["msg"])

    # Determine error code based on error type
    error_code = ErrorCode.VALIDATION_INVALID_FORMAT
    if any("required" in str(e.get("type", "")).lower() for e in errors):
        error_code = ErrorCode.VALIDATION_REQUIRED

    return create_error_response(
        request=request,
        code=error_code,
        message="Validation error",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"fields": field_errors},
    )


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle FastAPI HTTPException.

    Attempts to extract error code from exception detail if it's an APIError format,
    otherwise uses generic error codes based on status code.
    """
    from fastapi import HTTPException

    if not isinstance(exc, HTTPException):
        return await generic_exception_handler(request, exc)

    status_code = exc.status_code

    # Try to extract error code from detail if it's a dict
    error_code = ErrorCode.SERVER_INTERNAL_ERROR
    message = str(exc.detail)
    details = None

    if isinstance(exc.detail, dict) and "code" in exc.detail:
        try:
            error_code = ErrorCode(exc.detail["code"])
            message = exc.detail.get("message", message)
            details = exc.detail.get("details")
        except (ValueError, KeyError):
            pass

    # Map status codes to error codes if not already set
    if error_code == ErrorCode.SERVER_INTERNAL_ERROR:
        if status_code == 401:
            error_code = ErrorCode.AUTH_REQUIRED
        elif status_code == 404:
            error_code = ErrorCode.RESOURCE_NOT_FOUND
        elif status_code == 409:
            error_code = ErrorCode.RESOURCE_ALREADY_EXISTS
        elif status_code == 400:
            error_code = ErrorCode.VALIDATION_INVALID_FORMAT

    return create_error_response(
        request=request,
        code=error_code,
        message=message,
        status_code=status_code,
        details=details,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    import logging

    logger = logging.getLogger(__name__)
    logger.exception("Unhandled exception: %s", exc)

    return create_error_response(
        request=request,
        code=ErrorCode.SERVER_INTERNAL_ERROR,
        message="An unexpected error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details=None,
    )
