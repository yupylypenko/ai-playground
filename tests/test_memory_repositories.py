"""
Tests for in-memory repository implementations.
"""

from __future__ import annotations

from src.cockpit.memory import InMemoryAuthRepository, InMemoryUserRepository
from src.models import AuthProfile, User


class TestInMemoryUserRepository:
    """Tests for InMemoryUserRepository."""

    def test_list_users(self) -> None:
        """Test listing all users."""
        repo = InMemoryUserRepository()

        user1 = User(
            id="user-1",
            username="user1",
            email="user1@example.com",
            display_name="User 1",
        )
        user2 = User(
            id="user-2",
            username="user2",
            email="user2@example.com",
            display_name="User 2",
        )

        repo.save_user(user1)
        repo.save_user(user2)

        users = repo.list_users()
        assert len(users) == 2
        user_ids = {u.id for u in users}
        assert "user-1" in user_ids
        assert "user-2" in user_ids

    def test_delete_user_existing(self) -> None:
        """Test deleting an existing user."""
        repo = InMemoryUserRepository()

        user = User(
            id="user-1",
            username="user1",
            email="user1@example.com",
            display_name="User 1",
        )
        repo.save_user(user)

        assert repo.get_user("user-1") is not None

        repo.delete_user("user-1")

        assert repo.get_user("user-1") is None

    def test_delete_user_nonexistent(self) -> None:
        """Test deleting a non-existent user doesn't raise error."""
        repo = InMemoryUserRepository()

        # Should not raise
        repo.delete_user("nonexistent-id")

        assert repo.get_user("nonexistent-id") is None


class TestInMemoryAuthRepository:
    """Tests for InMemoryAuthRepository."""

    def test_get_by_user_id(self) -> None:
        """Test getting auth profile by user ID."""
        repo = InMemoryAuthRepository()

        profile = AuthProfile(
            id="auth-1",
            user_id="user-1",
            username="testuser",
            email="test@example.com",
            password_hash="hash123",
            password_salt="salt123",
        )

        repo.save_profile(profile)

        retrieved = repo.get_by_user_id("user-1")
        assert retrieved is not None
        assert retrieved.id == "auth-1"
        assert retrieved.user_id == "user-1"

    def test_get_by_user_id_nonexistent(self) -> None:
        """Test getting auth profile by non-existent user ID."""
        repo = InMemoryAuthRepository()

        result = repo.get_by_user_id("nonexistent-user-id")
        assert result is None

    def test_get_by_username_nonexistent(self) -> None:
        """Test getting auth profile by non-existent username."""
        repo = InMemoryAuthRepository()

        result = repo.get_by_username("nonexistent")
        assert result is None

    def test_get_by_email_nonexistent(self) -> None:
        """Test getting auth profile by non-existent email."""
        repo = InMemoryAuthRepository()

        result = repo.get_by_email("nonexistent@example.com")
        assert result is None
