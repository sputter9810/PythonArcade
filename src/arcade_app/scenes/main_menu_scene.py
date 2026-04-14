from __future__ import annotations

import pygame

from arcade_app.constants import APP_VERSION
from arcade_app.core.scene_base import SceneBase
from arcade_app.registry import get_game_by_id
from arcade_app.ui import theme


class MainMenuScene(SceneBase):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.title_font: pygame.font.Font | None = None
        self.body_font: pygame.font.Font | None = None
        self.meta_font: pygame.font.Font | None = None

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.TITLE_SIZE, bold=True)
        self.body_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.meta_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
                elif event.key == pygame.K_2:
                    from arcade_app.scenes.settings_scene import SettingsScene
                    self.app.scene_manager.go_to(SettingsScene(self.app))
                elif event.key == pygame.K_3:
                    from arcade_app.scenes.credits_scene import CreditsScene
                    self.app.scene_manager.go_to(CreditsScene(self.app))
                elif event.key == pygame.K_ESCAPE:
                    self.app.quit()

    def update(self, dt: float) -> None:
        return

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.body_font is not None
        assert self.meta_font is not None

        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Arcade", True, theme.TEXT)
        subtitle = self.body_font.render(
            "Press 1: Play  |  2: Settings  |  3: Credits  |  Esc: Quit",
            True,
            theme.MUTED_TEXT,
        )
        version = self.meta_font.render(f"Version {APP_VERSION}", True, theme.MUTED_TEXT)

        last_played_id = self.app.save_data.get_last_played_game_id()
        if last_played_id is None:
            last_played_text = "Last Played: None yet"
        else:
            last_played_game = get_game_by_id(last_played_id)
            if last_played_game is not None:
                last_played_label = last_played_game["title"]
            else:
                last_played_label = last_played_id

            last_played_text = f"Last Played: {last_played_label}"

        last_played = self.meta_font.render(last_played_text, True, theme.MUTED_TEXT)

        title_rect = title.get_rect(center=(screen.get_width() // 2, 180))
        subtitle_rect = subtitle.get_rect(center=(screen.get_width() // 2, 260))
        version_rect = version.get_rect(center=(screen.get_width() // 2, 320))
        last_played_rect = last_played.get_rect(center=(screen.get_width() // 2, 355))

        screen.blit(title, title_rect)
        screen.blit(subtitle, subtitle_rect)
        screen.blit(version, version_rect)
        screen.blit(last_played, last_played_rect)