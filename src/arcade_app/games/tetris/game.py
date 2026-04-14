from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme


class TetrisGame(GameBase):
    game_id = "tetris"
    title = "Tetris"

    SHAPES = {
        "I": [[1, 1, 1, 1]],
        "O": [[1, 1], [1, 1]],
        "T": [[0, 1, 0], [1, 1, 1]],
        "L": [[1, 0], [1, 0], [1, 1]],
        "J": [[0, 1], [0, 1], [1, 1]],
        "S": [[0, 1, 1], [1, 1, 0]],
        "Z": [[1, 1, 0], [0, 1, 1]],
    }

    COLORS = {
        "I": (100, 220, 220),
        "O": (230, 210, 90),
        "T": (180, 120, 230),
        "L": (230, 150, 90),
        "J": (100, 140, 230),
        "S": (120, 210, 120),
        "Z": (220, 100, 100),
    }

    def __init__(self, app) -> None:
        super().__init__(app)

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None

        self.rows = 20
        self.cols = 10
        self.cell_size = 28

        self.board_rect = pygame.Rect(0, 0, self.cols * self.cell_size, self.rows * self.cell_size)
        self.next_rect = pygame.Rect(0, 0, 180, 180)

        self.grid: list[list[tuple[int, int, int] | None]] = []

        self.current_shape: list[list[int]] = []
        self.current_color: tuple[int, int, int] = theme.ACCENT
        self.current_x = 0
        self.current_y = 0

        self.next_piece_name = ""
        self.next_shape: list[list[int]] = []
        self.next_color: tuple[int, int, int] = theme.ACCENT

        self.drop_timer = 0.0
        self.drop_delay = 0.55
        self.soft_drop_multiplier = 8.0

        self.horizontal_hold_timer = 0.0
        self.horizontal_repeat_delay = 0.10

        self.score = 0
        self.lines_cleared = 0
        self.is_game_over = False

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.reset_game()

    def reset_game(self) -> None:
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.score = 0
        self.lines_cleared = 0
        self.is_game_over = False
        self.drop_timer = 0.0
        self.horizontal_hold_timer = 0.0

        self.roll_next_piece()
        self.spawn_piece()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.board_rect = pygame.Rect(
            (screen.get_width() - self.cols * self.cell_size) // 2 - 60,
            150,
            self.cols * self.cell_size,
            self.rows * self.cell_size,
        )

        self.next_rect = pygame.Rect(
            self.board_rect.right + 40,
            self.board_rect.y + 40,
            180,
            180,
        )

    def roll_next_piece(self) -> None:
        piece_name = random.choice(list(self.SHAPES.keys()))
        self.next_piece_name = piece_name
        self.next_shape = [row[:] for row in self.SHAPES[piece_name]]
        self.next_color = self.COLORS[piece_name]

    def spawn_piece(self) -> None:
        self.current_shape = [row[:] for row in self.next_shape]
        self.current_color = self.next_color
        self.current_x = self.cols // 2 - len(self.current_shape[0]) // 2
        self.current_y = 0

        self.roll_next_piece()

        if self.collides(self.current_x, self.current_y, self.current_shape):
            self.is_game_over = True

    def collides(self, x: int, y: int, shape: list[list[int]]) -> bool:
        for row_idx, row in enumerate(shape):
            for col_idx, value in enumerate(row):
                if not value:
                    continue

                board_x = x + col_idx
                board_y = y + row_idx

                if board_x < 0 or board_x >= self.cols or board_y >= self.rows:
                    return True

                if board_y >= 0 and self.grid[board_y][board_x] is not None:
                    return True

        return False

    def lock_piece(self) -> None:
        for row_idx, row in enumerate(self.current_shape):
            for col_idx, value in enumerate(row):
                if value:
                    board_x = self.current_x + col_idx
                    board_y = self.current_y + row_idx
                    if 0 <= board_y < self.rows:
                        self.grid[board_y][board_x] = self.current_color

        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self) -> None:
        new_grid = []
        cleared = 0

        for row in self.grid:
            if all(cell is not None for cell in row):
                cleared += 1
            else:
                new_grid.append(row)

        while len(new_grid) < self.rows:
            new_grid.insert(0, [None for _ in range(self.cols)])

        self.grid = new_grid
        self.lines_cleared += cleared
        self.score += cleared * 100

    def move_piece(self, dx: int, dy: int) -> bool:
        new_x = self.current_x + dx
        new_y = self.current_y + dy

        if not self.collides(new_x, new_y, self.current_shape):
            self.current_x = new_x
            self.current_y = new_y
            return True
        return False

    def rotate_piece(self) -> None:
        rotated = [list(row) for row in zip(*self.current_shape[::-1])]
        if not self.collides(self.current_x, self.current_y, rotated):
            self.current_shape = rotated

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif not self.is_game_over:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.move_piece(-1, 0)
                        self.horizontal_hold_timer = 0.0
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.move_piece(1, 0)
                        self.horizontal_hold_timer = 0.0
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        if not self.move_piece(0, 1):
                            self.lock_piece()
                    elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
                        self.rotate_piece()

    def update_horizontal_hold(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        left_held = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right_held = keys[pygame.K_RIGHT] or keys[pygame.K_d]

        if left_held ^ right_held:
            self.horizontal_hold_timer += dt
            if self.horizontal_hold_timer >= self.horizontal_repeat_delay:
                self.horizontal_hold_timer = 0.0
                if left_held:
                    self.move_piece(-1, 0)
                elif right_held:
                    self.move_piece(1, 0)
        else:
            self.horizontal_hold_timer = 0.0

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.is_game_over:
            return

        self.update_horizontal_hold(dt)

        keys = pygame.key.get_pressed()
        effective_drop_delay = self.drop_delay
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            effective_drop_delay = self.drop_delay / self.soft_drop_multiplier

        self.drop_timer += dt
        if self.drop_timer >= effective_drop_delay:
            self.drop_timer = 0.0
            if not self.move_piece(0, 1):
                self.lock_piece()

    def draw_cell(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        size: int,
        color: tuple[int, int, int],
    ) -> None:
        rect = pygame.Rect(x, y, size, size)
        pygame.draw.rect(screen, color, rect, border_radius=4)
        pygame.draw.rect(screen, theme.BACKGROUND, rect, width=1, border_radius=4)

    def render_next_piece(self, screen: pygame.Surface) -> None:
        assert self.info_font is not None

        label = self.info_font.render("Next", True, theme.TEXT)
        screen.blit(label, label.get_rect(midbottom=(self.next_rect.centerx, self.next_rect.y - 8)))

        pygame.draw.rect(screen, theme.SURFACE, self.next_rect, border_radius=theme.RADIUS_MEDIUM)

        if not self.next_shape:
            return

        preview_cell = 24
        shape_h = len(self.next_shape)
        shape_w = len(self.next_shape[0])

        total_w = shape_w * preview_cell
        total_h = shape_h * preview_cell

        start_x = self.next_rect.centerx - total_w // 2
        start_y = self.next_rect.centery - total_h // 2

        for row_idx, row in enumerate(self.next_shape):
            for col_idx, value in enumerate(row):
                if value:
                    x = start_x + col_idx * preview_cell
                    y = start_y + row_idx * preview_cell
                    self.draw_cell(screen, x, y, preview_cell, self.next_color)

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Tetris", True, theme.TEXT)
        status_text = "Game Over" if self.is_game_over else "Stack pieces and clear lines"
        status = self.info_font.render(status_text, True, theme.TEXT)
        score = self.info_font.render(f"Score: {self.score}", True, theme.TEXT)
        lines = self.info_font.render(f"Lines: {self.lines_cleared}", True, theme.TEXT)
        controls = self.info_font.render(
            "Move: Arrow Keys / WASD  |  Hold Down: Soft Drop  |  Rotate: Up/W/Space  |  F5: Restart  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 35)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 80)))
        screen.blit(score, score.get_rect(center=(screen.get_width() // 2 - 120, 115)))
        screen.blit(lines, lines.get_rect(center=(screen.get_width() // 2 + 120, 115)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30)))

        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_MEDIUM)

        for row in range(self.rows):
            for col in range(self.cols):
                x = self.board_rect.x + col * self.cell_size
                y = self.board_rect.y + row * self.cell_size

                color = self.grid[row][col]
                if color is not None:
                    self.draw_cell(screen, x, y, self.cell_size, color)
                else:
                    rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                    pygame.draw.rect(screen, theme.SURFACE_ALT, rect, width=1, border_radius=4)

        if not self.is_game_over:
            for row_idx, row in enumerate(self.current_shape):
                for col_idx, value in enumerate(row):
                    if value:
                        x = self.board_rect.x + (self.current_x + col_idx) * self.cell_size
                        y = self.board_rect.y + (self.current_y + row_idx) * self.cell_size
                        self.draw_cell(screen, x, y, self.cell_size, self.current_color)

        self.render_next_piece(screen)