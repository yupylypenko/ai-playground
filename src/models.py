"""
Application Models

Data models for user profiles, missions, and gameplay progression.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Objective:
    """
    Single mission objective.

    Represents one goal within a mission that must be completed
    for mission success.

    Attributes:
        id: Unique objective identifier
        description: Human-readable objective description
        type: Objective type ("reach", "collect", "maintain", "avoid")
        target_id: Optional target body/ship ID
        position: Optional target position
        completed: Whether objective is completed

    Examples:
        >>> obj = Objective(
        ...     id="obj-1",
        ...     description="Reach Mars orbit",
        ...     type="reach",
        ...     target_id="mars"
        ... )
    """

    id: str
    description: str
    type: str  # "reach", "collect", "maintain", "avoid"
    target_id: Optional[str] = None
    position: Optional[tuple[float, float, float]] = None  # (x, y, z)
    completed: bool = False

    def __repr__(self) -> str:
        status = "✓" if self.completed else "○"
        return f"Objective[{status}](id='{self.id}', type='{self.type}')"


@dataclass
class Mission:
    """
    Mission with objectives, constraints, and tracking.

    Represents a complete mission with start conditions, objectives,
    and progress tracking.

    Attributes:
        id: Unique mission identifier
        name: Mission title
        type: Mission type ("tutorial", "free_flight", "challenge")
        difficulty: Difficulty level
        description: Mission description
        objectives: List of objectives
        current_objective_index: Currently active objective
        completion_criteria: Success conditions
        start_position: Initial position (x, y, z)
        target_body_id: Target celestial body
        max_fuel: Starting fuel in L
        time_limit: Optional time limit in seconds
        allowed_ship_types: Permitted ship types
        failure_conditions: Conditions that cause failure
        start_time: Mission start timestamp
        elapsed_time: Time since start
        distance_traveled: Total distance in meters
        fuel_consumed: Fuel used in L
        objectives_completed: Number of completed objectives
        status: Mission status
        estimated_time: Estimated duration in seconds

    Examples:
        >>> mission = Mission(
        ...     id="m-001",
        ...     name="Mars Approach",
        ...     type="challenge",
        ...     difficulty="intermediate"
        ... )
        >>> mission.start()
    """

    # Identity
    id: str
    name: str
    type: str  # "tutorial", "free_flight", "challenge"
    difficulty: str  # "beginner", "intermediate", "advanced"
    description: str

    # Objectives
    objectives: List[Objective] = field(default_factory=list)
    current_objective_index: int = 0
    completion_criteria: Dict[str, any] = field(default_factory=dict)

    # Constraints & Setup
    start_position: tuple[float, float, float] = (0.0, 0.0, 0.0)  # (x, y, z)
    target_body_id: Optional[str] = None
    max_fuel: float = 1000.0  # L
    time_limit: Optional[float] = None  # seconds
    allowed_ship_types: List[str] = field(default_factory=list)
    failure_conditions: List[str] = field(default_factory=list)

    # Tracking
    start_time: Optional[float] = None
    elapsed_time: float = 0.0
    distance_traveled: float = 0.0
    fuel_consumed: float = 0.0
    objectives_completed: int = 0

    # Status
    status: str = "not_started"  # "not_started", "in_progress", "completed", "failed"
    estimated_time: float = 3600.0  # seconds

    def start(self) -> None:
        """Start the mission."""
        self.start_time = datetime.now().timestamp()
        self.status = "in_progress"

    def complete_objective(self, objective_id: str) -> None:
        """
        Mark an objective as completed.

        Args:
            objective_id: ID of the objective to complete
        """
        for obj in self.objectives:
            if obj.id == objective_id and not obj.completed:
                obj.completed = True
                self.objectives_completed += 1
                break

    def check_completion(self) -> bool:
        """
        Check if all objectives are completed.

        Returns:
            True if all objectives completed
        """
        return all(obj.completed for obj in self.objectives)

    def get_current_objective(self) -> Optional[Objective]:
        """
        Get the currently active objective.

        Returns:
            Current objective or None
        """
        if 0 <= self.current_objective_index < len(self.objectives):
            return self.objectives[self.current_objective_index]
        return None

    def __repr__(self) -> str:
        return f"Mission(id='{self.id}', name='{self.name}', status='{self.status}')"


@dataclass
class User:
    """
    User profile with preferences and statistics.

    Tracks user settings, game progress, and accumulated statistics.

    Attributes:
        id: Unique user identifier (UUID)
        username: Login username
        email: Email address
        display_name: Display name
        screen_width: Display width in pixels
        screen_height: Display height in pixels
        fullscreen: Fullscreen mode
        font_scale: Text scaling 0.75-2.0
        high_contrast: High contrast mode
        enable_sounds: Audio enabled
        master_volume: Master volume 0.0-1.0
        music_volume: Music volume 0.0-1.0
        sfx_volume: SFX volume 0.0-1.0
        total_flight_time: Total flight time in hours
        missions_completed: Number of completed missions
        missions_attempted: Total mission attempts
        distance_traveled: Total distance in km
        fuel_consumed: Total fuel in L
        ship_types_used: List of unique ship types flown
        unlocked_ships: List of available ship IDs
        completed_missions: List of completed mission IDs
        best_times: Best time per mission (mission_id -> seconds)
        achievements: List of earned achievement IDs
        created_at: Account creation timestamp
        last_login: Last login timestamp

    Examples:
        >>> user = User(
        ...     id="user-001",
        ...     username="player1",
        ...     email="player1@example.com",
        ...     display_name="Explorer"
        ... )
    """

    # Identity
    id: str
    username: str
    email: str
    display_name: str

    # Display Preferences
    screen_width: int = 1280
    screen_height: int = 720
    fullscreen: bool = False

    # Accessibility Preferences
    font_scale: float = 1.0  # 0.75-2.0
    high_contrast: bool = False

    # Audio Preferences
    enable_sounds: bool = True
    master_volume: float = 0.8  # 0.0-1.0
    music_volume: float = 0.6  # 0.0-1.0
    sfx_volume: float = 0.8  # 0.0-1.0

    # Statistics
    total_flight_time: float = 0.0  # hours
    missions_completed: int = 0
    missions_attempted: int = 0
    distance_traveled: float = 0.0  # km
    fuel_consumed: float = 0.0  # L
    ship_types_used: List[str] = field(default_factory=list)

    # Progression
    unlocked_ships: List[str] = field(default_factory=list)
    completed_missions: List[str] = field(default_factory=list)
    best_times: Dict[str, float] = field(default_factory=dict)
    achievements: List[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None

    def update_statistics(
        self, flight_time: float, distance: float, fuel: float, ship_type: str
    ) -> None:
        """
        Update statistics after a flight session.

        Args:
            flight_time: Flight time in hours
            distance: Distance traveled in km
            fuel: Fuel consumed in L
            ship_type: Type of ship used
        """
        self.total_flight_time += flight_time
        self.distance_traveled += distance
        self.fuel_consumed += fuel
        if ship_type not in self.ship_types_used:
            self.ship_types_used.append(ship_type)
        self.last_login = datetime.now()

    def add_completed_mission(self, mission_id: str, time: float) -> None:
        """
        Record a completed mission.

        Args:
            mission_id: ID of the completed mission
            time: Mission completion time in seconds
        """
        if mission_id not in self.completed_missions:
            self.completed_missions.append(mission_id)
        self.missions_completed += 1
        if mission_id not in self.best_times or time < self.best_times[mission_id]:
            self.best_times[mission_id] = time

    def get_completion_rate(self) -> float:
        """
        Calculate mission completion rate.

        Returns:
            Completion rate as percentage (0-100)
        """
        if self.missions_attempted == 0:
            return 0.0
        return (self.missions_completed / self.missions_attempted) * 100.0

    def __repr__(self) -> str:
        return f"User(id='{self.id}', username='{self.username}')"


@dataclass
class AuthProfile:
    """
    Authentication profile for credential storage.

    Stores hashed credentials that back a `User` identity without
    exposing raw passwords to the rest of the system.

    Attributes:
        id: Unique auth profile identifier
        user_id: Associated user identifier
        username: Auth username (mirrors user username)
        email: Email used for login
        password_hash: Hashed password string
        password_salt: Salt used to hash the password
        created_at: Timestamp when the profile was created
    """

    id: str
    user_id: str
    username: str
    email: str
    password_hash: str
    password_salt: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Project:
    """
    User-created mission project template.

    Represents a customizable mission configuration that users can create,
    save, and later use to generate missions. Projects serve as templates
    that define mission parameters, objectives, and constraints.

    Attributes:
        id: Unique project identifier
        user_id: Owner user identifier
        name: Project name/title
        description: Project description
        mission_type: Type of mission ("tutorial", "free_flight", "challenge")
        difficulty: Difficulty level ("beginner", "intermediate", "advanced")
        target_body_id: Optional target celestial body ID
        start_position: Initial position (x, y, z) in meters
        max_fuel: Maximum fuel capacity in liters
        time_limit: Optional time limit in seconds
        allowed_ship_types: List of permitted ship type identifiers
        failure_conditions: List of failure condition descriptions
        objectives: List of objective templates
        is_public: Whether project is publicly shareable
        created_at: Project creation timestamp
        updated_at: Last update timestamp

    Examples:
        >>> project = Project(
        ...     id="proj-001",
        ...     user_id="user-123",
        ...     name="Mars Exploration",
        ...     description="Journey to Mars",
        ...     mission_type="challenge",
        ...     difficulty="intermediate"
        ... )
        >>> project.add_objective_template("Reach Mars orbit")
    """

    id: str
    user_id: str
    name: str
    description: str
    mission_type: str  # "tutorial", "free_flight", "challenge"
    difficulty: str  # "beginner", "intermediate", "advanced"

    # Mission configuration
    target_body_id: Optional[str] = None
    start_position: tuple[float, float, float] = (0.0, 0.0, 0.0)  # (x, y, z)
    max_fuel: float = 1000.0  # L
    time_limit: Optional[float] = None  # seconds
    allowed_ship_types: List[str] = field(default_factory=list)
    failure_conditions: List[str] = field(default_factory=list)

    # Objective templates (stored as dictionaries for flexibility)
    objectives: List[Dict[str, any]] = field(default_factory=list)

    # Visibility
    is_public: bool = False

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_objective_template(
        self,
        description: str,
        obj_type: str = "reach",
        target_id: Optional[str] = None,
        position: Optional[tuple[float, float, float]] = None,
    ) -> None:
        """
        Add an objective template to the project.

        Args:
            description: Objective description
            obj_type: Objective type ("reach", "collect", "maintain", "avoid")
            target_id: Optional target body/ship ID
            position: Optional target position (x, y, z)
        """
        objective = {
            "description": description,
            "type": obj_type,
            "target_id": target_id,
            "position": position,
        }
        self.objectives.append(objective)
        self.updated_at = datetime.now()

    def update_metadata(
        self, name: Optional[str] = None, description: Optional[str] = None
    ) -> None:
        """
        Update project metadata.

        Args:
            name: Optional new name
            description: Optional new description
        """
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        self.updated_at = datetime.now()

    def __repr__(self) -> str:
        return f"Project(id='{self.id}', name='{self.name}', user_id='{self.user_id}')"
