from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.core.run_result import RunResult
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class TetrisGame(GameBase):
    game_id = "tetris"
    title = "Tetris"

    BOARD_WIDTH = 10
    BOARD_HEIGHT = 20
    CELL_SIZE = 30

    MOVE_REPEAT_DELAY = 0.15
    MOVE_REPEAT_INTERVAL = 0.06
    SOFT_DROP_MULTIPLIER = 10.0

    SHAPES = {
        "I": [[1, 1, 1, 1]],
        "O": [[1, 1], [1, 1]],
        "T": [[0, 1, 0], [1, 1, 1]],
        "S": [[0, 1, 1], [1, 1, 0]],
        "Z": [[1, 1, 0], [0, 1, 1]],
        "J": [[1, 0, 0], [1, 1, 1]],
        "L": [[0, 0, 1], [1, 1, 1]],
    }

    SHAPE_COLORS = {
        "I": (80, 220, 220),
        "O": (240, 220, 90),
        "T": (190, 120, 240),
        "S": (110, 210, 120),
        "Z": (230, 90, 90),
        "J": (90, 140, 230),
        "L": (240, 160, 80),
    }

    def __init__(self, app) -> None:
        super().__init__(app)

        self.ui: GameUI | None = None

        self.play_rect = pygame.Rect(0, 0, 1100, 640)
        self.board_rect = pygame.Rect(0, 0, self.BOARD_WIDTH * self.CELL_SIZE, self.BOARD_HEIGHT * self.CELL_SIZE)
        self.next_rect = pygame.Rect(0, 0, 180, 180)

        self.board: list[list[tuple[int, int, int] | None]] = []
        self.current_piece: dict | None = None
        self.next_piece: dict | None = None

        self.score = 0
        self.lines = 0
        self.level = 1

        self.fall_timer = 0.0

        self.game_over = False
        self.paused = False
        self.result_submitted = False

        self.left_held = False
        self.right_held = False
        self.soft_drop_held = False

        self.left_repeat_timer = 0.0
        self.right_repeat_timer = 0.0

    def enter(self) -> None:
        self.ui = GameUI()
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(
            (screen.get_width() - 1100) // 2,
            165,
            1100,
            640,
        )
        self.board_rect = pygame.Rect(
            self.play_rect.left + 120,
            self.play_rect.top + 20,
            self.BOARD_WIDTH * self.CELL_SIZE,
            self.BOARD_HEIGHT * self.CELL_SIZE,
        )
        self.next_rect = pygame.Rect(
            self.board_rect.right + 90,
            self.board_rect.top + 40,
            180,
            180,
        )

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.board = [[None for _ in range(self.BOARD_WIDTH)] for _ in range(self.BOARD_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.fall_timer = 0.0
        self.game_over = False
        self.paused = False
        self.result_submitted = False

        self.left_held = False
        self.right_held = False
        self.soft_drop_held = False
        self.left_repeat_timer = 0.0
        self.right_repeat_timer = 0.0

        self.current_piece = self.create_piece()
        self.next_piece = self.create_piece()

        if not self.valid_position(self.current_piece, self.current_piece["x"], self.current_piece["y"]):
            self.game_over = True
            self.submit_run_result()

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["lines"] = self.lines
        payload["round"] = self.level
        return payload

    def create_piece(self) -> dict:
        kind = random.choice(list(self.SHAPES.keys()))
        shape = [row[:] for row in self.SHAPES[kind]]
        width = len(shape[0])
        return {
            "kind": kind,
            "shape": shape,
            "color": self.SHAPE_COLORS[kind],
            "x": self.BOARD_WIDTH // 2 - width // 2,
            "y": 0,
        }

    def valid_position(self, piece: dict, x: int, y: int, shape: list[list[int]] | None = None) -> bool:
        test_shape = shape if shape is not None else piece["shape"]

        for row_index, row in enumerate(test_shape):
            for col_index, value in enumerate(row):
                if not value:
                    continue

                board_x = x + col_index
                board_y = y + row_index

                if board_x < 0 or board_x >= self.BOARD_WIDTH:
                    return False
                if board_y >= self.BOARD_HEIGHT:
                    return False
                if board_y >= 0 and self.board[board_y][board_x] is not None:
                    return False

        return True

    def rotate_shape(self, shape: list[list[int]]) -> list[list[int]]:
        return [list(row) for row in zip(*shape[::-1])]

    def hard_drop(self) -> None:
        if self.current_piece is None or self.game_over or self.paused:
            return

        while self.valid_position(self.current_piece, self.current_piece["x"], self.current_piece["y"] + 1):
            self.current_piece["y"] += 1
            self.score += 2

        self.lock_piece()

    def rotate_piece(self) -> None:
        if self.current_piece is None or self.game_over or self.paused:
            return

        rotated = self.rotate_shape(self.current_piece["shape"])
        px = self.current_piece["x"]
        py = self.current_piece["y"]

        for offset in (0, -1, 1, -2, 2):
            if self.valid_position(self.current_piece, px + offset, py, rotated):
                self.current_piece["shape"] = rotated
                self.current_piece["x"] = px + offset
                return

    def move_piece(self, dx: int, dy: int) -> bool:
        if self.current_piece is None:
            return False

        new_x = self.current_piece["x"] + dx
        new_y = self.current_piece["y"] + dy

        if self.valid_position(self.current_piece, new_x, new_y):
            self.current_piece["x"] = new_x
            self.current_piece["y"] = new_y
            return True

        return False

    def submit_run_result(self) -> None:
        if self.result_submitted:
            return

        self.result_submitted = True

        result = RunResult(
            game_id="tetris",
            score=self.score,
            metadata={
                "lines": self.lines,
                "level": self.level,
            },
        )

        self.app.save_data.submit_run_result(result)

    def lock_piece(self) -> None:
        if self.current_piece is None:
            return

        for row_index, row in enumerate(self.current_piece["shape"]):
            for col_index, value in enumerate(row):
                if not value:
                    continue
                board_x = self.current_piece["x"] + col_index
                board_y = self.current_piece["y"] + row_index
                if 0 <= board_y < self.BOARD_HEIGHT:
                    self.board[board_y][board_x] = self.current_piece["color"]

        cleared = self.clear_lines()
        if cleared > 0:
            self.lines += cleared
            self.level = 1 + self.lines // 10
            self.score += {1: 100, 2: 300, 3: 500, 4: 800}.get(cleared, cleared * 200) * self.level

        self.current_piece = self.next_piece
        self.next_piece = self.create_piece()
        self.fall_timer = 0.0

        if self.current_piece is not None and not self.valid_position(self.current_piece, self.current_piece["x"], self.current_piece["y"]):
            self.game_over = True
            self.submit_run_result()

    def clear_lines(self) -> int:
        remaining_rows = [row for row in self.board if any(cell is None for cell in row)]
        cleared = self.BOARD_HEIGHT - len(remaining_rows)

        while len(remaining_rows) < self.BOARD_HEIGHT:
            remaining_rows.insert(0, [None for _ in range(self.BOARD_WIDTH)])

        self.board = remaining_rows
        return cleared

    def current_fall_delay(self) -> float:
        return max(0.08, 0.62 - (self.level - 1) * 0.045)

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene

        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def start_left_hold(self) -> None:
        moved = self.move_piece(-1, 0)
        self.left_held = True
        self.right_held = False
        self.left_repeat_timer = self.MOVE_REPEAT_DELAY if moved else self.MOVE_REPEAT_INTERVAL
        self.right_repeat_timer = 0.0

    def start_right_hold(self) -> None:
        moved = self.move_piece(1, 0)
        self.right_held = True
        self.left_held = False
        self.right_repeat_timer = self.MOVE_REPEAT_DELAY if moved else self.MOVE_REPEAT_INTERVAL
        self.left_repeat_timer = 0.0

    def stop_left_hold(self) -> None:
        self.left_held = False
        self.left_repeat_timer = 0.0

    def stop_right_hold(self) -> None:
        self.right_held = False
        self.right_repeat_timer = 0.0

    def stop_soft_drop(self) -> None:
        self.soft_drop_held = False

    def update_horizontal_repeat(self, dt: float) -> None:
        if self.left_held:
            self.left_repeat_timer -= dt
            while self.left_repeat_timer <= 0:
                moved = self.move_piece(-1, 0)
                self.left_repeat_timer += self.MOVE_REPEAT_INTERVAL
                if not moved:
                    self.left_repeat_timer = self.MOVE_REPEAT_INTERVAL
                    break

        if self.right_held:
            self.right_repeat_timer -= dt
            while self.right_repeat_timer <= 0:
                moved = self.move_piece(1, 0)
                self.right_repeat_timer += self.MOVE_REPEAT_INTERVAL
                if not moved:
                    self.right_repeat_timer = self.MOVE_REPEAT_INTERVAL
                    break

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
                elif not self.paused and not self.game_over:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.start_left_hold()
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.start_right_hold()
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.soft_drop_held = True
                        if self.move_piece(0, 1):
                            self.score += 1
                    elif event.key in (pygame.K_UP, pygame.K_q, pygame.K_e):
                        self.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        self.hard_drop()

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.stop_left_hold()
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.stop_right_hold()
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.stop_soft_drop()

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.paused or self.game_over or self.current_piece is None:
            return

        self.update_horizontal_repeat(dt)

        fall_speed = self.SOFT_DROP_MULTIPLIER if self.soft_drop_held else 1.0
        self.fall_timer += dt * fall_speed

        fall_delay = self.current_fall_delay()
        while self.fall_timer >= fall_delay:
            self.fall_timer -= fall_delay
            moved = self.move_piece(0, 1)
            if moved:
                if self.soft_drop_held:
                    self.score += 1
            else:
                self.lock_piece()
                break

    def draw_board(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.board_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        for row in range(self.BOARD_HEIGHT):
            for col in range(self.BOARD_WIDTH):
                cell_rect = pygame.Rect(
                    self.board_rect.x + col * self.CELL_SIZE,
                    self.board_rect.y + row * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE,
                )
                pygame.draw.rect(screen, theme.SURFACE_ALT, cell_rect, width=1, border_radius=3)

                cell = self.board[row][col]
                if cell is not None:
                    inner = cell_rect.inflate(-4, -4)
                    pygame.draw.rect(screen, cell, inner, border_radius=6)

    def draw_piece(self, screen: pygame.Surface, piece: dict, offset_x: int, offset_y: int, preview: bool = False) -> None:
        shape = piece["shape"]
        color = piece["color"]

        for row_index, row in enumerate(shape):
            for col_index, value in enumerate(row):
                if not value:
                    continue

                if preview:
                    x = offset_x + col_index * self.CELL_SIZE
                    y = offset_y + row_index * self.CELL_SIZE
                else:
                    x = self.board_rect.x + (piece["x"] + col_index) * self.CELL_SIZE
                    y = self.board_rect.y + (piece["y"] + row_index) * self.CELL_SIZE

                cell_rect = pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE)
                inner = cell_rect.inflate(-4, -4)
                pygame.draw.rect(screen, color, inner, border_radius=6)

    def draw_ghost_piece(self, screen: pygame.Surface) -> None:
        if self.current_piece is None:
            return

        ghost_y = self.current_piece["y"]
        while self.valid_position(self.current_piece, self.current_piece["x"], ghost_y + 1):
            ghost_y += 1

        for row_index, row in enumerate(self.current_piece["shape"]):
            for col_index, value in enumerate(row):
                if not value:
                    continue
                x = self.board_rect.x + (self.current_piece["x"] + col_index) * self.CELL_SIZE
                y = self.board_rect.y + (ghost_y + row_index) * self.CELL_SIZE
                cell_rect = pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE).inflate(-6, -6)
                pygame.draw.rect(screen, theme.MUTED_TEXT, cell_rect, width=2, border_radius=5)

    def draw_next_panel(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, theme.SURFACE, self.next_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.next_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        assert self.ui is not None
        label = self.ui.info_font.render("Next Piece", True, theme.TEXT)
        screen.blit(label, label.get_rect(center=(self.next_rect.centerx, self.next_rect.top + 24)))

        if self.next_piece is None:
            return

        shape = self.next_piece["shape"]
        width = len(shape[0]) * self.CELL_SIZE
        height = len(shape) * self.CELL_SIZE
        offset_x = self.next_rect.centerx - width // 2
        offset_y = self.next_rect.centery - height // 2 + 12

        self.draw_piece(screen, self.next_piece, offset_x, offset_y, preview=True)

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None
        assert self.current_piece is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "Tetris",
            "A/D or Left/Right move. Q/E/Up rotate. S/Down soft drop. Space hard drops.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Score: {self.score}",
                f"Lines: {self.lines}",
                f"Level: {self.level}",
            ],
        )

        if self.game_over:
            sub = "The stack reached the top."
        else:
            sub = "Plan clean placements, keep the stack low, and chase line clears."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

        self.draw_board(screen)
        self.draw_ghost_piece(screen)
        self.draw_piece(screen, self.current_piece, 0, 0)
        self.draw_next_panel(screen)

        if self.paused and not self.game_over:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.game_over:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "Game Over",
                f"Final Score: {self.score}",
                f"Lines Cleared: {self.lines}  |  Level Reached: {self.level}",
            )