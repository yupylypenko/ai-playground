"""
Tests for ProjectService.

Covers project creation, retrieval, listing, updating, and deletion.
"""

from __future__ import annotations

import pytest

from src.cockpit.memory import InMemoryProjectRepository
from src.cockpit.services import ProjectService
from src.models import Project


@pytest.fixture
def project_service() -> ProjectService:
    """Create a ProjectService for testing."""
    project_repo = InMemoryProjectRepository()
    return ProjectService(project_repository=project_repo)


class TestProjectServiceCreate:
    """Test project creation in ProjectService."""

    def test_create_project_success(self, project_service: ProjectService) -> None:
        """Test successful project creation."""
        project = project_service.create_project(
            user_id="user-123",
            name="Mars Mission",
            description="Journey to Mars",
            mission_type="challenge",
            difficulty="intermediate",
        )

        assert project.id is not None
        assert project.user_id == "user-123"
        assert project.name == "Mars Mission"
        assert project.description == "Journey to Mars"
        assert project.mission_type == "challenge"
        assert project.difficulty == "intermediate"
        assert project.is_public is False
        assert project.created_at is not None

    def test_create_project_with_custom_id(
        self, project_service: ProjectService
    ) -> None:
        """Test project creation with custom ID."""
        project = project_service.create_project(
            user_id="user-123",
            name="Custom Mission",
            description="Test",
            mission_type="tutorial",
            difficulty="beginner",
            project_id="custom-project-001",
        )

        assert project.id == "custom-project-001"

    def test_create_project_with_all_fields(
        self, project_service: ProjectService
    ) -> None:
        """Test project creation with all optional fields."""
        project = project_service.create_project(
            user_id="user-123",
            name="Complete Mission",
            description="Full featured mission",
            mission_type="challenge",
            difficulty="advanced",
            target_body_id="jupiter",
            start_position=(100.0, 200.0, 300.0),
            max_fuel=2000.0,
            time_limit=7200.0,
            allowed_ship_types=["explorer", "cargo"],
            failure_conditions=["Out of fuel"],
            is_public=True,
        )

        assert project.target_body_id == "jupiter"
        assert project.start_position == (100.0, 200.0, 300.0)
        assert project.max_fuel == 2000.0
        assert project.time_limit == 7200.0
        assert project.allowed_ship_types == ["explorer", "cargo"]
        assert project.failure_conditions == ["Out of fuel"]
        assert project.is_public is True

    def test_create_project_empty_name(self, project_service: ProjectService) -> None:
        """Test project creation with empty name raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            project_service.create_project(
                user_id="user-123",
                name="",
                description="Test",
                mission_type="tutorial",
                difficulty="beginner",
            )

    def test_create_project_invalid_mission_type(
        self, project_service: ProjectService
    ) -> None:
        """Test project creation with invalid mission type."""
        with pytest.raises(ValueError, match="Invalid mission type"):
            project_service.create_project(
                user_id="user-123",
                name="Test",
                description="Test",
                mission_type="invalid",
                difficulty="beginner",
            )

    def test_create_project_invalid_difficulty(
        self, project_service: ProjectService
    ) -> None:
        """Test project creation with invalid difficulty."""
        with pytest.raises(ValueError, match="Invalid difficulty"):
            project_service.create_project(
                user_id="user-123",
                name="Test",
                description="Test",
                mission_type="tutorial",
                difficulty="invalid",
            )

    def test_create_project_all_valid_mission_types(
        self, project_service: ProjectService
    ) -> None:
        """Test project creation with all valid mission types."""
        for mission_type in ["tutorial", "free_flight", "challenge"]:
            project = project_service.create_project(
                user_id="user-123",
                name=f"Test {mission_type}",
                description="Test",
                mission_type=mission_type,
                difficulty="beginner",
            )
            assert project.mission_type == mission_type

    def test_create_project_all_valid_difficulties(
        self, project_service: ProjectService
    ) -> None:
        """Test project creation with all valid difficulty levels."""
        for difficulty in ["beginner", "intermediate", "advanced"]:
            project = project_service.create_project(
                user_id="user-123",
                name=f"Test {difficulty}",
                description="Test",
                mission_type="tutorial",
                difficulty=difficulty,
            )
            assert project.difficulty == difficulty


class TestProjectServiceRetrieve:
    """Test project retrieval in ProjectService."""

    def test_get_project_success(self, project_service: ProjectService) -> None:
        """Test successful project retrieval."""
        created = project_service.create_project(
            user_id="user-123",
            name="Test Mission",
            description="Test",
            mission_type="tutorial",
            difficulty="beginner",
        )

        retrieved = project_service.get_project(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == created.name

    def test_get_project_not_found(self, project_service: ProjectService) -> None:
        """Test retrieval of non-existent project."""
        result = project_service.get_project("non-existent")
        assert result is None


class TestProjectServiceList:
    """Test project listing in ProjectService."""

    def test_list_user_projects(self, project_service: ProjectService) -> None:
        """Test listing projects for a specific user."""
        # Create projects for different users
        project_service.create_project(
            user_id="user-1",
            name="User 1 Project",
            description="Test",
            mission_type="tutorial",
            difficulty="beginner",
        )
        project_service.create_project(
            user_id="user-2",
            name="User 2 Project",
            description="Test",
            mission_type="tutorial",
            difficulty="beginner",
        )
        project_service.create_project(
            user_id="user-1",
            name="User 1 Project 2",
            description="Test",
            mission_type="challenge",
            difficulty="intermediate",
        )

        projects = project_service.list_user_projects("user-1")
        assert len(projects) == 2
        assert all(p.user_id == "user-1" for p in projects)

    def test_list_user_projects_with_type_filter(
        self, project_service: ProjectService
    ) -> None:
        """Test listing user projects with mission type filter."""
        project_service.create_project(
            user_id="user-1",
            name="Tutorial",
            description="Test",
            mission_type="tutorial",
            difficulty="beginner",
        )
        project_service.create_project(
            user_id="user-1",
            name="Challenge",
            description="Test",
            mission_type="challenge",
            difficulty="intermediate",
        )

        projects = project_service.list_user_projects("user-1", mission_type="tutorial")
        assert len(projects) == 1
        assert projects[0].mission_type == "tutorial"

    def test_list_public_projects(self, project_service: ProjectService) -> None:
        """Test listing public projects."""
        project_service.create_project(
            user_id="user-1",
            name="Public Project",
            description="Test",
            mission_type="tutorial",
            difficulty="beginner",
            is_public=True,
        )
        project_service.create_project(
            user_id="user-1",
            name="Private Project",
            description="Test",
            mission_type="tutorial",
            difficulty="beginner",
            is_public=False,
        )
        project_service.create_project(
            user_id="user-2",
            name="Another Public",
            description="Test",
            mission_type="challenge",
            difficulty="intermediate",
            is_public=True,
        )

        public_projects = project_service.list_public_projects()
        assert len(public_projects) == 2
        assert all(p.is_public for p in public_projects)

    def test_list_public_projects_with_type_filter(
        self, project_service: ProjectService
    ) -> None:
        """Test listing public projects with mission type filter."""
        project_service.create_project(
            user_id="user-1",
            name="Public Tutorial",
            description="Test",
            mission_type="tutorial",
            difficulty="beginner",
            is_public=True,
        )
        project_service.create_project(
            user_id="user-2",
            name="Public Challenge",
            description="Test",
            mission_type="challenge",
            difficulty="intermediate",
            is_public=True,
        )

        projects = project_service.list_public_projects(mission_type="tutorial")
        assert len(projects) == 1
        assert projects[0].mission_type == "tutorial"


class TestProjectServiceUpdate:
    """Test project updates in ProjectService."""

    def test_update_project_success(self, project_service: ProjectService) -> None:
        """Test successful project update."""
        project = project_service.create_project(
            user_id="user-123",
            name="Original Name",
            description="Original Description",
            mission_type="tutorial",
            difficulty="beginner",
        )

        project.name = "Updated Name"
        project.description = "Updated Description"
        project_service.update_project(project)

        updated = project_service.get_project(project.id)
        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.description == "Updated Description"
        assert updated.updated_at > updated.created_at

    def test_update_project_empty_name(self, project_service: ProjectService) -> None:
        """Test updating project with empty name raises error."""
        project = project_service.create_project(
            user_id="user-123",
            name="Original",
            description="Test",
            mission_type="tutorial",
            difficulty="beginner",
        )

        project.name = ""
        with pytest.raises(ValueError, match="cannot be empty"):
            project_service.update_project(project)

    def test_update_project_invalid_mission_type(
        self, project_service: ProjectService
    ) -> None:
        """Test updating project with invalid mission type."""
        project = project_service.create_project(
            user_id="user-123",
            name="Test",
            description="Test",
            mission_type="tutorial",
            difficulty="beginner",
        )

        project.mission_type = "invalid"
        with pytest.raises(ValueError, match="Invalid mission type"):
            project_service.update_project(project)

    def test_update_project_invalid_difficulty(
        self, project_service: ProjectService
    ) -> None:
        """Test updating project with invalid difficulty."""
        project = project_service.create_project(
            user_id="user-123",
            name="Test",
            description="Test",
            mission_type="tutorial",
            difficulty="beginner",
        )

        project.difficulty = "invalid"
        with pytest.raises(ValueError, match="Invalid difficulty"):
            project_service.update_project(project)


class TestProjectServiceDelete:
    """Test project deletion in ProjectService."""

    def test_delete_project_success(self, project_service: ProjectService) -> None:
        """Test successful project deletion."""
        project = project_service.create_project(
            user_id="user-123",
            name="To Delete",
            description="Test",
            mission_type="tutorial",
            difficulty="beginner",
        )

        project_service.delete_project(project.id)
        result = project_service.get_project(project.id)
        assert result is None

    def test_delete_project_not_found(self, project_service: ProjectService) -> None:
        """Test deleting non-existent project (should not raise)."""
        # Should not raise an error
        project_service.delete_project("non-existent")


class TestProjectModel:
    """Test Project model methods."""

    def test_add_objective_template(self) -> None:
        """Test adding objective templates to a project."""
        project = Project(
            id="proj-1",
            user_id="user-1",
            name="Test",
            description="Test",
            mission_type="tutorial",
            difficulty="beginner",
        )

        project.add_objective_template(
            description="Reach Mars",
            obj_type="reach",
            target_id="mars",
        )

        assert len(project.objectives) == 1
        assert project.objectives[0]["description"] == "Reach Mars"
        assert project.objectives[0]["type"] == "reach"
        assert project.objectives[0]["target_id"] == "mars"

    def test_update_metadata(self) -> None:
        """Test updating project metadata."""
        project = Project(
            id="proj-1",
            user_id="user-1",
            name="Original",
            description="Original Desc",
            mission_type="tutorial",
            difficulty="beginner",
        )

        original_updated = project.updated_at
        project.update_metadata(name="Updated", description="Updated Desc")

        assert project.name == "Updated"
        assert project.description == "Updated Desc"
        assert project.updated_at > original_updated

    def test_update_metadata_partial(self) -> None:
        """Test updating project metadata with partial updates."""
        project = Project(
            id="proj-1",
            user_id="user-1",
            name="Original",
            description="Original Desc",
            mission_type="tutorial",
            difficulty="beginner",
        )

        project.update_metadata(name="Updated Only Name")

        assert project.name == "Updated Only Name"
        assert project.description == "Original Desc"  # Unchanged
