from __future__ import annotations

import pygame

from arcade_app.constants import APP_VERSION
from arcade_app.core.scene_base import SceneBase
from arcade_app.ui import theme


class CreditsScene(SceneBase):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.title_font: pygame.font.Font | None = None
        self.heading_font: pygame.font.Font | None = None
        self.body_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.heading_font = pygame.font.SysFont("arial", 28, bold=True)
        self.body_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.small_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.main_menu_scene import MainMenuScene
                    self.app.scene_manager.go_to(MainMenuScene(self.app))

    def update(self, dt: float) -> None:
        return

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.heading_font is not None
        assert self.body_font is not None
        assert self.small_font is not None

        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Credits", True, theme.TEXT)
        subtitle = self.small_font.render(
            f"Arcade v{APP_VERSION}",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 60)))
        screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() // 2, 95)))

        panel = pygame.Rect(
            (screen.get_width() - 900) // 2,
            145,
            900,
            520,
        )
        pygame.draw.rect(screen, theme.SURFACE, panel, border_radius=theme.RADIUS_LARGE)

        sections = [
            (
                "Created By",
                [
                    "Sam Briggs",
                    "Design, development, UI polish, packaging, and iteration.",
                ],
            ),
            (
                "Project",
                [
                    "Python Arcade is a desktop mini-game collection built with Python and Pygame.",
                    "It includes a launcher, persistent settings, saved stats, and a scalable scene-based structure.",
                ],
            ),
            (
                "Special Thanks",
                [
                    "OpenAI ChatGPT for implementation support, iteration help, debugging assistance, and planning.",
                    "The open-source Python and Pygame communities.",
                ],
            ),
            (
                "Included Games",
                [
                    "Tic Tac Toe, Hangman, Snake, Connect 4, Battleships, Pong, Breakout, Memory Match, 2048, Whac-A-Mole, Space Invaders, Asteroids, Sudoku, Minesweeper, Tetris, Simon Says",
                ],
            ),
        ]

        current_y = panel.y + 28
        left_x = panel.x + 32

        for heading, lines in sections:
            heading_surface = self.heading_font.render(heading, True, theme.TEXT)
            screen.blit(heading_surface, (left_x, current_y))
            current_y += 36

            for line in lines:
                wrapped_lines = self.wrap_text(line, self.body_font, panel.width - 64)
                for wrapped in wrapped_lines:
                    line_surface = self.body_font.render(wrapped, True, theme.MUTED_TEXT)
                    screen.blit(line_surface, (left_x, current_y))
                    current_y += 28

            current_y += 18

        footer = self.small_font.render("Esc: Back to Main Menu", True, theme.MUTED_TEXT)
        screen.blit(footer, footer.get_rect(center=(screen.get_width() // 2, screen.get_height() - 35)))

    def wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        words = text.split()
        if not words:
            return [""]

        lines: list[str] = []
        current = words[0]

        for word in words[1:]:
            test = f"{current} {word}"
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = word

        lines.append(current)
        return lines