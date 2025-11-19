"""
HTTP API entrypoint.

Exposes a limited REST surface for simulator clients. By default the
application uses in-memory repositories, but callers can provide a fully
wired `AuthService` (for example backed by MongoDB) via `create_app`.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, FastAPI, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from src.api.errors import (
    APIError,
    ErrorCode,
    api_error_handler,
    generic_exception_handler,
    http_exception_handler,
    validation_error_handler,
)
from src.api.schemas import (
    LoginRequest,
    RegistrationRequest,
    RegistrationResponse,
    TokenResponse,
    UserProfileResponse,
)
from src.cockpit.auth import AuthService, RegistrationError
from src.cockpit.memory import InMemoryAuthRepository, InMemoryUserRepository
from src.cockpit.services import UserService
from src.models import User

logger = logging.getLogger(__name__)

# Security settings (simple defaults for development)
SECRET_KEY = os.getenv("API_SECRET_KEY", "dev-secret-key-please-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_MIN", "60"))

# Security scheme for Bearer token
security = HTTPBearer()


def _build_in_memory_auth_service() -> AuthService:
    """Create an AuthService backed by in-memory repositories."""
    user_repo = InMemoryUserRepository()
    auth_repo = InMemoryAuthRepository()
    user_service = UserService(user_repo)
    return AuthService(user_service=user_service, auth_repository=auth_repo)


def create_app(auth_service: Optional[AuthService] = None) -> FastAPI:
    """
    Build a FastAPI application.

    Args:
        auth_service: Optional pre-configured AuthService instance.
    """

    service = auth_service or _build_in_memory_auth_service()
    app = FastAPI(
        title="Cosmic Flight Simulator API",
        version="0.1.0",
        description="Public HTTP interface for simulator user management.",
    )

    # Register global exception handlers
    from fastapi import HTTPException
    from fastapi.exceptions import RequestValidationError

    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    def get_auth_service() -> AuthService:
        return service

    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Security(security),
        auth_service: AuthService = Depends(get_auth_service),
    ) -> User:
        """
        Dependency that validates JWT token and returns the authenticated user.

        This is the access guard for protected routes.

        Args:
            credentials: Bearer token from Authorization header
            auth_service: AuthService instance

        Returns:
            Authenticated User instance

        Raises:
            APIError: If token is invalid, expired, or user not found
        """
        token = credentials.credentials

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise APIError(
                    code=ErrorCode.AUTH_INVALID_TOKEN,
                    message="Invalid authentication credentials",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
        except JWTError as exc:
            logger.warning("JWT validation failed: %s", exc)
            raise APIError(
                code=ErrorCode.AUTH_EXPIRED_TOKEN,
                message="Invalid or expired token",
                status_code=status.HTTP_401_UNAUTHORIZED,
            ) from exc

        user = auth_service.user_service.get_user(user_id)
        if user is None:
            raise APIError(
                code=ErrorCode.AUTH_USER_NOT_FOUND,
                message="User not found",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        return user

    @app.post(
        "/register",
        status_code=status.HTTP_201_CREATED,
        response_model=RegistrationResponse,
        summary="Register a new simulator user",
        response_description="The created user profile.",
    )
    def register_user(
        payload: RegistrationRequest,
        service: AuthService = Depends(get_auth_service),
    ) -> RegistrationResponse:
        """
        Register a new user profile with validated credentials.
        """

        try:
            result = service.register_user(
                username=payload.username,
                email=str(payload.email),
                password=payload.password,
                display_name=payload.display_name,
            )
        except RegistrationError as exc:
            error_message = str(exc)
            error_code = ErrorCode.VALIDATION_INVALID_FORMAT
            details = None

            # Map specific registration errors to error codes
            if "password" in error_message.lower():
                error_code = ErrorCode.VALIDATION_PASSWORD_POLICY
                details = {"field": "password", "message": error_message}
            elif (
                "username" in error_message.lower()
                and "already" in error_message.lower()
            ):
                error_code = ErrorCode.RESOURCE_ALREADY_EXISTS
                details = {"field": "username", "value": payload.username}
            elif (
                "email" in error_message.lower() and "already" in error_message.lower()
            ):
                error_code = ErrorCode.RESOURCE_ALREADY_EXISTS
                details = {"field": "email", "value": str(payload.email)}
            elif "username" in error_message.lower():
                error_code = ErrorCode.VALIDATION_USERNAME_INVALID
                details = {"field": "username"}
            elif "email" in error_message.lower():
                error_code = ErrorCode.VALIDATION_EMAIL_INVALID
                details = {"field": "email"}

            raise APIError(
                code=error_code,
                message=error_message,
                status_code=status.HTTP_400_BAD_REQUEST,
                details=details,
            ) from exc
        except ValueError as exc:
            error_message = str(exc)
            error_code = ErrorCode.VALIDATION_INVALID_FORMAT
            details = None

            # Map ValueError to appropriate error codes
            if "already exists" in error_message.lower():
                if "username" in error_message.lower():
                    error_code = ErrorCode.RESOURCE_ALREADY_EXISTS
                    details = {"field": "username", "value": payload.username}
                elif "email" in error_message.lower():
                    error_code = ErrorCode.RESOURCE_ALREADY_EXISTS
                    details = {"field": "email", "value": str(payload.email)}

            raise APIError(
                code=error_code,
                message=error_message,
                status_code=status.HTTP_400_BAD_REQUEST,
                details=details,
            ) from exc

        logger.info("Registered new user %s", result.user.id)
        return RegistrationResponse.from_result(result)

    @app.get(
        "/health",
        status_code=status.HTTP_200_OK,
        summary="API health check",
        response_description="Simple health response.",
    )
    def healthcheck() -> dict[str, str]:
        """Return a trivial health status payload."""
        return {"status": "ok"}

    @app.post(
        "/login",
        status_code=status.HTTP_200_OK,
        response_model=TokenResponse,
        summary="Authenticate and receive an access token",
        response_description="Bearer token and metadata.",
    )
    def login(
        payload: LoginRequest,
        service: AuthService = Depends(get_auth_service),
    ) -> TokenResponse:
        """Authenticate using username/password and return a JWT access token."""
        user = service.authenticate(payload.username, payload.password)
        if not user:
            raise APIError(
                code=ErrorCode.AUTH_INVALID_CREDENTIALS,
                message="Invalid username or password",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        expire = datetime.now(tz=timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        claims = {
            "sub": user.id,
            "username": user.username,
            "exp": int(expire.timestamp()),
            "iat": int(datetime.now(tz=timezone.utc).timestamp()),
        }
        try:
            token = jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)
        except JWTError as exc:
            logger.exception("Failed to encode JWT")
            raise APIError(
                code=ErrorCode.SERVER_TOKEN_GENERATION_FAILED,
                message="Token generation failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from exc

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    @app.get(
        "/me",
        status_code=status.HTTP_200_OK,
        response_model=UserProfileResponse,
        summary="Get current user profile",
        response_description="Authenticated user's profile information.",
    )
    def get_current_user_profile(
        current_user: User = Depends(get_current_user),
    ) -> UserProfileResponse:
        """
        Protected route that returns the authenticated user's profile.

        Requires a valid JWT token in the Authorization header.
        """
        return UserProfileResponse.from_user(current_user)

    return app


app = create_app()
