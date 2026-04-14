from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme


class PongGame(GameBase):
    game_id = "pong"
    title = "Pong"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.score_font: pygame.font.Font | None = None
        self.mode_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1100, 520)

        self.paddle_width = 18
        self.paddle_height = 120
        self.paddle_speed = 520.0

        self.ball_size = 18
        self.ball_speed = 360.0

        self.left_score = 0
        self.right_score = 0

        self.vs_computer = True

        self.left_paddle = pygame.Rect(0, 0, self.paddle_width, self.paddle_height)
        self.right_paddle = pygame.Rect(0, 0, self.paddle_width, self.paddle_height)
        self.ball = pygame.Rect(0, 0, self.ball_size, self.ball_size)

        self.ball_velocity_x = 0.0
        self.ball_velocity_y = 0.0

        self.pvp_button = pygame.Rect(0, 0, 180, 44)
        self.pvc_button = pygame.Rect(0, 0, 180, 44)

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.score_font = pygame.font.SysFont("arial", 48, bold=True)
        self.mode_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE, bold=True)

        self.reset_positions()
        self.serve_ball(random.choice([-1, 1]))

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        board_width = 1100
        board_height = 520
        board_y = 210

        self.play_rect = pygame.Rect(
            (screen.get_width() - board_width) // 2,
            board_y,
            board_width,
            board_height,
        )

        self.pvp_button = pygame.Rect(screen.get_width() // 2 - 210, 115, 180, 44)
        self.pvc_button = pygame.Rect(screen.get_width() // 2 + 30, 115, 180, 44)

        self.left_paddle.width = self.paddle_width
        self.left_paddle.height = self.paddle_height
        self.right_paddle.width = self.paddle_width
        self.right_paddle.height = self.paddle_height

        self.left_paddle.x = self.play_rect.left + 24
        self.right_paddle.x = self.play_rect.right - 24 - self.paddle_width

        if self.left_paddle.top < self.play_rect.top:
            self.left_paddle.top = self.play_rect.top
        if self.left_paddle.bottom > self.play_rect.bottom:
            self.left_paddle.bottom = self.play_rect.bottom

        if self.right_paddle.top < self.play_rect.top:
            self.right_paddle.top = self.play_rect.top
        if self.right_paddle.bottom > self.play_rect.bottom:
            self.right_paddle.bottom = self.play_rect.bottom

        self.ball.clamp_ip(self.play_rect)

    def reset_positions(self) -> None:
        self.left_paddle = pygame.Rect(
            self.play_rect.left + 24,
            self.play_rect.centery - self.paddle_height // 2,
            self.paddle_width,
            self.paddle_height,
        )
        self.right_paddle = pygame.Rect(
            self.play_rect.right - 24 - self.paddle_width,
            self.play_rect.centery - self.paddle_height // 2,
            self.paddle_width,
            self.paddle_height,
        )
        self.ball = pygame.Rect(
            self.play_rect.centerx - self.ball_size // 2,
            self.play_rect.centery - self.ball_size // 2,
            self.ball_size,
            self.ball_size,
        )

    def serve_ball(self, direction: int) -> None:
        self.ball.center = self.play_rect.center
        angle_y = random.uniform(-0.8, 0.8)
        self.ball_velocity_x = self.ball_speed * direction
        self.ball_velocity_y = self.ball_speed * angle_y

    def reset_game(self) -> None:
        self.left_score = 0
        self.right_score = 0
        self.reset_positions()
        self.serve_ball(random.choice([-1, 1]))

    def set_mode(self, vs_computer: bool) -> None:
        self.vs_computer = vs_computer
        self.reset_game()

    def draw_mode_button(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        label: str,
        selected: bool,
    ) -> None:
        fill = theme.SURFACE_ALT if selected else theme.SURFACE
        border = theme.ACCENT if selected else theme.SURFACE_ALT

        pygame.draw.rect(screen, fill, rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, border, rect, width=3, border_radius=theme.RADIUS_MEDIUM)

        assert self.mode_font is not None
        text = self.mode_font.render(label, True, theme.TEXT)
        screen.blit(text, text.get_rect(center=rect.center))

    def move_paddle(self, paddle: pygame.Rect, direction: float, dt: float) -> None:
        paddle.y += int(direction * self.paddle_speed * dt)

        if paddle.top < self.play_rect.top:
            paddle.top = self.play_rect.top
        if paddle.bottom > self.play_rect.bottom:
            paddle.bottom = self.play_rect.bottom

    def update_ball(self, dt: float) -> None:
        self.ball.x += int(self.ball_velocity_x * dt)
        self.ball.y += int(self.ball_velocity_y * dt)

        if self.ball.top <= self.play_rect.top:
            self.ball.top = self.play_rect.top
            self.ball_velocity_y *= -1

        if self.ball.bottom >= self.play_rect.bottom:
            self.ball.bottom = self.play_rect.bottom
            self.ball_velocity_y *= -1

        if self.ball.colliderect(self.left_paddle) and self.ball_velocity_x < 0:
            self.ball.left = self.left_paddle.right
            self.ball_velocity_x *= -1
            self.add_paddle_bounce(self.left_paddle)

        if self.ball.colliderect(self.right_paddle) and self.ball_velocity_x > 0:
            self.ball.right = self.right_paddle.left
            self.ball_velocity_x *= -1
            self.add_paddle_bounce(self.right_paddle)

        if self.ball.right < self.play_rect.left:
            self.right_score += 1
            self.reset_positions()
            self.serve_ball(-1)

        if self.ball.left > self.play_rect.right:
            self.left_score += 1
            self.reset_positions()
            self.serve_ball(1)

    def add_paddle_bounce(self, paddle: pygame.Rect) -> None:
        relative_intersect = self.ball.centery - paddle.centery
        normalized = relative_intersect / (self.paddle_height / 2)
        self.ball_velocity_y = normalized * self.ball_speed
        self.ball_velocity_x *= 1.04
        self.ball_velocity_y *= 1.02

    def update_ai(self, dt: float) -> None:
        if not self.vs_computer:
            return

        ai_dead_zone = 10
        if self.ball.centery < self.right_paddle.centery - ai_dead_zone:
            self.move_paddle(self.right_paddle, -1, dt)
        elif self.ball.centery > self.right_paddle.centery + ai_dead_zone:
            self.move_paddle(self.right_paddle, 1, dt)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_1:
                    self.set_mode(False)
                elif event.key == pygame.K_2:
                    self.set_mode(True)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                if self.pvp_button.collidepoint(mouse_pos):
                    self.set_mode(False)
                    return

                if self.pvc_button.collidepoint(mouse_pos):
                    self.set_mode(True)
                    return

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()

        left_direction = 0.0
        if keys[pygame.K_w]:
            left_direction -= 1.0
        if keys[pygame.K_s]:
            left_direction += 1.0
        self.move_paddle(self.left_paddle, left_direction, dt)

        if self.vs_computer:
            self.update_ai(dt)
        else:
            right_direction = 0.0
            if keys[pygame.K_UP]:
                right_direction -= 1.0
            if keys[pygame.K_DOWN]:
                right_direction += 1.0
            self.move_paddle(self.right_paddle, right_direction, dt)

        self.update_ball(dt)

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.score_font is not None
        assert self.mode_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Pong", True, theme.TEXT)
        score_text = self.score_font.render(f"{self.left_score}     {self.right_score}", True, theme.TEXT)

        mode_text = "Mode: Player vs Computer" if self.vs_computer else "Mode: Player vs Player"
        mode_render = self.info_font.render(mode_text, True, theme.TEXT)

        controls = self.info_font.render(
            "Left: W/S  |  Right: ↑/↓ (PvP)  |  1: PvP  |  2: PvC  |  R: Restart  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 28)))
        screen.blit(score_text, score_text.get_rect(center=(screen.get_width() // 2, 78)))

        self.draw_mode_button(screen, self.pvp_button, "Player vs Player", not self.vs_computer)
        self.draw_mode_button(screen, self.pvc_button, "Player vs Computer", self.vs_computer)

        screen.blit(mode_render, mode_render.get_rect(center=(screen.get_width() // 2, 172)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30)))

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)

        dash_height = 20
        dash_gap = 14
        dash_width = 6
        y = self.play_rect.top + 20
        while y < self.play_rect.bottom - dash_height:
            dash = pygame.Rect(
                self.play_rect.centerx - dash_width // 2,
                y,
                dash_width,
                dash_height,
            )
            pygame.draw.rect(screen, theme.SURFACE_ALT, dash, border_radius=3)
            y += dash_height + dash_gap

        pygame.draw.rect(screen, theme.TEXT, self.left_paddle, border_radius=8)
        pygame.draw.rect(screen, theme.TEXT, self.right_paddle, border_radius=8)
        pygame.draw.ellipse(screen, theme.ACCENT, self.ball)