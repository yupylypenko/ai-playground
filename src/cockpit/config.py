"""
Database Configuration

MongoDB connection configuration for the Cosmic Flight Simulator.
"""

from __future__ import annotations

import os
from typing import Optional

from dataclasses import dataclass


@dataclass
class MongoConfig:
    """
    MongoDB connection configuration.

    Attributes:
        host: MongoDB host (default: localhost)
        port: MongoDB port (default: 27017)
        database: Database name (default: cosmic_flight_sim)
        username: Optional username for authentication
        password: Optional password for authentication
        connection_string: Optional full connection string (overrides host/port)
    """

    host: str = "localhost"
    port: int = 27017
    database: str = "cosmic_flight_sim"
    username: Optional[str] = None
    password: Optional[str] = None
    connection_string: Optional[str] = None

    @classmethod
    def from_env(cls) -> MongoConfig:
        """
        Create configuration from environment variables.

        Environment variables:
            MONGODB_HOST: MongoDB host (default: localhost)
            MONGODB_PORT: MongoDB port (default: 27017)
            MONGODB_DATABASE: Database name (default: cosmic_flight_sim)
            MONGODB_USERNAME: Optional username
            MONGODB_PASSWORD: Optional password
            MONGODB_URI: Optional full connection URI

        Returns:
            MongoConfig instance
        """
        connection_string = os.getenv("MONGODB_URI")
        if connection_string:
            return cls(connection_string=connection_string)

        return cls(
            host=os.getenv("MONGODB_HOST", "localhost"),
            port=int(os.getenv("MONGODB_PORT", "27017")),
            database=os.getenv("MONGODB_DATABASE", "cosmic_flight_sim"),
            username=os.getenv("MONGODB_USERNAME"),
            password=os.getenv("MONGODB_PASSWORD"),
        )

    def get_connection_string(self) -> str:
        """
        Get MongoDB connection string.

        Returns:
            Connection string for pymongo
        """
        if self.connection_string:
            return self.connection_string

        if self.username and self.password:
            return (
                f"mongodb://{self.username}:{self.password}@"
                f"{self.host}:{self.port}/{self.database}"
            )

        return f"mongodb://{self.host}:{self.port}/{self.database}"

