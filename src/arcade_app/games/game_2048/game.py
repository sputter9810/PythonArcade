from __future__ import annotations

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.games.game_2048.logic import Game2048Logic
from arcade_app.ui import theme


class Game2048(GameBase):
    game_id = "game_2048"
    title = "2048"

    def __init__(self, app) -> None:
        super().__init__(app)
        self.logic = Game2048Logic()

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.tile_font_large: pygame.font.Font | None = None
        self.tile_font_small: pygame.font.Font | None = None

        self.board_rect = pygame.Rect(0, 0, 520, 520)

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.tile_font_large = pygame.font.SysFont("arial", 38, bold=True)
        self.tile_font_small = pygame.font.SysFont("arial", 28, bold=True)

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.board_rect = pygame.Rect(
            (screen.get_width() - 520) // 2,
            170,
            520,
            520,
        )

    def get_status_text(self) -> str:
        if self.logic.is_game_over:
            return "Game Over"
        if self.logic.has_won:
            return "You reached 2048!"
        return "Combine matching tiles"

    def get_tile_color(self, value: int) -> tuple[int, int, int]:
        color_map = {
            0: theme.SURFACE_ALT,
            2: (238, 228, 218),
            4: (237, 224, 200),
            8: (242, 177, 121),
            16: (245, 149, 99),
            32: (246, 124, 95),
            64: (246, 94, 59),
            128: (237, 207, 114),
            256: (237, 204, 97),
            512: (237, 200, 80),
            1024: (237, 197, 63),
            2048: (237, 194, 46),
        }
        return color_map.get(value, (60, 58, 50))

    def get_tile_text_color(self, value: int) -> tuple[int, int, int]:
        if value in (2, 4):
            return (80, 70, 60)
        return theme.TEXT

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
                elif event.key == pygame.K_F5:
                    self.logic.reset()
                    self._submitted_record_keys.clear()
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.logic.move("left")
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.logic.move("right")
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.logic.move("up")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.logic.move("down")

    def update(self, dt: float) -> None:
        return

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.tile_font_large is not None
        assert self.tile_font_small is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        if self.logic.has_won or self.logic.is_game_over:
            self.submit_record_once("best_score", self.logic.score, higher_is_better=True)

        title = self.title_font.render("2048", True, theme.TEXT)
        status = self.info_font.render(self.get_status_text(), True, theme.TEXT)
        score = self.info_font.render(f"Score: {self.logic.score}", True, theme.TEXT)
        controls = self.info_font.render(
            "Arrow Keys / WASD: Move  |  F5: Restart  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 35)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 80)))
        screen.blit(score, score.get_rect(center=(screen.get_width() // 2, 115)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30)))

        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_MEDIUM)

        padding = 12
        tile_size = (self.board_rect.width - padding * 5) // 4

        for row in range(4):
            for col in range(4):
                x = self.board_rect.x + padding + col * (tile_size + padding)
                y = self.board_rect.y + padding + row * (tile_size + padding)
                rect = pygame.Rect(x, y, tile_size, tile_size)

                value = self.logic.grid[row][col]
                pygame.draw.rect(
                    screen,
                    self.get_tile_color(value),
                    rect,
                    border_radius=theme.RADIUS_SMALL,
                )

                if value != 0:
                    text_value = str(value)
                    font = self.tile_font_large if len(text_value) <= 3 else self.tile_font_small
                    text = font.render(text_value, True, self.get_tile_text_color(value))
                    screen.blit(text, text.get_rect(center=rect.center))