from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme


class BreakoutGame(GameBase):
    game_id = "breakout"
    title = "Breakout"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1100, 620)

        self.paddle = pygame.Rect(0, 0, 160, 18)
        self.paddle_speed = 700.0

        self.ball = pygame.Rect(0, 0, 18, 18)
        self.ball_velocity_x = 280.0
        self.ball_velocity_y = -280.0

        self.bricks: list[pygame.Rect] = []
        self.brick_rows = 6
        self.brick_cols = 10

        self.score = 0
        self.lives = 3
        self.is_won = False
        self.is_game_over = False

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)

        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(
            (screen.get_width() - 1100) // 2,
            140,
            1100,
            620,
        )

    def reset_positions(self) -> None:
        self.paddle = pygame.Rect(
            self.play_rect.centerx - 80,
            self.play_rect.bottom - 35,
            160,
            18,
        )
        self.ball = pygame.Rect(
            self.play_rect.centerx - 9,
            self.paddle.top - 28,
            18,
            18,
        )

        direction = random.choice([-1, 1])
        self.ball_velocity_x = 280.0 * direction
        self.ball_velocity_y = -280.0

    def build_bricks(self) -> None:
        self.bricks.clear()

        padding = 14
        top_padding = 30
        brick_width = (self.play_rect.width - padding * (self.brick_cols + 1)) // self.brick_cols
        brick_height = 28

        for row in range(self.brick_rows):
            for col in range(self.brick_cols):
                x = self.play_rect.x + padding + col * (brick_width + padding)
                y = self.play_rect.y + top_padding + row * (brick_height + padding)
                self.bricks.append(pygame.Rect(x, y, brick_width, brick_height))

    def reset_game(self) -> None:
        self.score = 0
        self.lives = 3
        self.is_won = False
        self.is_game_over = False
        self.build_bricks()
        self.reset_positions()

    def lose_life(self) -> None:
        self.lives -= 1
        if self.lives <= 0:
            self.is_game_over = True
        else:
            self.reset_positions()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
                elif event.key == pygame.K_F5:
                    self.reset_game()

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.is_won or self.is_game_over:
            return

        keys = pygame.key.get_pressed()

        move = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move += 1.0

        self.paddle.x += int(move * self.paddle_speed * dt)

        if self.paddle.left < self.play_rect.left:
            self.paddle.left = self.play_rect.left
        if self.paddle.right > self.play_rect.right:
            self.paddle.right = self.play_rect.right

        self.ball.x += int(self.ball_velocity_x * dt)
        self.ball.y += int(self.ball_velocity_y * dt)

        if self.ball.left <= self.play_rect.left:
            self.ball.left = self.play_rect.left
            self.ball_velocity_x *= -1

        if self.ball.right >= self.play_rect.right:
            self.ball.right = self.play_rect.right
            self.ball_velocity_x *= -1

        if self.ball.top <= self.play_rect.top:
            self.ball.top = self.play_rect.top
            self.ball_velocity_y *= -1

        if self.ball.bottom >= self.play_rect.bottom:
            self.lose_life()
            return

        if self.ball.colliderect(self.paddle) and self.ball_velocity_y > 0:
            self.ball.bottom = self.paddle.top
            self.ball_velocity_y *= -1

            offset = (self.ball.centerx - self.paddle.centerx) / (self.paddle.width / 2)
            self.ball_velocity_x = 320.0 * offset if offset != 0 else random.choice([-120.0, 120.0])

        hit_brick = None
        for brick in self.bricks:
            if self.ball.colliderect(brick):
                hit_brick = brick
                break

        if hit_brick is not None:
            self.bricks.remove(hit_brick)
            self.score += 100

            overlap_left = abs(self.ball.right - hit_brick.left)
            overlap_right = abs(self.ball.left - hit_brick.right)
            overlap_top = abs(self.ball.bottom - hit_brick.top)
            overlap_bottom = abs(self.ball.top - hit_brick.bottom)

            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap in (overlap_left, overlap_right):
                self.ball_velocity_x *= -1
            else:
                self.ball_velocity_y *= -1

        if not self.bricks:
            self.is_won = True

    def brick_color(self, brick: pygame.Rect) -> tuple[int, int, int]:
        relative_y = brick.y - self.play_rect.y
        band = relative_y // 42

        colors = [
            (220, 80, 80),
            (230, 130, 80),
            (230, 180, 80),
            (120, 200, 100),
            (100, 170, 240),
            (160, 120, 230),
        ]
        return colors[min(band, len(colors) - 1)]

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Breakout", True, theme.TEXT)

        if self.is_won:
            status_text = "You cleared all bricks!"
        elif self.is_game_over:
            status_text = "Game Over"
        else:
            status_text = "Break every brick"

        status = self.info_font.render(status_text, True, theme.TEXT)
        score = self.info_font.render(f"Score: {self.score}", True, theme.TEXT)
        lives = self.info_font.render(f"Lives: {self.lives}", True, theme.TEXT)
        controls = self.info_font.render(
            "Move: Arrow Keys / A,D  |  F5: Restart  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 32)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 75)))
        screen.blit(score, score.get_rect(center=(screen.get_width() // 2 - 100, 110)))
        screen.blit(lives, lives.get_rect(center=(screen.get_width() // 2 + 100, 110)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 28)))

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)

        for brick in self.bricks:
            pygame.draw.rect(screen, self.brick_color(brick), brick, border_radius=8)

        pygame.draw.rect(screen, theme.TEXT, self.paddle, border_radius=8)
        pygame.draw.ellipse(screen, theme.ACCENT, self.ball)