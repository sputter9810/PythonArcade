from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class MazeGame(GameBase):
    game_id = "maze"
    title = "Maze"

    DIFFICULTIES = {
        "Easy": (15, 15, 28),
        "Medium": (21, 21, 22),
        "Hard": (29, 29, 16),
    }

    DIRS = [
        (0, -1),
        (1, 0),
        (0, 1),
        (-1, 0),
    ]

    def __init__(self, app) -> None:
        super().__init__(app)
        self.ui: GameUI | None = None
        self.mode_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1040, 640)
        self.board_rect = pygame.Rect(0, 0, 600, 600)
        self.diff_buttons: dict[str, pygame.Rect] = {}

        self.difficulty = "Medium"
        self.rows = 21
        self.cols = 21
        self.cell_size = 22

        self.grid: list[list[int]] = []
        self.player = (1, 1)
        self.exit_cell = (19, 19)

        self.steps = 0
        self.completed = False
        self.paused = False

    def enter(self) -> None:
        self.ui = GameUI()
        self.mode_font = pygame.font.SysFont("arial", 18, bold=True)
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect((screen.get_width() - 1040) // 2, 165, 1040, 640)
        board_w = self.cols * self.cell_size
        board_h = self.rows * self.cell_size
        self.board_rect = pygame.Rect(0, 0, board_w, board_h)
        self.board_rect.center = self.play_rect.center
        self.board_rect.x -= 40

        self.diff_buttons = {
            "Easy": pygame.Rect(self.play_rect.right - 280, self.play_rect.top + 60, 80, 38),
            "Medium": pygame.Rect(self.play_rect.right - 185, self.play_rect.top + 60, 80, 38),
            "Hard": pygame.Rect(self.play_rect.right - 90, self.play_rect.top + 60, 80, 38),
        }

    def set_difficulty(self, difficulty: str) -> None:
        self.difficulty = difficulty
        self.reset_game()

    def reset_game(self) -> None:
        self.rows, self.cols, self.cell_size = self.DIFFICULTIES[self.difficulty]
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.grid = [[1 for _ in range(self.cols)] for _ in range(self.rows)]
        self.generate_maze()

        self.player = (1, 1)
        self.exit_cell = (self.rows - 2, self.cols - 2)
        self.steps = 0
        self.completed = False
        self.paused = False

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["round"] = self.steps
        payload["score"] = max(0, 2000 - self.steps * 5)
        return payload

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene
        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def generate_maze(self) -> None:
        stack = [(1, 1)]
        self.grid[1][1] = 0

        while stack:
            r, c = stack[-1]
            neighbors = []

            for dc, dr in self.DIRS:
                nr = r + dr * 2
                nc = c + dc * 2
                if 1 <= nr < self.rows - 1 and 1 <= nc < self.cols - 1 and self.grid[nr][nc] == 1:
                    neighbors.append((nr, nc, r + dr, c + dc))

            if neighbors:
                nr, nc, wr, wc = random.choice(neighbors)
                self.grid[wr][wc] = 0
                self.grid[nr][nc] = 0
                stack.append((nr, nc))
            else:
                stack.pop()

        self.grid[self.rows - 2][self.cols - 2] = 0

    def can_move(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols and self.grid[row][col] == 0

    def move_player(self, dr: int, dc: int) -> None:
        if self.paused or self.completed:
            return

        row, col = self.player
        nr, nc = row + dr, col + dc
        if self.can_move(nr, nc):
            self.player = (nr, nc)
            self.steps += 1
            if self.player == self.exit_cell:
                self.completed = True

    def draw_diff_button(self, screen: pygame.Surface, label: str, rect: pygame.Rect, selected: bool) -> None:
        assert self.mode_font is not None
        fill = theme.SURFACE_ALT if selected else theme.SURFACE
        border = theme.ACCENT if selected else theme.SURFACE_ALT
        pygame.draw.rect(screen, fill, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, width=2, border_radius=10)
        surface = self.mode_font.render(label, True, theme.TEXT)
        screen.blit(surface, surface.get_rect(center=rect.center))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif event.key == pygame.K_p and not self.completed:
                    self.paused = not self.paused
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif self.completed and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.reset_game()
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.move_player(0, -1)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.move_player(0, 1)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.move_player(-1, 0)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.move_player(1, 0)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label, rect in self.diff_buttons.items():
                    if rect.collidepoint(event.pos):
                        self.set_difficulty(label)
                        return
                if self.completed:
                    self.reset_game()

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None
        assert self.mode_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "Maze",
            "Move with Arrow Keys or WASD. Find the exit in as few steps as possible.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Difficulty: {self.difficulty}",
                f"Steps: {self.steps}",
            ],
        )
        sub = "Plan your route, avoid backtracking, and reach the exit cleanly." if not self.completed else "Exit reached."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "P: Pause  |  F5: New Maze  |  Esc: Back")

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        for label, rect in self.diff_buttons.items():
            self.draw_diff_button(screen, label, rect, label == self.difficulty)

        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(
                    self.board_rect.x + c * self.cell_size,
                    self.board_rect.y + r * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                color = theme.BACKGROUND if self.grid[r][c] == 1 else theme.SURFACE_ALT
                pygame.draw.rect(screen, color, rect)

        exit_rect = pygame.Rect(
            self.board_rect.x + self.exit_cell[1] * self.cell_size,
            self.board_rect.y + self.exit_cell[0] * self.cell_size,
            self.cell_size,
            self.cell_size,
        )
        pygame.draw.rect(screen, theme.ACCENT, exit_rect)

        player_rect = pygame.Rect(
            self.board_rect.x + self.player[1] * self.cell_size + 2,
            self.board_rect.y + self.player[0] * self.cell_size + 2,
            self.cell_size - 4,
            self.cell_size - 4,
        )
        pygame.draw.rect(screen, theme.WARNING, player_rect, border_radius=4)

        if self.paused and not self.completed:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.completed:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "Maze Cleared",
                f"Difficulty: {self.difficulty}",
                f"Steps Taken: {self.steps}",
            )