from __future__ import annotations

import math
import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class BulletHellLiteGame(GameBase):
    game_id = "bullet_hell_lite"
    title = "Bullet Hell Lite"

    def __init__(self, app) -> None:
        super().__init__(app)
        self.ui: GameUI | None = None

        self.play_rect = pygame.Rect(0, 0, 960, 620)

        self.player_pos = pygame.Vector2(0, 0)
        self.player_radius = 12
        self.player_speed = 280.0
        self.focus_speed = 160.0

        self.enemy_pos = pygame.Vector2(0, 0)
        self.enemy_radius = 18

        self.bullets: list[dict] = []
        self.popups: list[dict] = []

        self.time_alive = 0.0
        self.score = 0
        self.wave = 1

        self.paused = False
        self.completed = False

        self.pattern_timer = 0.0
        self.next_pattern_time = 1.0
        self.invuln_timer = 0.0

    def enter(self) -> None:
        self.ui = GameUI()
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(
            (screen.get_width() - 960) // 2,
            165,
            960,
            620,
        )

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.player_pos = pygame.Vector2(self.play_rect.centerx, self.play_rect.bottom - 80)
        self.enemy_pos = pygame.Vector2(self.play_rect.centerx, self.play_rect.top + 110)

        self.bullets.clear()
        self.popups.clear()

        self.time_alive = 0.0
        self.score = 0
        self.wave = 1

        self.paused = False
        self.completed = False

        self.pattern_timer = 0.0
        self.next_pattern_time = 0.9
        self.invuln_timer = 1.0

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["score"] = self.score
        payload["round"] = self.wave
        return payload

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene
        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def add_popup(self, text: str, pos: tuple[int, int], color: tuple[int, int, int]) -> None:
        self.popups.append(
            {
                "text": text,
                "pos": pygame.Vector2(pos[0], pos[1]),
                "vel": pygame.Vector2(0, -32),
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

    def spawn_radial_pattern(self, count: int, speed: float) -> None:
        for i in range(count):
            angle = (math.tau / count) * i
            velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
            self.bullets.append(
                {
                    "pos": pygame.Vector2(self.enemy_pos.x, self.enemy_pos.y),
                    "vel": velocity,
                    "radius": 8,
                }
            )

    def spawn_aimed_pattern(self, count: int, speed: float, spread: float) -> None:
        direction = self.player_pos - self.enemy_pos
        if direction.length_squared() == 0:
            direction = pygame.Vector2(0, 1)
        else:
            direction = direction.normalize()

        base_angle = math.atan2(direction.y, direction.x)
        start = base_angle - spread / 2

        if count == 1:
            angles = [base_angle]
        else:
            angles = [start + spread * (i / (count - 1)) for i in range(count)]

        for angle in angles:
            velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
            self.bullets.append(
                {
                    "pos": pygame.Vector2(self.enemy_pos.x, self.enemy_pos.y),
                    "vel": velocity,
                    "radius": 7,
                }
            )

    def spawn_ring_gap_pattern(self, count: int, speed: float, gap_index: int) -> None:
        for i in range(count):
            if i == gap_index or i == (gap_index + 1) % count:
                continue
            angle = (math.tau / count) * i
            velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
            self.bullets.append(
                {
                    "pos": pygame.Vector2(self.enemy_pos.x, self.enemy_pos.y),
                    "vel": velocity,
                    "radius": 9,
                }
            )

    def trigger_pattern(self) -> None:
        difficulty_scale = min(1.0 + self.time_alive / 30.0, 2.3)
        choice = random.choice(["radial", "aimed", "gap"])

        if choice == "radial":
            self.spawn_radial_pattern(int(10 + self.wave * 1.5), 150 * difficulty_scale)
        elif choice == "aimed":
            self.spawn_aimed_pattern(min(7 + self.wave, 12), 210 * difficulty_scale, 0.9)
        else:
            gap_index = random.randint(0, 11)
            self.spawn_ring_gap_pattern(12, 165 * difficulty_scale, gap_index)

        self.wave = 1 + int(self.time_alive // 12)
        self.next_pattern_time = max(0.35, 1.0 - self.time_alive * 0.015)

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
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.completed:
                self.reset_game()

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.update_popups(dt)

        if self.paused or self.completed:
            return

        self.time_alive += dt
        self.score = int(self.time_alive * 100)

        if self.invuln_timer > 0:
            self.invuln_timer -= dt

        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move.x += 1

        if move.length_squared() > 0:
            move = move.normalize()

        speed = self.focus_speed if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else self.player_speed
        self.player_pos += move * speed * dt
        self.player_pos.x = max(self.play_rect.left + self.player_radius, min(self.player_pos.x, self.play_rect.right - self.player_radius))
        self.player_pos.y = max(self.play_rect.top + self.player_radius, min(self.player_pos.y, self.play_rect.bottom - self.player_radius))

        self.pattern_timer += dt
        if self.pattern_timer >= self.next_pattern_time:
            self.pattern_timer = 0.0
            self.trigger_pattern()

        for bullet in self.bullets:
            bullet["pos"] += bullet["vel"] * dt

        self.bullets = [
            b for b in self.bullets
            if self.play_rect.left - 30 <= b["pos"].x <= self.play_rect.right + 30
            and self.play_rect.top - 30 <= b["pos"].y <= self.play_rect.bottom + 30
        ]

        if self.invuln_timer <= 0:
            for bullet in self.bullets:
                if bullet["pos"].distance_to(self.player_pos) <= bullet["radius"] + self.player_radius:
                    self.completed = True
                    self.add_popup("HIT", (int(self.player_pos.x), int(self.player_pos.y)), theme.DANGER)
                    break

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "Bullet Hell Lite",
            "Dodge incoming patterns. Hold Shift to focus for finer movement.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Score: {self.score}",
                f"Time: {self.time_alive:0.1f}s",
                f"Wave: {self.wave}",
            ],
        )
        sub = "Tiny movements matter. Read gaps early and commit cleanly." if not self.completed else "Run ended."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "WASD / Arrows: Move  |  Shift: Focus  |  P: Pause  |  F5: Restart  |  Esc: Back")

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        pygame.draw.circle(screen, theme.WARNING, (int(self.enemy_pos.x), int(self.enemy_pos.y)), self.enemy_radius)

        for bullet in self.bullets:
            pygame.draw.circle(
                screen,
                theme.DANGER,
                (int(bullet["pos"].x), int(bullet["pos"].y)),
                bullet["radius"],
            )

        player_color = theme.ACCENT if self.invuln_timer <= 0 or int(self.invuln_timer * 10) % 2 == 0 else theme.SURFACE_ALT
        pygame.draw.circle(screen, player_color, (int(self.player_pos.x), int(self.player_pos.y)), self.player_radius)
        pygame.draw.circle(screen, theme.TEXT, (int(self.player_pos.x), int(self.player_pos.y)), 4)

        self.ui.draw_floating_texts(screen, self.popups)

        if self.paused and not self.completed:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.completed:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "Run Over",
                f"Score: {self.score}",
                f"Survived: {self.time_alive:0.1f}s  |  Wave: {self.wave}",
            )