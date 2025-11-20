"""
Pydantic schemas for the public API surface.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.cockpit.auth import RegistrationResult
from src.models import Project, User


class RegistrationRequest(BaseModel):
    """Incoming payload for /register."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=32,
        pattern=r"^[a-zA-Z0-9_\-]+$",
        description="Unique username (letters, numbers, underscore, hyphen).",
    )
    email: EmailStr = Field(..., description="Valid email address.")
    password: str = Field(
        ...,
        min_length=8,
        max_length=64,
        description="Password with at least one digit and mixed case letters.",
    )
    display_name: str = Field(..., min_length=1, max_length=64)


class RegistrationResponse(BaseModel):
    """Response contract for successful registration."""

    model_config = ConfigDict(from_attributes=True)

    user_id: str = Field(description="Newly created user identifier.")
    username: str
    email: EmailStr
    display_name: str
    created_at: datetime = Field(description="User creation timestamp.")

    @classmethod
    def from_result(cls, result: RegistrationResult) -> "RegistrationResponse":
        """Create response from a registration result."""
        return cls(
            user_id=result.user.id,
            username=result.user.username,
            email=result.user.email,
            display_name=result.user.display_name,
            created_at=result.user.created_at,
        )


class LoginRequest(BaseModel):
    """Incoming payload for /login."""

    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=8, max_length=64)


class TokenResponse(BaseModel):
    """Access token returned on successful authentication."""

    access_token: str = Field(description="JWT access token.")
    token_type: str = Field(default="bearer", description="Token type (RFC6750).")
    expires_in: int = Field(description="Token lifetime in seconds.")


class UserProfileResponse(BaseModel):
    """Response contract for authenticated user profile."""

    model_config = ConfigDict(from_attributes=True)

    user_id: str = Field(description="User identifier.")
    username: str = Field(description="Username.")
    email: EmailStr = Field(description="Email address.")
    display_name: str = Field(description="Display name.")
    created_at: datetime = Field(description="Account creation timestamp.")
    last_login: datetime | None = Field(
        default=None, description="Last login timestamp."
    )

    @classmethod
    def from_user(cls, user: User) -> "UserProfileResponse":
        """Create response from a User model."""
        return cls(
            user_id=user.id,
            username=user.username,
            email=user.email,
            display_name=user.display_name,
            created_at=user.created_at,
            last_login=user.last_login,
        )


class ObjectiveTemplateRequest(BaseModel):
    """Objective template for project creation."""

    description: str = Field(
        ..., min_length=1, max_length=500, description="Objective description."
    )
    type: str = Field(
        default="reach",
        description="Objective type: reach, collect, maintain, avoid.",
    )
    target_id: str | None = Field(
        default=None, description="Optional target body/ship ID."
    )
    position: tuple[float, float, float] | None = Field(
        default=None, description="Optional target position (x, y, z)."
    )


class ProjectCreateRequest(BaseModel):
    """Request payload for creating a new project."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Project name/title.",
        examples=["Mars Exploration Mission"],
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Project description.",
        examples=["A challenging mission to reach Mars orbit."],
    )
    mission_type: str = Field(
        ...,
        description="Mission type: tutorial, free_flight, challenge.",
        examples=["challenge"],
    )
    difficulty: str = Field(
        ...,
        description="Difficulty level: beginner, intermediate, advanced.",
        examples=["intermediate"],
    )
    target_body_id: str | None = Field(
        default=None,
        description="Optional target celestial body ID.",
        examples=["mars"],
    )
    start_position: tuple[float, float, float] = Field(
        default=(0.0, 0.0, 0.0),
        description="Initial position (x, y, z) in meters.",
        examples=[(0.0, 0.0, 0.0)],
    )
    max_fuel: float = Field(
        default=1000.0,
        ge=0.0,
        description="Maximum fuel capacity in liters.",
        examples=[1500.0],
    )
    time_limit: float | None = Field(
        default=None,
        ge=0.0,
        description="Optional time limit in seconds.",
        examples=[3600.0],
    )
    allowed_ship_types: list[str] = Field(
        default_factory=list,
        description="List of permitted ship type identifiers.",
        examples=[["explorer", "cargo"]],
    )
    failure_conditions: list[str] = Field(
        default_factory=list,
        description="List of failure condition descriptions.",
        examples=["Out of fuel", "Collision detected"],
    )
    objectives: list[ObjectiveTemplateRequest] = Field(
        default_factory=list,
        description="List of objective templates.",
    )
    is_public: bool = Field(
        default=False, description="Whether project is publicly shareable."
    )


class ProjectResponse(BaseModel):
    """Response contract for project data."""

    model_config = ConfigDict(from_attributes=True)

    project_id: str = Field(description="Unique project identifier.")
    user_id: str = Field(description="Owner user identifier.")
    name: str = Field(description="Project name.")
    description: str = Field(description="Project description.")
    mission_type: str = Field(description="Mission type.")
    difficulty: str = Field(description="Difficulty level.")
    target_body_id: str | None = Field(description="Optional target celestial body ID.")
    start_position: tuple[float, float, float] = Field(
        description="Initial position (x, y, z)."
    )
    max_fuel: float = Field(description="Maximum fuel capacity in liters.")
    time_limit: float | None = Field(description="Optional time limit in seconds.")
    allowed_ship_types: list[str] = Field(description="List of permitted ship types.")
    failure_conditions: list[str] = Field(description="List of failure conditions.")
    objectives: list[dict[str, Any]] = Field(description="List of objective templates.")
    is_public: bool = Field(description="Whether project is publicly shareable.")
    created_at: datetime = Field(description="Project creation timestamp.")
    updated_at: datetime = Field(description="Last update timestamp.")

    @classmethod
    def from_project(cls, project: Project) -> "ProjectResponse":
        """Create response from a Project model."""
        return cls(
            project_id=project.id,
            user_id=project.user_id,
            name=project.name,
            description=project.description,
            mission_type=project.mission_type,
            difficulty=project.difficulty,
            target_body_id=project.target_body_id,
            start_position=project.start_position,
            max_fuel=project.max_fuel,
            time_limit=project.time_limit,
            allowed_ship_types=project.allowed_ship_types,
            failure_conditions=project.failure_conditions,
            objectives=project.objectives,
            is_public=project.is_public,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
