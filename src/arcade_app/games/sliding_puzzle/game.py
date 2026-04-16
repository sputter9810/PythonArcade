from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class SlidingPuzzleGame(GameBase):
    game_id = "sliding_puzzle"
    title = "Sliding Puzzle"

    DIFFICULTIES = {
        "Easy": 3,
        "Medium": 4,
        "Hard": 5,
    }

    def __init__(self, app):
        super().__init__(app)
        self.ui: GameUI | None = None
        self.tile_font: pygame.font.Font | None = None
        self.mode_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 980, 620)
        self.board_rect = pygame.Rect(0, 0, 420, 420)
        self.diff_buttons: dict[str, pygame.Rect] = {}

        self.difficulty = "Medium"
        self.size = 4
        self.grid: list[list[int]] = []
        self.empty = (0, 0)

        self.moves = 0
        self.completed = False
        self.paused = False

    def enter(self):
        self.ui = GameUI()
        self.tile_font = pygame.font.SysFont("arial", 34, bold=True)
        self.mode_font = pygame.font.SysFont("arial", 18, bold=True)
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect((screen.get_width() - 980) // 2, 165, 980, 620)

        board_size = min(460, 110 * self.size)
        self.board_rect = pygame.Rect(0, 0, board_size, board_size)
        self.board_rect.center = self.play_rect.center
        self.board_rect.y = self.play_rect.top + 92

        self.diff_buttons = {
            "Easy": pygame.Rect(self.play_rect.centerx - 190, self.play_rect.top + 24, 110, 40),
            "Medium": pygame.Rect(self.play_rect.centerx - 55, self.play_rect.top + 24, 110, 40),
            "Hard": pygame.Rect(self.play_rect.centerx + 80, self.play_rect.top + 24, 110, 40),
        }

    def set_difficulty(self, difficulty: str) -> None:
        self.difficulty = difficulty
        self.size = self.DIFFICULTIES[difficulty]
        self.reset_game()

    def reset_game(self):
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.size = self.DIFFICULTIES[self.difficulty]

        numbers = list(range(1, self.size * self.size)) + [0]
        self.grid = [numbers[i * self.size:(i + 1) * self.size] for i in range(self.size)]
        self.empty = (self.size - 1, self.size - 1)

        self.shuffle_safely()
        self.moves = 0
        self.completed = False
        self.paused = False

    def manhattan_distance(self) -> int:
        total = 0
        for r in range(self.size):
            for c in range(self.size):
                value = self.grid[r][c]
                if value == 0:
                    continue
                target_r = (value - 1) // self.size
                target_c = (value - 1) % self.size
                total += abs(r - target_r) + abs(c - target_c)
        return total

    def shuffle_safely(self) -> None:
        shuffle_moves = max(120, self.size * self.size * 24)
        last_empty = None

        for _ in range(shuffle_moves):
            er, ec = self.empty
            neighbors = []
            for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                nr, nc = er + dr, ec + dc
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    if last_empty is None or (nr, nc) != last_empty:
                        neighbors.append((nr, nc))

            if not neighbors:
                continue

            nr, nc = random.choice(neighbors)
            last_empty = self.empty
            self.grid[er][ec], self.grid[nr][nc] = self.grid[nr][nc], self.grid[er][ec]
            self.empty = (nr, nc)

        if self.is_solved() or self.manhattan_distance() < self.size * 3:
            self.shuffle_safely()

    def is_solved(self) -> bool:
        expected = list(range(1, self.size * self.size)) + [0]
        flat = [n for row in self.grid for n in row]
        return flat == expected

    def try_move_tile(self, row: int, col: int) -> None:
        if self.completed or self.paused:
            return

        er, ec = self.empty
        if abs(er - row) + abs(ec - col) != 1:
            return

        self.grid[er][ec], self.grid[row][col] = self.grid[row][col], self.grid[er][ec]
        self.empty = (row, col)
        self.moves += 1
        self.completed = self.is_solved()

    def move_by_direction(self, dr: int, dc: int) -> None:
        er, ec = self.empty
        tr, tc = er + dr, ec + dc
        if 0 <= tr < self.size and 0 <= tc < self.size:
            self.try_move_tile(tr, tc)

    def tile_at(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        if not self.board_rect.collidepoint(pos):
            return None
        cell = self.board_rect.width // self.size
        col = (pos[0] - self.board_rect.x) // cell
        row = (pos[1] - self.board_rect.y) // cell
        return int(row), int(col)

    def draw_diff_button(self, screen: pygame.Surface, label: str, rect: pygame.Rect, selected: bool) -> None:
        assert self.mode_font is not None
        fill = theme.SURFACE_ALT if selected else theme.SURFACE
        border = theme.ACCENT if selected else theme.SURFACE_ALT
        pygame.draw.rect(screen, fill, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, width=2, border_radius=10)
        surface = self.mode_font.render(label, True, theme.TEXT)
        screen.blit(surface, surface.get_rect(center=rect.center))

    def leave_to_menu(self):
        from arcade_app.scenes.game_select_scene import GameSelectScene
        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif e.key == pygame.K_p and not self.completed:
                    self.paused = not self.paused
                elif e.key == pygame.K_F5:
                    self.reset_game()
                elif self.completed and e.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.reset_game()
                elif e.key in (pygame.K_LEFT, pygame.K_a):
                    self.move_by_direction(0, 1)
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    self.move_by_direction(0, -1)
                elif e.key in (pygame.K_UP, pygame.K_w):
                    self.move_by_direction(1, 0)
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    self.move_by_direction(-1, 0)

            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for label, rect in self.diff_buttons.items():
                    if rect.collidepoint(e.pos):
                        self.set_difficulty(label)
                        return

                if self.completed:
                    self.reset_game()
                    continue
                if self.paused:
                    continue

                tile = self.tile_at(e.pos)
                if tile is not None:
                    self.try_move_tile(*tile)

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

    def render(self, screen):
        assert self.ui is not None
        assert self.tile_font is not None

        screen.fill(theme.BACKGROUND)
        self.rebuild_layout(screen)

        self.ui.draw_header(screen, "Sliding Puzzle", "Arrange the tiles in order with the blank in the bottom-right corner.")
        self.ui.draw_stats_row(
            screen,
            [
                f"Difficulty: {self.difficulty}",
                f"Moves: {self.moves}",
                f"Size: {self.size}x{self.size}",
            ],
        )
        sub = "Every shuffle is solvable and freshly generated." if not self.completed else "Puzzle solved."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "P: Pause  |  F5: New Puzzle  |  Esc: Back")

        for label, rect in self.diff_buttons.items():
            self.draw_diff_button(screen, label, rect, label == self.difficulty)

        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.board_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        cell = self.board_rect.width // self.size
        for r in range(self.size):
            for c in range(self.size):
                value = self.grid[r][c]
                rect = pygame.Rect(
                    self.board_rect.x + c * cell,
                    self.board_rect.y + r * cell,
                    cell,
                    cell,
                )
                pygame.draw.rect(screen, theme.SURFACE_ALT, rect, width=1, border_radius=4)

                if value != 0:
                    inner = rect.inflate(-8, -8)
                    pygame.draw.rect(screen, theme.ACCENT, inner, border_radius=10)
                    text = self.tile_font.render(str(value), True, theme.BACKGROUND)
                    screen.blit(text, text.get_rect(center=inner.center))

        if self.paused and not self.completed:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.completed:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "Solved",
                f"Moves: {self.moves}",
                f"Difficulty: {self.difficulty}",
            )