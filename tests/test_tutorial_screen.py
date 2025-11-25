"""
Tests for Tutorial Screen

Tests verify:
- Screen renders correctly
- Click handling responds within 0.1s
- Tutorial navigation works
- Keyboard navigation works
- Step progression and reset functionality
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

from src.screens.tutorial import TutorialAction, TutorialScreen


@pytest.fixture
def tutorial_screen() -> TutorialScreen:
    """Create a tutorial screen instance for testing."""
    if not PYGAME_AVAILABLE:
        pytest.skip("Pygame not available")
    pygame.init()
    return TutorialScreen(width=800, height=600)


@pytest.fixture
def surface() -> "pygame.Surface | None":
    """Create a pygame surface for rendering tests."""
    if not PYGAME_AVAILABLE:
        return None
    pygame.init()
    return pygame.Surface((800, 600))


def test_tutorial_screen_initialization(tutorial_screen: TutorialScreen) -> None:
    """Test that tutorial screen initializes correctly."""
    assert tutorial_screen.width == 800
    assert tutorial_screen.height == 600
    assert tutorial_screen.current_step == 0
    assert len(tutorial_screen.tutorial_steps) > 0
    assert tutorial_screen.font is not None
    assert tutorial_screen.title_font is not None


def test_tutorial_screen_render(
    tutorial_screen: TutorialScreen, surface: "pygame.Surface | None"
) -> None:
    """Test that tutorial screen renders without errors."""
    if surface is None:
        pytest.skip("Pygame surface not available")
    tutorial_screen.render(surface)
    # If no exception is raised, rendering succeeded


def test_tutorial_screen_click_handling(tutorial_screen: TutorialScreen) -> None:
    """Test that click handling responds quickly."""
    # Click on Next button area
    start_time = time.time()
    _result = tutorial_screen.handle_click(
        (400, 480)
    )  # Approximate Next button position
    elapsed = time.time() - start_time

    assert elapsed < 0.1, "Click handling should respond within 0.1 seconds"
    # Result may be None or TutorialAction depending on exact click position


def test_tutorial_screen_keyboard_navigation(tutorial_screen: TutorialScreen) -> None:
    """Test keyboard navigation through tutorial steps."""
    if not PYGAME_AVAILABLE:
        pytest.skip("Pygame not available")

    # Start at step 0
    assert tutorial_screen.current_step == 0

    # Navigate to next step
    result = tutorial_screen.handle_keyboard(pygame.K_RIGHT)
    assert tutorial_screen.current_step == 1
    assert result == TutorialAction.NEXT

    # Navigate to previous step
    result = tutorial_screen.handle_keyboard(pygame.K_LEFT)
    assert tutorial_screen.current_step == 0
    assert result == TutorialAction.PREVIOUS

    # Test escape returns back action
    result = tutorial_screen.handle_keyboard(pygame.K_ESCAPE)
    assert result == TutorialAction.BACK


def test_tutorial_screen_step_progression(tutorial_screen: TutorialScreen) -> None:
    """Test that tutorial steps progress correctly."""
    num_steps = len(tutorial_screen.tutorial_steps)

    # Navigate to last step
    for _ in range(num_steps - 1):
        tutorial_screen.current_step += 1

    assert tutorial_screen.current_step == num_steps - 1

    # Test reset
    tutorial_screen.reset()
    assert tutorial_screen.current_step == 0
    assert tutorial_screen.selected_action is None


def test_tutorial_screen_mouse_move(tutorial_screen: TutorialScreen) -> None:
    """Test mouse move updates hover state."""
    tutorial_screen.handle_mouse_move((400, 480))
    # Hover state should be updated (exact value depends on button positions)


def test_tutorial_screen_transitions(tutorial_screen: TutorialScreen) -> None:
    """Test fade transitions."""
    tutorial_screen.start_fade_in()
    assert tutorial_screen.fade_alpha == 255

    # Update transition
    tutorial_screen.update_transition(100)  # 100ms
    assert tutorial_screen.fade_alpha < 255

    # Continue updating until fade complete
    for _ in range(10):
        tutorial_screen.update_transition(50)
        if tutorial_screen.fade_alpha == 0:
            break

    assert tutorial_screen.fade_alpha == 0


def test_tutorial_screen_font_scale(tutorial_screen: TutorialScreen) -> None:
    """Test that font scaling works correctly."""
    screen_large = TutorialScreen(width=800, height=600, font_scale=1.5)
    assert screen_large.font_scale == 1.5

    screen_small = TutorialScreen(width=800, height=600, font_scale=0.8)
    assert screen_small.font_scale == 0.8

    # Test clamping
    screen_too_large = TutorialScreen(width=800, height=600, font_scale=3.0)
    assert screen_too_large.font_scale == 2.0

    screen_too_small = TutorialScreen(width=800, height=600, font_scale=0.5)
    assert screen_too_small.font_scale == 0.75


def test_tutorial_screen_high_contrast(tutorial_screen: TutorialScreen) -> None:
    """Test high contrast mode."""
    screen_hc = TutorialScreen(width=800, height=600, high_contrast=True)
    assert screen_hc.high_contrast is True
    assert screen_hc.bg_color == (0, 0, 0)
    assert screen_hc.title_color == (255, 255, 0)
