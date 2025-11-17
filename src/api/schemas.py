"""
Pydantic schemas for the public API surface.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.cockpit.auth import RegistrationResult


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
