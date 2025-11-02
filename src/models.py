"""
Application Models

Data models for user profiles, missions, and gameplay progression.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


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
        self,
        flight_time: float,
        distance: float,
        fuel: float,
        ship_type: str
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
