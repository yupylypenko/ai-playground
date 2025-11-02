"""
Tests for Application Models

Unit tests for User, Mission, and Objective models.
"""

from __future__ import annotations

import pytest
from datetime import datetime
from src.models import User, Mission, Objective


class TestUser:
    """Test cases for User model."""

    def test_user_initialization(self):
        """Test that User initializes correctly."""
        user = User(
            id="user-001",
            username="testuser",
            email="test@example.com",
            display_name="Test User"
        )
        
        assert user.id == "user-001"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.display_name == "Test User"
        assert user.total_flight_time == 0.0
        assert user.missions_completed == 0

    def test_update_statistics(self):
        """Test statistics update."""
        user = User(
            id="u1", username="test", email="test@example.com", display_name="Test"
        )
        
        user.update_statistics(
            flight_time=1.5,
            distance=5000.0,
            fuel=100.0,
            ship_type="scout"
        )
        
        assert user.total_flight_time == 1.5
        assert user.distance_traveled == 5000.0
        assert user.fuel_consumed == 100.0
        assert "scout" in user.ship_types_used

    def test_add_completed_mission(self):
        """Test adding completed mission."""
        user = User(
            id="u1", username="test", email="test@example.com", display_name="Test"
        )
        
        user.add_completed_mission("mission-1", 3600.0)
        
        assert user.missions_completed == 1
        assert "mission-1" in user.completed_missions
        assert user.best_times["mission-1"] == 3600.0

    def test_completion_rate(self):
        """Test completion rate calculation."""
        user = User(
            id="u1", username="test", email="test@example.com", display_name="Test"
        )
        
        # No attempts yet
        assert user.get_completion_rate() == 0.0
        
        # Add attempts and completions
        user.missions_attempted = 10
        user.missions_completed = 7
        
        assert user.get_completion_rate() == 70.0


class TestMission:
    """Test cases for Mission model."""

    def test_mission_initialization(self):
        """Test that Mission initializes correctly."""
        mission = Mission(
            id="mission-001",
            name="Test Mission",
            type="tutorial",
            difficulty="beginner",
            description="A test mission"
        )
        
        assert mission.id == "mission-001"
        assert mission.name == "Test Mission"
        assert mission.type == "tutorial"
        assert mission.difficulty == "beginner"
        assert mission.status == "not_started"

    def test_mission_start(self):
        """Test mission start."""
        mission = Mission(
            id="m1", name="Test", type="tutorial", difficulty="beginner", description="Test"
        )
        
        mission.start()
        
        assert mission.status == "in_progress"
        assert mission.start_time is not None

    def test_complete_objective(self):
        """Test objective completion."""
        mission = Mission(
            id="m1", name="Test", type="tutorial", difficulty="beginner", description="Test"
        )
        
        obj = Objective(
            id="obj-1",
            description="Reach orbit",
            type="reach",
            target_id="earth"
        )
        
        mission.objectives.append(obj)
        mission.complete_objective("obj-1")
        
        assert obj.completed is True
        assert mission.objectives_completed == 1

    def test_check_completion(self):
        """Test completion check."""
        mission = Mission(
            id="m1", name="Test", type="tutorial", difficulty="beginner", description="Test"
        )
        
        # No objectives = not complete
        assert mission.check_completion() is True  # Empty list is all completed
        
        # Add incomplete objective
        obj1 = Objective(id="obj-1", description="Task 1", type="reach")
        mission.objectives.append(obj1)
        assert mission.check_completion() is False
        
        # Complete objective
        mission.complete_objective("obj-1")
        assert mission.check_completion() is True


class TestObjective:
    """Test cases for Objective model."""

    def test_objective_initialization(self):
        """Test that Objective initializes correctly."""
        obj = Objective(
            id="obj-001",
            description="Reach Mars orbit",
            type="reach",
            target_id="mars"
        )
        
        assert obj.id == "obj-001"
        assert obj.description == "Reach Mars orbit"
        assert obj.type == "reach"
        assert obj.target_id == "mars"
        assert obj.completed is False
