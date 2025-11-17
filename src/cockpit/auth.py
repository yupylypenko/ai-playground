"""
Authentication Services

Provides registration flows and credential management that coordinate
application services with storage ports.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from dataclasses import dataclass

from src.cockpit.services import UserService
from src.cockpit.storage import AuthRepository
from src.models import AuthProfile, User


class RegistrationError(ValueError):
    """Raised when registration input fails validation."""


@dataclass
class RegistrationResult:
    """
    Value object returned after registration.

    Attributes:
        user: Newly created user profile
        auth_profile: Persisted authentication metadata
    """

    user: User
    auth_profile: AuthProfile


class AuthService:
    """
    Coordinates user registration with credential persistence.
    """

    MIN_PASSWORD_LENGTH = 8

    def __init__(
        self,
        user_service: UserService,
        auth_repository: AuthRepository,
    ) -> None:
        self.user_service = user_service
        self.auth_repository = auth_repository

    def register_user(
        self, username: str, email: str, password: str, display_name: str
    ) -> RegistrationResult:
        """
        Register a brand-new user with validated credentials.

        Args:
            username: Desired username
            email: Email address
            password: Plain-text password to hash
            display_name: Display name

        Returns:
            RegistrationResult containing persisted user and auth profile
        """
        normalized_username = username.strip()
        normalized_email = email.strip().lower()
        display_name = display_name.strip()

        if not normalized_username:
            raise RegistrationError("Username must not be empty")
        if not display_name:
            raise RegistrationError("Display name must not be empty")

        self._validate_password(password)

        if self.auth_repository.get_by_username(normalized_username):
            raise RegistrationError("Username already registered")
        if self.auth_repository.get_by_email(normalized_email):
            raise RegistrationError("Email already registered")

        user = self.user_service.create_user(
            username=normalized_username,
            email=normalized_email,
            display_name=display_name,
        )

        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)

        auth_profile = AuthProfile(
            id=f"auth-{uuid.uuid4().hex[:8]}",
            user_id=user.id,
            username=normalized_username,
            email=normalized_email,
            password_hash=password_hash,
            password_salt=salt,
        )
        self.auth_repository.save_profile(auth_profile)

        return RegistrationResult(user=user, auth_profile=auth_profile)

    @classmethod
    def _hash_password(cls, password: str, salt_hex: str) -> str:
        """Hash password with PBKDF2."""
        salt_bytes = bytes.fromhex(salt_hex)
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt_bytes,
            390000,
        )
        return derived.hex()

    def verify_password(self, password: str, profile: AuthProfile) -> bool:
        """
        Verify provided password against stored profile.

        Args:
            password: Plain-text password
            profile: Stored auth profile
        """
        hashed = self._hash_password(password, profile.password_salt)
        return hmac.compare_digest(hashed, profile.password_hash)

    def _validate_password(self, password: str) -> None:
        """Ensure password meets policy requirements."""
        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise RegistrationError("Password must be at least 8 characters long")
        if password.lower() == password or password.upper() == password:
            raise RegistrationError("Password must contain mixed case characters")
        if not any(char.isdigit() for char in password):
            raise RegistrationError("Password must contain at least one digit")

    # Authentication
    def authenticate(self, username: str, password: str) -> User | None:
        """
        Authenticate by username and password.

        Returns:
            The associated User if credentials are valid; otherwise None.
        """
        profile = self.auth_repository.get_by_username(username.strip())
        if not profile:
            return None
        if not self.verify_password(password, profile):
            return None
        user = self.user_service.get_user(profile.user_id)
        return user
