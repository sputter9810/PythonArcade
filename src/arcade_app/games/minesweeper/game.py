from __future__ import annotations

import random
from collections import deque

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class MinesweeperGame(GameBase):
    game_id = "minesweeper"
    title = "Minesweeper"

    ROWS = 12
    COLS = 16
    MINES = 28
    CELL_SIZE = 34

    NUMBER_COLORS = {
        1: (90, 140, 230),
        2: (110, 190, 110),
        3: (230, 90, 90),
        4: (130, 110, 220),
        5: (180, 70, 70),
        6: (70, 170, 170),
        7: (230, 230, 230),
        8: (160, 160, 160),
    }

    def __init__(self, app) -> None:
        super().__init__(app)
        self.ui: GameUI | None = None
        self.number_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1080, 640)
        self.board_rect = pygame.Rect(0, 0, self.COLS * self.CELL_SIZE, self.ROWS * self.CELL_SIZE)

        self.mine_grid: list[list[bool]] = []
        self.revealed: list[list[bool]] = []
        self.flagged: list[list[bool]] = []
        self.adjacent_counts: list[list[int]] = []

        self.first_click_done = False
        self.revealed_count = 0
        self.flags_used = 0
        self.moves = 0

        self.game_over = False
        self.won = False
        self.paused = False

    def enter(self) -> None:
        self.ui = GameUI()
        self.number_font = pygame.font.SysFont("arial", 24, bold=True)
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect((screen.get_width() - 1080) // 2, 165, 1080, 640)
        self.board_rect = pygame.Rect(0, 0, self.COLS * self.CELL_SIZE, self.ROWS * self.CELL_SIZE)
        self.board_rect.center = self.play_rect.center
        self.board_rect.y -= 10

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.mine_grid = [[False for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.revealed = [[False for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.flagged = [[False for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.adjacent_counts = [[0 for _ in range(self.COLS)] for _ in range(self.ROWS)]

        self.first_click_done = False
        self.revealed_count = 0
        self.flags_used = 0
        self.moves = 0

        self.game_over = False
        self.won = False
        self.paused = False

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["hits"] = self.revealed_count
        payload["round"] = self.flags_used
        return payload

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene
        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def neighbors(self, row: int, col: int):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.ROWS and 0 <= nc < self.COLS:
                    yield nr, nc

    def plant_mines(self, safe_row: int, safe_col: int) -> None:
        safe_cells = {(safe_row, safe_col), *set(self.neighbors(safe_row, safe_col))}
        available = [(r, c) for r in range(self.ROWS) for c in range(self.COLS) if (r, c) not in safe_cells]
        for r, c in random.sample(available, self.MINES):
            self.mine_grid[r][c] = True

        for r in range(self.ROWS):
            for c in range(self.COLS):
                if self.mine_grid[r][c]:
                    self.adjacent_counts[r][c] = -1
                else:
                    self.adjacent_counts[r][c] = sum(1 for nr, nc in self.neighbors(r, c) if self.mine_grid[nr][nc])

    def reveal_cell(self, row: int, col: int) -> None:
        if self.revealed[row][col] or self.flagged[row][col]:
            return

        if not self.first_click_done:
            self.first_click_done = True
            self.plant_mines(row, col)

        self.moves += 1

        if self.mine_grid[row][col]:
            self.revealed[row][col] = True
            self.game_over = True
            return

        queue = deque([(row, col)])
        while queue:
            r, c = queue.popleft()
            if self.revealed[r][c] or self.flagged[r][c]:
                continue

            self.revealed[r][c] = True
            self.revealed_count += 1

            if self.adjacent_counts[r][c] == 0:
                for nr, nc in self.neighbors(r, c):
                    if not self.revealed[nr][nc] and not self.mine_grid[nr][nc]:
                        queue.append((nr, nc))

        if self.revealed_count == self.ROWS * self.COLS - self.MINES:
            self.won = True
            self.game_over = True

    def toggle_flag(self, row: int, col: int) -> None:
        if self.revealed[row][col]:
            return
        self.flagged[row][col] = not self.flagged[row][col]
        self.flags_used += 1 if self.flagged[row][col] else -1

    def grid_cell_at(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        if not self.board_rect.collidepoint(pos):
            return None
        col = (pos[0] - self.board_rect.x) // self.CELL_SIZE
        row = (pos[1] - self.board_rect.y) // self.CELL_SIZE
        if 0 <= row < self.ROWS and 0 <= col < self.COLS:
            return int(row), int(col)
        return None

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif self.game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.reset_game()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over or self.paused:
                    if self.game_over and event.button == 1:
                        self.reset_game()
                    continue

                cell = self.grid_cell_at(event.pos)
                if cell is None:
                    continue
                row, col = cell

                if event.button == 1:
                    self.reveal_cell(row, col)
                elif event.button == 3:
                    self.toggle_flag(row, col)

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None
        assert self.number_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "Minesweeper",
            "Left click reveals. Right click flags. Clear every safe cell.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Flags: {self.flags_used}/{self.MINES}",
                f"Revealed: {self.revealed_count}",
                f"Moves: {self.moves}",
            ],
        )

        if self.game_over:
            sub = "Mine triggered." if not self.won else "Board cleared."
        else:
            sub = "Use flags carefully and open safe regions efficiently."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.board_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        for r in range(self.ROWS):
            for c in range(self.COLS):
                rect = pygame.Rect(
                    self.board_rect.x + c * self.CELL_SIZE,
                    self.board_rect.y + r * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE,
                )

                if self.revealed[r][c]:
                    fill = (74, 78, 90)
                else:
                    fill = (92, 96, 108)

                pygame.draw.rect(screen, fill, rect, border_radius=4)
                pygame.draw.rect(screen, theme.SURFACE_ALT, rect, width=1, border_radius=4)

                if self.revealed[r][c]:
                    if self.mine_grid[r][c]:
                        pygame.draw.circle(screen, theme.DANGER, rect.center, 9)
                    else:
                        count = self.adjacent_counts[r][c]
                        if count > 0:
                            text = self.number_font.render(str(count), True, self.NUMBER_COLORS.get(count, theme.TEXT))
                            screen.blit(text, text.get_rect(center=rect.center))
                elif self.flagged[r][c]:
                    pole = pygame.Rect(rect.centerx - 1, rect.y + 8, 3, 18)
                    pygame.draw.rect(screen, theme.TEXT, pole)
                    flag = [(rect.centerx + 1, rect.y + 8), (rect.centerx + 14, rect.y + 14), (rect.centerx + 1, rect.y + 20)]
                    pygame.draw.polygon(screen, theme.WARNING, flag)

        if self.paused and not self.game_over:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.game_over:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "You Win" if self.won else "Game Over",
                f"Revealed Cells: {self.revealed_count}",
                f"Flags Used: {self.flags_used}  |  Moves: {self.moves}",
            )