from __future__ import annotations

import math
import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme


class TopDownShooterGame(GameBase):
    game_id = "top_down_shooter"
    title = "Top-Down Shooter"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1100, 620)

        self.player_pos = pygame.Vector2(0, 0)
        self.player_radius = 20
        self.player_speed = 320.0
        self.player_health = 5
        self.player_max_health = 5

        self.bullets: list[dict] = []
        self.bullet_speed = 620.0
        self.bullet_radius = 5
        self.shoot_delay = 0.18
        self.shoot_timer = 0.0

        self.enemies: list[dict] = []
        self.enemy_spawn_padding = 40

        self.wave = 1
        self.score = 0
        self.is_game_over = False
        self.is_won = False

        self.max_waves = 6

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.small_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE)
        self.reset_game()

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.player_pos = pygame.Vector2(self.play_rect.centerx, self.play_rect.centery)
        self.player_health = self.player_max_health

        self.bullets.clear()
        self.enemies.clear()
        self.shoot_timer = 0.0

        self.wave = 1
        self.score = 0
        self.is_game_over = False
        self.is_won = False

        self.spawn_wave()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(
            (screen.get_width() - 1100) // 2,
            140,
            1100,
            620,
        )

    def spawn_wave(self) -> None:
        self.enemies.clear()

        enemy_count = 3 + self.wave * 2
        for _ in range(enemy_count):
            spawn_pos = self.random_edge_spawn()
            enemy = {
                "pos": spawn_pos,
                "radius": 18,
                "speed": 85.0 + self.wave * 8,
                "health": 2 if self.wave < 3 else 3,
                "damage_cooldown": 0.0,
            }
            self.enemies.append(enemy)

    def random_edge_spawn(self) -> pygame.Vector2:
        side = random.choice(["top", "bottom", "left", "right"])

        if side == "top":
            x = random.uniform(self.play_rect.left + 20, self.play_rect.right - 20)
            y = self.play_rect.top + self.enemy_spawn_padding
        elif side == "bottom":
            x = random.uniform(self.play_rect.left + 20, self.play_rect.right - 20)
            y = self.play_rect.bottom - self.enemy_spawn_padding
        elif side == "left":
            x = self.play_rect.left + self.enemy_spawn_padding
            y = random.uniform(self.play_rect.top + 20, self.play_rect.bottom - 20)
        else:
            x = self.play_rect.right - self.enemy_spawn_padding
            y = random.uniform(self.play_rect.top + 20, self.play_rect.bottom - 20)

        return pygame.Vector2(x, y)

    def fire_bullet(self, mouse_pos: tuple[int, int]) -> None:
        direction = pygame.Vector2(mouse_pos[0] - self.player_pos.x, mouse_pos[1] - self.player_pos.y)
        if direction.length_squared() == 0:
            return

        direction = direction.normalize()

        bullet = {
            "pos": self.player_pos.copy(),
            "vel": direction * self.bullet_speed,
            "radius": self.bullet_radius,
            "life": 1.5,
        }
        self.bullets.append(bullet)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
                elif event.key == pygame.K_F5:
                    self.reset_game()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.is_game_over and not self.is_won and self.shoot_timer <= 0:
                    self.fire_bullet(event.pos)
                    self.shoot_timer = self.shoot_delay

    def update_player(self, dt: float) -> None:
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
            move = move.normalize() * self.player_speed * dt
            self.player_pos += move

        self.player_pos.x = max(
            self.play_rect.left + self.player_radius,
            min(self.play_rect.right - self.player_radius, self.player_pos.x),
        )
        self.player_pos.y = max(
            self.play_rect.top + self.player_radius,
            min(self.play_rect.bottom - self.player_radius, self.player_pos.y),
        )

    def update_bullets(self, dt: float) -> None:
        for bullet in self.bullets[:]:
            bullet["pos"] += bullet["vel"] * dt
            bullet["life"] -= dt

            if bullet["life"] <= 0:
                self.bullets.remove(bullet)
                continue

            if not self.play_rect.collidepoint(int(bullet["pos"].x), int(bullet["pos"].y)):
                self.bullets.remove(bullet)
                continue

    def update_enemies(self, dt: float) -> None:
        for enemy in self.enemies:
            direction = self.player_pos - enemy["pos"]
            if direction.length_squared() > 0:
                direction = direction.normalize()
                enemy["pos"] += direction * enemy["speed"] * dt

            if enemy["damage_cooldown"] > 0:
                enemy["damage_cooldown"] -= dt

    def handle_collisions(self) -> None:
        # Bullet -> enemy
        for bullet in self.bullets[:]:
            hit_enemy = None

            for enemy in self.enemies:
                distance = bullet["pos"].distance_to(enemy["pos"])
                if distance <= bullet["radius"] + enemy["radius"]:
                    hit_enemy = enemy
                    break

            if hit_enemy is not None:
                hit_enemy["health"] -= 1
                if bullet in self.bullets:
                    self.bullets.remove(bullet)

                if hit_enemy["health"] <= 0 and hit_enemy in self.enemies:
                    self.enemies.remove(hit_enemy)
                    self.score += 100

        # Enemy -> player
        for enemy in self.enemies:
            distance = self.player_pos.distance_to(enemy["pos"])
            if distance <= self.player_radius + enemy["radius"]:
                if enemy["damage_cooldown"] <= 0:
                    self.player_health -= 1
                    enemy["damage_cooldown"] = 0.8

                    if self.player_health <= 0:
                        self.player_health = 0
                        self.is_game_over = True
                        return

    def update_wave_progression(self) -> None:
        if not self.enemies and not self.is_game_over:
            if self.wave >= self.max_waves:
                self.is_won = True
            else:
                self.wave += 1
                self.spawn_wave()

    def draw_crosshair(self, screen: pygame.Surface) -> None:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        size = 10
        pygame.draw.line(screen, theme.TEXT, (mouse_x - size, mouse_y), (mouse_x + size, mouse_y), 2)
        pygame.draw.line(screen, theme.TEXT, (mouse_x, mouse_y - size), (mouse_x, mouse_y + size), 2)

    def draw_player(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(
            screen,
            theme.ACCENT,
            (int(self.player_pos.x), int(self.player_pos.y)),
            self.player_radius,
        )

        mouse_pos = pygame.mouse.get_pos()
        aim = pygame.Vector2(mouse_pos[0] - self.player_pos.x, mouse_pos[1] - self.player_pos.y)
        if aim.length_squared() > 0:
            aim = aim.normalize()
            end_pos = self.player_pos + aim * (self.player_radius + 10)
            pygame.draw.line(
                screen,
                theme.TEXT,
                (int(self.player_pos.x), int(self.player_pos.y)),
                (int(end_pos.x), int(end_pos.y)),
                4,
            )

    def draw_enemies(self, screen: pygame.Surface) -> None:
        for enemy in self.enemies:
            pygame.draw.circle(
                screen,
                theme.DANGER,
                (int(enemy["pos"].x), int(enemy["pos"].y)),
                enemy["radius"],
            )

    def draw_bullets(self, screen: pygame.Surface) -> None:
        for bullet in self.bullets:
            pygame.draw.circle(
                screen,
                theme.WARNING,
                (int(bullet["pos"].x), int(bullet["pos"].y)),
                bullet["radius"],
            )

    def draw_health_bar(self, screen: pygame.Surface) -> None:
        bar_width = 220
        bar_height = 20
        x = self.play_rect.left
        y = 108

        pygame.draw.rect(screen, theme.SURFACE_ALT, (x, y, bar_width, bar_height), border_radius=8)

        fill_ratio = self.player_health / self.player_max_health
        fill_width = int(bar_width * fill_ratio)

        pygame.draw.rect(
            screen,
            theme.SUCCESS if fill_ratio > 0.4 else theme.WARNING if fill_ratio > 0.2 else theme.DANGER,
            (x, y, fill_width, bar_height),
            border_radius=8,
        )

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        if self.is_game_over or self.is_won:
            return

        self.update_player(dt)
        self.update_bullets(dt)
        self.update_enemies(dt)
        self.handle_collisions()
        self.update_wave_progression()

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.small_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Top-Down Shooter", True, theme.TEXT)

        if self.is_won:
            status_text = "You cleared all waves!"
        elif self.is_game_over:
            status_text = "Game Over"
        else:
            status_text = "Survive the enemy waves"

        status = self.info_font.render(status_text, True, theme.TEXT)
        score = self.info_font.render(f"Score: {self.score}", True, theme.TEXT)
        wave = self.info_font.render(f"Wave: {self.wave}/{self.max_waves}", True, theme.TEXT)
        health = self.small_font.render(f"Health: {self.player_health}/{self.player_max_health}", True, theme.TEXT)

        controls = self.info_font.render(
            "Move: WASD  |  Aim: Mouse  |  Shoot: Left Click  |  F5: Restart  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 32)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 75)))
        screen.blit(score, score.get_rect(center=(screen.get_width() // 2 - 160, 110)))
        screen.blit(wave, wave.get_rect(center=(screen.get_width() // 2 + 160, 110)))
        screen.blit(health, health.get_rect(midleft=(self.play_rect.left, 92)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 28)))

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)

        # subtle arena grid
        grid_step = 40
        for x in range(self.play_rect.left, self.play_rect.right, grid_step):
            pygame.draw.line(screen, theme.SURFACE_ALT, (x, self.play_rect.top), (x, self.play_rect.bottom), 1)
        for y in range(self.play_rect.top, self.play_rect.bottom, grid_step):
            pygame.draw.line(screen, theme.SURFACE_ALT, (self.play_rect.left, y), (self.play_rect.right, y), 1)

        self.draw_bullets(screen)
        self.draw_enemies(screen)
        self.draw_player(screen)
        self.draw_health_bar(screen)
        self.draw_crosshair(screen)

        if self.is_game_over:
            game_over = self.title_font.render("Game Over", True, theme.TEXT)
            restart = self.info_font.render("Press F5 to restart", True, theme.MUTED_TEXT)
            screen.blit(game_over, game_over.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20)))
            screen.blit(restart, restart.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 20)))

        if self.is_won:
            win_text = self.title_font.render("Victory!", True, theme.TEXT)
            restart = self.info_font.render("Press F5 to play again", True, theme.MUTED_TEXT)
            screen.blit(win_text, win_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20)))
            screen.blit(restart, restart.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 20)))