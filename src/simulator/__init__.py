"""
Simulator Package

Core physics engine and spacecraft simulation.
"""

from .asteroid import Asteroid
from .physics import PhysicsEngine
from .solar_system import CelestialBody, SolarSystem
from .spacecraft import Spacecraft
from .types import Quaternion, Vector3D

__all__ = [
    "Asteroid",
    "PhysicsEngine",
    "Vector3D",
    "Spacecraft",
    "SolarSystem",
    "CelestialBody",
    "Quaternion",
]
