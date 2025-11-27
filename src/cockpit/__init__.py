"""
Cockpit Control System

Interactive cockpit with HUD, controls, and instruments.
"""

from .auth import AuthService, RegistrationResult

# Storage ports and configuration
from .config import MongoConfig
from .protection import AsteroidProtectionSystem, ProtectionMode, ProtectionStatus
from .services import MissionService, UserService
from .storage import (
    AuthRepository,
    MissionRepository,
    ObjectiveRepository,
    UserRepository,
)

__all__ = [
    "MongoConfig",
    "AuthRepository",
    "UserRepository",
    "MissionRepository",
    "ObjectiveRepository",
    "UserService",
    "MissionService",
    "AuthService",
    "RegistrationResult",
    "AsteroidProtectionSystem",
    "ProtectionMode",
    "ProtectionStatus",
]
