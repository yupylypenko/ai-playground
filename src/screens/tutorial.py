"""
Tutorial Screen

Interactive tutorial screen for the Cosmic Flight Simulator.
Provides step-by-step guidance for new players learning the game.

This implementation:
- Mirrors MainMenuScreen pattern for consistency
- Displays tutorial steps and navigation
- Provides visual feedback for selections
- Uses the same theme and starfield background
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Tuple

import pygame


class TutorialAction(Enum):
    """Available tutorial actions"""

    NEXT = "Next"
    PREVIOUS = "Previous"
    SKIP = "Skip Tutorial"
    BACK = "Back to Main Menu"


class TutorialScreen:
    """
    Tutorial screen for the Cosmic Flight Simulator.

    Displays tutorial content and handles navigation through tutorial steps.
    Designed to respond within 0.1 seconds per performance requirements.

    Attributes:
        width: Screen width in pixels
        height: Screen height in pixels
        current_step: Current tutorial step index
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
        Initialize the tutorial screen.

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
        self.current_step = 0
        self.selected_action: Optional[TutorialAction] = None
        self.hover_action: Optional[TutorialAction] = None
        self.font: Optional[pygame.font.Font] = None
        self.title_font: Optional[pygame.font.Font] = None
        self.body_font: Optional[pygame.font.Font] = None
        self.font_scale = max(0.75, min(2.0, font_scale))
        self.high_contrast = high_contrast
        self.enable_sounds = enable_sounds

        # Tutorial steps
        self.tutorial_steps: List[Tuple[str, str]] = [
            (
                "Welcome to Cosmic Flight Simulator",
                "Learn the basics of space flight and navigation. Use arrow keys or mouse to navigate.",
            ),
            (
                "Controls",
                "WASD or Arrow Keys: Thrust\nSpace: Fire thrusters\nMouse: Rotate camera\nESC: Pause menu",
            ),
            (
                "Navigation",
                "Use your instruments to track your position. The HUD shows speed, fuel, and altitude.",
            ),
            (
                "Missions",
                "Complete missions to earn rewards. Each mission has objectives you must complete.",
            ),
            (
                "Ready to Fly!",
                "You're ready to start your journey. Select a mission or try free flight mode.",
            ),
        ]

        # Theme colors
        if self.high_contrast:
            self.bg_color = (0, 0, 0)
            self.title_color = (255, 255, 0)
            self.text_color = (255, 255, 255)
            self.highlight_color = (0, 255, 255)
            self.body_color = (255, 255, 255)
        else:
            self.bg_color = (5, 5, 15)
            self.title_color = (240, 240, 255)
            self.text_color = (200, 200, 200)
            self.highlight_color = (100, 200, 255)
            self.body_color = (180, 180, 200)

        # Transition alpha (0=opaque content, 255=black overlay)
        self.fade_alpha = 0

        # Starfield background: (x, y, speed)
        self.stars: List[Tuple[float, float, float]] = []
        self._initialize_fonts()
        self._initialize_starfield()
        self._initialize_audio()

    def _initialize_fonts(self) -> None:
        """Initialize pygame fonts for tutorial rendering."""
        try:
            pygame.font.init()
            base_small = int(32 * self.font_scale)
            base_medium = int(24 * self.font_scale)
            base_large = int(72 * self.font_scale)
            self.font = pygame.font.Font(None, base_small)
            self.body_font = pygame.font.Font(None, base_medium)
            self.title_font = pygame.font.Font(None, base_large)
        except Exception as e:
            print(f"Warning: Could not initialize fonts: {e}")
            self.font = None
            self.body_font = None
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
        Render the tutorial screen to the given surface.

        Args:
            surface: Pygame surface to render to
        """
        # Background
        surface.fill(self.bg_color)
        self._render_starfield(surface)

        if not self.font or not self.title_font or not self.body_font:
            return

        # Render title
        title_text = self.title_font.render("Tutorial", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.width // 2, 100))
        surface.blit(title_text, title_rect)

        # Render current tutorial step
        if 0 <= self.current_step < len(self.tutorial_steps):
            step_title, step_content = self.tutorial_steps[self.current_step]

            # Render step title
            step_title_text = self.font.render(step_title, True, self.text_color)
            step_title_rect = step_title_text.get_rect(center=(self.width // 2, 250))
            surface.blit(step_title_text, step_title_rect)

            # Render step content (multi-line)
            lines = step_content.split("\n")
            start_y = 320
            line_spacing = int(35 * self.font_scale)
            for i, line in enumerate(lines):
                if line.strip():
                    line_text = self.body_font.render(line, True, self.body_color)
                    line_rect = line_text.get_rect(
                        center=(self.width // 2, start_y + (i * line_spacing))
                    )
                    surface.blit(line_text, line_rect)

            # Render step indicator
            step_indicator = (
                f"Step {self.current_step + 1} of {len(self.tutorial_steps)}"
            )
            indicator_text = self.body_font.render(
                step_indicator, True, self.text_color
            )
            indicator_rect = indicator_text.get_rect(
                center=(self.width // 2, self.height - 200)
            )
            surface.blit(indicator_text, indicator_rect)

        # Render navigation buttons
        actions = []
        if self.current_step > 0:
            actions.append(TutorialAction.PREVIOUS)
        if self.current_step < len(self.tutorial_steps) - 1:
            actions.append(TutorialAction.NEXT)
        else:
            actions.append(TutorialAction.BACK)
        actions.append(TutorialAction.SKIP)

        button_start_y = self.height - 120
        button_spacing = int(120 * self.font_scale)
        button_start_x = self.width // 2 - ((len(actions) - 1) * button_spacing // 2)

        for i, action in enumerate(actions):
            x_pos = button_start_x + (i * button_spacing)

            # Hover/selection feedback
            if action == self.selected_action:
                color = self.highlight_color
            elif action == self.hover_action:
                color = (
                    min(self.highlight_color[0] + 20, 255),
                    min(self.highlight_color[1] + 20, 255),
                    min(self.highlight_color[2] + 20, 255),
                )
            else:
                color = self.text_color

            action_text = self.font.render(action.value, True, color)
            action_rect = action_text.get_rect(center=(x_pos, button_start_y))
            surface.blit(action_text, action_rect)

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

    def handle_click(self, pos: tuple[int, int]) -> Optional[TutorialAction]:
        """
        Handle mouse click on the tutorial screen.

        Designed to respond within 0.1 seconds per performance requirements.

        Args:
            pos: Mouse position (x, y)

        Returns:
            Selected TutorialAction if click was on an action button, None otherwise
        """
        x, y = pos

        actions = []
        if self.current_step > 0:
            actions.append(TutorialAction.PREVIOUS)
        if self.current_step < len(self.tutorial_steps) - 1:
            actions.append(TutorialAction.NEXT)
        else:
            actions.append(TutorialAction.BACK)
        actions.append(TutorialAction.SKIP)

        button_start_y = self.height - 120
        button_spacing = int(120 * self.font_scale)
        button_start_x = self.width // 2 - ((len(actions) - 1) * button_spacing // 2)
        button_width = int(140 * self.font_scale)
        button_height = int(44 * self.font_scale)

        for i, action in enumerate(actions):
            button_x = button_start_x + (i * button_spacing)

            # Check if click is within button bounds
            if (
                button_x - button_width // 2 <= x <= button_x + button_width // 2
                and button_start_y - button_height // 2
                <= y
                <= button_start_y + button_height // 2
            ):
                self.selected_action = action
                if self.click_sound:
                    try:
                        self.click_sound.play()
                    except Exception:
                        pass

                # Handle action
                if action == TutorialAction.NEXT:
                    if self.current_step < len(self.tutorial_steps) - 1:
                        self.current_step += 1
                elif action == TutorialAction.PREVIOUS:
                    if self.current_step > 0:
                        self.current_step -= 1
                elif action == TutorialAction.SKIP:
                    return TutorialAction.BACK

                return action

        return None

    def handle_keyboard(self, key: int) -> Optional[TutorialAction]:
        """
        Handle keyboard input for tutorial navigation.

        Args:
            key: Pygame key code

        Returns:
            Selected TutorialAction if Enter/Space/Escape was pressed, None otherwise
        """
        if key == pygame.K_RIGHT or key == pygame.K_RETURN or key == pygame.K_SPACE:
            if self.current_step < len(self.tutorial_steps) - 1:
                self.current_step += 1
                return TutorialAction.NEXT
            else:
                return TutorialAction.BACK
        elif key == pygame.K_LEFT:
            if self.current_step > 0:
                self.current_step -= 1
                return TutorialAction.PREVIOUS
        elif key == pygame.K_ESCAPE:
            return TutorialAction.BACK

        return None

    def handle_mouse_move(self, pos: tuple[int, int]) -> None:
        """Update hover state based on mouse position."""
        x, y = pos

        actions = []
        if self.current_step > 0:
            actions.append(TutorialAction.PREVIOUS)
        if self.current_step < len(self.tutorial_steps) - 1:
            actions.append(TutorialAction.NEXT)
        else:
            actions.append(TutorialAction.BACK)
        actions.append(TutorialAction.SKIP)

        button_start_y = self.height - 120
        button_spacing = int(120 * self.font_scale)
        button_start_x = self.width // 2 - ((len(actions) - 1) * button_spacing // 2)
        button_width = int(140 * self.font_scale)
        button_height = int(44 * self.font_scale)

        new_hover: Optional[TutorialAction] = None
        for i, action in enumerate(actions):
            button_x = button_start_x + (i * button_spacing)
            if (
                button_x - button_width // 2 <= x <= button_x + button_width // 2
                and button_start_y - button_height // 2
                <= y
                <= button_start_y + button_height // 2
            ):
                new_hover = action
                break
        self.hover_action = new_hover

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

    def get_current_step(self) -> int:
        """
        Get the current tutorial step index.

        Returns:
            Current step index (0-based)
        """
        return self.current_step

    def reset(self) -> None:
        """Reset tutorial to the first step."""
        self.current_step = 0
        self.selected_action = None
        self.hover_action = None

