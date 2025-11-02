"""
Simulator Package

Core physics engine and spacecraft simulation.
"""

from .physics import PhysicsEngine
from .spacecraft import Spacecraft
from .solar_system import SolarSystem, CelestialBody
from .types import Quaternion, Vector3D

__all__ = ['PhysicsEngine', 'Vector3D', 'Spacecraft', 'SolarSystem', 'CelestialBody', 'Quaternion']

