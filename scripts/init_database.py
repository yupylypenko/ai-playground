"""
Database Initialization Script

Creates indexes and initializes MongoDB collections for the Cosmic Flight Simulator.
"""

from __future__ import annotations

import logging
import sys

from src.adapters.mongodb import MongoDatabase
from src.cockpit.config import MongoConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_database(config: MongoConfig) -> None:
    """
    Initialize MongoDB database with indexes.

    Args:
        config: MongoDB configuration
    """
    try:
        with MongoDatabase(config) as db:
            logger.info("Initializing database collections and indexes...")

            # Create indexes for users collection
            db.db.users.create_index("username", unique=True)
            db.db.users.create_index("email", unique=True)
            logger.info("Created indexes for users collection")

            # Create indexes for missions collection
            db.db.missions.create_index("status")
            db.db.missions.create_index("type")
            db.db.missions.create_index([("user_id", 1), ("status", 1)])
            logger.info("Created indexes for missions collection")

            logger.info("Database initialization completed successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def main() -> int:
    """Main entry point."""
    config = MongoConfig.from_env()
    try:
        initialize_database(config)
        return 0
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

