from __future__ import annotations

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.games.minesweeper.logic import MinesweeperLogic
from arcade_app.ui import theme


class MinesweeperGame(GameBase):
    game_id = "minesweeper"
    title = "Minesweeper"

    def __init__(self, app) -> None:
        super().__init__(app)
        self.logic = MinesweeperLogic()

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.cell_font: pygame.font.Font | None = None

        self.board_rect = pygame.Rect(0, 0, 640, 640)
        self.cell_rects: list[list[pygame.Rect]] = []

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.cell_font = pygame.font.SysFont("arial", 24, bold=True)

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.board_rect = pygame.Rect(
            (screen.get_width() - 640) // 2,
            150,
            640,
            640,
        )

        padding = 6
        cell_size = (self.board_rect.width - padding * 11) // 10

        self.cell_rects = []
        for row in range(10):
            rect_row = []
            for col in range(10):
                x = self.board_rect.x + padding + col * (cell_size + padding)
                y = self.board_rect.y + padding + row * (cell_size + padding)
                rect_row.append(pygame.Rect(x, y, cell_size, cell_size))
            self.cell_rects.append(rect_row)

    def get_status_text(self) -> str:
        if self.logic.is_won:
            return "You cleared the minefield!"
        if self.logic.is_game_over:
            return "Boom! You hit a mine."
        return "Left click: reveal  |  Right click: flag"

    def get_number_color(self, value: int) -> tuple[int, int, int]:
        colors = {
            1: (100, 170, 255),
            2: (120, 220, 140),
            3: (255, 110, 110),
            4: (180, 130, 255),
            5: (255, 170, 90),
            6: (90, 220, 220),
            7: (230, 230, 230),
            8: (180, 180, 180),
        }
        return colors.get(value, theme.TEXT)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
                elif event.key == pygame.K_F5:
                    self.logic.reset()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                for row in range(10):
                    for col in range(10):
                        rect = self.cell_rects[row][col]
                        if rect.collidepoint(mouse_pos):
                            if event.button == 1:
                                self.logic.reveal(row, col)
                            elif event.button == 3:
                                self.logic.toggle_flag(row, col)
                            return

    def update(self, dt: float) -> None:
        return

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.cell_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Minesweeper", True, theme.TEXT)
        status = self.info_font.render(self.get_status_text(), True, theme.TEXT)
        flags = self.info_font.render(
            f"Flags: {self.logic.get_flag_count()} / {self.logic.MINE_COUNT}",
            True,
            theme.TEXT,
        )
        controls = self.info_font.render(
            "Left click: Reveal  |  Right click: Flag  |  F5: Restart  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 35)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 80)))
        screen.blit(flags, flags.get_rect(center=(screen.get_width() // 2, 115)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30)))

        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_MEDIUM)

        for row in range(10):
            for col in range(10):
                rect = self.cell_rects[row][col]
                revealed = self.logic.revealed[row][col]
                flagged = self.logic.flagged[row][col]
                is_mine = (row, col) in self.logic.mines
                count = self.logic.adjacent_counts[row][col]

                if revealed:
                    fill = theme.SURFACE_ALT
                else:
                    fill = theme.SURFACE

                if self.logic.is_game_over and is_mine:
                    fill = theme.DANGER

                pygame.draw.rect(screen, fill, rect, border_radius=theme.RADIUS_SMALL)

                if flagged and not revealed:
                    text = self.cell_font.render("F", True, theme.WARNING)
                    screen.blit(text, text.get_rect(center=rect.center))
                elif revealed:
                    if is_mine:
                        text = self.cell_font.render("*", True, theme.TEXT)
                        screen.blit(text, text.get_rect(center=rect.center))
                    elif count > 0:
                        text = self.cell_font.render(str(count), True, self.get_number_color(count))
                        screen.blit(text, text.get_rect(center=rect.center))