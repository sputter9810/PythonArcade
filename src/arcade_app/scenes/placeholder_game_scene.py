from __future__ import annotations

import pygame

from arcade_app.core.scene_base import SceneBase
from arcade_app.ui import theme


class PlaceholderGameScene(SceneBase):
    def __init__(self, app, game_title: str) -> None:
        super().__init__(app)
        self.game_title = game_title
        self.title_font: pygame.font.Font | None = None
        self.body_font: pygame.font.Font | None = None

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.body_font = pygame.font.SysFont("arial", theme.BODY_SIZE)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from arcade_app.scenes.game_select_scene import GameSelectScene
                self.app.scene_manager.go_to(GameSelectScene(self.app))

    def update(self, dt: float) -> None:
        return

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.body_font is not None

        screen.fill(theme.BACKGROUND)

        title = self.title_font.render(self.game_title, True, theme.TEXT)
        line1 = self.body_font.render("This game is not implemented yet.", True, theme.MUTED_TEXT)
        line2 = self.body_font.render("Press Esc to return to the launcher.", True, theme.MUTED_TEXT)

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 180)))
        screen.blit(line1, line1.get_rect(center=(screen.get_width() // 2, 280)))
        screen.blit(line2, line2.get_rect(center=(screen.get_width() // 2, 330)))