"""
Application Services

Services that coordinate domain logic with storage repositories.
"""

from __future__ import annotations

from typing import List, Optional

from src.cockpit.storage import MissionRepository, ProjectRepository, UserRepository
from src.models import Mission, Objective, Project, User


class UserService:
    """
    Service for user management operations.

    Coordinates user operations with storage repositories.
    """

    def __init__(self, user_repository: UserRepository) -> None:
        """
        Initialize user service.

        Args:
            user_repository: User repository implementation
        """
        self.user_repository = user_repository

    def create_user(
        self,
        username: str,
        email: str,
        display_name: str,
        user_id: Optional[str] = None,
    ) -> User:
        """
        Create a new user.

        Args:
            username: Username
            email: Email address
            display_name: Display name
            user_id: Optional user ID (generated if not provided)

        Returns:
            Created user instance

        Raises:
            ValueError: If username or email already exists
        """
        if self.user_repository.get_user_by_username(username):
            raise ValueError(f"Username '{username}' already exists")
        if self.user_repository.get_user_by_email(email):
            raise ValueError(f"Email '{email}' already exists")

        if not user_id:
            import uuid

            user_id = f"user-{uuid.uuid4().hex[:8]}"

        user = User(
            id=user_id,
            username=username,
            email=email,
            display_name=display_name,
        )
        self.user_repository.save_user(user)
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User instance or None
        """
        return self.user_repository.get_user(user_id)

    def update_user(self, user: User) -> None:
        """
        Update user profile.

        Args:
            user: User instance to update
        """
        self.user_repository.save_user(user)


class MissionService:
    """
    Service for mission management operations.

    Coordinates mission operations with storage repositories.
    """

    def __init__(self, mission_repository: MissionRepository) -> None:
        """
        Initialize mission service.

        Args:
            mission_repository: Mission repository implementation
        """
        self.mission_repository = mission_repository

    def create_mission(
        self,
        name: str,
        mission_type: str,
        difficulty: str,
        description: str,
        mission_id: Optional[str] = None,
        target_body_id: Optional[str] = None,
        start_position: tuple[float, float, float] = (0.0, 0.0, 0.0),
        max_fuel: float = 1000.0,
        time_limit: Optional[float] = None,
        allowed_ship_types: Optional[List[str]] = None,
        failure_conditions: Optional[List[str]] = None,
        objectives: Optional[List[Objective]] = None,
    ) -> Mission:
        """
        Create a new mission.

        Args:
            name: Mission name
            mission_type: Mission type ("tutorial", "free_flight", "challenge")
            difficulty: Difficulty level
            description: Mission description
            mission_id: Optional mission ID (generated if not provided)
            target_body_id: Optional target celestial body ID
            start_position: Initial position (x, y, z) in meters
            max_fuel: Maximum fuel capacity in liters
            time_limit: Optional time limit in seconds
            allowed_ship_types: List of permitted ship type identifiers
            failure_conditions: List of failure condition descriptions
            objectives: List of mission objectives

        Returns:
            Created mission instance

        Raises:
            ValueError: If mission name is empty or invalid type/difficulty
        """
        if not name or not name.strip():
            raise ValueError("Mission name cannot be empty")

        if mission_type not in ("tutorial", "free_flight", "challenge"):
            raise ValueError(
                f"Invalid mission type: {mission_type}. "
                "Must be one of: tutorial, free_flight, challenge"
            )

        if difficulty not in ("beginner", "intermediate", "advanced"):
            raise ValueError(
                f"Invalid difficulty: {difficulty}. "
                "Must be one of: beginner, intermediate, advanced"
            )

        if not mission_id:
            import uuid

            mission_id = f"mission-{uuid.uuid4().hex[:8]}"

        mission = Mission(
            id=mission_id,
            name=name.strip(),
            type=mission_type,
            difficulty=difficulty,
            description=description,
            target_body_id=target_body_id,
            start_position=start_position,
            max_fuel=max_fuel,
            time_limit=time_limit,
            allowed_ship_types=allowed_ship_types or [],
            failure_conditions=failure_conditions or [],
            objectives=objectives or [],
        )
        self.mission_repository.save_mission(mission)
        return mission

    def create_mission_from_project(
        self,
        project: Project,
        mission_id: Optional[str] = None,
        name_override: Optional[str] = None,
    ) -> Mission:
        """
        Create a mission from a project template.

        Args:
            project: Project template to create mission from
            mission_id: Optional mission ID (generated if not provided)
            name_override: Optional name override (uses project name if not provided)

        Returns:
            Created mission instance
        """
        import uuid

        # Convert project objectives to mission objectives
        objectives = []
        for idx, obj_template in enumerate(project.objectives):
            obj_id = (
                f"obj-{uuid.uuid4().hex[:8]}"
                if not mission_id
                else f"{mission_id}-obj-{idx}"
            )
            objective = Objective(
                id=obj_id,
                description=obj_template.get("description", ""),
                type=obj_template.get("type", "reach"),
                target_id=obj_template.get("target_id"),
                position=obj_template.get("position"),
                completed=False,
            )
            objectives.append(objective)

        return self.create_mission(
            name=name_override or project.name,
            mission_type=project.mission_type,
            difficulty=project.difficulty,
            description=project.description,
            mission_id=mission_id,
            target_body_id=project.target_body_id,
            start_position=project.start_position,
            max_fuel=project.max_fuel,
            time_limit=project.time_limit,
            allowed_ship_types=project.allowed_ship_types,
            failure_conditions=project.failure_conditions,
            objectives=objectives,
        )

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """
        Get mission by ID.

        Args:
            mission_id: Mission ID

        Returns:
            Mission instance or None
        """
        return self.mission_repository.get_mission(mission_id)

    def list_user_missions(
        self, user_id: str, status: Optional[str] = None
    ) -> List[Mission]:
        """
        List missions for a user.

        Args:
            user_id: User ID
            status: Optional status filter

        Returns:
            List of mission instances
        """
        return self.mission_repository.list_missions(user_id=user_id, status=status)

    def update_mission(self, mission: Mission) -> None:
        """
        Update mission.

        Args:
            mission: Mission instance to update
        """
        self.mission_repository.save_mission(mission)


class ProjectService:
    """
    Service for project management operations.

    Coordinates project operations with storage repositories.
    Projects are user-created mission templates that can be saved
    and later used to generate missions.
    """

    def __init__(self, project_repository: ProjectRepository) -> None:
        """
        Initialize project service.

        Args:
            project_repository: Project repository implementation
        """
        self.project_repository = project_repository

    def create_project(
        self,
        user_id: str,
        name: str,
        description: str,
        mission_type: str,
        difficulty: str,
        project_id: Optional[str] = None,
        target_body_id: Optional[str] = None,
        start_position: tuple[float, float, float] = (0.0, 0.0, 0.0),
        max_fuel: float = 1000.0,
        time_limit: Optional[float] = None,
        allowed_ship_types: Optional[List[str]] = None,
        failure_conditions: Optional[List[str]] = None,
        is_public: bool = False,
    ) -> Project:
        """
        Create a new project.

        Args:
            user_id: Owner user ID
            name: Project name
            description: Project description
            mission_type: Mission type ("tutorial", "free_flight", "challenge")
            difficulty: Difficulty level ("beginner", "intermediate", "advanced")
            project_id: Optional project ID (generated if not provided)
            target_body_id: Optional target celestial body ID
            start_position: Initial position (x, y, z) in meters
            max_fuel: Maximum fuel capacity in liters
            time_limit: Optional time limit in seconds
            allowed_ship_types: List of permitted ship type identifiers
            failure_conditions: List of failure condition descriptions
            is_public: Whether project is publicly shareable

        Returns:
            Created project instance

        Raises:
            ValueError: If project name is empty or invalid
        """
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty")

        if mission_type not in ("tutorial", "free_flight", "challenge"):
            raise ValueError(
                f"Invalid mission type: {mission_type}. "
                "Must be one of: tutorial, free_flight, challenge"
            )

        if difficulty not in ("beginner", "intermediate", "advanced"):
            raise ValueError(
                f"Invalid difficulty: {difficulty}. "
                "Must be one of: beginner, intermediate, advanced"
            )

        if not project_id:
            import uuid

            project_id = f"project-{uuid.uuid4().hex[:8]}"

        project = Project(
            id=project_id,
            user_id=user_id,
            name=name.strip(),
            description=description,
            mission_type=mission_type,
            difficulty=difficulty,
            target_body_id=target_body_id,
            start_position=start_position,
            max_fuel=max_fuel,
            time_limit=time_limit,
            allowed_ship_types=allowed_ship_types or [],
            failure_conditions=failure_conditions or [],
            is_public=is_public,
        )
        self.project_repository.save_project(project)
        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        """
        Get project by ID.

        Args:
            project_id: Project ID

        Returns:
            Project instance or None
        """
        return self.project_repository.get_project(project_id)

    def list_user_projects(
        self,
        user_id: str,
        mission_type: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> List[Project]:
        """
        List projects for a user.

        Args:
            user_id: User ID
            mission_type: Optional mission type filter
            is_public: Optional public visibility filter

        Returns:
            List of project instances
        """
        return self.project_repository.list_projects(
            user_id=user_id, mission_type=mission_type, is_public=is_public
        )

    def list_public_projects(self, mission_type: Optional[str] = None) -> List[Project]:
        """
        List publicly available projects.

        Args:
            mission_type: Optional mission type filter

        Returns:
            List of public project instances
        """
        return self.project_repository.list_projects(
            user_id=None, is_public=True, mission_type=mission_type
        )

    def update_project(self, project: Project) -> None:
        """
        Update project.

        Args:
            project: Project instance to update

        Raises:
            ValueError: If project name is empty or invalid
        """
        if not project.name or not project.name.strip():
            raise ValueError("Project name cannot be empty")

        if project.mission_type not in ("tutorial", "free_flight", "challenge"):
            raise ValueError(
                f"Invalid mission type: {project.mission_type}. "
                "Must be one of: tutorial, free_flight, challenge"
            )

        if project.difficulty not in ("beginner", "intermediate", "advanced"):
            raise ValueError(
                f"Invalid difficulty: {project.difficulty}. "
                "Must be one of: beginner, intermediate, advanced"
            )

        project.update_metadata()
        self.project_repository.save_project(project)

    def delete_project(self, project_id: str) -> None:
        """
        Delete a project.

        Args:
            project_id: Project ID
        """
        self.project_repository.delete_project(project_id)
