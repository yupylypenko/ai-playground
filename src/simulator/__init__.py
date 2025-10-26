"""
Simulator Package

Core physics engine and spacecraft simulation.
"""

from .physics import PhysicsEngine, Vector3D
from .spacecraft import Spacecraft
from .solar_system import SolarSystem, CelestialBody

__all__ = ['PhysicsEngine', 'Vector3D', 'Spacecraft', 'SolarSystem', 'CelestialBody']
