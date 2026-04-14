from __future__ import annotations

import pygame

from arcade_app.config import AppConfig
from arcade_app.constants import APP_TITLE, APP_VERSION
from arcade_app.core.save_data import SaveDataManager
from arcade_app.core.scene_manager import SceneManager
from arcade_app.scenes.main_menu_scene import MainMenuScene


class ArcadeApp:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.save_data = SaveDataManager(app_name="PythonArcade")

        loaded_settings = self.save_data.get_settings()

        base_config = config or AppConfig()
        base_config.fullscreen = bool(loaded_settings.get("fullscreen", False))
        base_config.sound_enabled = bool(loaded_settings.get("sound_enabled", True))
        base_config.music_enabled = bool(loaded_settings.get("music_enabled", True))

        self.config = base_config
        self.running = True
        self.screen: pygame.Surface | None = None
        self.clock: pygame.time.Clock | None = None

        self.scene_manager = SceneManager(self)

    def setup(self) -> None:
        pygame.init()
        self.apply_display_mode()
        pygame.display.set_caption(f"{APP_TITLE} v{APP_VERSION}")
        self.clock = pygame.time.Clock()
        self.scene_manager.go_to(MainMenuScene(self))

    def apply_display_mode(self) -> None:
        flags = pygame.FULLSCREEN if self.config.fullscreen else 0
        self.screen = pygame.display.set_mode((self.config.width, self.config.height), flags)

    def update_setting(self, key: str, value) -> None:
        if hasattr(self.config, key):
            setattr(self.config, key, value)

        self.save_data.set_setting(key, value)

        if key == "fullscreen":
            self.apply_display_mode()
            pygame.display.set_caption(f"{APP_TITLE} v{APP_VERSION}")

    def run(self) -> None:
        self.setup()
        assert self.screen is not None
        assert self.clock is not None

        while self.running:
            dt = self.clock.tick(self.config.fps) / 1000.0
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.scene_manager.handle_events(events)

            assert self.screen is not None
            self.scene_manager.update(dt)
            self.scene_manager.render(self.screen)
            pygame.display.flip()

        pygame.quit()

    def quit(self) -> None:
        self.running = False


def main() -> None:
    ArcadeApp().run()