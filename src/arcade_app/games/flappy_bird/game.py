from __future__ import annotations

import random
import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme


class FlappyBirdGame(GameBase):
    game_id = "flappy_bird"
    title = "Flappy Bird"

    def __init__(self, app):
        super().__init__(app)

        # Player
        self.bird_y = 0
        self.bird_vel = 0

        # Physics
        self.gravity = 0.5
        self.flap_strength = -9

        # Pipes
        self.pipes = []
        self.pipe_width = 80
        self.pipe_gap = 180
        self.pipe_speed = 4

        # Game state
        self.score = 0
        self.game_over = False

        # Layout
        self.bird_x = 300
        self.ground_y = 700

        # Fonts
        self.title_font = None
        self.score_font = None
        self.small_font = None

    def enter(self):
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.score_font = pygame.font.SysFont("arial", 48, bold=True)
        self.small_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE)

        self.reset()

    def reset(self):
        self.bird_y = 400
        self.bird_vel = 0
        self.pipes.clear()
        self.score = 0
        self.game_over = False

        for i in range(3):
            self.spawn_pipe(600 + i * 300)

    def spawn_pipe(self, x):
        gap_y = random.randint(200, 500)
        self.pipes.append({
            "x": x,
            "gap_y": gap_y,
            "passed": False
        })

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))

                if event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset()
                    else:
                        self.bird_vel = self.flap_strength

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over:
                    self.reset()
                else:
                    self.bird_vel = self.flap_strength

    def update(self, dt):
        if self.game_over:
            return

        # Bird physics
        self.bird_vel += self.gravity
        self.bird_y += self.bird_vel

        # Move pipes
        for pipe in self.pipes:
            pipe["x"] -= self.pipe_speed

        # Spawn new pipes
        if self.pipes and self.pipes[-1]["x"] < 900:
            self.spawn_pipe(1200)

        # Remove old pipes
        self.pipes = [p for p in self.pipes if p["x"] > -100]

        # Score
        for pipe in self.pipes:
            if not pipe["passed"] and pipe["x"] < self.bird_x:
                pipe["passed"] = True
                self.score += 1

        # Collision
        bird_rect = pygame.Rect(self.bird_x, self.bird_y, 40, 40)

        if self.bird_y > self.ground_y or self.bird_y < 0:
            self.game_over = True

        for pipe in self.pipes:
            top_rect = pygame.Rect(pipe["x"], 0, self.pipe_width, pipe["gap_y"] - self.pipe_gap // 2)
            bottom_rect = pygame.Rect(pipe["x"], pipe["gap_y"] + self.pipe_gap // 2, self.pipe_width, 800)

            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                self.game_over = True

    def render(self, screen):
        screen.fill((135, 206, 235))  # sky blue

        # Bird
        pygame.draw.rect(screen, (255, 255, 0), (self.bird_x, self.bird_y, 40, 40))

        # Pipes
        for pipe in self.pipes:
            pygame.draw.rect(screen, (0, 200, 0),
                             (pipe["x"], 0, self.pipe_width, pipe["gap_y"] - self.pipe_gap // 2))
            pygame.draw.rect(screen, (0, 200, 0),
                             (pipe["x"], pipe["gap_y"] + self.pipe_gap // 2, self.pipe_width, 800))

        # Ground
        pygame.draw.rect(screen, (200, 180, 120), (0, self.ground_y, screen.get_width(), 200))

        # Score
        score_text = self.score_font.render(str(self.score), True, (0, 0, 0))
        screen.blit(score_text, score_text.get_rect(center=(screen.get_width() // 2, 80)))

        # Game over
        if self.game_over:
            text = self.title_font.render("Game Over", True, (0, 0, 0))
            screen.blit(text, text.get_rect(center=(screen.get_width() // 2, 300)))

            restart = self.small_font.render("Press Space / Click to Restart", True, (0, 0, 0))
            screen.blit(restart, restart.get_rect(center=(screen.get_width() // 2, 350)))