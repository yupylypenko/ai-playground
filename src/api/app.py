"""
HTTP API entrypoint.

Exposes a limited REST surface for simulator clients. By default the
application uses in-memory repositories, but callers can provide a fully
wired `AuthService` (for example backed by MongoDB) via `create_app`.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status

from src.api.schemas import RegistrationRequest, RegistrationResponse
from src.cockpit.auth import AuthService, RegistrationError
from src.cockpit.memory import InMemoryAuthRepository, InMemoryUserRepository
from src.cockpit.services import UserService

logger = logging.getLogger(__name__)


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

    return app


app = create_app()
