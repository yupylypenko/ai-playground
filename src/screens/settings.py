"""
Settings Screen

Configuration screen for the Cosmic Flight Simulator.
Allows users to adjust display, audio, controls, and accessibility settings.

This implementation:
- Mirrors MainMenuScreen pattern for consistency
- Displays settings categories and options
- Provides visual feedback for selections
- Uses the same theme and starfield background
"""

from __future__ import annotations

from enum import Enum
from typing import Optional, List, Tuple

import pygame


class SettingsCategory(Enum):
    """Available settings categories"""
    DISPLAY = "Display"
    AUDIO = "Audio"
    CONTROLS = "Controls"
    ACCESSIBILITY = "Accessibility"
    BACK = "Back to Main Menu"


class SettingsScreen:
    """
    Settings screen for the Cosmic Flight Simulator.
    
    Displays settings categories and handles navigation.
    Designed to respond within 0.1 seconds per performance requirements.
    
    Attributes:
        width: Screen width in pixels
        height: Screen height in pixels
        selected_category: Currently selected settings category
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
        Initialize the settings screen.

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
        self.selected_category: Optional[SettingsCategory] = None
        self.hover_category: Optional[SettingsCategory] = None
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
        else:
            self.bg_color = (5, 5, 15)
            self.title_color = (240, 240, 255)
            self.text_color = (200, 200, 200)
            self.highlight_color = (100, 200, 255)

        # Transition alpha (0=opaque content, 255=black overlay)
        self.fade_alpha = 0

        # Starfield background: (x, y, speed)
        self.stars: List[Tuple[float, float, float]] = []
        self._initialize_fonts()
        self._initialize_starfield()
        self._initialize_audio()

    def _initialize_fonts(self) -> None:
        """Initialize pygame fonts for menu rendering."""
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
        Render the settings screen to the given surface.

        Args:
            surface: Pygame surface to render to
        """
        # Background
        surface.fill(self.bg_color)
        self._render_starfield(surface)

        if not self.font or not self.title_font:
            return

        # Render title
        title_text = self.title_font.render(
            "Settings",
            True,
            self.title_color
        )
        title_rect = title_text.get_rect(center=(self.width // 2, 150))
        surface.blit(title_text, title_rect)

        # Render settings categories
        categories = [
            SettingsCategory.DISPLAY,
            SettingsCategory.AUDIO,
            SettingsCategory.CONTROLS,
            SettingsCategory.ACCESSIBILITY,
            SettingsCategory.BACK,
        ]

        start_y = 350
        spacing = int(60 * self.font_scale)

        for i, category in enumerate(categories):
            y_pos = start_y + (i * spacing)

            # Hover/selection feedback
            if category == self.selected_category:
                color = self.highlight_color
            elif category == self.hover_category:
                color = (
                    min(self.highlight_color[0] + 20, 255),
                    min(self.highlight_color[1] + 20, 255),
                    min(self.highlight_color[2] + 20, 255),
                )
            else:
                color = self.text_color

            category_text = self.font.render(category.value, True, color)
            category_rect = category_text.get_rect(center=(self.width // 2, y_pos))
            surface.blit(category_text, category_rect)

        # Fade overlay for transitions
        if self.fade_alpha > 0:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(self.fade_alpha)
            overlay.fill((0, 0, 0))
            surface.blit(overlay, (0, 0))

    def _render_starfield(self, surface: pygame.Surface) -> None:
        """Render and update a simple starfield background."""
        for idx, (x, y, speed) in enumerate(self.stars):
            # Star brightness scales with speed
            c = max(120, min(255, int(180 + speed * 60)))
            surface.fill((c, c, c), rect=pygame.Rect(int(x), int(y), 2, 2))

            # Move star downward for a subtle drift
            y += speed
            if y >= self.height:
                y = 0
            self.stars[idx] = (x, y, speed)

    def handle_click(self, pos: tuple[int, int]) -> Optional[SettingsCategory]:
        """
        Handle mouse click on the settings screen.

        Designed to respond within 0.1 seconds per performance requirements.

        Args:
            pos: Mouse position (x, y)

        Returns:
            Selected SettingsCategory if click was on a category, None otherwise
        """
        x, y = pos

        categories = [
            SettingsCategory.DISPLAY,
            SettingsCategory.AUDIO,
            SettingsCategory.CONTROLS,
            SettingsCategory.ACCESSIBILITY,
            SettingsCategory.BACK,
        ]

        start_y = 350
        spacing = int(60 * self.font_scale)
        option_width = int(260 * self.font_scale)
        option_height = int(44 * self.font_scale)

        for i, category in enumerate(categories):
            option_y = start_y + (i * spacing)

            # Check if click is within option bounds
            if (self.width // 2 - option_width // 2 <= x <= self.width // 2 + option_width // 2 and
                    option_y - option_height // 2 <= y <= option_y + option_height // 2):
                self.selected_category = category
                if self.click_sound:
                    try:
                        self.click_sound.play()
                    except Exception:
                        pass
                return category

        return None

    def handle_keyboard(self, key: int) -> Optional[SettingsCategory]:
        """
        Handle keyboard input for settings navigation.

        Args:
            key: Pygame key code

        Returns:
            Selected SettingsCategory if Enter/Space was pressed, None otherwise
        """
        categories = [
            SettingsCategory.DISPLAY,
            SettingsCategory.AUDIO,
            SettingsCategory.CONTROLS,
            SettingsCategory.ACCESSIBILITY,
            SettingsCategory.BACK,
        ]

        if key == pygame.K_UP:
            if self.selected_category is None:
                self.selected_category = categories[0]
            else:
                current_index = categories.index(self.selected_category)
                self.selected_category = categories[(current_index - 1) % len(categories)]
            if self.hover_sound:
                try:
                    self.hover_sound.play()
                except Exception:
                    pass
        elif key == pygame.K_DOWN:
            if self.selected_category is None:
                self.selected_category = categories[0]
            else:
                current_index = categories.index(self.selected_category)
                self.selected_category = categories[(current_index + 1) % len(categories)]
            if self.hover_sound:
                try:
                    self.hover_sound.play()
                except Exception:
                    pass
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            return self.selected_category if self.selected_category else categories[0]
        elif key == pygame.K_ESCAPE:
            return SettingsCategory.BACK

        return None

    def handle_mouse_move(self, pos: tuple[int, int]) -> None:
        """Update hover state based on mouse position."""
        x, y = pos
        categories = [
            SettingsCategory.DISPLAY,
            SettingsCategory.AUDIO,
            SettingsCategory.CONTROLS,
            SettingsCategory.ACCESSIBILITY,
            SettingsCategory.BACK,
        ]
        start_y = 350
        spacing = int(60 * self.font_scale)
        option_width = int(260 * self.font_scale)
        option_height = int(44 * self.font_scale)

        new_hover: Optional[SettingsCategory] = None
        for i, category in enumerate(categories):
            option_y = start_y + (i * spacing)
            if (
                    self.width // 2 - option_width // 2 <= x <= self.width // 2 + option_width // 2
                    and option_y - option_height // 2 <= y <= option_y + option_height // 2
            ):
                new_hover = category
                break
        self.hover_category = new_hover

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

    def get_selected_category(self) -> Optional[SettingsCategory]:
        """
        Get the currently selected settings category.

        Returns:
            Currently selected SettingsCategory or None
        """
        return self.selected_category

