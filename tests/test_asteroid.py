"""
Tests for Asteroid class and collision detection.
"""

from __future__ import annotations

from src.simulator import Asteroid, PhysicsEngine, Spacecraft, Vector3D


class TestAsteroid:
    """Tests for Asteroid class."""

    def test_asteroid_creation(self) -> None:
        """Test basic asteroid creation."""
        asteroid = Asteroid(
            id="ast-001",
            name="Test Asteroid",
            position=Vector3D(100.0, 0.0, 0.0),
            velocity=Vector3D(0.0, 0.0, 0.0),
            radius=5.0,
            mass=1000.0,
        )
        assert asteroid.id == "ast-001"
        assert asteroid.name == "Test Asteroid"
        assert asteroid.radius == 5.0
        assert asteroid.mass == 1000.0
        assert asteroid.size_category == "small"

    def test_asteroid_size_categories(self) -> None:
        """Test automatic size category assignment."""
        small = Asteroid(id="s", name="Small", radius=5.0, mass=100.0)
        assert small.size_category == "small"
        assert small.is_destroyable is True

        medium = Asteroid(id="m", name="Medium", radius=50.0, mass=10000.0)
        assert medium.size_category == "medium"
        assert medium.is_destroyable is True

        large = Asteroid(id="l", name="Large", radius=150.0, mass=100000.0)
        assert large.size_category == "large"
        assert large.is_destroyable is False

    def test_collision_detection(self) -> None:
        """Test collision detection between asteroid and object."""
        asteroid = Asteroid(
            id="ast-001",
            name="Test",
            position=Vector3D(0.0, 0.0, 0.0),
            radius=10.0,
        )
        object_pos = Vector3D(5.0, 0.0, 0.0)  # Within collision radius
        assert asteroid.is_colliding_with(object_pos, 5.0) is True

        object_pos_far = Vector3D(100.0, 0.0, 0.0)  # Outside collision radius
        assert asteroid.is_colliding_with(object_pos_far, 5.0) is False

    def test_time_to_collision(self) -> None:
        """Test time to collision calculation."""
        asteroid = Asteroid(
            id="ast-001",
            name="Test",
            position=Vector3D(0.0, 0.0, 0.0),
            velocity=Vector3D(0.0, 0.0, 0.0),
            radius=5.0,
        )
        # Object moving toward asteroid
        obj_pos = Vector3D(100.0, 0.0, 0.0)
        obj_vel = Vector3D(-10.0, 0.0, 0.0)  # Moving toward origin
        time = asteroid.get_time_to_collision(obj_pos, obj_vel, 5.0)
        assert time is not None
        assert time > 0.0

        # Object moving away
        obj_vel_away = Vector3D(10.0, 0.0, 0.0)  # Moving away
        time_away = asteroid.get_time_to_collision(obj_pos, obj_vel_away, 5.0)
        assert time_away is None


class TestAsteroidCollisionDetection:
    """Tests for collision detection in physics engine."""

    def test_check_collision(self) -> None:
        """Test collision check between spacecraft and asteroid."""
        engine = PhysicsEngine()
        spacecraft = Spacecraft(
            id="ship-1",
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
        spacecraft.position = Vector3D(10.0, 0.0, 0.0)

        asteroid = Asteroid(
            id="ast-001",
            name="Test",
            position=Vector3D(0.0, 0.0, 0.0),
            radius=10.0,
        )

        # Collision detected
        assert engine.check_collision(spacecraft, asteroid, 5.0) is True

        # No collision
        spacecraft.position = Vector3D(100.0, 0.0, 0.0)
        assert engine.check_collision(spacecraft, asteroid, 5.0) is False

    def test_detect_nearby_asteroids(self) -> None:
        """Test detection of nearby asteroids."""
        engine = PhysicsEngine()
        position = Vector3D(0.0, 0.0, 0.0)

        asteroids = [
            Asteroid(
                id="a1", name="Near", position=Vector3D(100.0, 0.0, 0.0), radius=5.0
            ),
            Asteroid(
                id="a2", name="Far", position=Vector3D(2000.0, 0.0, 0.0), radius=5.0
            ),
            Asteroid(
                id="a3", name="Near2", position=Vector3D(0.0, 150.0, 0.0), radius=5.0
            ),
        ]

        nearby = engine.detect_nearby_asteroids(
            position, asteroids, detection_range=500.0
        )
        assert len(nearby) == 2
        assert nearby[0].id in ["a1", "a3"]
        assert nearby[1].id in ["a1", "a3"]

    def test_calculate_avoidance_vector(self) -> None:
        """Test avoidance vector calculation."""
        engine = PhysicsEngine()
        spacecraft = Spacecraft(
            id="ship-1",
            name="Test",
            ship_type="scout",
            mass=5000.0,
            dry_mass=4000.0,
            max_fuel_capacity=1000.0,
            current_fuel=500.0,
            max_thrust=10000.0,
            specific_impulse=300.0,
            cruise_speed=1000.0,
        )
        spacecraft.position = Vector3D(100.0, 0.0, 0.0)
        spacecraft.velocity = Vector3D(-10.0, 0.0, 0.0)  # Moving toward asteroid

        asteroid = Asteroid(
            id="ast-001",
            name="Test",
            position=Vector3D(0.0, 0.0, 0.0),
            velocity=Vector3D(0.0, 0.0, 0.0),
            radius=5.0,
        )

        avoidance = engine.calculate_avoidance_vector(spacecraft, asteroid)
        assert avoidance is not None
        assert avoidance.magnitude() > 0.0

        # No threat (moving away)
        spacecraft.velocity = Vector3D(10.0, 0.0, 0.0)
        avoidance_none = engine.calculate_avoidance_vector(spacecraft, asteroid)
        assert avoidance_none is None
