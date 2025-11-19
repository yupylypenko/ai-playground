"""
API package exposing FastAPI application factory and error handling.
"""

from src.api.app import app, create_app
from src.api.errors import APIError, ErrorCode, ErrorResponse

__all__ = ["app", "create_app", "APIError", "ErrorCode", "ErrorResponse"]
