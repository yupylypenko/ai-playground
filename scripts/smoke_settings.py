import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys
import time
import pygame

# Allow running from repo root or script dir
REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(REPO_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from screens.settings import SettingsScreen, SettingsCategory  # noqa: E402


def main() -> int:
    pygame.init()
    try:
        width, height = 800, 600
        screen = pygame.display.set_mode((width, height))
        settings = SettingsScreen(width=width, height=height, font_scale=1.0, high_contrast=False)

        # Initial render
        settings.start_fade_in()
        settings.update_transition(0)
        settings.render(screen)

        # Simulate mouse move to hover over first option
        settings.handle_mouse_move((width // 2, 350))
        settings.render(screen)

        # Simulate click on first option
        selected = settings.handle_click((width // 2, 350))
        assert selected in (SettingsCategory.DISPLAY, None)

        # Update fade for 250ms worth
        settings.update_transition(250)
        settings.render(screen)

        # Save a screenshot artifact in tmp
        out_path = os.path.join(REPO_ROOT, "smoke_settings.png")
        pygame.image.save(screen, out_path)
        print(f"Smoke test OK. Screenshot saved to: {out_path}")
        return 0
    finally:
        pygame.quit()


if __name__ == "__main__":
    raise SystemExit(main())

