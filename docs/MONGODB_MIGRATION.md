"""
MongoDB Migration Guide

This document explains how to migrate from in-memory storage to MongoDB.
"""

# MongoDB Migration Guide

## Overview

The Cosmic Flight Simulator has been migrated from in-memory storage to MongoDB for persistent data storage. This migration enables:

- **Persistent user profiles**: User data persists across sessions
- **Mission tracking**: Mission progress is saved and can be resumed
- **Statistics**: User statistics and achievements are tracked over time
- **Scalability**: Ready for multi-user scenarios

## Architecture

The migration follows the repository pattern with clear separation of concerns:

### Storage Ports (Interfaces)
Located in `src/cockpit/storage.py`:
- `UserRepository` - Protocol for user storage operations
- `MissionRepository` - Protocol for mission storage operations
- `ObjectiveRepository` - Protocol for objective storage operations

### MongoDB Adapters
Located in `src/adapters/mongodb.py`:
- `MongoUserRepository` - MongoDB implementation of UserRepository
- `MongoMissionRepository` - MongoDB implementation of MissionRepository
- `MongoObjectiveRepository` - MongoDB implementation of ObjectiveRepository
- `MongoDatabase` - Database connection manager

### Configuration
Located in `src/cockpit/config.py`:
- `MongoConfig` - MongoDB connection configuration

## Migration Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install `pymongo>=4.0.0`.

### 2. Setup MongoDB

Install and start MongoDB locally (see `.env.example` for details).

### 3. Initialize Database

Run the initialization script to create indexes:

```bash
python scripts/init_database.py
```

### 4. Update Code to Use Repositories

**Before (in-memory)**:
```python
user = User(id="user-001", username="player", ...)
# Data lost when program exits
```

**After (MongoDB)**:
```python
from src.adapters import MongoDatabase
from src.cockpit.config import MongoConfig

config = MongoConfig.from_env()
with MongoDatabase(config) as db:
    user_repo = db.user_repository
    user = User(id="user-001", username="player", ...)
    user_repo.save_user(user)  # Persisted to MongoDB
```

### 5. Service Layer Usage

For higher-level operations, use the service layer:

```python
from src.cockpit.services import UserService, MissionService

with MongoDatabase(config) as db:
    user_service = UserService(db.user_repository)
    mission_service = MissionService(db.mission_repository)

    # Create user
    user = user_service.create_user(
        username="player",
        email="player@example.com",
        display_name="Player"
    )

    # Create mission
    mission = mission_service.create_mission(
        name="Mars Mission",
        mission_type="challenge",
        difficulty="intermediate",
        description="Fly to Mars"
    )
```

## Testing

### Test MongoDB Connection

```bash
python main.py --test-db
```

### Run Unit Tests

```bash
pytest tests/test_mongodb.py
```

Note: Tests will be skipped if MongoDB is not available.

## Configuration

Configuration can be set via environment variables (see `.env.example`) or programmatically:

```python
from src.cockpit.config import MongoConfig

# From environment
config = MongoConfig.from_env()

# Or explicitly
config = MongoConfig(
    host="localhost",
    port=27017,
    database="cosmic_flight_sim"
)
```

## Data Model Changes

The data models (`User`, `Mission`, `Objective`) remain unchanged. The migration only affects how they are stored:

- **User**: Stored in `users` collection
- **Mission**: Stored in `missions` collection
- **Objective**: Stored as nested documents within missions

## Backward Compatibility

The application can still run without MongoDB for testing purposes. Use the `--skip-db` flag or handle connection errors gracefully.

## Next Steps

1. **User Authentication**: Add authentication layer using stored user credentials
2. **Mission Persistence**: Save mission state during gameplay
3. **Multi-user Support**: Support multiple concurrent users
4. **Data Migration**: Migrate existing in-memory data if needed

