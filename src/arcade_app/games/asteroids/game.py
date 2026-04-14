from __future__ import annotations

import math
import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme


class AsteroidsGame(GameBase):
    game_id = "asteroids"
    title = "Asteroids"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1100, 620)

        self.ship_pos = pygame.Vector2(0, 0)
        self.ship_vel = pygame.Vector2(0, 0)
        self.ship_angle = -90.0
        self.ship_rotation_speed = 220.0
        self.ship_acceleration = 260.0
        self.ship_radius = 18

        self.bullets: list[dict] = []
        self.asteroids: list[dict] = []

        self.shoot_cooldown = 0.0
        self.shoot_delay = 0.22

        self.score = 0
        self.lives = 3
        self.wave = 1
        self.is_game_over = False
        self.is_won = False

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

    def reset_ship(self) -> None:
        self.ship_pos = pygame.Vector2(self.play_rect.centerx, self.play_rect.centery)
        self.ship_vel = pygame.Vector2(0, 0)
        self.ship_angle = -90.0

    def spawn_wave(self) -> None:
        self.asteroids.clear()
        asteroid_count = 4 + self.wave

        for _ in range(asteroid_count):
            while True:
                x = random.uniform(self.play_rect.left + 20, self.play_rect.right - 20)
                y = random.uniform(self.play_rect.top + 20, self.play_rect.bottom - 20)
                if pygame.Vector2(x, y).distance_to(self.ship_pos) > 150:
                    break

            angle = random.uniform(0, 360)
            speed = random.uniform(50 + self.wave * 5, 100 + self.wave * 8)
            velocity = pygame.Vector2(1, 0).rotate(angle) * speed

            radius = random.randint(24, 42)

            self.asteroids.append(
                {
                    "pos": pygame.Vector2(x, y),
                    "vel": velocity,
                    "radius": radius,
                }
            )

    def reset_game(self) -> None:
        self.score = 0
        self.lives = 3
        self.wave = 1
        self.is_game_over = False
        self.is_won = False
        self.bullets.clear()
        self.shoot_cooldown = 0.0

        self.reset_ship()
        self.spawn_wave()

    def wrap_position(self, pos: pygame.Vector2, radius: float) -> None:
        if pos.x < self.play_rect.left - radius:
            pos.x = self.play_rect.right + radius
        elif pos.x > self.play_rect.right + radius:
            pos.x = self.play_rect.left - radius

        if pos.y < self.play_rect.top - radius:
            pos.y = self.play_rect.bottom + radius
        elif pos.y > self.play_rect.bottom + radius:
            pos.y = self.play_rect.top - radius

    def fire_bullet(self) -> None:
        direction = pygame.Vector2(1, 0).rotate(self.ship_angle)
        bullet_vel = direction * 460 + self.ship_vel

        self.bullets.append(
            {
                "pos": self.ship_pos.copy(),
                "vel": bullet_vel,
                "life": 1.2,
                "radius": 4,
            }
        )

    def break_asteroid(self, asteroid: dict) -> None:
        radius = asteroid["radius"]

        if radius <= 18:
            return

        for _ in range(2):
            angle = random.uniform(0, 360)
            speed = random.uniform(80, 140)
            velocity = pygame.Vector2(1, 0).rotate(angle) * speed

            self.asteroids.append(
                {
                    "pos": asteroid["pos"].copy(),
                    "vel": velocity,
                    "radius": max(14, radius // 2),
                }
            )

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif event.key == pygame.K_SPACE:
                    if not self.is_game_over and not self.is_won and self.shoot_cooldown <= 0:
                        self.fire_bullet()
                        self.shoot_cooldown = self.shoot_delay

    def update_ship(self, dt: float) -> None:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.ship_angle -= self.ship_rotation_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.ship_angle += self.ship_rotation_speed * dt

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            thrust = pygame.Vector2(1, 0).rotate(self.ship_angle) * self.ship_acceleration * dt
            self.ship_vel += thrust

        self.ship_vel *= 0.992
        self.ship_pos += self.ship_vel * dt
        self.wrap_position(self.ship_pos, self.ship_radius)

    def update_bullets(self, dt: float) -> None:
        for bullet in self.bullets[:]:
            bullet["pos"] += bullet["vel"] * dt
            bullet["life"] -= dt
            self.wrap_position(bullet["pos"], bullet["radius"])

            if bullet["life"] <= 0:
                self.bullets.remove(bullet)

    def update_asteroids(self, dt: float) -> None:
        for asteroid in self.asteroids:
            asteroid["pos"] += asteroid["vel"] * dt
            self.wrap_position(asteroid["pos"], asteroid["radius"])

    def check_collisions(self) -> None:
        for bullet in self.bullets[:]:
            bullet_pos = bullet["pos"]

            hit_asteroid = None
            for asteroid in self.asteroids:
                if bullet_pos.distance_to(asteroid["pos"]) <= bullet["radius"] + asteroid["radius"]:
                    hit_asteroid = asteroid
                    break

            if hit_asteroid is not None:
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                if hit_asteroid in self.asteroids:
                    self.asteroids.remove(hit_asteroid)
                    self.break_asteroid(hit_asteroid)
                    self.score += 100

        for asteroid in self.asteroids:
            if self.ship_pos.distance_to(asteroid["pos"]) <= self.ship_radius + asteroid["radius"]:
                self.lives -= 1

                if self.lives <= 0:
                    self.is_game_over = True
                else:
                    self.reset_ship()
                    self.bullets.clear()
                return

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

        if self.is_game_over or self.is_won:
            return

        self.update_ship(dt)
        self.update_bullets(dt)
        self.update_asteroids(dt)
        self.check_collisions()

        if not self.asteroids:
            self.wave += 1
            if self.wave > 5:
                self.is_won = True
            else:
                self.spawn_wave()

    def ship_points(self) -> list[tuple[int, int]]:
        forward = pygame.Vector2(1, 0).rotate(self.ship_angle) * self.ship_radius
        left = pygame.Vector2(1, 0).rotate(self.ship_angle + 140) * (self.ship_radius * 0.8)
        right = pygame.Vector2(1, 0).rotate(self.ship_angle - 140) * (self.ship_radius * 0.8)

        p1 = self.ship_pos + forward
        p2 = self.ship_pos + left
        p3 = self.ship_pos + right

        return [(int(p1.x), int(p1.y)), (int(p2.x), int(p2.y)), (int(p3.x), int(p3.y))]

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Asteroids", True, theme.TEXT)

        if self.is_won:
            status_text = "You survived the asteroid field!"
        elif self.is_game_over:
            status_text = "Game Over"
        else:
            status_text = "Destroy the asteroids"

        status = self.info_font.render(status_text, True, theme.TEXT)
        score = self.info_font.render(f"Score: {self.score}", True, theme.TEXT)
        lives = self.info_font.render(f"Lives: {self.lives}", True, theme.TEXT)
        wave = self.info_font.render(f"Wave: {self.wave}", True, theme.TEXT)
        controls = self.info_font.render(
            "Rotate: Left/Right or A,D  |  Thrust: Up/W  |  Space: Shoot  |  F5: Restart  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 32)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 75)))
        screen.blit(score, score.get_rect(center=(screen.get_width() // 2 - 180, 110)))
        screen.blit(lives, lives.get_rect(center=(screen.get_width() // 2, 110)))
        screen.blit(wave, wave.get_rect(center=(screen.get_width() // 2 + 180, 110)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 28)))

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)

        for asteroid in self.asteroids:
            pygame.draw.circle(
                screen,
                theme.SURFACE_ALT,
                (int(asteroid["pos"].x), int(asteroid["pos"].y)),
                asteroid["radius"],
                width=3,
            )

        for bullet in self.bullets:
            pygame.draw.circle(
                screen,
                theme.ACCENT,
                (int(bullet["pos"].x), int(bullet["pos"].y)),
                bullet["radius"],
            )

        pygame.draw.polygon(screen, theme.TEXT, self.ship_points(), width=3)