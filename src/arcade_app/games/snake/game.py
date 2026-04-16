from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class SnakeGame(GameBase):
    game_id = "snake"
    title = "Snake"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.ui: GameUI | None = None

        self.grid_size = 20
        self.cell_size = 28
        self.board_rect = pygame.Rect(0, 0, self.grid_size * self.cell_size, self.grid_size * self.cell_size)

        self.move_delay = 0.12
        self.move_timer = 0.0

        self.score = 0
        self.game_over = False
        self.paused = False

        self.reset()

    def reset(self) -> None:
        center = self.grid_size // 2
        self.snake = [(center, center), (center - 1, center), (center - 2, center)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self.spawn_food()
        self.game_over = False
        self.paused = False
        self.score = 0
        self.move_timer = 0.0

    def enter(self) -> None:
        self.ui = GameUI()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        board_width = self.grid_size * self.cell_size
        board_height = self.grid_size * self.cell_size
        self.board_rect = pygame.Rect(
            (screen.get_width() - board_width) // 2,
            165,
            board_width,
            board_height,
        )

    def spawn_food(self) -> tuple[int, int]:
        available = [
            (x, y)
            for y in range(self.grid_size)
            for x in range(self.grid_size)
            if (x, y) not in getattr(self, "snake", [])
        ]
        return random.choice(available)

    def set_direction(self, new_direction: tuple[int, int]) -> None:
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.next_direction = new_direction

    def step(self) -> None:
        if self.game_over:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        if not (0 <= new_head[0] < self.grid_size and 0 <= new_head[1] < self.grid_size):
            self.game_over = True
            return

        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
                elif event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                elif event.key == pygame.K_F5:
                    self.reset()
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.set_direction((0, -1))
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.set_direction((0, 1))
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.set_direction((-1, 0))
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.set_direction((1, 0))

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.paused or self.game_over:
            return

        self.move_timer += dt
        if self.move_timer >= self.move_delay:
            self.move_timer = 0.0
            self.step()

    def draw_cell(
        self,
        screen: pygame.Surface,
        grid_pos: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        x, y = grid_pos
        rect = pygame.Rect(
            self.board_rect.x + x * self.cell_size,
            self.board_rect.y + y * self.cell_size,
            self.cell_size,
            self.cell_size,
        )
        pygame.draw.rect(screen, color, rect, border_radius=6)

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "Snake",
            "Move with Arrow Keys or WASD. Eat food, grow longer, and avoid collisions.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Score: {self.score}",
                f"Length: {len(self.snake)}",
            ],
        )

        if self.game_over:
            sub = "Run ended. You hit a wall or yourself."
        else:
            sub = "Stay smooth through corners and keep your path open."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.board_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        for y in range(self.grid_size):
            for x in range(self.grid_size):
                cell_rect = pygame.Rect(
                    self.board_rect.x + x * self.cell_size,
                    self.board_rect.y + y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                pygame.draw.rect(screen, theme.SURFACE_ALT, cell_rect, width=1, border_radius=3)

        self.draw_cell(screen, self.food, theme.DANGER)

        for index, segment in enumerate(self.snake):
            color = theme.ACCENT if index == 0 else theme.SUCCESS
            self.draw_cell(screen, segment, color)

        if self.paused and not self.game_over:
            self.ui.draw_pause_overlay(screen, self.board_rect)

        if self.game_over:
            self.ui.draw_game_over(
                screen,
                self.board_rect,
                "Game Over",
                f"Final Score: {self.score}",
                f"Snake Length: {len(self.snake)}",
            )