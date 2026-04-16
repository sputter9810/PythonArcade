from __future__ import annotations

import math
import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class AsteroidsGame(GameBase):
    game_id = "asteroids"
    title = "Asteroids"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.ui: GameUI | None = None

        self.play_rect = pygame.Rect(0, 0, 1100, 640)

        self.ship_pos = pygame.Vector2(0, 0)
        self.ship_vel = pygame.Vector2(0, 0)
        self.ship_angle = 0.0

        self.turn_speed = 210.0
        self.thrust = 320.0
        self.friction = 0.992

        self.bullets: list[dict] = []
        self.asteroids: list[dict] = []
        self.popups: list[dict] = []

        self.score = 0
        self.lives = 3
        self.wave = 1

        self.game_over = False
        self.paused = False
        self.invuln_timer = 0.0
        self.shoot_cooldown = 0.0

    def enter(self) -> None:
        self.ui = GameUI()
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(
            (screen.get_width() - 1100) // 2,
            165,
            1100,
            640,
        )

    def reset_ship(self) -> None:
        self.ship_pos = pygame.Vector2(self.play_rect.centerx, self.play_rect.centery)
        self.ship_vel = pygame.Vector2(0, 0)
        self.ship_angle = -90.0
        self.invuln_timer = 2.0

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.score = 0
        self.lives = 3
        self.wave = 1
        self.game_over = False
        self.paused = False
        self.bullets.clear()
        self.asteroids.clear()
        self.popups.clear()
        self.shoot_cooldown = 0.0
        self.reset_ship()
        self.spawn_wave()

    def spawn_wave(self) -> None:
        self.asteroids.clear()
        count = 3 + self.wave

        for _ in range(count):
            while True:
                pos = pygame.Vector2(
                    random.randint(self.play_rect.left, self.play_rect.right),
                    random.randint(self.play_rect.top, self.play_rect.bottom),
                )
                if pos.distance_to(self.ship_pos) > 180:
                    break

            angle = random.uniform(0, math.tau)
            speed = random.uniform(40, 95) + self.wave * 6

            size = random.choice([54, 72, 96])

            self.asteroids.append(
                {
                    "pos": pos,
                    "vel": pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed),
                    "radius": size // 2,
                    "size": size,
                }
            )

    def add_popup(self, text: str, pos: pygame.Vector2, color: tuple[int, int, int]) -> None:
        self.popups.append(
            {
                "text": text,
                "pos": pygame.Vector2(pos.x, pos.y),
                "vel": pygame.Vector2(0, -36),
                "life": 0.6,
                "max_life": 0.6,
                "color": color,
                "alpha": 255,
            }
        )

    def update_popups(self, dt: float) -> None:
        updated: list[dict] = []
        for popup in self.popups:
            popup["life"] -= dt
            if popup["life"] <= 0:
                continue
            popup["pos"] += popup["vel"] * dt
            popup["alpha"] = int(255 * (popup["life"] / popup["max_life"]))
            updated.append(popup)
        self.popups = updated

    def wrap_position(self, pos: pygame.Vector2) -> None:
        if pos.x < self.play_rect.left:
            pos.x = self.play_rect.right
        elif pos.x > self.play_rect.right:
            pos.x = self.play_rect.left

        if pos.y < self.play_rect.top:
            pos.y = self.play_rect.bottom
        elif pos.y > self.play_rect.bottom:
            pos.y = self.play_rect.top

    def ship_points(self) -> list[tuple[int, int]]:
        angle_rad = math.radians(self.ship_angle)
        forward = pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad))
        right = forward.rotate(90)

        nose = self.ship_pos + forward * 20
        left = self.ship_pos - forward * 14 + right * 12
        right_pt = self.ship_pos - forward * 14 - right * 12

        return [(int(nose.x), int(nose.y)), (int(left.x), int(left.y)), (int(right_pt.x), int(right_pt.y))]

    def fire_bullet(self) -> None:
        if self.shoot_cooldown > 0 or self.game_over or self.paused:
            return

        angle_rad = math.radians(self.ship_angle)
        direction = pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad))
        bullet_pos = self.ship_pos + direction * 24
        bullet_vel = direction * 560 + self.ship_vel

        self.bullets.append(
            {
                "pos": bullet_pos,
                "vel": bullet_vel,
                "life": 1.4,
            }
        )
        self.shoot_cooldown = 0.18

    def split_asteroid(self, asteroid: dict) -> None:
        size = asteroid["size"]
        reward = 30 if size >= 96 else 60 if size >= 72 else 100
        self.score += reward
        self.add_popup(f"+{reward}", asteroid["pos"], theme.ACCENT)

        if size <= 54:
            return

        new_size = 72 if size >= 96 else 54
        for direction in (-1, 1):
            angle = random.uniform(0, math.tau) + direction * 0.6
            speed = random.uniform(90, 150)
            self.asteroids.append(
                {
                    "pos": pygame.Vector2(asteroid["pos"].x, asteroid["pos"].y),
                    "vel": pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed),
                    "radius": new_size // 2,
                    "size": new_size,
                }
            )

    def ship_hit(self) -> None:
        if self.invuln_timer > 0:
            return

        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
            return

        self.reset_ship()

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
                elif event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset_game()
                    else:
                        self.fire_bullet()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_over:
                    self.reset_game()
                else:
                    self.fire_bullet()

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.update_popups(dt)

        if self.paused:
            return

        if self.game_over:
            return

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        if self.invuln_timer > 0:
            self.invuln_timer -= dt

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.ship_angle -= self.turn_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.ship_angle += self.turn_speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            angle_rad = math.radians(self.ship_angle)
            direction = pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad))
            self.ship_vel += direction * self.thrust * dt

        self.ship_pos += self.ship_vel * dt
        self.ship_vel *= self.friction
        self.wrap_position(self.ship_pos)

        for bullet in self.bullets:
            bullet["pos"] += bullet["vel"] * dt
            bullet["life"] -= dt
            self.wrap_position(bullet["pos"])

        self.bullets = [b for b in self.bullets if b["life"] > 0]

        for asteroid in self.asteroids:
            asteroid["pos"] += asteroid["vel"] * dt
            self.wrap_position(asteroid["pos"])

        remaining_bullets: list[dict] = []
        destroyed_indices: set[int] = set()
        asteroids_to_split: list[dict] = []

        for bullet in self.bullets:
            hit = False
            for index, asteroid in enumerate(self.asteroids):
                if index in destroyed_indices:
                    continue
                if bullet["pos"].distance_to(asteroid["pos"]) <= asteroid["radius"]:
                    destroyed_indices.add(index)
                    asteroids_to_split.append(asteroid)
                    hit = True
                    break
            if not hit:
                remaining_bullets.append(bullet)

        if destroyed_indices:
            self.asteroids = [a for i, a in enumerate(self.asteroids) if i not in destroyed_indices]
            for asteroid in asteroids_to_split:
                self.split_asteroid(asteroid)

        self.bullets = remaining_bullets

        if self.invuln_timer <= 0:
            for asteroid in self.asteroids:
                if self.ship_pos.distance_to(asteroid["pos"]) <= asteroid["radius"] + 14:
                    self.ship_hit()
                    break

        if not self.asteroids and not self.game_over:
            self.wave += 1
            self.spawn_wave()

    def draw_ship(self, screen: pygame.Surface) -> None:
        points = self.ship_points()
        color = theme.TEXT if self.invuln_timer <= 0 or int(self.invuln_timer * 10) % 2 == 0 else theme.SURFACE_ALT
        pygame.draw.polygon(screen, color, points, width=2)

    def draw_asteroid(self, screen: pygame.Surface, asteroid: dict) -> None:
        pos = asteroid["pos"]
        radius = asteroid["radius"]
        points = []
        for i in range(9):
            angle = (math.tau / 9) * i
            offset = random.uniform(0.78, 1.15)
            x = pos.x + math.cos(angle) * radius * offset
            y = pos.y + math.sin(angle) * radius * offset
            points.append((int(x), int(y)))
        pygame.draw.polygon(screen, theme.MUTED_TEXT, points, width=2)

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "Asteroids",
            "Turn with A/D or Left/Right, thrust with W/Up, shoot with Space or Click.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Score: {self.score}",
                f"Lives: {self.lives}",
                f"Wave: {self.wave}",
            ],
        )
        self.ui.draw_sub_stats(screen, "Split large rocks, control your drift, and clear each wave.")
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        for asteroid in self.asteroids:
            self.draw_asteroid(screen, asteroid)

        for bullet in self.bullets:
            pygame.draw.circle(screen, theme.ACCENT, (int(bullet["pos"].x), int(bullet["pos"].y)), 3)

        self.draw_ship(screen)
        self.ui.draw_floating_texts(screen, self.popups)

        if self.paused and not self.game_over:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.game_over:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "Game Over",
                f"Final Score: {self.score}",
                f"Final Wave: {self.wave}",
            )