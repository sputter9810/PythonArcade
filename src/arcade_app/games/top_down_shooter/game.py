from __future__ import annotations

import math
import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class TopDownShooterGame(GameBase):
    game_id = "top_down_shooter"
    title = "Top-Down Shooter"

    POWERUP_RAPID_FIRE = "rapid_fire"
    POWERUP_PIERCE = "pierce"
    POWERUP_HEAL = "heal"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.ui: GameUI | None = None

        self.play_rect = pygame.Rect(0, 0, 1100, 640)

        self.player_pos = pygame.Vector2(0, 0)
        self.player_speed = 280.0
        self.player_radius = 18

        self.bullets: list[dict] = []
        self.enemies: list[dict] = []
        self.powerups: list[dict] = []
        self.popups: list[dict] = []

        self.wave = 1
        self.score = 0
        self.lives = 3

        self.game_over = False
        self.paused = False

        self.shoot_cooldown = 0.0
        self.enemy_spawn_timer = 0.0

        self.rapid_fire_timer = 0.0
        self.pierce_timer = 0.0

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

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.player_pos = pygame.Vector2(self.play_rect.centerx, self.play_rect.centery)
        self.bullets.clear()
        self.enemies.clear()
        self.powerups.clear()
        self.popups.clear()

        self.wave = 1
        self.score = 0
        self.lives = 3

        self.game_over = False
        self.paused = False

        self.shoot_cooldown = 0.0
        self.enemy_spawn_timer = 1.0
        self.rapid_fire_timer = 0.0
        self.pierce_timer = 0.0
        self.spawn_wave()

    def spawn_wave(self) -> None:
        self.enemies.clear()
        count = 4 + self.wave * 2

        for _ in range(count):
            self.enemies.append(self.spawn_enemy())

    def spawn_enemy(self) -> dict:
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            pos = pygame.Vector2(random.randint(self.play_rect.left, self.play_rect.right), self.play_rect.top - 30)
        elif edge == "bottom":
            pos = pygame.Vector2(random.randint(self.play_rect.left, self.play_rect.right), self.play_rect.bottom + 30)
        elif edge == "left":
            pos = pygame.Vector2(self.play_rect.left - 30, random.randint(self.play_rect.top, self.play_rect.bottom))
        else:
            pos = pygame.Vector2(self.play_rect.right + 30, random.randint(self.play_rect.top, self.play_rect.bottom))

        return {
            "pos": pos,
            "radius": random.randint(14, 22),
            "speed": random.uniform(70, 120) + self.wave * 6,
            "hp": 1,
        }

    def maybe_spawn_powerup(self, pos: pygame.Vector2) -> None:
        if random.random() > 0.16:
            return

        kind = random.choice([self.POWERUP_RAPID_FIRE, self.POWERUP_PIERCE, self.POWERUP_HEAL])
        color = (
            theme.ACCENT if kind == self.POWERUP_RAPID_FIRE
            else theme.WARNING if kind == self.POWERUP_PIERCE
            else theme.SUCCESS
        )

        self.powerups.append(
            {
                "kind": kind,
                "pos": pygame.Vector2(pos.x, pos.y),
                "radius": 13,
                "color": color,
            }
        )

    def add_popup(self, text: str, pos: tuple[int, int], color: tuple[int, int, int]) -> None:
        self.popups.append(
            {
                "text": text,
                "pos": pygame.Vector2(pos[0], pos[1]),
                "vel": pygame.Vector2(0, -34),
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

    def fire_bullet(self) -> None:
        if self.shoot_cooldown > 0 or self.game_over or self.paused:
            return

        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        direction = mouse_pos - self.player_pos
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
        else:
            direction = direction.normalize()

        self.bullets.append(
            {
                "pos": pygame.Vector2(self.player_pos.x, self.player_pos.y),
                "vel": direction * 520,
                "life": 1.2,
                "pierce": self.pierce_timer > 0,
            }
        )
        self.shoot_cooldown = 0.07 if self.rapid_fire_timer > 0 else 0.14

    def collect_powerup(self, powerup: dict) -> None:
        if powerup["kind"] == self.POWERUP_RAPID_FIRE:
            self.rapid_fire_timer = 8.0
            self.add_popup("RAPID FIRE", (int(powerup["pos"].x), int(powerup["pos"].y)), theme.ACCENT)
        elif powerup["kind"] == self.POWERUP_PIERCE:
            self.pierce_timer = 8.0
            self.add_popup("PIERCE", (int(powerup["pos"].x), int(powerup["pos"].y)), theme.WARNING)
        else:
            if self.lives < 5:
                self.lives += 1
            self.add_popup("+1 LIFE", (int(powerup["pos"].x), int(powerup["pos"].y)), theme.SUCCESS)

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
        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= dt
        if self.pierce_timer > 0:
            self.pierce_timer -= dt

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

        self.player_pos += move * self.player_speed * dt
        self.player_pos.x = max(self.play_rect.left + self.player_radius, min(self.player_pos.x, self.play_rect.right - self.player_radius))
        self.player_pos.y = max(self.play_rect.top + self.player_radius, min(self.player_pos.y, self.play_rect.bottom - self.player_radius))

        for bullet in self.bullets:
            bullet["pos"] += bullet["vel"] * dt
            bullet["life"] -= dt
        self.bullets = [b for b in self.bullets if b["life"] > 0 and self.play_rect.collidepoint(b["pos"].x, b["pos"].y)]

        for enemy in self.enemies:
            direction = self.player_pos - enemy["pos"]
            if direction.length_squared() > 0:
                enemy["pos"] += direction.normalize() * enemy["speed"] * dt

        remaining_bullets: list[dict] = []
        remaining_enemies = self.enemies.copy()

        for bullet in self.bullets:
            hit_any = False
            hits_this_bullet: list[dict] = []

            for enemy in remaining_enemies:
                if bullet["pos"].distance_to(enemy["pos"]) <= enemy["radius"] + 4:
                    hits_this_bullet.append(enemy)
                    hit_any = True
                    reward = 75
                    self.score += reward
                    self.add_popup(f"+{reward}", (int(enemy["pos"].x), int(enemy["pos"].y)), theme.ACCENT)
                    self.maybe_spawn_powerup(enemy["pos"])
                    if not bullet["pierce"]:
                        break

            for enemy in hits_this_bullet:
                if enemy in remaining_enemies:
                    remaining_enemies.remove(enemy)

            if not hit_any or bullet["pierce"]:
                remaining_bullets.append(bullet)

        self.bullets = remaining_bullets
        self.enemies = remaining_enemies

        for powerup in self.powerups[:]:
            if self.player_pos.distance_to(powerup["pos"]) <= self.player_radius + powerup["radius"]:
                self.collect_powerup(powerup)
                self.powerups.remove(powerup)

        for enemy in self.enemies[:]:
            if enemy["pos"].distance_to(self.player_pos) <= enemy["radius"] + self.player_radius:
                self.lives -= 1
                self.enemies.remove(enemy)
                if self.lives <= 0:
                    self.game_over = True
                break

        if not self.enemies and not self.game_over:
            self.wave += 1
            self.spawn_wave()

    def draw_player(self, screen: pygame.Surface) -> None:
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        direction = mouse_pos - self.player_pos
        angle = 0.0 if direction.length_squared() == 0 else math.atan2(direction.y, direction.x)

        nose = self.player_pos + pygame.Vector2(math.cos(angle), math.sin(angle)) * 22
        left = self.player_pos + pygame.Vector2(math.cos(angle + 2.4), math.sin(angle + 2.4)) * 16
        right = self.player_pos + pygame.Vector2(math.cos(angle - 2.4), math.sin(angle - 2.4)) * 16

        color = theme.WARNING if self.pierce_timer > 0 else theme.TEXT
        pygame.draw.polygon(
            screen,
            color,
            [(int(nose.x), int(nose.y)), (int(left.x), int(left.y)), (int(right.x), int(right.y))],
        )

    def draw_powerup(self, screen: pygame.Surface, powerup: dict) -> None:
        pygame.draw.circle(screen, powerup["color"], (int(powerup["pos"].x), int(powerup["pos"].y)), powerup["radius"])
        pygame.draw.circle(screen, theme.BACKGROUND, (int(powerup["pos"].x), int(powerup["pos"].y)), max(4, powerup["radius"] // 2))

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "Top-Down Shooter",
            "Move with WASD / Arrows. Aim with the mouse. Fire with Click or Space.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Score: {self.score}",
                f"Lives: {self.lives}",
                f"Wave: {self.wave}",
                f"Rapid: {'ON' if self.rapid_fire_timer > 0 else 'OFF'}",
                f"Pierce: {'ON' if self.pierce_timer > 0 else 'OFF'}",
            ],
        )
        self.ui.draw_sub_stats(screen, "Powerups: blue = rapid fire, yellow = pierce, green = heal.")
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        for enemy in self.enemies:
            pygame.draw.circle(screen, theme.DANGER, (int(enemy["pos"].x), int(enemy["pos"].y)), enemy["radius"])

        for powerup in self.powerups:
            self.draw_powerup(screen, powerup)

        for bullet in self.bullets:
            color = theme.WARNING if bullet["pierce"] else theme.ACCENT
            pygame.draw.circle(screen, color, (int(bullet["pos"].x), int(bullet["pos"].y)), 4)

        self.draw_player(screen)
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