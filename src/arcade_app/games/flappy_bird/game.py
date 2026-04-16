from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class FlappyBirdGame(GameBase):
    game_id = "flappy_bird"
    title = "Flappy Bird"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.ui: GameUI | None = None

        self.play_rect = pygame.Rect(0, 0, 1000, 620)

        self.bird_y = 0.0
        self.bird_vel = 0.0
        self.bird_x = 280
        self.bird_size = 40

        self.gravity = 0.5
        self.flap_strength = -9.0

        self.pipes: list[dict] = []
        self.pipe_width = 80
        self.pipe_gap = 180
        self.pipe_speed = 4.0

        self.score = 0
        self.game_over = False
        self.paused = False

        self.ground_height = 70

    def enter(self) -> None:
        self.ui = GameUI()
        self.reset()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(0, 0, 1000, 620)
        self.play_rect.centerx = screen.get_width() // 2
        self.play_rect.top = 165

    def reset(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.bird_y = float(self.play_rect.centery - 20)
        self.bird_vel = 0.0
        self.pipes.clear()
        self.score = 0
        self.game_over = False
        self.paused = False

        start_x = self.play_rect.left + 620
        for i in range(3):
            self.spawn_pipe(start_x + i * 280)

    def spawn_pipe(self, x: int) -> None:
        min_gap_y = self.play_rect.top + 140
        max_gap_y = self.play_rect.bottom - self.ground_height - 140
        gap_y = random.randint(min_gap_y, max_gap_y)

        self.pipes.append(
            {
                "x": x,
                "gap_y": gap_y,
                "passed": False,
            }
        )

    def flap(self) -> None:
        if self.game_over or self.paused:
            return
        self.bird_vel = self.flap_strength

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
                elif event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset()
                    else:
                        self.flap()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_over:
                    self.reset()
                else:
                    self.flap()

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.paused or self.game_over:
            return

        self.bird_vel += self.gravity
        self.bird_y += self.bird_vel

        for pipe in self.pipes:
            pipe["x"] -= self.pipe_speed

        if self.pipes and self.pipes[-1]["x"] < self.play_rect.right - 180:
            self.spawn_pipe(self.play_rect.right + 140)

        self.pipes = [p for p in self.pipes if p["x"] > self.play_rect.left - 120]

        for pipe in self.pipes:
            if not pipe["passed"] and pipe["x"] + self.pipe_width < self.bird_x:
                pipe["passed"] = True
                self.score += 1

        bird_rect = pygame.Rect(self.bird_x, int(self.bird_y), self.bird_size, self.bird_size)

        if bird_rect.top <= self.play_rect.top or bird_rect.bottom >= self.play_rect.bottom - self.ground_height:
            self.game_over = True

        for pipe in self.pipes:
            top_rect = pygame.Rect(
                pipe["x"],
                self.play_rect.top,
                self.pipe_width,
                pipe["gap_y"] - self.pipe_gap // 2 - self.play_rect.top,
            )
            bottom_rect = pygame.Rect(
                pipe["x"],
                pipe["gap_y"] + self.pipe_gap // 2,
                self.pipe_width,
                self.play_rect.bottom - self.ground_height - (pipe["gap_y"] + self.pipe_gap // 2),
            )

            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                self.game_over = True
                break

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "Flappy Bird",
            "Space or Click to flap. Thread the gaps and stay above the ground.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Score: {self.score}",
            ],
        )

        if self.game_over:
            sub = "You clipped a pipe or the floor."
        else:
            sub = "Quick taps keep the height under control."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

        sky = pygame.Rect(self.play_rect.left, self.play_rect.top, self.play_rect.width, self.play_rect.height)
        pygame.draw.rect(screen, (135, 206, 235), sky, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, sky, width=2, border_radius=theme.RADIUS_MEDIUM)

        for pipe in self.pipes:
            top_height = pipe["gap_y"] - self.pipe_gap // 2 - self.play_rect.top
            bottom_y = pipe["gap_y"] + self.pipe_gap // 2
            bottom_height = self.play_rect.bottom - self.ground_height - bottom_y

            top_rect = pygame.Rect(pipe["x"], self.play_rect.top, self.pipe_width, top_height)
            bottom_rect = pygame.Rect(pipe["x"], bottom_y, self.pipe_width, bottom_height)

            pygame.draw.rect(screen, (0, 170, 0), top_rect, border_radius=10)
            pygame.draw.rect(screen, (0, 170, 0), bottom_rect, border_radius=10)

        ground_rect = pygame.Rect(
            self.play_rect.left,
            self.play_rect.bottom - self.ground_height,
            self.play_rect.width,
            self.ground_height,
        )
        pygame.draw.rect(screen, (200, 180, 120), ground_rect)

        bird_rect = pygame.Rect(self.bird_x, int(self.bird_y), self.bird_size, self.bird_size)
        pygame.draw.rect(screen, (255, 225, 0), bird_rect, border_radius=10)
        pygame.draw.circle(screen, theme.TEXT, (bird_rect.right - 10, bird_rect.top + 12), 3)

        if self.paused and not self.game_over:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.game_over:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "Game Over",
                f"Final Score: {self.score}",
                "Press Space / Click / F5 to try again.",
            )