"""
Tests for configuration modules.
"""

from __future__ import annotations

import pytest

from src.cockpit.config import MongoConfig


class TestMongoConfig:
    """Tests for MongoConfig."""

    def test_from_env_with_uri(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test creating config from environment with MONGODB_URI."""
        monkeypatch.setenv("MONGODB_URI", "mongodb://example.com:27017/mydb")
        config = MongoConfig.from_env()
        assert config.connection_string == "mongodb://example.com:27017/mydb"

    def test_from_env_with_credentials(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test creating config from environment with username/password."""
        monkeypatch.delenv("MONGODB_URI", raising=False)
        monkeypatch.setenv("MONGODB_HOST", "example.com")
        monkeypatch.setenv("MONGODB_PORT", "27018")
        monkeypatch.setenv("MONGODB_DATABASE", "testdb")
        monkeypatch.setenv("MONGODB_USERNAME", "testuser")
        monkeypatch.setenv("MONGODB_PASSWORD", "testpass")

        config = MongoConfig.from_env()
        assert config.host == "example.com"
        assert config.port == 27018
        assert config.database == "testdb"
        assert config.username == "testuser"
        assert config.password == "testpass"

    def test_get_connection_string_with_uri(self) -> None:
        """Test getting connection string when URI is set."""
        config = MongoConfig(connection_string="mongodb://example.com/mydb")
        assert config.get_connection_string() == "mongodb://example.com/mydb"

    def test_get_connection_string_with_credentials(self) -> None:
        """Test getting connection string with username/password."""
        config = MongoConfig(
            host="example.com",
            port=27017,
            database="mydb",
            username="user",
            password="pass",
        )
        conn_str = config.get_connection_string()
        assert "mongodb://user:pass@example.com:27017/mydb" == conn_str

    def test_get_connection_string_default(self) -> None:
        """Test getting default connection string."""
        config = MongoConfig()
        assert (
            config.get_connection_string()
            == "mongodb://localhost:27017/cosmic_flight_sim"
        )
