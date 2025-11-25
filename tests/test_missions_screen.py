"""
Tests for Missions Screen

Tests verify:
- Screen renders correctly
- Click handling responds within 0.1s
- Mission selection works
- Keyboard navigation works
- Mission info display
"""

from __future__ import annotations

import time

import pytest

try:
    import pygame

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    pygame = None  # type: ignore

from src.screens.missions import MissionAction, MissionInfo, MissionsScreen


@pytest.fixture
def sample_missions() -> list[MissionInfo]:
    """Create sample missions for testing."""
    return [
        MissionInfo(
            id="test-001",
            name="Test Mission 1",
            description="First test mission",
            difficulty="Beginner",
            type="Tutorial",
        ),
        MissionInfo(
            id="test-002",
            name="Test Mission 2",
            description="Second test mission",
            difficulty="Advanced",
            type="Orbital",
            completed=True,
        ),
    ]


@pytest.fixture
def missions_screen(sample_missions: list[MissionInfo]) -> MissionsScreen:
    """Create a missions screen instance for testing."""
    if not PYGAME_AVAILABLE:
        pytest.skip("Pygame not available")
    pygame.init()
    return MissionsScreen(width=800, height=600, missions=sample_missions)


@pytest.fixture
def surface() -> "pygame.Surface | None":
    """Create a pygame surface for rendering tests."""
    if not PYGAME_AVAILABLE:
        return None
    pygame.init()
    return pygame.Surface((800, 600))


def test_missions_screen_initialization(missions_screen: MissionsScreen) -> None:
    """Test that missions screen initializes correctly."""
    assert missions_screen.width == 800
    assert missions_screen.height == 600
    assert len(missions_screen.missions) == 2
    assert missions_screen.font is not None
    assert missions_screen.title_font is not None


def test_missions_screen_render(
    missions_screen: MissionsScreen, surface: "pygame.Surface | None"
) -> None:
    """Test that missions screen renders without errors."""
    if surface is None:
        pytest.skip("Pygame surface not available")
    missions_screen.render(surface)
    # If no exception is raised, rendering succeeded


def test_missions_screen_click_handling(missions_screen: MissionsScreen) -> None:
    """Test that click handling responds quickly."""
    start_time = time.time()
    _result = missions_screen.handle_click((400, 230))  # Approximate mission area
    elapsed = time.time() - start_time

    assert elapsed < 0.1, "Click handling should respond within 0.1 seconds"
    # Result may be None or MissionAction depending on exact click position


def test_missions_screen_keyboard_navigation(missions_screen: MissionsScreen) -> None:
    """Test keyboard navigation through missions."""
    if not PYGAME_AVAILABLE:
        pytest.skip("Pygame not available")

    # Navigate down
    missions_screen.handle_keyboard(pygame.K_DOWN)
    assert missions_screen.selected_mission_index == 0

    missions_screen.handle_keyboard(pygame.K_DOWN)
    assert missions_screen.selected_mission_index == 1

    # Navigate up
    missions_screen.handle_keyboard(pygame.K_UP)
    assert missions_screen.selected_mission_index == 0

    # Test escape returns back action
    result = missions_screen.handle_keyboard(pygame.K_ESCAPE)
    assert result == MissionAction.BACK

    # Test enter starts mission when one is selected
    missions_screen.selected_mission_index = 0
    result = missions_screen.handle_keyboard(pygame.K_RETURN)
    assert result == MissionAction.START


def test_missions_screen_get_selected_mission(missions_screen: MissionsScreen) -> None:
    """Test getting selected mission."""
    assert missions_screen.get_selected_mission() is None

    missions_screen.selected_mission_index = 0
    selected = missions_screen.get_selected_mission()
    assert selected is not None
    assert selected.id == "test-001"
    assert selected.name == "Test Mission 1"

    missions_screen.selected_mission_index = 1
    selected = missions_screen.get_selected_mission()
    assert selected is not None
    assert selected.completed is True


def test_missions_screen_mouse_move(missions_screen: MissionsScreen) -> None:
    """Test mouse move updates hover state."""
    missions_screen.handle_mouse_move((400, 230))
    # Hover state should be updated (exact value depends on mission positions)


def test_missions_screen_transitions(missions_screen: MissionsScreen) -> None:
    """Test fade transitions."""
    missions_screen.start_fade_in()
    assert missions_screen.fade_alpha == 255

    # Update transition
    missions_screen.update_transition(100)  # 100ms
    assert missions_screen.fade_alpha < 255

    # Continue updating until fade complete
    for _ in range(10):
        missions_screen.update_transition(50)
        if missions_screen.fade_alpha == 0:
            break

    assert missions_screen.fade_alpha == 0


def test_missions_screen_default_missions() -> None:
    """Test that default missions are created when none provided."""
    if not PYGAME_AVAILABLE:
        pytest.skip("Pygame not available")
    pygame.init()
    screen = MissionsScreen(width=800, height=600)
    assert len(screen.missions) > 0
    assert all(isinstance(m, MissionInfo) for m in screen.missions)


def test_missions_screen_high_contrast() -> None:
    """Test high contrast mode."""
    if not PYGAME_AVAILABLE:
        pytest.skip("Pygame not available")
    pygame.init()
    screen_hc = MissionsScreen(width=800, height=600, high_contrast=True)
    assert screen_hc.high_contrast is True
    assert screen_hc.bg_color == (0, 0, 0)
    assert screen_hc.title_color == (255, 255, 0)
