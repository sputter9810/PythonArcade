from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class PongGame(GameBase):
    game_id = "pong"
    title = "Pong"

    WIN_SCORE = 7

    def __init__(self, app) -> None:
        super().__init__(app)

        self.ui: GameUI | None = None
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
        self.paused = False
        self.game_over = False
        self.winner_text = ""

        self.left_paddle = pygame.Rect(0, 0, self.paddle_width, self.paddle_height)
        self.right_paddle = pygame.Rect(0, 0, self.paddle_width, self.paddle_height)
        self.ball_pos = pygame.Vector2(0, 0)
        self.ball = pygame.Rect(0, 0, self.ball_size, self.ball_size)

        self.ball_velocity_x = 0.0
        self.ball_velocity_y = 0.0

        self.pvp_button = pygame.Rect(0, 0, 180, 44)
        self.pvc_button = pygame.Rect(0, 0, 180, 44)

    def enter(self) -> None:
        self.ui = GameUI()
        self.score_font = pygame.font.SysFont("arial", 48, bold=True)
        self.mode_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE, bold=True)
        self.reset_game()

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

        self.pvp_button = pygame.Rect(screen.get_width() // 2 - 210, 150, 180, 40)
        self.pvc_button = pygame.Rect(screen.get_width() // 2 + 30, 150, 180, 40)

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

        self.ball.topleft = (round(self.ball_pos.x), round(self.ball_pos.y))

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
        self.ball_pos = pygame.Vector2(self.ball.x, self.ball.y)

    def serve_ball(self, direction: int) -> None:
        self.ball.center = self.play_rect.center
        self.ball_pos = pygame.Vector2(self.ball.x, self.ball.y)

        angle_y = random.uniform(-0.8, 0.8)
        self.ball_velocity_x = self.ball_speed * direction
        self.ball_velocity_y = self.ball_speed * angle_y

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.left_score = 0
        self.right_score = 0
        self.paused = False
        self.game_over = False
        self.winner_text = ""
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

    def check_win_condition(self) -> None:
        if self.left_score >= self.WIN_SCORE:
            self.game_over = True
            self.winner_text = "Left Player Wins"
        elif self.right_score >= self.WIN_SCORE:
            self.game_over = True
            self.winner_text = "Right Player Wins"

    def update_ball(self, dt: float) -> None:
        self.ball_pos.x += self.ball_velocity_x * dt
        self.ball_pos.y += self.ball_velocity_y * dt
        self.ball.x = round(self.ball_pos.x)
        self.ball.y = round(self.ball_pos.y)

        if self.ball.top <= self.play_rect.top:
            self.ball.top = self.play_rect.top
            self.ball_pos.y = float(self.ball.y)
            self.ball_velocity_y *= -1

        if self.ball.bottom >= self.play_rect.bottom:
            self.ball.bottom = self.play_rect.bottom
            self.ball_pos.y = float(self.ball.y)
            self.ball_velocity_y *= -1

        if self.ball.colliderect(self.left_paddle) and self.ball_velocity_x < 0:
            self.ball.left = self.left_paddle.right
            self.ball_pos.x = float(self.ball.x)
            self.ball_velocity_x *= -1
            self.add_paddle_bounce(self.left_paddle)

        if self.ball.colliderect(self.right_paddle) and self.ball_velocity_x > 0:
            self.ball.right = self.right_paddle.left
            self.ball_pos.x = float(self.ball.x)
            self.ball_velocity_x *= -1
            self.add_paddle_bounce(self.right_paddle)

        if self.ball.right < self.play_rect.left:
            self.right_score += 1
            self.check_win_condition()
            if not self.game_over:
                self.reset_positions()
                self.serve_ball(-1)
            return

        if self.ball.left > self.play_rect.right:
            self.left_score += 1
            self.check_win_condition()
            if not self.game_over:
                self.reset_positions()
                self.serve_ball(1)
            return

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
                elif event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif event.key == pygame.K_1:
                    self.set_mode(False)
                elif event.key == pygame.K_2:
                    self.set_mode(True)
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN) and self.game_over:
                    self.reset_game()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                if self.pvp_button.collidepoint(mouse_pos):
                    self.set_mode(False)
                    return

                if self.pvc_button.collidepoint(mouse_pos):
                    self.set_mode(True)
                    return

                if self.game_over:
                    self.reset_game()

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.paused or self.game_over:
            return

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
        assert self.ui is not None
        assert self.score_font is not None
        assert self.mode_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        mode_text = "Player vs Computer" if self.vs_computer else "Player vs Player"
        self.ui.draw_header(
            screen,
            "Pong",
            "Left paddle: W/S. Right paddle: Arrow Keys in PvP. 1 = PvP, 2 = PvC.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Left: {self.left_score}",
                f"Right: {self.right_score}",
                f"Mode: {'PvC' if self.vs_computer else 'PvP'}",
            ],
        )
        self.ui.draw_sub_stats(screen, f"Current mode: {mode_text}  |  First to {self.WIN_SCORE}")
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  1: PvP  |  2: PvC  |  Esc: Back")

        self.draw_mode_button(screen, self.pvp_button, "Player vs Player", not self.vs_computer)
        self.draw_mode_button(screen, self.pvc_button, "Player vs Computer", self.vs_computer)

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

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

        if self.paused and not self.game_over:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.game_over:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                self.winner_text or "Match Over",
                f"Final Score: {self.left_score} - {self.right_score}",
                f"Mode: {'PvC' if self.vs_computer else 'PvP'}",
            )