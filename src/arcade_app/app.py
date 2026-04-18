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
        self.achievement_popups: list[dict] = []
        self.popup_title_font: pygame.font.Font | None = None
        self.popup_body_font: pygame.font.Font | None = None

    def setup(self) -> None:
        pygame.init()
        self.apply_display_mode()
        pygame.display.set_caption(f"{APP_TITLE} v{APP_VERSION}")
        self.clock = pygame.time.Clock()
        self.popup_title_font = pygame.font.SysFont("arial", 22, bold=True)
        self.popup_body_font = pygame.font.SysFont("arial", 16)
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

            newly_unlocked = self.save_data.consume_pending_achievement_unlocks()
            if newly_unlocked:
                self.enqueue_achievement_popups(newly_unlocked)

            assert self.screen is not None
            self.scene_manager.update(dt)
            self.scene_manager.render(self.screen)
            self.render_achievement_popups(self.screen)
            pygame.display.flip()

        pygame.quit()

    def enqueue_achievement_popups(self, achievements: list[dict]) -> None:
        now = pygame.time.get_ticks()
        for index, achievement in enumerate(achievements[:4]):
            self.achievement_popups.append(
                {
                    "id": achievement.get("id"),
                    "name": achievement.get("name", "Achievement Unlocked"),
                    "description": achievement.get("description", ""),
                    "category": achievement.get("category", "Achievement"),
                    "expires_at": now + 4500 + index * 250,
                }
            )

    def render_achievement_popups(self, screen: pygame.Surface) -> None:
        if self.popup_title_font is None or self.popup_body_font is None:
            return

        now = pygame.time.get_ticks()
        self.achievement_popups = [popup for popup in self.achievement_popups if popup["expires_at"] > now]

        base_x = screen.get_width() - 360
        base_y = 28
        gap = 12

        for index, popup in enumerate(self.achievement_popups[:4]):
            rect = pygame.Rect(base_x, base_y + index * (102 + gap), 320, 102)
            alpha_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            alpha_surface.fill((18, 24, 34, 228))
            screen.blit(alpha_surface, rect.topleft)
            pygame.draw.rect(screen, (255, 208, 84), rect, width=2, border_radius=16)
            pygame.draw.rect(screen, (255, 208, 84), pygame.Rect(rect.x, rect.y, 8, rect.height), border_radius=16)

            title = self.popup_title_font.render("Achievement Unlocked!", True, (255, 208, 84))
            name = self.popup_title_font.render(str(popup["name"])[:26], True, (240, 244, 252))
            category = self.popup_body_font.render(str(popup["category"])[:34], True, (170, 182, 201))
            description = self.popup_body_font.render(str(popup["description"])[:42], True, (205, 214, 228))

            screen.blit(title, title.get_rect(topleft=(rect.x + 20, rect.y + 10)))
            screen.blit(name, name.get_rect(topleft=(rect.x + 20, rect.y + 38)))
            screen.blit(category, category.get_rect(topleft=(rect.x + 20, rect.y + 66)))
            screen.blit(description, description.get_rect(topleft=(rect.x + 20, rect.y + 84)))

    def quit(self) -> None:
        self.running = False


def main() -> None:
    ArcadeApp().run()