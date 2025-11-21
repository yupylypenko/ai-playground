"""
Error mapping helper functions for API endpoints.

Provides reusable functions to map exceptions to standardized API errors,
reducing code duplication and improving maintainability.
"""

from __future__ import annotations

from typing import Any

from fastapi import status

from src.api.errors import APIError, ErrorCode


def map_validation_error(
    error_message: str,
    field_name: str | None = None,
    field_value: Any = None,
) -> tuple[ErrorCode, dict[str, Any] | None]:
    """
    Map a validation error message to an error code and details.

    Args:
        error_message: The error message from the exception
        field_name: Optional field name that caused the error
        field_value: Optional field value that caused the error

    Returns:
        Tuple of (ErrorCode, details dict or None)
    """
    error_message_lower = error_message.lower()
    details = None

    if field_name:
        details = {"field": field_name}
        if field_value is not None:
            details["value"] = field_value

    # Mission type validation
    if "mission type" in error_message_lower:
        return ErrorCode.VALIDATION_MISSION_TYPE_INVALID, details

    # Difficulty validation
    if "difficulty" in error_message_lower:
        return ErrorCode.VALIDATION_DIFFICULTY_INVALID, details

    # Name validation
    if "name" in error_message_lower and "empty" in error_message_lower:
        return ErrorCode.VALIDATION_INVALID_FORMAT, details

    # Resource not found
    if "not found" in error_message_lower:
        return ErrorCode.RESOURCE_NOT_FOUND, details

    # Default validation error
    return ErrorCode.VALIDATION_INVALID_FORMAT, details


def create_validation_api_error(
    exception: ValueError,
    field_name: str | None = None,
    field_value: Any = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> APIError:
    """
    Create an APIError from a ValueError with automatic error code mapping.

    Args:
        exception: The ValueError exception
        field_name: Optional field name that caused the error
        field_value: Optional field value that caused the error
        status_code: HTTP status code (default: 400)

    Returns:
        APIError instance with appropriate error code and details
    """
    error_code, details = map_validation_error(
        str(exception), field_name=field_name, field_value=field_value
    )

    return APIError(
        code=error_code,
        message=str(exception),
        status_code=status_code,
        details=details,
    )
