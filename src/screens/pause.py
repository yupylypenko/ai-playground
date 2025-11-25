"""
Pause Screen

Pause menu screen for the Cosmic Flight Simulator.
Displayed when the game is paused during gameplay.

This implementation:
- Mirrors MainMenuScreen pattern for consistency
- Displays pause menu options
- Provides visual feedback for selections
- Uses the same theme and starfield background
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Tuple

import pygame


class PauseOption(Enum):
    """Available pause menu options"""

    RESUME = "Resume"
    RESTART = "Restart Mission"
    SETTINGS = "Settings"
    MAIN_MENU = "Main Menu"
    QUIT = "Quit"


class PauseScreen:
    """
    Pause screen for the Cosmic Flight Simulator.

    Displays pause menu options when the game is paused.
    Designed to respond within 0.1 seconds per performance requirements.

    Attributes:
        width: Screen width in pixels
        height: Screen height in pixels
        selected_option: Currently selected pause option
        font: Font for rendering text
        title_font: Font for rendering the title
    """

    def __init__(
        self,
        width: int = 1280,
        height: int = 720,
        *,
        fullscreen: bool = False,
        font_scale: float = 1.0,
        high_contrast: bool = False,
        enable_sounds: bool = False,
    ) -> None:
        """
        Initialize the pause screen.

        Args:
            width: Screen width in pixels
            height: Screen height in pixels
            fullscreen: Whether screen is in fullscreen mode
            font_scale: Font scaling factor (0.75-2.0)
            high_contrast: Enable high contrast colors
            enable_sounds: Enable audio feedback
        """
        self.fullscreen = fullscreen
        self.width = width
        self.height = height
        self.selected_option: Optional[PauseOption] = None
        self.hover_option: Optional[PauseOption] = None
        self.font: Optional[pygame.font.Font] = None
        self.title_font: Optional[pygame.font.Font] = None
        self.font_scale = max(0.75, min(2.0, font_scale))
        self.high_contrast = high_contrast
        self.enable_sounds = enable_sounds

        # Theme colors
        if self.high_contrast:
            self.bg_color = (0, 0, 0)
            self.title_color = (255, 255, 0)
            self.text_color = (255, 255, 255)
            self.highlight_color = (0, 255, 255)
            self.overlay_color = (0, 0, 0, 180)  # Semi-transparent overlay
        else:
            self.bg_color = (5, 5, 15)
            self.title_color = (240, 240, 255)
            self.text_color = (200, 200, 200)
            self.highlight_color = (100, 200, 255)
            self.overlay_color = (0, 0, 0, 180)  # Semi-transparent overlay

        # Transition alpha (0=opaque content, 255=black overlay)
        self.fade_alpha = 0

        # Starfield background: (x, y, speed)
        self.stars: List[Tuple[float, float, float]] = []
        self._initialize_fonts()
        self._initialize_starfield()
        self._initialize_audio()

    def _initialize_fonts(self) -> None:
        """Initialize pygame fonts for pause menu rendering."""
        try:
            pygame.font.init()
            base_small = int(32 * self.font_scale)
            base_large = int(72 * self.font_scale)
            self.font = pygame.font.Font(None, base_small)
            self.title_font = pygame.font.Font(None, base_large)
        except Exception as e:
            print(f"Warning: Could not initialize fonts: {e}")
            self.font = None
            self.title_font = None

    def _initialize_starfield(self) -> None:
        """Create a simple starfield with varying speeds for parallax."""
        import random

        num_stars = max(100, (self.width * self.height) // 15000)
        self.stars = [
            (
                random.uniform(0, self.width),
                random.uniform(0, self.height),
                random.uniform(0.3, 1.2),
            )
            for _ in range(num_stars)
        ]

    def _initialize_audio(self) -> None:
        """Initialize audio system optionally for click/hover sounds."""
        if not self.enable_sounds:
            self.click_sound = None
            self.hover_sound = None
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.click_sound = None  # Placeholder for future asset
            self.hover_sound = None  # Placeholder for future asset
        except Exception as e:
            print(f"Warning: Could not initialize audio: {e}")
            self.click_sound = None
            self.hover_sound = None

    def render(self, surface: pygame.Surface) -> None:
        """
        Render the pause screen to the given surface.

        Args:
            surface: Pygame surface to render to
        """
        # Note: In a real game, the game screen would be rendered first,
        # then this pause overlay would be rendered on top

        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # Background starfield (subtle)
        self._render_starfield(surface, alpha=100)

        if not self.font or not self.title_font:
            return

        # Render title
        title_text = self.title_font.render("PAUSED", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.width // 2, 200))
        surface.blit(title_text, title_rect)

        # Render pause menu options
        pause_options = [
            PauseOption.RESUME,
            PauseOption.RESTART,
            PauseOption.SETTINGS,
            PauseOption.MAIN_MENU,
            PauseOption.QUIT,
        ]

        start_y = 350
        spacing = int(60 * self.font_scale)

        for i, option in enumerate(pause_options):
            y_pos = start_y + (i * spacing)

            # Hover/selection feedback
            if option == self.selected_option:
                color = self.highlight_color
            elif option == self.hover_option:
                color = (
                    min(self.highlight_color[0] + 20, 255),
                    min(self.highlight_color[1] + 20, 255),
                    min(self.highlight_color[2] + 20, 255),
                )
            else:
                color = self.text_color

            option_text = self.font.render(option.value, True, color)
            option_rect = option_text.get_rect(center=(self.width // 2, y_pos))
            surface.blit(option_text, option_rect)

        # Fade overlay for transitions
        if self.fade_alpha > 0:
            fade_overlay = pygame.Surface((self.width, self.height))
            fade_overlay.set_alpha(self.fade_alpha)
            fade_overlay.fill((0, 0, 0))
            surface.blit(fade_overlay, (0, 0))

    def _render_starfield(self, surface: pygame.Surface, alpha: int = 255) -> None:
        """Render and update a simple starfield background."""
        for idx, (x, y, speed) in enumerate(self.stars):
            # Star brightness scales with speed
            c = max(120, min(255, int(180 + speed * 60)))
            # Apply alpha for subtle effect
            star_surface = pygame.Surface((2, 2))
            star_surface.set_alpha(alpha)
            star_surface.fill((c, c, c))
            surface.blit(star_surface, (int(x), int(y)))

            # Move star downward for a subtle drift
            y += speed
            if y >= self.height:
                y = 0
            self.stars[idx] = (x, y, speed)

    def handle_click(self, pos: tuple[int, int]) -> Optional[PauseOption]:
        """
        Handle mouse click on the pause screen.

        Designed to respond within 0.1 seconds per performance requirements.

        Args:
            pos: Mouse position (x, y)

        Returns:
            Selected PauseOption if click was on a menu item, None otherwise
        """
        x, y = pos

        pause_options = [
            PauseOption.RESUME,
            PauseOption.RESTART,
            PauseOption.SETTINGS,
            PauseOption.MAIN_MENU,
            PauseOption.QUIT,
        ]

        start_y = 350
        spacing = int(60 * self.font_scale)
        option_width = int(260 * self.font_scale)
        option_height = int(44 * self.font_scale)

        for i, option in enumerate(pause_options):
            option_y = start_y + (i * spacing)

            # Check if click is within option bounds
            if (
                self.width // 2 - option_width // 2
                <= x
                <= self.width // 2 + option_width // 2
                and option_y - option_height // 2 <= y <= option_y + option_height // 2
            ):
                self.selected_option = option
                if self.click_sound:
                    try:
                        self.click_sound.play()
                    except Exception:
                        pass
                return option

        return None

    def handle_keyboard(self, key: int) -> Optional[PauseOption]:
        """
        Handle keyboard input for pause menu navigation.

        Args:
            key: Pygame key code

        Returns:
            Selected PauseOption if Enter/Space/Escape was pressed, None otherwise
        """
        pause_options = [
            PauseOption.RESUME,
            PauseOption.RESTART,
            PauseOption.SETTINGS,
            PauseOption.MAIN_MENU,
            PauseOption.QUIT,
        ]

        if key == pygame.K_UP:
            if self.selected_option is None:
                self.selected_option = pause_options[0]
            else:
                current_index = pause_options.index(self.selected_option)
                self.selected_option = pause_options[
                    (current_index - 1) % len(pause_options)
                ]
            if self.hover_sound:
                try:
                    self.hover_sound.play()
                except Exception:
                    pass
        elif key == pygame.K_DOWN:
            if self.selected_option is None:
                self.selected_option = pause_options[0]
            else:
                current_index = pause_options.index(self.selected_option)
                self.selected_option = pause_options[
                    (current_index + 1) % len(pause_options)
                ]
            if self.hover_sound:
                try:
                    self.hover_sound.play()
                except Exception:
                    pass
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            return self.selected_option if self.selected_option else PauseOption.RESUME
        elif key == pygame.K_ESCAPE:
            return PauseOption.RESUME

        return None

    def handle_mouse_move(self, pos: tuple[int, int]) -> None:
        """Update hover state based on mouse position."""
        x, y = pos
        pause_options = [
            PauseOption.RESUME,
            PauseOption.RESTART,
            PauseOption.SETTINGS,
            PauseOption.MAIN_MENU,
            PauseOption.QUIT,
        ]
        start_y = 350
        spacing = int(60 * self.font_scale)
        option_width = int(260 * self.font_scale)
        option_height = int(44 * self.font_scale)

        new_hover: Optional[PauseOption] = None
        for i, option in enumerate(pause_options):
            option_y = start_y + (i * spacing)
            if (
                self.width // 2 - option_width // 2
                <= x
                <= self.width // 2 + option_width // 2
                and option_y - option_height // 2 <= y <= option_y + option_height // 2
            ):
                new_hover = option
                break
        self.hover_option = new_hover

    def set_fullscreen(self, surface: pygame.Surface, enable: bool) -> pygame.Surface:
        """Toggle fullscreen, returning the new display surface."""
        if enable == self.fullscreen:
            return surface
        self.fullscreen = enable
        flags = pygame.FULLSCREEN if enable else 0
        display_info = pygame.display.Info()
        self.width = display_info.current_w if enable else self.width
        self.height = display_info.current_h if enable else self.height
        return pygame.display.set_mode((self.width, self.height), flags)

    def start_fade_in(self) -> None:
        """Begin a fade-in effect."""
        self.fade_alpha = 255

    def update_transition(self, dt_ms: int) -> None:
        """Update transition alpha based on elapsed time in ms."""
        if self.fade_alpha <= 0:
            return
        # Fade in over ~250ms
        self.fade_alpha = max(0, self.fade_alpha - int(255 * (dt_ms / 250.0)))

    def get_selected_option(self) -> Optional[PauseOption]:
        """
        Get the currently selected pause option.

        Returns:
            Currently selected PauseOption or None
        """
        return self.selected_option

    def reset(self) -> None:
        """Reset pause screen state."""
        self.selected_option = None
        self.hover_option = None
