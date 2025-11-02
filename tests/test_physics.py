"""
Tests for Physics Engine

Unit tests for physics calculations including gravity, acceleration, and vectors.
"""

from __future__ import annotations

from src.simulator import PhysicsEngine, Vector3D
from src.simulator.solar_system import CelestialBody
from src.simulator.spacecraft import Spacecraft


class TestPhysicsEngine:
    """Test cases for PhysicsEngine class."""

    def test_physics_engine_initialization(self):
        """Test that PhysicsEngine initializes correctly."""
        engine = PhysicsEngine()
        assert engine is not None
        assert engine.gravitational_constant == 6.67430e-11

    def test_calculate_gravity(self):
        """Test gravitational force calculation."""
        engine = PhysicsEngine()

        # Create test spacecraft
        ship = Spacecraft(
            id="test-ship",
            name="Test Ship",
            ship_type="scout",
            mass=5000.0,
            dry_mass=4000.0,
            max_fuel_capacity=1000.0,
            current_fuel=500.0,
            max_thrust=10000.0,
            specific_impulse=300.0,
            cruise_speed=1000.0,
        )

        # Create test celestial body (Earth)
        earth = CelestialBody(
            id="earth",
            name="Earth",
            type="planet",
            mass=5.972e24,  # kg
            radius=6.371e6,  # meters
            atmosphere_pressure=101.3,
            atmosphere_depth=100000.0,
            temperature=288.0,
            has_atmosphere=True,
            has_water=True,
        )

        # Position ship at 1 AU from Earth
        ship.position = Vector3D(1.496e11, 0.0, 0.0)
        earth.position = Vector3D(0.0, 0.0, 0.0)

        # Calculate gravity
        force = engine.calculate_gravity(ship, earth)

        # Verify force is a Vector3D
        assert isinstance(force, Vector3D)

        # Verify force magnitude is positive
        assert force.magnitude() > 0

        # Verify force points toward Earth (negative direction)
        assert force.x < 0  # Should point toward origin

    def test_calculate_gravity_zero_distance(self):
        """Test gravity calculation at zero distance."""
        engine = PhysicsEngine()

        ship = Spacecraft(
            id="test",
            name="Test",
            ship_type="scout",
            mass=5000,
            dry_mass=4000,
            max_fuel_capacity=1000,
            current_fuel=500,
            max_thrust=10000,
            specific_impulse=300,
            cruise_speed=1000,
        )

        earth = CelestialBody(
            id="earth",
            name="Earth",
            type="planet",
            mass=5.972e24,
            radius=6.371e6,
            atmosphere_pressure=101.3,
            atmosphere_depth=100000,
            temperature=288.0,
            has_atmosphere=True,
            has_water=True,
        )

        # Same position = zero distance
        ship.position = Vector3D(0.0, 0.0, 0.0)
        earth.position = Vector3D(0.0, 0.0, 0.0)

        force = engine.calculate_gravity(ship, earth)

        # Should return zero force at zero distance
        assert force.magnitude() == 0.0

    def test_calculate_acceleration(self):
        """Test acceleration calculation from force."""
        engine = PhysicsEngine()

        # F = ma, so a = F/m
        force = Vector3D(100.0, 0.0, 0.0)  # 100 N in x direction
        mass = 10.0  # 10 kg

        acceleration = engine.calculate_acceleration(force, mass)

        # Should be 10 m/s² in x direction
        assert acceleration.x == 10.0
        assert acceleration.y == 0.0
        assert acceleration.z == 0.0

    def test_calculate_acceleration_zero_mass(self):
        """Test acceleration with zero mass."""
        engine = PhysicsEngine()

        force = Vector3D(100.0, 0.0, 0.0)
        mass = 0.0

        acceleration = engine.calculate_acceleration(force, mass)

        # Should return zero acceleration for zero mass
        assert acceleration.magnitude() == 0.0
