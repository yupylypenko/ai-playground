"""
MongoDB Storage Adapters

MongoDB implementations of storage repositories for the Cosmic Flight Simulator.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from src.cockpit.config import MongoConfig
from src.models import AuthProfile, Mission, Objective, User

logger = logging.getLogger(__name__)


class MongoUserRepository:
    """
    MongoDB implementation of UserRepository.

    Handles persistence of User models to MongoDB.
    """

    def __init__(self, db: Database) -> None:
        """
        Initialize MongoDB user repository.

        Args:
            db: MongoDB database instance
        """
        self.collection: Collection = db.users

    def save_user(self, user: User) -> None:
        """Save or update a user profile."""
        doc = self._user_to_doc(user)
        self.collection.replace_one({"_id": user.id}, doc, upsert=True)
        logger.debug(f"Saved user: {user.id}")

    def get_user(self, user_id: str) -> Optional[User]:
        """Retrieve a user by ID."""
        doc = self.collection.find_one({"_id": user_id})
        if doc:
            return self._doc_to_user(doc)
        return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by username."""
        doc = self.collection.find_one({"username": username})
        if doc:
            return self._doc_to_user(doc)
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email."""
        doc = self.collection.find_one({"email": email})
        if doc:
            return self._doc_to_user(doc)
        return None

    def list_users(self) -> List[User]:
        """List all users."""
        docs = self.collection.find()
        return [self._doc_to_user(doc) for doc in docs]

    def delete_user(self, user_id: str) -> None:
        """Delete a user by ID."""
        self.collection.delete_one({"_id": user_id})
        logger.debug(f"Deleted user: {user_id}")

    @staticmethod
    def _user_to_doc(user: User) -> dict:
        """Convert User model to MongoDB document."""
        return {
            "_id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "screen_width": user.screen_width,
            "screen_height": user.screen_height,
            "fullscreen": user.fullscreen,
            "font_scale": user.font_scale,
            "high_contrast": user.high_contrast,
            "enable_sounds": user.enable_sounds,
            "master_volume": user.master_volume,
            "music_volume": user.music_volume,
            "sfx_volume": user.sfx_volume,
            "total_flight_time": user.total_flight_time,
            "missions_completed": user.missions_completed,
            "missions_attempted": user.missions_attempted,
            "distance_traveled": user.distance_traveled,
            "fuel_consumed": user.fuel_consumed,
            "ship_types_used": user.ship_types_used,
            "unlocked_ships": user.unlocked_ships,
            "completed_missions": user.completed_missions,
            "best_times": user.best_times,
            "achievements": user.achievements,
            "created_at": (
                user.created_at.isoformat()
                if isinstance(user.created_at, datetime)
                else user.created_at
            ),
            "last_login": (
                user.last_login.isoformat()
                if isinstance(user.last_login, datetime)
                else user.last_login
            ),
        }

    @staticmethod
    def _doc_to_user(doc: dict) -> User:
        """Convert MongoDB document to User model."""
        created_at = doc.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()

        last_login = doc.get("last_login")
        if isinstance(last_login, str):
            last_login = datetime.fromisoformat(last_login)
        elif last_login is None:
            last_login = None

        return User(
            id=doc["_id"],
            username=doc["username"],
            email=doc["email"],
            display_name=doc["display_name"],
            screen_width=doc.get("screen_width", 1280),
            screen_height=doc.get("screen_height", 720),
            fullscreen=doc.get("fullscreen", False),
            font_scale=doc.get("font_scale", 1.0),
            high_contrast=doc.get("high_contrast", False),
            enable_sounds=doc.get("enable_sounds", True),
            master_volume=doc.get("master_volume", 0.8),
            music_volume=doc.get("music_volume", 0.6),
            sfx_volume=doc.get("sfx_volume", 0.8),
            total_flight_time=doc.get("total_flight_time", 0.0),
            missions_completed=doc.get("missions_completed", 0),
            missions_attempted=doc.get("missions_attempted", 0),
            distance_traveled=doc.get("distance_traveled", 0.0),
            fuel_consumed=doc.get("fuel_consumed", 0.0),
            ship_types_used=doc.get("ship_types_used", []),
            unlocked_ships=doc.get("unlocked_ships", []),
            completed_missions=doc.get("completed_missions", []),
            best_times=doc.get("best_times", {}),
            achievements=doc.get("achievements", []),
            created_at=created_at,
            last_login=last_login,
        )


class MongoAuthRepository:
    """
    MongoDB implementation of AuthRepository.
    """

    def __init__(self, db: Database) -> None:
        self.collection: Collection = db.auth_profiles

    def save_profile(self, profile: AuthProfile) -> None:
        doc = self._profile_to_doc(profile)
        self.collection.replace_one({"_id": profile.id}, doc, upsert=True)
        logger.debug("Saved auth profile for user %s", profile.user_id)

    def get_by_username(self, username: str) -> Optional[AuthProfile]:
        doc = self.collection.find_one({"username": username})
        if doc:
            return self._doc_to_profile(doc)
        return None

    def get_by_email(self, email: str) -> Optional[AuthProfile]:
        doc = self.collection.find_one({"email": email})
        if doc:
            return self._doc_to_profile(doc)
        return None

    def get_by_user_id(self, user_id: str) -> Optional[AuthProfile]:
        doc = self.collection.find_one({"user_id": user_id})
        if doc:
            return self._doc_to_profile(doc)
        return None

    @staticmethod
    def _profile_to_doc(profile: AuthProfile) -> dict:
        return {
            "_id": profile.id,
            "user_id": profile.user_id,
            "username": profile.username,
            "email": profile.email,
            "password_hash": profile.password_hash,
            "password_salt": profile.password_salt,
            "created_at": profile.created_at.isoformat(),
        }

    @staticmethod
    def _doc_to_profile(doc: dict) -> AuthProfile:
        created_at = doc.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return AuthProfile(
            id=doc["_id"],
            user_id=doc["user_id"],
            username=doc["username"],
            email=doc["email"],
            password_hash=doc["password_hash"],
            password_salt=doc["password_salt"],
            created_at=created_at or datetime.now(),
        )


class MongoMissionRepository:
    """
    MongoDB implementation of MissionRepository.

    Handles persistence of Mission models to MongoDB.
    """

    def __init__(self, db: Database) -> None:
        """
        Initialize MongoDB mission repository.

        Args:
            db: MongoDB database instance
        """
        self.collection: Collection = db.missions

    def save_mission(self, mission: Mission) -> None:
        """Save or update a mission."""
        doc = self._mission_to_doc(mission)
        self.collection.replace_one({"_id": mission.id}, doc, upsert=True)
        logger.debug(f"Saved mission: {mission.id}")

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """Retrieve a mission by ID."""
        doc = self.collection.find_one({"_id": mission_id})
        if doc:
            return self._doc_to_mission(doc)
        return None

    def list_missions(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        mission_type: Optional[str] = None,
    ) -> List[Mission]:
        """List missions with optional filtering."""
        query: dict = {}
        if user_id:
            query["user_id"] = user_id
        if status:
            query["status"] = status
        if mission_type:
            query["type"] = mission_type

        docs = self.collection.find(query)
        return [self._doc_to_mission(doc) for doc in docs]

    def delete_mission(self, mission_id: str) -> None:
        """Delete a mission by ID."""
        self.collection.delete_one({"_id": mission_id})
        logger.debug(f"Deleted mission: {mission_id}")

    @staticmethod
    def _mission_to_doc(mission: Mission) -> dict:
        """Convert Mission model to MongoDB document."""
        objectives = [
            {
                "id": obj.id,
                "description": obj.description,
                "type": obj.type,
                "target_id": obj.target_id,
                "position": list(obj.position) if obj.position else None,
                "completed": obj.completed,
            }
            for obj in mission.objectives
        ]

        return {
            "_id": mission.id,
            "name": mission.name,
            "type": mission.type,
            "difficulty": mission.difficulty,
            "description": mission.description,
            "objectives": objectives,
            "current_objective_index": mission.current_objective_index,
            "completion_criteria": mission.completion_criteria,
            "start_position": list(mission.start_position),
            "target_body_id": mission.target_body_id,
            "max_fuel": mission.max_fuel,
            "time_limit": mission.time_limit,
            "allowed_ship_types": mission.allowed_ship_types,
            "failure_conditions": mission.failure_conditions,
            "start_time": mission.start_time,
            "elapsed_time": mission.elapsed_time,
            "distance_traveled": mission.distance_traveled,
            "fuel_consumed": mission.fuel_consumed,
            "objectives_completed": mission.objectives_completed,
            "status": mission.status,
            "estimated_time": mission.estimated_time,
        }

    @staticmethod
    def _doc_to_mission(doc: dict) -> Mission:
        """Convert MongoDB document to Mission model."""
        objectives = [
            Objective(
                id=obj_doc["id"],
                description=obj_doc["description"],
                type=obj_doc["type"],
                target_id=obj_doc.get("target_id"),
                position=(
                    tuple(obj_doc["position"]) if obj_doc.get("position") else None
                ),
                completed=obj_doc.get("completed", False),
            )
            for obj_doc in doc.get("objectives", [])
        ]

        start_position = doc.get("start_position", [0.0, 0.0, 0.0])
        if isinstance(start_position, list):
            start_position = tuple(start_position)

        return Mission(
            id=doc["_id"],
            name=doc["name"],
            type=doc["type"],
            difficulty=doc["difficulty"],
            description=doc["description"],
            objectives=objectives,
            current_objective_index=doc.get("current_objective_index", 0),
            completion_criteria=doc.get("completion_criteria", {}),
            start_position=start_position,
            target_body_id=doc.get("target_body_id"),
            max_fuel=doc.get("max_fuel", 1000.0),
            time_limit=doc.get("time_limit"),
            allowed_ship_types=doc.get("allowed_ship_types", []),
            failure_conditions=doc.get("failure_conditions", []),
            start_time=doc.get("start_time"),
            elapsed_time=doc.get("elapsed_time", 0.0),
            distance_traveled=doc.get("distance_traveled", 0.0),
            fuel_consumed=doc.get("fuel_consumed", 0.0),
            objectives_completed=doc.get("objectives_completed", 0),
            status=doc.get("status", "not_started"),
            estimated_time=doc.get("estimated_time", 3600.0),
        )


class MongoObjectiveRepository:
    """
    MongoDB implementation of ObjectiveRepository.

    Handles persistence of Objective models to MongoDB.
    Note: Objectives are stored as nested documents within missions.
    """

    def __init__(self, db: Database) -> None:
        """
        Initialize MongoDB objective repository.

        Args:
            db: MongoDB database instance
        """
        self.mission_collection: Collection = db.missions

    def save_objective(self, objective: Objective, mission_id: str) -> None:
        """Save or update an objective within a mission."""
        mission_doc = self.mission_collection.find_one({"_id": mission_id})
        if not mission_doc:
            raise ValueError(f"Mission {mission_id} not found")

        objectives = mission_doc.get("objectives", [])
        obj_index = next(
            (i for i, obj in enumerate(objectives) if obj["id"] == objective.id),
            None,
        )

        obj_doc = {
            "id": objective.id,
            "description": objective.description,
            "type": objective.type,
            "target_id": objective.target_id,
            "position": list(objective.position) if objective.position else None,
            "completed": objective.completed,
        }

        if obj_index is not None:
            objectives[obj_index] = obj_doc
        else:
            objectives.append(obj_doc)

        self.mission_collection.update_one(
            {"_id": mission_id}, {"$set": {"objectives": objectives}}
        )
        logger.debug(f"Saved objective: {objective.id} in mission: {mission_id}")

    def get_objective(self, objective_id: str, mission_id: str) -> Optional[Objective]:
        """Retrieve an objective by ID within a mission."""
        mission_doc = self.mission_collection.find_one({"_id": mission_id})
        if not mission_doc:
            return None

        objectives = mission_doc.get("objectives", [])
        obj_doc = next((obj for obj in objectives if obj["id"] == objective_id), None)
        if obj_doc:
            return Objective(
                id=obj_doc["id"],
                description=obj_doc["description"],
                type=obj_doc["type"],
                target_id=obj_doc.get("target_id"),
                position=(
                    tuple(obj_doc["position"]) if obj_doc.get("position") else None
                ),
                completed=obj_doc.get("completed", False),
            )
        return None

    def list_objectives(self, mission_id: str) -> List[Objective]:
        """List all objectives for a mission."""
        mission_doc = self.mission_collection.find_one({"_id": mission_id})
        if not mission_doc:
            return []

        objectives = mission_doc.get("objectives", [])
        return [
            Objective(
                id=obj_doc["id"],
                description=obj_doc["description"],
                type=obj_doc["type"],
                target_id=obj_doc.get("target_id"),
                position=(
                    tuple(obj_doc["position"]) if obj_doc.get("position") else None
                ),
                completed=obj_doc.get("completed", False),
            )
            for obj_doc in objectives
        ]

    def delete_objective(self, objective_id: str, mission_id: str) -> None:
        """Delete an objective by ID."""
        self.mission_collection.update_one(
            {"_id": mission_id},
            {"$pull": {"objectives": {"id": objective_id}}},
        )
        logger.debug(f"Deleted objective: {objective_id} from mission: {mission_id}")


class MongoDatabase:
    """
    MongoDB database connection manager.

    Provides access to repositories and manages database connections.
    """

    def __init__(self, config: MongoConfig) -> None:
        """
        Initialize MongoDB database connection.

        Args:
            config: MongoDB configuration
        """
        self.config = config
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self._user_repo: Optional[MongoUserRepository] = None
        self._mission_repo: Optional[MongoMissionRepository] = None
        self._objective_repo: Optional[MongoObjectiveRepository] = None
        self._auth_repo: Optional[MongoAuthRepository] = None

    def connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            connection_string = self.config.get_connection_string()
            self.client = MongoClient(connection_string)
            self.db = self.client[self.config.database]
            # Test connection
            self.client.server_info()
            logger.info(f"Connected to MongoDB: {self.config.database}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    @property
    def user_repository(self) -> MongoUserRepository:
        """Get user repository instance."""
        if not self._user_repo and self.db:
            self._user_repo = MongoUserRepository(self.db)
        if not self._user_repo:
            raise RuntimeError("Database not connected")
        return self._user_repo

    @property
    def mission_repository(self) -> MongoMissionRepository:
        """Get mission repository instance."""
        if not self._mission_repo and self.db:
            self._mission_repo = MongoMissionRepository(self.db)
        if not self._mission_repo:
            raise RuntimeError("Database not connected")
        return self._mission_repo

    @property
    def objective_repository(self) -> MongoObjectiveRepository:
        """Get objective repository instance."""
        if not self._objective_repo and self.db:
            self._objective_repo = MongoObjectiveRepository(self.db)
        if not self._objective_repo:
            raise RuntimeError("Database not connected")
        return self._objective_repo

    @property
    def auth_repository(self) -> MongoAuthRepository:
        """Get auth repository instance."""
        if not self._auth_repo and self.db:
            self._auth_repo = MongoAuthRepository(self.db)
        if not self._auth_repo:
            raise RuntimeError("Database not connected")
        return self._auth_repo

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
