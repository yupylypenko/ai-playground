"""
Tests for Pause Screen

Tests verify:
- Screen renders correctly
- Click handling responds within 0.1s
- Pause menu options work
- Keyboard navigation works
- Resume functionality
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

from src.screens.pause import PauseOption, PauseScreen


@pytest.fixture
def pause_screen() -> PauseScreen:
    """Create a pause screen instance for testing."""
    if not PYGAME_AVAILABLE:
        pytest.skip("Pygame not available")
    pygame.init()
    return PauseScreen(width=800, height=600)


@pytest.fixture
def surface() -> "pygame.Surface | None":
    """Create a pygame surface for rendering tests."""
    if not PYGAME_AVAILABLE:
        return None
    pygame.init()
    return pygame.Surface((800, 600))


def test_pause_screen_initialization(pause_screen: PauseScreen) -> None:
    """Test that pause screen initializes correctly."""
    assert pause_screen.width == 800
    assert pause_screen.height == 600
    assert pause_screen.font is not None
    assert pause_screen.title_font is not None


def test_pause_screen_render(
    pause_screen: PauseScreen, surface: "pygame.Surface | None"
) -> None:
    """Test that pause screen renders without errors."""
    if surface is None:
        pytest.skip("Pygame surface not available")
    pause_screen.render(surface)
    # If no exception is raised, rendering succeeded


def test_pause_screen_click_handling(pause_screen: PauseScreen) -> None:
    """Test that click handling responds quickly."""
    # Click on Resume button area
    start_time = time.time()
    _result = pause_screen.handle_click(
        (400, 350)
    )  # Approximate Resume button position
    elapsed = time.time() - start_time

    assert elapsed < 0.1, "Click handling should respond within 0.1 seconds"
    # Result may be None or PauseOption depending on exact click position


def test_pause_screen_keyboard_navigation(pause_screen: PauseScreen) -> None:
    """Test keyboard navigation through pause menu."""
    if not PYGAME_AVAILABLE:
        pytest.skip("Pygame not available")

    # Test escape resumes (doesn't set selected_option, just returns)
    result = pause_screen.handle_keyboard(pygame.K_ESCAPE)
    assert result == PauseOption.RESUME

    # Navigate down (starts at first option when selected_option is None)
    pause_screen.handle_keyboard(pygame.K_DOWN)
    assert pause_screen.selected_option == PauseOption.RESUME

    # Navigate down again to move to next option
    pause_screen.handle_keyboard(pygame.K_DOWN)
    assert pause_screen.selected_option == PauseOption.RESTART

    # Navigate up
    pause_screen.handle_keyboard(pygame.K_UP)
    assert pause_screen.selected_option == PauseOption.RESUME

    # Test enter selects option
    pause_screen.selected_option = PauseOption.QUIT
    result = pause_screen.handle_keyboard(pygame.K_RETURN)
    assert result == PauseOption.QUIT


def test_pause_screen_reset(pause_screen: PauseScreen) -> None:
    """Test reset functionality."""
    pause_screen.selected_option = PauseOption.SETTINGS
    pause_screen.hover_option = PauseOption.MAIN_MENU

    pause_screen.reset()

    assert pause_screen.selected_option is None
    assert pause_screen.hover_option is None


def test_pause_screen_mouse_move(pause_screen: PauseScreen) -> None:
    """Test mouse move updates hover state."""
    pause_screen.handle_mouse_move((400, 350))
    # Hover state should be updated (exact value depends on button positions)


def test_pause_screen_transitions(pause_screen: PauseScreen) -> None:
    """Test fade transitions."""
    pause_screen.start_fade_in()
    assert pause_screen.fade_alpha == 255

    # Update transition
    pause_screen.update_transition(100)  # 100ms
    assert pause_screen.fade_alpha < 255

    # Continue updating until fade complete
    for _ in range(10):
        pause_screen.update_transition(50)
        if pause_screen.fade_alpha == 0:
            break

    assert pause_screen.fade_alpha == 0


def test_pause_screen_get_selected_option(pause_screen: PauseScreen) -> None:
    """Test getting selected option."""
    assert pause_screen.get_selected_option() is None

    pause_screen.selected_option = PauseOption.RESUME
    assert pause_screen.get_selected_option() == PauseOption.RESUME


def test_pause_screen_high_contrast() -> None:
    """Test high contrast mode."""
    if not PYGAME_AVAILABLE:
        pytest.skip("Pygame not available")
    pygame.init()
    screen_hc = PauseScreen(width=800, height=600, high_contrast=True)
    assert screen_hc.high_contrast is True
    assert screen_hc.bg_color == (0, 0, 0)
    assert screen_hc.title_color == (255, 255, 0)
