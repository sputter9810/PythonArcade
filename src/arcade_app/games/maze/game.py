from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme


class MazeGame(GameBase):
    game_id = "maze"
    title = "Maze"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 760, 760)

        self.rows = 21
        self.cols = 21
        self.cell_size = 32

        self.grid: list[list[int]] = []
        self.player_cell = (1, 1)
        self.exit_cell = (self.rows - 2, self.cols - 2)

        self.steps = 0
        self.is_won = False

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.small_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE)
        self.reset_game()

    def reset_game(self) -> None:
        self.grid = self.generate_maze(self.rows, self.cols)
        self.player_cell = (1, 1)
        self.exit_cell = (self.rows - 2, self.cols - 2)
        self.steps = 0
        self.is_won = False

        # Ensure exit is open
        self.grid[self.exit_cell[0]][self.exit_cell[1]] = 0

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        board_size = min(screen.get_height() - 220, screen.get_width() - 260)
        board_size = max(420, board_size)

        self.cell_size = board_size // self.cols
        board_width = self.cols * self.cell_size
        board_height = self.rows * self.cell_size

        self.play_rect = pygame.Rect(
            (screen.get_width() - board_width) // 2,
            130,
            board_width,
            board_height,
        )

    def generate_maze(self, rows: int, cols: int) -> list[list[int]]:
        grid = [[1 for _ in range(cols)] for _ in range(rows)]

        def carve_passages(start_r: int, start_c: int) -> None:
            stack = [(start_r, start_c)]
            grid[start_r][start_c] = 0

            while stack:
                r, c = stack[-1]

                neighbors = []
                directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
                random.shuffle(directions)

                for dr, dc in directions:
                    nr = r + dr
                    nc = c + dc
                    if 1 <= nr < rows - 1 and 1 <= nc < cols - 1 and grid[nr][nc] == 1:
                        neighbors.append((nr, nc, dr, dc))

                if neighbors:
                    nr, nc, dr, dc = neighbors[0]
                    wall_r = r + dr // 2
                    wall_c = c + dc // 2

                    grid[wall_r][wall_c] = 0
                    grid[nr][nc] = 0
                    stack.append((nr, nc))
                else:
                    stack.pop()

        carve_passages(1, 1)

        # Ensure end area is reachable/open
        grid[rows - 2][cols - 2] = 0
        if grid[rows - 2][cols - 3] == 1 and grid[rows - 3][cols - 2] == 1:
            grid[rows - 2][cols - 3] = 0

        return grid

    def can_move_to(self, row: int, col: int) -> bool:
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False
        return self.grid[row][col] == 0

    def try_move(self, dr: int, dc: int) -> None:
        if self.is_won:
            return

        row, col = self.player_cell
        new_row = row + dr
        new_col = col + dc

        if self.can_move_to(new_row, new_col):
            self.player_cell = (new_row, new_col)
            self.steps += 1

            if self.player_cell == self.exit_cell:
                self.is_won = True

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                from arcade_app.scenes.game_select_scene import GameSelectScene
                self.app.scene_manager.go_to(GameSelectScene(self.app))
            elif event.key == pygame.K_F5:
                self.reset_game()
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.try_move(-1, 0)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.try_move(1, 0)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.try_move(0, -1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.try_move(0, 1)

    def update(self, dt: float) -> None:
        return

    def draw_maze(self, screen: pygame.Surface) -> None:
        for row in range(self.rows):
            for col in range(self.cols):
                x = self.play_rect.x + col * self.cell_size
                y = self.play_rect.y + row * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                if self.grid[row][col] == 1:
                    pygame.draw.rect(screen, theme.SURFACE_ALT, rect)
                else:
                    pygame.draw.rect(screen, theme.SURFACE, rect)

        # Exit
        exit_x = self.play_rect.x + self.exit_cell[1] * self.cell_size
        exit_y = self.play_rect.y + self.exit_cell[0] * self.cell_size
        exit_rect = pygame.Rect(exit_x, exit_y, self.cell_size, self.cell_size)
        pygame.draw.rect(screen, theme.SUCCESS, exit_rect, border_radius=6)

        # Player
        player_x = self.play_rect.x + self.player_cell[1] * self.cell_size + self.cell_size // 2
        player_y = self.play_rect.y + self.player_cell[0] * self.cell_size + self.cell_size // 2
        pygame.draw.circle(
            screen,
            theme.ACCENT,
            (player_x, player_y),
            max(6, self.cell_size // 3),
        )

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.small_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Maze", True, theme.TEXT)

        if self.is_won:
            status_text = "You escaped!"
        else:
            status_text = "Find the exit"

        status = self.info_font.render(status_text, True, theme.TEXT)
        steps = self.info_font.render(f"Steps: {self.steps}", True, theme.TEXT)
        controls = self.info_font.render(
            "Move: WASD / Arrows  |  F5: New Maze  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        legend_start = self.small_font.render("Start: Blue", True, theme.MUTED_TEXT)
        legend_exit = self.small_font.render("Exit: Green", True, theme.MUTED_TEXT)

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 32)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 75)))
        screen.blit(steps, steps.get_rect(center=(screen.get_width() // 2, 108)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 28)))
        screen.blit(legend_start, legend_start.get_rect(midleft=(self.play_rect.left, 108)))
        screen.blit(legend_exit, legend_exit.get_rect(midright=(self.play_rect.right, 108)))

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        self.draw_maze(screen)

        if self.is_won:
            win_text = self.title_font.render("Victory!", True, theme.TEXT)
            replay = self.info_font.render("Press F5 for a new maze", True, theme.MUTED_TEXT)
            screen.blit(win_text, win_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 18)))
            screen.blit(replay, replay.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 22)))