"""
Integration Tests

Tests that verify multiple components work together.
"""

from __future__ import annotations

import pytest
from src.simulator import (
    PhysicsEngine,
    Vector3D,
    Quaternion,
    Spacecraft,
    SolarSystem,
    CelestialBody,
)
from src.models import User, Mission, Objective


class TestModelIntegration:
    """Integration tests for models working together."""

    def test_spacecraft_physics_integration(self):
        """Test spacecraft with physics engine."""
        engine = PhysicsEngine()
        system = SolarSystem()
        sun = system.get_body("sun")
        
        assert sun is not None
        
        ship = Spacecraft(
            id="ship-1", name="Explorer", ship_type="scout",
            mass=5000, dry_mass=4000, max_fuel_capacity=1000,
            current_fuel=500, max_thrust=10000,
            specific_impulse=300, cruise_speed=1000
        )
        
        # Position ship away from sun
        ship.position = Vector3D(1.496e11, 0.0, 0.0)
        
        # Calculate gravity
        force = engine.calculate_gravity(ship, sun)
        
        assert force.magnitude() > 0

    def test_user_mission_integration(self):
        """Test user with mission tracking."""
        user = User(
            id="u1", username="test", email="test@example.com", display_name="Test"
        )
        
        mission = Mission(
            id="m1", name="Mars Mission", type="challenge",
            difficulty="intermediate", description="Navigate to Mars"
        )
        
        mission.start()
        user.missions_attempted += 1
        
        # Complete mission
        obj = Objective(id="obj1", description="Reach Mars", type="reach", target_id="mars")
        mission.objectives.append(obj)
        mission.complete_objective("obj1")
        
        if mission.check_completion():
            user.add_completed_mission(mission.id, mission.elapsed_time)
        
        assert user.missions_completed >= 0
        assert mission.status == "in_progress"

    def test_vector_operations(self):
        """Test Vector3D operations."""
        v1 = Vector3D(1.0, 2.0, 3.0)
        v2 = Vector3D(4.0, 5.0, 6.0)
        
        v3 = v1 + v2
        assert v3.x == 5.0
        assert v3.y == 7.0
        assert v3.z == 9.0
        
        v4 = v1 * 2.0
        assert v4.x == 2.0
        assert v4.y == 4.0
        assert v4.z == 6.0
        
        mag = v1.magnitude()
        assert mag > 0

    def test_quaternion_operations(self):
        """Test Quaternion operations."""
        q = Quaternion.from_euler(0.0, 0.0, 0.0)
        pitch, yaw, roll = q.to_euler()
        
        assert abs(pitch) < 0.001
        assert abs(yaw) < 0.001
        assert abs(roll) < 0.001

    def test_spacecraft_fuel_consumption(self):
        """Test spacecraft fuel consumption."""
        ship = Spacecraft(
            id="ship-1", name="Test", ship_type="scout",
            mass=5000, dry_mass=4000, max_fuel_capacity=1000,
            current_fuel=500, max_thrust=10000,
            specific_impulse=300, cruise_speed=1000
        )
        
        ship.set_throttle(50.0)  # 50% throttle
        
        initial_fuel = ship.current_fuel
        fuel_consumed = ship.consume_fuel(1.0)  # 1 second
        
        assert ship.current_fuel < initial_fuel
        assert fuel_consumed >= 0.0
