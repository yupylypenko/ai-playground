"""
Tests for authentication edge cases and error conditions.
"""

from __future__ import annotations

import pytest

from src.cockpit.auth import AuthService, RegistrationError
from src.cockpit.memory import InMemoryAuthRepository, InMemoryUserRepository
from src.cockpit.services import UserService


class TestAuthServiceEdgeCases:
    """Tests for AuthService edge cases."""

    @pytest.fixture
    def auth_service(self) -> AuthService:
        """Create an AuthService instance for testing."""
        user_repo = InMemoryUserRepository()
        auth_repo = InMemoryAuthRepository()
        user_service = UserService(user_repo)
        return AuthService(user_service=user_service, auth_repository=auth_repo)

    def test_register_empty_username(self, auth_service: AuthService) -> None:
        """Test registration with empty username raises error."""
        with pytest.raises(RegistrationError, match="Username must not be empty"):
            auth_service.register_user(
                username="   ",
                email="test@example.com",
                password="TestPass123",
                display_name="Test",
            )

    def test_register_empty_display_name(self, auth_service: AuthService) -> None:
        """Test registration with empty display name raises error."""
        with pytest.raises(RegistrationError, match="Display name must not be empty"):
            auth_service.register_user(
                username="testuser",
                email="test@example.com",
                password="TestPass123",
                display_name="   ",
            )

    def test_register_password_too_short(self, auth_service: AuthService) -> None:
        """Test registration with password too short raises error."""
        with pytest.raises(
            RegistrationError, match="Password must be at least 8 characters long"
        ):
            auth_service.register_user(
                username="testuser",
                email="test@example.com",
                password="Short1",
                display_name="Test",
            )

    def test_register_password_all_lowercase(self, auth_service: AuthService) -> None:
        """Test registration with all lowercase password raises error."""
        with pytest.raises(
            RegistrationError, match="Password must contain mixed case characters"
        ):
            auth_service.register_user(
                username="testuser",
                email="test@example.com",
                password="lowercase123",
                display_name="Test",
            )

    def test_register_password_all_uppercase(self, auth_service: AuthService) -> None:
        """Test registration with all uppercase password raises error."""
        with pytest.raises(
            RegistrationError, match="Password must contain mixed case characters"
        ):
            auth_service.register_user(
                username="testuser",
                email="test@example.com",
                password="UPPERCASE123",
                display_name="Test",
            )

    def test_register_password_no_digit(self, auth_service: AuthService) -> None:
        """Test registration with password without digit raises error."""
        with pytest.raises(
            RegistrationError, match="Password must contain at least one digit"
        ):
            auth_service.register_user(
                username="testuser",
                email="test@example.com",
                password="NoDigitPass",
                display_name="Test",
            )

    def test_verify_password_correct(self, auth_service: AuthService) -> None:
        """Test password verification with correct password."""
        result = auth_service.register_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123",
            display_name="Test User",
        )

        assert auth_service.verify_password("TestPass123", result.auth_profile) is True

    def test_verify_password_incorrect(self, auth_service: AuthService) -> None:
        """Test password verification with incorrect password."""
        result = auth_service.register_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123",
            display_name="Test User",
        )

        assert (
            auth_service.verify_password("WrongPassword123", result.auth_profile)
            is False
        )

    def test_register_username_normalization(self, auth_service: AuthService) -> None:
        """Test that username is normalized (trimmed)."""
        result = auth_service.register_user(
            username="  testuser  ",
            email="test@example.com",
            password="TestPass123",
            display_name="Test User",
        )

        assert result.user.username == "testuser"
        assert result.auth_profile.username == "testuser"

    def test_register_email_normalization(self, auth_service: AuthService) -> None:
        """Test that email is normalized (lowercased and trimmed)."""
        result = auth_service.register_user(
            username="testuser",
            email="  TEST@EXAMPLE.COM  ",
            password="TestPass123",
            display_name="Test User",
        )

        assert result.user.email == "test@example.com"
        assert result.auth_profile.email == "test@example.com"
