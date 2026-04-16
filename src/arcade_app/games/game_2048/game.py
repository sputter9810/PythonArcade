from __future__ import annotations

import random
from typing import Iterable

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class Game2048(GameBase):
    game_id = "game_2048"
    title = "2048"

    GRID_SIZE = 4
    TARGET = 2048

    TILE_COLORS = {
        0: (48, 52, 64),
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

    def __init__(self, app) -> None:
        super().__init__(app)
        self.ui: GameUI | None = None
        self.tile_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1000, 620)
        self.board_rect = pygame.Rect(0, 0, 420, 420)

        self.board: list[list[int]] = []
        self.score = 0
        self.best_tile = 0
        self.moves = 0

        self.game_over = False
        self.won = False
        self.paused = False

    def enter(self) -> None:
        self.ui = GameUI()
        self.tile_font = pygame.font.SysFont("arial", 32, bold=True)
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect((screen.get_width() - 1000) // 2, 165, 1000, 620)
        self.board_rect = pygame.Rect(0, 0, 420, 420)
        self.board_rect.center = self.play_rect.center
        self.board_rect.y -= 20

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.board = [[0 for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.score = 0
        self.best_tile = 0
        self.moves = 0
        self.game_over = False
        self.won = False
        self.paused = False

        self.spawn_tile()
        self.spawn_tile()
        self.update_state_flags()

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["score"] = self.score
        payload["round"] = self.best_tile
        return payload

    def spawn_tile(self) -> None:
        empty = [(r, c) for r in range(self.GRID_SIZE) for c in range(self.GRID_SIZE) if self.board[r][c] == 0]
        if not empty:
            return
        r, c = random.choice(empty)
        self.board[r][c] = 4 if random.random() < 0.1 else 2

    def compress_line(self, values: Iterable[int]) -> tuple[list[int], int]:
        filtered = [v for v in values if v != 0]
        merged: list[int] = []
        gained = 0
        skip = False

        for i, value in enumerate(filtered):
            if skip:
                skip = False
                continue
            if i + 1 < len(filtered) and filtered[i + 1] == value:
                new_value = value * 2
                merged.append(new_value)
                gained += new_value
                skip = True
            else:
                merged.append(value)

        while len(merged) < self.GRID_SIZE:
            merged.append(0)

        return merged, gained

    def move_left(self) -> bool:
        changed = False
        for r in range(self.GRID_SIZE):
            original = self.board[r][:]
            merged, gained = self.compress_line(original)
            self.board[r] = merged
            self.score += gained
            if merged != original:
                changed = True
        return changed

    def move_right(self) -> bool:
        changed = False
        for r in range(self.GRID_SIZE):
            original = self.board[r][:]
            reversed_row = list(reversed(original))
            merged, gained = self.compress_line(reversed_row)
            merged = list(reversed(merged))
            self.board[r] = merged
            self.score += gained
            if merged != original:
                changed = True
        return changed

    def move_up(self) -> bool:
        changed = False
        for c in range(self.GRID_SIZE):
            original = [self.board[r][c] for r in range(self.GRID_SIZE)]
            merged, gained = self.compress_line(original)
            self.score += gained
            if merged != original:
                changed = True
            for r in range(self.GRID_SIZE):
                self.board[r][c] = merged[r]
        return changed

    def move_down(self) -> bool:
        changed = False
        for c in range(self.GRID_SIZE):
            original = [self.board[r][c] for r in range(self.GRID_SIZE)]
            reversed_col = list(reversed(original))
            merged, gained = self.compress_line(reversed_col)
            merged = list(reversed(merged))
            self.score += gained
            if merged != original:
                changed = True
            for r in range(self.GRID_SIZE):
                self.board[r][c] = merged[r]
        return changed

    def has_moves_available(self) -> bool:
        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                value = self.board[r][c]
                if value == 0:
                    return True
                if c + 1 < self.GRID_SIZE and self.board[r][c + 1] == value:
                    return True
                if r + 1 < self.GRID_SIZE and self.board[r + 1][c] == value:
                    return True
        return False

    def update_state_flags(self) -> None:
        self.best_tile = max(max(row) for row in self.board)
        self.won = self.best_tile >= self.TARGET
        self.game_over = not self.has_moves_available()

    def try_move(self, direction: str) -> None:
        if self.paused or self.game_over:
            return

        moved = False
        if direction == "left":
            moved = self.move_left()
        elif direction == "right":
            moved = self.move_right()
        elif direction == "up":
            moved = self.move_up()
        elif direction == "down":
            moved = self.move_down()

        if moved:
            self.moves += 1
            self.spawn_tile()
            self.update_state_flags()

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene
        self.app.scene_manager.go_to(GameSelectScene(self.app))

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
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.try_move("left")
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.try_move("right")
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.try_move("up")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.try_move("down")

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

    def tile_color(self, value: int) -> tuple[int, int, int]:
        return self.TILE_COLORS.get(value, (60, 58, 50))

    def tile_text_color(self, value: int) -> tuple[int, int, int]:
        return theme.BACKGROUND if value >= 8 else (70, 64, 58)

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None
        assert self.tile_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "2048",
            "Slide with Arrow Keys or WASD. Merge tiles and reach 2048.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Score: {self.score}",
                f"Best Tile: {self.best_tile}",
                f"Moves: {self.moves}",
            ],
        )

        if self.game_over:
            sub = "No moves left."
        else:
            sub = "Build space, chain merges, and avoid trapping the board."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.board_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        gap = 10
        tile_size = (self.board_rect.width - gap * 5) // 4

        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                x = self.board_rect.x + gap + c * (tile_size + gap)
                y = self.board_rect.y + gap + r * (tile_size + gap)
                rect = pygame.Rect(x, y, tile_size, tile_size)
                value = self.board[r][c]

                pygame.draw.rect(screen, self.tile_color(value), rect, border_radius=10)

                if value:
                    font_size = 34 if value < 100 else 28 if value < 1000 else 22
                    font = pygame.font.SysFont("arial", font_size, bold=True)
                    text = font.render(str(value), True, self.tile_text_color(value))
                    screen.blit(text, text.get_rect(center=rect.center))

        if self.paused and not self.game_over:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.game_over:
            title = "You Win" if self.won else "Game Over"
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                title,
                f"Final Score: {self.score}",
                f"Best Tile: {self.best_tile}  |  Moves: {self.moves}",
            )