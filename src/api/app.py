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

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

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
            HTTPException: If token is invalid, expired, or user not found
        """
        token = credentials.credentials

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except JWTError as exc:
            logger.warning("JWT validation failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        user = auth_service.user_service.get_user(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token generation failed",
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
