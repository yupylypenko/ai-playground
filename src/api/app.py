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

from src.api.error_helpers import create_validation_api_error
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
    MissionCreateRequest,
    MissionResponse,
    ProjectCreateRequest,
    ProjectResponse,
    RegistrationRequest,
    RegistrationResponse,
    TokenResponse,
    UserProfileResponse,
)
from src.cockpit.auth import AuthService, RegistrationError
from src.cockpit.memory import (
    InMemoryAuthRepository,
    InMemoryMissionRepository,
    InMemoryProjectRepository,
    InMemoryUserRepository,
)
from src.cockpit.services import MissionService, ProjectService, UserService
from src.models import Objective, User

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


# Shared repository instances for dependency injection
_shared_project_repo: Optional[InMemoryProjectRepository] = None
_shared_mission_repo: Optional[InMemoryMissionRepository] = None


def _get_shared_project_repo() -> InMemoryProjectRepository:
    """Get or create shared project repository instance."""
    global _shared_project_repo
    if _shared_project_repo is None:
        _shared_project_repo = InMemoryProjectRepository()
    return _shared_project_repo


def _get_shared_mission_repo() -> InMemoryMissionRepository:
    """Get or create shared mission repository instance."""
    global _shared_mission_repo
    if _shared_mission_repo is None:
        _shared_mission_repo = InMemoryMissionRepository()
    return _shared_mission_repo


def _build_in_memory_project_service() -> ProjectService:
    """Create a ProjectService backed by in-memory repository."""
    return ProjectService(project_repository=_get_shared_project_repo())


def _build_in_memory_mission_service() -> MissionService:
    """Create a MissionService backed by in-memory repository."""
    return MissionService(mission_repository=_get_shared_mission_repo())


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

    def get_project_service() -> ProjectService:
        """Get ProjectService instance."""
        return _build_in_memory_project_service()

    def get_mission_service() -> MissionService:
        """Get MissionService instance."""
        return _build_in_memory_mission_service()

    def get_project_service_for_mission() -> ProjectService:
        """Get ProjectService instance for mission creation from projects."""
        # Use shared repository to ensure projects are accessible
        return ProjectService(project_repository=_get_shared_project_repo())

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

    @app.post(
        "/projects",
        status_code=status.HTTP_201_CREATED,
        response_model=ProjectResponse,
        summary="Create a new mission project",
        response_description="The created project template.",
        tags=["Projects"],
    )
    def create_project(
        payload: ProjectCreateRequest,
        current_user: User = Depends(get_current_user),
        project_service: ProjectService = Depends(get_project_service),
    ) -> ProjectResponse:
        """
        Create a new mission project template.

        Projects are user-created mission configurations that can be saved
        and later used to generate missions. This endpoint allows authenticated
        users to create custom mission templates with objectives, constraints,
        and configuration parameters.

        **Authentication Required**: This endpoint requires a valid JWT token
        in the Authorization header.

        **Request Body**:
        - `name`: Project name/title (required, 1-100 characters)
        - `description`: Project description (required, 1-1000 characters)
        - `mission_type`: Type of mission - "tutorial", "free_flight", or "challenge" (required)
        - `difficulty`: Difficulty level - "beginner", "intermediate", or "advanced" (required)
        - `target_body_id`: Optional target celestial body ID
        - `start_position`: Initial position (x, y, z) in meters (default: (0, 0, 0))
        - `max_fuel`: Maximum fuel capacity in liters (default: 1000.0)
        - `time_limit`: Optional time limit in seconds
        - `allowed_ship_types`: List of permitted ship type identifiers
        - `failure_conditions`: List of failure condition descriptions
        - `objectives`: List of objective templates
        - `is_public`: Whether project is publicly shareable (default: false)

        **Response**:
        Returns the created project with a unique project ID and timestamps.

        **Error Codes**:
        - `VALIDATION_INVALID_FORMAT`: Invalid request data
        - `VALIDATION_MISSION_TYPE_INVALID`: Invalid mission type
        - `VALIDATION_DIFFICULTY_INVALID`: Invalid difficulty level
        - `AUTH_INVALID_TOKEN`: Missing or invalid authentication token

        **Example Request**:
        ```json
        {
          "name": "Mars Exploration Mission",
          "description": "A challenging mission to reach Mars orbit",
          "mission_type": "challenge",
          "difficulty": "intermediate",
          "target_body_id": "mars",
          "max_fuel": 1500.0,
          "time_limit": 3600.0,
          "objectives": [
            {
              "description": "Reach Mars orbit",
              "type": "reach",
              "target_id": "mars"
            }
          ],
          "is_public": false
        }
        ```
        """
        try:
            # Create project using service
            project = project_service.create_project(
                user_id=current_user.id,
                name=payload.name,
                description=payload.description,
                mission_type=payload.mission_type,
                difficulty=payload.difficulty,
                target_body_id=payload.target_body_id,
                start_position=payload.start_position,
                max_fuel=payload.max_fuel,
                time_limit=payload.time_limit,
                allowed_ship_types=payload.allowed_ship_types,
                failure_conditions=payload.failure_conditions,
                is_public=payload.is_public,
            )

            # Add objectives from request
            for obj_template in payload.objectives:
                project.add_objective_template(
                    description=obj_template.description,
                    obj_type=obj_template.type,
                    target_id=obj_template.target_id,
                    position=obj_template.position,
                )

            # Save project with objectives
            project_service.update_project(project)

            logger.info("Created project %s for user %s", project.id, current_user.id)
            return ProjectResponse.from_project(project)

        except ValueError as exc:
            error_message = str(exc)
            error_code = ErrorCode.VALIDATION_INVALID_FORMAT
            details = None

            # Map specific validation errors to error codes
            if "mission type" in error_message.lower():
                error_code = ErrorCode.VALIDATION_MISSION_TYPE_INVALID
                details = {"field": "mission_type", "value": payload.mission_type}
            elif "difficulty" in error_message.lower():
                error_code = ErrorCode.VALIDATION_DIFFICULTY_INVALID
                details = {"field": "difficulty", "value": payload.difficulty}
            elif "name" in error_message.lower() and "empty" in error_message.lower():
                error_code = ErrorCode.VALIDATION_INVALID_FORMAT
                details = {"field": "name", "message": error_message}

            raise APIError(
                code=error_code,
                message=error_message,
                status_code=status.HTTP_400_BAD_REQUEST,
                details=details,
            ) from exc

    @app.post(
        "/missions",
        status_code=status.HTTP_201_CREATED,
        response_model=MissionResponse,
        summary="Create a new mission",
        response_description="The created mission instance.",
        tags=["Missions"],
    )
    def create_mission(
        payload: MissionCreateRequest,
        current_user: User = Depends(get_current_user),
        mission_service: MissionService = Depends(get_mission_service),
        project_service: ProjectService = Depends(get_project_service_for_mission),
    ) -> MissionResponse:
        """
        Create a new mission instance.

        Missions are executable mission instances that can be created from scratch
        or from a project template. This endpoint allows authenticated users to
        create missions with objectives, constraints, and configuration parameters.

        **Authentication Required**: This endpoint requires a valid JWT token
        in the Authorization header.

        **Creating from Project Template**:
        If `project_id` is provided, the mission will be created from the project
        template. All other fields (except `name` which can be overridden) will
        be inherited from the project. The `objectives` field will be ignored
        when using a project template.

        **Creating from Scratch**:
        If `project_id` is not provided, the mission will be created with the
        provided fields. All fields are optional except `name`, `description`,
        `mission_type`, and `difficulty`.

        **Request Body**:
        - `name`: Mission name/title (required, 1-100 characters)
        - `description`: Mission description (required, 1-1000 characters)
        - `mission_type`: Type of mission - "tutorial", "free_flight", or "challenge" (required)
        - `difficulty`: Difficulty level - "beginner", "intermediate", or "advanced" (required)
        - `project_id`: Optional project template ID to create mission from
        - `target_body_id`: Optional target celestial body ID
        - `start_position`: Initial position (x, y, z) in meters (default: (0, 0, 0))
        - `max_fuel`: Maximum fuel capacity in liters (default: 1000.0)
        - `time_limit`: Optional time limit in seconds
        - `allowed_ship_types`: List of permitted ship type identifiers
        - `failure_conditions`: List of failure condition descriptions
        - `objectives`: List of mission objectives (ignored if project_id provided)

        **Response**:
        Returns the created mission with a unique mission ID and initial status.

        **Error Codes**:
        - `VALIDATION_INVALID_FORMAT`: Invalid request data
        - `VALIDATION_MISSION_TYPE_INVALID`: Invalid mission type
        - `VALIDATION_DIFFICULTY_INVALID`: Invalid difficulty level
        - `RESOURCE_NOT_FOUND`: Project template not found (if project_id provided)
        - `AUTH_INVALID_TOKEN`: Missing or invalid authentication token

        **Example Request (from scratch)**:
        ```json
        {
          "name": "Mars Landing Mission",
          "description": "Land safely on Mars surface",
          "mission_type": "challenge",
          "difficulty": "intermediate",
          "target_body_id": "mars",
          "max_fuel": 1500.0,
          "objectives": [
            {
              "description": "Reach Mars orbit",
              "type": "reach",
              "target_id": "mars"
            }
          ]
        }
        ```

        **Example Request (from project)**:
        ```json
        {
          "name": "My Mars Mission",
          "description": "Custom mission",
          "mission_type": "challenge",
          "difficulty": "intermediate",
          "project_id": "project-abc123"
        }
        ```
        """
        try:
            # Check if creating from project template
            if payload.project_id:
                project = project_service.get_project(payload.project_id)
                if not project:
                    raise APIError(
                        code=ErrorCode.RESOURCE_NOT_FOUND,
                        message=f"Project template '{payload.project_id}' not found",
                        status_code=status.HTTP_404_NOT_FOUND,
                        details={"field": "project_id", "value": payload.project_id},
                    )

                # Create mission from project template
                mission = mission_service.create_mission_from_project(
                    project=project,
                    name_override=payload.name,
                )
            else:
                # Create mission from scratch
                import uuid

                # Convert objective requests to Objective objects
                objectives = []
                for idx, obj_req in enumerate(payload.objectives):
                    obj_id = f"obj-{uuid.uuid4().hex[:8]}"
                    objective = Objective(
                        id=obj_id,
                        description=obj_req.description,
                        type=obj_req.type,
                        target_id=obj_req.target_id,
                        position=obj_req.position,
                        completed=False,
                    )
                    objectives.append(objective)

                mission = mission_service.create_mission(
                    name=payload.name,
                    mission_type=payload.mission_type,
                    difficulty=payload.difficulty,
                    description=payload.description,
                    target_body_id=payload.target_body_id,
                    start_position=payload.start_position,
                    max_fuel=payload.max_fuel,
                    time_limit=payload.time_limit,
                    allowed_ship_types=payload.allowed_ship_types,
                    failure_conditions=payload.failure_conditions,
                    objectives=objectives,
                )

            logger.info("Created mission %s for user %s", mission.id, current_user.id)
            return MissionResponse.from_mission(mission)

        except ValueError as exc:
            # Use helper function for cleaner error mapping
            raise create_validation_api_error(
                exc,
                field_name=(
                    "mission_type"
                    if "mission type" in str(exc).lower()
                    else "difficulty"
                    if "difficulty" in str(exc).lower()
                    else "name"
                ),
                field_value=(
                    payload.mission_type
                    if "mission type" in str(exc).lower()
                    else (
                        payload.difficulty
                        if "difficulty" in str(exc).lower()
                        else payload.name
                    )
                ),
            ) from exc

    return app


app = create_app()
