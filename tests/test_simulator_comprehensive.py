"""
Comprehensive tests for simulator modules.
"""

from __future__ import annotations

from src.simulator.physics import PhysicsEngine
from src.simulator.solar_system import CelestialBody, SolarSystem
from src.simulator.spacecraft import Spacecraft
from src.simulator.types import Vector3D


class TestPhysicsEngine:
    """Tests for PhysicsEngine."""

    def test_calculate_gravity_zero_distance(self) -> None:
        """Test gravity calculation when distance is zero."""
        engine = PhysicsEngine()
        spacecraft = Spacecraft(
            id="ship-1",
            name="Test Ship",
            ship_type="scout",
            mass=1000.0,
            dry_mass=800.0,
            max_fuel_capacity=200.0,
            current_fuel=100.0,
            max_thrust=10000.0,
            specific_impulse=300.0,
            cruise_speed=100.0,
        )
        spacecraft.position = Vector3D(0.0, 0.0, 0.0)

        body = CelestialBody(
            id="earth",
            name="Earth",
            type="planet",
            mass=5.972e24,
            radius=6.371e6,
            atmosphere_pressure=101.3,
            atmosphere_depth=100000.0,
            temperature=288.0,
            has_atmosphere=True,
            has_water=True,
        )
        body.position = Vector3D(0.0, 0.0, 0.0)

        force = engine.calculate_gravity(spacecraft, body)
        assert force.x == 0.0
        assert force.y == 0.0
        assert force.z == 0.0

    def test_calculate_acceleration_zero_mass(self) -> None:
        """Test acceleration calculation with zero mass."""
        engine = PhysicsEngine()
        force = Vector3D(100.0, 0.0, 0.0)

        acceleration = engine.calculate_acceleration(force, 0.0)
        assert acceleration.x == 0.0
        assert acceleration.y == 0.0
        assert acceleration.z == 0.0

    def test_physics_engine_repr(self) -> None:
        """Test PhysicsEngine string representation."""
        engine = PhysicsEngine()
        assert "PhysicsEngine" in repr(engine)


class TestCelestialBody:
    """Tests for CelestialBody."""

    def test_get_surface_gravity_zero_radius(self) -> None:
        """Test surface gravity with zero radius."""
        body = CelestialBody(
            id="test",
            name="Test Body",
            type="planet",
            mass=1.0e24,
            radius=0.0,
            atmosphere_pressure=0.0,
            atmosphere_depth=0.0,
            temperature=0.0,
            has_atmosphere=False,
            has_water=False,
        )

        gravity = body.get_surface_gravity()
        assert gravity == 0.0

    def test_get_surface_gravity_normal(self) -> None:
        """Test surface gravity calculation with normal radius."""
        body = CelestialBody(
            id="earth",
            name="Earth",
            type="planet",
            mass=5.972e24,
            radius=6.371e6,
            atmosphere_pressure=101.3,
            atmosphere_depth=100000.0,
            temperature=288.0,
            has_atmosphere=True,
            has_water=True,
        )

        gravity = body.get_surface_gravity()
        # Earth's surface gravity is approximately 9.81 m/s²
        assert 9.0 < gravity < 10.0

    def test_is_in_atmosphere_no_atmosphere(self) -> None:
        """Test atmosphere check when body has no atmosphere."""
        body = CelestialBody(
            id="moon",
            name="Moon",
            type="moon",
            mass=7.342e22,
            radius=1.737e6,
            atmosphere_pressure=0.0,
            atmosphere_depth=0.0,
            temperature=250.0,
            has_atmosphere=False,
            has_water=False,
        )
        body.position = Vector3D(0.0, 0.0, 0.0)

        position = Vector3D(1.0e6, 0.0, 0.0)
        assert body.is_in_atmosphere(position) is False

    def test_is_in_atmosphere_within(self) -> None:
        """Test atmosphere check when position is within atmosphere."""
        body = CelestialBody(
            id="earth",
            name="Earth",
            type="planet",
            mass=5.972e24,
            radius=6.371e6,
            atmosphere_pressure=101.3,
            atmosphere_depth=100000.0,
            temperature=288.0,
            has_atmosphere=True,
            has_water=True,
        )
        body.position = Vector3D(0.0, 0.0, 0.0)

        # Position within atmosphere
        position = Vector3D(6.4e6, 0.0, 0.0)  # Just above surface
        assert body.is_in_atmosphere(position) is True

    def test_get_distance_to_surface(self) -> None:
        """Test distance to surface calculation."""
        body = CelestialBody(
            id="earth",
            name="Earth",
            type="planet",
            mass=5.972e24,
            radius=6.371e6,
            atmosphere_pressure=101.3,
            atmosphere_depth=100000.0,
            temperature=288.0,
            has_atmosphere=True,
            has_water=True,
        )
        body.position = Vector3D(0.0, 0.0, 0.0)

        # Position above surface
        position = Vector3D(7.0e6, 0.0, 0.0)
        distance = body.get_distance_to_surface(position)
        assert distance > 0.0
        assert abs(distance - (7.0e6 - 6.371e6)) < 1.0

        # Position below surface (negative distance)
        position = Vector3D(5.0e6, 0.0, 0.0)
        distance = body.get_distance_to_surface(position)
        assert distance < 0.0

    def test_celestial_body_post_init(self) -> None:
        """Test that position and velocity are initialized if None."""
        body = CelestialBody(
            id="test",
            name="Test",
            type="planet",
            mass=1.0e24,
            radius=1.0e6,
            atmosphere_pressure=0.0,
            atmosphere_depth=0.0,
            temperature=0.0,
            has_atmosphere=False,
            has_water=False,
            position=None,
            velocity=None,
        )

        assert body.position is not None
        assert body.velocity is not None
        assert body.position.x == 0.0
        assert body.velocity.x == 0.0

    def test_celestial_body_repr(self) -> None:
        """Test CelestialBody string representation."""
        body = CelestialBody(
            id="earth",
            name="Earth",
            type="planet",
            mass=5.972e24,
            radius=6.371e6,
            atmosphere_pressure=101.3,
            atmosphere_depth=100000.0,
            temperature=288.0,
            has_atmosphere=True,
            has_water=True,
        )

        repr_str = repr(body)
        assert "earth" in repr_str
        assert "Earth" in repr_str
        assert "planet" in repr_str


class TestSolarSystem:
    """Tests for SolarSystem."""

    def test_get_nearest_body_empty(self) -> None:
        """Test getting nearest body when system is empty."""
        system = SolarSystem()
        # Clear bodies (keep sun for initialization)
        system.bodies = {}

        position = Vector3D(1.0e11, 0.0, 0.0)
        nearest = system.get_nearest_body(position)
        assert nearest is None

    def test_get_nearest_body(self) -> None:
        """Test getting nearest body."""
        system = SolarSystem()

        earth = CelestialBody(
            id="earth",
            name="Earth",
            type="planet",
            mass=5.972e24,
            radius=6.371e6,
            atmosphere_pressure=101.3,
            atmosphere_depth=100000.0,
            temperature=288.0,
            has_atmosphere=True,
            has_water=True,
        )
        earth.position = Vector3D(1.5e11, 0.0, 0.0)  # 1 AU

        mars = CelestialBody(
            id="mars",
            name="Mars",
            type="planet",
            mass=6.39e23,
            radius=3.39e6,
            atmosphere_pressure=0.6,
            atmosphere_depth=11000.0,
            temperature=210.0,
            has_atmosphere=True,
            has_water=False,
        )
        mars.position = Vector3D(2.3e11, 0.0, 0.0)  # ~1.5 AU

        system.add_body(earth)
        system.add_body(mars)

        # Position closer to Earth
        position = Vector3D(1.6e11, 0.0, 0.0)
        nearest = system.get_nearest_body(position)
        assert nearest is not None
        assert nearest.id == "earth"

    def test_solar_system_repr(self) -> None:
        """Test SolarSystem string representation."""
        system = SolarSystem()
        repr_str = repr(system)
        assert "SolarSystem" in repr_str


class TestSpacecraft:
    """Tests for Spacecraft."""

    def test_get_fuel_percent_zero_capacity(self) -> None:
        """Test fuel percentage with zero capacity."""
        ship = Spacecraft(
            id="ship-1",
            name="Test Ship",
            ship_type="scout",
            mass=1000.0,
            dry_mass=1000.0,
            max_fuel_capacity=0.0,
            current_fuel=0.0,
            max_thrust=10000.0,
            specific_impulse=300.0,
            cruise_speed=100.0,
        )

        assert ship.get_fuel_percent() == 0.0

    def test_get_fuel_percent_normal(self) -> None:
        """Test fuel percentage calculation with normal capacity."""
        ship = Spacecraft(
            id="ship-1",
            name="Test Ship",
            ship_type="scout",
            mass=1000.0,
            dry_mass=800.0,
            max_fuel_capacity=200.0,
            current_fuel=100.0,  # 50% full
            max_thrust=10000.0,
            specific_impulse=300.0,
            cruise_speed=100.0,
        )

        assert ship.get_fuel_percent() == 50.0

    def test_consume_fuel_no_thrust(self) -> None:
        """Test fuel consumption with no thrust."""
        ship = Spacecraft(
            id="ship-1",
            name="Test Ship",
            ship_type="scout",
            mass=1000.0,
            dry_mass=800.0,
            max_fuel_capacity=200.0,
            current_fuel=100.0,
            max_thrust=10000.0,
            specific_impulse=300.0,
            cruise_speed=100.0,
        )
        ship.thrust_level = 0.0

        consumed = ship.consume_fuel(1.0)
        assert consumed == 0.0
        assert ship.current_fuel == 100.0

    def test_consume_fuel_with_boost(self) -> None:
        """Test fuel consumption with boost active."""
        ship = Spacecraft(
            id="ship-1",
            name="Test Ship",
            ship_type="scout",
            mass=1000.0,
            dry_mass=800.0,
            max_fuel_capacity=200.0,
            current_fuel=100.0,
            max_thrust=10000.0,
            specific_impulse=300.0,
            cruise_speed=100.0,
        )
        ship.thrust_level = 0.5
        ship.boost_active = True

        initial_fuel = ship.current_fuel
        consumed = ship.consume_fuel(1.0)

        # Boost should double consumption
        assert consumed > 0.0
        assert ship.current_fuel < initial_fuel

    def test_update_life_support_status_transitions(self) -> None:
        """Test life support status transitions."""
        ship = Spacecraft(
            id="ship-1",
            name="Test Ship",
            ship_type="scout",
            mass=1000.0,
            dry_mass=800.0,
            max_fuel_capacity=200.0,
            current_fuel=100.0,
            max_thrust=10000.0,
            specific_impulse=300.0,
            cruise_speed=100.0,
        )

        # Nominal
        ship.oxygen_level = 60.0
        ship.update_life_support(1.0)
        assert ship.life_support_status == "nominal"

        # Warning
        ship.oxygen_level = 30.0
        ship.update_life_support(1.0)
        assert ship.life_support_status == "warning"

        # Critical
        ship.oxygen_level = 10.0
        ship.update_life_support(1.0)
        assert ship.life_support_status == "critical"

    def test_set_throttle_bounds(self) -> None:
        """Test throttle setting with boundary values."""
        ship = Spacecraft(
            id="ship-1",
            name="Test Ship",
            ship_type="scout",
            mass=1000.0,
            dry_mass=800.0,
            max_fuel_capacity=200.0,
            current_fuel=100.0,
            max_thrust=10000.0,
            specific_impulse=300.0,
            cruise_speed=100.0,
        )

        # Below minimum
        ship.set_throttle(-10.0)
        assert ship.throttle == 0.0
        assert ship.thrust_level == 0.0

        # Above maximum
        ship.set_throttle(150.0)
        assert ship.throttle == 100.0
        assert ship.thrust_level == 1.0

        # Normal value
        ship.set_throttle(50.0)
        assert ship.throttle == 50.0
        assert ship.thrust_level == 0.5

    def test_spacecraft_repr(self) -> None:
        """Test Spacecraft string representation."""
        ship = Spacecraft(
            id="ship-1",
            name="Test Ship",
            ship_type="scout",
            mass=1000.0,
            dry_mass=800.0,
            max_fuel_capacity=200.0,
            current_fuel=100.0,
            max_thrust=10000.0,
            specific_impulse=300.0,
            cruise_speed=100.0,
        )

        repr_str = repr(ship)
        assert "ship-1" in repr_str
        assert "Test Ship" in repr_str
        assert "scout" in repr_str
